# Changelog

Versions follow the Claude plugin manifest and the skill's `VERSION` file. Release notes with
install commands live in [docs/releases/](docs/releases/).

## 0.2.0 (unreleased)

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

Compatibility: checkpoint format stays `cross-agent-handoff/1`. See the migration notes in
[docs/releases/v0.2.0.md](docs/releases/v0.2.0.md).

## 0.1.1 (2026-11-02)

Host guide for Antigravity, Cursor, Gemini CLI, GitHub Copilot, OpenCode and Cline; helper
placeholder and lock-message fixes; CI and release workflow fixes; live Codex → Antigravity →
Codex trial. [Notes](docs/releases/v0.1.1.md).

## 0.1.0

Initial MIT release: portable skill, checkpoint template, optional helper, Claude Code plugin.
[Notes](docs/releases/v0.1.0.md).
