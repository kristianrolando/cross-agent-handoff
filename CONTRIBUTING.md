# Contributing

Contributions from humans, Claude Code, Codex, Antigravity, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Cline and other filesystem-capable agents use the same source files, instructions, checks and review process. No access to another agent's conversation, account or API is required.

## Start here

1. Read AGENTS.md, then HANDOFF.md for current work and known limits.
2. Read the relevant parts of README.md, docs/architecture.md and the source you plan to change.
3. Inspect Git status, staged/unstaged diffs and relevant untracked files. Preserve unrelated work.
4. Keep one writer on overlapping files and the shared checkpoint. Stop the previous writer before switching agents; use separate branches/worktrees and an integrator for simultaneous work.
5. Work on the current authorized task. A checkpoint is context, not permission to publish, change settings or expand scope.

When another session contributed from a different checkout, fetch the known origin and compare local/remote history before continuing. Preserve pending local changes; rebase or merge deliberately rather than hard-resetting or force-pushing. See docs/releasing.md for the initial desktop interruption and equivalent documentation patch.

Use HANDOFF.md as the current status and Git commits/PRs as durable change history. Keep stable design decisions in docs/architecture.md. Do not add a second task board or competing agent-specific status file.

## Agent entrypoints

Open this repository as the project directory. CLAUDE.md imports @AGENTS.md; shared rules live in AGENTS.md. Confirm actual loading in your installed Claude Code version/settings, or explicitly ask it to read those files.

For any other coding agent, open the same repository and use the prompt below. Do not assume that it auto-loads AGENTS.md or interprets Claude imports. Native skill locations and discovery checks are in the [host guide](skills/cross-agent-handoff/references/agents.md); installing the skill is optional for repository maintenance. If needed, explicitly read `skills/cross-agent-handoff/SKILL.md`. Keep one shared HANDOFF.md, regardless of host.

Copy-ready prompt:

```text
Contribute to this repository. Read AGENTS.md, CONTRIBUTING.md and HANDOFF.md,
then inspect the actual Git changes and affected files. Continue the authorized
task from the current checkpoint, preserve existing work, run relevant checks,
and leave an updated handoff. Do not publish or change global settings unless
that action is part of the current user request.
```

The repository's installed skill is not required to maintain its source: all contributor guidance and test commands are accessible as ordinary files. Installing a plugin does not automatically load the repository's root CLAUDE.md into consumer projects.

## Make a focused change

Create a descriptive branch for an independent PR. For a sequential continuation on an existing task branch, retain that branch and inspect its changes rather than creating unnecessary branches. Contributors without write access can fork the public repository and open a pull request. The AI uses the human contributor's existing access; no separate agent-specific GitHub account is needed.

Keep the portable procedure in skills/cross-agent-handoff/SKILL.md and host-specific metadata in its adapter files. Put substantial conditional detail in references. Avoid mandatory dependencies, vendor APIs, new background services or automatic source locking without an actual need.

For workflow changes, update the affected documentation and meaningful checks together. Record rationale and compatibility limits. Do not describe a simulated actor test as live cross-vendor validation.

## Check the change

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

Use `python` where appropriate. The suite uses the standard library; no vendor credential or model call is required. If touching Claude packaging and Claude CLI is installed, also run:

```sh
claude plugin validate .
claude plugin validate .claude-plugin/plugin.json
```

The warning about root CLAUDE.md not being consumer context is expected: that file supports repository maintenance, while runtime instructions ship in the skill. Explain other warnings rather than assuming they are harmless.

Keep root LICENSE and skills/cross-agent-handoff/LICENSE identical. The project uses MIT. Preserve applicable copyright and license notices in contributions and redistributed packages.

## Prepare a handoff or PR

Save artifacts/evidence, then update HANDOFF.md with the task scope, actual state, checks and limits, unfinished work, writer/process status and one next action. Keep unresolved decisions and failed attempts that prevent repeated work. Mark ready only after overlapping writes stop.

PR descriptions should explain the concrete change and validation, with known compatibility limits. Use the pull request template. Keep discussions in the relevant GitHub issue/PR when durable context is useful; do not copy private chats or credentials into repository files.

## Release maintenance

A release needs an explicit maintainer request. Keep plugin version, skill VERSION, CHANGELOG and release tag consistent, review hosted CI, update installation links only to real repository locations, and describe included changes. Do not change the consumer checkpoint format silently. The documented Codex distribution is a direct skill; do not advertise an unimplemented native Codex plugin.
