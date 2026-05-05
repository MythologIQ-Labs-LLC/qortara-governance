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

Most agent governance hooks into callbacks or wraps tools. That's observation, not enforcement: the dispatch path that native tool-calling agents take can route around it. These adapters sit on the dispatch path itself — `BaseTool.invoke`, `ToolNode.invoke`, and equivalents in other frameworks — so policy decisions are synchronous, deterministic, and impossible to bypass.

## Packages

| Package | Status | PyPI | Description |
|---|---|---|---|
| [`qortara-governance-langchain`](packages/qortara-governance-langchain) | Alpha (v0.2.x) | [![PyPI](https://img.shields.io/pypi/v/qortara-governance-langchain.svg)](https://pypi.org/project/qortara-governance-langchain/) | LangChain + LangGraph adapter |

Sibling packages for CrewAI, LlamaIndex, and AutoGen are planned as additional `packages/*` members under the same workspace. See [open issues](https://github.com/MythologIQ-Labs-LLC/qortara-governance/issues) tagged `help wanted`.

## Quickstart

For LangChain / LangGraph:

```bash
pip install qortara-governance-langchain
```

```python
import qortara_governance

qortara_governance.init()

# Existing LangChain code runs unchanged.
# Tool dispatches now pass through policy evaluation before execution.
```

Full integration guide: [`packages/qortara-governance-langchain/README.md`](packages/qortara-governance-langchain/README.md).

## Layout

```
qortara-governance/
├── packages/
│   └── qortara-governance-langchain/   LangChain + LangGraph adapter
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
