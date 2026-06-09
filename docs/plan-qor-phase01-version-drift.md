# Plan: D1 — Resolve runtime/packaging version drift

**change_class**: hotfix

**doc_tier**: minimal

## Open Questions

None. Canonical version is `0.2.1`, established by two agreeing signals: `pyproject.toml` `version = "0.2.1"` and `CHANGELOG.md` top entry `## v0.2.1`. The runtime `__version__` lags at `0.2.0`.

## Phase 1: Align runtime version and guard against future drift

### Affected Files

- `packages/qortara-governance-langchain/tests/test_version_consistency.py` (NEW) — assert installed package metadata version equals the runtime `__version__`.
- `packages/qortara-governance-langchain/src/qortara_governance/__init__.py` — bump `__version__` from `"0.2.0"` to `"0.2.1"`.

### Changes

1. Add `test_version_consistency.py`: import `qortara_governance`, read `importlib.metadata.version("qortara-governance-langchain")`, assert it equals `qortara_governance.__version__`. The test invokes both lookups and asserts equality of their outputs — it fails the moment the two diverge again.
2. Edit `__init__.py`: `__version__ = "0.2.1"`.

### Unit Tests

- `tests/test_version_consistency.py` — `test_runtime_version_matches_package_metadata`: given the installed distribution, the runtime `__version__` string equals `importlib.metadata.version("qortara-governance-langchain")`. If either drifts, the equality assertion fails (survives SG-035: a silently re-drifted version makes this test red).

## Feature Inventory Touches

| entry_id | operation | test_path | test_descriptor |
|---|---|---|---|
| FX-version | MODIFIED | packages/qortara-governance-langchain/tests/test_version_consistency.py | `qortara_governance.__version__` equals `importlib.metadata.version("qortara-governance-langchain")` |

## Definition of Done

### Deliverable: version-consistency

- **D1**: The SDK reports one version. Runtime `__version__`, packaging metadata, and changelog agree.
- **D2**: `__version__ == "0.2.1"` in `src/qortara_governance/__init__.py`.
- **D3**: META_LEDGER GATE entries (plan, audit, seal); SYSTEM_STATE + FEATURE_INDEX updated; BACKLOG D1 closed.
- **D4**: `tests/test_version_consistency.py::test_runtime_version_matches_package_metadata` passes and asserts metadata == `__version__`.

## CI Commands

- `uv run --package qortara-governance-langchain pytest` — full package test suite incl. the new version-consistency test.
- `uv tool run ruff check .` — lint workspace.
