# Live trial record: skill installed or not, v0.3.0 routing block (2026-11-26, third pass)

Follow-up to [the second pass](live-trial-2026-11-26-routing-block-v2.md). Question: does installing
the skill in the project change what an agent does, once the project already carries the v0.3.0
routing block? Only what was observed is recorded.

## Setup

- macOS, Claude Code 2.1.319 headless, model `claude-sonnet-5-5`, fresh sessions, 16 runs in two
  parallel batches of eight, arms assigned in random order with neutral folder names and read after
  scoring.
- Fixture: the second-pass fixture (running `bash render.sh` job, 70 clip files, nine planted facts,
  a 2,184-word checkpoint). Routing block: the one on `main` after PR #19 (the "candidate" of the
  second pass).
- Arms: `skill` = the bundled installer copied the skill into `.claude/skills/` of the fixture
  (8 runs); `plain` = no skill (8 runs). The skill arm ran without `--disable-slash-commands`, so
  its skill was loadable; the plain arm kept that flag. Both used
  `--setting-sources project --strict-mcp-config --no-session-persistence`, which keeps the
  user-level plugin out. `Bash(python3:*)` was added to the allowed tools so an agent could run the
  helper; the earlier passes did not allow it.
- Scorer: [score.sh](live-trial-v0.2.2/score.sh) as revised in the second pass.

## Results

| Check | plain (8) | skill (8) |
| --- | --- | --- |
| Checkpoint at most 1,300 words (starts at 2,184) | 8/8 (431 to 537 words) | 8/8 (519 to 577 words) |
| `updated_at` from the real clock, not rounded to `:00` | 7/8 | 7/8 |
| Nine planted facts kept | 8/8 | 8/8 |
| Owner answer applied, owner question saved | 8/8 | 8/8 |
| `upload.sh` run or render restarted | 0 | 0 |
| Running render visible | 7/8 | 8/8 |

The one plain run that missed the render check and the one run per arm that wrote a rounded time
are within what these counts cannot separate. No run created a `.handoff/` folder, so none ran the
helper's lock or snapshot paths; whether an agent read `SKILL.md` was not recorded and cannot be read
from the result files.

## What it says

- With the v0.3.0 routing block in place, installing the skill made no measurable difference on
  these checks. The block alone was enough in this fixture, which matches the audit's finding that
  the block is the text agents reliably load.
- Across the second and third passes, the current block produced a checkpoint within 1,300 words in
  29 of 29 runs, against 6 of 13 for the v0.2.3 block (second pass, same fixture).
- Limits: one model, one host, one synthetic project; 8 runs per arm; no Windows; the skill's
  effect on tasks other than this one (initialising a project, recovery after a crash) was not
  tested; C3 and the render check contain judgment made by Claude.
