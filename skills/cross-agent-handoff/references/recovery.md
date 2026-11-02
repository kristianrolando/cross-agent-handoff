# Recovery decisions

Read this only when state is missing, damaged, ambiguous, or inconsistent.

| Observation | Action |
| --- | --- |
| No checkpoint | Inspect project identity, instructions, request, relevant artifacts and baseline; create a minimum snapshot. Do not invent past intent. |
| Truncated checkpoint | Preserve it outside the live path; inspect the helper's previous copy if present. Treat that copy as historical, then reconstruct from files. |
| Saved work newer than checkpoint | Inspect actual changes, including staged and untracked inputs. Record recovered progress as current observations, not fabricated predecessor events. |
| Checkpoint says tests passed | Verify the tested inputs/environment and evidence. If absent or changed, mark historical/unverified and repeat affected checks. |
| Checkpoint says done but criteria fail | Reopen as partial or blocked and record the discrepancy and evidence. |
| Conflicting specifications | Find controlling user decision and one canonical owner. If unresolved intent changes dependent work, ask for that decision while continuing independent work. |
| Failed approach absent from checkpoint | Do not infer it from memory. Record any now-verifiable result and uncertainty. |
| Writer still active or activity unknown | Do not overlap writes. Stop your own jobs when appropriate; otherwise establish inactivity or explicit transfer. Old timestamps and PIDs alone are insufficient. |
| Helper save refuses stale digest | Reread latest checkpoint and relevant files; merge supported facts into a new candidate. Never retry blindly with a new digest. |
| Helper lock remains after crash | Inspect for a live helper writer. Only after establishing inactivity, remove the recorded save lock; do not use a timeout as proof. |
| Competing handoff files | Select the actual canonical owner with applicable rules; migrate useful facts, then replace obsolete routing with a pointer. Preserve meaningful history. |
| New device or uploaded snapshot | Compare identities and include required uncommitted/untracked files. A commit alone may omit the work. |

## Recovery save

Save products/evidence first, then write the reconciled checkpoint. Keep verified facts, hypotheses, and unknowns visibly distinct. Include the discrepancy, inspection performed, invalidated checks, remaining scope, and next action. Record the current agent as observer; do not attribute changes from modification times. A Markdown backup cannot restore lost source code.

## Concurrency extension

Use separate branches/worktrees or explicitly disjoint output areas, task-specific checkpoints, and an integrator when simultaneous work is requested. Agree how shared decisions and records merge. Do not share the sequential checkpoint among uncoordinated writers. The helper's short save lock only serializes helper writes; it does not lock source files, stop models, or coordinate manual editors.
