# Plan — Phase 22: live-agent end-to-end conformance (B1-followup) + init-time exceptions (B2-followup)

**Risk Grade**: L3 (init-time reachability path + new public exceptions + agent runtime coverage)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Base**: `main` (`fb4a152`).
**Target**: BACKLOG B1-followup (live-LLM agent end-to-end test) + B2-followup (§8.3 exceptions).

## Research findings (verified, no new dep)
- `langgraph.prebuilt.create_react_agent` is available; `langchain_core.GenericFakeChatModel` is
  available. A deterministic agent end-to-end test is feasible with the existing optional
  `[langgraph]` extra — **no `langchain` test-dep needed**.
- `require_reachable()` (`client.py:171-174`) collapses every init-time failure (401/403 auth,
  timeout, connection error, non-2xx) into a single generic `QortaraSidecarUnavailable` via the
  bool `health()`. Auth + timeout are distinct, diagnosable conditions → genuine raise sites.
- `QortaraPolicyInvalid` / `QortaraDecisionMalformed` have **no** clean Beta raise site: the
  dispatch path is fail-closed (a malformed/invalid decision returns a *deny decision*, it does not
  raise — Phase 13 SEC-03). Wiring them would contradict deny-closed → deferred with rationale.

## Promise (Definition of Done)

### D1 — Vision
The modern agent entry point (`create_react_agent`) is *empirically proven* governed end-to-end,
and an init-time auth/timeout failure fails fast with a typed, diagnosable error.

### D2 — Code / tests
1. **B1-followup**: new conformance test driving a real `create_react_agent` graph with a minimal
   deterministic fake tool-calling chat model (emits one tool call) + a tool. Assert a **denied**
   tool is blocked through the agent runtime (`QortaraPolicyDenied`; body never runs), proving the
   agent's internal `ToolNode`/`run` dispatch is governed. No new dependency.
2. **B2-followup**: add `QortaraTimeout(QortaraSidecarUnavailable)` and
   `QortaraAuthenticationError(QortaraError)` to `exceptions.py` (frozen `__all__` + package export).
   Refactor `SidecarClient.require_reachable()` to distinguish: a `health` probe returning **401/403**
   → `QortaraAuthenticationError` (clear "credential rejected"); a **timeout** → `QortaraTimeout`; a
   connection error / other non-2xx → existing `QortaraSidecarUnavailable` (unchanged). `health()`
   keeps its bool contract; the distinction is made in `require_reachable` via an internal status
   probe so the breaker/health semantics are untouched. `QortaraTimeout` subclasses
   `QortaraSidecarUnavailable` (back-compat: `except QortaraSidecarUnavailable` still catches it).

### D3 — Governance
Ledger GATE + SEAL; BACKLOG B1-followup → done, B2-followup → done-with-rationale (2 of 4 wired);
exceptions doc note. Carry no uncommitted artifacts (clean branch off main).

### D4 — Empirical
- `test_create_react_agent_denied_tool_blocked` — a denied tool driven via `create_react_agent`
  raises `QortaraPolicyDenied`; the tool body never runs.
- `test_require_reachable_401_raises_auth_error` — a sidecar health 401 → `QortaraAuthenticationError`.
- `test_require_reachable_timeout_raises_timeout` — a health timeout → `QortaraTimeout` (and it is a
  `QortaraSidecarUnavailable` subclass).
- `test_require_reachable_connection_error_still_unavailable` — a connection error → unchanged
  `QortaraSidecarUnavailable` (regression).

## Non-goals (deferred, with rationale)
- `QortaraPolicyInvalid` / `QortaraDecisionMalformed` — dispatch path is fail-closed (deny, not
  raise); no Beta raise site. They gain sites only in a future policy-validation / remote-daemon
  error-surfacing path. Documented in BACKLOG.
- Live multi-turn / streaming agent runs, real LLM matrix — post-Beta.
- Standing residuals unchanged.

## Section 4 Razor
One conformance test (existing deps) + two exception classes + a `require_reachable` refactor that
keeps `health()`'s bool contract. No new dependency, no enforcement-path change.

## Blast radius
B1 test is additive. B2: `require_reachable` raises a *more specific* error for 401/403/timeout; the
generic connection-error case is unchanged (regression-tested). `QortaraTimeout` subclasses
`QortaraSidecarUnavailable` so existing handlers still catch it; `QortaraAuthenticationError` is a
new sibling (a 401 at init now surfaces as auth, not "unavailable" — a diagnostic improvement,
documented). Additive public exception names (minor-compatible).

## Review Boundary
Commit + push + open a new PR off `main`; track CI; hand off. NO tag, NO PyPI, NO merge. No AI footer.
