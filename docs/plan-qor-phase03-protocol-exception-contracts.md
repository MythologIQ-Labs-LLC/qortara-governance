# Plan: B2 — Protocol versioning + frozen exception contract

**change_class**: feature

**doc_tier**: standard

**terms_introduced**:
- term: PROTOCOL_VERSION
  home: packages/qortara-governance-langchain/src/qortara_governance/protocol_version.py

**boundaries**:
- limitations: The decision request/response payload schema is owned by the external `qortara_protocol` package; this phase versions the SDK↔sidecar *wire path* and freezes the *exception* contract, not the payload dataclasses.
- non_goals: Not implementing sidecar `/version` negotiation (that is sidecar work, blocker S1); this phase delivers the SDK-side version surface + compatibility gate the negotiation will call.
- exclusions: The fuller §8.3 exception set (QortaraConfigurationError, QortaraPolicyInvalid, QortaraDecisionMalformed, QortaraAuthenticationError, QortaraTimeout) is deferred until each has a real raise site, to avoid declaring exceptions with no backing behavior.

## Open Questions

None. The wire protocol version is already implicit as the literal `v0.1` repeated in three endpoint paths in `client.py` (`/v0.1/decisions`, `/v0.1/evidence`, `/v0.1/health`) — verified by read. This phase promotes that literal to a single `PROTOCOL_VERSION` constant (single source of truth) and adds the protocol-mismatch contract. Pattern mirrors the existing `CONTRACT_VERSION` + `IncompatibleAdapterVersion` in `contract/state.py`.

## Phase 1: Protocol-version single source of truth + mismatch exception

### Affected Files

- `packages/qortara-governance-langchain/tests/test_protocol_versioning.py` (NEW) — behavioral tests: client request path derives from `PROTOCOL_VERSION`; `require_compatible_protocol` raises on major mismatch with structured fields; `QortaraProtocolMismatch` is catchable as `QortaraError`.
- `packages/qortara-governance-langchain/src/qortara_governance/protocol_version.py` (NEW) — `PROTOCOL_VERSION = "v0.1"`; `require_compatible_protocol(peer_version: str) -> None` raising `QortaraProtocolMismatch` when the major component differs.
- `packages/qortara-governance-langchain/src/qortara_governance/exceptions.py` — add `QortaraProtocolMismatch(QortaraError)` with structured fields `expected` / `received`; add `__all__` freezing the public exception set as a Beta contract.
- `packages/qortara-governance-langchain/src/qortara_governance/client.py` — replace the three `/v0.1/...` string literals with `f"/{PROTOCOL_VERSION}/..."`; import `PROTOCOL_VERSION`.
- `packages/qortara-governance-langchain/src/qortara_governance/__init__.py` — export `PROTOCOL_VERSION`, `require_compatible_protocol`, `QortaraProtocolMismatch`.

### Changes

1. `protocol_version.py`: define `PROTOCOL_VERSION` and `require_compatible_protocol`. Major component = substring before the first dot of the trimmed leading `v`. Same major ⇒ return; different ⇒ raise `QortaraProtocolMismatch(expected=PROTOCOL_VERSION, received=peer_version)`.
2. `exceptions.py`: add `QortaraProtocolMismatch` (subclass of `QortaraError`) storing `expected` and `received`; add `__all__` listing the frozen set: `QortaraError`, `QortaraPolicyDenied`, `QortaraApprovalRequired`, `QortaraSidecarUnavailable`, `QortaraProtocolMismatch`.
3. `client.py`: `from qortara_governance.protocol_version import PROTOCOL_VERSION`; endpoint strings become `f"/{PROTOCOL_VERSION}/decisions"` etc. (behavior unchanged — value is `"v0.1"`).
4. `__init__.py`: add the three new names to imports + `__all__`.

### Unit Tests

- `tests/test_protocol_versioning.py`:
  - `test_client_request_path_uses_protocol_version`: drive `SidecarClient.decide` through an `httpx.MockTransport` handler that captures `request.url.path`; assert the path equals `/{PROTOCOL_VERSION}/decisions`. Fails if the path literal and the constant diverge.
  - `test_require_compatible_protocol_accepts_same_major`: `require_compatible_protocol(PROTOCOL_VERSION)` returns without raising.
  - `test_require_compatible_protocol_rejects_different_major`: a different-major version raises `QortaraProtocolMismatch`; assert `.expected` and `.received` fields carry the two versions.
  - `test_protocol_mismatch_is_qortara_error`: `QortaraProtocolMismatch(...)` is an instance of `QortaraError` (catch-contract stability).

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-protocol-version | NEW | packages/qortara-governance-langchain/tests/test_protocol_versioning.py | client request path equals `/{PROTOCOL_VERSION}/decisions`; mismatch raises `QortaraProtocolMismatch(expected, received)` |
| FX-exceptions | MODIFIED | packages/qortara-governance-langchain/tests/test_protocol_versioning.py | `QortaraProtocolMismatch` is a `QortaraError` subclass (frozen catch-contract) |

## Definition of Done

### Deliverable: protocol-version-contract

- **D1**: The SDK declares one wire protocol version and refuses an incompatible peer; the public exception set is a frozen Beta contract.
- **D2**: `PROTOCOL_VERSION` in `protocol_version.py` drives client endpoints; `QortaraProtocolMismatch` in `exceptions.py` with `__all__`; new names exported from `__init__`.
- **D3**: META_LEDGER GATE + SEAL entries; FEATURE_INDEX rows; BACKLOG B2 closed (with deferred-set follow-up noted).
- **D4**: `tests/test_protocol_versioning.py` (4 tests) pass; full suite stays green.

## CI Commands

- `uv run --package qortara-governance-langchain pytest` — full suite incl. new protocol tests.
- `uv tool run ruff check .` — lint workspace.
