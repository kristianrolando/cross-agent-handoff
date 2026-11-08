#!/usr/bin/env python3
"""Advisory single-writer lock and switch log. Python 3.9+, standard library only.

The lock in .handoff/lock.json is a shared note, not enforcement: it cannot stop an agent
or a person from editing files. It makes a second writer visible. A held lock is never
taken over without --confirm-takeover, which an agent passes only after the user confirms
that the previous session has stopped. A stale heartbeat alone does not prove that.
Each acquisition appends one line to .handoff/log.jsonl.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cross_agent_handoff_snapshot', HERE / 'snapshot.py')
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)
handoff = snapshot.handoff

SCHEMA = 'cross-agent-handoff/lock-1'
REASONS = ('limit', 'manual', 'crash', 'new-session', 'unknown')
ALIAS = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,39}')
DEFAULT_STALE_MINUTES = 10


class LockError(Exception):
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def paths(root):
    folder = root / '.handoff'
    return folder / 'lock.json', folder / 'log.jsonl'


def identity(agent, alias):
    alias = alias or os.environ.get('HANDOFF_AGENT_ALIAS') or None
    for label, value in (('agent', agent), ('alias', alias)):
        if value is not None and not ALIAS.fullmatch(value):
            raise LockError('{} must be a short label of letters, digits, ".", "_" or "-" (no emails or '
                            'personal data); got {!r}'.format(label, value))
    return {'agent': agent, 'alias': alias}


def label(record):
    return record['agent'] + ('/' + record['alias'] if record.get('alias') else '')


def read_lock(root):
    path = paths(root)[0]
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or 'agent' not in data:
            raise ValueError('missing agent')
        return data
    except (OSError, ValueError) as exc:
        return {'agent': 'unknown', 'alias': None, 'invalid': str(exc)}


def heartbeat_age(record):
    try:
        moment = datetime.fromisoformat(record['heartbeat'])
        return max(0.0, (time.time() - moment.timestamp()) / 60)
    except (KeyError, TypeError, ValueError):
        return None


def state(root, stale_minutes):
    record = read_lock(root)
    if record is None:
        return {'state': 'free'}
    age = heartbeat_age(record)
    fresh = age is not None and age < stale_minutes
    return {'state': 'fresh' if fresh else 'stale', 'holder': label(record), 'lock': record,
            'heartbeat_minutes': None if age is None else round(age, 1)}


def ensure_ignored(root):
    """Keep the machine-local lock out of Git without editing the project's .gitignore."""
    ignore = root / '.handoff' / '.gitignore'
    lines = ignore.read_text(encoding='utf-8').splitlines() if ignore.is_file() else []
    if 'lock.json' not in lines:
        with open(ignore, 'a', encoding='utf-8') as stream:
            if not lines:
                stream.write('# Machine-local continuity files; log.jsonl stays committed.\n')
            stream.write('lock.json\n')


def append_log(root, entry):
    with open(paths(root)[1], 'a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry) + '\n')


def last_writer(root):
    try:
        lines = paths(root)[1].read_text(encoding='utf-8').splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            return json.loads(line).get('to')
        except ValueError:
            continue
    return None


def checkpoint_sha(root, checkpoint):
    path = root / checkpoint
    return handoff.digest(path.read_bytes()) if path.is_file() else None


def new_record(who, host):
    now = snapshot.iso()
    return {'schema': SCHEMA, 'agent': who['agent'], 'alias': who['alias'], 'host': host,
            'started_at': now, 'heartbeat': now}


def acquire(root, who, host, reason, confirm, stale_minutes, checkpoint):
    lock_path, _ = paths(root)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    ensure_ignored(root)
    current = state(root, stale_minutes)
    takeover = False
    if current['state'] != 'free':
        held = current['lock']
        if held.get('agent') == who['agent'] and held.get('alias') == who['alias'] and 'invalid' not in held:
            refresh(root, held)
            return {'result': 'already-held', 'holder': label(held)}
        if not confirm:
            if current['state'] == 'fresh':
                message = ('Lock held by {} (heartbeat {} min ago). Another session may still be writing. Ask the '
                           'user to confirm it has stopped, then rerun with --confirm-takeover.')
            else:
                message = ('Lock held by {} is stale (heartbeat {} min ago), but a stale heartbeat does not prove '
                           'that session stopped. Ask the user to confirm, then rerun with --confirm-takeover.')
            raise LockError(message.format(current['holder'], current.get('heartbeat_minutes')), code=3)
        takeover = True
    record = new_record(who, host)
    data = (json.dumps(record, indent=2) + '\n').encode('utf-8')
    if takeover:
        handoff.atomic(lock_path, data)
    else:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            raise LockError('Another session acquired the lock at the same moment; check status again.', code=3)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
    previous = current.get('holder') if takeover else last_writer(root)
    entry = {'at': record['started_at'], 'from': previous, 'to': label(record), 'reason': reason,
             'reason_source': 'reported', 'takeover': takeover,
             'checkpoint_sha256': checkpoint_sha(root, checkpoint)}
    if takeover:
        entry['previous_state'] = current['state']
    append_log(root, entry)
    return {'result': 'taken-over' if takeover else 'acquired', 'holder': label(record), 'log': entry}


def refresh(root, record):
    record = dict(record, heartbeat=snapshot.iso())
    handoff.atomic(paths(root)[0], (json.dumps(record, indent=2) + '\n').encode('utf-8'))


def release(root, who, force):
    record = read_lock(root)
    if record is None:
        return {'result': 'free'}
    ours = record.get('agent') == who['agent'] and record.get('alias') == who['alias']
    if not ours and not force:
        raise LockError('Lock is held by {}, not {}; nothing released. Use force-release only after the user '
                        'confirms that session has stopped.'.format(label(record), label(who)), code=3)
    paths(root)[0].unlink()
    if not ours:
        append_log(root, {'at': snapshot.iso(), 'from': label(record), 'to': None, 'reason': 'force-release',
                          'reason_source': 'reported', 'takeover': False, 'checkpoint_sha256': None})
    return {'result': 'released', 'holder': label(record)}


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('action', choices=('status', 'acquire', 'release', 'force-release'))
    parser.add_argument('--project', default='.')
    parser.add_argument('--checkpoint', default='HANDOFF.md')
    parser.add_argument('--agent', help='Agent label, for example claude, codex or antigravity')
    parser.add_argument('--alias', help='Account alias chosen by the user (default: HANDOFF_AGENT_ALIAS)')
    parser.add_argument('--host', help='Hook host whose snapshots refresh the heartbeat: claude, codex or antigravity')
    parser.add_argument('--reason', default='unknown', choices=REASONS, help='Why the previous writer stopped, as reported')
    parser.add_argument('--confirm-takeover', action='store_true',
                        help='Take over a held lock; pass only after the user confirms the holder stopped')
    parser.add_argument('--stale-minutes', type=float)
    parser.add_argument('--yes', action='store_true', help='Required for force-release')
    args = parser.parse_args(argv)
    root = Path(args.project).resolve()
    if not root.is_dir():
        raise LockError('Project must be an existing directory.')
    config = snapshot.load_config(root)
    stale = args.stale_minutes or float(config.get('lock_stale_minutes', DEFAULT_STALE_MINUTES))
    if args.action == 'status':
        return state(root, stale)
    if args.action == 'force-release':
        if not args.yes:
            raise LockError('force-release removes another session\'s lock; rerun with --yes after the user confirms.')
        return release(root, identity(args.agent or 'unknown', args.alias), force=True)
    if not args.agent:
        raise LockError('--agent is required for ' + args.action)
    who = identity(args.agent, args.alias)
    if args.action == 'acquire':
        return acquire(root, who, args.host or args.agent, args.reason, args.confirm_takeover, stale, args.checkpoint)
    return release(root, who, force=False)


def main():
    try:
        print(json.dumps(run(), indent=2))
        return 0
    except LockError as exc:
        print('lock: ' + str(exc), file=sys.stderr)
        return exc.code


if __name__ == '__main__':
    sys.exit(main())
