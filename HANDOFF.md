# Project handoff

- format: cross-agent-handoff/1
- task_status: partial
- handoff: ready
- writer: none

## Project
Cross-Agent Handoff: a portable Agent Skill for sequential project continuity.
Rules: AGENTS.md. Installation: README.md. Design and sources: docs/architecture.md.
Source: skills/cross-agent-handoff. Validation and limitations: docs/validation.md.
No runtime services; Python 3.9+ only for the optional helper, Git optional for consumers.

## Task
Build the reusable Cross-Agent Handoff skill as a standalone project in this checkout.
Criteria: initialization/resume/checkpoint/handoff/recovery, platform independence, minimal files, non-destructive existing-project support, English documentation, realistic failure tests, honest platform limits.
The user clarified that the previously named external repository was unrelated. No external placement or integration is required.

## State
Verified: skill, template, three conditional references, optional helper, host metadata, standalone Claude plugin/catalog and user documentation exist. See docs/file-map.md.
Tests: see docs/validation.md and docs/evidence/unittest.txt for exact coverage.
Independent context trial preserved source and unrelated draft, recovered complete work from stale status, and saved an evidence-based checkpoint.
Unfinished validation: live Claude/Codex round trip and host discovery remain unvalidated. No public remote or distribution release exists.
Decision: one current checkpoint, reuse canonical project documentation, no mandatory event log or global hooks. Rationale and alternatives: docs/architecture.md.
Writers/operations: no application writer or background job belongs to this package. The attempted Claude CLI trial has ended. No model trial continues running.

## Evidence
Automated protocol/package checks and native Claude manifest validation: docs/validation.md. A true cross-vendor handoff has not passed. Historical model test claims are not accepted as current evidence.
The original source reference was not modified. Runtime content contains no personal path or API-key requirement. The generic packaged quick validator was blocked by missing PyYAML; YAML was independently parsed with Ruby and metadata checked by the package suite.

## Next
Run a disposable live handoff in both actual hosts when available, checking discovery, instruction loading and continuation in each direction. Use README.md for installation. Do not publish or infer new authorization from this checkpoint.

## Recent outcomes
- Current Codex session: inspected the reference guide, selected the single-checkpoint architecture, and built the standalone package.
- Current Codex session: exercised filesystem failures and both simulated handoff directions; an independent fresh agent recovered stale state without repeating completed work.
- Current Codex session: documented platform limits and left this package ready for continuation without chat history.
- User scope correction: this checkout is the project; removed the unrelated external placement requirement and updated routing/status documentation.
