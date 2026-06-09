# Plan: ADR-0001 Increment A — pivot to extend-on-AGT (foundation)

**change_class**: feature

**doc_tier**: system

**originating_remediation**: ADR-0001 (depend on agent-governance-toolkit[full]; do not vendor; do not modify AGT internals)

**terms_introduced**:
- term: AGT dependency probe
  home: packages/qortara-governance-langchain/src/qortara_governance/agt.py

**boundaries**:
- limitations: This increment establishes the AGT dependency + repositions the project; it does NOT rewire the live enforcement path onto AGT's engine (that is Increment B, L3). After this increment the SDK still requires an external sidecar endpoint until B lands.
- non_goals: No change to `BaseTool.invoke` decision logic; no `qortara_protocol` removal; no AGT internal modification.
- exclusions: The dispatch-patch re-base + protocol reconcile are Increment B.

## Open Questions

None. `agent-governance-toolkit[full]==4.0.0` resolves on Windows (verified via `uv pip install --dry-run`: 48 packages, pure-Python, no Rust build). Published components: `-core`, `-cli`, `-integrations`, `-protocols`.

## Phase 1: Declare the AGT dependency + a justified probe

### Affected Files

- `packages/qortara-governance-langchain/tests/test_agt_dependency.py` (NEW) — assert AGT is installed and its version resolves (proves the dependency loads).
- `packages/qortara-governance-langchain/src/qortara_governance/agt.py` (NEW) — `agt_version() -> str | None` and `agt_available() -> bool` via `importlib.metadata` (minimal, import-path-agnostic; foundation for Increment B's engine wiring).
- `packages/qortara-governance-langchain/pyproject.toml` — add `agent-governance-toolkit[full]==4.0.0` to `dependencies`.

### Changes

`agt.py` reads `importlib.metadata.version("agent-governance-toolkit")`; `agt_available()` returns False on `PackageNotFoundError` rather than raising. This justifies the dependency (used + tested) without guessing AGT's import API, which Increment B will study.

### Unit Tests

- `test_agt_dependency.py`: `test_agt_is_available` (`agt_available()` is True in the synced env), `test_agt_version_resolves` (`agt_version()` returns a non-empty string equal to the installed metadata version).

## Phase 2: Retire the S1 sidecar scaffold

### Affected Files

- `packages/qortara-governance-sidecar/` (DELETE) — the from-scratch evaluator/policy/app/auth built earlier this session; superseded by AGT (ADR-0001). Removing the workspace member returns the SDK to its pre-S1 "external endpoint required" state until Increment B wires AGT.
- `docs/FEATURE_INDEX.md` — remove the four sidecar rows (FX-sidecar-evaluator/-policy/-app/-auth); update coverage counts.
- `docs/BACKLOG.md` — reframe S1/S2: foundation now provided by the AGT dependency (Increment B); scaffold retired.

### Unit Tests

None — deletion + doc reconciliation. SDK tests do not depend on the sidecar package (they monkeypatch `SidecarClient.decide`); `uv run pytest` for the langchain package must stay green after removal (the verification).

## Phase 3: Reposition the project as an AGT extension

### Affected Files

- `docs/CONCEPT.md` — Why/anti-goals reframed from "independent alternative" to "extends AGT (full capability) + adds a bypass-proof dispatch hook + Azure upstream."
- `docs/ARCHITECTURE_PLAN.md` — add the AGT-dependency layer to the target architecture; note S1 retired; mark the enforcement re-base as Increment B.
- `packages/qortara-governance-langchain/README.md` — positioning lines: built on AGT, closes #73 on top of it.
- `README.md` (root) — "What this is" gains a one-line "Built on Microsoft AGT" note.

### Unit Tests

None — documentation. Validation is `qor-logic governance-health` (no placeholder markers; artifacts well-formed).

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-agt-dependency | NEW | packages/qortara-governance-langchain/tests/test_agt_dependency.py | `agt_available()` True and `agt_version()` equals installed `agent-governance-toolkit` metadata version |
| FX-sidecar-evaluator | n/a-justified | (removed) | S1 scaffold retired per ADR-0001 (superseded by AGT dependency) |
| FX-sidecar-policy | n/a-justified | (removed) | S1 scaffold retired per ADR-0001 |
| FX-sidecar-app | n/a-justified | (removed) | S1 scaffold retired per ADR-0001 |
| FX-sidecar-auth | n/a-justified | (removed) | S2 scaffold retired per ADR-0001 |

## Definition of Done

### Deliverable: agt-foundation-pivot

- **D1**: The project depends on AGT and is documented as an AGT extension; the duplicative S1 scaffold is gone.
- **D2**: `agent-governance-toolkit[full]==4.0.0` in pyproject; `agt.py` probe; `packages/qortara-governance-sidecar/` removed.
- **D3**: META_LEDGER GATE+SEAL; FEATURE_INDEX reconciled; BACKLOG S1/S2 reframed; GOVERNANCE_INDEX updated.
- **D4**: `test_agt_dependency.py` passes; full langchain suite stays green after sidecar removal; governance-health clean.

## CI Commands

- `uv sync --all-extras` — install AGT + drop the removed member.
- `uv run --package qortara-governance-langchain pytest` — full SDK suite incl. the AGT probe test.
- `uv tool run ruff check .` — lint.
- `qor-logic governance-health --profile skill-entry` — doc artifact health.

## Implementation amendments (2026-06-09, recorded at seal)

Two facts surfaced during implementation that amend Phase 1 as audited; both re-verified before seal:

1. **Dependency spec: `[full]` → library components.** `agent-governance-toolkit[full]` pulls `-cli` (operator tool, Python ≥3.11). The SDK depends on the library components instead: `agent-governance-toolkit-{core,protocols,integrations}==4.0.0` — full library capability, no CLI. The `agt.py` probe anchors on `agent-governance-toolkit-core`.
2. **Python floor 3.10 → 3.11 (operator-approved compat decision).** AGT 4.0.0 (incl. `-core`) requires Python ≥3.11. To adopt AGT, `requires-python` was raised to `>=3.11`, the 3.10 classifier removed, and CI matrix narrowed to 3.11–3.13. Recorded in META_LEDGER Phase 07; supersedes the project's prior 3.10 support.

Audit caveat: the Phase-07 audit's "AGT resolvability verified (dry-run)" was based on an isolated `--dry-run` against the active 3.11 interpreter; it did not exercise the workspace 3.10 floor, so the AGT≥3.11 constraint was missed until full `uv sync`. See AUDIT_REPORT-phase07 addendum.
