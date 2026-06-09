# Qortara Governance — Threat Model

**Status:** Beta-track (B4)
**Scope:** `qortara-governance-langchain` SDK + the default **in-process AGT** enforcement path (optional remote sidecar covered as a secondary boundary)
**Last updated:** 2026-06-09
**Companion docs:** [`BETA-LAUNCH-ARCHITECTURAL-ROADMAP.md`](../BETA-LAUNCH-ARCHITECTURAL-ROADMAP.md) §7.3 (bypass model) + §11 (security hardening)

## 1. Purpose and scope

This document states what Qortara Governance defends, the boundaries it defends across, and — explicitly — what it does **not** defend against. It is a boundary statement, not a certification: some mitigations name controls that are themselves open Beta blockers (e.g. authenticated local transport, `[S2]`), and those are marked `backlog` in the status column.

In scope: the LangChain/LangGraph framework adapter; the **default in-process decision path** (Microsoft AGT `PolicyEngine`, via `init_agt`); the optional remote sidecar path (`init()`); and local policy. Out of scope (post-Beta): Qortara Cloud federation, confidential computing, and hardware attestation.

> **Post-pivot note (Phases 07–09):** the default local decision path is **in-process** via AGT — there is no loopback HTTP channel in that mode, so threats **2 (sidecar impersonation)** and **3 (port hijacking)** below apply **only to the optional remote-daemon (`init()`) mode**, not the default `init_agt()` path.

## 2. Assets

| Asset | Why it matters |
|---|---|
| Policy decisions (`allow` / `deny` / `require_approval` / `exempt`) | The enforcement output; corrupting it defeats the product. |
| Tool arguments | May contain credentials, PII, source, financial/health data. |
| Tenant key / hosted credentials | Authenticate to Qortara Cloud; theft enables impersonation. |
| Evidence records + signing keys | Integrity of the audit trail; forgery destroys non-repudiation. |
| Policy packs | The rules themselves; tampering changes what is allowed. |
| Sidecar endpoint (loopback) | The decision channel; hijacking it injects decisions. |

## 3. Trust boundaries

1. **Cooperative in-process boundary (default)** — the adapter patches `BaseTool.run` / `.arun` (the dispatch funnel `invoke`/`ainvoke` call) and `ToolNode.invoke` / `.ainvoke` inside the *same* Python process as the agent, and (default path) the AGT `PolicyEngine` decision is also in-process. It assumes application code is cooperative, not hostile. In-process code that restores patched methods or calls a tool's underlying function directly (incl. the private `_run`/`_arun`) is **outside** the boundary (see §5).
2. **Loopback sidecar boundary (optional remote-daemon mode only)** — when `init()` is used, SDK ↔ sidecar over `127.0.0.1` (or a local socket). Anything that can bind that port or read process arguments is a threat. Not present on the default in-process (`init_agt`) path.
3. **Hosted boundary** — SDK/sidecar ↔ Qortara hosted decision service + managed Azure over the network. Optional; only present when hosted mode is configured. See [`../ARCHITECTURE-BOUNDARIES.md`](../ARCHITECTURE-BOUNDARIES.md).

## 4. Threat inventory (roadmap §11.1)

STRIDE tags: **S**poofing, **T**ampering, **R**epudiation, **I**nfo-disclosure, **D**oS, **E**levation. Status: `mitigated` (control exists), `partial` (control exists but incomplete), `backlog` (control is an open blocker).

| # | Threat | STRIDE | Mitigation | Residual risk | Status |
|---|---|---|---|---|---|
| 1 | **Bypass of patched dispatch** | E | Patch all supported dispatch entry points; enumerate + conformance-test them; document unsupported paths. | Non-cooperative in-process code can still bypass (§5). | partial |
| 2 | **Sidecar impersonation** | S | Verify sidecar `/version` + protocol before patching; ephemeral auth token to the child; bind loopback only. | Token handling is `[S2]`. | backlog |
| 3 | **Local port hijacking** | S/T | Prefer Unix domain socket where available; verify child identity; reject unauthenticated local requests. | Port race window on TCP loopback. | backlog |
| 4 | **Malicious policy packs** | T/E | Schema-validate packs; require hash; optional signature; fail closed on invalid policy (never downgrade to permissive). | Unsigned packs trusted if signing not enabled. | partial |
| 5 | **Stale policy reuse** | T | Policy freshness/expiration in the sidecar; surface policy version + content hash on each decision. | Expiration enforcement is sidecar work (`[S1]`). | backlog |
| 6 | **Tenant-key theft** | S/I | Keep key out of process arguments and logs; redact in diagnostics; document storage + rotation. | Key-at-rest protection is operator-owned. | partial |
| 7 | **Argument exfiltration** | I | Redaction/omission/hashing of arguments in evidence; do not log raw arguments by default; max payload size. | Default minimization must be implemented in evidence layer. | partial |
| 8 | **Approval-URL tampering** | T/S | Treat approval URL as integrity-protected; validate origin; never auto-approve on malformed approval. | Hosted approval is preview-scope. | backlog |
| 9 | **Decision replay** | T | Idempotency key per evaluation; bind decision to request hash + trace id; decision expiration. | Replay protection depends on idempotency wiring. | partial |
| 10 | **Protocol downgrade** | T/E | Negotiate or reject incompatible protocol versions; fail closed on mismatch (no silent fallback). | Negotiation is Beta protocol work (B2). | partial |
| 11 | **Dependency compromise** | T/E | Lockfiles; dependency + secret scanning; SBOM; provenance attestation; trusted publishing (OIDC). | Supply-chain CI is roadmap §11.4. | backlog |
| 12 | **Signing-key compromise** | S/R | Explicit key generation; restricted permissions; rotation; identify ephemeral subprocess keys as ephemeral; publish verification material. | Key lifecycle is roadmap §10.3. | backlog |
| 13 | **Evidence tampering** | T/R | RFC 8785 canonicalization + Ed25519 signature + SHA-256 content hash; signature verification with test vectors. | Verification path needs fixtures. | partial |
| 14 | **DoS via sidecar failure** | D | Bounded timeouts < tool timeout; circuit breaker with explicit cooldown; fail closed (deny) on unavailability. | Fail-closed denies legitimate calls during outage (accepted: security > availability). | mitigated |
| 15 | **Policy confusion (observe vs enforce)** | E | Explicit `policy_mode`; never silently treat observe as enforce or vice-versa; surface effective mode in diagnostics. | Operator misconfiguration possible. | partial |
| 16 | **Missing-tenant-identity trust** | S/E | Never treat missing tenant identity as trusted; reject unauthenticated decisions in default mode. | Depends on authenticated transport `[S2]`. | backlog |

## 5. Bypass model (roadmap §7.3) — what this does NOT protect against

The adapter protects supported dispatch paths in a **cooperative** application process. It does **not** contain:

- code that calls a tool's underlying function directly, outside LangChain/LangGraph dispatch — including a tool's per-subclass private impl `BaseTool._run`/`._arun`, which cannot be governed at the `BaseTool` class level (the adapter hooks the public `run`/`arun` funnel that `invoke`/`ainvoke` pass through);
- malicious in-process code that restores or replaces patched methods;
- unsupported framework internals or dynamically imported framework versions outside the compatibility matrix;
- subprocesses or remote workers that never initialized the SDK;
- alternate tool-execution paths not routed through the patched interfaces.

This boundary does not invalidate the product; it defines what customers must understand. Threats 1–3 above are the cooperative-boundary edge.

## 6. Fail-closed posture

The default and intended failure mode is **deny**. When policy evaluation is unavailable, malformed, expired, or protocol-incompatible, the system denies rather than allows. Availability is deliberately subordinated to enforcement integrity (threat 14). Operators who need availability-over-enforcement must opt in explicitly via policy; the SDK never substitutes silent allow.

## 7. Open security blockers (tracked in BACKLOG.md)

- `[S1]` Sidecar delivery — without a delivered sidecar the local enforcement path is incomplete (threats 5, 16 depend on it).
- `[S2]` Authenticated local sidecar transport — the default decision endpoint must reject unauthenticated requests (threats 2, 3, 16).

These are Beta release blockers per the roadmap. This threat model is the design baseline they will be measured against.
