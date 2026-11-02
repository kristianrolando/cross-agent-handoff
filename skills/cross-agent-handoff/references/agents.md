# Agent compatibility and activation

Use this guide for installation, missing discovery, or host routing. Keep the same checkpoint
when switching agents. Do not read this matrix on every ordinary resume.

## Install the complete skill

Copy the entire `cross-agent-handoff` folder from the package's `skills` directory, including
LICENSE, references, assets and scripts, into **one** supported location per host. The path
below is a parent directory: append `cross-agent-handoff/SKILL.md` for the entry file.
Inspect existing installations before replacing them. Avoid duplicate versions of the same skill.

Official locations checked on 2026-11-02; features remain version/settings dependent.
These are documented loading routes, not claims of live application tests.

| Host | Project skill parent | User skill parent | Activation / discovery check |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | Direct: `/cross-agent-handoff`; bundled plugin: `/cross-agent-handoff:cross-agent-handoff`. |
| Codex | `.agents/skills/` | `~/.agents/skills/` | Ask `Use $cross-agent-handoff to resume this project.` |
| Google Antigravity | `.agents/skills/` | `~/.gemini/config/skills/` | App: `/cross-agent-handoff`; IDE: inspect Customizations. Otherwise request the skill by name. Legacy `.agent/skills/` is also documented. |
| Cursor | `.agents/skills/` or `.cursor/skills/` | `~/.cursor/skills/` | Type `/cross-agent-handoff` in Agent chat. Remote agents need the skill in their actual workspace or supported sync route. |
| Gemini CLI | `.agents/skills/` or `.gemini/skills/` | `~/.gemini/skills/` | Check `/skills list`; request the skill by name and accept required activation consent. `/skills reload` refreshes discovery. |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` | Request the skill by name in a supported agent surface. Locations and feature availability depend on IDE/CLI/cloud surface. |
| OpenCode | `.opencode/skills/` or `.agents/skills/` | `~/.config/opencode/skills/` | Ask it to load `cross-agent-handoff` using its skill tool; check skill permissions if missing. |
| Cline | `.cline/skills/` | `~/.cline/skills/` | Enable the skill in Skills, then use `/cross-agent-handoff` or request it by name. |

For project use, one `.agents/skills/cross-agent-handoff` copy can serve the documented
shared-directory hosts. Add host-specific copies only where required, and update those copies
together. All installations must point to the same project checkpoint, not agent-specific state.

The repository includes a Claude Code plugin wrapper only. A direct skill installation does not
create a plugin, marketplace listing or native extension for another host.

## Installer option

From the consumer project, use the public Skills CLI and select the target host:

```sh
npx skills add kristianrolando/cross-agent-handoff --skill cross-agent-handoff
```

For an explicit project-local Antigravity install:

```sh
npx skills add kristianrolando/cross-agent-handoff --skill cross-agent-handoff --agent antigravity --copy
```

The installer currently requires Node.js 22.20+. The portable procedure and manual copy need
no Node.js. Review its displayed destinations. Installer defaults can differ from host docs:
for example, the checked installer lists legacy Antigravity global paths and a shared Cline
project path. Use the documented manual paths above if the installed host does not discover
that destination. Do not assume `--global` works identically across products or versions.
Do not install into every host or change global settings merely to enable handoff.

## Activate and route project context

Use the host's supported skill selector or request the skill by name. If discovery fails,
explicitly read the installed entry file instead of inventing a slash command:

```text
Read .agents/skills/cross-agent-handoff/SKILL.md and follow it to resume this
project. Read applicable project instructions and the canonical checkpoint,
inspect actual files and changes, preserve unfinished work, and continue
only the authorized task. Do not assume historical test claims are verified.
```

Replace the first path with the actual installed location. With this repository open for
maintenance, the entry is `skills/cross-agent-handoff/SKILL.md`.
This explicit-file route also works for Windsurf and other coding agents with read/write
filesystem access; this package makes no independently verified native-discovery claim for them.
Without write access, inspect and report limitations instead of claiming to save a checkpoint.

During initialization, inspect the active host's existing instructions, including relevant
`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, IDE rules, or Copilot/Cline instruction files.
Respect their actual scopes and host precedence. Keep the portable routing block in one
canonical place, normally `AGENTS.md`. If the host does not load it, add a small instruction
to the existing supported entrypoint: `Read AGENTS.md and HANDOFF.md before substantial work.`
Use actual paths and plain instructions; `@AGENTS.md` imports are not universal syntax.
Do not generate a full collection of vendor configuration files, duplicate permanent rules,
or place volatile progress inside host rules. Verify actual loading by checking the agent's
first assessment against the saved task and real files. Discovery alone proves neither.

When switching, save, stop overlapping writers and open the same complete project in the next
host. If a cloud agent has a separate checkout, explicitly transfer required dirty/untracked
files and checkpoint, reconcile branches, then verify the snapshot. No automatic sync is provided.

## Official sources

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Codex skills](https://developers.openai.com/codex/skills/)
- [Antigravity skills](https://antigravity.google/docs/skills)
- [Cursor skills](https://cursor.com/docs/skills)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)
- [GitHub Copilot skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [OpenCode skills](https://opencode.ai/docs/skills)
- [Cline skills](https://docs.cline.bot/customization/skills)
- [Skills CLI agent destinations](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
