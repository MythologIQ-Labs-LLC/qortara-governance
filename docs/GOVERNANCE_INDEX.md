# Governance Index

**Last Reviewed**: 2026-06-10 (Phase 23 / governance-doc validation: SYSTEM_STATE, FEATURE_INDEX, CHANGELOG re-synced to ledger #54)

A single authoritative map of every governance artifact in this project, organized
into six freshness tiers with explicit drift contracts. A stale entry here is
itself a Tier 1 drift bug, so the index is self-policing. See
`qor/references/doctrine-governance-index.md` for the model and contracts.

## Tier 1 — Canonical Source

MUST be current at every cycle close. Drift signal: wrong version / wrong state / missing recent entries.

| Artifact | Path | Freshness marker |
|----------|------|------------------|
| Meta Ledger | `docs/META_LEDGER.md` | latest sealed entry |
| System State | `docs/SYSTEM_STATE.md` | latest phase snapshot |
| Concept | `docs/CONCEPT.md` | stable |
| Architecture Plan | `docs/ARCHITECTURE_PLAN.md` | stable |
| Backlog | `docs/BACKLOG.md` | open items current |
| Feature Index | `docs/FEATURE_INDEX.md` | every feature has a test |
| Changelog | `packages/qortara-governance-langchain/CHANGELOG.md` | latest release stamped |
| README | `README.md` | badges current |

## Tier 2 — Doctrine & Policy

Stable; changes are explicit doctrine events. Drift signal: rules contradict each other or operator memory.

| Artifact | Path |
|----------|------|
| Code of Conduct | `CODE_OF_CONDUCT.md` |
| Contributing | `CONTRIBUTING.md` |
| Security Policy | `SECURITY.md` |
| Threat Model | `docs/security/THREAT-MODEL.md` |
| ADR 0001 — AGT foundation vendoring | `docs/adr/0001-agt-foundation-vendoring.md` |
| AGT Component Map | `docs/architecture/AGT-COMPONENT-MAP.md` |
| Architecture Boundaries (public/hosted/Azure) | `docs/ARCHITECTURE-BOUNDARIES.md` |
| Evidence Event Schema | `docs/evidence-schema.md` |

## Tier 3 — Active Initiative

Live until close; ages out at substantiate. Drift signal: shipped feature still tracked as pending.

| Artifact | Path | Opened |
|----------|------|--------|
| Genesis session | `.qor/session/` | 2026-06-09 |

## Tier 4 — Per-Plan Artifact

Live for plan duration; archived at substantiate. Drift signal: plan shipped but artifact still presents as open.

| Artifact | Path | Plan |
|----------|------|------|
| Sealed per-phase plans | `docs/plan-qor-phase01..23-*.md` | one per sealed phase (historical; their ledger SEAL entry is canonical) |

## Tier 5 — Reference Material

Informational, slow-drift. Drift signal: factual claims diverge from current code.

| Artifact | Path |
|----------|------|
| Compatibility Matrix (CI-tested) | `docs/COMPATIBILITY.md` |
| AxonFlow comparative research | `docs/research-brief-axonflow-2026-06-09.md` |
| Deep-audit red-team brief | `docs/research-brief-deep-audit-redteam-2026-06-09.md` |
| Docs-alignment research brief | `docs/research-brief-docs-alignment-2026-06-09.md` |
| B5 dispatch-evidence ideation + research | `docs/ideation-b5-dispatch-evidence-emission.md`, `docs/research-brief-b5-dispatch-evidence-emission-2026-06-09.md` |

## Tier 6 — Archived

Frozen historical record. Drift signal: none (frozen).

| Archive | Path |
|---------|------|
| _none yet_ | — |

## How to add a governance artifact

1. Create the file in the same commit that registers it here.
2. Add a row to the tier whose freshness contract matches the file's lifecycle.
3. Refresh **Last Reviewed** above.

## How to retire a governance artifact

1. Move the file to the Tier 6 archive path.
2. Move its row from its live tier to Tier 6 (or delete it if superseded).
3. Refresh **Last Reviewed** above.
