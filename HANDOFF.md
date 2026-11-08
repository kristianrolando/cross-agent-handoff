# Project handoff

- format: cross-agent-handoff/1
- task_status: in_progress
- handoff: ready
- writer: none
- updated_at: 2026-11-08T08:03:23+07:00

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
In progress: WP1 on stacked branch `feat/wp1-auto-snapshot`. Done so far: skill scripts
`snapshot.py` (Git state, recent files, media size/mtime, optional partial hash, atomic
`.handoff/auto/latest.json`, pruned `history.jsonl`, self-ignoring `.handoff/auto/.gitignore`,
once-per-checkpoint staleness guard, always exit 0) and `inject.py` (resume context with a
live scan for files and commits after the checkpoint; works without hooks), plus
tests/test_autosave.py. Deliberate correction to the brief: "latest.json newer than
HANDOFF.md" is not used as the warning signal, because a per-turn Stop snapshot is always
newer; the warning uses files or commits newer than the checkpoint instead.
Unfinished in WP1: `scripts/hooks.py` (install/remove/status for Claude, Codex, Antigravity),
`references/hooks.md`, SKILL.md/setup.md/recovery.md routing, README/architecture updates.
Decisions (maintainer approved the plan 2026-11-08; read conservatively):
- Hooks are installed only by an explicit command; none ship inside the existing plugin.
- Keep format `cross-agent-handoff/1`; new metadata are optional bullets, no YAML front matter.
- Lock is advisory and opt-in; takeover of a stale lock needs user confirmation and a reason.
- Account aliases come from the session (prompt or env var); never persisted as identity.
- Branches are stacked locally, one per package. No push or PR until the maintainer allows it.
Open questions for the maintainer: push/PR permission; agents and accounts available for live
trials (brief placeholders unfilled).
Writers / operations: none running.

## Evidence
- `python3 -m unittest discover -s tests -v`: 47 tests OK after the WP1 scripts, macOS
  27.0.1, Python 3.9.6. Includes abrupt-stop scenario, fresh-clone false-positive check,
  guard loop protection, 2,000-file speed check, paths with spaces, CRLF.
- Manual run on this repo: inject 0.11 s, snapshot 41 ms.
- Widened CI matrix not yet run on GitHub (nothing pushed). setup-python manifest checked:
  3.9 resolves to 3.9.13 on macOS arm64 and Windows x64; 3.14.10 exists on all three OSes.
- Hook facts: official pages fetched 2026-11-08, links in the audit.

## Next
Write `skills/cross-agent-handoff/scripts/hooks.py` to merge and remove opt-in hook entries
for Claude Code (settings.local.json by default), Codex (.codex/hooks.json) and Antigravity
(.agents/hooks.json), with --dry-run and tests.

## Recent outcomes
- Published v0.1.1; release tags and passing CI were verified.
- Added eight attributed brand marks to responsive README hero artwork.
- 2026-11-08, Claude Code: completed the v0.2.0 Phase 0 audit; maintainer approved the plan.
- 2026-11-08, Claude Code: Step 0 committed locally (roadmap docs, 6-job CI matrix).
- 2026-11-08, Claude Code: WP4-lite optional metadata validated and committed locally.
