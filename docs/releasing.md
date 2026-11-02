# Publishing and releases

## Publication status

The maintainer authorized publication at `kristianrolando/cross-agent-handoff`. The public repository has been created and ownership/visibility verified. Initial source upload, hosted CI review and release creation are in progress. Root contributor files support both Claude Code and Codex.

The README badge, installation commands and plugin metadata point to that repository. Inspect the actual GitHub state before reporting a release or CI pass.

## Release procedure

1. Verify repository ownership, visibility and current state. Do not overwrite unrelated work.
2. Confirm origin points to the real repository.
3. Push the local main branch. Preserve existing commits and inspect divergence before changing refs; do not force-push.
4. Set topics: agent-skills, claude-code, codex, handoff, ai-agents. Inspect the first hosted Package checks run and fix actual failures.
5. Verify the public skill-install route and Claude plugin marketplace route against the hosted files. Keep the direct skill route for Codex; no native Codex plugin is implemented.
6. Create a release tagged v0.1.0 at the verified commit. The plugin manifest version is 0.1.0. Use the release notes below.
7. Record actual repository, run and release links in HANDOFF.md and docs/validation.md. Keep maintainer feedback distinct from automated or directly observed evidence.

## Initial release notes

Title: Cross-Agent Handoff v0.1.0

Portable sequential handoff across Claude Code, Codex and filesystem-capable agents. Save project context in one compact checkpoint, inspect the actual project on resume, and recover supported facts after interruption without relying on another agent's conversation.

Included:
- Initialize, resume, checkpoint, handoff and recovery procedures.
- Reusable checkpoint template and optional standard-library Python helper.
- Claude Code plugin/catalog and direct skill installation for Codex.
- Shared Claude/Codex contributor instructions and PR template.
- Quick start, before/after examples and compatibility documentation.
- MIT license bundled with the standalone skill.
- Automated protocol/package checks and a configured cross-platform CI matrix.

The core has no cloud, vendor API, IDE or runtime dependency. Python 3.9+ is needed only for the optional helper. The skills CLI installer has its own Node.js requirement. Maintainer-reported successful use and automated evidence are documented separately. The workflow is sequential; no automatic crash save, cross-device synchronization or overlapping-source lock is promised.
