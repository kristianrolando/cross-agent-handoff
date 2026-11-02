# Project handoff

- format: cross-agent-handoff/1
- task_status: in_progress
- handoff: working
- writer: Claude Code session (maintainer's Mac checkout)

## Project
Cross-Agent Handoff: portable sequential project continuity and a Claude Code plugin wrapper.
Public source: https://github.com/kristianrolando/cross-agent-handoff
Rules: AGENTS.md. Claude adapter: CLAUDE.md. Contributor workflow: CONTRIBUTING.md.
User docs: README.md. Design: docs/architecture.md. Evidence: docs/validation.md.
Host loading/routing: skills/cross-agent-handoff/references/agents.md.
Release and synchronization history: docs/releasing.md.

## Task
Critical review of reliability, portability, usability and public accuracy, with justified
fixes. The maintainer then approved all review recommendations: commit and push the fixes,
confirm hosted CI, run live host trials where CLIs exist, and publish release v0.1.1.
Still not authorized: global skill installs, vendor settings changes, moving v0.1.0.

## State
Verified at start: main matched origin/main at b8ad312 with a clean tree. Only release is
v0.1.0 (tag at 666e04c, unchanged). plugin.json on main is 0.1.1 and is not released.

Review conclusion: the core lifecycle (SKILL.md, recovery, one checkpoint, ownership table,
untrusted-history rules) is sound and concise. Defects found and fixed (committed with this checkpoint):
- release.yml: removed the v0.1.0 bootstrap push trigger and default tag; with manifest 0.1.1
  they would fail the version check on any main push touching the file or a default dispatch.
- ci.yml and release.yml: `git diff --check` compared nothing on a fresh checkout; now checks
  the committed tree against the empty tree.
- references/agents.md and README: corrected host paths/activation from official docs (Copilot
  reads `.agents`/`.claude` skills and has no slash command; Cursor reads `.claude/skills`;
  Cline has no documented `.agents/skills` and enables skills by default; Antigravity CLI slash
  commands; `~/.agents/skills` user paths). Replaced the claim that one `.agents` copy serves
  the shared hosts with the actual two-folder coverage. Added the Claude AGENTS.md-vs-CLAUDE.md
  rule and the Gemini CLI GEMINI.md default. Updated the redirected Codex docs link.
- scripts/handoff.py: placeholder check no longer rejects legitimate uppercase `REPLACE`; clear
  message when a save lock exists. Two tests added in tests/test_handoff.py.
- docs: releasing.md, ci.md, file-map.md updated to match workflows; validation.md corrected
  the "ten files" installer record (nine tracked files; the tenth was most likely `.DS_Store`)
  and gained a dated review section.
Decisions: no new hosts, files, dependencies or per-agent state; core SKILL.md unchanged.

Writers / operations: none from this session. Hosted run 41447769806 for b8ad312 completed
with success (checked via gh at the end of this review).

## Evidence
- `python3 -m unittest discover -s tests -v`: 28 passed (macOS, Python 3.9.6) on the
  uncommitted working tree.
- `git diff --check` clean; `git diff --check <empty tree> HEAD` clean on b8ad312.
- Workflow and openai.yaml YAML parsed with Ruby; workflows not executed on GitHub; actionlint
  not available.
- `handoff.py check` on this repository: no errors or warnings before this rewrite.
- Official docs fetched 2026-11-02 for Claude Code (skills, memory), Codex, Antigravity,
  Cursor, Gemini CLI (skills, GEMINI.md), Copilot, OpenCode and Cline.
- not_run: Claude plugin validation (packaging unchanged), live host discovery, model handoffs.

## Next
Push this commit and confirm all four hosted Package checks jobs, including the new whitespace
step. Then run live trials with locally installed Claude Code, Codex and Antigravity CLIs in
disposable projects, add docs/releases/v0.1.1.md, and push tag v0.1.1.

## Recent outcomes
- Published MIT v0.1.0 and verified public discovery and Claude/Codex copy installation.
- Reconciled the original Mac checkout without losing interrupted documentation.
- Added six documented native-skill host routes and a portable fallback for other agents.
- Verified expanded installer selection, complete resources and existing package checks.
- 2026-11-02 review: fixed release/CI workflow defects, host-path inaccuracies and helper
  placeholder false positives; maintainer approved commit, live trials and v0.1.1 release.
