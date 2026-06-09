# Plan: S1 — Local sidecar scaffold (shared evaluation core)

**change_class**: feature

**doc_tier**: system

**high_risk_target**: false

**terms_introduced**:
- term: LocalPolicy
  home: packages/qortara-governance-sidecar/src/qortara_sidecar/policy.py
- term: Evaluation core
  home: packages/qortara-governance-sidecar/src/qortara_sidecar/evaluator.py

**boundaries**:
- limitations: This is the Beta scaffold — a deterministic local evaluator + stdlib HTTP app over the `qortara_protocol` v0.1 contract. It is NOT production-hardened: no TLS, no auth yet (that is S2), no hosted sync, no signing.
- non_goals: Not implementing Ed25519 evidence signing, hosted plane sync, or Cedar policy evaluation (the bundled `qortara_protocol` carries Cedar texts; the scaffold evaluates a simple local rule model).
- exclusions: Authentication/transport security is S2; conformance against all dispatch paths is B1.

## Open Questions

None. The wire contract is fixed by `qortara_protocol==0.1.2` (verified): `ActionRequest` → `ActionDecision` with `DecisionKind` ∈ {allow, deny, require_approval, ...}; `SidecarHealth`, `PolicyCacheState` for `/health`/`/version`. Endpoints the SDK calls (verified in `client.py`): `/v0.1/decisions`, `/v0.1/evidence`, `/v0.1/health`.

## Phase 1: Evaluation core + local policy

### Affected Files

- `packages/qortara-governance-sidecar/tests/test_evaluator.py` (NEW) — allow-rule allows; deny-rule denies; no-match defaults to DENY (fail-closed); decision carries policy pack id + sha.
- `packages/qortara-governance-sidecar/tests/test_policy.py` (NEW) — `LocalPolicy.from_dict` parses rules; `load_policy` reads JSON; malformed policy raises.
- `packages/qortara-governance-sidecar/src/qortara_sidecar/policy.py` (NEW) — `LocalPolicy` (pack_id, default decision, ordered rules by tool/capability glob) + `load_policy(path)`.
- `packages/qortara-governance-sidecar/src/qortara_sidecar/evaluator.py` (NEW) — `evaluate(request: ActionRequest, policy: LocalPolicy) -> ActionDecision`; first-match wins; **default DENY** when no rule matches (fail-closed).
- `packages/qortara-governance-sidecar/src/qortara_sidecar/__init__.py` (NEW) — `__version__`, exports.

### Changes

`evaluate` is a pure function: iterate policy rules in order; first whose `tool` glob matches `request.target_resource` and `capability` glob matches `request.requested_capability` yields its decision_kind; if none match, return `DecisionKind.DENY` with rationale "no matching rule — default deny". Every decision stamps `policy_pack_id` and `policy_version_sha256` from the policy.

### Unit Tests

- `test_evaluator.py`: `test_allow_rule_allows` (matching allow rule → ALLOW), `test_deny_rule_denies` (matching deny rule → DENY), `test_no_match_defaults_deny` (empty/no-match → DENY, rationale names default-deny), `test_decision_stamps_pack_identity` (decision.policy_pack_id == policy.pack_id).
- `test_policy.py`: `test_from_dict_parses_rules`, `test_load_policy_reads_json` (tmp file round-trip), `test_malformed_policy_raises`.

## Phase 2: Stdlib HTTP app + console entry

### Affected Files

- `packages/qortara-governance-sidecar/tests/test_app.py` (NEW) — `dispatch` routing: `/v0.1/health`→200 SidecarHealth; `/version`→200 with version; `/v0.1/decisions` POST→200 ActionDecision JSON; unknown path→404; decision endpoint with bad body→fail-closed DENY or 400.
- `packages/qortara-governance-sidecar/src/qortara_sidecar/app.py` (NEW) — pure `dispatch(method, path, body: bytes) -> tuple[int, bytes]` over the evaluator + a thin `http.server.BaseHTTPRequestHandler` that delegates to `dispatch`; binds `127.0.0.1` only.
- `packages/qortara-governance-sidecar/src/qortara_sidecar/__main__.py` (NEW) — `run(host="127.0.0.1", port=8787, policy_path=...)`.
- `packages/qortara-governance-sidecar/pyproject.toml` (NEW) — workspace member; dep `qortara-protocol==0.1.2`; console script `qortara-governance-sidecar = "qortara_sidecar.__main__:main"`.
- `packages/qortara-governance-sidecar/README.md` (NEW) — scaffold scope + run instructions.

### Changes

`dispatch` is HTTP-framework-agnostic and fully unit-testable without binding a socket. The `BaseHTTPRequestHandler` is a thin adapter. Server binds loopback only (threat 3 mitigation baseline; auth is S2).

### Unit Tests

- `test_app.py`: `test_health_returns_ok` (dispatch GET /v0.1/health → 200, status "ok"), `test_version_endpoint` (→ 200, body has version), `test_decision_endpoint_allows` (POST a request matching an allow rule → ALLOW JSON), `test_unknown_path_404`, `test_malformed_decision_body_fails_closed` (invalid JSON → not ALLOW).

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-sidecar-evaluator | NEW | packages/qortara-governance-sidecar/tests/test_evaluator.py | no-match request → `DecisionKind.DENY` (fail-closed); matching allow rule → ALLOW |
| FX-sidecar-policy | NEW | packages/qortara-governance-sidecar/tests/test_policy.py | `load_policy` round-trips JSON; malformed policy raises |
| FX-sidecar-app | NEW | packages/qortara-governance-sidecar/tests/test_app.py | `dispatch` GET /v0.1/health→200 ok; POST /v0.1/decisions→ActionDecision; unknown→404; bad body fails closed |

## Definition of Done

### Deliverable: sidecar-scaffold

- **D1**: A local sidecar exists that the SDK can call; it evaluates a local policy and fails closed on no match / bad input.
- **D2**: `packages/qortara-governance-sidecar/` workspace package with `evaluator.evaluate`, `policy.LocalPolicy/load_policy`, `app.dispatch`, console entry `qortara-governance-sidecar`.
- **D3**: META_LEDGER GATE+SEAL; FEATURE_INDEX rows; BACKLOG S1 updated (scaffold done; hardening tracked).
- **D4**: `test_evaluator.py` + `test_policy.py` + `test_app.py` pass; default-deny asserted; `uv sync` succeeds with the new member.

## CI Commands

- `uv run --package qortara-governance-sidecar pytest packages/qortara-governance-sidecar` — sidecar suite.
- `uv run --package qortara-governance-langchain pytest` — SDK suite stays green.
- `uv tool run ruff check .` — lint workspace.
