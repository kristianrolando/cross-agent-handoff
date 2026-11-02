# Validation results

## Observed environment and scope

Validation date: 2026-11-02. macOS, Python 3.9.6, Git 2.54.0, Claude Code 2.1.287. Tests run in disposable directories. The package is authored and delivered in its standalone checkout. The user clarified that the previously named external repository was unrelated; no placement into that repository is required.

No global host settings, installed skill directories, subscription configuration, production application, remote repository, or cloud service were changed. A temporary virtual environment was used to attempt validator dependency setup; its package download failed due to network resolution, and no runtime dependency was added to this package.

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

Observed result: the agent inspected source, avoided rewriting completed work, ran five direct string-case checks, preserved an unrelated user draft, marked old test history and authorship unknown, and saved a done/ready checkpoint. The saved checkpoint and reproduction procedure are retained in [the evidence artifact](evidence/independent-recovery.md). This is a single-family independent context trial, not a Claude/Codex end-to-end test. The temporary absolute path in that artifact records the trial location and is not a runtime dependency.

## Platform and format checks

- Claude Code's native plugin validator passed for both the standalone plugin manifest and marketplace after adding attribution/catalog descriptions.
- YAML frontmatter and Codex UI metadata parsed successfully with Ruby's standard YAML parser. The bundled skill-creator quick validator could not run because PyYAML was absent; attempted dependency retrieval in a temporary environment failed due to network resolution. The package's own metadata tests also check required fields, name/directory match, description size, links and placeholder absence.
- Claude CLI was present and reported authenticated status. A bounded read-only resume request was attempted; it produced no usable resume assessment and ended with `error_during_execution` after interruption of the pending run. It is inconclusive, not a passing model or discovery test. No cause beyond the available diagnostic is claimed.
- No `codex` CLI executable was found. This Work session and its independent agent can exercise the portable procedure, but do not substitute for testing Codex CLI discovery or a bidirectional live handoff.
- Real install/discovery in both hosts, persistent instruction loading, a true Claude to Codex to Claude round trip, and cross-device transfer remain unvalidated.

## Reproduce automated checks

From the package root:

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
claude plugin validate .claude-plugin/plugin.json
```

The automated suite comprises 24 tests. Actual output is saved in [test output](evidence/unittest.txt). It does not call either vendor model. The helper requires only the Python standard library.

## Self-review and fixes

1. Removed the mandatory separate event log and event-pointer protocol to reduce duplicated state and interrupted cross-file updates.
2. Kept only one optional helper; instruction-file editing remains deliberate and reviewable rather than an automatic config migration.
3. Fixed CRLF candidate validation found during portability review.
4. Preserved leading Git status columns instead of stripping whitespace, retaining staged/unstaged meaning.
5. Added explicit stale-digest refusal and no-timeout lock takeover rules. No source-lock claim remains.
6. Added negative checks demonstrating that valid Markdown can still contain false completion claims. The resume procedure, not the schema, must establish truth.
7. Kept durable criteria/decisions in existing owners; the checkpoint is not a second backlog. Existing equivalent formats remain supported manually.
8. Clearly separated implementation, local protocol tests, independent-agent behavior, plugin-manifest validation, actual installation, and full cross-vendor verification.

## Remaining work

Run the small live round-trip acceptance trial in both actual hosts, including actual skill discovery and persistent instruction loading. A remote Git repository and public release have not been created; select a license and release destination before publication. Do not call consumer installation, public distribution, or end-to-end platform compatibility complete until those actions are actually verified.
