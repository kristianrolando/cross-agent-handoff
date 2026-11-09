# Project handoff

- format: cross-agent-handoff/1
- task_status: done
- handoff: ready
- writer: none
- updated_at: 2026-11-10T00:10:19+07:00

## Project
Cross-Agent Handoff: portable sequential project continuity and a Claude Code plugin wrapper.
Public source: https://github.com/kristianrolando/cross-agent-handoff
Rules: AGENTS.md. Contributor workflow: CONTRIBUTING.md. Claude adapter: CLAUDE.md.
User docs: README.md. Design: docs/architecture.md. Evidence: docs/validation.md.
Host loading/routing: skills/cross-agent-handoff/references/agents.md.
Release history: docs/releasing.md. Roadmap: docs/roadmap/.

## Task
Maintain the skill. v0.2.1 (token budget) is released; no task is open. Checkpoint format is
unchanged. Talk to the maintainer in Indonesian; write code and docs in English.

## State
Verified: v0.2.1 released 2026-11-10 (PR #10 merged as cca0182, tag 485679e, publish run
42661782630, Latest). It adds the inject word-target warning, section-only saves between steps,
compaction guidance and a shorter routing block. Details: CHANGELOG.md, docs/releases/v0.2.1.md,
docs/validation.md.
Verified: v0.2.0 released 2026-11-08 from 3e5f380 (tag 49811bb, run 42439322328). Work packages,
merges #1-#8 and live trials: CHANGELOG.md, docs/releases/v0.2.0.md,
docs/evidence/live-trial-2026-11-08.md and Git history. PR #9 merged as de65729.
Unfinished (optional, maintainer-only): Antigravity App/IDE, a second Claude account, Windows,
StopFailure on a real limit, trusted Codex hooks, guard; steps in
docs/evidence/live-trial-kit-v0.2.0.md. Deferred to v0.3.0: rolling history, media manifest,
style-tokens template, hooks for the other five hosts, Beads.
Decisions (maintainer approved 2026-11-08; read conservatively):
- Hooks are installed only by an explicit command; none ship inside the existing plugin.
- Keep format `cross-agent-handoff/1`; new metadata are optional bullets, no YAML front matter.
- Lock is advisory and opt-in; takeover of a stale lock needs user confirmation and a reason.
- Account aliases come from the session (prompt or env var); never persisted as identity.
- Stacked PRs: retarget the next PR to main before deleting a merged base branch (deleting
  #1's base once closed #2).
- PR commands need the owner's GitHub account (`kristianrolando`); the other gh account lacks
  write access.
Open question for the maintainer: agents and accounts available for live trials (brief
placeholders unfilled).
Writers / operations: none running.

## Evidence
- 82 tests OK on `feat/token-budget` (macOS, Python 3.9.6); `git diff --check` clean;
  `claude plugin validate .` passed with pre-existing warnings (root CLAUDE.md, no icon,
  system files).
- 82 tests OK on main aafa07e before PR #9; PR #8 passed six hosted jobs. Older runs:
  docs/validation.md.
- Live: Claude Code 2.1.318 ran the SessionStart and Stop hooks and the model quoted the
  injected context. StopFailure, PreCompact, guard, Codex and Antigravity hooks not run live.
- CI lessons: Ubuntu 3.9 needs the pinned ubuntu-24.04 runner; on Windows NUL stdin reports
  isatty, so hooks.py treats EOF as no confirmation.
- Hook facts: official pages fetched 2026-11-08, links in docs/roadmap/v0.2.0-audit.md.

## Next
No work remains for v0.2.1. Optional: the maintainer runs the remaining live-trial kit steps and
records them with docs/evidence/live-trial-template.md. Never move the v0.1.0, v0.1.1, v0.2.0 or
v0.2.1 tags.

## Recent outcomes
- 2026-11-08, Claude Code: ran headless live trials of v0.2.0; all passed; three findings fixed.
- 2026-11-08, Claude Code: published v0.2.0 and verified the release.
- 2026-11-10, Claude Code: merged PR #10 (token budget), tagged and published v0.2.1, verified.
