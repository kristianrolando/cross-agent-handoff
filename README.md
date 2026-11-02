# Cross-Agent Handoff

[![Package checks](https://github.com/kristianrolando/cross-agent-handoff/actions/workflows/ci.yml/badge.svg)](https://github.com/kristianrolando/cross-agent-handoff/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Continue a project in Claude Code, Codex, or a new session without relying on the previous conversation. Keep the goal, verified progress, unfinished work, decisions and next step in the project itself.

**One compact checkpoint. No cross-vendor API calls. No additional cloud service.**

Use it when a usage limit interrupts work, when you switch agents, or when you return to a project later. The core needs ordinary filesystem access; Python and Git are optional.

## Quick start

### 1. Install the skill

Run from the project where you want to use the skill:

```sh
npx skills add kristianrolando/cross-agent-handoff --skill cross-agent-handoff
```

Choose Claude Code or Codex in the installer. The installer needs Node.js 22.20+; the core workflow does not need Node.js. To install without this CLI, download or clone this repository and copy the complete skill folder using [installation options](#installation-options).

For direct installation, the project locations are `.claude/skills/cross-agent-handoff/` for Claude Code and `.agents/skills/cross-agent-handoff/` for Codex. See [installation options](#installation-options) for user-wide installation and the Claude plugin route. Avoid installing both the direct skill and plugin in the same host.

### 2. Initialize your project

Choose the prompt for your host:

| Host | Prompt |
| --- | --- |
| Claude Code, direct skill | `/cross-agent-handoff Initialize continuity in this project. Reuse existing documentation and preserve project instructions.` |
| Claude Code, plugin | `/cross-agent-handoff:cross-agent-handoff Initialize continuity in this project. Reuse existing documentation and preserve project instructions.` |
| Codex | `Use $cross-agent-handoff to initialize continuity in this project. Reuse existing documentation and preserve project instructions.` |

The agent inspects the project, reuses an existing checkpoint or creates `HANDOFF.md`, and adds a short routing block when needed. For a new project, include your goal and acceptance criteria. Initialization does not scaffold an application or choose a tech stack.

### 3. Save and switch

In the outgoing agent:

```text
Use cross-agent-handoff to save a handoff. Record actual progress, unfinished
work, evidence and limits, running operations, and one next action.
Start no new implementation.
```

Stop the outgoing session and any operations writing overlapping files. Open the **same project files** in the next agent:

```text
Use cross-agent-handoff to resume this project. Read the checkpoint and
applicable instructions, inspect actual files and changes, then continue
from the next supported action. Preserve unfinished work.
```

The procedure works in either direction. The user opens the next host; the skill does not switch applications automatically.

## What a handoff looks like

Illustrative example, not a test result:

| Before the switch | After continuation |
| --- | --- |
| Named greeting implemented; blank fallback unfinished | Successor inspects the existing function and adds only the missing fallback |
| Named case checked; blank case not run | Named and blank cases checked against the saved source |
| Next: implement blank fallback | Task complete; no new work assumed |

See the [full before/after checkpoint example](docs/checkpoint-example.md). Examples and templates are learning material; the real project's files and criteria determine what is true.

## Compatibility

| Host or component | Available route | Evidence and limits |
| --- | --- | --- |
| Claude Code | Direct skill or included Claude plugin | Maintainer reports successful use. Plugin and marketplace manifests independently validated locally. Exact maintainer-tested version/settings were not recorded. |
| Codex | Direct skill; optional UI metadata included | Maintainer reports successful use. Independent fresh-agent recovery exercised the workflow; separate Codex CLI discovery was not observed in the authoring environment. |
| Other filesystem-capable agents | Explicitly read SKILL.md and project checkpoint | Portable procedure; host discovery and invocation are not verified. |
| Plain chat or uploaded project | Read the provided checkpoint and files | Snapshot only unless live filesystem tools are available. No automatic synchronization. |
| Optional Python helper | Python 3.9+; standard library only | Local checks passed on macOS with Python 3.9. Hosted CI also passed on Linux (Python 3.9/3.13), macOS and Windows (Python 3.13). |
| Concurrent agents editing overlapping files | Outside the sequential core | Requires separate areas/workspaces and an integrator. The checkpoint is not a source lock. |

The maintainer reported that their own testing worked smoothly. This is recorded as maintainer feedback, separately from reproducible automated evidence. It does not establish every host version, operating system, or concurrency scenario. Details: [validation record](docs/validation.md).

## Installation options

Copy the complete `skills/cross-agent-handoff` directory, retaining its name, LICENSE and resources. Do not copy only SKILL.md.

| Host | Project location | User location |
| --- | --- | --- |
| Claude Code | `.claude/skills/cross-agent-handoff/` | `~/.claude/skills/cross-agent-handoff/` |
| Codex | `.agents/skills/cross-agent-handoff/` | `~/.agents/skills/cross-agent-handoff/` |

Use one installation per host. Windows users can copy with their file manager; no symlinks are required. When updating, inspect the destination instead of nesting a new copy inside an existing folder.

### Claude Code plugin

This repository includes a plugin and a local marketplace. Run inside Claude Code:

```text
/plugin marketplace add kristianrolando/cross-agent-handoff
/plugin install cross-agent-handoff@cross-agent-tools
```

Root AGENTS.md and CLAUDE.md guide maintenance of this repository; installing the plugin does not automatically load those files into a consumer project. Initialization adds the reviewed project routing when needed.

For local development, the marketplace command can instead point to this checkout. The documented Codex route is a direct skill; this package does not provide a native Codex plugin wrapper.

## Recovery after interruption

```text
Use cross-agent-handoff to recover after interruption. Inspect the checkpoint,
actual files, relevant diffs and untracked work, available evidence and running
operations. Separate verified progress from unknown history, save reconciled
state, then continue the authorized task.
```

Only persisted facts and artifacts can survive a lost session. Checkpointing is an agent procedure, not an emergency-save daemon. The skill cannot guarantee a save before a usage limit or crash, stop other sessions, or reconstruct unsaved decisions.

## Health, updates and removal

```text
Use cross-agent-handoff to review continuity health without changing files.
Check routing, checkpoint claims versus files, validation inputs,
unfinished work and writer activity.
```

The [optional helper](skills/cross-agent-handoff/references/helper.md) provides draft creation, structural checks, selective file hashes, a previous copy and guarded atomic saves. It never proves that historical test claims are true or that another writer has stopped.

To update, review and replace the installed skill while keeping project records. To remove, delete only the installation and its reviewed routing additions; keep project data and decisions. See [setup and removal](skills/cross-agent-handoff/references/setup.md).

## Automated checks

Run the same dependency-free suite used by CI:

```sh
python3 -m unittest discover -s tests -v
```

On Windows, use `python` if `python3` is unavailable. [GitHub Actions](.github/workflows/ci.yml) runs the suite on pushes, pull requests and manual dispatch. It covers filesystem failure scenarios, metadata, local documentation links, bundled license consistency, and example checkpoint structure. It makes no model calls and needs no vendor credentials.

The [first hosted CI run](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41401002913) passed all four matrix jobs. The badge above reflects current workflow status. See [CI scope and maintenance](docs/ci.md).

## Documentation

- [Architecture and trade-offs](docs/architecture.md)
- [Before/after checkpoint example](docs/checkpoint-example.md)
- [Validation evidence and compatibility limits](docs/validation.md)
- [Directory map](docs/file-map.md)

## License

[MIT](LICENSE). Copyright (c) 2026 Kristian Rolando Limantara.

The standalone skill includes the same license so its notice travels with direct installations. Preserve copyright and license notices when distributing copies or substantial portions. No change to a consumer project's license is required merely to follow this workflow.

## Contributing

Human and AI-assisted contributions use the same shared rules, checkpoint and checks. See [CONTRIBUTING.md](CONTRIBUTING.md) for the Claude Code entrypoint, Codex workflow, PR process and handoff prompts.
