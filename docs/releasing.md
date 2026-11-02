# Publishing and releases

## Publication status

Public repository: [kristianrolando/cross-agent-handoff](https://github.com/kristianrolando/cross-agent-handoff).
Latest release: [v0.1.1](https://github.com/kristianrolando/cross-agent-handoff/releases/tag/v0.1.1) ([notes](releases/v0.1.1.md)), tag pushed by the maintainer on verified source commit `5eb5279d461807582158474aead506692d5c8348`.
Published initial release: [v0.1.0](https://github.com/kristianrolando/cross-agent-handoff/releases/tag/v0.1.0). The tag targets verified source commit `666e04c279d312a375a9ba06b5f9e6dfd3d92204`.

All four release-source CI jobs and the release workflow succeeded; the public Skills CLI discovered and copied the complete skill to both host directories in a disposable project. See docs/validation.md for actual run links and limits. Contributor support is shared through AGENTS.md, CLAUDE.md, CONTRIBUTING.md and HANDOFF.md.

Keep a release frozen at its verified source commit. Closing handoff/evidence updates may follow on main without moving that tag. Never force-move an existing public tag.

## Release procedure

1. Verify repository ownership, visibility and current state. Do not overwrite unrelated work.
2. Confirm origin points to the real repository.
3. Push the local main branch. Preserve existing commits and inspect divergence before changing refs; do not force-push.
4. Set topics: agent-skills, claude-code, codex, handoff, ai-agents. Inspect the first hosted Package checks run and fix actual failures.
5. Verify the public skill-install route and Claude plugin marketplace route against the hosted files. Use direct skills for the other documented hosts; the included plugin wrapper remains Claude-specific.
6. On an explicit maintainer release request, use a new tag matching the current plugin manifest version and prepare matching versioned notes. The initial v0.1.0 release below is historical; never reuse or move its tag.
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

The Publish release workflow checks the manifest version, versioned notes, and package suite before publishing with GitHub's built-in token. Write permission is limited to the publishing job. It runs only on a pushed version tag or a manual dispatch naming the tag; it never runs on ordinary main-branch pushes. An existing release is left unchanged. No personal token is required. The earlier v0.1.0 bootstrap trigger was removed after that release was published, because it would now fail against the 0.1.1 manifest. For a future version, update the manifest and versioned notes in a reviewed change, then trigger explicitly.

## Resolved desktop synchronization

The initial desktop interruption is resolved. The original Mac checkout was reconciled with origin/main, and commit `b0d3e39` records the verification. The interrupted documentation commit `57c17ab` and its published equivalent `fddd8d1` have identical file snapshots; `git diff --quiet 57c17ab fddd8d1` succeeded. The equivalent local commit was dropped during rebase, with no documentation changes lost. Local main and the public branch subsequently matched at `b0d3e39` with a clean working tree.

This is historical evidence of the completed recovery, not a pending synchronization task or a claim that branches remain synchronized forever. For future work from another checkout, inspect current Git status, fetch the known origin, and compare history before choosing whether to fast-forward, rebase or merge. Preserve unfamiliar changes and resolve actual conflicts deliberately.
