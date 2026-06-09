# Research Brief — Deep-Audit Red Team

**Date**: 2026-06-09
**Analyst**: The Qor-logic Governor (deep-audit bundle, 4 parallel red-team subagents)
**Target**: `qortara-governance-langchain` enforcement SDK (post-AGT-pivot) + CI + docs
**Scope**: adversarial production-gap audit — enforcement bypass, fail-open, correctness, test adequacy, config/supply-chain, doc drift.

---

## Executive Summary

Four adversarial subagents (security, code-correctness, test-adequacy, config/supply-chain) found **~30 findings**: after dedup + verification, **6 confirmed CRITICAL/GA-blocking**, ~8 HIGH, the rest MED/LOW, **1 CRITICAL refuted**. The dominant theme: the AGT-pivot work (sealed this session) has **fail-open seams and a largely-inert arg-safety claim** that the constructive audit cycles + conformance tests did not catch (the tests used a tool name AGT happens to recognize). This cycle remediates the confirmed CRITICAL bypass/fail-open set; HIGH/MED design, CI, and doc items are deferred to a tracked follow-up.

## Verification status (Phase 3)

| GAP | Severity | Status | Evidence |
|---|---|---|---|
| GAP-SEC-05 arg-safety inert for real tool names | CRITICAL | **CONFIRMED** | AGT `policy_engine.check_violation` arg-checks key on 8 hardcoded names (`run_command`, `database_query`, `write_file`, …); LangChain tools rarely match. Conformance used `database_query` → false green. |
| GAP-SEC-06 `ToolNode.ainvoke` unpatched | CRITICAL | **CONFIRMED** | `langgraph_patches.apply` patches only `invoke` (`originals={"invoke":…}`); async LangGraph ungoverned. |
| GAP-SEC-02 non-DENY verdicts allow | CRITICAL | **CONFIRMED** | `tool_patches.py:39-50` raises only on DENY/REQUIRE_APPROVAL; DOWNGRADE/REDACT/SANDBOX/OBSERVE/garbage fall through to run. |
| GAP-SEC-03 malformed 2xx fail-open | CRITICAL | **CONFIRMED** | `client.py:103-108` catches only `(RequestError, HTTPStatusError)`; `ActionDecision.model_validate` raises `ValidationError` which escapes + breaker not tripped. |
| GAP-SEC-04 `check_violation` uncaught | HIGH→CRIT | **CONFIRMED** | `agt_engine.py:58-62` has no try/except around the engine call; a raising check is not fail-closed. |
| GAP-CAP-01 REQUIRE_APPROVAL dead on AGT path | HIGH | **RESOLVED (Phase 15, docs+boundary)** | AGT path is binary by design (ADR-0001 — no speculative extension); README decision model now states AGT=allow/deny while `require_approval`/transform kinds are sidecar/hosted-plane kinds the SDK routes correctly when received. Boundary test asserts AGT never emits `require_approval`; end-to-end test proves a scripted `require_approval` → `QortaraApprovalRequired`. |
| GAP-SEC-01 no-context = silent fail-open | HIGH | **RESOLVED (Phase 14)** | Both paths now call `warn_missing_context()` → `QortaraUngovernedDispatchWarning` instead of a silent early-return; escalating the category to an error (stdlib `warnings` filter) makes ungoverned dispatch fail closed. Exempt tools don't warn. |
| GAP-SEC-07 unpatch/`__qortara_original__` + settable `qortara_exempt` | HIGH | **RESOLVED (Phase 16, defense-in-depth)** | `__qortara_original__` handle removed from all wrappers (unread; originals only in the unpatch dict). `qortara_exempt` now sets a module-private identity sentinel; `is_exempt` checks `is _EXEMPT_MARKER`, so a raw truthy `__qortara_exempt__` no longer exempts. Within the cooperative-process boundary (THREAT-MODEL §5 unchanged — hostile in-process code still out of scope). |
| GAP-SEC-08 `.run`/`._run`/`__call__` ungoverned | HIGH | **RESOLVED (Phase 15)** | Chokepoint moved to `BaseTool.run`/`.arun` — the funnel `invoke`/`ainvoke` call (verified langchain_core 1.4.2) — so a direct `tool.run(...)`/`.arun(...)` is now governed. `__call__` does not exist on `BaseTool`. `_run`/`_arun` (per-subclass private impls) are unpatchable at the class level → documented cooperative-process boundary (THREAT-MODEL §5). |
| GAP-CFG-01 dead config (policy_mode/offline_policy/require_compatible_protocol) | HIGH | **RESOLVED (Phase 14)** | `policy_mode=observe` now real (shadow/dry-run: evaluate + log would-be block, never raise; threaded `init`/`init_agt`→`apply_patches`→adapters→`enforce_decision`). `offline_policy_path`/`QORTARA_OFFLINE_POLICY` **removed** (dead; air-gapped path is `init_agt` per ADR-0001). README config table corrected. *`require_compatible_protocol` wiring still deferred — `health()` exposes no peer version; documented limitation, not dead config.* |
| GAP-CI-01 security.yml gates `\|\| true` | HIGH | **RESOLVED (Phase 16)** | bandit + pip-audit now blocking (both pass clean); pip-audit invocation corrected to audit the synced project venv (`uv run --with pip-audit`), not an isolated tool env — the prior gate was near-meaningless. SBOM kept non-blocking by design (artifact gen, stated rationale). |
| GAP-CI-02 gitleaks binary no checksum | MED | **RESOLVED (Phase 16)** | gitleaks 8.21.2 tarball pinned to SHA256 `5bc41815…e3ba` (official release checksums.txt), verified via `sha256sum -c` before extraction; version bump must update the digest (commented). |
| GAP-DOC-01 README "(local sidecar)"/"bundled sidecar" + ARCHITECTURE-BOUNDARIES pre-pivot + evidence no-op | MED | CONFIRMED | internal contradiction. *(deferred — doc)* |
| MED/LOW: blocking httpx in async wrapper; tenant_key cleartext over http | MED | **RESOLVED (Phase 17)** | async wrappers run blocking-IO decisions via `asyncio.to_thread` (`blocking_io` flag; in-process AGT stays inline); `SidecarClient` warns `QortaraInsecureTransportWarning` on tenant_key over non-TLS non-loopback. |
| MED/LOW residuals: breaker half-open; signature metadata; non-SHA256 policy_version field | LOW | **DEFERRED (rationale)** | breaker design is acceptable/fail-closed; `functools.wraps` rejected (would re-add `__wrapped__`, undoing SEC-07); `policy_version_sha256` is an external `qortara_protocol` field name — not ours to rename. |
| ~~AGT 4.0.0 uninstallable / `agent_control_plane` import mismatch~~ | ~~CRITICAL~~ | **REFUTED** | subagent had no network; main-context verified `uv sync` installs core/protocols/integrations + 83 tests pass against the real `PolicyEngine` + CI green. |

## Remediation scope — THIS cycle (operator-approved) — ✅ RESOLVED (Phase 13)

Confirmed CRITICAL bypass/fail-open set: **GAP-SEC-02, -03, -04, -05, -06** — all **RESOLVED** (Phase 13, META_LEDGER #32 GATE / #33 SEAL), verified by adversarial tests in `tests/conformance/test_redteam_failclosed.py` + `test_agt_arg_safety.py` (18 tests; full suite 97 passed/2 skipped). SEC-05 mitigated (truth + opt-in `capability_aliases`); AGT internals unchanged.

| GAP | Fix |
|---|---|
| SEC-06 | Patch `ToolNode.ainvoke` (async wrapper mirroring BaseTool). |
| SEC-03 | `client.decide` catches `ValidationError`/`ValueError` → `_record_failure()` + deny-closed. |
| SEC-04 | `AgtDecisionClient.decide` wraps the engine call; any exception → fail-closed DENY. |
| SEC-02 | Wrappers fail-closed on any decision kind that isn't ALLOW/EXEMPT/DENY/REQUIRE_APPROVAL (unsupported → deny with rationale); document DOWNGRADE/REDACT/SANDBOX/OBSERVE as not-yet-supported. |
| SEC-05 | Truth-in-advertising: correct the overclaiming docstrings; add an **opt-in tool→AGT-capability name map** on `AgtPolicyAdapter` so operators can route their tool names into AGT's arg-checks; add a test proving the *boundary* (unmapped tool with dangerous args is NOT arg-checked) so the limitation is explicit, not hidden. (AGT internals not modified — ADR-0001.) |

## Deferred (tracked follow-up — operator-sequenced)

GAP-DOC-01 (rest) + MED/LOW hardening. (GAP-SEC-01 + GAP-CFG-01 resolved in Phase 14; GAP-SEC-08 + GAP-CAP-01 in Phase 15; GAP-SEC-07 + GAP-CI-01 + GAP-CI-02 in Phase 16. `require_compatible_protocol` init-wiring remains deferred pending a sidecar health-version field. All other CONFIRMED HIGH/CRITICAL findings are closed.)

## Meta-finding (process)

Self-audit (the constructive `/qor-audit` PASS verdicts + session seal) did **not** surface these; adversarial separate-context red-teaming did. Notably the arg-safety conformance tests gave false confidence by using an AGT-recognized tool name. **Doctrine note:** enforcement features need an adversarial test that tries to *bypass* them with realistic inputs, not only a happy-path conformance test; and dispatch-path changes must enumerate every sibling entry point (`invoke` AND `ainvoke`, BaseTool AND ToolNode).

---
_Findings advisory; remediation of the CRITICAL set proceeds as a governed cycle (Phase 13)._
