# Project handoff

- format: cross-agent-handoff/1
- task_status: done
- handoff: ready
- writer: none
- updated_at: 2026-11-26T05:37:27+07:00

## Project
Cross-Agent Handoff: portable sequential project continuity and a Claude Code plugin wrapper.
Public source: https://github.com/kristianrolando/cross-agent-handoff
Rules: AGENTS.md. Contributor workflow: CONTRIBUTING.md. Claude adapter: CLAUDE.md.
User docs: README.md. Design: docs/architecture.md. Evidence: docs/validation.md.
Host loading/routing: skills/cross-agent-handoff/references/agents.md.
Release history: docs/releasing.md. Roadmap: docs/roadmap/.

## Task
Maintain the skill. v0.3.0 (compaction, size hints, doctor) is released (2026-11-26; PR #19 8b716a5, prep PR #20 edcefa5, tag object e21477e, publish run 45714596537, Latest). v0.2.3 (small fixes) is released (2026-11-26; PR #16 7fe0ffe, prep PR #17 ea9f59c, tag object 350e54d, publish run 45711238994, Latest). v0.2.1 is released. v0.2.2 (audit fixes) is released (2026-11-26; PR #12 a395f52, prep PR #13 9333c35, tag
object b4b9244, publish run 45705163155, Latest). Checkpoint format is
unchanged. Talk to the maintainer in Indonesian; write code and docs in English.

## State
Verified: PR #19 merged as 8b716a5 with all 12 hosted checks; 98 tests OK on Python 3.9.6 and 3.15.2. Routing block now 155 words with markers (was 128):
adds "paste date -Iseconds" and "compact in the same save"; 26 side-by-side runs: size within 1,300 words 13/13 vs 6/13, real clock
13/13 vs 7/13, planted facts kept 35/36 (docs/evidence/live-trial-2026-11-26-routing-block-v2.md; one model, synthetic project).
Also: localized size hints in check/save/inject (F10, F20), doctor plugin route (F25), video profile and host-memory guidance
(F09, F06), copy-before-compaction in SKILL.md. Not done: shared Git module (F35, F16), rolling history, other-host hooks.
Verified: PR #16 merged as 7fe0ffe: 93 tests OK on Python 3.9.6 and 3.15.2 and all 12 hosted checks; the three new tests and the
extended hooks case fail on v0.2.2 scripts. Adds the `${CLAUDE_PROJECT_DIR}` and shell-expansion hook-command patch (F13), unreadable
manifest reporting in install.py, save warnings (F23) and the edit-tool guidance in SKILL.md (F08). Version files, CHANGELOG
(0.2.3, 2026-11-26), docs/releases/v0.2.3.md and docs/validation.md updated; README badge and docs/releasing.md wait for the
release. Live trial of the v0.2.2 routing block: docs/evidence/live-trial-2026-11-26-routing-block.md (PR #15).
Verified: v0.2.2 released from 9333c35; PR #12 merged as a395f52: 90 tests OK on Python 3.9.6 and 3.15.2 and all 12 hosted
checks; the seven new checks fail on v0.2.1 scripts. Closes audit findings F01-F05, F07, F12,
F13, F15-F17, F24 (docs/evidence/audit-2026-11-26.md). Deferred to v0.3.0: alt-A compaction (F08, F23, hook-command and manifest items moved to v0.2.3). Routing text is not shown to change agent behavior (no live trial).
The three audit `.pyc` files were deleted with the maintainer's approval.
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
No work remains for v0.3.0. Later: repeat the routing-block trial on a second host and with the skill installed; shared Git module (F35, F16);
rolling history only if evidence appears. Never move the v0.1.0 to v0.3.0 tags.

## Recent outcomes
- 2026-11-26, Claude Code: tagged and published v0.3.0 and verified the release.
- 2026-11-26, Claude Code: ran three more trial batches, adopted the new routing block, built v0.3.0 on feat/v0.3.0.
- 2026-11-26, Claude Code: tagged and published v0.2.3 and verified the release.
- 2026-11-26, Claude Code: ran the v0.2.2 routing-block live trial (PR #15), prepared v0.2.3 and merged PR #16 (7fe0ffe).
- 2026-11-26, Claude Code: prepared v0.2.2 from the 2026-11-26 audit and merged PR #12 and #13, tagged and published v0.2.2.
- 2026-11-08, Claude Code: ran headless live trials of v0.2.0; all passed; three findings fixed.
- 2026-11-08, Claude Code: published v0.2.0 and verified the release.
- 2026-11-10, Claude Code: merged PR #10 (token budget), tagged and published v0.2.1, verified.
