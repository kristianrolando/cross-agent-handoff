# Live trial record: v0.2.0 headless agents (2026-11-08)

Real agent sessions run from the command line by the Claude Code session that built v0.2.0, in
disposable projects on one machine. Each session saw only the project files and its prompt.
This record follows [live-trial-template.md](live-trial-template.md). It covers the kit's
headless parts; App/IDE surfaces, a second Claude account and Windows were not covered.

## Environment

| Item | Value |
| --- | --- |
| OS and version | macOS 27.0.1 |
| Python / Node.js / Git / FFmpeg | 3.9.6 / 26.11.1 / 2.54.0 / 9.0.2 |
| Skill version and install route | 0.2.0 from `main` at c5f977b, `install.py --hosts claude,codex,antigravity --with-hooks --yes` |
| Hooks installed | Claude Code (`settings.local.json`), Codex (`.codex/hooks.json`, never trusted), Antigravity (`.agents/hooks.json`); no guard |
| Agents | Claude Code 2.1.318 (`claude -p`, one signed-in account, default model, `acceptEdits` plus allowed `python3`, `node`, `git status/diff/log`, `ls`; video added `nohup`, `ffmpeg`, `ffprobe`); Codex CLI 0.167.0-alpha.3.2 (`codex exec -s workspace-write`, default model); Antigravity CLI 1.4.12 (`agy -p --mode accept-edits`, default model) |

Account aliases are labels. `claude-A` and `claude-B` were the same signed-in Claude account,
so a real second-account switch was not exercised.

## Trial 1-3: GAME-1 chain (game profile)

Task: `move(x, dx)` with A (`move(0,1)` is 1), B (clamp 0-10), C (`node --test` covers A and B).

| Step | Agent / alias | Observed | Assessment |
| --- | --- | --- | --- |
| 1 | Claude Code / claude-A | SessionStart hook ran. Acquired the lock, initialized HANDOFF.md with a filled game section and an AGENTS.md routing block, saved an opening checkpoint, implemented only A, checked it with node, saved through the helper, released the lock. | Pass. `updated_at` was written as 09:08 for a save made about 09:04 (guessed, not read from the clock). |
| 2 | Codex / codex-main | Read SKILL.md, lock.md, checkpoint and diffs; logged switch `claude/claude-A → codex/codex-main`, reason `limit`; implemented only B; 9 direct assertions; recorded C as `not_run`; noted the predecessor's future timestamp and reconciled from files; released the lock. Codex hooks did not run (not trusted). | Pass. |
| 3a | Antigravity CLI | `--mode auto` is unavailable for this account; the first shell command was auto-denied and the session ended after one step. | Blocked by host permissions, as in v0.1.1. `--dangerously-skip-permissions` and global allow-rules were not used. |
| 3b | Antigravity CLI | Rerun told to use file tools only. Skill expanded; wrote a correct `game.test.js`; recorded tests and lock as `not_run`. Wrote two `observed_file` lines as prose, which the helper flagged. The Antigravity `Stop` hook wrote a snapshot (host `antigravity`, `terminationReason: NO_TOOL_CALL`, no event name). | Pass with a format slip. Whether SessionStart `injectSteps` reached the model was not visible. |
| 4 | Claude Code / claude-B | Logged switch `codex/codex-main → claude/claude-B`; ran `node --test` (2/2); replaced the prose observations with real hashes; set `done` only with test evidence; released the lock. | Pass. |

The reviewing session independently ran `node --test` after step 3b (2 pass) and step 4
(2 pass), and `handoff.py check` after steps 1, 2 and 4 (no errors or warnings).

## Trial 4: abrupt stop (GAME-2)

A Claude Code session (claude-A) was told to implement D (`physics.js`) then E (test), and was
killed with SIGKILL 44 seconds in, as soon as `physics.js` appeared. It had already saved an
opening checkpoint (`in_progress`, `working`, writer claude-A) and held the lock. No Stop hook
ran. `inject.py` then reported three warnings: checkpoint still `working`, `1 files and 0
commits changed after HANDOFF.md was saved` listing `physics.js`, and a fresh advisory lock.
The checkpoint's Next still said to implement D.

Codex resumed with a prompt stating that the user confirmed the Claude session had stopped.
It inspected the untracked `physics.js` itself (it did not run inject), kept it unchanged,
recorded "predecessor runtime validation of physics.js is unknown", took over with
`--confirm-takeover` (log: `takeover: true`, `previous_state: fresh`, reason `limit`), added
`physics.test.js`, and verified `node --test` (4/4). Assessment: pass. A real usage limit was
not produced, so `StopFailure` remains unobserved.

## Trial 5: profiles

- **video:** Claude Code initialized `Profile: video`, recorded the exact 90-second real-time
  ffmpeg render under Running renders with start time and PID, started it with `nohup`, and
  stopped. ffmpeg finished normally about 90 seconds later (log ends with encoder statistics;
  ffprobe 90.0 s). Codex resumed, checked for a running ffmpeg with `pgrep`, read the log,
  verified the output (90.0 s, 2,700 frames), marked it latest, and did not render again: the
  file's modification time was unchanged. Pass.
- **motion:** Claude Code initialized `Profile: motion` with `design/tokens.json` and built
  `intro.html` (criterion H). Antigravity CLI (file tools only) read HANDOFF.md, then
  `tokens.json`, `intro.html` and profiles.md, and wrote `outro.html` (criterion I). All six
  token values (three colors, display font, easing, 900 ms) appear exactly in both files.
  Antigravity's Stop hook wrote a snapshot. Pass.
- **game:** covered by Trials 1-3.

## Findings fixed after the trial

1. Antigravity Stop payloads carry no event name, so snapshots now take `--event Stop` from
   the installed hook command.
2. Agents guessed `updated_at`; SKILL.md now says to read the system clock.
3. A prose `observed_file` line now gets a warning that shows the expected JSON form.

## Not covered

Antigravity App and IDE, a second Claude account, Windows, `StopFailure` on a real rate limit,
`PreCompact`, Codex hooks after trust, the staleness guard, interactive sessions, Cursor,
Gemini CLI, GitHub Copilot, OpenCode and Cline. Single runs on one machine; not a statistical
result.
