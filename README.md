# Cross-Agent Handoff

A portable Agent Skill for continuing the same project across Claude Code, Codex, and other filesystem-capable agents. It keeps one compact project checkpoint and uses existing requirements, decisions, logs, and source as their own information owners. No vendor API or additional subscription is required.

This checkout is the standalone Cross-Agent Handoff project. Its skill and plugin packaging are maintained here.

## Install as a skill

Copy the complete `skills/cross-agent-handoff` directory to ONE supported location for each host, retaining its name and resources. Do not copy only SKILL.md.

| Host | Project installation | User installation |
| --- | --- | --- |
| Claude Code | `.claude/skills/cross-agent-handoff/` | `~/.claude/skills/cross-agent-handoff/` |
| Codex | `.agents/skills/cross-agent-handoff/` | `~/.agents/skills/cross-agent-handoff/` |

Avoid duplicate installations of the same name in a host. Use an absolute source directory when copying from elsewhere; the installed skill has no dependency on its original checkout. Windows users can copy folders using their file manager. No symlinks are required.

Project installation example, run at the target project's root after replacing SOURCE with this checkout:

```sh
mkdir -p .claude/skills .agents/skills
cp -R SOURCE/skills/cross-agent-handoff .claude/skills/cross-agent-handoff
cp -R SOURCE/skills/cross-agent-handoff .agents/skills/cross-agent-handoff
```

Run only when those destination skill folders do not already exist; review updates rather than nesting a copy inside an existing folder. This installs the same skill for two independent hosts, not two copies inside one host's search path.

### Optional Claude Code plugin

This standalone package includes its own `.claude-plugin/plugin.json` and marketplace. In Claude Code, add this checkout as a local marketplace, then install:

```text
/plugin marketplace add /absolute/path/to/this-checkout
/plugin install cross-agent-handoff@cross-agent-tools
```

After hosting this repository, the first command can instead reference its real Git URL. No public repository has been created by this package. Codex's documented direct-skill path above is the supported route here; no native Codex plugin manifest is claimed.

## Activate on an existing project

Claude Code:

```text
/cross-agent-handoff Initialize continuity in this project. Reuse existing documentation and preserve project instructions. Do not change application code.
```

When installed as the plugin, use `/cross-agent-handoff:cross-agent-handoff` instead of `/cross-agent-handoff`.

Codex:

```text
Use $cross-agent-handoff to initialize continuity in this project. Reuse existing documentation and preserve project instructions. Do not change application code.
```

The agent inspects first, chooses one checkpoint (HANDOFF.md only if needed), fills it from evidence, and adds small routing instructions. For a new project use the same prompt with your goal and acceptance criteria; the skill does not choose a stack or scaffold software on its own.

## Switch either direction

Outgoing agent:

```text
Use cross-agent-handoff to prepare a handoff. Save actual progress, unresolved work, evidence and limits, relevant writers, and the next action. Start no new implementation.
```

Wait for the save and stop the outgoing writer and relevant background operations. Open the SAME actual project in the other agent:

```text
Use cross-agent-handoff to resume this project from its checkpoint. Verify files, changes, criteria and writer activity before continuing. Preserve unfinished work.
```

This works in either direction. The agent must read the checkpoint even when a skill was discovered automatically. For persistent behavior, retain the short routing block documented in the skill's setup reference. Skill selection is not an enforced lifecycle hook.

## After a crash or usage limit

Stop any remaining writer, then ask the successor:

```text
Use cross-agent-handoff to recover this project after interruption. Treat saved status as a lead. Inspect actual files, relevant diffs and untracked work, available evidence and running operations. Separate verified progress from unknown history, save reconciled state, then continue the authorized task.
```

Only saved facts and artifacts can survive. A usage limit can prevent the last checkpoint. No automatic emergency save or guaranteed lossless recovery is provided.

## Status, update, and removal

```text
Use cross-agent-handoff to review continuity health without changing files. Check canonical routing, checkpoint claims versus actual files, validation inputs, unfinished work and writer activity.
```

For mechanical checks and optional atomic saves, see [helper instructions](skills/cross-agent-handoff/references/helper.md). A check passing does not prove project correctness. To update, replace the installed skill after review while retaining project records. To remove, delete only the installation and its reviewed routing additions; keep project data and decisions. Details: [setup and removal](skills/cross-agent-handoff/references/setup.md).

## What is automatic

| Mechanism | Actual behavior |
| --- | --- |
| Skill discovery | Host-dependent selection; explicit invocation is more dependable |
| Checkpointing | Agent follows instructions; no timer, daemon or crash hook |
| Optional helper | Draft creation, structural/hash checks, guarded atomic checkpoint replacement |
| Agent switching | User opens the other host and resumes the same filesystem |
| Concurrent writes | Not supported by the sequential core; separate areas/workspaces and integration are required |
| File transfer | User/environment responsibility when changing devices or snapshots |

See [architecture and reference critique](docs/architecture.md), [validation results](docs/validation.md), and [file map](docs/file-map.md). Runtime files and prompts are English. The core works without Git or Python; the optional helper requires Python 3.9+ and uses no third-party modules.
