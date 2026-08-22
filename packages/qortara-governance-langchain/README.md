<div align="center">

# qortara-governance-langchain

**Policy-mediated tool dispatch for LangChain and LangGraph agents.**

[![PyPI](https://img.shields.io/pypi/v/qortara-governance-langchain.svg)](https://pypi.org/project/qortara-governance-langchain/)
[![Python](https://img.shields.io/pypi/pyversions/qortara-governance-langchain.svg)](https://pypi.org/project/qortara-governance-langchain/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#project-status)

</div>

## Product-family boundary

This package is a framework adapter. It is **not** a Qortara product module.

Keep these concepts separate:

- **`qortara-governance-langchain`**: this public LangChain/LangGraph adapter package.
- **Qortara Agent Governance**: the managed Qortara product domain for authoritative governance state, evidence, operator workflows, controlled agent evolution, and authority management.
- **Qortara SDLC Governance**: one of the seven user-facing modules inside Qortara SDLC.

Qortara SDLC's canonical modules are Development, Governance, Evidence, Compliance, Oversight, Operations, and Administration. The authoritative taxonomy lives in [`qortara-sdlc/PRODUCT_MODULES.md`](https://github.com/MythologIQ-Labs-LLC/qortara-sdlc/blob/main/PRODUCT_MODULES.md).

The current published v0.2.x package line depends on Microsoft Agent Governance Toolkit 4.x packages. That is package-version truth, not the current hosted Qortara Agent Governance architecture. Do not infer the hosted runtime from this package's historical dependency line.

## What this package does

The package intercepts supported LangChain/LangGraph tool-dispatch paths and routes calls through policy evaluation before execution.

```text
agent resolves tool
      |
      v
BaseTool / ToolNode dispatch
      |
      v
Qortara adapter interception
      |
      v
policy evaluation
  | allow
  | deny
  | approval / other remote decision
      |
      v
execute or fail closed according to decision
```

The cooperative-process boundary matters: normal framework dispatch is mediated; code that directly invokes private tool implementations outside supported dispatch paths is outside this adapter's guarantee. See [`../../docs/security/THREAT-MODEL.md`](../../docs/security/THREAT-MODEL.md).

## Quickstart

```bash
pip install qortara-governance-langchain

# Optional LangGraph support
pip install 'qortara-governance-langchain[langgraph]'
```

```python
import qortara_governance
from qortara_governance import AgentContext, set_context

qortara_governance.init_agt(
    agent_id="my-agent",
    allowed_tools=["lookup"],
)

set_context(
    AgentContext(
        tenant_id="t",
        agent_id="my-agent",
        session_id="s",
    )
)
```

Requires Python 3.11+ and `langchain-core >= 0.3` for the current package line.

Remote/daemon mode uses `qortara_governance.init()` and the configured `QORTARA_SIDECAR_ENDPOINT` contract supported by this version.

## Decision model

The adapter handles policy decisions at the dispatch boundary.

| Decision | SDK behavior |
| --- | --- |
| `allow` | Execute the tool normally |
| `deny` | Raise `QortaraPolicyDenied` |
| `require_approval` | Raise `QortaraApprovalRequired` when emitted by the remote decision path |
| `exempt` | Execute according to the package's explicit exemption semantics while preserving the configured evidence behavior |

The bundled in-process AGT 4.x path used by this package line is binary allow/deny. Additional remote decision kinds are properties of the configured remote decision service, not proof that this package itself owns approval authority.

Unknown/unsupported decision kinds must not silently become permission.

## Enforcement is not product authority

This SDK is an interception/enforcement point, not a complete governance system.

| Concern | Authority |
| --- | --- |
| LangChain/LangGraph dispatch interception | This package |
| Package-local configuration and compatibility | This package and its tests |
| Managed tenant governance state and approvals | Owning Qortara Agent Governance services |
| Current hosted AGT/ACS architecture | `MythologIQ-Labs-LLC/Qortara` and current Microsoft upstream |
| Qortara SDLC product/module taxonomy | `MythologIQ-Labs-LLC/qortara-sdlc/PRODUCT_MODULES.md` |
| Compliance module semantics | Qortara SDLC + Qor Compliance authority where applicable |
| Oversight module semantics | Qortara SDLC + Qor Oversight authority where applicable |

A class name, adapter hook, or package identifier does not acquire cross-product authority merely by existing in the dispatch path.

## Local and remote modes

### In-process mode

`init_agt(...)` uses the AGT engine packaged for this release line inside the application process. No remote sidecar is required.

### Remote/daemon mode

`init(...)` uses the package's sidecar/remote decision client contract. The sidecar may be spawned locally or supplied through `QORTARA_SIDECAR_ENDPOINT`, depending on configuration and package support.

If a required remote decision service becomes unavailable, enforcement should fail closed according to the package's configured circuit-breaker behavior rather than converting unavailability into permission.

## Agent context

Set an `AgentContext` for governed dispatch:

```python
from qortara_governance import AgentContext, set_context

set_context(
    AgentContext(
        tenant_id="tenant-1",
        agent_id="agent-1",
        session_id="session-1",
    )
)
```

A process-global patch may also see calls that have no agent context. The package warns for ungoverned dispatch unless callers explicitly escalate that warning behavior. Read the threat model before treating process-global interception as a sandbox boundary.

## Evidence emission

The package can emit decision/execution evidence through configured sinks. Evidence emission is additive to enforcement and must not weaken the permit/deny path.

See [`../../docs/evidence-schema.md`](../../docs/evidence-schema.md) for the package's evidence contract.

## Configuration

Common configuration includes:

| Setting | Purpose |
| --- | --- |
| `QORTARA_SIDECAR_ENDPOINT` | Select an external remote/daemon decision endpoint |
| `QORTARA_POLICY_MODE` | Select enforcement versus supported observe/shadow behavior |
| tenant/context configuration | Bind requests to the caller's governance context |

Exact option names and defaults are version-specific. Use the package source/tests as authority when prose and behavior disagree.

## Security boundary

This adapter is not a kernel, VM boundary, sandbox, or universal Python execution reference monitor. Its guarantee is limited to the supported framework dispatch paths and configuration of the installed version.

Do not represent successful package interception as proof that arbitrary code cannot bypass governance. See:

- [`../../docs/security/THREAT-MODEL.md`](../../docs/security/THREAT-MODEL.md)
- [`../../SECURITY.md`](../../SECURITY.md)

## Project status

Alpha. The API and supported framework/runtime coverage may change.

The v0.2.x line remains an AGT 4.x-based published package. Migration to newer ACS-native runtime primitives, if/when performed for this public line, requires an explicit compatibility release rather than a README-only relabeling exercise.

## Development

From the repository root:

```bash
uv sync --all-extras
uv run --package qortara-governance-langchain pytest
uv tool run ruff check .
```

## License

Apache-2.0. See [`LICENSE`](LICENSE).

LangChain, LangGraph, and LangSmith are trademarks of LangChain, Inc. Qortara is a trademark of MythologIQ Labs, LLC.
