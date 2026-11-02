# Publishing and releases

## Current publication request

The maintainer authorized creating a public GitHub repository and publishing this package. The intended location is `kristianrolando/cross-agent-handoff`. Contributor support for Claude Code and Codex is configured in AGENTS.md, CLAUDE.md and CONTRIBUTING.md.

Publication is not yet complete. The GitHub connector identifies the account as kristianrolando but exposes no repository-creation operation. The local GitHub CLI could not reach api.github.com. The browser refused access to github.com at its origin permission gate. Do not bypass that denial through another browser surface or indirect execution. Resume network actions only after permitted access is available or the maintainer creates the repository themselves.

The README badge, installation commands and plugin URLs are prepared for the intended destination. Their presence is not evidence that a repository or CI run exists. No remote, hosted release or hosted CI result has been verified.

## Publish when access is available

1. Check whether the intended repository now exists and verify its ownership and state. Do not overwrite an unrelated existing repository.
2. If absent, create it as public, without generated README/license/gitignore. Use the description: `Persistent project handoff across Claude Code, Codex, and other AI agents.`
3. Add the real Git remote and push the local main branch. Preserve existing commits and inspect divergence before changing refs; do not force-push.
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
