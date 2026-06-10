# Research Brief — Dispatch-Path Evidence Emission (B5)

**Date**: 2026-06-09
**Analyst**: The Qor-logic Analyst (research mode)
**Target**: feasibility of emitting decision + execution evidence from the enforcement dispatch
path (`BaseTool.run`/`.arun`, `ToolNode`), per ideation `dispatch-path-evidence-emission`.
**Scope**: the three blocking unknowns A4 (sink contract), A6 (execution-evidence capture without
disturbing the bypass-resistant chokepoint), and the per-dispatch perf budget. All findings cite
current `main` (`166a688`) source.

---

## Executive Summary
All three blocking unknowns resolve **favorably**. The decision is made *before* `original(...)` in
both wrappers, so capturing the run result in a `try/finally` around the existing call adds **no
bypass surface** (A6 ✅). A best-effort, never-raises sink contract **already exists** as
`DecisionClient.submit_evidence` (implemented by `SidecarClient`, no-op on `AgtDecisionClient`), and
OTel emission infra already exists in `otel.py` (A4 ✅). Perf is opt-in by construction: **zero
overhead when no sink is configured**. No DRIFT vs the ideation. Recommend proceeding to `/qor-plan`
with Option A (opt-in `EvidenceSink`), decision-evidence + execution-evidence both in scope.

## Findings

### F1 — A6: execution-evidence capture is safe (no chokepoint disturbance)
- **Sync wrapper** (`patches/tool_patches.py:137-139`): `_decide_or_raise(...)` runs (line 138),
  **then** `return original(self, *args, **kwargs)` (line 139).
- **Async wrapper** (`patches/tool_patches.py:151-160`): decision runs (line 153-159), **then**
  `return await original(...)` (line 160).
- The gate fires *before* `original(...)`. Wrapping line 139 / 160 in `try/except/finally` to capture
  `executed`/`errored` + duration measures the call that already happens — it does **not** move the
  decision point, does not add an alternate entry, and does not change the `run`/`arun` funnel
  (GAP-SEC-08). **The Phase-8 escalation trigger ("execution-evidence wrapping weakens
  bypass-resistance") does not fire.** Execution-evidence is SAFE to include.

### F2 — A4: the sink contract already exists; only the in-process sink is missing
- `DecisionClient` Protocol declares `submit_evidence(records: list[EvidenceRecord]) -> None`
  (`decision_client.py:36`).
- `SidecarClient.submit_evidence` (`client.py:149-158`) is a **working best-effort sink**: POSTs to
  `/v0.1/evidence`, breaker-gated, catches `httpx.RequestError`, **never raises**.
- `AgtDecisionClient.submit_evidence` (`agt_engine.py:119`) is a **no-op** — the in-process default
  has no sink. **This is the sole gap.**
- **Implication**: the existing `submit_evidence(list[EvidenceRecord])` signature is a ready-made
  `EvidenceSink` contract. A sidecar deployment already emits "for free"; the in-process path needs a
  pluggable local/OTel/callback sink injected at init.

### F3 — OTel sink is feasible with existing infra
- `otel.py` already provides `current_trace_context()` (W3C traceparent, `otel.py:19-33`) and
  `tag_evidence_id()` (span attribute, `otel.py:36-47`) — both **guarded** (`_HAS_OTEL`) and
  best-effort. `opentelemetry-api>=1.30` is already a runtime dependency (`pyproject.toml:22`).
- An OTel `EvidenceSink` can emit a span event + `tag_evidence_id(record.evidence_id)`; it is a
  **sink implementation under Option A**, not a competing design (confirms ideation Option D folds in).

### F4 — Best-effort emission precedent already exists
- `QortaraCallbackHandler._emit` (`callback.py:84-87`) wraps `self._client.submit_evidence([record])`
  in `try/except Exception: pass` — never blocks, never raises into the caller. Dispatch-path
  emission MUST mirror this (ideation forbidden-interpretation: "an emission failure must not raise
  into the caller or alter the decision").

### F5 — Request + decision are available but currently discarded
- `_decide_or_raise` (`tool_patches.py:114-126`) builds `request = build_tool_action(...)`
  (line 125) and obtains the decision via `client.decide(request, tool_input)` (line 126), then
  **discards both** after `enforce_decision`. Emission needs them surfaced — e.g., `_decide_or_raise`
  returns `(request, decision)`, or the decision-evidence emit happens inside it. **A real
  structural change the plan must account for** (not a blocker — the data exists at the gate).

### F6 — Perf budget
- **No sink (default)** → zero evidence work; the only added cost is a `None` check. Confirms the
  opt-in "zero overhead" success criterion.
- **With a sink**: decision-evidence = 1 `uuid4` + 1 `EvidenceRecord` build + 1 best-effort sink call
  (deny path only — see F7); execution-evidence = `time.perf_counter` delta + `try/finally` + 1 build
  + 1 sink call per permitted run.
- **Async + blocking sink**: `SidecarClient.submit_evidence` is blocking `httpx`. On the async path it
  MUST be offloaded via `asyncio.to_thread`, reusing the existing `blocking_io` pattern
  (`tool_patches.py:153-157`); otherwise it stalls the event loop.

### F7 — Builder semantics constrain *which* event fires *where*
- `decision_evidence` (`evidence.py:62-79`) accepts only terminal verdicts (deny/exempt/observe) and
  **raises ValueError** otherwise. Therefore: at the gate, emit `decision_evidence` only for **deny**
  (the terminal block — no run follows). For an **allow**, the *execution* event (post-run) carries
  the allow decision via `execution_evidence`. This matches the Phase-20 builder design exactly — no
  new mapping needed.

## Blueprint / Ideation Alignment

| Ideation assumption | Source finding | Status |
|---|---|---|
| A1 builders are the right shape | F7 — terminal/non-terminal split maps cleanly to gate vs run | MATCH |
| A2 emission should be opt-in | F6 — zero overhead only when no sink; opt-in is the perf contract | MATCH |
| A3 best-effort never-raises is acceptable | F4 — existing callback precedent | MATCH |
| A4 in-process needs a pluggable sink | F2 — `submit_evidence` exists; AGT path is the no-op gap | CONFIRMED |
| A5 async reuses `asyncio.to_thread` | F6 — required for blocking sinks; pattern exists | CONFIRMED |
| A6 execution-evidence needs a deeper hook; may risk bypass | F1 — wrapping `original(...)` is safe; **escalation does not fire** | **RESOLVED (favorable)** |

No DRIFT detected against current `main`.

## Recommendations (for /qor-plan)
1. **`EvidenceSink` Protocol** = the existing `submit_evidence(list[EvidenceRecord]) -> None` shape
   (best-effort, never-raises). Inject at init: `init(..., evidence_sink=None)` /
   `init_agt(..., evidence_sink=None)`. **Default `None` → no emission (zero overhead).** Priority: HIGH.
2. **Decision-evidence at the gate**: emit `decision_evidence` on **deny** only (F7), best-effort,
   wrapped like `callback.py:84-87`. Surface `(request, decision)` from `_decide_or_raise` (F5). Priority: HIGH.
3. **Execution-evidence around `original(...)`**: `try/except/finally` with `time.perf_counter` →
   `execution_evidence(executed|errored, duration_ms)`, best-effort; async blocking sink via
   `asyncio.to_thread` (F1, F6). Priority: HIGH. **F1 clears the bypass-risk escalation.**
4. **Ship two sink impls**: (a) the existing `SidecarClient.submit_evidence` (already works), (b) a
   local OTel sink built on `otel.py` (F3). A JSONL/callback sink is optional. Priority: MEDIUM.
5. **Conformance** (the ideation `evidence_required` set): no-sink=zero-emission; never-raises with a
   throwing sink; deny→decision event; executed/errored→execution event + duration; fail-closed
   unchanged with a throwing sink; async non-blocking. Priority: HIGH.

## Updated Knowledge
Doctrine note (for `docs/SHADOW_GENOME.md` / evidence-schema): the dispatch-path emission point has
the request + decision in hand at `tool_patches.py:125-126` but discards them; any emission feature
must surface them rather than rebuild. The `submit_evidence` Protocol method is the canonical
best-effort sink contract — new sinks should match its "never raise into the caller" guarantee.

---
_Research complete. Findings advisory — implementation decisions remain with the Governor. Recommended next phase: **/qor-plan** (readiness upgraded from research_required → plan-ready; all blocking unknowns resolved favorably)._
