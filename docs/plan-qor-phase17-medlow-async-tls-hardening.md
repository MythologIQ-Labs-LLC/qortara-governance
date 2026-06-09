# Plan — Phase 17: MED/LOW hardening — non-blocking async decisions + cleartext-credential warning

**Risk Grade**: L3 (async dispatch path + credential transport)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Target**: deferred red-team MED/LOW batch (brief line 31)
**Cycle scope**: the two MED items with clear, low-risk, correctness/security value. The
remaining MED/LOW items are explicitly deferred *with rationale* below — not silently dropped.

## Triage of the MED/LOW batch
| Item | Decision | Why |
|---|---|---|
| **blocking httpx in async wrapper** | **FIX** | Real correctness bug: `arun`/`ainvoke` run the *sync* `SidecarClient.decide` (blocking `httpx.Client.post`) inside the event loop. |
| **tenant_key cleartext over http** | **FIX** | Real security issue: the subscription-key header is sent in plaintext to a non-TLS, non-loopback endpoint with no signal. |
| breaker half-open / health-reset | **DEFER** | Current design (reset on any success; reset after cooldown) is acceptable and fail-closed; half-open probing is an enhancement, not a defect. |
| `policy_version_sha256` carries non-sha256 values | **DEFER (won't-fix)** | The field name is defined by the external `qortara_protocol` contract (ADR-0001 — we don't fork the protocol). Renaming is a protocol-breaking change outside this repo. |
| wrapper signature metadata loss | **DEFER (intentional)** | `functools.wraps` would set `__wrapped__ = original` — re-introducing exactly the bypass handle removed in GAP-SEC-07. We keep `__qualname__` only, on purpose. |

## Evidence (verified)
- `tool_patches._make_async_wrapper` / `langgraph_patches._make_async_wrapper` call the sync
  `_decide_or_raise` / `_decide_each` directly (`tool_patches.py:150-152`), and
  `SidecarClient.decide` does a blocking `self._client.post(...)` (`client.py:98`). In an async
  agent this blocks the event loop until the sidecar responds (up to the 10s timeout).
- `AgtDecisionClient` (the default in-process path) does **no** IO — blocking it in a thread
  would add a gratuitous thread hop.
- `SidecarClient.__init__` sets `Ocp-Apim-Subscription-Key: <tenant_key>` (`client.py:53-54`)
  with no scheme check; an `http://` non-loopback endpoint leaks the key in cleartext.

## Promise (Definition of Done)

### D1 — Vision
Governed async dispatch never blocks the event loop on a remote decision, and configuring a
credential against a plaintext transport is loud, not silent.

### D2 — Code
1. **MED-async**: introduce a `blocking_io: bool` class attribute on decision clients —
   `SidecarClient.blocking_io = True` (does network IO), `AgtDecisionClient.blocking_io = False`
   (in-process). Both async wrappers run the decision via `await asyncio.to_thread(...)` **iff**
   `getattr(client, "blocking_io", True)` (default True = safe for unknown clients), else inline.
   `asyncio.to_thread` propagates the current `contextvars.Context`, so `get_context()` still
   resolves inside the thread. The decision still runs *before* the original method (a DENY/
   approval raises before the tool body). No change to the sync path.
2. **MED-tls**: add `QortaraInsecureTransportWarning(UserWarning)` (exceptions.py + export).
   `SidecarClient.__init__` emits it once when a `tenant_key` is set AND the endpoint scheme is
   `http` (not `https`) AND the host is not loopback (`localhost`/`127.0.0.1`/`::1`). The client
   still works (warn, don't break); operators can escalate the category to an error.

### D3 — Governance
Ledger GATE + SEAL; brief MED/LOW row updated (two FIXED, rest DEFERRED with rationale);
README/THREAT-MODEL note the cleartext-credential warning + async non-blocking behavior if a
natural spot exists.

### D4 — Empirical
- `test_async_sidecar_decision_runs_in_thread` — with a `blocking_io=True` client whose `decide`
  records its thread, an `arun` dispatch runs `decide` off the calling thread (non-blocking).
- `test_async_inprocess_decision_runs_inline` — `AgtDecisionClient` (`blocking_io=False`) async
  dispatch runs `decide` on the calling thread (no gratuitous hop) and still enforces.
- `test_async_deny_still_blocks_via_thread` — DENY through the threaded async path raises
  `QortaraPolicyDenied` and the tool body never runs.
- `test_tenant_key_http_nonloopback_warns` — `SidecarClient("http://api.example.com", "k")`
  warns `QortaraInsecureTransportWarning`.
- `test_tenant_key_https_no_warn` / `test_tenant_key_http_loopback_no_warn` /
  `test_no_tenant_key_no_warn` — negative cases.

## Section 4 Razor
No new module/dep. One class attr + a stdlib `asyncio.to_thread` branch; one warning class +
a scheme check. No new config.

## Blast radius
Async path: behavior-preserving (same decision, same raise semantics) — only *where* the sync
decision runs (thread vs inline) changes, gated by an explicit, default-safe flag. Sync path
untouched. `FakeClient` (test) inherits `SidecarClient.blocking_io=True` → exercised by the
threaded branch. TLS warning is additive (warn-only); a new public warning class is minor-compatible.

## Non-goals
Breaker half-open, protocol field rename, `functools.wraps` (see triage). `require_compatible_protocol`
wiring remains deferred (sidecar health-version field).

## Review Boundary
Commit + push to PR #13. NO tag, NO PyPI. No AI footer.
