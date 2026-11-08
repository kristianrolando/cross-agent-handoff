# Agent compatibility and activation

Use this guide for installation, missing discovery, or host routing. Keep the same checkpoint
when switching agents. Do not read this matrix on every ordinary resume.

## Install the complete skill

Copy the entire `cross-agent-handoff` folder from the package's `skills` directory, including
LICENSE, references, assets and scripts, into **one** supported location per host. The path
below is a parent directory: append `cross-agent-handoff/SKILL.md` for the entry file.
Inspect existing installations before replacing them. Avoid duplicate versions of the same skill.

Official locations rechecked on 2026-11-02; features remain version/settings dependent.
These are documented loading routes, not claims of live application tests.

| Host | Project skill parent | User skill parent | Activation / discovery check |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | Direct: `/cross-agent-handoff`; bundled plugin: `/cross-agent-handoff:cross-agent-handoff`. Does not read `.agents/skills/`. |
| Codex | `.agents/skills/` (current directory up to repository root) | `~/.agents/skills/` | Ask `Use $cross-agent-handoff to resume this project.` or pick it from `/skills`. |
| Google Antigravity | `.agents/skills/` (legacy `.agent/skills/`) | `~/.gemini/config/skills/` | App and CLI: `/cross-agent-handoff`; CLI `/skills reload` after adding it mid-session; IDE: inspect Customizations, then request the skill by name. |
| Cursor | `.agents/skills/` or `.cursor/skills/`; also reads `.claude/skills/` | `~/.agents/skills/` or `~/.cursor/skills/` | Type `/cross-agent-handoff` in Agent chat. Remote agents need the skill in their actual workspace or supported sync route. |
| Gemini CLI | `.agents/skills/` or `.gemini/skills/` (`.agents` wins) | `~/.agents/skills/` or `~/.gemini/skills/` | Check `/skills list`; request the skill by name and accept the activation consent prompt. `/skills reload` refreshes discovery. |
| GitHub Copilot | `.github/skills/`, `.agents/skills/` or `.claude/skills/` | `~/.copilot/skills/` or `~/.agents/skills/` | No documented slash command; Copilot loads skills when relevant, so name the skill in the request. Locations and availability vary by app, CLI, IDE and cloud surface. |
| OpenCode | `.opencode/skills/`, `.agents/skills/` or `.claude/skills/` | `~/.config/opencode/skills/`, `~/.agents/skills/` or `~/.claude/skills/` | Ask it to load `cross-agent-handoff` with its skill tool; check `permission.skill` if it is hidden or asks for approval. |
| Cline | `.cline/skills/` (recommended), `.clinerules/skills/` or `.claude/skills/` | `~/.cline/skills/` | Skills are enabled when discovered; check its toggle in the Skills tab, then use `/cross-agent-handoff` or request it by name. Does not document `.agents/skills/`. |

No single project folder reaches every host. `.agents/skills/` serves Codex, Antigravity,
Cursor, Gemini CLI, Copilot and OpenCode; `.claude/skills/` serves Claude Code, Cursor, Copilot,
OpenCode and Cline. A team using Claude Code with Codex therefore needs both copies, and hosts
that read both folders then see the skill twice. Keep every copy on the same version and update
them together. All installations must point to the same project checkpoint, not agent-specific state.

The repository includes a Claude Code plugin wrapper only. A direct skill installation does not
create a plugin, marketplace listing or native extension for another host.

## Bundled installer and doctor

With Python 3.9+, the skill can copy itself to every project folder the chosen hosts read.
No Node.js, Git or symlinks are needed. Run it from a checkout or any installed copy:

```sh
python3 SKILL/scripts/install.py --project PROJECT --hosts claude,codex,antigravity --dry-run
python3 SKILL/scripts/install.py --project PROJECT --hosts claude,codex,antigravity
python3 SKILL/scripts/install.py --project PROJECT --doctor
```

It uses the fewest folders: `.agents/skills/` for Codex, Antigravity, Cursor, Gemini CLI,
Copilot and OpenCode, and `.claude/skills/` for Claude Code and Cline. Each copy gets
`VERSION` and `MANIFEST.sha256`. `--doctor` reports edited copies, copies that differ from each
other, copies missing for `--hosts`, hooks pointing at missing scripts, and personal hook files
not ignored by Git. Exit codes: 0 healthy, 1 warnings, 2 problems.

An existing copy that differs is never replaced silently: `--update` lists local edits and
asks for confirmation (`--yes` skips it). Copies from v0.1.x or another installer have no
manifest, so their edits cannot be detected; review them first. `--uninstall` removes only
verified copies of this skill and its own hook entries, never `HANDOFF.md`, `.handoff/` or
other skills. `--with-hooks` also runs the opt-in hook setup in [hooks.md](hooks.md).
`--user` uses the user folders in the table above; it changes nothing in the project.
`--dry-run` works with every mutating action.

## Skills CLI option

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
The Skills CLI and the bundled installer write the same folders, and `install.py --doctor`
also checks copies made by the Skills CLI. The Claude plugin is separate: Claude Code keeps it
in its own plugin cache, which the bundled installer neither reads nor changes. Use one route
per host so Claude Code does not see the plugin and a direct copy at the same time.

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
Respect their actual scopes and host precedence. Two documented defaults matter most:
Claude Code reads `AGENTS.md` only when no `CLAUDE.md` or `CLAUDE.local.md` applies, so an
existing `CLAUDE.md` needs an `@AGENTS.md` import or plain pointer; Gemini CLI loads only
`GEMINI.md` unless `context.fileName` includes `AGENTS.md`, so prefer a pointer in `GEMINI.md`
over changing settings. Keep the portable routing block in one
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

- [Claude Code skills](https://code.claude.com/docs/en/skills) and [AGENTS.md loading](https://code.claude.com/docs/en/memory)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills) (formerly developers.openai.com/codex/skills)
- [Antigravity skills](https://antigravity.google/docs/skills)
- [Cursor skills](https://cursor.com/docs/skills)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) and [context files](https://geminicli.com/docs/cli/gemini-md/)
- [GitHub Copilot skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [OpenCode skills](https://opencode.ai/docs/skills)
- [Cline skills](https://docs.cline.bot/customization/skills)
- [Skills CLI agent destinations](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
