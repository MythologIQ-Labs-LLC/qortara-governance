# Research Brief — AxonFlow comparative analysis

**Date**: 2026-06-09
**Analyst**: The Qor-logic Analyst
**Target**: AxonFlow (`getaxonflow.com` / `github.com/getaxonflow/axonflow`) vs qortara-governance + Microsoft AGT
**Scope**: Verify AxonFlow exists; characterize its category, enforcement model, capabilities, and license; compare to qortara+AGT on agent governance / tool-dispatch policy enforcement.

> **Sourcing note:** This is competitive research grounded in public web sources (not a codebase scan). Claims are attributed; figures quoted from AxonFlow's own GitHub/docs are "as-documented" and were not independently re-derived. Name collisions exist — `axonflow.in` (an unrelated "AI agency") and an AxonFlow legal-research SaaS are **not** the comparator. The comparator is the **getaxonflow.com** governance control plane.

---

## Executive Summary

AxonFlow is **verified real**: a source-available (BSL 1.1) **runtime AI control plane**, written primarily in Go, that enforces policy as an **inline service** (gateway/proxy modes + a Workflow Control Plane) which applications call via HTTP/SDKs. It is a **peer/competitor to Microsoft AGT** (both are broad governance control planes), not to qortara specifically. qortara's distinct value — **in-process, bypass-proof interception of the native LangChain `BaseTool.invoke` dispatch path** — is precisely the gap an AxonFlow-style "route your calls through our SDK/proxy" model does **not** cover for native tool-calling agents unless every call site is explicitly wired. The comparison reinforces qortara's niche rather than threatening it.

## Findings

### AxonFlow — category & positioning
- "Runtime Control Layer for Production AI" / "Enterprise AI Control Plane." Source: [getaxonflow.com](https://getaxonflow.com/), [docs.getaxonflow.com](https://docs.getaxonflow.com/).
- Self-hosted services: Agent on `:8080`, Orchestrator on `:8081`; runs entirely in the customer's infra (SaaS / cloud-account / on-prem options). Source: [search overview], [GitHub](https://github.com/getaxonflow/axonflow).

### AxonFlow — enforcement model (the key axis)
- **Multiple interception modes**, all call-site/inline: **Gateway** ("pre-check + your own LLM call + audit"), **Proxy** (AxonFlow proxies model/tool execution), **Workflow Control Plane** (step-level gates, durable ledger, cancellation, SSE). Source: [GitHub](https://github.com/getaxonflow/axonflow).
- **Framework-agnostic, not framework-coupled**: "Works with LangChain, CrewAI, or any framework — AxonFlow acts as a governance sidecar." Integration via **HTTP REST + SDKs (Python/TS/Go/Java/Rust) + MCP connectors**. **No native LangChain callback or monkeypatch.** Source: [GitHub](https://github.com/getaxonflow/axonflow).
- Python SDK is opt-in at the call site:
  ```python
  async with AxonFlow(endpoint="http://localhost:8080") as ax:
      response = await ax.proxy_llm_call(user_token="user-123", query="...", request_type="chat")
  ```
  → governance applies **only to calls explicitly routed through AxonFlow**.

### AxonFlow — capabilities
- 60+ built-in policies; SQL-injection (37 patterns), PII (SSN/credit-card/medical), compliance (GDPR/PCI-DSS/HIPAA/EU AI Act). Media + code governance. Source: [GitHub](https://github.com/getaxonflow/axonflow), [docs audit-logging](https://docs.getaxonflow.com/docs/governance/audit-logging/).
- Multi-Agent Planning (YAML-defined agents → executable workflows); immutable audit logs; sub-10ms P95 enforcement (as-documented). Source: [search overview].
- A **Claude Code governance plugin** exists ([getaxonflow/axonflow-claude-plugin](https://github.com/getaxonflow/axonflow-claude-plugin)) — blocks dangerous commands, governs MCP/command execution.

### AxonFlow — license & language
- **BSL 1.1** (converts to Apache-2.0 after 4 years) — source-available, **not** OSI-open initially. Primary language **Go (~95.7%)**. Source: [GitHub](https://github.com/getaxonflow/axonflow).

### qortara + AGT (this project, for contrast)
- qortara: **in-process monkeypatch** of `BaseTool.invoke`/`ToolNode.invoke` — synchronous, fail-closed, governs native tool-calling dispatch that callbacks/wrappers miss (the AGT #73 closure). Apache-2.0, Python, alpha.
- Foundation: **Microsoft AGT** (MIT) — in-process `PolicyEngine` (default-deny), identity, sandbox, SRE, OWASP. qortara extends AGT (ADR-0001).

## Comparison

| Axis | AxonFlow | qortara + AGT |
|---|---|---|
| Category | Broad runtime control plane (service) | Narrow in-process LangChain enforcement layer on AGT |
| Enforcement locus | Inline gateway/proxy; **call sites must route through it** (HTTP/SDK/MCP) | **Dispatch-path monkeypatch** — governs even un-wrapped/native tool calls |
| LangChain coupling | Framework-agnostic; no native callback/patch | Deep `BaseTool`/`ToolNode` interception |
| Bypass exposure | A tool call that doesn't call AxonFlow is ungoverned | Native dispatch is intercepted regardless of call site (cooperative-process boundary only) |
| Breadth | High (multi-modal, MAP, WCP, 60+ policies, 5 SDKs) | Low (LangChain/LangGraph, Python) — leans on AGT for engine breadth |
| Deployment | Self-hosted services (`:8080/:8081`) | In-process (no service needed locally, post-Increment-B) |
| License | BSL 1.1 → Apache-2.0 (source-available) | Apache-2.0 (qortara) + MIT (AGT) — fully OSI-open |
| Maturity | Productized, multi-language | Alpha |

## Implications for qortara (architecture/positioning)

| Consideration | Finding | Status |
|---|---|---|
| AxonFlow is a direct qortara competitor | No — it's an AGT-class control plane; qortara's dispatch-path niche is orthogonal | DIFFERENTIATED |
| AxonFlow covers the #73 dispatch-bypass for LangChain | No — its model is call-site/proxy routing; native `BaseTool.invoke` bypass is exactly what it doesn't natively intercept | qortara EDGE |
| Licensing posture | qortara+AGT is fully OSI-open (Apache+MIT); AxonFlow is BSL-restricted for 4y | qortara EDGE (openness) |
| Breadth gap | AxonFlow's policy/compliance/multi-modal/multi-language breadth far exceeds qortara's | qortara GAP (mitigated by leaning on AGT) |

## Recommendations

1. **Positioning (P1):** Frame qortara explicitly as *"bypass-proof dispatch-path enforcement for LangChain/LangGraph"* — the one thing call-site/proxy control planes (AxonFlow-style) structurally cannot guarantee for native tool-calling. This is the durable differentiator; make it the headline.
2. **Competitive doctrine (P2):** Record AxonFlow as an *AGT-class control plane* (peer to the foundation), not a qortara competitor — avoid feature-parity chasing on breadth (MAP/WCP/multi-modal); double down on the dispatch-path moat.
3. **Watch item (P3):** AxonFlow markets a "governance sidecar" that "works with LangChain." If it adds *native* `BaseTool.invoke` interception, the differentiation narrows — monitor `getaxonflow/axonflow` for a LangChain dispatch-level adapter.
4. **No architecture change.** This research does not alter ADR-0001 or the in-progress arg-safety follow-up.

## Updated Knowledge

Add to competitive doctrine (informal, this brief): AxonFlow ≈ AGT-class control plane (BSL 1.1, Go, inline gateway/proxy, framework-agnostic via SDK/HTTP/MCP). qortara's moat = in-process dispatch-path interception (#73), not breadth.

---

_Research complete. Findings are advisory — implementation decisions remain with the Governor._

---

## Correction — operator feedback (2026-06-09)

The original comparison **understated qortara** on two axes. Corrected:

### 1. Breadth was wrong (retracted "Low / GAP")
qortara depends on the **full AGT library surface** (`agent-governance-toolkit-{core,protocols,integrations}`), so it **inherits AGT's entire breadth** — policy engine, zero-trust identity, execution sandboxing, SRE, OWASP-Agentic compliance, MAP/WCP — and *adds* the bypass-proof dispatch hook on top. The "Breadth: Low" and "qortara GAP (breadth)" rows are **retracted**. Correct framing: **AGT-class (full) breadth + the dispatch-path moat** — parity-plus over an AGT-class control plane, not a subset.

### 2. Upstream authoritative decision engine (PAMA) was omitted
The architecture is **three-tier**, not two:

```
qortara dispatch hook (bypass-proof interception)
   -> AGT in-process PolicyEngine        (local authoritative decision)
   -> PAMA upstream authoritative engine  (centralized / governed adaptive-state plane)
```

PAMA provides a centralized **authoritative** decision tier *and* governed **adaptive-state** governance — a dimension beyond AxonFlow's documented control-plane scope.

**Sourcing caveat (Analyst honesty):** "PAMA" is **operator-asserted**. It is not present in AGT, the installed packages, or the working tree; the beta roadmap (PR #11) references it once as a post-Beta item — *"PAMA or governed adaptive-state implementation"* (§26) — without expanding the acronym. Recorded as a Qortara-internal concept **pending a canonical definition/source to cite**.

### Corrected comparison rows
| Axis | AxonFlow | qortara + AGT (+ PAMA) |
|---|---|---|
| Breadth | High (control plane) | **AGT-class full breadth + dispatch-path moat** (parity-plus, not a gap) |
| Authoritative / central plane | Its own control plane | AGT local engine **+ PAMA upstream authoritative engine** |
| Adaptive-state governance | Not documented | **PAMA governed adaptive-state** (Qortara architecture; roadmap §24/§26) |
| Native dispatch bypass (#73) | Uncovered (route-through model) | Closed (in-process patch) |

### Revised bottom line
qortara + AGT (+ PAMA) is **not** a narrow niche tool. It is an **AGT-class governance stack** that additionally (a) closes the native-dispatch bypass AxonFlow's call-site model leaves open, and (b) adds an **upstream authoritative + adaptive-state plane (PAMA)**. On a fair comparison it is broader than AxonFlow on governance surface *and* deeper on enforcement integrity — pending public substantiation of the PAMA tier.

## Sources
- [AxonFlow — Runtime Control Layer for Production AI](https://getaxonflow.com/)
- [AxonFlow Documentation](https://docs.getaxonflow.com/) · [Audit Logging](https://docs.getaxonflow.com/docs/governance/audit-logging/)
- [github.com/getaxonflow/axonflow](https://github.com/getaxonflow/axonflow) · [axonflow-sdk-python](https://github.com/getaxonflow/axonflow-sdk-python) · [axonflow-claude-plugin](https://github.com/getaxonflow/axonflow-claude-plugin)
- [axonflow on PyPI](https://pypi.org/project/axonflow/)
