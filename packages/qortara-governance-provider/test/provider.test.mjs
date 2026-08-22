import assert from 'node:assert/strict';
import test from 'node:test';

import {
  GovernanceInputError,
  createGovernanceProvider,
} from '../src/index.mjs';

const fixedClock = () => new Date('2026-08-22T20:00:00.000Z');
const fixedId = () => 'qg_test_decision';
const baseRequest = {
  run_id: 'run-001',
  operation_id: 'op-001',
  correlation_id: 'corr-001',
  action: {
    principal_id: 'principal:test',
    principal_type: 'human',
    agent_id: 'agent:qor-test',
    capability: 'status.read',
    target_ref: 'repo:test',
    input_digest: `sha256:${'a'.repeat(64)}`,
  },
};

function provider(overrides = {}) {
  return createGovernanceProvider({
    rules: [
      { action: 'status.read', effect: 'allow' },
      { action: 'admin.delete', effect: 'deny' },
      { action: '*', effect: 'deny' },
    ],
    clock: fixedClock,
    idFactory: fixedId,
    ...overrides,
  });
}

test('real AGT allow is a verified provider allow', async () => {
  const result = await provider().evaluate(baseRequest);

  assert.equal(result.contract_version, '0.1');
  assert.equal(result.run_id, 'run-001');
  assert.equal(result.operation_id, 'op-001');
  assert.equal(result.correlation_id, 'corr-001');
  assert.equal(result.result.effect, 'allow');
  assert.equal(result.result.provider.status, 'verified');
  assert.equal(result.result.provider.native_effect, 'allow');
  assert.equal(result.result.provider.version, '5.0.0');
  assert.equal(result.result.qortara.decision_id, 'qg_test_decision');
});

test('real AGT native deny stays distinct from provider failure', async () => {
  const request = structuredClone(baseRequest);
  request.action.capability = 'admin.delete';

  const result = await provider().evaluate(request);

  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.status, 'verified');
  assert.equal(result.result.provider.native_effect, 'deny');
  assert.ok(result.result.reason_codes.includes('agt_policy_deny'));
});

test('unknown capability is default-denied by AGT and remains a verified native deny', async () => {
  const request = structuredClone(baseRequest);
  request.action.capability = 'unknown.capability';

  const result = await provider().evaluate(request);

  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.status, 'verified');
  assert.equal(result.result.provider.native_effect, 'deny');
});

test('provider unavailability fails closed without inventing an AGT policy denial', async () => {
  const unavailable = Object.assign(new Error('provider unavailable'), { code: 'AGT_UNAVAILABLE' });
  const result = await provider({
    engineFactory: () => ({
      evaluate() {
        throw unavailable;
      },
    }),
  }).evaluate(baseRequest);

  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.status, 'unavailable');
  assert.equal(result.result.provider.native_effect, undefined);
  assert.deepEqual(result.result.reason_codes, ['qortara_provider_unavailable']);
});

test('unsupported runtime fails closed and remains attributed to provider availability', async () => {
  const unsupported = Object.assign(new Error('runtime unsupported'), { code: 'AGT_UNSUPPORTED_RUNTIME' });
  const result = await provider({
    engineFactory: () => {
      throw unsupported;
    },
  }).evaluate(baseRequest);

  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.status, 'unsupported');
  assert.equal(result.result.provider.native_effect, undefined);
  assert.equal(result.result.provider.error_code, 'AGT_UNSUPPORTED_RUNTIME');
});

test('unexpected provider exception fails closed as provider error', async () => {
  const result = await provider({
    engineFactory: () => ({
      evaluate() {
        throw new Error('boom');
      },
    }),
  }).evaluate(baseRequest);

  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.status, 'error');
  assert.equal(result.result.provider.native_effect, undefined);
  assert.deepEqual(result.result.reason_codes, ['qortara_provider_error']);
});

test('non-terminal native decision never becomes permission', async () => {
  const result = await provider({
    engineFactory: () => ({ evaluate: () => 'warn' }),
  }).evaluate(baseRequest);

  assert.equal(result.result.effect, 'inconclusive');
  assert.equal(result.result.provider.status, 'verified');
  assert.equal(result.result.provider.native_effect, 'warn');
  assert.deepEqual(result.result.reason_codes, ['agt_non_terminal_decision']);
});

test('malformed identity is rejected before provider evaluation', async () => {
  let evaluated = false;
  const governed = provider({
    engineFactory: () => ({
      evaluate() {
        evaluated = true;
        return 'allow';
      },
    }),
  });
  const request = structuredClone(baseRequest);
  request.action.principal_id = '';

  await assert.rejects(
    governed.evaluate(request),
    (error) => error instanceof GovernanceInputError && error.code === 'invalid_governance_request',
  );
  assert.equal(evaluated, false);
});

test('policy evidence metadata is preserved when supplied', async () => {
  const governed = provider({
    policyRef: 'policy:test:v1',
    policyDigest: `sha256:${'b'.repeat(64)}`,
  });

  const result = await governed.evaluate(baseRequest);
  assert.equal(result.result.provider.policy_ref, 'policy:test:v1');
  assert.equal(result.result.provider.policy_digest, `sha256:${'b'.repeat(64)}`);
});
