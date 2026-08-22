# Qortara Governance Provider

A small host-neutral ESM adapter that evaluates a consequential capability through Microsoft Agent Governance Toolkit and emits the Qortara Governance proving-ground exchange contract.

This package is deliberately narrow. It does not own policy language, QOR Agent execution, Qortara SDLC lifecycle semantics, Agent Memory semantics, or AgentTrust evidence semantics.

## Boundary

```text
host capability request
        |
        v
Qortara Governance Provider
        |
        v
Microsoft AGT PolicyEngine
        |
        +-- allow -> verified provider allow -> Qortara may permit
        +-- deny  -> verified provider deny  -> no execution
        +-- other -> verified non-terminal   -> inconclusive / no execution
        +-- error/unavailable/unsupported    -> Qortara fail-closed deny
```

A provider failure is never rewritten as a native AGT policy denial. The exchange preserves both the Qortara execution effect and the provider-native state so evidence attribution remains honest.

## Runtime profile

The proving trajectory pins:

- `@microsoft/agent-governance-sdk` `5.0.0`
- Qortara exchange contract `0.1`
- Qortara provider adapter `0.1.0`

The package itself imports no Node filesystem APIs. Its first Cloudflare consumer uses the modern Node-compatible workerd profile. Strict no-Node AGT portability remains a separate compatibility result and is not hidden by this adapter.

## Usage

```js
import { createGovernanceProvider } from '@mythologiq/qortara-governance-provider';

const governance = createGovernanceProvider({
  rules: [
    { action: 'status.read', effect: 'allow' },
    { action: '*', effect: 'deny' },
  ],
});

const exchange = await governance.evaluate({
  run_id: 'run-123',
  operation_id: 'op-456',
  action: {
    principal_id: 'principal:operator',
    agent_id: 'agent:qor',
    capability: 'status.read',
  },
});
```

The caller must treat only a verified provider `allow` as permission. `deny`, `inconclusive`, `unavailable`, `unsupported`, and `error` are all non-execution states.

## Testing

```bash
npm install --ignore-scripts
npm run check
npm test
```

The test suite exercises the real pinned AGT `PolicyEngine` for allow/default-deny behavior and injected failure surfaces for deterministic attribution tests.

## Project relationship

This package implements `MythologIQ-Labs-LLC/qortara-governance#32` and stacks on the validated host-neutral exchange contract in PR #27. It exists so QOR Agent and other hosts can consume Qortara Governance without copying Qortara semantics into their own runtime.
