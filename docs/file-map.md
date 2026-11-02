# File map

| Path | Purpose |
| --- | --- |
| skills/cross-agent-handoff/SKILL.md | Portable lifecycle, information ownership and boundaries |
| skills/cross-agent-handoff/agents/openai.yaml | Optional Codex UI metadata; ignored by the portable core |
| skills/cross-agent-handoff/assets/checkpoint.md | The single default project checkpoint template |
| skills/cross-agent-handoff/references/agents.md | Host installation paths, activation, routing and official sources |
| skills/cross-agent-handoff/references/setup.md | Non-destructive setup, migration and removal |
| skills/cross-agent-handoff/references/recovery.md | Interrupted/stale/conflicting state and concurrency boundaries |
| skills/cross-agent-handoff/references/helper.md | Optional helper commands and exact limitations |
| skills/cross-agent-handoff/scripts/handoff.py | Standard-library draft/check/inspect/save helper |
| .claude-plugin/plugin.json | Standalone Claude Code plugin wrapper |
| .claude-plugin/marketplace.json | Local/Git marketplace catalog for that wrapper |
| docs/releasing.md | Publication runbook, resolved synchronization record and release notes |
| CONTRIBUTING.md | Shared human and coding-agent contribution and handoff workflow |
| CLAUDE.md | Claude contributor adapter importing shared rules |
| AGENTS.md | Canonical shared contributor instructions |
| .github/pull_request_template.md | Focused change and validation review template |
| docs/assets/*.svg | Editable README banner, handoff flow and checkpoint map |
| README.md | Public quick start, compatibility matrix, installation and workflows |
| LICENSE | User-approved MIT license for the project |
| skills/cross-agent-handoff/LICENSE | Same MIT notice bundled with direct skill installs |
| .github/workflows/release.yml | Checked versioned release publication; initial v0.1.0 bootstrap |
| docs/releases/v0.1.0.md | Initial public release notes and install commands |
| .github/workflows/ci.yml | GitHub Actions matrix for automatic package/protocol checks |
| docs/ci.md | CI scope, configured environments and local equivalent |
| docs/checkpoint-example.md | Explanation of an illustrative handoff |
| docs/examples/before.md | Complete illustrative outgoing checkpoint |
| docs/examples/after.md | Complete illustrative successor checkpoint |
| docs/architecture.md | Reference critique, alternatives, trade-offs and official sources |
| docs/validation.md | Observed results and unvalidated areas |
| docs/evidence/ | Reproducible test output and independent-agent recovery artifact |
| tests/test_handoff.py | Disposable filesystem and failure-injection scenarios |
| tests/test_package.py | Package integrity and portable metadata/link checks |
| .gitignore | Exclude generated Python caches |

A consumer project normally gains only HANDOFF.md plus reviewed routing additions to existing instructions. Helper saves additionally create HANDOFF.md.previous; the save lock and replacement temp files are transient unless interrupted. Existing project formats may be reused without helper tooling.

## Project and distribution scope

This checkout is the standalone Cross-Agent Handoff project. Maintain the skill under `skills/cross-agent-handoff` and its optional Claude Code plugin/catalog at the checkout root. No placement into another repository is required.

Consumer installation is separate from authoring. Follow README.md to copy the complete skill to a supported host location or load this checkout as a local Claude Code marketplace. Review an existing destination before updating it; do not overwrite another skill or plugin's configuration. Actual host installation and discovery remain distinct from manifest validation.
