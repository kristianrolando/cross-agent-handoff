# Mechanical snapshots and opt-in hooks

Read this when setting up automatic snapshots, when a resume shows a stale-checkpoint
warning, or when removing hooks. The checkpoint stays the semantic record; snapshots only
record what changed, never why.

## Two layers

| Layer | Written by | Contains | Survives a usage limit? |
| --- | --- | --- | --- |
| Checkpoint (`HANDOFF.md`) | The agent | Goal, verified state, decisions, evidence, next action | Only what was saved before the limit |
| Snapshot (`.handoff/auto/latest.json`) | `scripts/snapshot.py`, by hand or from a hook | Time, hook event and error, Git status and diff summary, recently modified files, media size and time | Yes when a hook ran at or after the last turn |

`scripts/inject.py` prints compact resume context: checkpoint status, Task, Next, the last
snapshot, and a warning when files or commits are newer than the checkpoint. That check runs
when inject runs, so it detects an abrupt stop on every host, with or without hooks:

```sh
python3 SKILL/scripts/inject.py --project PROJECT
python3 SKILL/scripts/snapshot.py --project PROJECT
```

A warning means the predecessor probably stopped before saving. Recover from the actual files
with [recovery.md](recovery.md); do not trust the checkpoint alone. Tracked files identical to
Git HEAD are not reported, so a fresh clone or checkout does not trigger it.

The scripts need Python 3.9+ and only the standard library. They run only in a project that
already has the checkpoint or a `.handoff/` folder, never raise inside a hook, and always exit
0. `.handoff/auto/` ignores itself in Git. Media files get size and time only; add
`--partial-hash` to hash the first and last 1 MB. The scan stops after 1.5 seconds or 50,000
entries and says so. Optional `.handoff/config.json` keys: `snapshot.window_minutes` (120),
`snapshot.exclude` (folder paths), `snapshot.partial_hash`, `snapshot.history_max_lines`
(500), `guard.files` (5), `guard.minutes` (30), `inject.max_lines` (150).

## Install hooks only on request

Hooks run commands automatically, so install them only when the user asks. Review the
printed change first; `--dry-run` writes nothing, and other entries are preserved:

```sh
python3 SKILL/scripts/hooks.py install --project PROJECT --host claude --dry-run
python3 SKILL/scripts/hooks.py install --project PROJECT --host claude --host codex
python3 SKILL/scripts/hooks.py status --project PROJECT --host codex
python3 SKILL/scripts/hooks.py remove --project PROJECT --host claude
```

The skill copy for that host must exist in the project (`.claude/skills/` for Claude,
`.agents/skills/` for Codex and Antigravity), or pass `--skill-dir`. `--python` sets the
interpreter command (default `python3`, or `python` on Windows). The bundled Claude plugin
ships no hooks: plugin hooks start as soon as the plugin is enabled, which would not be opt-in.

## Host support (official documentation checked 2026-11-08)

| Host | Config written | Events used | Status |
| --- | --- | --- | --- |
| Claude Code | `.claude/settings.local.json` (`--shared`: `.claude/settings.json`) | `SessionStart` → inject; `Stop`, `StopFailure`, `PreCompact` → snapshot | Events and formats documented. `Stop` does not run on API errors; `StopFailure` does, including `rate_limit`. Hook execution on Windows not verified here. |
| Codex | `.codex/hooks.json`, with `commandWindows` | `SessionStart` → inject; `Stop`, `PreCompact` → snapshot | Documented. Hooks run only after review and trust in `/hooks`, and project hooks need a trusted project. No usage-limit event is documented. |
| Antigravity App, IDE, CLI | `.agents/hooks.json`, entry `cross-agent-handoff` | `SessionStart` → inject (`injectSteps`); `Stop` → snapshot | Events and file documented. Whether `ephemeralMessage` context is visible to the model, and trust or Windows behavior, are unverified. |
| Cursor, Gemini CLI, Copilot, OpenCode, Cline | none | none | Not verified in this release; use inject by hand at session start. |

Codex and Antigravity commands contain absolute paths because neither documents a
project-root variable; rerun `install` after moving the project. Without a usage-limit event,
the last snapshot is from the end of the last completed turn. Edits made during an
interrupted turn still appear in the live inject scan.

Live evidence so far: one Claude Code 2.1.318 print-mode session ran the `SessionStart` and
`Stop` hooks in a disposable project, and the model quoted the injected context. `StopFailure`,
`PreCompact`, the guard, Codex and Antigravity hooks have not run in a live host session.

## Optional staleness guard

`install --guard` adds `--guard` to the Stop snapshot. When at least `guard.files` files
changed after the checkpoint, or any changed and the checkpoint is older than
`guard.minutes`, the hook asks the agent once to update the checkpoint (`decision: block` on
Claude and Codex, `continue` on Antigravity). Loop protection: it never asks while the host
reports `stop_hook_active`, and it asks at most once per checkpoint version, recorded in
`.handoff/auto/guard.json`. Claude also caps consecutive Stop continuations at eight.

## Remove

`hooks.py remove` deletes only entries whose command runs this skill's `snapshot.py` or
`inject.py` (on Antigravity, the `cross-agent-handoff` entry). It never deletes
`HANDOFF.md`, `.handoff/` records or other hooks. Delete `.handoff/auto/` by hand if the
snapshots are no longer wanted.
