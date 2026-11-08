# Optional helper

Use Python 3.9+ and the standard library only. The core skill works manually without Python. Resolve the installed skill directory from the host rather than assuming a machine-specific path. In these commands, replace `SKILL` with that directory and `PROJECT` with the actual target directory. Do not run the helper against the skill package when you mean the user's project.

```sh
python3 SKILL/scripts/handoff.py init --project PROJECT
python3 SKILL/scripts/handoff.py inspect --project PROJECT
python3 SKILL/scripts/handoff.py check --project PROJECT
```

`init` creates only a draft HANDOFF.md using exclusive creation. It never overwrites an existing checkpoint, edits instructions, installs dependencies or initializes Git. Fill every REPLACE line before claiming initialization complete. `inspect` reads Git metadata when available and emits the checkpoint SHA-256. It does not inspect diffs, source contents, ignored assets, or writer activity for you.

## Save safely

Prepare a complete candidate outside the live checkpoint, review it, then use the digest from the checkpoint you actually read:

```sh
python3 SKILL/scripts/handoff.py save --project PROJECT \
  --candidate CANDIDATE.md --expected-sha DIGEST_FROM_INSPECT
```

This validates the candidate, refuses a stale digest, creates HANDOFF.md.previous with the prior bytes, then atomically replaces HANDOFF.md. The backup may itself be a damaged or draft record; inspect before trusting it. It is not an archive or source backup. Remove your candidate after confirming the save if it is no longer useful.

A short `.HANDOFF.md.save-lock` excludes simultaneous helper saves. A crash can leave it behind. Establish inactivity before removing it; the helper never steals it based on elapsed time. Manual editors bypass the guard. No cross-file transaction, source lock, power-loss durability, or synchronization across machines is promised. Keep only one writer. Custom relative checkpoint paths are supported through `--checkpoint`; parent directories must exist. Symlink checkpoint targets and paths escaping the project are refused.

## Optional metadata

Since v0.2.0, `check` and `save` also validate three optional metadata lines. Each may appear at most once:

| Line | Accepted values | Example |
| --- | --- | --- |
| `- updated_at:` | ISO 8601 time with a UTC offset (`Z` or `+HH:MM`) | `2026-11-08T14:05:00+07:00` |
| `- language:` | Language code; prose language only | `id`, `en`, `pt-BR` |
| `- profile:` | Lowercase names separated by commas | `video` or `game, motion` |

Malformed values are errors that name the field, the expected form and the received value. An `updated_at` more than five minutes in the future is a warning. The format stays `cross-agent-handoff/1`, so v0.1.x helpers ignore these lines and older checkpoints without them stay valid. The helper never writes `updated_at` for you; the saving agent sets it in the candidate.

## Optional stale-file detection

Use a small selection of relevant source/config/input files, not the whole project:

```sh
python3 SKILL/scripts/handoff.py inspect --project PROJECT --file src/example.py
```

Copy each returned observation into the Evidence section as one line:

```text
- observed_file: {"path":"src/example.py","sha256":"actual returned digest"}
```

For automatic change detection across the whole project, use `snapshot.py` and `inject.py` instead; see [hooks.md](hooks.md). `check` warns when those files change or disappear, or the checkpoint exceeds the reading budget. It cannot detect unobserved changes, missing dependencies, false evidence, changed requirements, or secret leakage. A matching hash does not prove a test passed.

Exit codes: `0` mechanical checks passed (or command succeeded), `1` warnings need review, `2` invalid records or an operation error. A valid structure is not proof that the project is ready for handoff. Run the agent's resume/recovery procedure regardless.
