# Live trial record: routing block v0.2.1, v0.2.3 and a candidate (2026-11-26, second pass)

Follow-up to [the first pass](live-trial-2026-11-26-routing-block.md), which found the fixture
confounded for C6. Procedure: [live-trial-kit-v0.2.2.md](live-trial-kit-v0.2.2.md) with the kit
revised as described below. Only what was observed is recorded.

## Environment and changes to the kit

- macOS, Claude Code 2.1.319 headless, model `claude-sonnet-5-5`, fresh sessions run in parallel
  batches, the skill not installed in the fixtures, user-level plugin kept out with
  `--setting-sources project --disable-slash-commands --strict-mcp-config --no-session-persistence`.
- Fixture changes: the fake job is now a process named `bash render.sh` (a second start is
  recorded and does nothing), the 70 clip files exist, and the checkpoint plants facts that
  compaction must keep. Batch 4 plants nine (three key facts and six open items).
- Scorer changes: C5 also fails if `render.sh` is started a second time; C6 passes when any line of
  `HANDOFF.md` says the render is or may be alive (the first version looked only for the label
  "Writers / operations", which agents dropped when compacting); C7 counts planted facts kept.
  The scorer first required the token "4 seconds", which three runs wrote as "4 s"; those were
  rewording, not loss, and the token is now "4 s".
- Arms: `old` = routing block of tag v0.2.1 (94 words); `new` = block of v0.2.2 and v0.2.3
  (128 words); `cand` = a candidate of 155 words (counted with its two marker lines, the way the
  package test counts) that adds two sentences: "Run `date -Iseconds` and paste the result into
  updated_at; never estimate it" and "If HANDOFF.md is over 1,200 words, compact it in the same
  save: one line per finished item; keep open items, decisions and failed attempts."
- Arms were assigned in random order with neutral folder names and unblinded after scoring. The
  scorer (Claude) saw the arms only after scoring, except for the lost blinding noted in the first
  pass, which did not recur.

## Results

| Batch | Arms (runs) | Checkpoint at most 1,300 words (starts 2,096 to 2,184) | `updated_at` from the real clock (not rounded to `:00`) | Planted facts kept | Upload run or render restarted |
| --- | --- | --- | --- | --- | --- |
| 2 | old (5), new (5) | old 0/5, new 3/5 | old 0/5, new 2/5 | 3/3 in all 10 | none |
| 3 | new (5), cand (5) | new 3/5, cand 5/5 | new 3/5, cand 5/5 | 3/3 in all 10 | none |
| 4 | new (8), cand (8) | new 3/8, cand 8/8 | new 4/8, cand 8/8 | new 7/8 runs complete (one dropped the Indonesian-first caption wish), cand 8/8 | none |

Pooled over the batches that ran `new` and `cand` together (3 and 4): size 6 of 13 against 13 of
13 (Fisher exact, one-sided, p about 0.003); real clock 7 of 13 against 13 of 13 (p about 0.008).
Both are from one model on one synthetic project, so they say the added sentences changed what
these agents did there, not that real projects behave the same. C2 (owner answer applied) and C3
(owner question saved) passed in every run; C6 (running render visible) passed in 25 of 26 scored runs by whole-file
mention. The exception is one `cand` run that recorded the pid as a `bash render.sh` process of
unverified liveness and said not to start a render; the scorer's keywords missed it, and a person
would count it as visible.

## What it says

- The two added sentences made compaction and the clock dependable in this fixture. Under the
  `new` block half of the runs left the checkpoint at its starting size.
- Compaction to 390 to 670 words kept the planted facts in 35 of 36 runs; the one loss was in a
  `new` run. This does not show that compaction is safe in general.
- Cost of the added words: 27 words against `new`, about 95 tokens per session at the audit's
  characters-per-token estimate.
- Limits: three batches, two fixture versions; one model and one host; no Windows; blinding was by
  folder name only; C3 and the render check contain judgment, made by Claude.
