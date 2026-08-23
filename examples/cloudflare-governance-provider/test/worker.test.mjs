import assert from 'node:assert/strict';
import test from 'node:test';

import worker from '../src/index.mjs';

function governanceRequest(capability, overrides = {}) {
  return {
    run_id: 'run-cloudflare-proving-001',
    operation_id: `op-${capability}`,
    action: {
      principal_id: 'principal:test-operator',
      principal_type: 'human',
      agent_id: 'agent:qor-cloudflare-proving',
      capability,
      target_ref: 'r2://qor-agent-proving-ground-markers/tests/marker.json',
    },
    ...overrides,
  };
}

async function post(body) {
  return await worker.fetch(new Request('https://governance.internal/v1/governance/evaluate', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  }));
}

test('health reports exact proving identity without claiming a public surface', async () => {
  const response = await worker.fetch(new Request('https://governance.internal/health'));
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.equal(result.status, 'healthy');
  assert.equal(result.contract_version, '0.1');
  assert.equal(result.adapter, 'qortara-governance-provider');
  assert.equal(result.adapter_version, '0.1.0');
  assert.equal(result.provider_source_revision, '8d9e2e4e50a29b7df5e678a027403da7071fe128');
  assert.equal(result.agt_version, '5.0.0');
  assert.equal(result.public_surface, false);
  assert.deepEqual(result.allowed_capabilities, [
    'release.marker.publish',
    'release.marker.cleanup',
  ]);
});

for (const capability of ['release.marker.publish', 'release.marker.cleanup']) {
  test(`${capability} is permitted only through a verified native AGT allow`, async () => {
    const response = await post(governanceRequest(capability));
    assert.equal(response.status, 200);
    const result = await response.json();
    assert.equal(result.result.effect, 'allow');
    assert.equal(result.result.provider.status, 'verified');
    assert.equal(result.result.provider.native_effect, 'allow');
    assert.equal(result.result.provider.version, '5.0.0');
    assert.equal(result.result.provider.policy_ref, 'policy:qor-release-marker-proving:v1');
  });
}

test('unknown capability is a verified native/default deny', async () => {
  const response = await post(governanceRequest('admin.delete'));
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.status, 'verified');
  assert.equal(result.result.provider.native_effect, 'deny');
});

test('malformed identity is rejected before provider evaluation', async () => {
  const request = governanceRequest('release.marker.publish');
  request.action.principal_id = '';
  const response = await post(request);
  assert.equal(response.status, 400);
  const result = await response.json();
  assert.equal(result.status, 'invalid_request');
  assert.equal(result.error, 'invalid_governance_request');
});

test('caller cannot inject a policy rule surface into the fixed proving adapter', async () => {
  const response = await post({
    ...governanceRequest('admin.delete'),
    rules: [{ action: 'admin.delete', effect: 'allow' }],
  });
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.equal(result.result.effect, 'deny');
  assert.equal(result.result.provider.native_effect, 'deny');
});
