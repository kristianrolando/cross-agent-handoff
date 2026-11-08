# Project handoff

- format: cross-agent-handoff/1
- task_status: done
- handoff: ready
- writer: none
- updated_at: 2026-11-08T09:38:13+07:00

## Project
Cross-Agent Handoff: portable sequential project continuity and a Claude Code plugin wrapper.
Public source: https://github.com/kristianrolando/cross-agent-handoff
Rules: AGENTS.md. Contributor workflow: CONTRIBUTING.md. Claude adapter: CLAUDE.md.
User docs: README.md. Design: docs/architecture.md. Evidence: docs/validation.md.
Host loading/routing: skills/cross-agent-handoff/references/agents.md.
Release history: docs/releasing.md. Roadmap: docs/roadmap/.

## Task
v0.2.0 roadmap. Brief: docs/roadmap/v0.2.0-mission-brief.md (verbatim). Approved plan and
host hook facts: docs/roadmap/v0.2.0-audit.md. Talk to the maintainer in Indonesian; write
code and docs in English. Order: Step 0 (roadmap + CI) → WP4-lite → WP1 → WP2 → WP3-lite →
WP5-lite → WP8. WP7 tests go with each package. Deferred to v0.3.0: rolling history, full
media manifest/style tokens, hooks for the other five hosts, Beads.

## State
Done: Step 0 on local branch `chore/v0.2.0-roadmap` (roadmap docs, 6-job CI matrix).
Done: WP4-lite on stacked branch `feat/wp4-checkpoint-metadata`. handoff.py validates optional
`updated_at`, `language` and `profile` lines (clear errors, future-time warning) and exposes
`updated_at()` for WP1. The template gains an `updated_at` line. SKILL.md, helper.md, setup.md
(migration note), architecture.md (decision) and the after example were updated.
Done: WP1 on stacked branch `feat/wp1-auto-snapshot`. Skill scripts `snapshot.py` (Git state,
recent files, media size/mtime, optional partial hash, atomic `.handoff/auto/latest.json`,
pruned history, self-ignoring folder, installed skill folders excluded, once-per-version
staleness guard, always exit 0), `inject.py` (resume context plus live scan for files and
commits newer than the checkpoint; works without hooks) and `hooks.py` (opt-in install,
remove, status for Claude Code, Codex, Antigravity; dry-run; confirmation). New
references/hooks.md; SKILL.md, setup.md block, recovery.md, helper.md, template, README,
architecture.md, file map and validation updated. Correction to the brief: the warning uses
files or commits newer than the checkpoint, not "latest.json newer than HANDOFF.md".
Done: WP2 on stacked branch `feat/wp2-installer`: `scripts/install.py` (--hosts to the two
folders, --user, --update with local-edit report and confirmation, --uninstall keeping project
records and removing own hooks, --doctor with VERSION and MANIFEST.sha256, --with-hooks,
--dry-run), `VERSION` 0.2.0-dev, tests/test_install.py, docs (agents.md, setup.md, README,
architecture, file map, validation). Cline maps to `.claude/skills/` to avoid a third copy.
Done: WP3-lite on stacked branch `feat/wp3-lock`: `scripts/lock.py` (status, acquire,
release, force-release; held locks, fresh or stale, need --confirm-takeover after user
confirmation; alias from flag or HANDOFF_AGENT_ALIAS, email-like labels rejected), switch log
`.handoff/log.jsonl`, lock ignored via `.handoff/.gitignore`, heartbeat refreshed by hook
snapshots for the same host, inject warning, references/lock.md, docs. Rolling history deferred.
Done: WP5-lite on stacked branch `feat/wp5-profiles`: `assets/profiles/{game,video,motion}.md`
sections inserted after State by `handoff.py init --profile`, `profile:` metadata, warning for
a listed profile without a section, inject prints running operations and renders,
references/profiles.md, README/SKILL/setup/helper/architecture/file map/validation.
Deferred to v0.3.0: media_manifest.py and a style-tokens template.
Fixed: WP5 Windows CI failure (CRLF template in profile composition), commit d3f1bbd.
Done: WP8 on stacked branch `feat/wp8-release-prep`: live-trial kit and record template in
docs/evidence/ (results empty), CHANGELOG.md, docs/releases/v0.2.0.md with upgrade notes,
version 0.2.0 in plugin.json and VERSION with a consistency test, README rows and links,
v0.2.0 checklist in docs/releasing.md. README badge stays v0.1.1 until the release exists.
Merged into main 2026-11-08 at the maintainer's request, in order, with merge commits: #1 fa65c0c,
#2 47302e2, #3 c9bddf2, #4 0d195da, #5 c80fa13, #6 7d2cbd2, #7 99e3acf. main's tree equals the
tested #7 head 0204fa7. Merged branches were deleted. Incident: deleting #1's branch closed #2
because this repo does not retarget PRs; the base was restored at the same commit, #2 reopened
and retargeted, and later PRs were retargeted before their base was deleted. No code was lost.
Live trials run 2026-11-08 at the maintainer's request (headless CLIs, disposable projects):
GAME chain Claude Code → Codex → Antigravity CLI → Claude Code, abrupt-stop recovery, video and
motion profiles all passed; record in docs/evidence/live-trial-2026-11-08.md. Three findings
fixed on branch `fix/live-trial-findings` (Antigravity Stop event name, clock-read updated_at
guidance, actionable observed_file warning) with README, notes, kit, hooks guide and validation
updated.
PR #8 (live-trial findings) merged as aafa07e after all 12 checks passed. CHANGELOG dated for
the v0.2.0 release on 2026-11-08 at the maintainer's request ("Merge #8, then release").
Released: v0.2.0 published 2026-11-08 from 3e5f380 (annotated tag 49811bb, pushed by the agent
at the maintainer's request); publish run 42439322328 succeeded; release is Latest; README badge
updated. v0.1.0 and v0.1.1 tags unchanged.
Unfinished (optional, maintainer-only): Antigravity App/IDE, a second Claude account, Windows,
StopFailure on a real limit, trusted Codex hooks, guard; steps in the live-trial kit. Deferred to
v0.3.0: rolling history, media manifest, style-tokens template, hooks for the other five hosts.
Decisions (maintainer approved the plan 2026-11-08; read conservatively):
- Hooks are installed only by an explicit command; none ship inside the existing plugin.
- Keep format `cross-agent-handoff/1`; new metadata are optional bullets, no YAML front matter.
- Lock is advisory and opt-in; takeover of a stale lock needs user confirmation and a reason.
- Account aliases come from the session (prompt or env var); never persisted as identity.
- Packages were delivered as stacked PRs #1-#7, now merged. For future stacks here, retarget the
  next PR to main before deleting a merged base branch.
  gh's active account lacks write access; PR commands use the owner's token via GH_TOKEN only.
Open question for the maintainer: agents and accounts available for live trials (brief
placeholders unfilled).
Writers / operations: none running.

## Evidence
- 82 tests OK on main aafa07e (macOS, Python 3.9.6); PR #8 passed six hosted jobs.
- 80 tests OK on main 99e3acf (macOS, Python 3.9.6). All seven PR heads passed six hosted jobs
  before merge; main's own run 42436655218 was in progress when this was saved.
- 79 tests OK after WP5-lite (macOS, Python 3.9.6).
- 73 tests OK after WP3-lite (macOS, Python 3.9.6). WP2 PR #4 CI green on all six jobs.
- 65 tests OK after WP2 (macOS, Python 3.9.6); real v0.1.1 tag upgrade checked manually.
- `python3 -m unittest discover -s tests -v`: 54 tests OK after WP1, macOS 27.0.1,
  Python 3.9.6 (abrupt stop, clean clone, commits after checkpoint, spaces, CRLF, 2,000 files,
  guard loop protection, hook merge/removal, Codex command run through a shell).
- Live: Claude Code 2.1.318 ran the installed SessionStart and Stop hooks once in a
  disposable project; the model quoted the injected context. Details and limits in
  docs/validation.md. StopFailure, PreCompact, guard, Codex and Antigravity hooks not run live.
- First hosted runs: macOS 3.9/3.14 and Ubuntu 3.14 passed. Ubuntu 3.9 failed setup because
  ubuntu-latest is now 26.04 with no 3.9 build (fixed: pinned ubuntu-24.04). Windows failed one
  test: NUL stdin reports isatty, so hooks.py hit EOFError (fixed: EOF means no confirmation).
  Re-runs passed: PR checks green on #1 (d92b18c), #2 (f58f0e1) and #3 (04a985b), all six jobs.
  Main's own CI will hit the Ubuntu 3.9 issue until #1 is merged.
- Hook facts: official pages fetched 2026-11-08, links in the audit.

## Next
No work remains for v0.2.0. Optional: the maintainer runs the remaining live-trial kit steps and
records them with docs/evidence/live-trial-template.md. Never move the v0.1.0, v0.1.1 or v0.2.0 tags.

## Recent outcomes
- 2026-11-08, Claude Code: WP5-lite game, video and motion profiles committed.
- 2026-11-08, Claude Code: WP8 release preparation committed; v0.2.0 awaits merge and approval.
- 2026-11-08, Claude Code: merged PRs #1-#7 into main; v0.2.0 awaits release approval.
- 2026-11-08, Claude Code: ran headless live trials of v0.2.0; all passed; three findings fixed.
- 2026-11-08, Claude Code: published v0.2.0 and verified the release.
