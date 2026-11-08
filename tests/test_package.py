"""Package integrity checks without third-party runtime dependencies."""
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'cross-agent-handoff'


class PackageTests(unittest.TestCase):
    def test_portable_frontmatter(self):
        text = (SKILL / 'SKILL.md').read_text()
        match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        self.assertIsNotNone(match)
        fields = dict(line.split(': ', 1) for line in match[1].splitlines())
        self.assertEqual(set(fields), {'name', 'description', 'license'})
        self.assertEqual(fields['name'], SKILL.name)
        self.assertEqual(fields['license'], 'MIT')
        self.assertRegex(fields['name'], r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
        self.assertTrue(0 < len(fields['description']) <= 1024)
        self.assertNotIn('[TODO', text)

    def test_relative_markdown_links(self):
        for path in ROOT.rglob('*.md'):
            text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    self.assertTrue((path.parent / link.split('#')[0]).exists(), (str(path), link))

    def test_runtime_has_no_personal_dependencies(self):
        for path in SKILL.rglob('*'):
            if path.is_file() and path.suffix in {'.md', '.py', '.yaml'} and '__pycache__' not in path.parts:
                text = path.read_text()
                self.assertNotIn('/Users/', text, str(path))
                self.assertNotIn('/root/', text, str(path))
                self.assertNotIn('ANTHROPIC_API_KEY', text, str(path))
                self.assertNotIn('OPENAI_API_KEY', text, str(path))

    def test_plugin_paths_resolve(self):
        plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        for path in plugin['skills']:
            self.assertTrue((ROOT / path / 'SKILL.md').is_file())
        self.assertEqual(market['plugins'][0]['name'], plugin['name'])
        self.assertTrue((ROOT / market['plugins'][0]['source']).is_dir())

    def test_license_travels_with_standalone_skill(self):
        root_license = (ROOT / 'LICENSE').read_text()
        self.assertEqual((SKILL / 'LICENSE').read_text(), root_license)
        self.assertIn('MIT License', root_license)
        self.assertIn('Copyright (c) 2026 Kristian Rolando Limantara', root_license)
        plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(plugin['license'], 'MIT')

    def test_public_examples_use_valid_checkpoint_format(self):
        for name in ('before.md', 'after.md'):
            result = subprocess.run(
                [sys.executable, str(SKILL / 'scripts/handoff.py'), 'check',
                 '--project', str(ROOT), '--checkpoint', 'docs/examples/' + name],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_version_file(self):
        version = (SKILL / 'VERSION').read_text()
        self.assertRegex(version, r'^[0-9]+\.[0-9]+\.[0-9]+(?:-dev)?\n$')
        plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(version.strip().replace('-dev', ''), plugin['version'])
        self.assertTrue((ROOT / 'docs' / 'releases' / ('v' + plugin['version'] + '.md')).is_file())
        self.assertIn('## ' + plugin['version'], (ROOT / 'CHANGELOG.md').read_text())

    def test_core_reading_size(self):
        self.assertLess(len((SKILL / 'SKILL.md').read_text().split()), 1600)
        self.assertLess(len((SKILL / 'assets/checkpoint.md').read_text().split()), 400)


if __name__ == '__main__':
    unittest.main(verbosity=2)
