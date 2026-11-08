# Live-trial kit for v0.2.0

Instructions for the maintainer to run real agent sessions. Record every result with
[live-trial-template.md](live-trial-template.md): copy it to
`docs/evidence/live-trial-YYYY-MM-DD-NAME.md` and fill it during the session. Results here are
intentionally empty. Never write a result you did not observe, and keep a failed or partial
trial as it happened.

## What is already known (before this kit)

| Item | Status on 2026-11-08 |
| --- | --- |
| Codex → Antigravity CLI → Codex handoff | Passed once (v0.1.1, [record](live-trial-2026-11-02.md)) |
| Claude Code SessionStart and Stop hooks | Ran once in print mode; model quoted injected context ([validation](../validation.md)) |
| Claude Code handoff, Antigravity App/IDE, StopFailure, Codex hooks, Antigravity hooks, Windows hooks, profiles | Not run |

## Setup (once per trial)

Use a disposable folder, not a real project. Replace `KIT` with this repository's path.

```sh
mkdir trial-project && cd trial-project && git init
python3 KIT/skills/cross-agent-handoff/scripts/install.py --project . --hosts claude,codex,antigravity --dry-run
python3 KIT/skills/cross-agent-handoff/scripts/install.py --project . --hosts claude,codex,antigravity
python3 KIT/skills/cross-agent-handoff/scripts/install.py --project . --doctor
```

For hook trials add `--with-hooks` (it asks before writing), then open `/hooks` in Codex to
trust its hooks. Record each agent's version, account alias (for example `claude-A`, never an
email), and model if shown. Do not paste tokens, emails or private chat into the record.

Task for trials 1-3: a small game file `game.js` with `move(x, dx)` and three criteria.
A: `move(0, 1)` returns 1. B: positions are clamped to 0-10. C: a test file covers A and B and
passes with `node --test` (or a Python equivalent if Node is absent).

## Trial 1: Claude Code (claude-A) → Codex

1. Claude Code, account claude-A:
   `/cross-agent-handoff Initialize continuity in this project. Profile: game. Then implement only criterion A, save a handoff and stop. Do not commit.`
   Then: `Acquire the advisory lock as agent claude, alias claude-A, before editing.`
2. Record: was HANDOFF.md created with a game profile section; did the agent acquire and,
   at handoff, release the lock; output of `python3 .claude/skills/cross-agent-handoff/scripts/handoff.py check --project .`.
3. Close Claude Code. Codex: `Use $cross-agent-handoff to resume this project. Implement only criterion B, save a handoff and stop. Do not commit.`
4. Record: did Codex read the checkpoint before editing, keep A, record evidence honestly,
   and log the switch (`.handoff/log.jsonl`)?

## Trial 2: Codex → Antigravity App or IDE

1. Start from trial 1's state. In the Antigravity App or IDE, open the same folder and check
   that the skill is listed (IDE: Customizations).
2. Prompt: `/cross-agent-handoff Resume this project. Finish criterion C, verify it, save the final handoff.`
3. Record: discovery surface, whether shell commands ran, whether the test passed, final status.
   If hooks were installed: did `.handoff/auto/latest.json` record a `Stop` from host `antigravity`,
   and did the SessionStart context appear?

## Trial 3: Antigravity → Claude Code (claude-B)

1. Switch Claude Code to account claude-B. Prompt:
   `/cross-agent-handoff Resume this project. Review the finished work against the criteria, take over the lock as claude-B if I confirm, and save.`
2. When the lock warning appears, confirm only after Antigravity is closed.
3. Record: did the agent ask before `--confirm-takeover`; was the takeover logged with `from` and `to`?

## Trial 4: abrupt stop without a semantic save

1. With hooks installed for Claude Code, ask for a change that touches two files, and stop the
   session mid-work: close the terminal or app while it edits, or let a usage limit hit.
   Do not ask for a handoff.
2. Open the next agent and resume.
3. Record: inject output (copy the WARNING lines), whether the successor listed the changed
   files, recovered from the actual files rather than the stale checkpoint, and marked unknown
   history as unknown. If a real limit hit Claude Code, record whether
   `.handoff/auto/latest.json` shows event `StopFailure` with error `rate_limit`.

## Trial 5: profiles

Run once each, in fresh folders, with any agent:

- `game`: Trial 1 already covers it if the game section was filled correctly.
- `video`: initialize with `Profile: video`, ask for an ffmpeg command that renders a 3-second
  test clip from a generated source (`ffmpeg -f lavfi -i testsrc=duration=3 ...`). Ask the
  agent to record the render before starting it. Switch agents during or after the render.
  Record whether the successor checked the output instead of re-rendering.
- `motion`: initialize with `Profile: motion` and a small style-tokens file. Switch agents and
  ask for a second composition. Record whether the successor read the tokens first and kept
  the same colors and durations.

## Optional checks

- Windows: run Setup and Trial 4 on Windows 11 and record the hook command form that worked.
- Codex hook trust: record what `/hooks` showed before and after trusting.
- Staleness guard: install with `--guard`, edit five files without saving, and record whether
  the agent was asked once and then allowed to stop.

## After the trials

Add a short summary with links to docs/validation.md and update the README compatibility
rows only with what the records show. Keep "not run" for anything not observed.
