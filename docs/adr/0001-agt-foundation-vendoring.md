# ADR 0001 — Build qortara-governance on AGT, and how to incorporate it

**Status:** Accepted (2026-06-09) — Option 1, depend on full AGT; no vendoring
**Date:** 2026-06-09
**Deciders:** Kevin Knapp (maintainer)
**Context docs:** [AGT Component Map](../architecture/AGT-COMPONENT-MAP.md)

## Context

Operator intent (corrected this session): *qortara-governance is AGT "with added bells and whistles," literally using the AGT LangChain sidecar as the foundation and building around it,* with a potential Azure upstream backend.

This **contradicts the repository's current self-positioning**, which presents qortara as an *independent* dispatch-path enforcement alternative to AGT, with:
- a clean-room protocol (`qortara_protocol` 0.1.2) that is **not** wire-compatible with any AGT component;
- a from-scratch sidecar scaffold (`packages/qortara-governance-sidecar/`, built this session under S1) that **duplicates** AGT's decision-engine role;
- README/CONCEPT text framing AGT as prior art to be replaced (the #73 wrapper-bypass critique).

Due diligence (AGT v3.7.0 @ `83cf9c2`, MIT © Microsoft) found that "the AGT langchain sidecar" is not one artifact (see Component Map). The enforcement-aligned foundation is the **ACS `policy-engine`** — a **Rust core + Python SDK** (`agent-control-specification` 0.3.1b0) whose Python SDK already has a LangChain `pre/post_tool_call` adapter.

## Problem

How should qortara incorporate AGT as its foundation, given (a) AGT's enforcement core is polyglot (Rust+Python), (b) qortara's existing protocol/sidecar are independent and partly duplicative, and (c) license/provenance obligations (MIT → Apache-2.0)?

## Options

1. **Depend (no vendor).** Add `agent-control-specification` (and/or `agentmesh_platform`) as pinned PyPI deps; qortara becomes the layer around them (dispatch patch + Azure upstream). Cleanest provenance, upstream security/maintenance retained. Rust core consumed as a built wheel.
2. **Hybrid vendor.** Consume the Rust ACS core as a pinned dependency, but vendor the **Python** ACS SDK + `acs-sidecar-reference` into `packages/` (MIT LICENSE/NOTICE) to own the LangChain seam. Medium provenance cost; avoids copying a Rust crate.
3. **Full vendor.** Copy the ACS `policy-engine` (Rust + Python) into the monorepo with MIT attribution. Maximum control; **highest cost**: own a Microsoft Rust crate's build, security, and upstream-sync.
4. **IATP vendor.** Vendor `agent-os/modules/iatp` (FastAPI trust proxy). **Rejected** — wrong concern (agent-to-agent trust, not tool-dispatch policy); protocol mismatch with `qortara_protocol`.

Operator's stated preference is to vendor (option 2 or 3). This ADR records that and asks for the precise scope.

## Decision

**Option 1 — depend on `agent-governance-toolkit[full]`; vendor nothing.**

Deciding factor: the operator confirmed **qortara will NOT modify AGT's internals** (explicit, 2026-06-09). Modification was the only justification for forking/vendoring; without it, the relationship is *extend*, not *fork*.

Capability rationale (the question that drove this): depending does **not** degrade AGT. The Rust ACS core ships as a compiled wheel, so a pinned dependency exposes identical runtime capability to vendoring its source — vendoring only adds *modifiability*, which is explicitly out of scope. Conversely, vendoring any *subset* would degrade AGT's breadth (it captures one of five subsystems) and freeze it stale at commit `83cf9c2`. Therefore depending on the **full** toolkit is the capability-maximizing **and** lowest-burden choice. Vendoring is rejected in all forms (Options 2, 3, 4).

### Target architecture

```
qortara-governance (Apache-2.0)
  ├─ depends on → agent-governance-toolkit[full]  (MIT, PyPI)   ← full AGT capability, unmodified
  ├─ adds        → bypass-proof BaseTool.invoke / ToolNode.invoke dispatch patch (the #73 closure)
  │                 routing decisions INTO AGT's ACS policy engine
  └─ adds        → Azure upstream backend integration
```

## Cross-cutting decisions (apply to any vendor option)

- **Protocol reconciliation is unavoidable.** `qortara_protocol` ≠ ACS's protocol. Either (a) adopt ACS's protocol and retire `qortara_protocol`, or (b) keep `qortara_protocol` and write an adapter at the sidecar boundary. This is a first-class workstream, not an afterthought.
- **Retire/demote the S1 scaffold.** `packages/qortara-governance-sidecar/` duplicates the foundation. Keep it only as a local test-double, or delete it.
- **Reposition the docs.** README/CONCEPT must change from "independent alternative" to "extends AGT; closes the #73 dispatch-bypass gap on top of ACS." The #73 critique stays valid (it's why the dispatch patch exists) but the *independent* framing goes.
- **License hygiene.** Vendored MIT files retain Microsoft's copyright + MIT text in-place; add a `THIRD_PARTY/` or per-dir `LICENSE` + update root `NOTICE`; record source commit `83cf9c2` and version for provenance. Do not relicense vendored files as Apache-2.0.
- **Trademark.** MIT permits derivative/commercial use; do not imply Microsoft endorsement; review the `AGT`/`agentmesh`/`ACS` naming before public branding.

## Consequences

- **Reframes the project**: positioning changes from "independent alternative to AGT" to "extends AGT; adds a bypass-proof dispatch hook + Azure upstream." README/CONCEPT must be rewritten.
- **Adds one dependency** (`agent-governance-toolkit[full]`, MIT) to a security-critical path — but no third-party source, no Rust build, no vendored-code maintenance, and AGT stays on its upstream security track. NOTICE gets a normal dependency attribution only.
- **Supersedes part of this session's work** (must be reconciled in the execution cycle):
  - `packages/qortara-governance-sidecar/` (S1 scaffold) — **retire** or demote to a local test-double; AGT's ACS engine is the real decision point.
  - `qortara_protocol` (0.1.2, bespoke) — **reconcile**: drive AGT's ACS decision API instead of a homegrown `/v0.1` protocol/sidecar. Keep `qortara_protocol` only if a thin adapter at the AGT boundary is genuinely needed.
- The genesis "independent enforcement SDK" framing (CONCEPT/ARCHITECTURE_PLAN) is partly invalidated and should be amended.

## Next action

Governed `/qor-plan` cycle to execute the extend-on-AGT refactor: (1) add `agent-governance-toolkit[full]` dependency; (2) re-base the dispatch patch to call AGT's ACS engine; (3) retire the S1 sidecar + reconcile `qortara_protocol`; (4) reposition README/CONCEPT/ARCHITECTURE_PLAN. No source is vendored.
