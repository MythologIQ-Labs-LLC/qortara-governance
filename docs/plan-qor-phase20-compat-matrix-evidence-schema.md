# Plan — Phase 20: CI-verified compatibility matrix (N4/B3) + evidence event schema (N5/B5, definitional)

**Risk Grade**: L3 (public compatibility claim + a new public contract surface)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Base**: stacked on `feat/qor-phase19-...` (PR #14, unmerged) → new stacked PR.
**Cycle scope**: N4 (full) + N5 (definitional only — emission deferred). No expansion.

## Research findings (verified this cycle)
- `langchain-core==0.3.0` **resolves** with the full stack, and `invoke`→`run` / `ainvoke`→`arun`
  **holds** there (so the Phase-15 hook has no enforcement gap across 0.3→1.4) — and the **full suite
  passes** on `langchain-core>=0.3,<0.4` + `langgraph<0.3`. The `>=0.3` floor is therefore *sound* but
  **CI-unverified** (CI runs only the resolved latest, 1.4.2). This is exactly B3's "unbounded claim".
- `qortara_protocol.EvidenceRecord` already carries **both** `decision` (ActionDecision) and
  `execution_result` (ExecutionResult ∈ executed/denied/approved/timed_out/errored/exempt/observed).
  The **dispatch path emits no evidence today** — only `callback.py` does (OBSERVE). Emitting from the
  hot dispatch path is a **behavior change** with design weight (perf; the in-process AGT client's
  `submit_evidence` is a no-op — nowhere to send it).

## Promise (Definition of Done)

### D1 — Vision
The compatibility claim is CI-enforced, not asserted; the evidence model has a documented,
tested contract that cleanly separates a *decision event* from an *execution event*.

### D2 — Code / CI
1. **N4 (B3)**: add a `compat` job to `ci.yml` that installs the **floor** (`langchain-core>=0.3,<0.4`
   + `langgraph>=0.2,<0.3`) on Python 3.11 and runs the full suite — proving the floor on every PR
   alongside the existing latest-resolved matrix. Add `docs/COMPATIBILITY.md` stating the tested matrix
   (Python 3.11/3.12/3.13 × langchain-core floor 0.3 → latest 1.x; langgraph 0.2 floor → latest);
   register it in `GOVERNANCE_INDEX.md`. README "Compatibility" line points to it. No dep-range change
   (the existing `>=0.3` is now verified, not widened).
2. **N5 (B5, definitional)**: new `evidence.py` encoding the **decision vs execution** separation
   *honestly*:
   - `decision_evidence(request, decision)` — for a **terminal gate verdict** only; maps
     deny→DENIED, exempt→EXEMPT, observe→OBSERVED, and **raises `ValueError`** for a non-terminal
     kind (allow / require_approval / transform) since those have no execution result at decision
     time (this refusal is the point — it forbids fabricating an outcome).
   - `execution_evidence(request, decision, result, *, duration_ms=0, result_payload_ref=None)` — for
     a **post-run** event (executed / errored / timed_out / approved / denied).
   Both share one internal record constructor. Refactor `callback.py`'s inline `EvidenceRecord` to call
   `decision_evidence(...)` (OBSERVE is a terminal observed state) so the builder is *used*, not
   speculative. `docs/evidence-schema.md` documents the two event types, the ExecutionResult taxonomy
   (decision-terminal vs execution), and field mapping. Export the two helpers.

### D3 — Governance
Ledger GATE + SEAL; BACKLOG [B3] done, [B5] partial; GOVERNANCE_INDEX updated; this plan recorded.

### D4 — Empirical
- CI `compat` job green on the floor (proves the matrix).
- `test_decision_evidence_terminal_verdicts` — deny→DENIED, exempt→EXEMPT, observe→OBSERVED;
  field mapping (tenant_id from request, decision passed through).
- `test_decision_evidence_rejects_non_terminal` — allow / require_approval raise `ValueError`.
- `test_execution_evidence_builder` — result + duration_ms + result_payload_ref mapped correctly.
- `test_callback_emits_observe_via_builder` — callback OBSERVE record still has
  `execution_result=OBSERVED` and `decision_kind=observe` (regression: same shape).

## Non-goals (deferred, with rationale)
- **Emitting decision-evidence from the dispatch path** — a hot-path behavior change; and the default
  in-process AGT client `submit_evidence` is a no-op (no sink). This needs a deliberate opt-in design
  (when to emit, perf budget, where it goes) — a future cycle / `/qor-ideate`, not a blind add.
- Widening or raising the dependency floor — `>=0.3` is verified sound; no change.
- Standing residuals (breaker half-open, policy_version_sha256, require_compatible_protocol wiring,
  live-LLM create_agent test, remote-daemon §8.3 exceptions) — unchanged.

## Section 4 Razor
One CI job; two doc files; one small builder module + a callback refactor to use it; tests. No
runtime dep change, no enforcement-path behavior change.

## Blast radius
CI: additive job. `evidence.py` builders are pure constructors (no IO, no hot-path call); callback
refactor preserves the existing emitted shape (covered by the existing + new callback test). Docs are
additive. No public API removed; builders are additive exports.

## Review Boundary
Commit + push + open a **stacked PR** (base = `feat/qor-phase19-...` so the diff is just N4/N5);
track CI to green; hand off for review. NO tag, NO PyPI, NO merge without explicit approval. No AI footer.
