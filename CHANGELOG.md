# Changelog

Versions follow the Claude plugin manifest and the skill's `VERSION` file. Release notes with
install commands live in [docs/releases/](docs/releases/).

## 0.3.0 (2026-11-26)

Compaction and the clock, measured in a live trial, plus tools that say where a checkpoint is
long. The checkpoint format `cross-agent-handoff/1` is unchanged and nothing needs enabling.

Changed (guidance):
- The routing block grows by 27 words (155 counted with its marker lines, from 128): "Run
  `date -Iseconds` and paste the result into updated_at; never estimate it" and "If HANDOFF.md is
  over 1,200 words, compact it in the same save: one line per finished item; keep open items,
  decisions and failed attempts." In a synthetic trial (Claude Code headless, one model, 26 runs of the
  previous and new block side by side, see
  [the record](docs/evidence/live-trial-2026-11-26-routing-block-v2.md)), checkpoints stayed
  within 1,300 words in 13 of 13 runs with the new block against 6 of 13 with the v0.2.3 block, and
  `updated_at` came from the real clock in 13 of 13 against 7 of 13. Planted facts survived
  compaction in 35 of 36 runs. Existing blocks keep working; replace the block after reviewing
  local edits. The package test now allows a block under 160 words.
- `SKILL.md`: before a large compaction, copy the checkpoint to a uniquely named file, then confirm
  every open item, decision, risk and failed attempt still appears or is marked resolved.
- Video profile: `Outputs` keeps only the latest output per deliverable and a `Render log` line
  points to the project's own history, so renders stop growing the checkpoint.
- `references/agents.md`: host memory must not be the only owner of a decision or status.

Added:
- `check`, `save` and the resume context say where a checkpoint is long: prose before the first
  section (over 100 words), sections outside the template (over 200 words), Recent outcomes with
  more than 8 entries, a Next section over 150 words, and the three largest sections once over
  the 1,200-word target. They are advisory and never reject a save.
- `install.py --doctor` recognises the Claude plugin route (read-only: `enabledPlugins` and the
  plugin version) instead of reporting "No installed copy found", and warns when the plugin and a
  `.claude/skills` copy would both load.

Compatibility: format unchanged; helpers v0.1.1 to v0.2.3 read the same checkpoints. Not done in
this release: one shared Git module for the scripts, rolling history, hooks for other hosts.

## 0.2.3 (2026-11-26)

Small fixes deferred from v0.2.2 (audit findings F08, F13 rest, F23). The checkpoint format and
the routing block are unchanged.

Fixed:
- Hook commands for Claude Code now use `${CLAUDE_PROJECT_DIR}`, the form Claude Code rewrites
  when hooks run in PowerShell; the bare `$CLAUDE_PROJECT_DIR` written before resolved to nothing
  there (not tested on Windows). `hooks.py install` refuses a project or skill path containing
  `$` or a backtick, because a shell would expand it inside the quoted command, and
  `hooks.py status` reports an entry written for such a path by an earlier version. Entries
  with the bare form are recognised and upgraded by the next `hooks.py install`.
- `install.py --doctor`, `--update` and plain installs report an unreadable `MANIFEST.sha256`
  (bad line, binary content) instead of ending in a traceback; `--update` rewrites it.
- `handoff.py save` prints the same advisory warnings as `check` (reading budget, future
  `updated_at`, observed files) in its JSON result and on stderr. The save and exit code 0 are
  unchanged.

Changed (guidance):
- `SKILL.md` asks for an edit tool that fails when the old text is missing and a reread after a
  full-file rewrite, because a silent no-op leaves a stale line and a rewrite can overwrite
  another writer's edit.

Compatibility: format `cross-agent-handoff/1` unchanged. Hook entries installed by v0.2.2 keep
working; reinstalling hooks upgrades them.

## 0.2.2 (2026-11-26)

Fixes from an audit of the skill against its use in four real projects
([evidence](docs/evidence/audit-2026-11-26.md)). The checkpoint format is unchanged.

Changed (guidance):
- The routing block grows by about 34 words: keep the checkpoint near 1,200 words, reconcile open
  items with files, Git and owner answers, save owner questions and answers before the final
  message, take `updated_at` from `date -Iseconds`, check for other writers before marking
  ready, and never rerun a recorded command just to test state. It was the only text those
  projects' agents loaded each session, and none ran the helper. Existing blocks keep working.
  The sentence listing the checkpoint sections was dropped from the block to pay for the
  additions; `SKILL.md` still lists them.
- `updated_at` errors now name `date -Iseconds` and say offsets need the colon (`+0700` was
  written in a real project and rejected).
- README no longer says two agents "never write at once": the lock is advisory.

Fixed:
- `inject.py` printed no running operation when the label was a list item, bold, or had its
  details on following lines; it now prints those lines and cuts each printed line at 300
  characters, so one unwrapped paragraph cannot flood a session start.
- Hook scripts (`snapshot.py`, `inject.py`) exit 0 on invalid arguments. A hook command from
  another skill version made argparse exit 2, which blocks `Stop` and `PreCompact` in Claude Code.
- `install.py --uninstall` removes hooks written with `hooks.py install --shared`, and `--doctor`
  reports shared hooks that point at missing scripts.
- `snapshot.py` no longer hides modified files when a Git call times out (large media
  repositories), and records `status_error` instead of an empty status.
- Hook Git calls set `GIT_OPTIONAL_LOCKS=0` and `diff.autoRefreshIndex=false`, so a background
  snapshot no longer takes `.git/index.lock` and fails a concurrent `git add` or `commit`.
- `inject.py` writes its output as UTF-8 bytes, because Python before 3.15 can fail to encode
  checkpoint text for an ANSI-code-page pipe. Tested by simulating the code page, which passed on
  the hosted Windows jobs; not observed in a real Windows host session.

Compatibility: format `cross-agent-handoff/1` unchanged. The new routing text is not shown to
change agent behavior: the audit read one reader per variant and no live trial has run.

## 0.2.1 (2026-11-10)

Changed (token budget; checkpoint format unchanged):
- Inject resume context warns when the checkpoint exceeds the 1,200-word reading target,
  so the next agent compacts it instead of only `handoff.py check` reporting it.
- SKILL.md: between-step saves update only changed sections; the full compaction and reread
  stay at handoff. The save step states the word target and how to compact resolved work.
- `references/setup.md`: shorter routing block that skips small or read-only tasks. Projects
  keep their existing block; replace it only after reviewing local edits.

## 0.2.0 (2026-11-08)

Built for rotating agents and accounts on one project, including media work. Everything new
is opt-in; updating the skill alone keeps v0.1.1 behavior apart from guidance text.

Added:
- Mechanical snapshots (`scripts/snapshot.py`) and resume context (`scripts/inject.py`).
  Inject warns when files or commits are newer than the checkpoint, on any host.
- Opt-in hooks (`scripts/hooks.py`) for Claude Code (including `StopFailure` on rate limits),
  Codex and Antigravity, plus an optional staleness guard with loop protection.
- Multi-host installer and doctor (`scripts/install.py`), with `VERSION` and `MANIFEST.sha256`
  per copy, drift and edit detection, safe update and uninstall.
- Advisory lock and switch log (`scripts/lock.py`). Takeover needs user confirmation.
- Game, video and motion profiles (`assets/profiles/`, `handoff.py init --profile`).
- Optional checkpoint metadata: `updated_at`, `language`, `profile`.
- References: `hooks.md`, `lock.md`, `profiles.md`. Live-trial kit in `docs/evidence/`.

Changed:
- Guidance: checkpoint after every completed step; record command, output path and start
  time before long operations.
- CI runs Ubuntu, macOS and Windows on Python 3.9 and 3.14 (six jobs).
- The template records `updated_at` and running operations in more detail.

Fixed after the 2026-11-08 live trial: Antigravity snapshots record the Stop event name, the
skill asks agents to read `updated_at` from the clock, and malformed file observations get an
actionable warning.

Compatibility: checkpoint format stays `cross-agent-handoff/1`. See the migration notes in
[docs/releases/v0.2.0.md](docs/releases/v0.2.0.md).

## 0.1.1 (2026-11-02)

Host guide for Antigravity, Cursor, Gemini CLI, GitHub Copilot, OpenCode and Cline; helper
placeholder and lock-message fixes; CI and release workflow fixes; live Codex → Antigravity →
Codex trial. [Notes](docs/releases/v0.1.1.md).

## 0.1.0

Initial MIT release: portable skill, checkpoint template, optional helper, Claude Code plugin.
[Notes](docs/releases/v0.1.0.md).
