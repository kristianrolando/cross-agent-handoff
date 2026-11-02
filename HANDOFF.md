# Project handoff

- format: cross-agent-handoff/1
- task_status: done
- handoff: ready
- writer: none

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
At review start main matched origin/main at b8ad312. v0.1.1 is now released (Latest) from
source 5eb5279; v0.1.0 remains unchanged at 666e04c. plugin.json is 0.1.1.

Review conclusion: the core lifecycle (SKILL.md, recovery, one checkpoint, ownership table,
untrusted-history rules) is sound and concise. Defects found and fixed in ee5996d:
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

Approved follow-up: ee5996d pushed; Package checks 41452193109 passed all four jobs, including
the new committed-whitespace step, and did not start the release workflow. Release source
5eb5279 adds v0.1.1 notes, README badge and live-trial records; Package checks 41453750169
passed all four jobs on it.
Release: the agent's tag push was refused by its safety check, so the maintainer pushed the
annotated v0.1.1 tag. Publish release run 41460822031 passed and created the release; the
README v0.1.1 badge now resolves.

Writers / operations: none. Trial agents ran in a disposable project outside the repository
and have exited.

## Evidence
- `python3 -m unittest discover -s tests -v`: 28 passed locally (macOS, Python 3.9.6); hosted
  runs above passed on Ubuntu 3.9/3.13, macOS 3.13 and Windows 3.13.
- Workflow and openai.yaml YAML parsed with Ruby; actionlint not available.
- Release: https://github.com/kristianrolando/cross-agent-handoff/releases/tag/v0.1.1 is
  Latest, not draft/prerelease, tag resolves to 5eb5279, body matches docs/releases/v0.1.1.md.
  Publish run: https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41460822031
- Official docs fetched 2026-11-02 for Claude Code (skills, memory), Codex, Antigravity,
  Cursor, Gemini CLI (skills, GEMINI.md), Copilot, OpenCode and Cline.
- Live trial (docs/evidence/live-trial-2026-11-02.md): Codex CLI 0.166 → Antigravity CLI 1.2.3
  → fresh Codex session finished GREET-1 from files only; final tests 2 passed. Claude Code
  2.1.287 listed the skill but its sign-in had expired. Headless Antigravity denied shell
  commands; the auto-approve flag was blocked by this session's safety check and not used.
- `claude plugin validate .` and `.claude-plugin/plugin.json` passed; only the expected
  root CLAUDE.md warning.
- not_run: Cursor, Gemini CLI, Copilot, OpenCode and Cline live runs.

## Next
No work remains for this task. Open options, each needing a maintainer request: rerun the
live trial with Claude Code after re-signing in, try Antigravity with shell access, or trial
Cursor, Gemini CLI, Copilot, OpenCode or Cline. Never move the v0.1.0 or v0.1.1 tags.

## Recent outcomes
- Published MIT v0.1.0 and verified public discovery and Claude/Codex copy installation.
- Added six documented native-skill host routes and a portable fallback for other agents.
- Verified expanded installer selection, complete resources and existing package checks.
- 2026-11-02 review: fixed release/CI workflow defects, host-path inaccuracies and helper
  placeholder false positives; pushed with passing hosted checks.
- 2026-11-02: live Codex → Antigravity → Codex trial recorded.
- 2026-11-02: v0.1.1 released from 5eb5279 (maintainer pushed the tag); publish run verified.
