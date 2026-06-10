# Changelog — qortara-governance-langchain

## [Unreleased]

Governed work since the 0.2.1 restructure (no release tag yet — held at the Review Boundary).
Version remains `0.2.1`; this section accumulates the changes that a later release will stamp.

### Added

- **In-process enforcement via Microsoft AGT.** `init_agt(agent_id, allowed_tools, ...)` installs the dispatch patch with an AGT `PolicyEngine` decision source — local enforcement, no sidecar required (ADR-0001). `capability_aliases` routes custom tool names into AGT's argument-level (SQL/code/path) checks.
- **`policy_mode="observe"`** shadow/dry-run mode (evaluate policy + log would-be blocks at WARNING, never raise) on `init()` / `init_agt()`.
- **Opt-in evidence emission** from the dispatch path: pass `evidence_sink=` to `init()`/`init_agt()`. Emits a *decision* event on a terminal deny and an *execution* event (`executed`/`errored` + duration) after each permitted run. New `EvidenceSink` protocol + built-in `OTelEvidenceSink`; `decision_evidence`/`execution_evidence` builders. Best-effort — never raises into the caller, never weakens fail-closed; default (no sink) leaves the hot path unchanged.
- **`qortara-governance doctor`** diagnostics CLI: `python -m qortara_governance.doctor [--json]` + `collect_status()`/`GovernanceStatus` — reports patch state, decision client, enforce/observe, evidence sink, context, and warns on silent "looks-governed-but-isn't" traps.
- **`DecisionClient` Protocol** shared by `SidecarClient` and `AgtDecisionClient`.
- New public exceptions `QortaraConfigurationError`, `QortaraTimeout`, `QortaraAuthenticationError`; new warning categories `QortaraUngovernedDispatchWarning`, `QortaraInsecureTransportWarning`.
- CI-verified compatibility matrix (`docs/COMPATIBILITY.md` + a `compat-floor` CI job exercising the `langchain-core>=0.3,<0.4` + `langgraph>=0.2,<0.3` floor).

### Changed

- **Dispatch hook moved from `BaseTool.invoke`/`.ainvoke` to `BaseTool.run`/`.arun`** — the funnel `invoke`/`ainvoke`/`stream` all pass through, and a direct `tool.run(...)` call is now governed too (closes a residual bypass). `ToolNode.ainvoke` is patched alongside `.invoke`.
- A dispatch with **no `AgentContext`** now emits `QortaraUngovernedDispatchWarning` instead of silently skipping; escalate the category to an error to fail closed.
- `SidecarClient.require_reachable()` distinguishes **auth (401/403)** and **timeout** from a generic unreachable failure; a 4xx decision response denies with a distinct rationale.
- Async dispatch runs blocking decisions and evidence emission **off the event loop** (`asyncio.to_thread`).
- Decision model documented honestly: the in-process AGT engine is **binary allow/deny**; `require_approval` + transform kinds come from the sidecar/hosted plane.
- Removed the unimplemented `offline_policy_path` / `QORTARA_OFFLINE_POLICY` config (the air-gapped path is `init_agt`, in-process).

### Security

- Closed the red-team fail-open/bypass set: non-DENY verdicts (DOWNGRADE/REDACT/SANDBOX/unknown) now **deny-closed**; malformed 2xx bodies and AGT engine errors **deny-closed** (the breaker counts malformed responses).
- Removed the `__qortara_original__` "restore-me" handle from the wrappers; `@qortara_exempt` now uses an identity sentinel so a stray/injected truthy attribute no longer exempts.
- CI security gates (bandit, pip-audit) are **blocking**; the gitleaks tarball is pinned by SHA256; least-privilege workflow permissions; a `tenant_key`-over-plaintext-http warning.

### Out of scope

- Sibling-framework adapters (CrewAI / LlamaIndex / AutoGen) and a hosted-cloud preview — declined; the package stays LangChain/LangGraph-only.

## v0.2.1 — 2026-05-04

### Changed

- Repository restructured as a uv workspace mono-repo. Source moves from the repository root into `packages/qortara-governance-langchain/`. Sibling adapter packages (CrewAI, LlamaIndex, AutoGen) will land as additional `packages/*` members.
- Repository renamed from `qortara-governance-langchain` to `qortara-governance`. GitHub redirects the old URL. PyPI package name is unchanged — `pip install qortara-governance-langchain` continues to work without modification.

### Fixed

- `LICENSE` file now contains the full canonical Apache-2.0 text. The prior file shipped only the boilerplate notice header, which prevented GitHub's license detector and downstream tooling from identifying the license (`spdx_id: NOASSERTION`).

### No API changes

- No public API, import paths, dependency pins, or runtime behavior changed in this release.

## v0.2.0 — 2026-04-23

### Added

- `qortara_governance.contract` module — versioned `FrameworkAdapter` Protocol, frozen `AdapterState`, `CONTRACT_VERSION` constant, and an internal `ConformanceSuite` (not re-exported from `__init__` — importable via its module path). This is the extension point for future framework adapters.
- `LangChainToolAdapter` and `LangGraphToolNodeAdapter` — the existing patch logic now implements the `FrameworkAdapter` Protocol. Module-level `apply()` / `unpatch()` functions preserved; the adapter classes delegate to them.
- `AdapterRegistry` replaces the prior module-global patch state. Accepts a sequence of adapters; unwinds LIFO on `unpatch_all()`; rejects version mismatches with `IncompatibleAdapterVersion`.
- `py.typed` marker — signals to mypy/pyright that this package ships type information.

### Changed

- Availability probe in `AdapterRegistry` now uses `importlib.util.find_spec` instead of `importlib.import_module`. Detecting whether a framework is installed no longer triggers that framework's import-time side effects. If `find_spec` resolves but the adapter's own `apply()` raises `ImportError` (broken submodule), the registry skips the adapter with the same `RuntimeWarning` path.
- Module-level `tool_patches.apply()` and `langgraph_patches.apply()` reject double-install — calling `apply()` against `BaseTool.invoke` / `ainvoke` / `ToolNode.invoke` that is already `__qortara_wrapped__` raises `RuntimeError` with a remediation hint.
- `qortara-protocol` dependency pin bumped to `==0.1.2` (additive protocol changes; see qortara-protocol CHANGELOG).

### Fixed

- n/a (no bug fixes; this release is additive + architectural).

### License

Apache-2.0.

## v0.1.0 — Unreleased

First public release.

### Added

- `qortara_governance.init()` — one-line integration with LangChain.
- Deep `BaseTool.invoke/ainvoke` + `langgraph.prebuilt.ToolNode.invoke` patches that close the AGT issue #73 wrapper-bypass gap. Native tool-calling dispatch is now governed, not just observed.
- Subprocess auto-spawn + external-daemon opt-in via `QORTARA_SIDECAR_ENDPOINT`.
- HTTP+JSON protocol (v0.1) to the sidecar. Pydantic models shared via `qortara-protocol` package.
- Circuit breaker: consecutive 5xx from the sidecar fails closed to deny-all for a 30s cooldown.
- `QortaraCallbackHandler` — additive observability for chain boundaries and retrieval. Never blocks.
- `@qortara_exempt` decorator for tool opt-out, with evidence still emitted.
- W3C traceparent propagation for LangSmith correlation. `qortara.evidence_id` attaches to the current OTel span.
- `QortaraPolicyDenied`, `QortaraApprovalRequired`, `QortaraSidecarUnavailable` exceptions.
- Unit and integration-with-fakes test suite (24 tests including the AGT #73 bypass-closed regression).

### Not in v0.1

- CrewAI / LlamaIndex / AutoGen adapters — planned as follow-on packages.
- Federation Phase 2 connectors — separate plan.
- Real LangChain version pinning beyond `langchain-core >= 0.3`; upcoming versions tracked as they land.

### License

Apache-2.0.
