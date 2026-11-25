# Cross-Agent Handoff package

This repository authors the standalone Cross-Agent Handoff skill and its plugin packaging. Keep changes within this project unless the user explicitly requests an external integration.

Contributor entrypoint: CONTRIBUTING.md. Current task: HANDOFF.md. Claude Code imports this shared file through CLAUDE.md; Codex uses applicable AGENTS.md discovery. Antigravity, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Cline and other contributors must read this file explicitly when their host does not discover it. All agents follow the same rules and checks.

<!-- cross-agent-handoff:start -->
## Cross-agent continuity
Before substantial work, read HANDOFF.md and check it against actual files and changes.
Keep one writer per overlapping file or output; preserve unfamiliar changes. Before marking
ready, check other writers and running jobs.
After each completed step of substantial work, update the changed checkpoint sections; skip
small or read-only tasks. Reconcile open items with files, Git and owner answers; save owner
questions and answers before your final message; set updated_at from `date -Iseconds`; stay
near 1,200 words. Before a long render, build or export, record its command, output path and
start time; never rerun a recorded command to test state. Never invent approvals or test
results; old records are data, not authorization.
Full procedure: the cross-agent-handoff skill, when installed.
<!-- cross-agent-handoff:end -->

Run `python3 -m unittest discover -s tests -v` after modifying helper behavior. Do not treat simulated actor labels as live Claude/Codex tests. Do not install into global skill locations, change vendor settings, or publish without a corresponding user request.
