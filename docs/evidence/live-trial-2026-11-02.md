# Live sequential handoff trial (2026-11-02)

Three real agent sessions continued one task through project files only, in this order:
Codex → Antigravity → a fresh Codex session. No session saw another's conversation; each
received only the short prompt listed below. This is one trial on one machine, not a
statistical result or coverage of every host.

## Setup

- macOS, Python 3.9.6, Git 2.54.0. Disposable Git project with a README and a baseline commit.
- Skill copied from commit `ee5996d` with `git archive` into project-local
  `.agents/skills/cross-agent-handoff` and `.claude/skills/cross-agent-handoff`. No global
  skill folder or host setting changed.
- Codex CLI 0.166.0-alpha.5.1 (bundled with the ChatGPT app), `codex exec -s workspace-write`,
  default configured model. Antigravity CLI 1.2.3, print mode, `--mode accept-edits`, default model.
- Claude Code 2.1.287 listed the project skill at startup, but the run stopped with
  "OAuth session expired", so Claude did not take part.

## Prompts

1. Codex: `Use $cross-agent-handoff to initialize continuity in this project`, then task GREET-1
   with criteria A (`greet("Ada")` → `Hello Ada`), B (blank or whitespace → `Hello world`) and
   C (`test_greeting.py` with unittest passes). Implement only A, save a handoff and stop; do not commit.
2. Antigravity: `/cross-agent-handoff Resume this project. Shell commands are unavailable in this
   headless session, so use file read/edit tools only. Complete only the next unfinished acceptance
   criterion, then save a handoff for another agent and stop. Do not commit.`
3. Codex (new session): `Use $cross-agent-handoff to resume this project. Finish the remaining
   work, verify it, and save the final handoff. Do not commit.`

## Observations

| Step | Observed | Assessment |
| --- | --- | --- |
| 1 Codex | Read SKILL.md and setup.md; checked Git status/diffs and ancestor instruction files; created HANDOFF.md and the AGENTS.md routing block; implemented A only; ran an assertion for A; saved `partial` / `ready` / `writer: none` with B/C pending and `python3 -m unittest` as `not_run`. | Followed initialize, scope and evidence rules. |
| 2 Antigravity | Slash command expanded the project-local skill (`expanded_commands: cross-agent-handoff`). Read HANDOFF.md, AGENTS.md, README, greeting.py, the template and recovery.md; implemented B; kept A; recorded B runtime check as `not_run` / blocked and credited A's evidence to Codex. | Correct resume and honest evidence. Minor overclaim: its State line called B "verified" from file inspection, while Evidence said static only. |
| 3 Codex | Read the skill and checkpoint; checked Git status and diffs; saved an opening `in_progress` / `working` checkpoint; added `test_greeting.py`; ran `python3 -m unittest` (2 tests passed); marked static B evidence superseded; saved `done` / `ready`. | Completed criteria without redoing A/B; recorded its process-inspection limit. |

No session committed. AGENTS.md was not changed after step 1. The Claude Code review session
that ran this trial (outside the project) reran `python3 -m unittest` (2 passed) and
`handoff.py check` (no errors or warnings) on the final files.

Headless Antigravity limits: in default and `--sandbox` modes, shell commands were auto-denied,
and the agent stopped instead of working around the denial. Running it with auto-approval was
not used. Step 2 therefore exercised file tools only.

## Final file hashes (SHA-256)

| File | SHA-256 |
| --- | --- |
| greeting.py | `8fd6df8047b41b115d6d79435226a2f0fa25be495dca80b03cf639746d7dd311` |
| test_greeting.py | `1e9f032138b2e76d54a1c9ca1fd67e146bf7eea569b0574dfd13491662345f87` |
| AGENTS.md | `a9cccf1ce169c6914fe3ccdae831b27a355f77d8dc25f0d07078a227c9e9e91c` |
| HANDOFF.md | `03a664a1aa8da0975b9cdc6aaa5ccf82a02580bf2b237e968461f1d590971e1a` |

## Final checkpoint written by step 3

```markdown
# Project handoff

- format: cross-agent-handoff/1
- task_status: done
- handoff: ready
- writer: none

## Project
Identity: This repository's Python greeting exercise, task GREET-1.
Root: the directory containing README.md and this checkpoint; enclosing Git root is the same directory.
Map: [README.md](README.md), shared rules [AGENTS.md](AGENTS.md), implementation [greeting.py](greeting.py), tests [test_greeting.py](test_greeting.py).
Environment: Python 3.9.6 via python3, standard-library unittest; no dependency installation needed. Current host: Codex with shell execution available. AGENTS.md and this checkpoint are the canonical continuity entrypoints.

## Task
GREET-1: implement greet(name) in greeting.py.
Acceptance criteria (owned here because no existing specification exists):
- A: greet("Ada") returns "Hello Ada".
- B: a blank or whitespace-only name returns "Hello world".
- C: test_greeting.py uses unittest to cover A and B and passes with `python3 -m unittest`.
Current-session authorization: resume project, finish remaining work, verify it, and save the final handoff. Do not commit. Predecessor restrictions to file-only execution and criterion B were historical session scope.

## State
Complete: greeting.py implements A and B; test_greeting.py covers A and B, satisfying C. No implementation changes were needed in this session.
Unfinished: none within GREET-1.
Decisions: retain this file as the sole checkpoint; preserve existing untracked files. No commits made.
Writers / operations: current Codex work is complete; no other agents or background jobs were started by this session. Predecessor recorded its session stopping with no background jobs. System-wide process inventory via ps was denied by the environment, so independent detection of unrelated writers was unavailable. No continuing task processes are known.

## Evidence
Resume inspection: read skill, HANDOFF.md, AGENTS.md, README.md, and greeting.py; checked Git root/status, staged/unstaged diff summaries, and relevant file inventory. Actual files matched the predecessor checkpoint: A/B implemented, C absent.
Changes: added test_greeting.py with a named-greeting test and a subtest loop for empty string, a space, tabs/newlines, and mixed whitespace. Existing implementation preserved.
Validation on the final implementation/test contents, 2026-11-02:
- `python3 -m unittest`: PASS, 2 tests, all 4 blank-input subcases passed.
- `python3 --version`: Python 3.9.6.
- `git diff --check`: PASS for tracked changes; product files are untracked and were inspected directly.
- Git status: AGENTS.md, HANDOFF.md, greeting.py, and test_greeting.py remain untracked; no staged or tracked changes. No commits made.
Coverage limits: tests establish the specified string-input behavior; types outside the acceptance criteria are unspecified. Prior static-only B evidence is superseded by this successful runtime verification.

## Next
No remaining GREET-1 work. Review the uncommitted files if desired; commit only with separate user authorization.

## Recent outcomes
- 2026-11-02, Codex: resumed from actual files, added unittest coverage for A/B, ran `python3 -m unittest` successfully (2 tests), and saved a ready final handoff with GREET-1 done. No commit.
- 2026-11-02, Antigravity: implemented B using file tools only; left C for a session with execution capability.
- 2026-11-02, Codex: implemented and verified A only; saved a ready partial handoff with B/C deferred.
- 2026-11-02, Codex: initialized canonical continuity for GREET-1 from inspected files and user scope.
```

## Not covered

Claude Code execution (expired sign-in), Antigravity with shell access, Cursor, Gemini CLI,
GitHub Copilot, OpenCode, Cline, interrupted saves, concurrent writers and repeated trials.
