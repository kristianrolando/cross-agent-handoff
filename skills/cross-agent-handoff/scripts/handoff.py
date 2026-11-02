#!/usr/bin/env python3
"""Optional checkpoint mechanics. Python 3.9+, standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SECTIONS = ('Project', 'Task', 'State', 'Evidence', 'Next', 'Recent outcomes')
VALUES = {'format': {'cross-agent-handoff/1'},
          'task_status': {'in_progress', 'partial', 'blocked', 'done', 'superseded'},
          'handoff': {'working', 'ready', 'recovery'}}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(root, name):
    path = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Use a project-relative path without parent traversal.')
    if path.is_symlink() or root not in path.resolve().parents:
        raise ValueError('Path must resolve inside the project and not be a symlink.')
    return path


def fields(text, key):
    return re.findall(r'^- ' + re.escape(key) + r': (.+)$', text, re.M)


def validate(text):
    text = text.replace('\r\n', '\n')
    errors = []
    for key, choices in VALUES.items():
        values = fields(text, key)
        if len(values) != 1 or values[0] not in choices:
            errors.append('Expected one valid ' + key)
    writers = fields(text, 'writer')
    if len(writers) != 1 or not writers[0].strip():
        errors.append('Expected one nonempty writer')
    if fields(text, 'handoff') == ['ready'] and writers != ['none']:
        errors.append('ready requires writer: none; process inactivity still needs human/agent verification')
    for section in SECTIONS:
        pattern = r'^## ' + re.escape(section) + r'\n(.*?)(?=^## |\Z)'
        found = re.findall(pattern, text, re.M | re.S)
        if len(found) != 1 or not found[0].strip():
            errors.append('Expected one nonempty section: ' + section)
    if 'REPLACE' in text:
        errors.append('Unfilled template: replace every REPLACE instruction')
    if text.count('```') % 2:
        errors.append('Unbalanced code fences')
    return errors


def observations(root, text):
    warnings = []
    for raw in fields(text, 'observed_file'):
        try:
            record = json.loads(raw)
            path = local(root, record['path'])
            if not path.is_file() or digest(path.read_bytes()) != record['sha256']:
                warnings.append('Observed file changed or is missing: ' + record['path'])
        except (ValueError, KeyError, TypeError, OSError) as exc:
            warnings.append('Invalid file observation: ' + str(exc))
    if len(text.split()) > 1200:
        warnings.append('Checkpoint exceeds the 1,200-word reading target; compact only resolved detail.')
    return warnings


def atomic(path, data):
    """Replace one file; not a multi-file transaction or power-loss guarantee."""
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def git_info(root):
    def run(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=10)
        return result.stdout.rstrip('\n') if result.returncode == 0 else None
    try:
        top = run('rev-parse', '--show-toplevel')
        if top is None:
            return {'available': False, 'reason': 'No Git repository at this project'}
        status = run('status', '--short', '--untracked-files=normal')
        lines = status.splitlines() if status else []
        return {'available': True, 'root': top, 'head': run('rev-parse', 'HEAD'),
                'branch': run('branch', '--show-current'), 'status': lines[:100],
                'status_truncated': len(lines) > 100,
                'note': 'Status includes enclosing repository; inspect diffs and relevant untracked contents separately.'}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'available': False, 'reason': str(exc)}


def execute(args):
    root = Path(args.project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Project must be a directory')
    target = local(root, args.checkpoint)
    if not target.parent.is_dir():
        raise ValueError('Checkpoint parent directory must already exist')
    if args.command == 'init':
        template = Path(__file__).resolve().parent.parent / 'assets' / 'checkpoint.md'
        with target.open('xb') as stream:
            stream.write(template.read_bytes())
        print('Created a draft; fill every REPLACE field before check/save. Existing instructions were not edited.')
        return 0
    if args.command == 'inspect':
        output = {'project': str(root), 'checkpoint': args.checkpoint,
                  'sha256': digest(target.read_bytes()) if target.is_file() else None,
                  'git': git_info(root), 'observations': []}
        for name in args.file:
            path = local(root, name)
            output['observations'].append({'path': name, 'sha256': digest(path.read_bytes())})
        print(json.dumps(output, indent=2))
        return 0
    if args.command == 'check':
        text = target.read_text(encoding='utf-8')
        errors, warnings = validate(text), observations(root, text)
        print(json.dumps({'errors': errors, 'warnings': warnings,
                          'sha256': digest(target.read_bytes()),
                          'limits': 'Checks structure and explicit observed_file hashes only; not intent, completeness, writer inactivity or test truth.'}, indent=2))
        return 2 if errors else (1 if warnings else 0)
    # Single helper writer guard, not a project lock. Never steal it by age.
    lock = target.with_name('.' + target.name + '.save-lock')
    lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(lock_fd, 'w') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'checkpoint': args.checkpoint}))
        current = target.read_bytes()
        if digest(current) != args.expected_sha:
            raise ValueError('Stale checkpoint: reread and reconcile before saving.')
        candidate = Path(args.candidate).read_bytes()
        errors = validate(candidate.decode('utf-8'))
        if errors:
            raise ValueError('; '.join(errors))
        # Verify candidate before touching the backup or live checkpoint.
        backup = local(root, args.checkpoint + '.previous')
        atomic(backup, current)
        atomic(target, candidate)
        print(json.dumps({'saved': args.checkpoint, 'sha256': digest(candidate),
                          'previous': args.checkpoint + '.previous'}))
    finally:
        lock.unlink()
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'inspect', 'check', 'save'))
    parser.add_argument('--project', required=True)
    parser.add_argument('--checkpoint', default='HANDOFF.md')
    parser.add_argument('--file', action='append', default=[])
    parser.add_argument('--candidate')
    parser.add_argument('--expected-sha')
    args = parser.parse_args()
    if args.command == 'save' and (not args.candidate or not args.expected_sha):
        parser.error('save requires --candidate and --expected-sha from inspect')
    try:
        return execute(args)
    except (OSError, ValueError, UnicodeError) as exc:
        print('handoff: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
