# Plan: S2 — Authenticated local sidecar transport

**change_class**: feature

**doc_tier**: system

**high_risk_target**: false

**terms_introduced**:
- term: Ephemeral sidecar token
  home: packages/qortara-governance-sidecar/src/qortara_sidecar/auth.py

**boundaries**:
- limitations: Bearer-token authentication over loopback; TLS/mTLS for daemon mode is out of scope (roadmap §11.3). The SDK launcher handshake (delivering the token to the SDK at spawn) is documented as a follow-up; this phase delivers the sidecar-side enforcement + token model.
- non_goals: Not implementing mTLS, OAuth, or hosted-plane tenant auth.
- exclusions: Conformance across dispatch paths is B1.

## Open Questions

None. Threats 2/3/16 in `docs/security/THREAT-MODEL.md` require rejecting unauthenticated local decision requests. The S1 sidecar `dispatch` is the enforcement point.

## Phase 1: Bearer-token enforcement on sensitive endpoints

### Affected Files

- `packages/qortara-governance-sidecar/tests/test_auth.py` (NEW) — token generation entropy; constant-time match accept/reject; dispatch 401 without/with-wrong token on `/v0.1/decisions`; 200 with correct token; `/v0.1/health` reachable unauthenticated.
- `packages/qortara-governance-sidecar/src/qortara_sidecar/auth.py` (NEW) — `generate_token()` (`secrets.token_urlsafe`), `extract_bearer(headers)`, `token_matches(expected, headers)` using `hmac.compare_digest` (constant-time).
- `packages/qortara-governance-sidecar/src/qortara_sidecar/app.py` — `SidecarContext` gains `auth_token: str | None = None`; `dispatch` gains a `headers` mapping param (default empty); `/v0.1/decisions` and `/v0.1/evidence` require a matching bearer when `auth_token` is set, else `401`; `/v0.1/health` + `/version` stay unauthenticated (liveness). Handler forwards request headers.
- `packages/qortara-governance-sidecar/src/qortara_sidecar/__main__.py` — read `QORTARA_SIDECAR_TOKEN` env or `generate_token()`; pass to context; never print the token (print only that auth is enabled).

### Changes

`token_matches` compares with `hmac.compare_digest` (no early-exit timing leak). When `ctx.auth_token` is `None`, no auth is enforced (embedded/dev mode); when set, sensitive endpoints reject by default. The token is never written to logs (handler already silences access logs; `__main__` prints presence, not value).

### Unit Tests

- `test_auth.py`:
  - `test_generate_token_has_entropy`: two tokens differ; length ≥ 32 chars.
  - `test_token_matches_accepts_correct` / `test_token_matches_rejects_wrong` / `test_token_matches_rejects_absent`.
  - `test_decisions_rejected_without_token`: `auth_token` set, no header → 401, body not `allow`.
  - `test_decisions_rejected_with_wrong_token`: wrong bearer → 401.
  - `test_decisions_allowed_with_correct_token`: correct bearer + matching allow rule → 200 `allow`.
  - `test_health_unauthenticated`: `/v0.1/health` returns 200 even with `auth_token` set and no header.

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-sidecar-auth | NEW | packages/qortara-governance-sidecar/tests/test_auth.py | sensitive endpoints return 401 without/with-wrong bearer; 200 with correct; health unauth; compare is constant-time |
| FX-sidecar-app | MODIFIED | packages/qortara-governance-sidecar/tests/test_auth.py | `dispatch` enforces bearer on `/v0.1/decisions` + `/v0.1/evidence` when `auth_token` set |

## Definition of Done

### Deliverable: sidecar-auth

- **D1**: The sidecar rejects unauthenticated decision/evidence requests when a token is configured; comparison is timing-safe; the token is never logged.
- **D2**: `auth.py` (`generate_token`/`extract_bearer`/`token_matches`); `app.dispatch(headers=...)` + `SidecarContext.auth_token`; `__main__` token wiring.
- **D3**: META_LEDGER GATE+SEAL; FEATURE_INDEX rows; BACKLOG S2 updated.
- **D4**: `test_auth.py` passes; S1 sidecar tests still green (backward-compatible default `auth_token=None`).

## CI Commands

- `uv run --package qortara-governance-sidecar pytest packages/qortara-governance-sidecar` — sidecar suite incl. auth.
- `uv tool run ruff check .` — lint workspace.
