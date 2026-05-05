# qortara-governance

Python workspace for Qortara Governance framework adapters.

Tool-dispatch policy enforcement for AI-agent frameworks. Enforcement happens at the dispatch boundary — the path native tool-calling agents actually take — not just the callback surface that wrapper-based governance can observe.

## Packages

| Package | Status | PyPI |
|---|---|---|
| [`qortara-governance-langchain`](packages/qortara-governance-langchain) | Alpha (v0.2.x) | [pypi.org/project/qortara-governance-langchain](https://pypi.org/project/qortara-governance-langchain/) |

Adapters for additional frameworks (CrewAI, LlamaIndex, AutoGen) are planned as sibling packages under `packages/`.

## Layout

```
qortara-governance/
├── packages/
│   └── qortara-governance-langchain/   LangChain + LangGraph adapter
├── pyproject.toml                       uv workspace config
└── .github/                             shared CI + issue templates
```

Each package is independently versioned and released to PyPI. Shared concerns — code of conduct, contributing, security policy, license — live at the workspace root.

## Development

This workspace uses [`uv`](https://docs.astral.sh/uv/) workspaces.

```bash
# Install all packages and their dev dependencies
uv sync --all-extras

# Run tests for a specific package
uv run --package qortara-governance-langchain pytest

# Lint the whole workspace
uv tool run ruff check .
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributor Covenant applies — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md).

## License

Apache-2.0. See [LICENSE](LICENSE).

LangChain, LangGraph, and LangSmith are trademarks of LangChain, Inc. Qortara is a trademark of MythologIQ Labs, LLC — see individual package `TRADEMARKS.md` files for details.
