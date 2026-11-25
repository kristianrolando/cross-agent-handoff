# Changelog

Versions follow the Claude plugin manifest and the skill's `VERSION` file. Release notes with
install commands live in [docs/releases/](docs/releases/).

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
