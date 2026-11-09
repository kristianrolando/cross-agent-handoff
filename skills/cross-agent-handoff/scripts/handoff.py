#!/usr/bin/env python3
"""Optional checkpoint mechanics. Python 3.9+, standard library only."""
import argparse
from datetime import datetime, timedelta, timezone
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
# Optional metadata added in v0.2.0. Absent fields keep v0.1.x checkpoints valid.
TIMESTAMP = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{3}|\.\d{6})?)?(?:Z|[+-]\d{2}:\d{2})')
NAME = r'[a-z0-9]+(?:-[a-z0-9]+)*'
OPTIONAL = {
    'updated_at': (None, 'an ISO 8601 time with a UTC offset, such as '
                         '2026-11-08T14:05:00+07:00 or 2026-11-08T07:05:00Z'),
    'language': (re.compile(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*'),
                 'a language code such as en, id or pt-BR'),
    'profile': (re.compile(NAME + r'(?:, *' + NAME + r')*'),
                'lowercase profile names separated by commas, such as video or game, motion'),
}
CLOCK_SKEW = timedelta(minutes=5)
WORD_TARGET = 1200  # Advisory reading budget; never a reason to drop unresolved facts.
WORD_WARNING = 'Checkpoint exceeds the 1,200-word reading target; compact only resolved detail.'
PROFILES = Path(__file__).resolve().parent.parent / 'assets' / 'profiles'


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


def parse_timestamp(value):
    """Return an aware datetime for a valid updated_at value, otherwise None."""
    value = value.strip()
    if not TIMESTAMP.fullmatch(value):
        return None
    try:  # Python 3.9 fromisoformat does not accept a trailing Z.
        return datetime.fromisoformat(value[:-1] + '+00:00' if value.endswith('Z') else value)
    except ValueError:
        return None


def updated_at(text):
    """The checkpoint's optional updated_at as an aware datetime, or None."""
    values = fields(text.replace('\r\n', '\n'), 'updated_at')
    return parse_timestamp(values[0]) if len(values) == 1 else None


def validate_optional(text):
    errors = []
    for key, (pattern, expected) in OPTIONAL.items():
        values = [value.strip() for value in fields(text, key)]
        if len(values) > 1:
            errors.append('Expected at most one ' + key)
        elif values:
            valid = parse_timestamp(values[0]) if key == 'updated_at' else pattern.fullmatch(values[0])
            if not valid:
                errors.append(key + ' must be ' + expected + '; got ' + repr(values[0]))
    return errors


def profile_names(text):
    values = fields(text.replace('\r\n', '\n'), 'profile')
    return [name.strip() for name in values[0].split(',')] if len(values) == 1 else []


def with_profiles(template, names):
    """Insert profile sections after State and record them in the metadata."""
    available = sorted(path.stem for path in PROFILES.glob('*.md'))
    unknown = [name for name in names if name not in available]
    if unknown:
        raise ValueError('Unknown profile(s): {}. Available: {}'.format(', '.join(unknown), ', '.join(available)))
    crlf = '\r\n' in template  # Windows checkouts may convert line endings; keep the template's style.
    template = template.replace('\r\n', '\n')
    sections = ''.join((PROFILES / (name + '.md')).read_text(encoding='utf-8').replace('\r\n', '\n').rstrip('\n')
                       + '\n\n' for name in names)
    marker = '\n## Evidence\n'
    if marker not in template or '\n- writer: ' not in template:
        raise ValueError('Template lacks the writer line or Evidence section')
    template = template.replace(marker, '\n' + sections.rstrip('\n') + '\n' + marker, 1)
    head, rest = template.split('\n- writer: ', 1)
    line, rest = rest.split('\n', 1)
    updated = rest.split('\n', 1) if rest.startswith('- updated_at: ') else None
    if updated:
        result = '{}\n- writer: {}\n{}\n- profile: {}\n{}'.format(head, line, updated[0], ', '.join(names), updated[1])
    else:
        result = '{}\n- writer: {}\n- profile: {}\n{}'.format(head, line, ', '.join(names), rest)
    return result.replace('\n', '\r\n') if crlf else result


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
    errors.extend(validate_optional(text))
    for section in SECTIONS:
        pattern = r'^## ' + re.escape(section) + r'\n(.*?)(?=^## |\Z)'
        found = re.findall(pattern, text, re.M | re.S)
        if len(found) != 1 or not found[0].strip():
            errors.append('Expected one nonempty section: ' + section)
    # Match template placeholders only, so project terms such as SQL REPLACE stay valid.
    if re.search(r'\bREPLACE (?:with|from)\b', text):
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
            warnings.append('Invalid file observation ({}): write it as one JSON object from inspect, for example '
                            '- observed_file: {{"path":"src/app.py","sha256":"..."}}; or drop the line.'.format(exc))
    for name in profile_names(text):
        if not re.search(r'^## Profile: ' + re.escape(name) + r'\s*$', text, re.M):
            warnings.append('profile lists ' + name + ' but the checkpoint has no "## Profile: ' + name + '" section.')
    saved = updated_at(text)
    if saved and saved > datetime.now(timezone.utc) + CLOCK_SKEW:
        warnings.append('updated_at is in the future; check the clock or the recorded time.')
    if len(text.split()) > WORD_TARGET:
        warnings.append(WORD_WARNING)
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
        content = template.read_bytes()
        names = [name.strip() for name in (args.profile or '').split(',') if name.strip()]
        if names:
            content = with_profiles(content.decode('utf-8'), list(dict.fromkeys(names))).encode('utf-8')
        with target.open('xb') as stream:
            stream.write(content)
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
    try:
        lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError('Save lock exists: ' + lock.name + '. Another helper save may be running, or an '
                         'interrupted save left it. Establish inactivity before removing it; it is never stolen by age.')
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
    parser.add_argument('--profile', help='init: comma-separated profiles from assets/profiles, e.g. video,motion')
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
