# Plan: Phase 10 — documentation alignment remediation

**change_class**: feature

**doc_tier**: system

**originating_remediation**: research-brief-docs-alignment-2026-06-09.md (6 drift clusters)

**boundaries**:
- limitations: Documentation-only realignment to the post-pivot reality (AGT in-process; Phase 07–09). No code change.
- non_goals: No edits to historical artifacts (ADR-0001, AGT-COMPONENT-MAP, plan-qor-phase*, research-brief-*, META_LEDGER) — they are correct archaeology.
- exclusions: No new feature; the optional remote-daemon (SidecarClient) path is documented as optional, not deleted.

## Open Questions

None. The research brief enumerates the 6 drifts with file:line citations and the aligned/out-of-scope sets.

## Phase 1: Realign forward-facing authoritative docs

### Affected Files

- `docs/ARCHITECTURE_PLAN.md` — rewrite the body (file tree note, layered architecture, data flow, dependencies, known-gaps) to AGT-in-process; demote the sidecar/launcher/client to "optional remote-daemon mode." (DRIFT-1)
- `docs/SYSTEM_STATE.md` — refresh to Phase-09 reality: sidecar package removed; Python 3.11 floor; AGT enforcement wired; correct test counts (79 passed / 2 skipped); next-action updated. (DRIFT-2)
- `README.md` — Quickstart → `init_agt(agent_id, allowed_tools)` as the local path; keep `init()` documented as the remote-daemon path. (DRIFT-3)
- `packages/qortara-governance-langchain/README.md` — Quickstart/positioning → AGT-backed in-process; `init_agt()`. (DRIFT-3)
- `packages/qortara-governance-langchain/pyproject.toml` — description: drop "sidecar SDK"; reflect AGT-backed dispatch enforcement. (DRIFT-4)
- `docs/security/THREAT-MODEL.md` — re-scope around the in-process AGT decision boundary; mark sidecar threats (2,3) as remote-daemon-only. (DRIFT-5)
- `CONTRIBUTING.md`, `SECURITY.md` — reframe "sidecar HTTP client is the model" → "AGT-backed in-process enforcement; optional sidecar client for remote-daemon." (DRIFT-6)

### Changes

Each edit replaces stale sidecar-as-default framing with the AGT-in-process model, preserving the sidecar as an explicitly-optional remote-daemon path. No claim is added that isn't already true post-Phase-09.

### Unit Tests

None — documentation-only. No `src/` touched; Feature Inventory empty (exempt). Validation is `qor-logic governance-health` (artifact well-formedness) + internal-consistency review.

## Feature Inventory Touches

_Empty — docs/governance only._

## Definition of Done

### Deliverable: docs-alignment

- **D1**: Forward-facing docs describe the AGT-in-process reality; no authoritative doc still presents the retired local sidecar as the default.
- **D2**: The 8 listed files edited per the brief; historical artifacts untouched.
- **D3**: META_LEDGER GATE+SEAL; SYSTEM_STATE refreshed; research brief's drifts resolved.
- **D4.d**: Waiver — documentation deliverable; validation = `qor-logic governance-health` passes + a re-grep shows no stale sidecar-as-default framing in the 8 files. **Follow-up**: none.

## CI Commands

- `qor-logic governance-health --profile skill-entry` — artifact health.
- `uv run --package qortara-governance-langchain pytest packages/qortara-governance-langchain` — confirm docs edits didn't disturb code (regression guard).
