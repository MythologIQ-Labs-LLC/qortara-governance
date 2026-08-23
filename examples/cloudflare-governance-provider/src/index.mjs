import {
  ADAPTER_NAME,
  ADAPTER_VERSION,
  AGT_SDK,
  AGT_VERSION,
  CONTRACT_VERSION,
  GovernanceInputError,
  createGovernanceProvider,
} from '@mythologiq/qortara-governance-provider';

const PROVIDER_SOURCE_REVISION = '8d9e2e4e50a29b7df5e678a027403da7071fe128';
const POLICY_REF = 'policy:qor-release-marker-proving:v1';
const ALLOWED_CAPABILITIES = Object.freeze([
  'release.marker.publish',
  'release.marker.cleanup',
]);

const provider = createGovernanceProvider({
  rules: [
    { action: 'release.marker.publish', effect: 'allow' },
    { action: 'release.marker.cleanup', effect: 'allow' },
    { action: '*', effect: 'deny' },
  ],
  runtimeProfile: 'cloudflare-worker-node-compatible',
  policyRef: POLICY_REF,
});

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { 'cache-control': 'no-store' },
  });
}

async function evaluate(request) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({
      status: 'invalid_request',
      error: 'invalid_json',
    }, 400);
  }

  try {
    return json(await provider.evaluate(body));
  } catch (error) {
    if (error instanceof GovernanceInputError) {
      return json({
        status: 'invalid_request',
        error: error.code,
        message: error.message,
      }, 400);
    }

    console.error('qortara_governance_adapter_failure', error);
    return json({
      status: 'unavailable',
      error: 'qortara_governance_adapter_failure',
    }, 503);
  }
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === 'GET' && url.pathname === '/health') {
      return json({
        service: 'qortara-governance-provider-proving',
        status: 'healthy',
        contract_version: CONTRACT_VERSION,
        adapter: ADAPTER_NAME,
        adapter_version: ADAPTER_VERSION,
        provider_source_revision: PROVIDER_SOURCE_REVISION,
        agt_sdk: AGT_SDK,
        agt_version: AGT_VERSION,
        policy_ref: POLICY_REF,
        allowed_capabilities: ALLOWED_CAPABILITIES,
        public_surface: false,
      });
    }

    if (request.method === 'POST' && url.pathname === '/v1/governance/evaluate') {
      return await evaluate(request);
    }

    return json({ error: 'not_found' }, 404);
  },
};
