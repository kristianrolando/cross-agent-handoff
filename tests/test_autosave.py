"""Mechanical snapshot and resume-context scenarios in disposable projects.

Hook payloads below are hand-written fixtures shaped like the documented host inputs;
no vendor host or model runs in these tests.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills' / 'cross-agent-handoff' / 'scripts'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_handoff import checkpoint  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location('fixture_' + name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


snapshot = load('snapshot')
inject = load('inject')


class AutosaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'project with spaces'
        self.root.mkdir()
        self.auto = self.root / '.handoff' / 'auto'

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, name, *args, payload=None):
        result = subprocess.run([sys.executable, str(SCRIPTS / (name + '.py')), *args],
                                input=json.dumps(payload) if payload is not None else '',
                                text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def write_checkpoint(self, age_seconds=600, text=None):
        path = self.root / 'HANDOFF.md'
        path.write_text(text or checkpoint())
        past = time.time() - age_seconds
        os.utime(path, (past, past))
        return path

    def age(self, name, seconds=900):
        past = time.time() - seconds
        os.utime(self.root / name, (past, past))

    def git(self, *args):
        subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def init_git(self):
        if not shutil.which('git'):
            self.skipTest('git unavailable')
        self.git('init')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')

    def latest(self):
        return json.loads((self.auto / 'latest.json').read_text())

    def test_snapshot_without_git(self):
        self.write_checkpoint()
        (self.root / 'scene.py').write_text('draft')
        self.run_script('snapshot', '--project', str(self.root))
        record = self.latest()
        self.assertEqual(record['schema'], 'cross-agent-handoff/snapshot-1')
        self.assertFalse(record['git']['available'])
        self.assertEqual([item['path'] for item in record['recent_files']['files']], ['scene.py'])
        self.assertTrue(record['checkpoint']['exists'])
        self.assertIn('*', (self.auto / '.gitignore').read_text())
        self.assertEqual(len((self.auto / 'history.jsonl').read_text().splitlines()), 1)

    def test_snapshot_with_git_and_skipped_directories(self):
        self.init_git()
        self.write_checkpoint()
        (self.root / 'app.js').write_text('base')
        self.git('add', '.')
        self.git('commit', '-m', 'Fixture baseline')
        (self.root / 'app.js').write_text('changed')
        (self.root / 'node_modules').mkdir()
        (self.root / 'node_modules' / 'dep.js').write_text('vendor')
        skill_copy = self.root / '.claude' / 'skills' / 'cross-agent-handoff'
        skill_copy.mkdir(parents=True)
        (skill_copy / 'SKILL.md').write_text('installed tooling')
        self.run_script('snapshot', '--project', str(self.root))
        record = self.latest()
        self.assertTrue(record['git']['available'])
        self.assertTrue(any('app.js' in line for line in record['git']['status']))
        paths = [item['path'] for item in record['recent_files']['files']]
        self.assertIn('app.js', paths)
        self.assertNotIn('node_modules/dep.js', paths)
        self.assertNotIn('.claude/skills/cross-agent-handoff/SKILL.md', paths)
        self.assertFalse(any(path.startswith('.handoff') for path in paths))

    def test_snapshot_outside_continuity_project_records_nothing(self):
        (self.root / 'file.txt').write_text('x')
        result = self.run_script('snapshot', '--project', str(self.root))
        self.assertIn('nothing recorded', result.stderr)
        self.assertFalse((self.root / '.handoff').exists())

    def test_snapshot_never_fails_the_hook(self):
        self.write_checkpoint()
        (self.root / '.handoff').mkdir()
        (self.root / '.handoff' / 'config.json').write_text('{broken')
        result = self.run_script('snapshot', '--hook', '--project', str(self.root), payload='not json')
        self.assertIn('ignoring unreadable', result.stderr)
        with mock.patch.object(snapshot, 'run', side_effect=RuntimeError('boom')):
            self.assertEqual(snapshot.main(), 0)
        with mock.patch.object(inject, 'run', side_effect=RuntimeError('boom')):
            self.assertEqual(inject.main(), 0)

    def test_media_metadata_and_optional_partial_hash(self):
        self.write_checkpoint()
        data = os.urandom(3 * 1024 * 1024)
        (self.root / 'render.mp4').write_bytes(data)
        self.run_script('snapshot', '--project', str(self.root))
        media = self.latest()['recent_files']['files'][0]
        self.assertTrue(media['media'])
        self.assertEqual(media['size'], len(data))
        self.assertNotIn('partial_sha256', media)
        self.run_script('snapshot', '--project', str(self.root), '--partial-hash')
        expected = hashlib.sha256(data[:1024 * 1024] + data[-1024 * 1024:]).hexdigest()
        self.assertEqual(self.latest()['recent_files']['files'][0]['partial_sha256'], expected)

    def test_history_is_pruned(self):
        self.write_checkpoint()
        (self.root / '.handoff').mkdir()
        (self.root / '.handoff' / 'config.json').write_text(json.dumps({'snapshot': {'history_max_lines': 3}}))
        for _ in range(5):
            self.run_script('snapshot', '--project', str(self.root))
        self.assertEqual(len((self.auto / 'history.jsonl').read_text().splitlines()), 3)

    def test_abrupt_stop_without_semantic_save(self):
        # Work was saved as files and a hook snapshot ran, but the agent never updated the checkpoint.
        self.write_checkpoint()
        (self.root / 'level1.js').write_text('half-finished collision code')
        payload = {'hook_event_name': 'StopFailure', 'error': 'rate_limit', 'cwd': str(self.root),
                   'transcript_path': '/private/transcript.jsonl'}
        self.run_script('snapshot', '--hook', '--host', 'claude', payload=payload)
        record = self.latest()
        self.assertEqual(record['event']['error'], 'rate_limit')
        self.assertNotIn('transcript_path', json.dumps(record))  # Only whitelisted hook fields.
        output = self.run_script('inject', '--project', str(self.root)).stdout
        self.assertIn('WARNING: 1 files and 0 commits changed after HANDOFF.md', output)
        self.assertIn('level1.js', output)
        self.assertIn('ended with error "rate_limit"', output)
        self.assertIn('Run the greeting checks.', output)  # Next action from the checkpoint.
        self.assertIn('GREET-1', output)  # Task identity from the checkpoint.

    def test_inject_quiet_when_checkpoint_is_newest(self):
        (self.root / 'done.py').write_text('finished')
        self.age('done.py')
        self.write_checkpoint(age_seconds=10)
        output = self.run_script('inject', '--project', str(self.root)).stdout
        self.assertNotIn('WARNING', output)
        self.assertIn('task_status: partial', output)

    def test_fresh_clone_is_not_reported_as_unsaved_work(self):
        self.init_git()
        self.write_checkpoint()
        (self.root / 'game.js').write_text('committed work')
        self.git('add', '.')
        self.git('commit', '-m', 'Work and checkpoint')
        os.utime(self.root / 'game.js')  # A checkout refreshes modification times.
        output = self.run_script('inject', '--project', str(self.root)).stdout
        self.assertNotIn('WARNING', output)

    def test_commits_after_checkpoint_are_reported(self):
        self.init_git()
        self.write_checkpoint()
        self.git('add', '.')
        self.git('commit', '-m', 'Checkpoint')
        (self.root / 'edit.py').write_text('later')
        self.git('add', '.')
        self.git('commit', '-m', 'Unrecorded follow-up')
        output = self.run_script('inject', '--project', str(self.root)).stdout
        self.assertIn('0 files and 1 commits changed', output)
        self.assertIn('Unrecorded follow-up', output)

    def test_inject_from_subdirectory_crlf_and_cap(self):
        self.write_checkpoint(text=checkpoint(phase='working', actor='claude-A').replace('\n', '\r\n'))
        (self.root / 'src').mkdir()
        payload = {'cwd': str(self.root / 'src'), 'hook_event_name': 'SessionStart'}
        output = self.run_script('inject', '--hook', payload=payload).stdout
        self.assertIn('handoff: working (writer: claude-A)', output)
        capped = self.run_script('inject', '--project', str(self.root), '--max-lines', '4').stdout
        self.assertEqual(len(capped.splitlines()), 4)
        self.assertIn('output capped', capped)
        steps = json.loads(self.run_script('inject', '--project', str(self.root), '--format', 'antigravity').stdout)
        self.assertIn('resume context', steps['injectSteps'][0]['ephemeralMessage'])

    def test_inject_silent_outside_continuity_project(self):
        self.assertEqual(self.run_script('inject', '--project', str(self.root)).stdout, '')

    def test_staleness_guard_asks_once_per_checkpoint_version(self):
        self.write_checkpoint(age_seconds=3600)
        (self.root / 'cut.py').write_text('edit list')
        stop = {'hook_event_name': 'Stop', 'stop_hook_active': False, 'cwd': str(self.root)}
        first = self.run_script('snapshot', '--hook', '--host', 'claude', '--guard', payload=stop).stdout
        decision = json.loads(first)
        self.assertEqual(decision['decision'], 'block')
        self.assertIn('Update the checkpoint', decision['reason'])
        again = self.run_script('snapshot', '--hook', '--host', 'claude', '--guard', payload=stop).stdout
        self.assertEqual(again, '')  # Loop protection: same checkpoint version.
        (self.auto / 'guard.json').unlink()
        active = dict(stop, stop_hook_active=True)
        self.assertEqual(self.run_script('snapshot', '--hook', '--guard', payload=active).stdout, '')
        agy = {'workspacePaths': [str(self.root)], 'terminationReason': 'model_stop'}
        result = json.loads(self.run_script('snapshot', '--hook', '--host', 'antigravity', '--guard',
                                            payload=agy).stdout)
        self.assertEqual(result['decision'], 'continue')

    def test_guard_silent_for_small_recent_change(self):
        self.write_checkpoint(age_seconds=60)
        (self.root / 'one.py').write_text('x')
        stop = {'hook_event_name': 'Stop', 'cwd': str(self.root)}
        self.assertEqual(self.run_script('snapshot', '--hook', '--guard', payload=stop).stdout, '')

    def test_snapshot_speed_on_many_files(self):
        self.write_checkpoint()
        for index in range(2000):
            folder = self.root / 'assets' / str(index % 20)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / ('frame%04d.png' % index)).write_bytes(b'x')
        started = time.monotonic()
        self.run_script('snapshot', '--project', str(self.root))
        self.assertLess(time.monotonic() - started, 5)
        record = self.latest()['recent_files']
        self.assertEqual(record['count'], 2000)
        self.assertEqual(len(record['files']), 200)  # Listing capped; count stays exact.


if __name__ == '__main__':
    unittest.main(verbosity=2)
