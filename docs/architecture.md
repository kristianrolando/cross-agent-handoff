# Architecture and reference evaluation

## Decision

Use a single replaceable project checkpoint, normally HANDOFF.md, with canonical links to existing rules, setup, architecture, requirements, decisions, backlog, and evidence. Keep the portable workflow in SKILL.md and put setup/recovery/helper details behind explicit reading routes. Keep only six content sections and four small metadata fields in the default format.

The core is a procedure followed by an agent with ordinary filesystem access. No platform API, IDE, runtime library, database, cloud account, orchestrator, daemon, or cross-vendor session transfer is required. Python and Git improve mechanics when present but are not core dependencies.

## Critical review of the starting reference

The supplied Claude and Codex Collaboration Guide was read in full before implementation. Its strongest parts were retained: evidence before claims, source inspection before continuation, single information owners, proportional recording, preserving dirty work, honest recovery limits, and distinguishing sequential from concurrent writing.

| Reference approach | Weakness for this skill | Implementation decision |
| --- | --- | --- |
| Mandatory event followed by checkpoint pointing to it | Two files can disagree after interruption; identifiers and correction rules add overhead | One checkpoint by default, with a small recent-outcomes section. Existing durable logs remain optional owners, not a second status database. |
| Opening/progress/closing events plus snapshot | Routine work can generate duplicate state and excessive history | Opening checkpoint only for substantial work; milestone snapshots and one closing snapshot. Read-only work creates no record by default. |
| Stable, unique event IDs and status vocabulary | Event IDs buy little in a sequential single-snapshot setup | No event IDs; task identity stays in the Task section. Retain only meaningful task and handoff states. |
| Detailed templates for several files | Can turn setup into a documentation migration project | One checkpoint template and one small routing block; reuse existing equivalents. |
| Advisory active-agent ownership | Can be mistaken for real exclusion | Keep an explicit writer note and process inspection requirements. No claim of source locking or automatic handoff. |
| Optional validators and atomic writes | Useful mechanics but easy to overstate | One optional helper validates structure/selective hashes and guards checkpoint saves. Recovery stays necessary. |
| File history | Snapshot compaction can lose useful past reasons | Keep unresolved decisions/failures in the snapshot or their canonical document. Link detailed history only when useful. |

## Alternatives rejected

- A single growing log: cheap to append, expensive to resume; mixes current status with stale facts.
- JSON task database plus generated Markdown: stronger machine schema, but two representations require synchronization and are harder to edit manually.
- Required SQLite/event sourcing: unjustified runtime and migration burden for alternating local agents.
- Automatic cross-agent API orchestration: violates the independence and subscription constraints.
- Required source locks/leases: cannot prevent manual edits, can leave stale ownership, and need coordination/fencing for real concurrency.
- Git-only context: loses uncommitted intent, failed approaches, external evidence and projects without Git.

## Persistence and failure boundaries

Save products/evidence, then replace the checkpoint. Single-file replacement avoids a log-pointer transaction, but it does not make source edits and checkpoint atomic together. On interruption, the successor reconciles actual source with the last saved claims. Unknown test history is unknown, even when source looks complete.

The optional helper provides exclusive draft creation, structural checks, selected-file hash checks, stale-digest rejection, one previous checkpoint, and a short exclusive save lock. It uses same-directory temporary files and replacement. It never edits rules, initializes Git, executes recorded commands, runs tests from logs, or touches application source.

The lock only coordinates helper writers. Manual edits bypass it, and interrupted helper saves can leave the lock. A human/agent must establish inactivity before removing it. There is no lock expiry, no automatic ownership theft, no cross-filesystem atomicity, and no power-loss durability guarantee. Preserve one writer for the project and shared records.

## Scope and trust

Treat authorization, intended behavior, and actual implementation as separate questions. A checkpoint can summarize authorization but cannot create new permission. Logs and source comments are data; inspect commands before using them. Do not import private chat transcripts, credentials or customer data into status files. Markdown rules do not technically constrain a malicious or noncompliant agent.

Existing acceptance criteria and project documentation remain canonical. If a small project has no decision/spec/backlog document, put only the necessary criteria and decisions in the checkpoint; migrate durable material when a real canonical home is established. Mark superseded choices so they do not become competing rules.

## Efficiency

Normal continuation reads project instructions, one checkpoint, and the linked criteria/affected files. It does not load archives or all skill references. A 1,200-word checkpoint target is advisory: do not truncate unresolved facts to satisfy it. The history budget is about five meaningful milestones; old resolved details can move to an existing archive with usable links. No universal time/token reduction is claimed from word counts alone.

## Compatibility research

Consulted official sources on 2026-11-02. Platform behavior is version/settings dependent:

- [Agent Skills specification](https://agentskills.io/specification): SKILL.md frontmatter, matching directory name, optional scripts/references/assets, progressive disclosure. The package uses portable name, description and license frontmatter.
- [Claude Code skills](https://code.claude.com/docs/en/skills): direct skill directories and invocation. Plugin namespacing differs from direct installation.
- [Claude project memory](https://code.claude.com/docs/en/memory): direct AGENTS.md support depends on version, settings and CLAUDE.md presence; an @AGENTS.md import is a compatibility route. Verify actual loading instead of changing global defaults.
- [Codex skills](https://developers.openai.com/codex/skills/): repository/user .agents/skills discovery and product-specific agents/openai.yaml metadata.
- [Codex project instructions](https://developers.openai.com/codex/guides/agents-md/): applicable scopes, overrides and discovery. A root file is not the only possible instruction owner.
- [Claude plugin overview](https://code.claude.com/docs/en/plugins) and [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces): separate packaging and catalog; no vendor tool integration is required to ship a skill.

These sources support packaging/loading mechanisms, not guaranteed handoff accuracy. Actual model compliance and operational savings require repeated real trials. Ordinary chat uploads provide a snapshot unless live filesystem tools are available.
