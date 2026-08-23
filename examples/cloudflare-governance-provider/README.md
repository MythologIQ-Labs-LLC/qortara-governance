# Qortara Governance Cloudflare proving adapter

This directory exposes the owner-managed Qortara Governance proving provider through a minimal internal Cloudflare Worker so external harnesses can consume a real Governance result without copying provider or AGT semantics.

## Ownership boundary

```text
QOR / other host
    -> Cloudflare Service Binding
        -> this Worker adapter
            -> @mythologiq/qortara-governance-provider
                -> @microsoft/agent-governance-sdk 5.0.0
```

The Worker is transport glue only. The host-neutral exchange and provider normalization remain owned by Qortara Governance.

## Service identity

```text
service: qortara-governance-provider-proving
QOR binding: QORTARA_GOVERNANCE
```

These are proving-ground deployment names, not stable product API.

## Proving policy

The adapter intentionally does **not** accept policy rules from callers. It uses one fixed synthetic proving policy:

```text
release.marker.publish -> allow
release.marker.cleanup -> allow
*                      -> deny
```

That prevents a caller from turning the proving transport itself into an authority-expansion mechanism.

## Routes

```text
GET  /health
POST /v1/governance/evaluate
```

The evaluation route returns the native Qortara Governance Exchange 0.1 envelope produced by the existing provider package. It does not translate a provider failure into a native AGT policy denial.

## Security posture

- `workers_dev` is disabled.
- preview URLs are disabled.
- no secrets are required.
- public Internet exposure is not required for the proving scenario.
- the adapter does not accept caller-supplied policy rules.
- only a verified native provider allow can permit the two registered proving capabilities.

The separate Python dependency/security blocker tracked by Qortara Governance #28 / PR #31 remains independently visible. A successful Node/workerd proving adapter does not make that owner-repository security gate green.

## Validation

```bash
npm install --ignore-scripts --no-audit --no-fund
npm run check
npm run dev
```

Repository CI also starts the Worker under Wrangler/workerd and proves a real AGT allow for `release.marker.publish` and a real default deny for an unrelated capability.
