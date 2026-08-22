<div align="center">

# qortara-governance

**Public framework adapter packages for policy-mediated AI agent tool dispatch.**

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#packages)

</div>

## Product-family boundary

This repository is easy to misread because its historical name overlaps two current Qortara concepts. The distinctions are intentional:

- **`qortara-governance` repository**: public/open framework adapter and enforcement-package workspace described by this README.
- **Qortara Agent Governance**: the managed Qortara product domain for authoritative governance state, evidence, operator workflows, controlled agent evolution, and authority management.
- **Qortara SDLC Governance module**: one of the seven user-facing modules inside Qortara SDLC.

This repository is **not** the Qortara SDLC Governance module and is **not** the complete Qortara Agent Governance product.

Qortara SDLC itself has seven canonical modules:

1. Development
2. Governance
3. Evidence
4. Compliance
5. Oversight
6. Operations
7. Administration

The authoritative SDLC module taxonomy lives in [`MythologIQ-Labs-LLC/qortara-sdlc/PRODUCT_MODULES.md`](https://github.com/MythologIQ-Labs-LLC/qortara-sdlc/blob/main/PRODUCT_MODULES.md). This repository does not redefine it.

## What this repository is

A Python monorepo of framework-specific adapters that intercept supported AI-agent tool-dispatch paths and route calls through policy evaluation before execution.

The current published `qortara-governance-langchain` v0.2.x line is an **alpha LangChain/LangGraph adapter**. Its repository dependency contract is still based on Microsoft Agent Governance Toolkit 4.x packages. That fact is specific to this package line and must not be used to infer the current hosted Qortara Agent Governance runtime architecture.

Current Qortara hosted architecture and AGT/ACS integration are governed in the `MythologIQ-Labs-LLC/Qortara` repository. Package evolution should follow explicit compatibility and migration work rather than silently projecting hosted architecture backward onto this published adapter.

## Packages

| Package | Status | Purpose |
| --- | --- | --- |
| [`qortara-governance-langchain`](packages/qortara-governance-langchain) | Alpha, v0.2.x line | LangChain/LangGraph tool-dispatch adapter |

The workspace may host additional framework-specific adapters only when there is a concrete compatibility need. A new package is not automatically a new Qortara product or SDLC module.

## Current enforcement boundary

The LangChain/LangGraph adapter targets cooperative in-process dispatch paths such as `BaseTool.run` / `.arun` and `ToolNode.invoke` / `.ainvoke`.

It can mediate normal framework dispatch, but code that bypasses the supported framework path and invokes private implementations directly is outside that cooperative-process boundary. See [`docs/security/THREAT-MODEL.md`](docs/security/THREAT-MODEL.md).

The adapter does not become authoritative merely because it intercepts a call. Product/tenant authority, managed approvals, durable governance state, and current hosted runtime policy architecture belong to their owning Qortara product services.

## Quickstart

For the current published LangChain/LangGraph adapter:

```bash
pip install qortara-governance-langchain
```

```python
import qortara_governance
from qortara_governance import AgentContext, set_context

qortara_governance.init_agt(
    agent_id="my-agent",
    allowed_tools=["search", "read_file"],
)
set_context(
    AgentContext(
        tenant_id="t",
        agent_id="my-agent",
        session_id="s",
    )
)
```

For remote/daemon mode, `qortara_governance.init()` uses the configured `QORTARA_SIDECAR_ENDPOINT` according to this package line's supported contract.

Full package guide: [`packages/qortara-governance-langchain/README.md`](packages/qortara-governance-langchain/README.md).

## Architecture ownership

| Concern | Owning source |
| --- | --- |
| This public adapter/package line | This repository and package tests |
| Current Qortara Agent Governance product architecture | `MythologIQ-Labs-LLC/Qortara` |
| Qortara SDLC product/module taxonomy | `MythologIQ-Labs-LLC/qortara-sdlc/PRODUCT_MODULES.md` |
| Microsoft AGT / ACS runtime semantics | Current Microsoft upstream packages/specification |

When those sources differ, do not paper over the difference with prose. Treat it as a version/migration boundary and document it explicitly.

## Layout

```text
qortara-governance/
├── packages/
│   └── qortara-governance-langchain/
├── docs/
│   ├── ARCHITECTURE-BOUNDARIES.md
│   └── security/
├── pyproject.toml
└── .github/
```

## Development

This workspace uses `uv` workspaces.

```bash
uv sync --all-extras
uv run --package qortara-governance-langchain pytest
uv tool run ruff check .
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately. See [SECURITY.md](SECURITY.md). Do not file public issues for security reports.

## License

Apache-2.0. See [LICENSE](LICENSE).

LangChain, LangGraph, and LangSmith are trademarks of LangChain, Inc. Qortara is a trademark of MythologIQ Labs, LLC.
