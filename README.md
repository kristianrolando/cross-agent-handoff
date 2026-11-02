# Cross-Agent Handoff

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/readme-hero-mobile.svg">
  <img src="docs/assets/readme-hero.svg" alt="Switch agents. Keep the work. Claude Code and Codex share context through the project checkpoint, one writer at a time.">
</picture>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#compatibility">Compatibility</a> ·
  <a href="#documentation">Documentation</a>
</p>

[![Package checks](https://github.com/kristianrolando/cross-agent-handoff/actions/workflows/ci.yml/badge.svg)](https://github.com/kristianrolando/cross-agent-handoff/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-315b43?style=flat-square)](LICENSE)
[![v0.1.0](https://img.shields.io/badge/Release-v0.1.0-a15d3e?style=flat-square)](https://github.com/kristianrolando/cross-agent-handoff/releases/tag/v0.1.0)

**Hit a usage limit? Switching agents? Returning in a new session?** Save the useful context in your project, then let the next agent inspect the files and continue.

One compact checkpoint preserves the goal, verified progress, unfinished work, decisions, evidence and next action. No cross-vendor API calls, extra cloud service or shared chat history are required.

## Quick start

### Install your preferred route

**Claude Code plugin** · run inside Claude Code:

```text
/plugin marketplace add kristianrolando/cross-agent-handoff
/plugin install cross-agent-handoff@cross-agent-tools
```

**Direct skill for Codex or Claude Code** · run in your project:

```sh
npx skills add kristianrolando/cross-agent-handoff --skill cross-agent-handoff
```

Choose your host in the installer. This installer requires Node.js 22.20+; the core workflow does not need Node.js. For manual copying and user-wide paths, see [installation options](#installation-options). Use one installation route per host.

### Initialize once

| Your installation | Prompt |
| --- | --- |
| Claude Code plugin | `/cross-agent-handoff:cross-agent-handoff Initialize continuity in this project.` |
| Claude Code direct skill | `/cross-agent-handoff Initialize continuity in this project.` |
| Codex | `Use $cross-agent-handoff to initialize continuity in this project.` |

The agent inspects existing instructions and documentation, reuses a suitable checkpoint or creates `HANDOFF.md`, and adds short project routing where needed. For a new project, include your goal and acceptance criteria. Initialization does not scaffold an application or choose a stack.

## How it works

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/handoff-flow-mobile.svg">
  <img src="docs/assets/handoff-flow.svg" alt="Three steps: work in one agent; save scope, state, evidence and the next action to the project; stop overlapping writers, then resume in the next agent after inspecting actual files.">
</picture>

**Before switching**, ask the outgoing agent:

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

Works in either direction. You open the next host; the skill does not switch applications automatically.

## What survives the switch

<picture>
  <source media="(max-width: 600px)" srcset="docs/assets/checkpoint-map-mobile.svg">
  <img src="docs/assets/checkpoint-map.svg" alt="Checkpoint map: project and task explain the goal; state separates verified and unfinished work; evidence identifies checks and inputs; next provides an actionable step. An illustrative greeting example shows unfinished blank-name handling.">
</picture>

| Saved context | Why it matters |
| --- | --- |
| Goal, scope and acceptance criteria | Keep the task focused |
| Verified work and unfinished changes | Reuse progress without assuming completion |
| Decisions, failed attempts and blockers | Avoid rediscovering important findings |
| Checks, input identity and coverage limits | Know which evidence still applies |
| Writers, running operations and next action | Continue without overlapping edits |

The checkpoint links to existing requirements, architecture and backlog instead of becoming a second specification. See the [complete before/after example](docs/checkpoint-example.md) and [default template](skills/cross-agent-handoff/assets/checkpoint.md). The diagram is illustrative, not test evidence.

## Compatibility

| Host / component | Available route | Evidence and limits |
| --- | --- | --- |
| **Claude Code** | Direct skill or included plugin | Maintainer reports successful use; manifests locally validated; installer copied full skill resources. Exact maintainer-tested version/settings were not recorded. |
| **Codex** | Direct skill with optional UI metadata | Maintainer reports successful use; installer and independent fresh-agent recovery checked. Separate Codex CLI model discovery was not observed in the authoring environment. |
| Other filesystem-capable agents | Explicitly read `SKILL.md` and the checkpoint | Portable procedure; host-specific discovery/invocation unverified. |
| Plain chat / uploads | Read supplied checkpoint and files | Snapshot only unless live filesystem tools are available. |
| Optional Python helper | Python 3.9+, standard library | Hosted checks passed on Linux, macOS and Windows. |
| Concurrent overlapping writers | Requires separate coordination | The sequential checkpoint does not lock source files. |

Public CLI discovery and copy installation were checked in a disposable project for both host directories, including resources and MIT notices. Maintainer-reported app behavior is recorded separately from automated evidence. See [validation and coverage](docs/validation.md).

## What to expect

- **Project files carry context.** Applicable instructions and the inspected filesystem remain authoritative; the checkpoint guides the next inspection.
- **One writer at a time.** Stop overlapping source and output writers before handing over. Use separate areas/workspaces and an integrator for simultaneous work.
- **Save after meaningful progress.** There is no emergency-save daemon; unsaved facts can be lost during a crash or usage limit.
- **Check the actual environment.** The core needs filesystem access. Git and Python are optional; the helper requires Python 3.9+.
- **Keep records with the work.** Moving devices requires transferring relevant dirty/untracked files and verifying the snapshot. No automatic cross-device synchronization is provided.

## Installation options

<details>
<summary><strong>Manual installation, locations and plugin loading</strong></summary>

Copy the complete `skills/cross-agent-handoff` directory, including LICENSE and supporting resources, to one supported location for each host.

| Host | Project location | User location |
| --- | --- | --- |
| Claude Code | `.claude/skills/cross-agent-handoff/` | `~/.claude/skills/cross-agent-handoff/` |
| Codex | `.agents/skills/cross-agent-handoff/` | `~/.agents/skills/cross-agent-handoff/` |

Windows users can use their file manager; symlinks are not required. Inspect an existing installation before updating it rather than nesting a new copy inside its directory.

For local Claude plugin development, the marketplace command can point to this checkout. Root `AGENTS.md` and `CLAUDE.md` guide repository maintenance; installing the plugin does not automatically load those files into consumer projects. Initialization adds reviewed project routing when needed.

The documented Codex route is a direct skill. This package does not provide a native Codex plugin wrapper.

</details>

<details>
<summary><strong>Recovery, health checks, updates and removal</strong></summary>

After an interruption:

```text
Use cross-agent-handoff to recover after interruption. Inspect the checkpoint,
actual files, relevant diffs and untracked work, available evidence and running
operations. Separate verified progress from unknown history, save reconciled
state, then continue the authorized task.
```

For a read-only health review:

```text
Use cross-agent-handoff to review continuity health without changing files.
Check routing, checkpoint claims versus files, validation inputs,
unfinished work and writer activity.
```

The [optional helper](skills/cross-agent-handoff/references/helper.md) provides draft creation, structural checks, selective file hashes, a previous copy and guarded atomic saves. It cannot prove historical test claims or writer inactivity.

To update, review and replace the installed skill while retaining project records. To remove, delete only the installation and reviewed routing additions; keep project data and decisions. See [setup and removal](skills/cross-agent-handoff/references/setup.md).

</details>

## Documentation

| Start here | Go deeper |
| --- | --- |
| [Checkpoint example](docs/checkpoint-example.md) | [Architecture and trade-offs](docs/architecture.md) |
| [Contributing with Claude or Codex](CONTRIBUTING.md) | [Validation evidence and limits](docs/validation.md) |
| [Setup and migration](skills/cross-agent-handoff/references/setup.md) | [File map](docs/file-map.md) |

## Checks and contributions

```sh
python3 -m unittest discover -s tests -v
```

Use `python` on systems where `python3` is unavailable. The [CI workflow](.github/workflows/ci.yml) checks pushes and pull requests without model calls or vendor credentials. The badge shows current status; [recorded evidence](docs/validation.md) separates automated checks, illustrative examples and live-use reports.

Human and AI-assisted contributions use the same instructions, checkpoint and review process. Start with [CONTRIBUTING.md](CONTRIBUTING.md). Visual assets in `docs/assets/` are editable SVG files with wide and narrow layouts, descriptive alternative text, no external fonts and no embedded scripts.

## License

[MIT](LICENSE) · Copyright (c) 2026 Kristian Rolando Limantara.

The standalone skill bundles the same license. Preserve its notices when distributing copies or substantial portions. Following this workflow does not itself require changing a consumer project's license.
