"""Domain profile scenarios: game, video and motion sections in disposable projects."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'cross-agent-handoff'
HELPER = SKILL / 'scripts' / 'handoff.py'
PROFILES = SKILL / 'assets' / 'profiles'
PROFILE_BUDGET = 150  # Words per profile section template.
DRAFT_BUDGET = 700  # Base template plus every profile, leaving room under the 1,200-word target.


def fill(text):
    """Replace each template instruction with a short concrete value, as an agent would."""
    text = re.sub(r'^- updated_at: .*$', '- updated_at: 2026-11-01T09:00:00+07:00', text, flags=re.M)
    return re.sub(r'REPLACE (?:with|from)[^\n]*', 'Recorded fixture value.', text)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'promo video'
        self.root.mkdir()
        self.target = self.root / 'HANDOFF.md'

    def tearDown(self):
        self.temp.cleanup()

    def helper(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(HELPER), *args, '--project', str(self.root)],
                                text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_profile_files_are_compact_sections(self):
        names = sorted(path.stem for path in PROFILES.glob('*.md'))
        self.assertEqual(names, ['game', 'motion', 'video'])
        for name in names:
            text = (PROFILES / (name + '.md')).read_text()
            self.assertEqual(text.splitlines()[0], '## Profile: ' + name)
            self.assertLessEqual(len(text.split()), PROFILE_BUDGET, name)
            for line in text.splitlines()[1:]:
                self.assertIn('REPLACE with', line)

    def test_init_with_profiles_extends_the_base_template(self):
        self.helper('init', '--profile', 'video,motion')
        text = self.target.read_text()
        headings = re.findall(r'^## (.+)$', text, re.M)
        self.assertEqual(headings, ['Project', 'Task', 'State', 'Profile: video', 'Profile: motion',
                                    'Evidence', 'Next', 'Recent outcomes'])
        self.assertIn('\n- profile: video, motion\n', text)
        self.helper('check', expected=2)  # Unfilled draft is not an initialized checkpoint.
        self.target.write_text(fill(text))
        self.helper('check')

    def test_all_profiles_fit_the_size_budget(self):
        self.helper('init', '--profile', 'game,video,motion')
        draft = self.target.read_text()
        self.assertLessEqual(len(draft.split()), DRAFT_BUDGET)
        self.target.write_text(fill(draft))
        self.assertEqual(json.loads(self.helper('check').stdout)['warnings'], [])

    def test_unknown_profile_creates_nothing(self):
        result = self.helper('init', '--profile', 'video,film', expected=2)
        self.assertIn('Unknown profile(s): film', result.stderr)
        self.assertFalse(self.target.exists())

    def test_listed_profile_without_section_warns(self):
        self.helper('init', '--profile', 'game')
        text = fill(self.target.read_text())
        text = re.sub(r'## Profile: game\n(?:.+\n)+\n', '', text)
        self.target.write_text(text)
        warnings = json.loads(self.helper('check', expected=1).stdout)['warnings']
        self.assertIn('no "## Profile: game" section', warnings[0])

    def test_inject_surfaces_running_render_before_rerun(self):
        self.helper('init', '--profile', 'video')
        text = fill(self.target.read_text()).replace(
            'Running renders: Recorded fixture value.',
            'Running renders: ffmpeg -i cut.mov -c:v libx264 out/promo_v3.mp4, started 08:40. Do NOT re-render.')
        self.target.write_text(text)
        output = subprocess.run([sys.executable, str(SKILL / 'scripts' / 'inject.py'), '--project', str(self.root)],
                                text=True, capture_output=True, check=True, timeout=60).stdout
        self.assertIn('Running operations (check before rerunning anything):', output)
        self.assertIn('out/promo_v3.mp4, started 08:40. Do NOT re-render.', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
