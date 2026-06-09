# Plan — Phase 18: e2e-review remediation (verified findings)

**Risk Grade**: L3 (public init surface + client decision path + CI privileges)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Target**: confirmed findings from the external e2e review, after ground-truth triage.
**Cycle scope**: the verified, high-value, low-risk set below. False positives and
already-triaged/won't-fix items are explicitly recorded — not silently actioned.

## Triage outcome (verified against the code)
- **False positives (no action):** H-4/H-5 (circuit breaker + 5xx ARE tested in
  `test_client_circuit_breaker.py`), M-7 (`__version__`/pyproject drift is guarded by
  `test_version_consistency.py`).
- **Won't-fix, per maintainer steer + prior triage:** M-8 (keep AGT `==4.0.0` for
  consistency with the AGT repo's released version), H-7 (keep gitleaks working-tree
  `--no-git` scan), M-4 (`policy_version_sha256` is an external `qortara_protocol` field),
  M-5 (pre-1.0 config removal, no deprecation cycle needed), M-2 (None-for-required is
  internal-only construction), M-1/M-10/M-13 (minor DX/coverage/efficiency).
- **FIX this cycle:** C-1, C-2, H-1, H-2, H-3, H-6, M-3, M-9, M-11, M-12.

## Promise (Definition of Done)

### D1 — Vision
The two decision clients share a typed contract and a single init guard; the decision
path reports honest failure rationales; the patch lifecycle is concurrency-safe and
symmetric; CI runs least-privilege with a pinned governance tool; the observability
callback is covered.

### D2 — Code
1. **C-2** — new `DecisionClient(typing.Protocol)` (`decide`, `close`, `require_reachable`,
   `submit_evidence`, `health`, `blocking_io`). Type `apply_patches`, `AdapterRegistry`,
   the wrapper factories, and `FrameworkAdapter.apply` against it; drop the
   `# type: ignore[arg-type]` in `init_agt`. `SidecarClient`/`AgtDecisionClient` satisfy it
   structurally (no inheritance change).
2. **C-1** — unify the re-init guard. `_InitFingerprint` becomes `(mode, params)` where
   `init()` → `("sidecar", endpoint/key/policy_mode)` and `init_agt()` →
   `("agt", agent_id/allowed_tools/aliases/policy_mode)`. Both: identical args ⇒ no-op
   (idempotent); different args ⇒ one clean `RuntimeError`. `init_agt` stores the active
   adapter (`_AGT_ADAPTER`) and returns it on idempotent re-call; `_unpatch_and_reset`
   clears both globals.
3. **H-3** — `SidecarClient.decide` distinguishes: `>=500` → "sidecar 5xx: N"; `>=400` →
   "sidecar client error: N (deny-closed)"; connection/timeout (`httpx.RequestError`) →
   "unreachable"; malformed 2xx → existing deny. (Stop folding 4xx into "unreachable".)
4. **H-1** — module `threading.Lock` in `registry.py` around `apply_patches`/`unpatch_all`.
5. **H-2** — make `langgraph_patches.unpatch` symmetric (restore both `invoke`/`ainvoke`
   the same way).
6. **M-3** — `require_compatible_protocol`/`_major` reject `None`/empty `peer_version` with
   a clear `QortaraProtocolMismatch` instead of an opaque `AttributeError`.

### D3 — Governance / CI
7. **M-11** — add `permissions: contents: read` to `ci.yml`.
8. **M-12** — pin `qor-logic==0.106.0` in `compliance.yml` (HARD-gate tool).
9. Ledger GATE + SEAL; this plan + the triage recorded.

### D4 — Empirical
- `test_init_agt_idempotent` — `init_agt` twice same args ⇒ no-op + same adapter; different
  args ⇒ RuntimeError; `init` after `init_agt` ⇒ clean RuntimeError; `unpatch_all` allows re-init.
- `test_decision_client_protocol` — `SidecarClient` and `AgtDecisionClient` both
  `isinstance(..., DecisionClient)` (runtime-checkable Protocol).
- `test_client_4xx_distinct_rationale` — a 401/403 yields a "client error" deny rationale
  (not "unreachable"), still deny-closed.
- `test_callback_emits_observe_evidence` / `_no_context_no_emit` / `_never_raises` —
  `QortaraCallbackHandler` coverage.
- `test_require_compatible_protocol_rejects_none` — None/empty peer raises cleanly.
- conftest `_unpatch_after` also resets `_ctx_var` (M-9) — verified by suite isolation.

## Section 4 Razor
One Protocol + one lock + a fingerprint reshape + rationale branch + CI YAML. No new deps.

## Blast radius
Protocol is structural — `SidecarClient`/`AgtDecisionClient` unchanged at runtime; only
annotations + the dropped `type: ignore`. Fingerprint reshape changes internal state only;
`init()` public behavior preserved (covered by `test_init_idempotent.py`). 4xx rationale:
no test asserts the old string (grep-verified). Lock is uncontended at startup. CI changes
are privilege-narrowing + a version pin.

## Review Boundary
Commit + push to PR #13. NO tag, NO PyPI. No AI footer.
