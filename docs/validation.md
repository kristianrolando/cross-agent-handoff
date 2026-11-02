# Validation results

## Observed environment and scope

Validation date: 2026-11-02. macOS, Python 3.9.6, Git 2.54.0, Claude Code 2.1.287. Tests run in disposable directories. The package is authored and delivered in its standalone checkout. No integration into an unrelated repository is required.

No global host settings, installed skill directories, subscription configuration, production application, remote repository, or cloud service were changed. A temporary virtual environment was used to attempt validator dependency setup; its package download failed due to network resolution, and no runtime dependency was added to this package.

## Maintainer feedback and public packaging update

The maintainer reported successful testing and smooth operation, then authorized MIT licensing and public documentation/CI improvements. Record that as successful maintainer feedback. Exact tested application versions, operating systems, settings, and scenario coverage were not supplied; do not invent them or relabel the original authoring-environment trial as a pass.

The public package now includes MIT notices in both the repository and standalone skill, a short quick start, explicitly fictional before/after checkpoint examples, a compatibility matrix, and a GitHub Actions workflow. The Linux/macOS/Windows matrix subsequently passed its first hosted run; see the hosted evidence below. No additional live model testing was attempted for this documentation update.

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

## Hosted CI evidence

Public repository: [kristianrolando/cross-agent-handoff](https://github.com/kristianrolando/cross-agent-handoff).
First hosted run: [Package checks #1](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41401002913) on commit `74d2c5c4c7fae8adf72e3053e4db4cb22f829af2`.
The GitHub API reported all four jobs completed successfully:

| Runner / Python | Job ID | Result |
| --- | --- | --- |
| macos-latest / 3.13 | 125132595593 | success |
| windows-latest / 3.13 | 125132595775 | success |
| ubuntu-latest / 3.9 | 125132595843 | success |
| ubuntu-latest / 3.13 | 125132595933 | success |

Each job's package/protocol step and whitespace check succeeded. These are actual hosted checks, distinct from maintainer-reported live use and the earlier independent-agent trial.

## Distribution checks

The public command `npx --yes skills add kristianrolando/cross-agent-handoff --list` cloned the GitHub repository and found exactly one skill: cross-agent-handoff.

In a disposable project, `npx --yes skills add kristianrolando/cross-agent-handoff --skill cross-agent-handoff --agent codex --agent claude-code --copy --yes` exited successfully. Both `.agents/skills/cross-agent-handoff` and `.claude/skills/cross-agent-handoff` contained identical SKILL.md instructions plus LICENSE, helper, template and setup reference. No global host installation or live model invocation was performed. This checks distribution and file completeness, separately from maintainer-reported app behavior.

## Release evidence

[Cross-Agent Handoff v0.1.0](https://github.com/kristianrolando/cross-agent-handoff/releases/tag/v0.1.0) is published, not a draft or prerelease. Its source target is `666e04c279d312a375a9ba06b5f9e6dfd3d92204`.

- [Package checks on the release source](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41429718683): four jobs completed successfully (Windows 3.13, Ubuntu 3.9, macOS 3.13, Ubuntu 3.13).
- [Publish release](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41429718374): version/notes/package checks and publication job completed successfully.
- Release/tag publication was read back through the GitHub API. Closing documentation/checkpoint updates follow on main without moving the frozen v0.1.0 tag.

## Publication status

The public repository, MIT skill, Claude Code plugin/catalog, contributor guidance, CI and initial versioned release are available. README and plugin metadata point to the actual repository. Repository topics agent-skills, ai-agents, claude-code, codex and handoff were saved and visibly verified.

The original Mac checkout has been reconciled. Commit `b0d3e39` records the completed recovery; local main and the public branch matched at that commit with a clean working tree when reviewed. The interrupted `57c17ab` and published `fddd8d1` snapshots were compared again and found identical. The [resolved synchronization record](releasing.md#resolved-desktop-synchronization) retains the history and guidance for future checkouts. No pending synchronization blocker remains from that interruption. Native Codex plugin packaging remains outside the documented direct-skill route.

## Expanded agent routes (2026-11-02)

Added host-specific installation, activation and instruction-routing guidance for Antigravity,
Cursor, Gemini CLI, GitHub Copilot, OpenCode and Cline. Official sources and current documented
locations are recorded in the bundled [host guide](../skills/cross-agent-handoff/references/agents.md).
The portable lifecycle and default checkpoint format remain unchanged. The core now contains
about 1,214 whitespace-delimited words; the host guide is loaded only for installation/routing.

On macOS with Node.js 26.11.1, Skills CLI 1.7.4 completed a project-local copy installation
from this working checkout into a disposable directory, selecting all eight named agents:

```sh
npx skills@1.7.4 add /path/to/cross-agent-handoff --skill cross-agent-handoff \
  --agent claude-code codex antigravity cursor gemini-cli github-copilot opencode cline \
  --copy --yes
```

The CLI produced two shared destinations: `.agents/skills/cross-agent-handoff` and
`.claude/skills/cross-agent-handoff`. In both destinations all ten files from the local source folder matched
byte-for-byte, including the new host guide, LICENSE, template and helper. A separate manual
copy to the officially documented Cline destination, `.cline/skills/cross-agent-handoff`, also
matched all ten files. Correction (later review): the skill has nine tracked files; the tenth
was most likely the untracked macOS `.DS_Store` in that local checkout, which a GitHub install
does not receive. Installing from a local working folder copies untracked files too. Multiple selected hosts share the same physical folder; this is not
eight independently observed host loaders. No global installation or settings changed.

All 27 existing package/protocol checks passed again. Both changed hero SVGs were rendered
and visually inspected at their desktop/mobile sizes. No helper implementation changed.
The plugin manifest version advances to 0.1.1 so updated instructions have a distinct package
version on main. This is not a claim that a v0.1.1 release/tag has been published; v0.1.0 stays
frozen. New host model execution, automatic discovery, activation consent and live round-trip
handoffs were not exercised. Windsurf and other filesystem agents have an explicit-file fallback;
no native-discovery test is claimed for them. These limits do not negate the maintainer's earlier
reported successful use, whose exact application coverage remains unspecified.

Hosted [Package checks for the expanded-agent feature](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41447517465) completed
successfully on commit `a2c92cccf05d01ecec78b2eb0e6b43753ff6d49b`, covering all four configured
OS/Python jobs. GitHub-rendered README and the published host guide were read back successfully.
Closing evidence updates follow that verified feature commit on main.

## Critical review (2026-11-02, after b8ad312)

Host paths and activation were rechecked against the official pages linked in the host guide.
Corrections: Copilot also reads `.agents/skills/` and `.claude/skills/` and documents no slash
command; Cursor also reads `.claude/skills/` and `~/.agents/skills/`; Gemini CLI and Copilot also
read `~/.agents/skills/`; Cline enables discovered skills by default and does not document
`.agents/skills/`; Antigravity CLI exposes skills as slash commands. Claude Code reads `AGENTS.md`
only when no `CLAUDE.md` applies, and Gemini CLI loads only `GEMINI.md` by default. The Codex
skills page now redirects to learn.chatgpt.com.

Workflow fixes: the release workflow's v0.1.0 bootstrap trigger and default were removed because,
with manifest 0.1.1, any main push touching that file or a default dispatch would fail the version
check. Both workflows' whitespace step previously ran `git diff --check` on a fresh checkout,
which compares nothing; they now check the committed tree against Git's empty tree. Locally that
full-tree check passed on b8ad312. The new workflow YAML parsed; it has not run on GitHub yet.

Helper fixes: placeholder detection now matches template phrases (`REPLACE with`/`REPLACE from`)
instead of any uppercase `REPLACE`, so project terms such as SQL `INSERT OR REPLACE` no longer
block saves; an existing save lock now reports a clear recovery message. 28 local tests pass
(Python 3.9.6, macOS). No live host discovery or model handoff was exercised in this review.

## Live sequential handoff trial (2026-11-02)

A real Codex → Antigravity → Codex chain completed a three-criterion task in a disposable project,
each session seeing only the project files and a short prompt. Codex CLI 0.166 initialized the
checkpoint and did criterion A; Antigravity CLI 1.2.3 expanded `/cross-agent-handoff` from the
project-local `.agents/skills/` copy, resumed and did B with file tools only, recording its runtime
check as not_run; a fresh Codex session added tests, ran them (2 passed) and closed the task.
Details, prompts, hashes and the final checkpoint: [live trial evidence](evidence/live-trial-2026-11-02.md).

Limits: one trial on one Mac. Claude Code 2.1.287 discovered the project skill but could not run
(expired sign-in). Headless Antigravity denied shell commands in default and `--sandbox` modes;
auto-approval was not used, so Antigravity with shell access, its App and IDE remain untested.
Cursor, Gemini CLI, GitHub Copilot, OpenCode and Cline were not run.
