# Plan: B4 — Authoring the Beta threat model

**change_class**: feature

**doc_tier**: system

**terms_introduced**:
- term: Trust boundary
  home: docs/security/THREAT-MODEL.md
- term: Cooperative process
  home: docs/security/THREAT-MODEL.md

**boundaries**:
- limitations: The threat model documents the Beta enforcement boundary; it does not certify the implementation against each threat (mitigations name the controls, some of which are themselves backlog items, e.g. S1/S2).
- non_goals: Not a formal STRIDE/LINDDUN certification; not a pen-test report.
- exclusions: Post-Beta surfaces (Qortara Cloud federation, confidential computing, hardware attestation) are out of scope.

## Open Questions

None. Threat inventory is taken from the Beta roadmap §11.1 (16 enumerated threats) and grounded in the five-layer architecture (adapter → decision client → sidecar → policy pack → Cloud).

## Phase 1: Author docs/security/THREAT-MODEL.md

### Affected Files

- `docs/security/THREAT-MODEL.md` (NEW) — STRIDE-organized threat model: assets, trust boundaries, the 16 roadmap threats with mitigation + residual-risk + status (mitigated / partial / backlog), and an explicit bypass model.
- `docs/GOVERNANCE_INDEX.md` — register the threat model under Tier 2 (Doctrine & Policy).

### Changes

1. Write THREAT-MODEL.md: assets, trust boundaries (the cooperative in-process boundary, the loopback sidecar boundary, the hosted boundary), threat table for all 16 §11.1 threats, and the honest bypass model from roadmap §7.3.
2. Register the doc in GOVERNANCE_INDEX Tier 2 and bump **Last Reviewed**.

### Unit Tests

None — documentation deliverable. Validation is structural (governance-health) and review-based, not behavioral. No `src/` touched, so no functional test is owed (Feature Inventory empty, exempt per qor-plan/qor-audit doc-only rule).

## Feature Inventory Touches

_Empty — this plan touches only docs/governance._

## Definition of Done

### Deliverable: threat-model

- **D1**: A reader can identify what the SDK protects, the trust boundaries, and what it explicitly does not defend against.
- **D2**: `docs/security/THREAT-MODEL.md` exists and covers all 16 roadmap §11.1 threats + the §7.3 bypass model.
- **D3**: GOVERNANCE_INDEX registers it (Tier 2); META_LEDGER seal; BACKLOG B4 closed.
- **D4.d**: Waiver — documentation deliverable has no runtime behavior to assert. **Validation**: `qor-logic governance-health` passes (no placeholder markers; artifact well-formed). **Follow-up phase**: none required.

## CI Commands

- `qor-logic governance-health --profile skill-entry` — confirms the new doc and index are well-formed (no unresolved placeholder markers).
