"""Installer, updater and doctor scenarios in disposable projects (no host application runs)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'cross-agent-handoff'
INSTALL = SKILL / 'scripts' / 'install.py'
# Files added after v0.1.1; removing them approximates a v0.1.1 install without Git tags,
# because CI checkouts are shallow. A manual check against the real tag is in docs/validation.md.
V020_ONLY = ('VERSION', 'scripts/snapshot.py', 'scripts/inject.py', 'scripts/hooks.py',
             'scripts/install.py', 'references/hooks.md')


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'video project'
        self.root.mkdir()
        self.home = Path(self.temp.name) / 'home dir'
        self.home.mkdir()
        (self.root / 'HANDOFF.md').write_text('# Project handoff\nkept\n')
        (self.root / '.handoff').mkdir()
        (self.root / '.handoff' / 'log.jsonl').write_text('{}\n')

    def tearDown(self):
        self.temp.cleanup()

    def run_install(self, *args, expected=0):
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
        result = subprocess.run([sys.executable, str(INSTALL), '--project', str(self.root), *args],
                                text=True, capture_output=True, stdin=subprocess.DEVNULL, env=env, timeout=120)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def copy(self, parent):
        return self.root / parent / 'cross-agent-handoff'

    def source_files(self):
        return sorted(p.relative_to(SKILL).as_posix() for p in SKILL.rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store')

    def assert_complete(self, path):
        for rel in self.source_files():
            self.assertEqual((path / rel).read_bytes(), (SKILL / rel).read_bytes(), rel)
        self.assertTrue((path / 'MANIFEST.sha256').is_file())
        self.assertTrue((path / 'LICENSE').is_file())
        self.assertFalse((path / 'cross-agent-handoff').exists())  # Never nested.

    def test_install_all_hosts_uses_two_folders_and_is_idempotent(self):
        result = self.run_install('--hosts', 'claude,codex,antigravity,cursor,gemini,copilot,opencode,cline')
        self.assertEqual(result.stdout.count('Installing'), 2)
        self.assert_complete(self.copy('.claude/skills'))
        self.assert_complete(self.copy('.agents/skills'))
        again = self.run_install('--hosts', 'claude,codex')
        self.assertEqual(again.stdout.count('Up to date'), 2)
        self.assertNotIn('Installing', again.stdout)
        self.assertEqual(self.run_install('--doctor', '--hosts', 'claude,codex').stdout.strip().splitlines()[-1], 'Healthy.')

    def test_doctor_detects_edited_and_missing_copies(self):
        self.run_install('--hosts', 'claude,codex')
        skill_md = self.copy('.claude/skills') / 'SKILL.md'
        skill_md.write_text(skill_md.read_text() + '\nlocal edit\n')
        report = json.loads(self.run_install('--doctor', '--json', expected=1).stdout)
        self.assertTrue(any('Edited copy .claude/skills/cross-agent-handoff' in w and 'SKILL.md' in w
                            for w in report['warnings']))
        self.assertTrue(any('drift' in w for w in report['warnings']))
        shutil.rmtree(self.copy('.agents/skills'))
        report = json.loads(self.run_install('--doctor', '--json', '--hosts', 'claude,codex', expected=2).stdout)
        self.assertTrue(any('Missing copy for codex' in p for p in report['problems']))

    def test_unreadable_manifest_is_reported_and_repaired_not_a_traceback(self):
        self.run_install('--hosts', 'claude')
        manifest = self.copy('.claude/skills') / 'MANIFEST.sha256'
        for broken in (b'not a manifest line\n', b'\xff\xfe\x00 binary', b'abc  \n'):
            manifest.write_bytes(broken)
            result = self.run_install('--doctor', '--json', expected=1)
            self.assertNotIn('Traceback', result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(any('Unreadable manifest' in w and '--update' in w for w in report['warnings']), report)
            shown = self.run_install('--hosts', 'claude')
            self.assertIn('manifest unreadable', shown.stdout)
            self.assertEqual(manifest.read_bytes(), broken)  # Without --update nothing is replaced.
        updated = self.run_install('--hosts', 'claude', '--update', '--yes')
        self.assertIn('manifest cannot be read', updated.stdout)
        self.assert_complete(self.copy('.claude/skills'))
        self.assertEqual(self.run_install('--doctor', '--hosts', 'claude').stdout.strip().splitlines()[-1], 'Healthy.')

    def enable_plugin(self, where, enabled=True):
        """Record the Claude Code plugin route the way Claude Code writes it, in the disposable HOME."""
        key = 'cross-agent-handoff@cross-agent-tools'
        settings = where / 'settings.json'
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps({'enabledPlugins': {key: enabled, 'other@x': True}}))
        records = self.home / '.claude' / 'plugins'
        records.mkdir(parents=True, exist_ok=True)
        (records / 'installed_plugins.json').write_text(json.dumps(
            {'version': 2, 'plugins': {key: [{'scope': 'user', 'version': '0.2.3'}]}}))

    def test_doctor_recognises_the_plugin_route(self):
        # Without a copy or a plugin the doctor still warns, as before.
        self.run_install('--doctor', expected=1)
        self.enable_plugin(self.home / '.claude')
        result = self.run_install('--doctor', '--json')
        report = json.loads(result.stdout)
        self.assertEqual(report['plugins'], [{'plugin': 'cross-agent-handoff@cross-agent-tools',
                                              'enabled_in': 'user settings', 'version': '0.2.3'}])
        self.assertEqual(report['warnings'], [])
        text = self.run_install('--doctor').stdout
        self.assertIn('plugin: cross-agent-handoff@cross-agent-tools  version 0.2.3', text)
        # Claude Code is served by the plugin, so asking for a claude copy is not a problem; codex still is.
        self.run_install('--doctor', '--hosts', 'claude')
        self.assertIn('Missing copy for codex', json.loads(self.run_install('--doctor', '--json', '--hosts', 'claude,codex',
                                                                           expected=2).stdout)['problems'][0])
        # A project-level enable counts too, and a disabled entry does not.
        shutil.rmtree(self.home / '.claude')
        self.enable_plugin(self.root / '.claude', enabled=False)
        self.run_install('--doctor', expected=1)
        self.enable_plugin(self.root / '.claude')
        self.assertEqual(json.loads(self.run_install('--doctor', '--json').stdout)['plugins'][0]['enabled_in'],
                         'project settings')

    def test_doctor_warns_when_plugin_and_claude_copy_both_load(self):
        self.enable_plugin(self.home / '.claude')
        self.run_install('--hosts', 'codex')
        self.run_install('--doctor')  # A copy Claude Code does not read is no duplicate.
        self.run_install('--hosts', 'claude')
        report = json.loads(self.run_install('--doctor', '--json', expected=1).stdout)
        self.assertTrue(any('listed twice' in w for w in report['warnings']), report)

    def test_a_damaged_plugin_record_is_ignored_not_a_traceback(self):
        records = self.home / '.claude' / 'plugins'
        records.mkdir(parents=True)
        (self.home / '.claude' / 'settings.json').write_text('{not json')
        (records / 'installed_plugins.json').write_text('[1, 2')
        result = self.run_install('--doctor', expected=1)
        self.assertNotIn('Traceback', result.stderr)

    def test_update_reports_local_edits_and_needs_confirmation(self):
        self.run_install('--hosts', 'claude')
        target = self.copy('.claude/skills') / 'references' / 'setup.md'
        target.write_text('edited')
        result = self.run_install('--hosts', 'claude')
        self.assertIn('Rerun with --update', result.stdout)
        self.assertEqual(target.read_text(), 'edited')
        result = self.run_install('--hosts', 'claude', '--update', expected=2)
        self.assertIn('Local changes that will be lost: references/setup.md', result.stdout)
        self.assertIn('Confirmation required', result.stderr)
        self.assertEqual(target.read_text(), 'edited')
        self.run_install('--hosts', 'claude', '--update', '--yes')
        self.assert_complete(self.copy('.claude/skills'))

    def test_upgrade_from_v011_layout(self):
        for parent in ('.claude/skills', '.agents/skills'):
            old = self.copy(parent)
            shutil.copytree(SKILL, old, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
            for rel in V020_ONLY:
                (old / rel).unlink()
        report = json.loads(self.run_install('--doctor', '--json', expected=1).stdout)
        self.assertTrue(all(copy['manifest'] == 'absent' for copy in report['copies']))
        self.assertTrue(all(copy['version'].startswith('unknown') for copy in report['copies']))
        dry = self.run_install('--hosts', 'claude,codex', '--update', '--dry-run')
        self.assertIn('Would replace unknown', dry.stdout)
        self.assertFalse((self.copy('.claude/skills') / 'VERSION').exists())
        self.run_install('--hosts', 'claude,codex', '--update', '--yes')
        for parent in ('.claude/skills', '.agents/skills'):
            self.assert_complete(self.copy(parent))
        self.assertEqual((self.root / 'HANDOFF.md').read_text(), '# Project handoff\nkept\n')
        self.assertFalse([p for p in (self.root / '.claude/skills').iterdir() if p.name.startswith('.')])

    def test_refuses_to_replace_a_different_skill(self):
        foreign = self.copy('.claude/skills')
        foreign.mkdir(parents=True)
        (foreign / 'SKILL.md').write_text('---\nname: other-skill\n---\n')
        result = self.run_install('--hosts', 'claude', '--update', '--yes', expected=2)
        self.assertIn('is not a cross-agent-handoff skill copy', result.stderr)
        self.assertEqual((foreign / 'SKILL.md').read_text(), '---\nname: other-skill\n---\n')

    def test_dry_run_and_unknown_host_write_nothing(self):
        self.run_install('--hosts', 'claude,codex', '--dry-run')
        self.assertFalse((self.root / '.claude').exists())
        result = self.run_install('--hosts', 'claude,windsurf', expected=2)
        self.assertIn('Unknown host(s): windsurf', result.stderr)
        self.assertFalse((self.root / '.claude').exists())

    def test_with_hooks_then_uninstall_keeps_project_records(self):
        other = self.root / '.claude' / 'skills' / 'my-other-skill'
        other.mkdir(parents=True)
        (other / 'SKILL.md').write_text('---\nname: my-other-skill\n---\n')
        self.run_install('--hosts', 'claude,codex,antigravity', '--with-hooks', '--yes')
        settings = json.loads((self.root / '.claude' / 'settings.local.json').read_text())
        self.assertIn('SessionStart', settings['hooks'])
        self.assertTrue((self.root / '.codex' / 'hooks.json').is_file())
        self.assertIn('cross-agent-handoff', json.loads((self.root / '.agents' / 'hooks.json').read_text()))
        self.run_install('--uninstall', expected=2)  # Needs confirmation.
        self.assertTrue(self.copy('.claude/skills').exists())
        self.run_install('--uninstall', '--yes')
        self.assertFalse(self.copy('.claude/skills').exists())
        self.assertFalse(self.copy('.agents/skills').exists())
        self.assertTrue((other / 'SKILL.md').is_file())
        self.assertEqual((self.root / 'HANDOFF.md').read_text(), '# Project handoff\nkept\n')
        self.assertTrue((self.root / '.handoff' / 'log.jsonl').is_file())
        self.assertNotIn('hooks', json.loads((self.root / '.claude' / 'settings.local.json').read_text()))
        self.assertNotIn('cross-agent-handoff', json.loads((self.root / '.agents' / 'hooks.json').read_text()))

    def test_doctor_reports_hooks_pointing_at_removed_scripts(self):
        self.run_install('--hosts', 'codex', '--with-hooks', '--yes')
        shutil.rmtree(self.copy('.agents/skills'))
        report = json.loads(self.run_install('--doctor', '--json', expected=2).stdout)
        self.assertTrue(any('codex hooks reference missing scripts' in p for p in report['problems']))

    def run_hooks(self, *args):
        result = subprocess.run([sys.executable, str(SKILL / 'scripts' / 'hooks.py'), *args, '--project', str(self.root)],
                                text=True, capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shared_claude_hooks_are_checked_and_removed(self):
        self.run_install('--hosts', 'claude')
        self.run_hooks('install', '--host', 'claude', '--shared', '--yes')
        shared = self.root / '.claude' / 'settings.json'
        data = json.loads(shared.read_text())
        data['permissions'] = {'allow': ['Bash(npm test)']}
        shared.write_text(json.dumps(data))
        shutil.rmtree(self.copy('.claude/skills'))
        report = json.loads(self.run_install('--doctor', '--json', expected=2).stdout)
        self.assertTrue(any('claude hooks reference missing scripts' in p and '.claude/settings.json' in p
                            for p in report['problems']), report)
        self.run_install('--hosts', 'claude')
        result = self.run_install('--uninstall', '--yes')
        self.assertIn('including shared .claude/settings.json', result.stdout)
        self.assertEqual(json.loads(shared.read_text()), {'permissions': {'allow': ['Bash(npm test)']}})

    def test_user_install_uses_documented_user_folders(self):
        self.run_install('--user', '--hosts', 'antigravity,cline,claude')
        self.assert_complete(self.home / '.gemini' / 'config' / 'skills' / 'cross-agent-handoff')
        self.assert_complete(self.home / '.cline' / 'skills' / 'cross-agent-handoff')
        self.assert_complete(self.home / '.claude' / 'skills' / 'cross-agent-handoff')
        self.assertFalse((self.root / '.claude').exists())

    def test_installed_copy_can_install_other_hosts(self):
        self.run_install('--hosts', 'codex')
        nested_installer = self.copy('.agents/skills') / 'scripts' / 'install.py'
        result = subprocess.run([sys.executable, str(nested_installer), '--project', str(self.root),
                                 '--hosts', 'codex,claude'], text=True, capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Source copy, left as is', result.stdout)
        doctor = self.run_install('--doctor', '--hosts', 'claude,codex')
        self.assertIn('Healthy.', doctor.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
