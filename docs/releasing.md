# Publishing and releases

## Publication status

Public repository: [kristianrolando/cross-agent-handoff](https://github.com/kristianrolando/cross-agent-handoff).
Published initial release: [v0.1.0](https://github.com/kristianrolando/cross-agent-handoff/releases/tag/v0.1.0). The tag targets verified source commit `666e04c279d312a375a9ba06b5f9e6dfd3d92204`.

All four release-source CI jobs and the release workflow succeeded; the public Skills CLI discovered and copied the complete skill to both host directories in a disposable project. See docs/validation.md for actual run links and limits. Contributor support is shared through AGENTS.md, CLAUDE.md, CONTRIBUTING.md and HANDOFF.md.

Keep a release frozen at its verified source commit. Closing handoff/evidence updates may follow on main without moving that tag. Never force-move an existing public tag.

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

## Release workflow

The Publish release workflow checks the manifest version, versioned notes, and package suite before publishing with GitHub's built-in token. Write permission is limited to the publishing job. It accepts version-tag pushes or manual dispatch. A main-branch change to the workflow also attempts the fixed initial v0.1.0 release to bootstrap publication; if that release already exists, it leaves it unchanged. No personal token is required. Do not edit the bootstrap default to publish a future version; use a reviewed version/tag/notes update and explicit release trigger.

The original desktop may retain an unpushed documentation-only commit 57c17ab from the environment interruption. Its five-file patch was restored on GitHub as fddd8d1. Before resuming that local checkout, inspect `git status`, fetch origin, and compare the local/remote log. If the worktree is clean, rebase the local main branch onto origin/main; Git can skip the already-applied equivalent patch. Preserve unfamiliar work, resolve any actual conflict, and never force-push or hard-reset merely to align state.
