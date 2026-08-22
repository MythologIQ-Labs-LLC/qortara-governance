# Qortara Governance proving-ground exchange

Status: **prototype contract fixture** for [issue #26](https://github.com/MythologIQ-Labs-LLC/qortara-governance/issues/26).

Parent project: `MythologIQ-Labs-LLC/Myth-Tech-Forge#247`.

This directory defines the first language-neutral exchange envelope used by the integrated Qortara proving ground.

It does **not** replace the existing `qortara_protocol` v0.1 `ActionRequest -> ActionDecision` contract. The existing action request/decision remains the governance payload. This envelope adds the cross-product information the proving ground needs to preserve provider identity, runtime compatibility, native evidence, and failure attribution without making LangChain, Python, QOR Agent, or Cloudflare part of the public semantic contract.

## Design rule

```text
Qortara normalizes execution semantics.
The provider keeps its native evidence identity.
```

For Microsoft Agent Governance Toolkit this means a Qortara result can fail closed while still distinguishing:

- a native AGT policy denial;
- AGT unavailable;
- unsupported AGT version;
- AGT runtime incompatibility;
- malformed/native AGT error;
- Qortara transport or adapter failure.

Those states are not interchangeable.

## Correlation identity

The cross-system Wayfinder contract uses:

```text
scenario_id   # composite/lifecycle layer
run_id        # one complete journey
operation_id  # one consequential action/obligation pair
```

This Qortara Governance exchange is narrower than the composite lifecycle envelope, so it carries `run_id` and **required `operation_id`**. `scenario_id`, Agent Memory, AgentTrust, outcome-observation, and cleanup composition remain Qortara SDLC concerns.

An optional `correlation_id` may link a lower-level trace or transport event, but it must not become a competing run identity.

## Files

- `qortara-governance-exchange.v0.1.schema.json` - prototype JSON Schema for a request/result exchange.
- `fixtures/allow-agt.json` - verified AGT allow translated to a Qortara permit while retaining AGT evidence.
- `fixtures/agt-unavailable.json` - fail-closed Qortara denial caused by provider unavailability, explicitly not relabeled as an AGT policy denial.
- `fixtures/agt-runtime-unsupported.json` - fail-closed result for an unsupported runtime/provider combination.

## Existing protocol relationship

The current Python SDK already uses:

```text
ActionRequest
    -> DecisionClient
        -> AgtDecisionClient OR SidecarClient
    -> ActionDecision
```

The proving-ground exchange wraps that semantic operation:

```text
run + operation identity
        +
ActionRequest-compatible action
        |
        v
Qortara Governance
        |
        +--> provider decision
        |
        v
normalized Qortara effect
        +
native provider evidence envelope
```

A future stable wire version may reuse, merge, or supersede parts of this prototype after the Cloudflare reference host and a non-QOR host exercise it. Do not publish this schema as a stable compatibility promise merely because it exists in the repository.

## Host neutrality

The schema intentionally contains no:

- LangChain or LangGraph object types;
- Python import paths;
- QOR Agent session types;
- Cloudflare Worker bindings, Durable Object stubs, D1 bookmarks, or Workflow APIs;
- Microsoft AGT class names.

A Cloudflare Worker, CLI, daemon, embedded runtime, or future adapter should be able to serialize the same semantic exchange.

## Provider evidence rules

When a provider is AGT, preserve where known:

- provider/package/version identity;
- adapter/language SDK identity;
- intervention point;
- policy reference/digest;
- native effect;
- native reason codes/text references;
- native receipt/audit/evidence reference;
- runtime profile;
- provider latency;
- explicit unavailable/unsupported/error state.

Large or sensitive native payloads should be retained by reference/digest rather than copied into every response.

## Fail-closed invariant

For a protected action:

```text
verified permitting provider result -> Qortara may permit
anything else                     -> no execution
```

The execution effect and the provider verdict are separate fields precisely so fail-closed behavior cannot rewrite the historical cause.

## Read-only upstream rule

For parent project #247, Microsoft AGT and AgentTrust are read-only upstream dependencies. This fixture may inspect, pin, and test their public artifacts and retain results locally, but it does not authorize upstream writes or evidence transmission.

## Brennan / alternate-host requirement

QOR Agent is the proving-ground host, not a required production dependency. Brennan's existing Cloudflare Worker harness must be able to consume the same exchange semantics without importing QOR Agent.
