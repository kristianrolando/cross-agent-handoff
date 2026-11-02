# Validation results

## Observed environment and scope

Validation date: 2026-11-02. macOS, Python 3.9.6, Git 2.54.0, Claude Code 2.1.287. Tests run in disposable directories. The package is authored and delivered in its standalone checkout. No integration into an unrelated repository is required.

No global host settings, installed skill directories, subscription configuration, production application, remote repository, or cloud service were changed. A temporary virtual environment was used to attempt validator dependency setup; its package download failed due to network resolution, and no runtime dependency was added to this package.

## Maintainer feedback and public packaging update

The maintainer reported successful testing and smooth operation, then authorized MIT licensing and public documentation/CI improvements. Record that as successful maintainer feedback. Exact tested application versions, operating systems, settings, and scenario coverage were not supplied; do not invent them or relabel the original authoring-environment trial as a pass.

The public package now includes MIT notices in both the repository and standalone skill, a short quick start, explicitly fictional before/after checkpoint examples, a compatibility matrix, and a GitHub Actions workflow. The configured Linux/macOS/Windows matrix has not run on GitHub from this environment. No additional live model testing was attempted for this documentation update.

## Scenario coverage

| Requested case | Observed validation | Limit |
| --- | --- | --- |
| A: fresh project | Draft created; incomplete draft rejected; reviewed complete candidate saved and checked | Scripted filesystem fixture, not host onboarding |
| B: existing project | Existing instructions, README and source retained byte-for-byte; repeated init refused | Helper never edits routing; the agent's manual integration still requires review |
| C: Claude to Codex | Labeled actor protocol fixture passes; successor reads saved files and finishes greeting criteria | Labels simulate roles; not a live cross-vendor handoff |
| D: Codex to Claude | Reverse labeled actor fixture passes | Same simulation limitation |
| E: unexpected interruption | Truncated checkpoint detected, previous copy accessible, saved source preserved, recovered claims marked unknown; failed replacement preserves live bytes | Fault injection does not simulate power loss or every filesystem |
| F: stale/conflicting documentation | Selected hash changes/missing files warned; stale candidate refused; separate agent discovered already-complete source despite unfinished checkpoint | Structural validator deliberately cannot detect false claims without observations/inspection |
| G: context efficiency | Core skill and template have explicit word budgets; ordinary fixture resume needs no 10,000-line historical file | Reading-volume proxy; no measured model token, speed or cost improvement versus a baseline |
| H: portability | Relocated full skill works on a no-Git project with spaces; Windows CRLF candidate accepted; runtime files checked for personal paths/API-key dependencies | Actual runtime tests on macOS only; Windows/Linux host discovery not exercised |

Additional mechanics cover staged plus unstaged and untracked Git changes, duplicate/invalid metadata, ready with active writer, save-lock contention, symlink/path traversal rejection, backup preservation on invalid candidates, and not executing historical commands. The historical-command test covers the helper only; it is not proof of model-level prompt-injection resistance.

## Independent agent trial

A fresh Codex-family agent received only the skill path, disposable project path, a request to resume after interruption, and confirmation that prior writers stopped. It had no predecessor chat or expected answer. Source already contained the blank fallback; the checkpoint said it was unfinished and asserted historical tests without evidence.

Observed result: the agent inspected source, avoided rewriting completed work, ran five direct string-case checks, preserved an unrelated user draft, marked old test history and authorship unknown, and saved a done/ready checkpoint. The saved checkpoint and reproduction procedure are retained in [the evidence artifact](evidence/independent-recovery.md). This is a single-family independent context trial, not a Claude/Codex end-to-end test. The local temporary path in that artifact is omitted for publication; the saved procedure and source hashes retain the useful trial evidence.

## Platform and format checks

- Claude Code's native plugin validator passed for the marketplace and plugin manifest. During the public-packaging update, plugin validation also warned that root CLAUDE.md is not loaded as plugin project context. That file is for maintaining this repository; consumers receive the workflow through SKILL.md and their reviewed project routing, so no runtime CLAUDE.md loading is claimed.
- YAML frontmatter and Codex UI metadata parsed successfully with Ruby's standard YAML parser. The bundled skill-creator quick validator could not run because PyYAML was absent; attempted dependency retrieval in a temporary environment failed due to network resolution. The package's own metadata tests also check required fields, name/directory match, description size, links and placeholder absence.
- Claude CLI was present and reported authenticated status. A bounded read-only resume request was attempted; it produced no usable resume assessment and ended with `error_during_execution` after interruption of the pending run. It is inconclusive, not a passing model or discovery test. No cause beyond the available diagnostic is claimed.
- No `codex` CLI executable was found. This Work session and its independent agent can exercise the portable procedure, but do not substitute for testing Codex CLI discovery or a bidirectional live handoff.
- The authoring environment did not independently verify live installation or a cross-vendor round trip. The maintainer subsequently reported successful use; exact coverage remains unspecified. Cross-device transfer has no recorded verification.

## Reproduce automated checks

From the package root:

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
claude plugin validate .claude-plugin/plugin.json
```

The automated suite now comprises 27 tests, including bundled-license and public-example checks. Actual output is saved in [test output](evidence/unittest.txt). It does not call either vendor model. The helper requires only the Python standard library.

## Self-review and fixes

1. Removed the mandatory separate event log and event-pointer protocol to reduce duplicated state and interrupted cross-file updates.
2. Kept only one optional helper; instruction-file editing remains deliberate and reviewable rather than an automatic config migration.
3. Fixed CRLF candidate validation found during portability review.
4. Preserved leading Git status columns instead of stripping whitespace, retaining staged/unstaged meaning.
5. Added explicit stale-digest refusal and no-timeout lock takeover rules. No source-lock claim remains.
6. Added negative checks demonstrating that valid Markdown can still contain false completion claims. The resume procedure, not the schema, must establish truth.
7. Kept durable criteria/decisions in existing owners; the checkpoint is not a second backlog. Existing equivalent formats remain supported manually.
8. Clearly separated implementation, local protocol tests, independent-agent behavior, plugin-manifest validation, actual installation, and full cross-vendor verification.

## Publication status

MIT licensing, public documentation, shared Claude/Codex contributor entrypoints and CI configuration are complete. The maintainer authorized public publication. Repository `kristianrolando/cross-agent-handoff` has been created and verified public. Source upload, hosted CI and initial release are in progress; no hosted success is claimed yet. See [releasing.md](releasing.md) for the release procedure.

README commands and plugin metadata use the actual repository destination. The direct Codex skill route and Claude Code plugin route remain distinct. No additional live model testing is required for this packaging update.
