# Advisory lock and switch log

Read this when a project uses `.handoff/lock.json`, when inject warns about a held lock, or
when the user asks to make a second writer visible. The lock is opt-in: it exists only after
someone runs `lock.py acquire`. It is a shared note, not enforcement. It cannot stop another
agent, editor or process, and the sequential one-writer rule still applies.

## Use

```sh
python3 SKILL/scripts/lock.py status --project PROJECT
python3 SKILL/scripts/lock.py acquire --project PROJECT --agent claude --alias claude-A --reason limit
python3 SKILL/scripts/lock.py release --project PROJECT --agent claude --alias claude-A
```

- `--agent` is the host label. `--alias` is a short label the user chose for an account,
  such as `claude-A`. It can also come from the `HANDOFF_AGENT_ALIAS` environment variable.
  Labels allow only letters, digits, `.`, `_` and `-`, so emails cannot be stored.
  Two accounts of one host on the same machine cannot be detected automatically; take the alias
  from the user for each session and do not reuse a stored one.
- `--reason` records why the previous writer stopped, as reported:
  `limit`, `manual`, `crash`, `new-session` or `unknown`. It is not verified.
- Acquire on a held lock fails with exit code 3. This applies whether the heartbeat is fresh
  (default under 10 minutes; `lock.stale_minutes` in `.handoff/config.json`) or stale.
  A stale heartbeat does not prove that the session stopped. Ask the user. Only after they
  confirm, rerun acquire with `--confirm-takeover`; the takeover is logged.
- `release` frees only your own lock. `force-release --yes` removes another session's lock
  after the user confirms, and is logged.
- Release your lock when you save a `ready` handoff.

## Files

| File | Git | Content |
| --- | --- | --- |
| `.handoff/lock.json` | Ignored (written to `.handoff/.gitignore`) | `agent`, `alias`, `host`, `started_at`, `heartbeat` |
| `.handoff/log.jsonl` | Committed by default | One line per acquisition: `at`, `from`, `to`, `reason`, `reason_source`, `takeover`, `checkpoint_sha256` |

The heartbeat is refreshed when an opt-in Stop or PreCompact hook snapshot runs for the
same host as the lock ([hooks.md](hooks.md)). Without hooks it is refreshed only by
re-running acquire, so a live session can look stale. That is one reason stale locks still
need confirmation. The switch log is a short audit trail, not a resume source: read the
checkpoint first. Rolling copies of past checkpoints are deferred to v0.3.0; the helper's
`HANDOFF.md.previous` and Git history remain the history.
