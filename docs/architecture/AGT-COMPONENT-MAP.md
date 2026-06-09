# AGT Component Map (foundation analysis)

**Purpose:** Ground-truth map of `microsoft/agent-governance-toolkit` (AGT) for the decision to build qortara-governance on it. Companion to [ADR 0001](../adr/0001-agt-foundation-vendoring.md).

**Source inspected:** `github.com/microsoft/agent-governance-toolkit` — repo **v3.7.0**, commit `83cf9c2f161c43ad17e446e890e2a9d5e050127c`, **MIT © Microsoft Corporation**. Inspected via scratch clone (not vendored).

## AGT is a polyglot governance monorepo

Top-level language stacks: `agent-governance-python`, `-dotnet`, `-golang`, `-rust`, `-typescript`, plus a Rust `policy-engine/` and host CLIs (claude-code, copilot-cli, …).

## LangChain-relevant components

| AGT component | Path | Language | Package / version | What it is |
|---|---|---|---|---|
| **ACS policy-engine** | `policy-engine/` + `policy-engine/sdk/python` | **Rust core + Python SDK** | `agent-control-specification` **0.3.1b0** (Rust via Cargo) | Policy decision engine ("Agent Control Specification"). Python SDK ships a **LangChain adapter** that *"guards a BaseTool-style object via pre/post_tool_call"* (`_adapters/langchain.py:60`) + an `acs-sidecar-reference` (k8s). **Closest match to qortara's BaseTool-patch + sidecar enforcement model.** |
| **agent-mesh governance** | `agent-mesh/src/agentmesh/governance/` | Python | `agentmesh_platform` **4.0.0** | Authority/policy evaluation. Defines its *own* `ActionRequest` (action_type, tool_name, resource, parameters, requested_spend) + `AuthorityDecision` (allow / allow_narrowed / deny / audit). |
| **langchain-agentmesh** | `agentmesh-integrations/langchain-agentmesh/` | Python | (integration) | **Callback-level** LangChain adapter (`callbacks.py`). This is the *observation, not enforcement* approach qortara's README critiques (AGT issue #73 / wrapper-bypass). |
| **IATP sidecar** | `agent-os/modules/iatp/` | Python (FastAPI) + Go | `inter-agent-trust-protocol` **3.1.0** | A **trust proxy** sidecar: capability-manifest exchange, attestation, reputation/slashing, privacy. **Different concern** (agent-to-agent trust), not tool-dispatch policy decisions. |

## How qortara relates today (important)

- **`qortara_protocol` (0.1.2) is independent, NOT AGT's contract.** It re-uses the names `ActionRequest`/`ActionDecision` but is a distinct, richer pydantic contract: `schema_version, tenant_id, agent_id, session_id, framework, action_type, target_resource, requested_capability, risk_tier, trust_state, execution_stage, trace_context` → `ActionDecision` with `DecisionKind ∈ {allow, deny, require_approval, downgrade, redact, sandbox, exempt, observe}`. AGT's agent-mesh `ActionRequest` is a slimmer, different shape. **There is no existing wire-compatibility** between qortara and any AGT component.
- **qortara's SDK** (`BaseTool.invoke`/`ainvoke` patch in `patches/tool_patches.py`) is dispatch-path enforcement — conceptually the same intent as ACS's `pre/post_tool_call` LangChain adapter, but a *different* mechanism (monkeypatch vs wrapper) and a different protocol.
- **The S1 sidecar built this session** (`packages/qortara-governance-sidecar/`) is a from-scratch evaluator that **duplicates the foundation's role**. Under an AGT-foundation strategy it should be retired or demoted to a local test-double.

## Consequence for "vendor the langchain sidecar"

There is no single artifact literally named "langchain sidecar." The enforcement foundation that matches qortara is **ACS policy-engine**, which is **Rust + Python**. Vendoring it wholesale means copying a Microsoft **Rust crate** into an Apache-2.0 Python monorepo, plus reconciling two *different* decision protocols (`qortara_protocol` ↔ ACS). That is materially larger than a Python file copy and is the central risk ADR 0001 weighs.
