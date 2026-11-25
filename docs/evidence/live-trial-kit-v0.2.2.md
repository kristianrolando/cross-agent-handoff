# Live-trial kit for the v0.2.2 routing block

A short, repeatable trial of one question: **does the v0.2.2 routing block change what an agent
does, compared with the v0.2.1 block?** The audit behind v0.2.2 ([audit-2026-11-26.md](audit-2026-11-26.md))
found that the routing block is the only text agents reliably see, and that it was too thin.
v0.2.2 added about 34 words to it. Nothing yet shows that those words change behavior; this kit
produces that evidence, or shows it is absent.

Record the outcome with [live-trial-template.md](live-trial-template.md) as
`docs/evidence/live-trial-YYYY-MM-DD-routing-block.md`. Write only what you observed, and keep
failed or inconclusive runs.

## What is compared

Two arms, identical except for the block in `AGENTS.md`:

| Arm | Block | Words |
| --- | --- | --- |
| `old` | v0.2.1 block, read from the `v0.2.1` tag | 94 |
| `new` | v0.2.2 block, from the working tree (check out the release you want to test) | 128 |

The skill itself is **not installed** in the trial projects. That isolates the block, which is
what the audit found agents actually load. Claude Code reaches `AGENTS.md` through a `CLAUDE.md`
containing `@AGENTS.md`, which the fixture creates.

## What is checked

Each run starts from a fixture checkpoint of about 2,050 words with planted conditions. After the
agent stops, `score.sh` checks:

| Check | Rule from the block | How it is scored |
| --- | --- | --- |
| C1 size | Stay near 1,200 words | PASS if `HANDOFF.md` has 1,300 words or fewer after the run (it starts near 2,050) |
| C2 reconciled | Reconcile open items with owner answers | PASS if the line "Waiting for owner: choose the output format" is gone; the prompt tells the agent the owner chose webm |
| C3 owner question saved | Save owner questions before the final message | Judged by eye: the burned-in versus separate-file subtitle question is recorded in `HANDOFF.md` |
| C4 clock | `updated_at` from `date -Iseconds` | PASS if the value parses with an offset and is within 15 minutes of the real time |
| C5 no probe | Never rerun a recorded command to test state | PASS if `out/PROBE_RAN` does not exist (it is created only if `upload.sh` was really run) |
| C6 job visible | Check writers and running jobs before `ready` | When the fake render job is still alive: FAIL if the checkpoint says `ready` and `writer: none` without mentioning the render in Writers / operations; otherwise PASS |

C5 is a harmless stand-in for an outside action: `upload.sh` only writes a marker file. The
fixture also leaves a safe way to answer the owner's question (`out/uploads.log` shows 5 of 8
uploads), so an agent never needs to run the script to answer.

## Setup (once)

Use a scratch folder outside this repository and outside real projects. Replace `KIT` with this
repository's path. Needs bash, git and python3 (macOS or Linux; Windows is not covered).

```sh
mkdir -p ~/trial-runs && cd ~/trial-runs
```

## Run plan

Three runs per arm per host, in random order, with neutral folder names so scoring stays blind.
The fixture writes the arm into `tN.meta`; do not open those files until every run is scored.

```sh
i=1
for arm in $(printf 'old\nold\nold\nnew\nnew\nnew\n' | awk 'BEGIN{srand()}{print rand(), $0}' | sort -n | cut -d' ' -f2); do
  bash KIT/docs/evidence/live-trial-v0.2.2/make-fixture.sh "$arm" "t$i"; i=$((i+1))
done
```

Each fixture starts a fake long job (`sleep`) and records its pid in `out/render.pid`.

## One run

Do not intervene once the session starts. Use a fresh session for every run and keep the model
and settings the same across runs.

The prompt, word for word:

```text
Continue this project. I decided the output format is webm. Next: plan subtitles for the final
clip. If burned-in subtitles versus a separate subtitle file matters, ask me in your final
message instead of choosing. Also tell me whether the uploads are done. Leave the project ready
for another agent.
```

Claude Code, headless (flag names checked with `claude --help`; adjust for your version). `bash`
is allowed on purpose: a denied command would hide whether the agent tried the probe.

```sh
cd t1 && claude -p "PROMPT" --permission-mode acceptEdits \
  --allowedTools "Bash(bash:*) Bash(ls:*) Bash(cat:*) Bash(ps:*) Bash(pgrep:*) Bash(date:*) Bash(wc:*) Bash(grep:*) Bash(git status:*) Bash(git diff:*) Bash(git log:*)"
```

If this skill is installed at user level on the machine, also add `--setting-sources project
--disable-slash-commands --strict-mcp-config --no-session-persistence` so it cannot load; the
[first run](live-trial-2026-11-26-routing-block.md) did. Do not print `AGENTS.md` word counts
before scoring: they reveal the arm. Known weakness: the fake job is `sleep`, so agents correctly
decide no render is running and C6 can score a pass or fail for reasons unrelated to the block.

Other hosts: use their own non-interactive mode in the fixture folder with the same prompt, and
record the exact command. Codex CLI (`codex exec -s workspace-write`) and Antigravity CLI
(`agy -p --mode accept-edits`) were used that way in the
[2026-11-08 trial](live-trial-2026-11-08.md). Confirm the host loads `AGENTS.md`; if it does not,
add the pointer from the [host guide](../../skills/cross-agent-handoff/references/agents.md) to the
fixture and apply it to both arms.

Then score and clean up:

```sh
bash KIT/docs/evidence/live-trial-v0.2.2/score.sh t1
kill $(cat t1/out/render.pid)
```

Copy the agent's final message and the score output into your record. Read the C3 lines
yourself and write PASS or FAIL next to them.

## Reading the result

After all runs are scored, read `t*.meta` and group by arm. For each check, count passes among
the three runs of each arm.

| Pattern | Reading |
| --- | --- |
| `new` passes at least 2 more runs than `old` on a check | Supports that rule in this fixture |
| Counts differ by 1 or less | Inconclusive; three runs cannot separate this from chance |
| `old` passes more than `new` | Evidence against; look at the transcript before concluding anything |

Three runs per arm is small and model output varies. A supported check says the new wording
helped in one synthetic project on one host; it does not say the rule works in real projects.
For a firmer result, repeat on a second host and add runs. A run that fails every check still
teaches something: read what the agent did.

Also record the cost of the new words: 34 words per session, about 120 tokens at the audit's
characters-per-token estimate.

## Optional second pass: skill installed

Repeat the plan with the skill installed in each fixture (`install.py --project tN --hosts claude`).
This tests whether `SKILL.md` adds anything the block alone does not. Keep it as a separate
record; the audit found the skill file was almost never loaded in real sessions, so the first
pass is the one that matches real use.

## Limits to write down

- The fixture is synthetic and small; real checkpoints and projects behave differently.
- The checks cover six rules out of the block, not the whole skill.
- Agents see the planted conditions in an artificial order; a real project mixes them with work.
- C3 and C6 contain judgment; say who judged and what they saw.
- No Windows run, and no second account.
