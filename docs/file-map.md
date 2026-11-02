# File map

| Path | Purpose |
| --- | --- |
| skills/cross-agent-handoff/SKILL.md | Portable lifecycle, information ownership and boundaries |
| skills/cross-agent-handoff/agents/openai.yaml | Optional Codex UI metadata; ignored by the portable core |
| skills/cross-agent-handoff/assets/checkpoint.md | The single default project checkpoint template |
| skills/cross-agent-handoff/references/setup.md | Non-destructive setup, migration and removal |
| skills/cross-agent-handoff/references/recovery.md | Interrupted/stale/conflicting state and concurrency boundaries |
| skills/cross-agent-handoff/references/helper.md | Optional helper commands and exact limitations |
| skills/cross-agent-handoff/scripts/handoff.py | Standard-library draft/check/inspect/save helper |
| .claude-plugin/plugin.json | Standalone Claude Code plugin wrapper |
| .claude-plugin/marketplace.json | Local/Git marketplace catalog for that wrapper |
| README.md | Installation and copy-ready user workflows |
| docs/architecture.md | Reference critique, alternatives, trade-offs and official sources |
| docs/validation.md | Observed results and unvalidated areas |
| docs/evidence/ | Reproducible test output and independent-agent recovery artifact |
| tests/test_handoff.py | Disposable filesystem and failure-injection scenarios |
| tests/test_package.py | Package integrity and portable metadata/link checks |
| .gitignore | Exclude generated Python caches |

A consumer project normally gains only HANDOFF.md plus reviewed routing additions to existing instructions. Helper saves additionally create HANDOFF.md.previous; the save lock and replacement temp files are transient unless interrupted. Existing project formats may be reused without helper tooling.

## Target repository integration

The requested destination repository is outside this session's writable roots. An actual directory creation attempt returned `Operation not permitted`. This standalone checkout was implemented in the writable project workspace instead. The original motion-video-director files and manifest were not modified. The source reference was not modified.

To add only the skill to the requested repository after opening that repository in an authorized workspace, copy `skills/cross-agent-handoff` alongside `skills/motion-video-director`. Refuse an existing destination rather than overwriting it. Do not copy this standalone package's root manifest over the existing motion-video-director manifest. Its plugin wrapper belongs to this standalone checkout.

Example from this checkout, with TARGET replaced by the intended repository root:

```sh
test ! -e TARGET/skills/cross-agent-handoff && \
  cp -R skills/cross-agent-handoff TARGET/skills/cross-agent-handoff
```

Then review the existing host packaging before distributing a combined plugin. Direct installation from this standalone checkout already works independently. Target-directory placement and automatic host discovery were not verified here.
