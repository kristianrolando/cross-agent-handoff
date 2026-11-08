"""Advisory lock and switch-log scenarios; agent names are labels, not running hosts."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills' / 'cross-agent-handoff' / 'scripts'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_handoff import checkpoint  # noqa: E402


class LockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'motion project'
        self.root.mkdir()
        (self.root / 'HANDOFF.md').write_text(checkpoint())
        self.lock_file = self.root / '.handoff' / 'lock.json'
        self.log_file = self.root / '.handoff' / 'log.jsonl'

    def tearDown(self):
        self.temp.cleanup()

    def lock(self, *args, expected=0, env=None):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'lock.py'), *args, '--project', str(self.root)],
                                text=True, capture_output=True, timeout=60,
                                env=dict(os.environ, **(env or {})))
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout) if expected == 0 else result

    def log(self):
        return [json.loads(line) for line in self.log_file.read_text().splitlines()]

    def age_heartbeat(self, minutes):
        record = json.loads(self.lock_file.read_text())
        record['heartbeat'] = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
        self.lock_file.write_text(json.dumps(record))

    def test_acquire_release_and_switch_log(self):
        self.assertEqual(self.lock('status')['state'], 'free')
        first = self.lock('acquire', '--agent', 'claude', '--alias', 'claude-A', '--reason', 'new-session')
        self.assertEqual(first['result'], 'acquired')
        self.assertEqual(self.lock('status')['state'], 'fresh')
        self.assertEqual(self.lock('acquire', '--agent', 'claude', '--alias', 'claude-A')['result'], 'already-held')
        self.lock('release', '--agent', 'claude', '--alias', 'claude-A')
        self.assertFalse(self.lock_file.exists())
        self.lock('acquire', '--agent', 'codex', '--reason', 'limit')
        entries = self.log()
        self.assertEqual([e['to'] for e in entries], ['claude/claude-A', 'codex'])
        self.assertEqual(entries[1]['from'], 'claude/claude-A')
        self.assertEqual(entries[1]['reason'], 'limit')
        self.assertEqual(entries[1]['reason_source'], 'reported')
        self.assertEqual(len(entries[1]['checkpoint_sha256']), 64)
        self.assertIn('lock.json', (self.root / '.handoff' / '.gitignore').read_text())

    def test_fresh_lock_blocks_silent_resume(self):
        self.lock('acquire', '--agent', 'claude', '--alias', 'claude-A')
        result = self.lock('acquire', '--agent', 'claude', '--alias', 'claude-B', expected=3)
        self.assertIn('held by claude/claude-A', result.stderr)
        self.assertIn('--confirm-takeover', result.stderr)
        self.assertEqual(json.loads(self.lock_file.read_text())['alias'], 'claude-A')
        result = self.lock('release', '--agent', 'codex', expected=3)
        self.assertTrue(self.lock_file.exists())

    def test_stale_lock_still_needs_confirmation_then_logs_takeover(self):
        self.lock('acquire', '--agent', 'antigravity')
        self.age_heartbeat(30)
        self.assertEqual(self.lock('status')['state'], 'stale')
        result = self.lock('acquire', '--agent', 'claude', '--alias', 'claude-B', expected=3)
        self.assertIn('stale heartbeat does not prove', result.stderr)
        taken = self.lock('acquire', '--agent', 'claude', '--alias', 'claude-B', '--reason', 'limit',
                          '--confirm-takeover')
        self.assertEqual(taken['result'], 'taken-over')
        entry = self.log()[-1]
        self.assertTrue(entry['takeover'])
        self.assertEqual(entry['from'], 'antigravity')
        self.assertEqual(entry['previous_state'], 'stale')
        self.assertEqual(json.loads(self.lock_file.read_text())['alias'], 'claude-B')

    def test_alias_from_environment_and_privacy_check(self):
        self.lock('acquire', '--agent', 'claude', env={'HANDOFF_AGENT_ALIAS': 'claude-A'})
        self.assertEqual(json.loads(self.lock_file.read_text())['alias'], 'claude-A')
        result = self.lock('acquire', '--agent', 'codex', '--alias', 'me@example.com', expected=2)
        self.assertIn('no emails', result.stderr)

    def test_force_release_requires_yes_and_is_logged(self):
        self.lock('acquire', '--agent', 'codex')
        self.lock('force-release', expected=2)
        self.lock('force-release', '--yes')
        self.assertFalse(self.lock_file.exists())
        self.assertEqual(self.log()[-1]['reason'], 'force-release')

    def test_snapshot_refreshes_heartbeat_only_for_the_lock_host(self):
        self.lock('acquire', '--agent', 'codex', '--host', 'codex')
        self.age_heartbeat(30)
        payload = json.dumps({'hook_event_name': 'Stop', 'cwd': str(self.root)})
        for host, expected in (('claude', 'stale'), ('codex', 'fresh')):
            subprocess.run([sys.executable, str(SCRIPTS / 'snapshot.py'), '--hook', '--host', host],
                           input=payload, text=True, capture_output=True, check=True, timeout=60)
            self.assertEqual(self.lock('status')['state'], expected, host)

    def test_inject_warns_about_a_held_lock(self):
        self.lock('acquire', '--agent', 'claude', '--alias', 'claude-A')
        output = subprocess.run([sys.executable, str(SCRIPTS / 'inject.py'), '--project', str(self.root)],
                                text=True, capture_output=True, check=True, timeout=60).stdout
        self.assertIn('WARNING: Advisory lock held by claude/claude-A (fresh', output)

    def test_corrupt_lock_is_reported_not_overwritten_silently(self):
        self.lock_file.parent.mkdir(parents=True)
        self.lock_file.write_text('{broken')
        status = self.lock('status')
        self.assertEqual(status['holder'], 'unknown')
        self.lock('acquire', '--agent', 'codex', expected=3)
        self.assertEqual(self.lock_file.read_text(), '{broken')


if __name__ == '__main__':
    unittest.main(verbosity=2)
