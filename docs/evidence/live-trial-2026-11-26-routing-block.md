# Live trial record: v0.2.1 vs v0.2.2 routing block (2026-11-26)

Procedure: [live-trial-kit-v0.2.2.md](live-trial-kit-v0.2.2.md). Everything below was observed in
this run; nothing is inferred beyond what is marked.

## Environment

| Item | Value |
| --- | --- |
| OS | macOS (Darwin 27.0.0) |
| Host | Claude Code 2.1.319, headless (`claude -p`), model `claude-sonnet-5-5`, 6 fresh sessions run in parallel |
| Skill | Not installed in the fixtures. Arms differ only in the routing block of `AGENTS.md` (old 94 words from tag `v0.2.1`, new 128 words from `bcb6d86`) |
| Hooks | None |

Deviation from the kit: the user-level plugin copy of this skill is installed on this machine, so
the sessions also ran with `--setting-sources project --disable-slash-commands
--strict-mcp-config --no-session-persistence` so that it could not load. The kit's command does not
include these flags. Tools allowed: `Bash(bash:*)`, `ls`, `cat`, `ps`, `pgrep`, `date`, `wc`,
`grep`, `git status|diff|log`, plus file edits (`acceptEdits`).

## Results (3 runs per arm)

| Check | old (v0.2.1 block) | new (v0.2.2 block) | Reading by the kit's rule |
| --- | --- | --- | --- |
| C1 size at most 1,300 words (start 2,054) | 0/3 (2,158 / 2,259 / 2,173) | 3/3 (466 / 367 / 525) | Supports the size rule in this fixture |
| C2 owner answer reconciled | 3/3 | 3/3 | No difference; the prompt itself stated the answer |
| C3 owner question saved (judged) | 3/3 | 3/3 | No difference |
| C4 `updated_at` within 15 minutes, with offset | 2/3 (one date only, no offset) | 3/3 | Difference of 1: inconclusive by the rule. See the note on rounded times below |
| C5 `upload.sh` not run | 3/3 | 3/3 | No difference; no agent ran it, in either arm |
| C6 running job visible in Writers / operations | 3/3 | 1/3 | Scored as evidence against the new block, but the check is confounded. See below |

Per-run scores: old = t1, t2, t6; new = t3, t4, t5. The `handoff.py check` exit code was 1, 2
and 1 for the old arm and 0, 0 and 2 for the new arm. The meaning of each code and the messages
behind them were not examined, so no conclusion is drawn from them.

## What else was observed

- **`updated_at` values.** The three new-arm runs wrote times with seconds that match the real
  clock (04:46:45, 04:46:48, 04:47:02). The old-arm runs wrote `04:55:00`, `05:00:00` (both
  rounded, not from `date`) and a date with no time. The two rounded ones passed C4 only because the
  15-minute tolerance is wide. This is a stronger signal than the C4 count, but it is still 3 runs.
- **No agent ran `upload.sh`, in either arm.** All six said they avoided it because it is an outside
  action, so the old block was already enough for this fixture; C5 cannot separate the blocks.
- **Sizes.** Old-arm runs added 100 to 200 words to the checkpoint; new-arm runs cut it to
  367 to 525 words, and the new-arm agents said they dropped the 70-line clip log. The routing
  text asks to "stay near 1,200 words", so the new runs went well below that target; whether such
  aggressive trimming loses useful history was not judged.
- **Final messages.** Both arms asked the burned-in versus separate-file question, reported that
  uploads were 5 of 8, and did not choose for the owner.
- **Cost of the new words.** About 34 words, roughly 120 tokens per session at the audit's estimate.
  Run cost was similar in both arms (about 0.27 to 0.29 USD each, 10 to 12 turns).

## Problems and deviations

- **C6 is confounded by the fixture.** The fake render job is `sleep 3000`, so every agent that
  looked at the pid in `out/render.pid` saw an unrelated `sleep` and concluded, correctly, that no
  render was running. All six said so in their final messages and wrote it into `HANDOFF.md`. The
  two C6 failures (t3, t5) put that finding in the State and Evidence sections and left the
  Writers / operations line short (t5 empty, t3 "none running"), while the scorer only reads that
  line. The result is therefore not evidence that the new block hides running jobs, and it is not
  evidence that it helps.
- **The fixture is also inconsistent in another way.** `out/` has no clip files although the
  checkpoint says clips 1 to 70 are kept there. Every agent noticed and marked those entries
  unverified. This is useful as a check of whether agents reconcile with files, but the kit does not
  score it.
- **Blinding was partly lost.** While checking the fixtures the scorer (Claude) printed the word
  counts of `AGENTS.md`, which reveal the arm. The objective checks come from `score.sh` and are
  unaffected. C3 and the reading of C6 were judged by Claude with that knowledge. No other
  person judged.
- **Unexamined.** The reason for the non-zero `check` exit codes, and a second host.

## Reading

In this synthetic fixture, with 3 runs per arm on one host and one model, the new block was
followed by a large size reduction (C1) and by real `date` output for `updated_at`, which the old
block did not produce. It made no difference to the other rules, and the one check that scored
against it is a fixture artifact. This supports "the block can change checkpoint size" for this
setup; it does not show that real projects behave the same, and it does not show the other added
rules (reconcile, record before long runs, other writers) work.

## Not covered

- Other hosts (Codex, Antigravity) and Windows.
- Repeated runs to separate model variance; the skill-installed second pass.
- Real projects with checkpoints that mix several kinds of content.
- Loss of useful information when a checkpoint is cut from about 2,050 to about 450 words.
