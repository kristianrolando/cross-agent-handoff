#!/usr/bin/env python3
"""Install, update, check or remove project copies of this skill. Python 3.9+, standard library only.

One command places the complete skill in every folder the chosen hosts read, so all copies
stay on one version. Copies are plain directories (no symlinks). Each installed copy gets
VERSION and MANIFEST.sha256 so --doctor can detect edits, drift and missing copies.
Uninstall removes only verified copies of this skill and its own hook entries; it never
deletes HANDOFF.md, .handoff/ records or other project data.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
NAME = 'cross-agent-handoff'
MANIFEST = 'MANIFEST.sha256'
SKIP = {'__pycache__', '.DS_Store', MANIFEST}
HOOK_HOSTS = ('claude', 'codex', 'antigravity')
# Fewest folders that reach each host, from references/agents.md (rechecked 2026-11-02).
PROJECT = {'claude': '.claude/skills', 'codex': '.agents/skills', 'antigravity': '.agents/skills',
           'cursor': '.agents/skills', 'gemini': '.agents/skills', 'copilot': '.agents/skills',
           'opencode': '.agents/skills', 'cline': '.claude/skills'}
USER = {'claude': '.claude/skills', 'codex': '.agents/skills', 'antigravity': '.gemini/config/skills',
        'cursor': '.agents/skills', 'gemini': '.agents/skills', 'copilot': '.agents/skills',
        'opencode': '.agents/skills', 'cline': '.cline/skills'}
# Other documented project folders where an existing copy may live (checked by --doctor).
KNOWN_PROJECT = ('.claude/skills', '.agents/skills', '.agent/skills', '.cursor/skills', '.gemini/skills',
                 '.github/skills', '.opencode/skills', '.cline/skills', '.clinerules/skills')


class InstallError(Exception):
    pass


def load_hooks():
    spec = importlib.util.spec_from_file_location('cross_agent_handoff_hooks', HERE / 'hooks.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def files(root):
    """Relative POSIX paths of skill files, excluding caches and the manifest."""
    found = []
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if path.is_symlink():
            raise InstallError('Refusing symlink in skill copy: ' + str(path))
        if path.is_file() and not SKIP.intersection(rel.parts) and not path.name.endswith('.pyc'):
            found.append(rel.as_posix())
    return found


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {rel: sha256(root / rel) for rel in files(root)}


def digest(table):
    return hashlib.sha256(''.join(h + '  ' + p + '\n' for p, h in sorted(table.items())).encode()).hexdigest()


def manifest_text(table):
    return ''.join(table[rel] + '  ' + rel + '\n' for rel in sorted(table))


def read_manifest(root):
    path = root / MANIFEST
    if not path.is_file():
        return None
    table = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            value, rel = line.split('  ', 1)
            table[rel] = value
    return table


def version(root):
    path = root / 'VERSION'
    return path.read_text(encoding='utf-8').strip() if path.is_file() else None


def is_our_skill(path):
    entry = path / 'SKILL.md'
    try:
        head = entry.read_text(encoding='utf-8')[:400]
    except OSError:
        return False
    return path.is_dir() and not path.is_symlink() and '\nname: ' + NAME + '\n' in head


def inspect(path):
    """Describe one installed copy: version, edits against its manifest, content digest."""
    table = hashes(path)
    record = {'path': str(path), 'version': version(path) or 'unknown (v0.1.x or another installer)',
              'digest': digest(table), 'files': len(table)}
    manifest = read_manifest(path)
    if manifest is None:
        record['manifest'] = 'absent'
    else:
        changed = sorted(rel for rel in manifest if rel in table and table[rel] != manifest[rel])
        missing = sorted(set(manifest) - set(table))
        extra = sorted(set(table) - set(manifest))
        record['manifest'] = 'ok' if not (changed or missing or extra) else 'differs'
        record.update({key: value for key, value in
                       (('changed', changed), ('missing', missing), ('extra', extra)) if value})
    return record


def shown(path, base):
    try:
        return Path(path).relative_to(base).as_posix()
    except ValueError:
        return str(path)


def destinations(base, hosts, table):
    plan = {}
    for host in hosts:
        plan.setdefault((base / table[host] / NAME), []).append(host)
    return plan


def same_or_nested(a, b):
    a, b = a.resolve(), b.resolve()
    return a == b or a in b.parents or b in a.parents


def copy_into(dest, source_table):
    """Build a complete copy next to dest, then swap it in; the old copy is removed last."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.' + NAME + '-new-', dir=str(dest.parent)))
    try:
        for rel in source_table:
            target = staging / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / rel, target)
        (staging / MANIFEST).write_text(manifest_text(source_table), encoding='utf-8')
        old = None
        if dest.exists():
            old = Path(tempfile.mkdtemp(prefix='.' + NAME + '-old-', dir=str(dest.parent)))
            old.rmdir()
            dest.rename(old)
        staging.rename(dest)
        if old is not None:
            shutil.rmtree(old)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def confirm(message, assume_yes):
    if assume_yes:
        return True
    required = 'Confirmation required: rerun with --yes after reviewing the plan, or use --dry-run.'
    if not sys.stdin.isatty():
        raise InstallError(required)
    try:
        return input(message + ' [y/N] ').strip().lower() in ('y', 'yes')
    except EOFError:
        raise InstallError(required)


def install(base, hosts, args, user):
    source_table = hashes(SOURCE)
    source_digest = digest(source_table)
    replace = []
    for dest, owners in destinations(base, hosts, USER if user else PROJECT).items():
        label = '{} ({})'.format(shown(dest, base), ', '.join(owners))
        if same_or_nested(dest, SOURCE):
            if dest.resolve() == SOURCE.resolve():
                print('Source copy, left as is: ' + label)
                continue
            raise InstallError('Refusing to nest a copy inside another: ' + label)
        if not dest.exists():
            print(('Would install ' if args.dry_run else 'Installing ') + label)
            if not args.dry_run:
                copy_into(dest, source_table)
            continue
        if not is_our_skill(dest):
            raise InstallError(str(dest) + ' exists but is not a ' + NAME + ' skill copy; nothing changed.')
        current = inspect(dest)
        if current['digest'] == source_digest and current['manifest'] == 'ok':
            print('Up to date: ' + label)
            continue
        if not args.update:
            print('Differs from source ({}, manifest {}): {}. Rerun with --update to replace it.'.format(
                current['version'], current['manifest'], label))
            continue
        replace.append((dest, label, current))
    if replace:
        for dest, label, current in replace:
            edits = current.get('changed', []) + current.get('extra', [])
            print('{} {} -> {}: {}'.format('Would replace' if args.dry_run else 'Replace', current['version'],
                                          version(SOURCE), label))
            if edits:
                print('  Local changes that will be lost: ' + ', '.join(edits))
            if current['manifest'] == 'absent':
                print('  No manifest: local edits cannot be detected; review before replacing.')
        if not args.dry_run and confirm('Replace these copies?', args.yes):
            for dest, label, _ in replace:
                copy_into(dest, source_table)
                print('Updated: ' + label)
    if args.with_hooks and not user:
        hook_hosts = [host for host in hosts if host in HOOK_HOSTS]
        if hook_hosts:
            hook_args = ['install', '--project', str(base)]
            for host in hook_hosts:
                hook_args += ['--host', host]
            hook_args += [flag for flag, on in (('--dry-run', args.dry_run), ('--yes', args.yes),
                                                ('--guard', args.guard)) if on]
            load_hooks().run(hook_args)
    return 0


def found_copies(base, user):
    parents = sorted(set(USER.values())) if user else KNOWN_PROJECT
    return [base / parent / NAME for parent in parents if is_our_skill(base / parent / NAME)]


def uninstall(base, hosts, args, user):
    table = USER if user else PROJECT
    targets = destinations(base, hosts, table) if hosts else {path: [] for path in found_copies(base, user)}
    remove = [path for path in targets if is_our_skill(path) and not same_or_nested(path, SOURCE)]
    for path in remove:
        sharing = sorted(host for host, parent in table.items() if base / parent / NAME == path)
        print('{} {} (read by: {})'.format('Would remove' if args.dry_run else 'Remove', shown(path, base),
                                          ', '.join(sharing) or 'unknown'))
    hook_hosts = [host for host in (hosts or HOOK_HOSTS) if host in HOOK_HOSTS] if not user else []
    if not remove and not hook_hosts:
        print('Nothing to remove.')
        return 0
    if hook_hosts:
        print('{} this skill\'s hook entries for: {}'.format('Would remove' if args.dry_run else 'Remove',
                                                            ', '.join(hook_hosts)))
    if args.dry_run:
        return 0
    if not confirm('Remove these? HANDOFF.md, .handoff/ and other project files are kept.', args.yes):
        print('Skipped.')
        return 0
    hooks = load_hooks()
    for host in hook_hosts:  # Hook entries first, so no hook points at a removed script.
        hooks.run(['remove', '--project', str(base), '--host', host, '--yes'])
    for path in remove:
        shutil.rmtree(path)
        print('Removed ' + shown(path, base))
    return 0


def ignored(base, rel):
    try:
        result = subprocess.run(['git', '-C', str(base), 'check-ignore', '-q', rel], capture_output=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {0: True, 1: False}.get(result.returncode)


def doctor(base, hosts, args, user):
    problems, warnings = [], []
    copies = [dict(inspect(path), path=shown(path, base)) for path in found_copies(base, user)]
    if hosts:
        for dest, owners in destinations(base, hosts, USER if user else PROJECT).items():
            if not is_our_skill(dest):
                problems.append('Missing copy for {}: {}'.format(', '.join(owners), shown(dest, base)))
    if not copies and not hosts:
        warnings.append('No installed copy found in the known {} folders.'.format('user' if user else 'project'))
    for record in copies:
        if record['manifest'] == 'differs':
            warnings.append('Edited copy {}: changed {}, missing {}, extra {}'.format(
                record['path'], record.get('changed', []), record.get('missing', []), record.get('extra', [])))
        elif record['manifest'] == 'absent':
            warnings.append('No manifest in {} ({}); run --update to make it checkable.'.format(
                record['path'], record['version']))
    if len({record['digest'] for record in copies}) > 1:
        warnings.append('Copies differ from each other (drift); run --update to align them.')
    hook_reports = []
    if not user:
        hooks = load_hooks()
        for host in HOOK_HOSTS:
            report = hooks.status(base, host, False)
            if report['installed']:
                hook_reports.append(report)
                if report['missing_scripts']:
                    problems.append('{} hooks reference missing scripts: {}'.format(host, report['missing_scripts']))
                if report.get('ignored_by_git') is False:
                    warnings.append('{} holds personal hook settings and is not ignored by Git.'.format(report['config']))
        if (base / '.handoff' / 'auto').is_dir() and ignored(base, '.handoff/auto/latest.json') is False:
            warnings.append('.handoff/auto/ is not ignored by Git; restore its .gitignore file.')
    result = {'copies': copies, 'hooks': hook_reports, 'problems': problems, 'warnings': warnings,
              'source_version': version(SOURCE)}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for record in copies:
            print('{}  version {}  manifest {}  digest {}'.format(record['path'], record['version'],
                                                                 record['manifest'], record['digest'][:12]))
        for report in hook_reports:
            print('hooks: {} in {}'.format(report['host'], report['config']))
        for item in problems:
            print('PROBLEM: ' + item)
        for item in warnings:
            print('WARNING: ' + item)
        if not problems and not warnings:
            print('Healthy.')
    return 2 if problems else (1 if warnings else 0)


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--project', default='.', help='Project directory (default: current directory)')
    parser.add_argument('--hosts', help='Comma-separated: ' + ','.join(PROJECT))
    parser.add_argument('--user', action='store_true', help='Use user-wide folders instead of the project')
    parser.add_argument('--update', action='store_true', help='Replace copies that differ from this source')
    parser.add_argument('--uninstall', action='store_true')
    parser.add_argument('--doctor', action='store_true')
    parser.add_argument('--with-hooks', action='store_true', help='Also install opt-in hooks (Claude, Codex, Antigravity)')
    parser.add_argument('--guard', action='store_true', help='With --with-hooks: add the staleness guard')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--json', action='store_true', help='Doctor output as JSON')
    args = parser.parse_args(argv)
    hosts = [item.strip().lower() for item in (args.hosts or '').split(',') if item.strip()]
    unknown = sorted(set(hosts) - set(PROJECT))
    if unknown:
        raise InstallError('Unknown host(s): {}. Use: {}'.format(', '.join(unknown), ', '.join(PROJECT)))
    hosts = list(dict.fromkeys(hosts))
    base = Path.home() if args.user else Path(args.project).resolve()
    if not base.is_dir():
        raise InstallError('Project must be an existing directory.')
    if args.doctor:
        return doctor(base, hosts, args, args.user)
    if args.uninstall:
        return uninstall(base, hosts, args, args.user)
    if not hosts:
        raise InstallError('Choose hosts with --hosts, for example --hosts claude,codex,antigravity.')
    return install(base, hosts, args, args.user)


def main():
    try:
        return run()
    except (InstallError, OSError) as exc:
        print('install: ' + str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # hooks.HookError and other reported failures.
        if type(exc).__name__ == 'HookError':
            print('install: ' + str(exc), file=sys.stderr)
            return 2
        raise


if __name__ == '__main__':
    sys.exit(main())
