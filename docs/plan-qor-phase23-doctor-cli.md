# Plan — Phase 23: `qortara-governance doctor` diagnostics CLI (W3)

**Risk Grade**: L2 — additive read-only introspection + a CLI; no enforcement-path behavior change.
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Base**: `main` (`e0baaf7`).
**Target**: BACKLOG W3 — operator diagnostics: "is governance actually active, and how?"

## Why
The SDK has several "looks-governed-but-isn't" states it (correctly) handles quietly: no
`AgentContext` set (ungoverned dispatch — warned), `policy_mode=observe` (evaluated but not
enforced), no `evidence_sink` (no audit trail), plaintext-credential transport. An operator
has no single command to confirm enforcement is live and in which mode. `doctor` surfaces it.

## Promise (Definition of Done)

### D1 — Vision
`python -m qortara_governance.doctor` prints a clear governance status report and returns an
exit code suitable for a healthcheck (0 = patched/active, 1 = not active).

### D2 — Code
1. **Registry introspection (additive, no behavior change)**: `AdapterRegistry` stores the
   `observe` flag + `evidence_sink` already passed to `apply_patches` (currently baked into
   adapters but not surfaced). `apply_patches` sets them; `unpatch_all` clears them. Expose
   `get_observe() -> bool` and `get_evidence_sink() -> EvidenceSink | None` (registry +
   `patches/__init__`). Pure storage of an existing value — enforcement is untouched.
2. **`doctor.py`**:
   - `GovernanceStatus` (frozen dataclass): `patched`, `wrapped_methods` (list[str]),
     `client_kind` (str), `policy_mode` ("enforce"/"observe"), `evidence_sink` (class name |
     None), `context_set` (bool), `warnings` (list[str]).
   - `collect_status() -> GovernanceStatus` — from `is_patched`, `get_client`, `get_observe`,
     `get_evidence_sink`, `get_context`, and the `BaseTool.run`/`.arun` (+ `ToolNode` if
     langgraph) `__qortara_wrapped__` flags. Never raises; redacts (tenant_key shown only as a
     bool, endpoint host only). Builds `warnings` for the silent traps (not patched; no context;
     observe mode; no sink; SidecarClient tenant_key over plaintext http).
   - `format_report(status) -> str` — human-readable, sectioned.
   - `main(argv=None) -> int` — print report; `0` if patched else `1`; `--json` flag emits the
     status as JSON. `if __name__ == "__main__": sys.exit(main())`.
3. Export `collect_status`, `GovernanceStatus` from the package for programmatic use.

### D3 — Governance/docs
README: a "Diagnostics" note (`python -m qortara_governance.doctor`). BACKLOG W3 → done.
Ledger GATE + SEAL.

### D4 — Empirical
- `test_doctor_reports_not_active` — no init ⇒ `patched=False`, `main()` exit 1, warning present.
- `test_doctor_reports_enforce_agt` — after `init_agt(...)` ⇒ `patched=True`, `client_kind`
  mentions AGT, `policy_mode="enforce"`, run/arun wrapped, `main()` exit 0.
- `test_doctor_reports_observe_mode` — `init_agt(..., policy_mode="observe")` ⇒
  `policy_mode="observe"` + a "not enforcing" warning.
- `test_doctor_reports_no_context_warning` — patched but no `set_context` ⇒ a no-context warning.
- `test_doctor_reports_evidence_sink` — `init_agt(..., evidence_sink=...)` ⇒ sink class surfaced.
- `test_doctor_redacts_tenant_key` — a SidecarClient status never includes the raw key value.
- `test_doctor_json_output` — `main(["--json"])` emits valid JSON with the status fields.

## Section 4 Razor
One small registry accessor (stores an existing value) + one self-contained `doctor.py` reading
public introspection. No new dependency. No enforcement-path change.

## Blast radius
`apply_patches`/`unpatch_all` gain two stored attributes (set/clear) — no behavior change to
patch install or dispatch. `doctor` is read-only. New public names (`collect_status`,
`GovernanceStatus`, `get_observe`, `get_evidence_sink`) are additive.

## Non-goals
- Live network probing of a sidecar from doctor (it reports configured state, not reachability —
  `require_reachable` already covers reachability at init).
- Auto-remediation. Doctor diagnoses; it does not change config.

## Review Boundary
Commit + push + open a new PR off `main`; track CI; hand off. NO tag, NO PyPI, NO merge. No AI footer.
