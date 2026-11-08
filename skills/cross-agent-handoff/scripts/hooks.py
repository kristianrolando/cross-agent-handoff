#!/usr/bin/env python3
"""Opt-in host hooks for mechanical snapshots. Python 3.9+, standard library only.

install merges this skill's hook entries into a project's host configuration without
touching other entries; remove deletes only those entries; status reports them. Nothing
is installed without an explicit command and confirmation (or --yes). Event names and
file formats follow official host documentation checked on 2026-11-08; see
references/hooks.md for verified and unverified behavior.
"""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cross_agent_handoff_helper', HERE / 'handoff.py')
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)

SKILL = 'cross-agent-handoff'
OURS = re.compile(r'cross-agent-handoff[/\\]scripts[/\\](?:snapshot|inject)\.py')
ANTIGRAVITY_KEY = 'cross-agent-handoff'
HOSTS = {
    # host: (config file, default skill copy, events -> script arguments)
    'claude': ('.claude/settings.local.json', '.claude/skills/' + SKILL, {
        'SessionStart': ('inject.py', '--hook'),
        'Stop': ('snapshot.py', '--hook --host claude'),
        'StopFailure': ('snapshot.py', '--hook --host claude'),
        'PreCompact': ('snapshot.py', '--hook --host claude')}),
    'codex': ('.codex/hooks.json', '.agents/skills/' + SKILL, {
        'SessionStart': ('inject.py', '--hook'),
        'Stop': ('snapshot.py', '--hook --host codex'),
        'PreCompact': ('snapshot.py', '--hook --host codex')}),
    'antigravity': ('.agents/hooks.json', '.agents/skills/' + SKILL, {
        'SessionStart': ('inject.py', '--hook --format antigravity'),
        'Stop': ('snapshot.py', '--hook --host antigravity')}),
}
NOTES = {
    'claude': 'Claude Code reads .claude/settings.local.json for this project on this machine only. '
              'Run /hooks in Claude Code to see the active hooks.',
    'codex': 'Codex runs project hooks only in a trusted project after you review and trust them: '
             'open /hooks in Codex. Commands use absolute paths; rerun install if the project moves.',
    'antigravity': 'Antigravity reads .agents/hooks.json in the App, IDE and CLI. Commands use '
                   'absolute paths; rerun install if the project moves. SessionStart context '
                   'injection is unverified in a live session.',
}


class HookError(Exception):
    pass


def config_path(root, host, shared=False):
    if host == 'claude' and shared:
        return root / '.claude' / 'settings.json'
    return root / HOSTS[host][0]


def default_python():
    return 'python' if os.name == 'nt' else 'python3'


def command(root, host, skill_dir, script, arguments, python):
    if host == 'claude':
        path = '$CLAUDE_PROJECT_DIR/' + Path(skill_dir).as_posix() + '/scripts/' + script
    else:
        path = str(root / skill_dir / 'scripts' / script)
    if '"' in path:
        raise HookError('Project paths containing double quotes are not supported.')
    return '{} "{}" {}'.format(python, path, arguments)


def load(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        raise HookError('{} is not valid JSON ({}); fix it before installing hooks. Nothing changed.'.format(path, exc))
    if not isinstance(data, dict):
        raise HookError('{} does not contain a JSON object; nothing changed.'.format(path))
    return data


def is_ours(handler):
    return isinstance(handler, dict) and bool(OURS.search(str(handler.get('command', ''))))


def strip(data, host):
    """Return a copy without this skill's entries, and how many were removed."""
    data = copy.deepcopy(data)
    if host == 'antigravity':
        return data, int(data.pop(ANTIGRAVITY_KEY, None) is not None)
    removed = 0
    events = data.get('hooks')
    if not isinstance(events, dict):
        return data, 0
    for event in list(events):
        groups = events[event] if isinstance(events[event], list) else []
        kept = []
        for group in groups:
            handlers = group.get('hooks') if isinstance(group, dict) else None
            if not isinstance(handlers, list):
                kept.append(group)
                continue
            remaining = [handler for handler in handlers if not is_ours(handler)]
            removed += len(handlers) - len(remaining)
            if remaining:
                kept.append(dict(group, hooks=remaining))
        if kept:
            events[event] = kept
        elif groups:
            del events[event]
    if not events:
        del data['hooks']
    return data, removed


def entries(root, host, skill_dir, python, guard):
    handlers = {}
    for event, (script, arguments) in HOSTS[host][2].items():
        if guard and event == 'Stop':
            arguments += ' --guard'
        handler = {'type': 'command', 'command': command(root, host, skill_dir, script, arguments, python),
                   'timeout': 30}
        if host == 'codex':
            handler['commandWindows'] = command(root, host, skill_dir, script, arguments, 'py -3')
        handlers[event] = handler
    return handlers


def merged(data, root, host, skill_dir, python, guard):
    data, _ = strip(data, host)
    handlers = entries(root, host, skill_dir, python, guard)
    if host == 'antigravity':
        data[ANTIGRAVITY_KEY] = {event: [handler] for event, handler in handlers.items()}
        return data
    events = data.setdefault('hooks', {})
    if not isinstance(events, dict):
        raise HookError('The "hooks" value is not an object; nothing changed.')
    for event, handler in handlers.items():
        if not isinstance(events.setdefault(event, []), list):
            raise HookError('The "{}" hook value is not a list; nothing changed.'.format(event))
        events[event].append({'hooks': [handler]})
    return data


def present(data, host):
    return strip(data, host)[1] > 0


def referenced_scripts(data, host):
    if host == 'antigravity':
        groups = (data.get(ANTIGRAVITY_KEY) or {}).values()
        handlers = [handler for group in groups for handler in group]
    else:
        handlers = [handler for groups in (data.get('hooks') or {}).values() for group in groups
                    if isinstance(group, dict) for handler in group.get('hooks') or []]
    return [handler['command'] for handler in handlers if is_ours(handler)]


def script_path(root, text):
    match = re.search(r'"([^"]+)"', text)
    path = match[1] if match else ''
    return Path(path.replace('$CLAUDE_PROJECT_DIR', str(root))) if path else None


def ignored_by_git(root, path):
    try:
        result = subprocess.run(['git', '-C', str(root), 'check-ignore', '-q', str(path)],
                                capture_output=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {0: True, 1: False}.get(result.returncode)


def confirm(message, assume_yes):
    if assume_yes:
        return True
    required = 'Confirmation required: rerun with --yes after reviewing the change, or use --dry-run.'
    if not sys.stdin.isatty():
        raise HookError(required)
    try:
        return input(message + ' [y/N] ').strip().lower() in ('y', 'yes')
    except EOFError:  # Windows NUL reports isatty() but has no input.
        raise HookError(required)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    handoff.atomic(path, (json.dumps(data, indent=2) + '\n').encode('utf-8'))


def status(root, host, shared):
    path = config_path(root, host, shared)
    report = {'host': host, 'config': path.relative_to(root).as_posix(), 'exists': path.exists()}
    data = load(path)
    commands = referenced_scripts(data, host)
    report['installed'] = bool(commands)
    report['missing_scripts'] = sorted({str(script_path(root, text)) for text in commands
                                        if not (script_path(root, text) or Path()).is_file()})
    if path.exists():
        report['ignored_by_git'] = ignored_by_git(root, path)
    return report


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('action', choices=('install', 'remove', 'status'))
    parser.add_argument('--project', default='.')
    parser.add_argument('--host', action='append', choices=sorted(HOSTS), required=True)
    parser.add_argument('--skill-dir', help='Project-relative skill copy; default: the host location')
    parser.add_argument('--python', default=default_python(), help='Interpreter command written into hooks')
    parser.add_argument('--guard', action='store_true', help='Also ask once to refresh a stale checkpoint on Stop')
    parser.add_argument('--shared', action='store_true', help='Claude: write .claude/settings.json instead of settings.local.json')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--yes', action='store_true', help='Skip the confirmation prompt')
    args = parser.parse_args(argv)
    root = Path(args.project).resolve()
    if not root.is_dir():
        raise HookError('Project must be an existing directory.')
    for host in dict.fromkeys(args.host):
        path = config_path(root, host, args.shared)
        if args.action == 'status':
            print(json.dumps(status(root, host, args.shared), indent=2))
            continue
        data = load(path)
        if args.action == 'install':
            skill_dir = args.skill_dir or HOSTS[host][1]
            missing = [name for name in ('snapshot.py', 'inject.py', 'handoff.py')
                       if not (root / skill_dir / 'scripts' / name).is_file()]
            if missing:
                raise HookError('{} lacks {}; install the skill for {} first or pass --skill-dir.'.format(
                    skill_dir, ', '.join(missing), host))
            result = merged(data, root, host, skill_dir, args.python, args.guard)
        else:
            result, removed = strip(data, host)
            if not removed:
                print('{}: no cross-agent-handoff hooks in {}; nothing to remove.'.format(host, path.relative_to(root)))
                continue
        if result == data:
            print('{}: {} already up to date.'.format(host, path.relative_to(root)))
            continue
        print('{} {} hooks in {}:'.format('Would update' if args.dry_run else 'Updating', host, path.relative_to(root)))
        print(json.dumps(result, indent=2))
        if args.dry_run:
            continue
        if not confirm('Write this file?', args.yes):
            print('Skipped {}.'.format(host))
            continue
        write(path, result)
        print('Done. ' + NOTES[host] if args.action == 'install' else 'Removed.')
        if args.action == 'install' and not args.shared and ignored_by_git(root, path) is False:
            print('Note: {} holds personal, machine-specific hook settings and is not ignored by Git; '
                  'consider adding it to .gitignore.'.format(path.relative_to(root)))
    return 0


def main():
    try:
        return run()
    except HookError as exc:
        print('hooks: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
