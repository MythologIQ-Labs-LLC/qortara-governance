# Architecture Plan

## Foundation: extends Microsoft AGT (ADR-0001)

qortara-governance **builds on** Microsoft's Agent Governance Toolkit (AGT), declared as a dependency — `agent-governance-toolkit-{core,protocols,integrations}==4.0.0` (MIT) — **not** vendored and **not** modified. AGT supplies the policy engine, identity/zero-trust, sandboxing, SRE, and OWASP-Agentic compliance. qortara adds, on top:

1. a **bypass-proof dispatch-path hook** (`BaseTool.invoke`/`ToolNode.invoke` monkeypatch) that routes decisions into AGT's engine — closing the wrapper-bypass gap (AGT #73) AGT's callback adapter leaves open;
2. an optional **Azure upstream backend**.

Adopting AGT 4.0.0 sets the floor at **Python ≥3.11** (AGT requirement; 3.10 dropped — see ADR 0001 / META_LEDGER Phase 07). The standalone sidecar scaffold (former S1) was **retired** — AGT is the decision engine. Wiring the dispatch patch into AGT's engine + reconciling `qortara_protocol` against `agent-governance-toolkit-protocols` is **Increment B** (its own L3 cycle).

## Risk Grade: L3

### Risk Assessment
- [x] Contains security/auth logic -> **L3** (fail-closed policy enforcement, tenant-key auth, Ed25519 evidence signing, sidecar trust boundary)
- [x] Modifies existing APIs -> also L2-relevant (runtime monkey-patching of `BaseTool.invoke` / `ToolNode.invoke`)
- [ ] UI-only changes -> not applicable

**Rationale:** This package is a security-enforcement control. A defect can allow a denied tool to execute, fail open silently, leak sensitive tool arguments, or fabricate evidence. Security path detected — `/qor-audit` is MANDATORY before implementation cycles.

## File Tree (The Contract)

Current state of `packages/qortara-governance-langchain/src/qortara_governance/`:

```
src/qortara_governance/
|-- __init__.py            # public API surface (init()), __version__
|-- client.py              # decision client: connectivity, timeout, circuit breaker, fail-closed
|-- config.py              # configuration precedence + normalization
|-- context.py             # agent/trace/tool/execution context propagation
|-- callback.py            # framework callback integration
|-- decorators.py          # exemption / annotation surface
|-- launcher.py            # sidecar process launch + readiness coordination
|-- exceptions.py          # public exception hierarchy (QortaraError ...)
|-- otel.py                # OpenTelemetry / W3C trace-context propagation
|-- py.typed               # typing marker
|-- contract/
|   |-- protocol.py        # decision request/response protocol schema
|   |-- conformance.py     # conformance harness
|   |-- state.py           # protocol/runtime state
|-- patches/
    |-- registry.py        # patch registry (idempotent, reversible)
    |-- tool_patches.py    # LangChain BaseTool interception
    |-- langgraph_patches.py # LangGraph ToolNode interception
    |-- action_builder.py  # normalized governance-request construction
```

## Target Layered Architecture (post-AGT pivot, Phase 07–09)

```
Application / Agent Runtime
  -> Qortara Framework Adapter   (patches/, context.py, decorators.py)
  -> Decision source (one of):
       +-- AgtDecisionClient (agt_engine.py)  DEFAULT, in-process -> AGT PolicyEngine   (no sidecar)
       +-- SidecarClient (client.py)          OPTIONAL remote-daemon -> sidecar over /v0.1 HTTP
  -> (optional) Qortara hosted decision service + managed Azure   (see ARCHITECTURE-BOUNDARIES.md)
```

Local enforcement is **in-process** via Microsoft AGT's `agent_control_plane.PolicyEngine` (`init_agt`). The HTTP `SidecarClient` + `launcher.py` remain only for an optional remote-daemon deployment; no sidecar is required for the default local path.

## Interface Contracts

### `qortara_governance.init_agt(agent_id, allowed_tools)` (default local path)
- **Input**: an AGT policy role (`agent_id`) + its allow-list.
- **Output**: dispatch patch installed with an AGT-backed in-process decision source.
- **Side Effects**: patches `BaseTool.invoke`/`ToolNode.invoke`; decisions resolve via AGT `PolicyEngine.check_violation` (default-deny).

### `qortara_governance.init()` (optional remote-daemon path)
- **Input**: a sidecar endpoint (`QORTARA_SIDECAR_ENDPOINT`) or a spawnable sidecar binary.
- **Output**: dispatch patch installed with an HTTP `SidecarClient` decision source.
- **Side Effects**: connects to / launches the remote sidecar; raises `QortaraSidecarUnavailable` if unreachable.

### Decision sources (`agt_engine.py` / `client.py`)
- **Output**: decision state in {`allow`, `deny`, `require_approval`, `exempt`} + rationale + policy id.
- **Side Effects**: `AgtDecisionClient` — in-process AGT call (incl. arg-safety, Phase 09); `SidecarClient` — HTTP transport + circuit breaker; both fail-closed on uncertainty.

### Patch Registry (`patches/registry.py`)
- **Input**: target framework dispatch methods.
- **Output**: registered, reversible patches.
- **Side Effects**: idempotent interception; detects prior patching; preserves teardown restoration.

## Data Flow

agent invocation -> framework dispatch -> Qortara adapter -> **AGT in-process PolicyEngine** (default) -> (allow -> tool executes | deny/require_approval -> blocked) -> evidence event. (Optional remote-daemon mode substitutes an HTTP sidecar for the in-process engine.)

## Dependencies

| Package | Justification | Vanilla Alternative |
|---------|---------------|---------------------|
| `langchain-core` | dispatch interception target (`BaseTool`) | no |
| `langgraph` | dispatch interception target (`ToolNode`) | no |
| `opentelemetry-*` | W3C trace-context propagation | partial (manual) |
| `agent-governance-toolkit-{core,protocols,integrations}` | **in-process policy decision engine (AGT)** | no — the foundation (ADR-0001) |
| `qortara-protocol` | decision request/response contract | no |

## Section 4 Razor Pre-Check
- [ ] All planned functions <= 40 lines (verify per-cycle; existing code not yet audited)
- [ ] All planned files <= 250 lines (verify per-cycle)
- [ ] No planned nesting > 3 levels

## Resolved since genesis (Phases 01–09)
- ~~Default `init()` depends on an undelivered sidecar~~ → **resolved**: `init_agt()` uses AGT's in-process engine (Phase 08); sidecar is now optional remote-daemon.
- ~~Version drift (0.2.0 vs 0.2.1)~~ → **resolved** (Phase 01: `__version__` 0.2.1 + consistency test).
- ~~Conformance coverage unenumerated~~ → **resolved** (Phase 06: BaseTool sync/async conformance; Phase 08/09: AGT enforcement + arg-safety).

## Open follow-ups
- `qortara_protocol` ↔ `agent-governance-toolkit-protocols` reconcile; sidecar/client/launcher cleanup; LangGraph `ToolNode` → AGT wiring.

---
*Blueprint sealed. Awaiting GATE tribunal.*
