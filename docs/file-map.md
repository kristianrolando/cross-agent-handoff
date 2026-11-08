# File map

| Path | Purpose |
| --- | --- |
| skills/cross-agent-handoff/SKILL.md | Portable lifecycle, information ownership and boundaries |
| skills/cross-agent-handoff/agents/openai.yaml | Optional Codex UI metadata; ignored by the portable core |
| skills/cross-agent-handoff/assets/checkpoint.md | The single default project checkpoint template |
| skills/cross-agent-handoff/assets/profiles/*.md | Optional game, video and motion checkpoint sections |
| skills/cross-agent-handoff/references/profiles.md | When to use each profile, rules and contribution guide |
| skills/cross-agent-handoff/references/agents.md | Host installation paths, activation, routing and official sources |
| skills/cross-agent-handoff/references/setup.md | Non-destructive setup, migration and removal |
| skills/cross-agent-handoff/references/recovery.md | Interrupted/stale/conflicting state and concurrency boundaries |
| skills/cross-agent-handoff/references/helper.md | Optional helper commands and exact limitations |
| skills/cross-agent-handoff/scripts/handoff.py | Standard-library draft/check/inspect/save helper |
| skills/cross-agent-handoff/scripts/snapshot.py | Mechanical snapshot into `.handoff/auto/` and the optional staleness guard |
| skills/cross-agent-handoff/scripts/inject.py | Resume context with a live check for work newer than the checkpoint |
| skills/cross-agent-handoff/scripts/install.py | Multi-host project/user install, update, doctor and uninstall |
| skills/cross-agent-handoff/VERSION | Package version written into each installed copy |
| skills/cross-agent-handoff/scripts/lock.py | Opt-in advisory lock and append-only switch log |
| skills/cross-agent-handoff/references/lock.md | Lock use, takeover confirmation, files and limits |
| skills/cross-agent-handoff/scripts/hooks.py | Opt-in install/remove/status of Claude Code, Codex and Antigravity hooks |
| skills/cross-agent-handoff/references/hooks.md | Snapshot layers, hook support per host, guard and removal |
| .claude-plugin/plugin.json | Standalone Claude Code plugin wrapper |
| .claude-plugin/marketplace.json | Local/Git marketplace catalog for that wrapper |
| docs/releasing.md | Publication runbook, resolved synchronization record and release notes |
| CONTRIBUTING.md | Shared human and coding-agent contribution and handoff workflow |
| CLAUDE.md | Claude contributor adapter importing shared rules |
| AGENTS.md | Canonical shared contributor instructions |
| .github/pull_request_template.md | Focused change and validation review template |
| docs/assets/*.svg | Editable README banner with eight agent logos, handoff flow and checkpoint map |
| docs/assets/brand-credits.md | Pinned logo sources, attribution and maintenance notes |
| docs/assets/lobe-icons-LICENSE | Upstream MIT notice for embedded Lobe Icons brand marks |
| README.md | Public quick start, compatibility matrix, installation and workflows |
| LICENSE | User-approved MIT license for the project |
| skills/cross-agent-handoff/LICENSE | Same MIT notice bundled with direct skill installs |
| .github/workflows/release.yml | Checked versioned release publication on explicit tag or dispatch |
| docs/releases/v0.1.0.md | Initial public release notes and install commands |
| CHANGELOG.md | Version history with links to release notes |
| docs/releases/v0.2.0.md | v0.2.0 notes and upgrade steps from v0.1.1 |
| docs/evidence/live-trial-kit-v0.2.0.md | Step-by-step live trials for the maintainer, results left empty |
| docs/evidence/live-trial-2026-11-08.md | Headless Claude Code, Codex and Antigravity CLI trials of v0.2.0 |
| docs/evidence/live-trial-template.md | Record form for live trials |
| docs/releases/v0.1.1.md | Expanded host guide, helper and workflow fixes release notes |
| .github/workflows/ci.yml | GitHub Actions matrix for automatic package/protocol checks |
| docs/ci.md | CI scope, configured environments and local equivalent |
| docs/checkpoint-example.md | Explanation of an illustrative handoff |
| docs/examples/before.md | Complete illustrative outgoing checkpoint |
| docs/examples/after.md | Complete illustrative successor checkpoint |
| docs/architecture.md | Reference critique, alternatives, trade-offs and official sources |
| docs/validation.md | Observed results and unvalidated areas |
| docs/roadmap/ | Maintainer v0.2.0 brief (verbatim) and the approved Phase 0 audit and plan |
| docs/evidence/ | Test output, independent-agent recovery and the 2026-11-02 live Codex/Antigravity trial |
| tests/test_handoff.py | Disposable filesystem and failure-injection scenarios |
| tests/test_package.py | Package integrity and portable metadata/link checks |
| tests/test_autosave.py | Snapshot, resume-context and abrupt-stop scenarios |
| tests/test_install.py | Installer idempotency, doctor, v0.1.1-layout upgrade and uninstall |
| tests/test_lock.py | Lock acquisition, blocked and confirmed takeover, switch log, heartbeat |
| tests/test_profiles.py | Profile sections, size budgets and running-render surfacing |
| tests/test_hooks.py | Hook configuration merge, removal and command execution |
| .gitignore | Exclude generated Python caches |

A consumer project normally gains only HANDOFF.md plus reviewed routing additions to existing instructions. Snapshots, when used, add a self-ignored `.handoff/auto/` folder; opt-in hooks add entries to the host configuration files listed in the hook guide. Helper saves additionally create HANDOFF.md.previous; the save lock and replacement temp files are transient unless interrupted. Existing project formats may be reused without helper tooling.

## Project and distribution scope

This checkout is the standalone Cross-Agent Handoff project. Maintain the skill under `skills/cross-agent-handoff` and its optional Claude Code plugin/catalog at the checkout root. No placement into another repository is required.

Consumer installation is separate from authoring. Follow README.md to copy the complete skill to a supported host location or load this checkout as a local Claude Code marketplace. Review an existing destination before updating it; do not overwrite another skill or plugin's configuration. Actual host installation and discovery remain distinct from manifest validation.
