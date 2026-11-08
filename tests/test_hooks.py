"""Opt-in hook configuration merge/remove scenarios in disposable projects.

These tests check file merging and command execution only; no host application reads the
generated configuration here.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'cross-agent-handoff'
HOOKS = SKILL / 'scripts' / 'hooks.py'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_handoff import checkpoint  # noqa: E402

EXISTING = {
    'permissions': {'allow': ['Bash(npm test)']},
    'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': 'say done'}]}],
              'PostToolUse': [{'matcher': 'Write', 'hooks': [{'type': 'command', 'command': 'fmt'}]}]},
}


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'my project'
        self.root.mkdir()
        (self.root / 'HANDOFF.md').write_text(checkpoint())

    def tearDown(self):
        self.temp.cleanup()

    def install_skill(self, parent):
        shutil.copytree(SKILL, self.root / parent / 'cross-agent-handoff',
                        ignore=shutil.ignore_patterns('__pycache__'))

    def hooks(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(HOOKS), *args, '--project', str(self.root)],
                                text=True, capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def read(self, rel):
        return json.loads((self.root / rel).read_text())

    def test_claude_merge_is_idempotent_and_removable(self):
        self.install_skill('.claude/skills')
        settings = self.root / '.claude' / 'settings.local.json'
        settings.write_text(json.dumps(EXISTING))
        self.hooks('install', '--host', 'claude', '--yes')
        data = self.read('.claude/settings.local.json')
        self.assertEqual(data['permissions'], EXISTING['permissions'])
        self.assertEqual(data['hooks']['PostToolUse'], EXISTING['hooks']['PostToolUse'])
        self.assertEqual(data['hooks']['Stop'][0], EXISTING['hooks']['Stop'][0])
        self.assertEqual(set(data['hooks']), {'Stop', 'PostToolUse', 'SessionStart', 'StopFailure', 'PreCompact'})
        command = data['hooks']['SessionStart'][0]['hooks'][0]['command']
        self.assertIn('"$CLAUDE_PROJECT_DIR/.claude/skills/cross-agent-handoff/scripts/inject.py"', command)
        self.assertNotIn('--guard', json.dumps(data))
        self.assertIn('already up to date', self.hooks('install', '--host', 'claude', '--yes').stdout)
        self.hooks('remove', '--host', 'claude', '--yes')
        self.assertEqual(self.read('.claude/settings.local.json'), EXISTING)
        self.assertIn('nothing to remove', self.hooks('remove', '--host', 'claude', '--yes').stdout)

    def test_shared_claude_settings_and_guard(self):
        self.install_skill('.claude/skills')
        self.hooks('install', '--host', 'claude', '--shared', '--guard', '--yes')
        data = self.read('.claude/settings.json')
        self.assertIn('--guard', data['hooks']['Stop'][0]['hooks'][0]['command'])
        self.assertNotIn('--guard', data['hooks']['StopFailure'][0]['hooks'][0]['command'])
        self.assertFalse((self.root / '.claude' / 'settings.local.json').exists())

    def test_refuses_invalid_json_missing_skill_and_unconfirmed_writes(self):
        self.hooks('install', '--host', 'claude', '--yes', expected=2)  # Skill copy missing.
        self.install_skill('.claude/skills')
        settings = self.root / '.claude' / 'settings.local.json'
        settings.write_text('{"hooks": ')
        result = self.hooks('install', '--host', 'claude', '--yes', expected=2)
        self.assertIn('not valid JSON', result.stderr)
        self.assertEqual(settings.read_text(), '{"hooks": ')
        settings.unlink()
        result = self.hooks('install', '--host', 'claude', expected=2)
        self.assertIn('Confirmation required', result.stderr)
        self.assertFalse(settings.exists())

    def test_dry_run_writes_nothing(self):
        self.install_skill('.agents/skills')
        result = self.hooks('install', '--host', 'codex', '--host', 'antigravity', '--dry-run')
        self.assertIn('Would update codex', result.stdout)
        self.assertFalse((self.root / '.codex').exists())
        self.assertFalse((self.root / '.agents' / 'hooks.json').exists())

    def test_codex_command_runs_with_spaces_in_path(self):
        self.install_skill('.agents/skills')
        self.hooks('install', '--host', 'codex', '--yes', '--python', sys.executable)
        data = self.read('.codex/hooks.json')
        stop = data['hooks']['Stop'][0]['hooks'][0]
        self.assertIn('commandWindows', stop)
        self.assertIn('py -3 "', stop['commandWindows'])
        payload = json.dumps({'hook_event_name': 'Stop', 'cwd': str(self.root), 'stop_hook_active': False})
        result = subprocess.run(stop['command'], shell=True, input=payload, text=True,
                                capture_output=True, cwd=str(self.root), timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        latest = json.loads((self.root / '.handoff' / 'auto' / 'latest.json').read_text())
        self.assertEqual(latest['event'], {'hook_event_name': 'Stop', 'host': 'codex'})
        start = data['hooks']['SessionStart'][0]['hooks'][0]['command']
        result = subprocess.run(start, shell=True, input=json.dumps({'cwd': str(self.root)}), text=True,
                                capture_output=True, cwd=str(self.root), timeout=60)
        self.assertIn('resume context', result.stdout)

    def test_antigravity_uses_its_own_named_entry(self):
        self.install_skill('.agents/skills')
        hooks_file = self.root / '.agents' / 'hooks.json'
        hooks_file.write_text(json.dumps({'lint': {'PostToolUse': [{'matcher': 'run_command', 'hooks': []}]}}))
        self.hooks('install', '--host', 'antigravity', '--yes')
        data = self.read('.agents/hooks.json')
        self.assertIn('lint', data)
        ours = data['cross-agent-handoff']
        self.assertEqual(set(ours), {'SessionStart', 'Stop'})
        self.assertIn('--format antigravity', ours['SessionStart'][0]['command'])
        self.assertIn('--event Stop', ours['Stop'][0]['command'])
        self.hooks('remove', '--host', 'antigravity', '--yes')
        self.assertEqual(set(self.read('.agents/hooks.json')), {'lint'})

    def test_status_reports_missing_scripts(self):
        self.install_skill('.agents/skills')
        self.hooks('install', '--host', 'codex', '--yes')
        report = json.loads(self.hooks('status', '--host', 'codex').stdout)
        self.assertTrue(report['installed'])
        self.assertEqual(report['missing_scripts'], [])
        (self.root / '.agents/skills/cross-agent-handoff/scripts/snapshot.py').unlink()
        report = json.loads(self.hooks('status', '--host', 'codex').stdout)
        self.assertEqual(len(report['missing_scripts']), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
