<div align="center">

# qortara-governance-langchain

**Policy enforcement for LangChain and LangGraph agents — at the point of tool dispatch.**

[![PyPI](https://img.shields.io/pypi/v/qortara-governance-langchain.svg)](https://pypi.org/project/qortara-governance-langchain/)
[![Python](https://img.shields.io/pypi/pyversions/qortara-governance-langchain.svg)](https://pypi.org/project/qortara-governance-langchain/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#project-status)

</div>

---

## The problem

If you've added a callback handler or a tool wrapper to govern your LangChain agents, there's a good chance some calls walk past it.

Native tool-calling agents — anything using `OpenAIToolsAgent`, `create_tool_calling_agent`, structured-output binding, or LangGraph's `ToolNode` — dispatch through `BaseTool.invoke`. Callbacks fire **around** that path; they observe, they don't gate. Wrappers govern the tools they wrap, but unwrapped tools (sub-agents, dynamically loaded tools, `ToolNode` paths) bypass them entirely.

This is the "wrapper-bypass" gap [tracked as AGT issue #73](https://github.com/microsoft/agent-governance-toolkit/issues/73): observability is not enforcement.

> **Built on AGT.** qortara extends Microsoft's [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) (a dependency, MIT) rather than reimplementing it: AGT provides the policy engine, identity, sandboxing, and OWASP-Agentic compliance; qortara adds the bypass-proof dispatch-path hook that closes #73 and routes decisions into AGT's engine. See [`docs/adr/0001`](../../docs/adr/0001-agt-foundation-vendoring.md). Requires Python ≥3.11 (AGT 4.0 floor).

## What this package does

It places a synchronous decision point on the dispatch path itself:

```
                      ┌──────────────┐
                      │ AgentExec    │
                      └──────┬───────┘
                             │ resolve tool
                             ▼
                  ┌──────────────────────┐
                  │  BaseTool.run()      │  ← intercepted
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Policy evaluation   │
                  │ (in-process AGT, or  │
                  │   remote sidecar)    │
                  └──────────┬───────────┘
            allow │ deny │ approval │ exempt
            ──────┼──────┼──────────┼──────
                  ▼     raise      raise
            tool runs  exception  exception
```

The hook sits on `BaseTool.run`/`.arun` — the dispatch funnel that `invoke()` and `ainvoke()` both call — so `invoke`, `ainvoke`, `run`, and `arun` are all governed by one decision per dispatch. Denied calls raise `QortaraPolicyDenied`; calls requiring human approval raise `QortaraApprovalRequired` with an approval URL; allowed calls execute normally. No tool rewriting, no callback re-registration, no agent code changes. (The per-subclass private impls `_run`/`_arun` are not patchable at the `BaseTool` class level; calling them directly to skip dispatch is the cooperative-process boundary — see THREAT-MODEL §5.)

## Quickstart

```bash
pip install qortara-governance-langchain

# Optional — LangGraph support:
pip install 'qortara-governance-langchain[langgraph]'
```

```python
import qortara_governance
from qortara_governance import AgentContext, set_context
from langchain_core.tools import tool
from langchain.agents import AgentExecutor

# Local enforcement, in-process via the bundled Microsoft AGT engine (no sidecar).
qortara_governance.init_agt(agent_id="my-agent", allowed_tools=["lookup"])
set_context(AgentContext(tenant_id="t", agent_id="my-agent", session_id="s"))
# (Remote/daemon deployments use qortara_governance.init() + QORTARA_SIDECAR_ENDPOINT instead.)

@tool
def send_email(to: str, body: str) -> str:
    """Send an email."""
    ...

agent_executor = AgentExecutor(agent=agent, tools=[send_email])

try:
    result = agent_executor.invoke({"input": "Email finance the Q3 numbers."})
except qortara_governance.QortaraPolicyDenied as denied:
    log.warning("blocked by policy: %s", denied.rationale)
except qortara_governance.QortaraApprovalRequired as needs_approval:
    log.info("approval needed at: %s", needs_approval.approval_url)
```

Requires Python 3.11+ and `langchain-core >= 0.3`.

## Decision model

Every intercepted call resolves to one of four states:

| Decision | SDK behavior | When |
|---|---|---|
| `allow` | Execute the tool normally | Routine, low-blast-radius calls |
| `deny` | Raise `QortaraPolicyDenied` with rationale + policy ID | Hard-stop policies (compliance, classification, locked-down tools) |
| `require_approval` | Raise `QortaraApprovalRequired` with an approval URL | Higher-blast-radius calls that should pause for a human |
| `exempt` | Execute without evaluation, but emit evidence | Pre-trusted tools (clocks, ID generators) |

**Which plane emits which decision.** The in-process AGT engine (`init_agt`) is **binary — `allow` or `deny`** (default-deny, fail-closed); it does not emit `require_approval`. `require_approval` (and the transform kinds `downgrade`/`redact`/`sandbox`) come from the **remote sidecar / hosted decision plane** (`init`). The SDK routes whatever it receives: `require_approval` → `QortaraApprovalRequired`; any decision kind it does not implement (the transform kinds) → **deny-closed** with a rationale. Separately, `policy_mode="observe"` turns every would-be block into a logged-but-allowed shadow decision (see [Configuration](#configuration)).

Exempt tools opt out of evaluation but still produce an audit record:

```python
from qortara_governance import qortara_exempt

@qortara_exempt
@tool
def read_clock() -> str:
    """Trusted internal tool — no policy evaluation."""
    return datetime.utcnow().isoformat()
```

## Where the SDK ends and other concerns begin

This package is an **enforcement point**, not a complete governance system:

| Concern | Where it lives |
|---|---|
| Tool-dispatch interception | This SDK |
| Local policy evaluation | Bundled sidecar |
| Evidence signing (Ed25519, RFC 8785 JCS, SHA-256) | Sidecar |
| Policy authoring, versioning, distribution | Local policy pack OR Qortara Cloud Governance |
| Cross-organization identity, trust, federation | Qortara Cloud Governance |
| Multi-tenant evidence ledger and retention | Qortara Cloud Governance |
| Compliance reporting and audit surfaces | Qortara Cloud Governance |

For air-gapped or local-only deployments: use `init_agt(...)`, which runs the decision engine (Microsoft AGT) **in-process** with no sidecar and no network dependency (see ADR-0001).

For hosted policy distribution and cross-organization features: provide a `tenant_key` and Qortara Cloud Governance handles policy sync, federation, and long-term retention. Nothing in this package requires the hosted plane.

## Sidecar (optional remote-daemon mode)

> **Default is in-process.** `init_agt(...)` runs the decision engine (Microsoft AGT) inside your process — **no sidecar required**. The sidecar below is an *optional* remote-daemon deployment selected via `init()`; the diagrams/tables in this section describe that mode.

The SDK can alternatively talk to a remote sidecar over HTTP. Two run modes:

- **Subprocess** — `init()` spawns the sidecar as a child process bound to `127.0.0.1` on an ephemeral port. Terminates with the parent.
- **Daemon** — run the sidecar externally and set `QORTARA_SIDECAR_ENDPOINT=http://host:port`. `init()` uses the existing endpoint instead of spawning.

If the sidecar becomes unreachable, the SDK enters a circuit-breaker state that **fails closed** for a short cooldown. Calls during that window raise `QortaraSidecarUnavailable`.

## Configuration

| Option | Env var | Default | Notes |
|---|---|---|---|
| `tenant_key` | `QORTARA_TENANT_KEY` | *(none)* | Required for hosted decisions; optional for local-only policy packs |
| `sidecar_endpoint` | `QORTARA_SIDECAR_ENDPOINT` | *(spawn subprocess)* | Set to use an external daemon |
| `policy_mode` | `QORTARA_POLICY_MODE` | `enforce` | `enforce` raises on a non-permit decision; `observe` is a shadow/dry-run mode that logs every would-be block at WARNING (via the `qortara_governance` logger) and lets execution proceed. Honoured by both `init()` and `init_agt(policy_mode=...)`. |

Resolution order: `init()` kwarg → env var → default.

> Air-gapped / offline policy evaluation is provided by `init_agt(...)` (in-process AGT), not a config flag.

### Ungoverned dispatch (no agent context)

Once `init()`/`init_agt()` patch the tool-dispatch methods, a dispatch off a code path that never set an `AgentContext` runs **ungoverned** (policy cannot evaluate it). The SDK emits a `QortaraUngovernedDispatchWarning` on each such call rather than failing closed by default, because the patched methods are process-global and some non-agent call paths legitimately run uncontextualized. To make ungoverned dispatch fail closed, escalate the category to an error:

```python
import warnings
from qortara_governance import QortaraUngovernedDispatchWarning

warnings.filterwarnings("error", category=QortaraUngovernedDispatchWarning)
```

## Observability

`QortaraCallbackHandler` is an additive LangChain callback for chain-boundary and retrieval events. It never blocks execution; safe to register alongside LangSmith or any other callback:

```python
from qortara_governance import QortaraCallbackHandler
chain.invoke({...}, config={"callbacks": [QortaraCallbackHandler()]})
```

W3C `traceparent` propagates on every sidecar call, so evidence records and LangSmith traces share trace IDs for correlation.

## Data handling

In the **default in-process mode** (`init_agt`), tool arguments are evaluated by the AGT policy engine **inside your process** — they never cross a network boundary. Argument-level checks (SQL/code/path) run only on this in-process path.

In the **optional remote sidecar mode** (`init()`), the SDK sends a normalized `ActionRequest` (tool identity, capability, trace + agent context) and does **not** inline the raw tool arguments over the wire — so the sidecar performs identity/role/policy decisions, not raw-argument inspection. Tool arguments may still be sensitive; in regulated environments review what the in-process engine sees and what (if anything) you forward to a remote sidecar, and ensure any sidecar storage satisfies your data-classification requirements.

Subprocess sidecar mode keeps all traffic on `localhost`; daemon mode depends on the network path you configure.

## Compatibility

| Dependency | Tested range |
|---|---|
| Python | 3.11, 3.12, 3.13 |
| `langchain-core` | `>= 0.3` — floor (`0.3.x`) **and** latest 1.x are exercised by CI |
| `langgraph` | `>= 0.2` (optional) — floor (`0.2.x`) exercised by CI |

Every cell is CI-verified, not asserted: a `compat-floor` job runs the full suite against the lower bound on each PR, so the claim and the test move together. Full matrix + rationale: [`docs/COMPATIBILITY.md`](../../docs/COMPATIBILITY.md). File an issue if you hit a patching regression on a version not yet covered.

## Project status

**Alpha.** Minor breaking changes may ship before 1.0. Evaluate carefully before production use and pin to a specific version. No warranty is provided; see [LICENSE](LICENSE).

The current test suite includes a regression test for the AGT issue #73 wrapper-bypass closure. Test fidelity rises with each release; production fidelity awaits 1.0.

## Roadmap

Tracked in [open issues](https://github.com/MythologIQ-Labs-LLC/qortara-governance/issues):

- Compatibility tracking against incoming LangChain 0.4 / 0.5 releases
- Additional examples (RAG retrieval governance, multi-agent supervisor with policy escalation)
- Sibling packages for CrewAI, LlamaIndex, AutoGen (separate adapter packages under the same workspace)
- LangSmith metadata integration so governance decisions surface in trace UIs
- v1.0 stabilization once the public API surface stops shifting

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md). Do not open public issues for security reports.

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md). Contributor Covenant applies — see [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md). Discussions open at [GitHub Discussions](https://github.com/MythologIQ-Labs-LLC/qortara-governance/discussions).

## Acknowledgments

The wrapper-bypass gap was first articulated in [Microsoft AGT issue #73](https://github.com/microsoft/agent-governance-toolkit/issues/73). This SDK closes it for LangChain.

LangChain, LangGraph, and LangSmith are trademarks of LangChain, Inc. `qortara-governance-langchain` is an independent project and is not affiliated with, endorsed by, or sponsored by LangChain, Inc.

Qortara is a trademark of MythologIQ Labs, LLC. See [TRADEMARKS.md](TRADEMARKS.md).

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
