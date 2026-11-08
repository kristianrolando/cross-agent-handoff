#!/usr/bin/env python3
"""Mechanical continuity snapshot. Python 3.9+, standard library only.

Records what changed in the project without a model: Git state, recently modified
files and media metadata. Writes .handoff/auto/latest.json and a one-line summary to
.handoff/auto/history.jsonl. Designed to run inside host hooks: it never raises and
always exits 0, reporting problems on stderr. It is not a daemon and does not save
intent; the agent's checkpoint remains the semantic record.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SCHEMA = 'cross-agent-handoff/snapshot-1'
SKIP_DIRS = {'.git', '.hg', '.svn', 'node_modules', '.handoff', '__pycache__', '.venv', 'venv',
             '.tox', '.nox', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache', '.next',
             '.turbo', '.parcel-cache', '.gradle', '.idea', '.vs'}
MEDIA = {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v', '.mxf', '.prores', '.gif',
         '.wav', '.mp3', '.aac', '.flac', '.ogg', '.m4a', '.aiff',
         '.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff', '.exr', '.psd', '.svg',
         '.lottie', '.blend', '.fbx', '.glb', '.gltf', '.obj', '.ttf', '.otf', '.woff2'}
DEFAULTS = {'window_minutes': 120, 'exclude': [], 'partial_hash': False,
            'history_max_lines': 500, 'scan_seconds': 1.5, 'max_entries': 50000,
            'max_files': 200, 'guard_files': 5, 'guard_minutes': 30, 'max_lines': 150}
EVENT_FIELDS = ('hook_event_name', 'hookEventName', 'source', 'error', 'terminationReason')
PARTIAL = 1024 * 1024
TOLERANCE = 2.0  # Seconds of filesystem timestamp slack.


def load_handoff():
    spec = importlib.util.spec_from_file_location('cross_agent_handoff_helper', HERE / 'handoff.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


handoff = load_handoff()


def warn(message):
    print('snapshot: ' + message, file=sys.stderr)


def iso(timestamp=None):
    moment = datetime.now(timezone.utc) if timestamp is None else datetime.fromtimestamp(timestamp, timezone.utc)
    return moment.astimezone().isoformat(timespec='seconds')


def find_root(start, checkpoint='HANDOFF.md'):
    """Nearest directory at or above start holding the checkpoint or .handoff/."""
    start = Path(start).resolve()
    for directory in (start, *start.parents):
        if (directory / checkpoint).is_file() or (directory / '.handoff').is_dir():
            return directory
        if (directory / '.git').exists():
            break
    return None


def load_config(root):
    config = dict(DEFAULTS)
    path = root / '.handoff' / 'config.json'
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            for section in ('snapshot', 'guard', 'inject'):
                for key, value in (data.get(section) or {}).items():
                    config[key if section != 'guard' else 'guard_' + key] = value
        except (OSError, ValueError, AttributeError) as exc:
            warn('ignoring unreadable .handoff/config.json: ' + str(exc))
    return config


def git(root, *args, timeout=5):
    try:
        result = subprocess.run(['git', '-c', 'core.quotepath=off', '-C', str(root), *args],
                                capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def git_state(root):
    if git(root, 'rev-parse', '--is-inside-work-tree') is None:
        return {'available': False}
    status = (git(root, 'status', '--porcelain', '--untracked-files=normal') or '').splitlines()
    stat = git(root, 'diff', '--stat', 'HEAD')
    if stat is None:  # No commit yet.
        stat = git(root, 'diff', '--stat') or ''
    stat = stat.splitlines()
    return {'available': True, 'branch': (git(root, 'branch', '--show-current') or '').strip() or None,
            'head': (git(root, 'rev-parse', '--short', 'HEAD') or '').strip() or None,
            'status': status[:200], 'status_truncated': len(status) > 200,
            'diff_stat': stat[-50:], 'note': 'Status paths are relative to the Git root.'}


def tracked_clean(root):
    """Tracked files under root whose content matches the index and HEAD, or None without Git."""
    listed = git(root, 'ls-files', '-z')
    if listed is None:
        return None
    tracked = set(filter(None, listed.split('\0')))
    modified = set(filter(None, (git(root, 'ls-files', '-z', '--modified') or '').split('\0')))
    staged = git(root, 'diff', '--cached', '--name-only', '-z', '--relative')
    staged = tracked if staged is None else set(filter(None, staged.split('\0')))
    return tracked - modified - staged


def scan(root, since, config, ignore=()):
    """Files modified after `since` (epoch seconds), newest first, within a time budget."""
    exclude = {str(item).strip('/').replace('\\', '/') for item in config['exclude']}
    ignore = set(ignore)
    deadline = time.monotonic() + float(config['scan_seconds'])
    stack, found, scanned, truncated = [root], [], 0, False
    while stack and not truncated:
        directory = stack.pop()
        try:
            entries = os.scandir(directory)
        except OSError:
            continue
        with entries:
            for entry in entries:
                scanned += 1
                if scanned > int(config['max_entries']) or time.monotonic() > deadline:
                    truncated = True
                    break
                try:
                    rel = Path(entry.path).relative_to(root).as_posix()
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name not in SKIP_DIRS and rel not in exclude:
                            stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False) and rel not in ignore:
                        info = entry.stat(follow_symlinks=False)
                        if info.st_mtime > since:
                            found.append((rel, info.st_size, info.st_mtime))
                except OSError:
                    continue
    found.sort(key=lambda item: item[2], reverse=True)
    return found, truncated, scanned


def partial_hash(path, size):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        digest.update(stream.read(PARTIAL))
        if size > 2 * PARTIAL:
            stream.seek(-PARTIAL, os.SEEK_END)
            digest.update(stream.read(PARTIAL))
        elif size > PARTIAL:
            digest.update(stream.read())
    return digest.hexdigest()


def describe(root, files, config, hashes=False):
    output = []
    for rel, size, mtime in files[:int(config['max_files'])]:
        record = {'path': rel, 'size': size, 'mtime': iso(mtime)}
        if Path(rel).suffix.lower() in MEDIA:
            record['media'] = True
            if hashes:
                try:
                    record['partial_sha256'] = partial_hash(root / rel, size)
                except OSError as exc:
                    record['partial_sha256_error'] = str(exc)
        output.append(record)
    return output


def checkpoint_ignores(checkpoint):
    name = Path(checkpoint)
    return {name.as_posix(), (name.parent / (name.name + '.previous')).as_posix(),
            (name.parent / ('.' + name.name + '.save-lock')).as_posix()}


def changes_since_checkpoint(root, checkpoint, config):
    """Files changed after the checkpoint was last written, ignoring clean tracked files.

    The reference is the checkpoint's modification time: a save always updates it. A Git
    checkout also refreshes it, so tracked files identical to HEAD are not reported.
    """
    path = root / checkpoint
    if not path.is_file():
        return None
    reference = path.stat().st_mtime
    found, truncated, scanned = scan(root, reference + TOLERANCE, config, checkpoint_ignores(checkpoint))
    clean = tracked_clean(root)
    if clean is not None:
        found = [item for item in found if item[0] not in clean]
    commits = []
    if clean is not None:
        commits = commits_after(root, checkpoint, reference, clean)
    return {'reference': iso(reference), 'files': found, 'truncated': truncated,
            'scanned': scanned, 'commits': commits}


def commits_after(root, checkpoint, reference, clean):
    """Commits made after the checkpoint's latest saved version."""
    name = Path(checkpoint).as_posix()
    if name in clean:  # Committed and unchanged: count commits after the last one touching it.
        last = (git(root, 'log', '-1', '--format=%H', '--', name) or '').strip()
        if last:
            return (git(root, 'log', '--format=%h %s', '-n', '20', last + '..HEAD') or '').splitlines()
    since = datetime.fromtimestamp(reference + TOLERANCE, timezone.utc).isoformat()
    return (git(root, 'log', '--since=' + since, '--format=%h %s', '-n', '20') or '').splitlines()


def read_event(raw):
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError:
        return {}, {}
    if not isinstance(data, dict):
        return {}, {}
    event = {key: str(data[key])[:100] for key in EVENT_FIELDS if data.get(key) not in (None, '')}
    return event, data


def guard_decision(root, checkpoint, config, state_path, host, payload):
    """Ask the agent to refresh a stale checkpoint at most once per checkpoint version."""
    if payload.get('stop_hook_active'):
        return None  # Already continuing because of a Stop hook; never chain blocks.
    changes = changes_since_checkpoint(root, checkpoint, config)
    if not changes or not changes['files']:
        return None
    age = (time.time() - (root / checkpoint).stat().st_mtime) / 60
    if len(changes['files']) < int(config['guard_files']) and age < float(config['guard_minutes']):
        return None
    sha = handoff.digest((root / checkpoint).read_bytes())
    try:
        if json.loads(state_path.read_text(encoding='utf-8')).get('checkpoint_sha256') == sha:
            return None  # Already asked for this checkpoint version.
    except (OSError, ValueError, AttributeError):
        pass
    handoff.atomic(state_path, json.dumps({'checkpoint_sha256': sha, 'asked_at': iso()}).encode())
    reason = ('cross-agent-handoff: {} files changed since {} was saved {:.0f} minutes ago. Update the '
              'checkpoint now with actual progress, unfinished work, evidence and one next action, then '
              'stop. This reminder is shown once per checkpoint version.').format(
                  len(changes['files']), checkpoint, age)
    return {'decision': 'continue' if host == 'antigravity' else 'block', 'reason': reason}


def snapshot(root, checkpoint, config, event, hashes):
    started = time.monotonic()
    auto = root / '.handoff' / 'auto'
    auto.mkdir(parents=True, exist_ok=True)
    ignore_file = auto / '.gitignore'
    if not ignore_file.exists():
        ignore_file.write_text('# Machine-local snapshots; do not commit.\n*\n', encoding='utf-8')
    target = root / checkpoint
    record = {'schema': SCHEMA, 'created_at': iso(), 'event': event,
              'checkpoint': {'path': checkpoint, 'exists': target.is_file()}}
    if target.is_file():
        data = target.read_bytes()
        stamp = handoff.updated_at(data.decode('utf-8', 'replace'))
        record['checkpoint'].update({'sha256': handoff.digest(data), 'mtime': iso(target.stat().st_mtime),
                                     'updated_at': stamp.isoformat() if stamp else None})
    record['git'] = git_state(root)
    window = float(config['window_minutes'])
    found, truncated, scanned = scan(root, time.time() - window * 60, config, checkpoint_ignores(checkpoint))
    record['recent_files'] = {'window_minutes': window, 'count': len(found), 'scan_truncated': truncated,
                              'entries_scanned': scanned,
                              'files': describe(root, found, config, hashes or bool(config['partial_hash']))}
    record['duration_ms'] = round((time.monotonic() - started) * 1000)
    handoff.atomic(auto / 'latest.json', (json.dumps(record, indent=2) + '\n').encode('utf-8'))
    summary = {'created_at': record['created_at'], 'event': event.get('hook_event_name') or event.get('hookEventName'),
               'error': event.get('error'), 'recent_files': len(found),
               'git_changes': len(record['git'].get('status', [])),
               'checkpoint_sha256': record['checkpoint'].get('sha256')}
    append_history(auto / 'history.jsonl', summary, int(config['history_max_lines']))
    return record


def append_history(path, summary, limit):
    with open(path, 'a', encoding='utf-8') as stream:
        stream.write(json.dumps(summary) + '\n')
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    if len(lines) > limit:
        handoff.atomic(path, ''.join(lines[-limit:]).encode('utf-8'))


def run(argv=None, stdin=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--project', help='Project directory; default: hook input, then cwd')
    parser.add_argument('--checkpoint', default='HANDOFF.md')
    parser.add_argument('--hook', action='store_true', help='Read the host hook JSON from stdin')
    parser.add_argument('--host', default='generic', choices=('generic', 'claude', 'codex', 'antigravity'))
    parser.add_argument('--partial-hash', action='store_true', help='Hash first and last 1 MB of media')
    parser.add_argument('--guard', action='store_true', help='Stop hook: ask once to refresh a stale checkpoint')
    args = parser.parse_args(argv)
    event, payload = read_event((stdin or sys.stdin).read()) if args.hook else ({}, {})
    if args.host != 'generic':
        event['host'] = args.host
    workspaces = payload.get('workspacePaths') or []
    start = (args.project or payload.get('cwd') or (workspaces[0] if workspaces else None)
             or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())
    root = find_root(start, args.checkpoint)
    if root is None:
        warn('no ' + args.checkpoint + ' or .handoff/ found from ' + str(start) + '; nothing recorded.')
        return 0
    config = load_config(root)
    snapshot(root, args.checkpoint, config, event, args.partial_hash)
    if args.guard:
        decision = guard_decision(root, args.checkpoint, config, root / '.handoff' / 'auto' / 'guard.json',
                                  args.host, payload)
        if decision:
            print(json.dumps(decision))
    return 0


def main():
    try:
        run()
    except Exception as exc:  # A hook must never break the host session.
        warn('failed: {}: {}'.format(type(exc).__name__, exc))
    return 0


if __name__ == '__main__':
    sys.exit(main())
