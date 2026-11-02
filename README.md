# Cross-Agent Handoff

Continue a project in Claude Code, Codex, or a new session without relying on the previous conversation. Keep the goal, verified progress, unfinished work, decisions and next step in the project itself.

**One compact checkpoint. No cross-vendor API calls. No additional cloud service.**

Use it when a usage limit interrupts work, when you switch agents, or when you return to a project later. The core needs ordinary filesystem access; Python and Git are optional.

## Quick start

### 1. Install the skill

Download or clone this repository. Ask your coding agent to install it with this prompt, replacing the source directory with your actual checkout:

```text
Install cross-agent-handoff from <checkout>/skills/cross-agent-handoff
into this project's supported skill directory for this host.
Copy the complete folder, including LICENSE and supporting resources.
Inspect an existing installation before changing it; do not overwrite it blindly.
Do not change application code or global settings.
```

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
| Optional Python helper | Python 3.9+; standard library only | Local checks passed on macOS with Python 3.9. CI is configured for Linux, macOS and Windows; hosted results are pending. |
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

This repository includes a plugin and a local marketplace. Run inside Claude Code, replacing the directory with this checkout:

```text
/plugin marketplace add /absolute/path/to/this-checkout
/plugin install cross-agent-handoff@cross-agent-tools
```

Root AGENTS.md and CLAUDE.md guide maintenance of this repository; installing the plugin does not automatically load those files into a consumer project. Initialization adds the reviewed project routing when needed.

When this repository is publicly hosted, its real Git URL can replace the local path. The documented Codex route is a direct skill; this package does not provide a native Codex plugin wrapper. Public-hosting commands are not fabricated before a release URL exists.

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

The workflow is configured here; a hosted CI pass can only be reported after an actual GitHub run. See [CI scope and maintenance](docs/ci.md).

## Documentation

- [Architecture and trade-offs](docs/architecture.md)
- [Before/after checkpoint example](docs/checkpoint-example.md)
- [Validation evidence and compatibility limits](docs/validation.md)
- [Directory map](docs/file-map.md)

## License

[MIT](LICENSE). Copyright (c) 2026 Kristian Rolando Limantara.

The standalone skill includes the same license so its notice travels with direct installations. Preserve copyright and license notices when distributing copies or substantial portions. No change to a consumer project's license is required merely to follow this workflow.
