#!/usr/bin/env python3
"""Print compact resume context from the checkpoint and the actual files.

Python 3.9+, standard library only. Works with or without hooks: the scan for files
changed after the checkpoint runs now, so an abrupt stop is detected on any host.
Output is a route to inspection, not evidence. Always exits 0 so a session-start hook
cannot break the host.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cross_agent_handoff_snapshot', HERE / 'snapshot.py')
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)
handoff = snapshot.handoff
spec = importlib.util.spec_from_file_location('cross_agent_handoff_lock', HERE / 'lock.py')
lock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lock)
LISTED_FILES = 15


def section(text, name, limit):
    match = re.search(r'^## ' + re.escape(name) + r'\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    lines = [line for line in (match[1].strip().splitlines() if match else []) if line.strip()]
    return lines[:limit] + (['(... see ' + name + ' in the checkpoint)'] if len(lines) > limit else [])


def latest_snapshot(root):
    try:
        return json.loads((root / '.handoff' / 'auto' / 'latest.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


def build(root, checkpoint, config):
    lines = ['cross-agent-handoff resume context (generated from project files; verify before trusting)']
    path = root / checkpoint
    if not path.is_file():
        lines.append('No ' + checkpoint + ' found. Use the cross-agent-handoff skill to recover or initialize.')
        return lines
    text = path.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
    meta = {key: (handoff.fields(text, key) or ['?'])[0].strip()
            for key in ('task_status', 'handoff', 'writer', 'updated_at', 'language', 'profile')}
    summary = 'Checkpoint: {} | task_status: {} | handoff: {} | writer: {}'.format(
        checkpoint, meta['task_status'], meta['handoff'], meta['writer'])
    for key in ('updated_at', 'language', 'profile'):
        if meta[key] != '?':
            summary += ' | {}: {}'.format(key, meta[key])
    lines.append(summary)

    warnings = []
    errors = handoff.validate(text)
    if errors:
        warnings.append('Checkpoint fails structural checks: ' + '; '.join(errors[:3]))
    if meta['handoff'] in ('working', 'recovery'):
        warnings.append('Checkpoint says handoff: {} (writer: {}). Confirm that session has stopped '
                        'before editing overlapping files.'.format(meta['handoff'], meta['writer']))
    changes = snapshot.changes_since_checkpoint(root, checkpoint, config)
    if changes['files'] or changes['commits']:
        warnings.append('{} files and {} commits changed after {} was saved ({}). The previous session '
                        'probably stopped before saving. Recover from the actual files; do not trust the '
                        'checkpoint alone.'.format(len(changes['files']), len(changes['commits']),
                                                   checkpoint, changes['reference']))
    if changes['truncated']:
        warnings.append('The change scan stopped early after {} entries; inspect the project directly.'.format(
            changes['scanned']))
    held = lock.state(root, float(config['lock_stale_minutes']))
    if held['state'] != 'free':
        warnings.append('Advisory lock held by {} ({}, heartbeat {} min ago). Do not edit overlapping files until '
                        'the user confirms that session has stopped; then take over with lock.py acquire '
                        '--confirm-takeover.'.format(held['holder'], held['state'], held.get('heartbeat_minutes')))
    last = latest_snapshot(root)
    event = (last or {}).get('event') or {}
    if event.get('error') and last.get('checkpoint', {}).get('sha256') == handoff.digest(path.read_bytes()):
        warnings.append('The last recorded session ended with error "{}" at {}.'.format(
            event['error'], last.get('created_at')))
    lines.extend('WARNING: ' + item for item in warnings)

    lines.append('Task:')
    lines.extend('  ' + line for line in section(text, 'Task', 8))
    lines.append('Next:')
    lines.extend('  ' + line for line in section(text, 'Next', 6))
    if changes['files']:
        lines.append('Changed after the checkpoint (newest first):')
        for rel, size, mtime in changes['files'][:LISTED_FILES]:
            lines.append('  {}  ({} bytes, {})'.format(rel, size, snapshot.iso(mtime)))
        if len(changes['files']) > LISTED_FILES:
            lines.append('  ... {} more'.format(len(changes['files']) - LISTED_FILES))
    if changes['commits']:
        lines.append('Commits after the checkpoint:')
        lines.extend('  ' + commit for commit in changes['commits'][:10])
    if last:
        lines.append('Last mechanical snapshot: {} (event: {}, recent files: {})'.format(
            last.get('created_at'), event.get('hook_event_name') or event.get('hookEventName') or 'manual',
            (last.get('recent_files') or {}).get('count')))
    lines.append('Use the cross-agent-handoff skill to resume: read applicable instructions and the '
                 'checkpoint, inspect actual files and changes, preserve unfinished work, then continue.')
    return lines


def render(lines, limit, output_format):
    if len(lines) > limit:
        lines = lines[:limit - 1] + ['(output capped at {} lines)'.format(limit)]
    text = '\n'.join(lines)
    if output_format == 'antigravity':
        return json.dumps({'injectSteps': [{'ephemeralMessage': text}]})
    return text


def run(argv=None, stdin=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--project', help='Project directory; default: hook input, then cwd')
    parser.add_argument('--checkpoint', default='HANDOFF.md')
    parser.add_argument('--hook', action='store_true', help='Read the host hook JSON from stdin')
    parser.add_argument('--format', default='text', choices=('text', 'antigravity'))
    parser.add_argument('--max-lines', type=int)
    args = parser.parse_args(argv)
    payload = snapshot.read_event((stdin or sys.stdin).read())[1] if args.hook else {}
    workspaces = payload.get('workspacePaths') or []
    start = (args.project or payload.get('cwd') or (workspaces[0] if workspaces else None)
             or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
    root = snapshot.find_root(start, args.checkpoint)
    if root is None:
        return ''  # Not a continuity project; stay silent inside hooks.
    config = snapshot.load_config(root)
    return render(build(root, args.checkpoint, config), args.max_lines or int(config['max_lines']), args.format)


def main():
    try:
        output = run()
        if output:
            print(output)
    except Exception as exc:  # A session-start hook must never break the host.
        print('inject: failed: {}: {}'.format(type(exc).__name__, exc), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
