# Plan — Phase 14: SEC-01 ungoverned-dispatch signal + CFG-01 honest config

**Risk Grade**: L3 (touches the enforcement dispatch path)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Target**: deferred red-team HIGH items GAP-SEC-01 + GAP-CFG-01 (brief: `docs/research-brief-deep-audit-redteam-2026-06-09.md`)
**Cycle scope**: SEC-01 + CFG-01 only. No expansion into the other deferred items.

## Why

Two "looks-governed-but-isn't" traps survive the CRITICAL-set remediation:

- **GAP-SEC-01** — after `init()`/`init_agt()`, `BaseTool.invoke`/`ToolNode.invoke` are
  patched process-wide, but `_decide_or_raise`/`_decide_each` **early-return silently**
  when `get_context() is None` (`tool_patches.py:64-65`, `langgraph_patches.py:63-64`).
  A tool dispatched off any code path without an `AgentContext` runs **ungoverned with
  zero signal**. Silent fail-open.
- **GAP-CFG-01** — `Config.policy_mode` (ENFORCE/OBSERVE) and `Config.offline_policy_path`
  are resolved + fingerprinted but **never consulted** (`config.py:62-66`, `__init__.py:73-78`).
  `README.md:148` promises `observe` "logs but executes" and `README.md:127,149` sell
  `offline_policy_path` as a working air-gapped feature. Both are **false advertising**.

## Promise (Definition of Done)

### D1 — Vision
Enforcement never *silently* does nothing: an ungoverned dispatch is observable, and a
config knob either does what it says or does not exist.

### D2 — Code
1. **SEC-01**: new warning category `QortaraUngovernedDispatchWarning(UserWarning)` in
   `exceptions.py` (+ package export). `warn_missing_context(tool_name)` helper in
   `tool_patches.py`, called from both `_decide_or_raise` and `_decide_each` when
   `ctx is None`, **before** the early return. Relies on the stdlib `warnings` machinery
   (default: once per call-site; operators may `warnings.filterwarnings("error",
   category=QortaraUngovernedDispatchWarning)` to make ungoverned dispatch **fail closed**).
   Exempt tools (`is_exempt`) do not warn.
2. **CFG-01a — implement OBSERVE for real**: thread an `observe: bool` from
   `init`/`init_agt` → `apply_patches(client, *, observe=)` → `_default_adapters(observe=)`
   → adapter `__init__(observe=)` → module `apply(client, observe=)` → wrapper closures →
   `enforce_decision(decision, *, observe=)`. When `observe=True`, a non-permit decision
   is **logged** (`logging.getLogger("qortara_governance").warning(...)`) and **does not
   raise** (shadow/dry-run). ENFORCE behavior is byte-unchanged. `init_agt` gains
   `policy_mode: str | PolicyMode = PolicyMode.ENFORCE`.
3. **CFG-01b — remove dead config**: delete `offline_policy_path` from `Config`,
   `load_config`, `init`. Air-gapped guidance redirects to `init_agt` (in-process AGT,
   no network — the real offline path per ADR-0001). `QORTARA_OFFLINE_POLICY` env var
   no longer read.

### D3 — Governance
META_LEDGER entries (plan/audit + seal), gate artifacts, brief marked RESOLVED for
SEC-01 + CFG-01, README config table corrected.

### D4 — Empirical
- `test_observe_mode_never_raises_but_logs` (deny in OBSERVE → no raise, caplog records it).
- `test_enforce_mode_still_raises` (regression: ENFORCE unchanged).
- `test_no_context_dispatch_warns` (warns `QortaraUngovernedDispatchWarning`).
- `test_no_context_dispatch_filter_error_fails_closed` (filter→error ⇒ ungoverned
  dispatch raises = fail-closed path).
- `test_exempt_tool_does_not_warn`.
- `test_init_agt_observe_mode_allows_denied` (AGT path shadow mode).
- `test_offline_policy_path_removed` (config no longer carries it) — update
  `test_config_precedence.py` accordingly.

## Non-goals / explicitly NOT this cycle
- `require_compatible_protocol` wiring into `init()` — the sidecar `health()` endpoint
  returns only a bool (no peer version: `client.py:128-137`); honest wiring needs a
  sidecar contract change. Documented limitation, NOT dead config. **Deferred.**
- GAP-CAP-01, SEC-07, SEC-08, CI-01/02, DOC-01(rest), MED/LOW — remain tracked-deferred.

## Section 4 Razor
No new module, no new dependency, no new config file. OBSERVE reuses the existing
`PolicyMode` enum; SEC-01 reuses the stdlib `warnings` machinery (no bespoke warn-once
state — the filter system gives both "once" and "escalate-to-error" for free).

## Blast radius
Internal signatures gain default-valued kwargs (`observe=False`) → backward compatible.
Public surface: `init_agt` gains an optional kwarg (additive); `offline_policy_path` /
`QORTARA_OFFLINE_POLICY` **removed** (pre-release v0.2.1, unmerged PR #13 — safe). New
public warning class (additive). README config table corrected.

## Review Boundary
Commit + push to PR #13 (`feat/qortara-governance-genesis`). NO tag, NO PyPI. No AI footer.
