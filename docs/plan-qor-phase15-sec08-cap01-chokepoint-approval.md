# Plan — Phase 15: SEC-08 deep chokepoint (`run`/`arun`) + CAP-01 honest decision model

**Risk Grade**: L3 (relocates the enforcement chokepoint)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Target**: deferred red-team HIGH items GAP-SEC-08 + GAP-CAP-01 (brief: `docs/research-brief-deep-audit-redteam-2026-06-09.md`)
**Cycle scope**: SEC-08 + CAP-01 only. No expansion.

## Evidence (verified against langchain_core 1.4.2)
- `BaseTool.invoke()` → `self.run(tool_input, **kwargs)`; `BaseTool.ainvoke()` → `await self.arun(...)`.
  (`inspect.getsource(BaseTool.invoke)` / `.ainvoke`.)
- `BaseTool.__call__` does **not** exist (`'__call__' not in vars(BaseTool)`).
- Therefore patching only `invoke`/`ainvoke` leaves **direct `tool.run(...)`/`tool.arun(...)`
  ungoverned** (GAP-SEC-08). `run`/`arun` is the single funnel every public dispatch passes through.
- `AgtDecisionClient.decide` (`agt_engine.py:98-100`) returns **only ALLOW or DENY** — AGT's
  `check_violation` is binary. `REQUIRE_APPROVAL` is unreachable on the AGT path (GAP-CAP-01),
  yet README (`README.md:45,90-99`) presents a four-state model without qualifying the AGT plane.

## Why
- **SEC-08**: a real bypass — anyone (or any framework path) calling `tool.run(...)` directly
  skips policy entirely. The #73 thesis ("any path reaching dispatch is governed") is only true
  if we hook the actual funnel.
- **CAP-01**: docs imply the in-process AGT engine can emit `require_approval`; it cannot. The
  SDK's `enforce_decision` *does* route `require_approval` → `QortaraApprovalRequired` when a
  decision plane emits it (sidecar/hosted), so the code is correct — the docs overclaim for AGT.

## Promise (Definition of Done)

### D1 — Vision
The enforcement hook sits at the true dispatch funnel (`run`/`arun`), so every public entry point
(`invoke`/`ainvoke`/`run`/`arun`) is governed by a single decision; and the documented decision
model states honestly which decision plane produces which kinds.

### D2 — Code
1. **SEC-08**: `tool_patches.apply()` patches `BaseTool.run` + `BaseTool.arun` (instead of
   `invoke`/`ainvoke`). Wrappers become signature-agnostic pass-throughs
   (`def wrapper(self, *args, **kwargs)`; `tool_input = args[0] if args else kwargs.get("tool_input")`)
   so they match `run`'s rich signature and bind `tool_input` whether positional or keyword.
   Double-install guard + `unpatch` track `run`/`arun`. `invoke`/`ainvoke` remain unpatched and
   reach policy *through* `run`/`arun` (no double-decision). `_run`/`_arun` (per-subclass private
   impls) and direct-private-call bypass are documented as the cooperative-process boundary
   (THREAT-MODEL §5) — not patchable at the `BaseTool` class level.
2. **CAP-01**: no code change to the binary AGT mapping (ADR-0001 — don't modify/extend AGT
   semantics speculatively). Honest docs + boundary test only.

### D3 — Governance
README decision-model section qualified (AGT = allow/deny fail-closed; `require_approval` +
transform kinds = sidecar/hosted plane; SDK routes each correctly when received; `observe`
downgrades to log). Diagram `(local sidecar)` → in-process/sidecar; `BaseTool.invoke() ←
intercepted` → `BaseTool.run() (invoke/ainvoke/arun all funnel here)`. THREAT-MODEL note on the
`_run` private-call boundary. Ledger GATE + SEAL; brief SEC-08/CAP-01 marked RESOLVED.

### D4 — Empirical
- `test_direct_run_is_governed` — `tool.run(...)` under DENY raises and `_run` never executes
  (the SEC-08 bypass, now closed).
- `test_direct_arun_is_governed` — async equivalent.
- `test_invoke_still_governed_via_run` — regression: `tool.invoke(...)` still blocks under DENY.
- `test_run_arun_are_the_wrapped_methods` — `BaseTool.run`/`.arun` carry `__qortara_wrapped__`;
  `invoke`/`ainvoke` are untouched originals.
- Update `test_unpatch_byte_identical.py` + `test_tool_patches_rejects_double_install.py` to
  assert run/arun wrapping + byte-identical restore of run/arun.
- `test_agt_path_is_binary_allow_deny` — `AgtDecisionClient.decide` only ever yields ALLOW/DENY
  across allow + deny inputs (CAP-01 boundary, documents the limit explicitly).
- `test_sidecar_require_approval_routes_to_approval` — a scripted `REQUIRE_APPROVAL` decision
  flowing through the patched dispatch raises `QortaraApprovalRequired` (proves 4-state handling
  is real where the plane emits it).

## Section 4 Razor
No new module/dep/config. Moves one chokepoint deeper; deletes nothing the public relies on
behaviorally (invoke/ainvoke still work and are still governed). Docs-only for CAP-01.

## Blast radius
`run`/`arun` wrappers use pass-through `*args/**kwargs` → tolerant of langchain's rich `run`
signature. Behavioral contract for existing `.invoke()`-based tests unchanged (still governed).
Three patch-internals tests re-pointed from invoke→run assertions (they encoded the hook location,
not a behavioral contract). No public API change. CAP-01 is docs + tests only.

## Non-goals
- An in-process approval backend / making AGT emit `require_approval` (speculative; ADR-0001).
- `require_compatible_protocol` wiring, GAP-SEC-07, CI-01/02, DOC-01(rest), MED/LOW — deferred.

## Review Boundary
Commit + push to PR #13. NO tag, NO PyPI. No AI footer.
