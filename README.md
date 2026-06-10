<div align="center">

# Qortara Governance

**Tool-dispatch policy enforcement for AI agents — at the boundary your agent actually crosses.**

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#packages)
[![Discussions](https://img.shields.io/github/discussions/MythologIQ-Labs-LLC/qortara-governance)](https://github.com/MythologIQ-Labs-LLC/qortara-governance/discussions)

</div>

---

## What this is

A Python monorepo of framework-specific adapters that intercept tool dispatch in AI agents and route each call through a local policy decision point before execution.

Most agent governance hooks into callbacks or wraps tools. That's observation, not enforcement: the dispatch path that native tool-calling agents take can route around it. These adapters sit on the dispatch funnel itself — `BaseTool.run`/`.arun` (which `invoke`/`ainvoke` and streaming all flow through), `ToolNode.invoke`/`.ainvoke`, and equivalents in other frameworks — so policy decisions are synchronous, deterministic, and bypass-resistant for any code using the framework's own dispatch. The boundary is cooperative-process: code that calls a tool's private implementation directly is out of scope (see [`docs/security/THREAT-MODEL.md`](docs/security/THREAT-MODEL.md) §5).

**Built on Microsoft AGT.** qortara extends the [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) (MIT) as a dependency — AGT supplies the policy engine, identity, sandboxing, and OWASP-Agentic compliance; qortara adds the bypass-resistant dispatch-path hook (closing AGT #73) and an optional Azure upstream. It does not vendor or modify AGT. See [`docs/adr/0001`](docs/adr/0001-agt-foundation-vendoring.md).

## Public and hosted layers

`qortara-governance` is the open integration and deterministic enforcement layer.

It can run locally with policy packs, local audit events, and no hosted dependency. Qortara's licensed hosted platform adds proportional authority evaluation, cumulative and sequence-aware risk analysis, adaptive escalation, tenant policy, managed approvals, and enterprise enforcement on Azure.

The public package exposes the request, response, adapter, and enforcement contracts. It does not expose the proprietary algorithms used by the hosted decision service.

See [`docs/ARCHITECTURE-BOUNDARIES.md`](docs/ARCHITECTURE-BOUNDARIES.md) for the full responsibility and capability split.

## Packages

| Package | Status | PyPI | Description |
|---|---|---|---|
| [`qortara-governance-langchain`](packages/qortara-governance-langchain) | Alpha (v0.2.x) | [![PyPI](https://img.shields.io/pypi/v/qortara-governance-langchain.svg)](https://pypi.org/project/qortara-governance-langchain/) | LangChain + LangGraph adapter |

The monorepo is structured so framework-specific adapters could live as additional `packages/*` members reusing the framework-agnostic core, but the current scope is the LangChain/LangGraph adapter only.

## Quickstart

For LangChain / LangGraph:

```bash
pip install qortara-governance-langchain
```

```python
import qortara_governance
from qortara_governance import AgentContext, set_context

# Local enforcement, in-process via the bundled AGT engine — no sidecar required.
qortara_governance.init_agt(agent_id="my-agent", allowed_tools=["search", "read_file"])
set_context(AgentContext(tenant_id="t", agent_id="my-agent", session_id="s"))

# Existing LangChain code runs unchanged. Tool dispatches now pass through the
# AGT policy engine before execution: allow-listed tools run, others are denied
# (QortaraPolicyDenied) before the tool body executes.
```

For a remote/daemon deployment, `qortara_governance.init()` connects to a sidecar over `QORTARA_SIDECAR_ENDPOINT` instead of the in-process engine.

Full integration guide: [`packages/qortara-governance-langchain/README.md`](packages/qortara-governance-langchain/README.md).

## Layout

```
qortara-governance/
├── packages/
│   └── qortara-governance-langchain/   LangChain + LangGraph adapter
├── docs/
│   └── ARCHITECTURE-BOUNDARIES.md       Public, hosted, and Azure boundaries
├── pyproject.toml                       uv workspace config
└── .github/                             shared CI + issue templates
```

Each package is independently versioned and released to PyPI. Workspace-level concerns (code of conduct, contributing, security policy, license) live at the root.

## Development

This workspace uses [`uv`](https://docs.astral.sh/uv/) workspaces.

```bash
uv sync --all-extras                                              # install everything
uv run --package qortara-governance-langchain pytest              # run package tests
uv tool run ruff check .                                          # lint workspace
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributor Covenant applies — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Discussions open at [GitHub Discussions](https://github.com/MythologIQ-Labs-LLC/qortara-governance/discussions).

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md). Do not file public issues for security reports.

## License

Apache-2.0. See [LICENSE](LICENSE).

LangChain, LangGraph, and LangSmith are trademarks of LangChain, Inc. Qortara is a trademark of MythologIQ Labs, LLC. See per-package `TRADEMARKS.md` files for details.
