import { PolicyEngine } from '@microsoft/agent-governance-sdk';

export const CONTRACT_VERSION = '0.1';
export const ADAPTER_NAME = 'qortara-governance-provider';
export const ADAPTER_VERSION = '0.1.0';
export const AGT_SDK = '@microsoft/agent-governance-sdk';
export const AGT_VERSION = '5.0.0';

export class GovernanceInputError extends TypeError {
  constructor(message, code = 'invalid_governance_request') {
    super(message);
    this.name = 'GovernanceInputError';
    this.code = code;
  }
}

function requireObject(value, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new GovernanceInputError(`${name} must be an object`);
  }
  return value;
}

function requireString(value, name) {
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new GovernanceInputError(`${name} must be a non-empty string`);
  }
  return value;
}

function validateDigest(value, name) {
  if (value === undefined) return undefined;
  requireString(value, name);
  if (!/^(sha256|sha512):[A-Fa-f0-9]+$/.test(value)) {
    throw new GovernanceInputError(`${name} must be a sha256: or sha512: digest`);
  }
  return value;
}

function normalizeRequest(request) {
  const input = requireObject(request, 'request');
  const action = requireObject(input.action, 'request.action');

  const normalizedAction = {
    ...action,
    principal_id: requireString(action.principal_id, 'request.action.principal_id'),
    agent_id: requireString(action.agent_id, 'request.action.agent_id'),
    capability: requireString(action.capability, 'request.action.capability'),
  };

  if (action.input_digest !== undefined) {
    normalizedAction.input_digest = validateDigest(action.input_digest, 'request.action.input_digest');
  }

  return {
    contract_version: CONTRACT_VERSION,
    run_id: requireString(input.run_id, 'request.run_id'),
    operation_id: requireString(input.operation_id, 'request.operation_id'),
    correlation_id: input.correlation_id === undefined
      ? undefined
      : requireString(input.correlation_id, 'request.correlation_id'),
    action: normalizedAction,
  };
}

function nowIso(clock) {
  const value = clock();
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new GovernanceInputError('clock must return a valid Date-compatible value');
  }
  return date.toISOString();
}

function defaultDecisionId() {
  if (globalThis.crypto?.randomUUID) return `qg_${globalThis.crypto.randomUUID()}`;
  return `qg_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

function normalizeNativeDecision(decision) {
  if (typeof decision === 'string') {
    return { effect: decision, reasonCodes: [] };
  }

  if (decision && typeof decision === 'object') {
    const effect = decision.effect ?? decision.decision ?? decision.result;
    const reasonCodes = decision.reason_codes ?? decision.reasonCodes ?? [];
    if (typeof effect === 'string') {
      return {
        effect,
        reasonCodes: Array.isArray(reasonCodes)
          ? [...new Set(reasonCodes.filter((value) => typeof value === 'string' && value.length > 0))]
          : [],
      };
    }
  }

  return { effect: 'unknown', reasonCodes: [] };
}

function classifyProviderError(error) {
  if (error?.code === 'AGT_UNAVAILABLE') return 'unavailable';
  if (error?.code === 'AGT_UNSUPPORTED_RUNTIME') return 'unsupported';
  return 'error';
}

function latencyMs(started) {
  const ended = globalThis.performance?.now?.() ?? Date.now();
  return Math.max(0, ended - started);
}

function providerMetadata({
  status,
  nativeEffect,
  nativeReasonCodes = [],
  runtimeProfile,
  observedAt,
  latency,
  policyRef,
  policyDigest,
  errorCode,
}) {
  return {
    name: 'microsoft-agent-governance-toolkit',
    status,
    version: AGT_VERSION,
    sdk: AGT_SDK,
    adapter: ADAPTER_NAME,
    intervention_point: 'pre_capability',
    runtime_profile: runtimeProfile,
    ...(nativeEffect ? { native_effect: nativeEffect } : {}),
    ...(nativeReasonCodes.length > 0 ? { native_reason_codes: nativeReasonCodes } : {}),
    ...(policyRef ? { policy_ref: policyRef } : {}),
    ...(policyDigest ? { policy_digest: policyDigest } : {}),
    ...(errorCode ? { error_code: errorCode } : {}),
    latency_ms: latency,
    observed_at: observedAt,
  };
}

function envelope({ request, effect, reasons, provider, decidedAt, latency, decisionId }) {
  return {
    contract_version: CONTRACT_VERSION,
    run_id: request.run_id,
    operation_id: request.operation_id,
    ...(request.correlation_id ? { correlation_id: request.correlation_id } : {}),
    action: request.action,
    result: {
      effect,
      reason_codes: [...new Set(reasons)],
      qortara: {
        adapter: ADAPTER_NAME,
        adapter_version: ADAPTER_VERSION,
        decision_id: decisionId,
        decided_at: decidedAt,
        latency_ms: latency,
        transport: 'in_process',
      },
      provider,
    },
  };
}

export function createGovernanceProvider({
  rules,
  engineFactory = (policyRules) => new PolicyEngine(policyRules),
  clock = () => new Date(),
  idFactory = defaultDecisionId,
  runtimeProfile = 'workerd-node-compatible',
  policyRef,
  policyDigest,
} = {}) {
  if (!Array.isArray(rules) || rules.length === 0) {
    throw new GovernanceInputError('rules must be a non-empty array', 'invalid_policy_rules');
  }
  if (typeof engineFactory !== 'function') {
    throw new GovernanceInputError('engineFactory must be a function');
  }
  validateDigest(policyDigest, 'policyDigest');
  if (policyRef !== undefined) requireString(policyRef, 'policyRef');
  requireString(runtimeProfile, 'runtimeProfile');

  let engine;
  let initializationError;
  try {
    engine = engineFactory(rules);
  } catch (error) {
    initializationError = error;
  }

  return Object.freeze({
    async evaluate(rawRequest) {
      const request = normalizeRequest(rawRequest);
      const started = globalThis.performance?.now?.() ?? Date.now();
      const decidedAt = nowIso(clock);
      const decisionId = requireString(idFactory(), 'idFactory result');

      if (initializationError) {
        const status = classifyProviderError(initializationError);
        const latency = latencyMs(started);
        return envelope({
          request,
          effect: 'deny',
          reasons: [`qortara_provider_${status}`],
          provider: providerMetadata({
            status,
            runtimeProfile,
            observedAt: decidedAt,
            latency,
            policyRef,
            policyDigest,
            errorCode: initializationError?.code ?? 'provider_initialization_error',
          }),
          decidedAt,
          latency,
          decisionId,
        });
      }

      try {
        const native = normalizeNativeDecision(await engine.evaluate(request.action.capability));
        const latency = latencyMs(started);

        if (native.effect === 'allow') {
          return envelope({
            request,
            effect: 'allow',
            reasons: native.reasonCodes.length > 0 ? native.reasonCodes : ['agt_policy_allow'],
            provider: providerMetadata({
              status: 'verified',
              nativeEffect: native.effect,
              nativeReasonCodes: native.reasonCodes,
              runtimeProfile,
              observedAt: decidedAt,
              latency,
              policyRef,
              policyDigest,
            }),
            decidedAt,
            latency,
            decisionId,
          });
        }

        if (native.effect === 'deny') {
          return envelope({
            request,
            effect: 'deny',
            reasons: native.reasonCodes.length > 0 ? native.reasonCodes : ['agt_policy_deny'],
            provider: providerMetadata({
              status: 'verified',
              nativeEffect: native.effect,
              nativeReasonCodes: native.reasonCodes,
              runtimeProfile,
              observedAt: decidedAt,
              latency,
              policyRef,
              policyDigest,
            }),
            decidedAt,
            latency,
            decisionId,
          });
        }

        return envelope({
          request,
          effect: 'inconclusive',
          reasons: ['agt_non_terminal_decision'],
          provider: providerMetadata({
            status: 'verified',
            nativeEffect: native.effect,
            nativeReasonCodes: native.reasonCodes,
            runtimeProfile,
            observedAt: decidedAt,
            latency,
            policyRef,
            policyDigest,
          }),
          decidedAt,
          latency,
          decisionId,
        });
      } catch (error) {
        const status = classifyProviderError(error);
        const latency = latencyMs(started);
        return envelope({
          request,
          effect: 'deny',
          reasons: [`qortara_provider_${status}`],
          provider: providerMetadata({
            status,
            runtimeProfile,
            observedAt: decidedAt,
            latency,
            policyRef,
            policyDigest,
            errorCode: error?.code ?? 'provider_evaluation_error',
          }),
          decidedAt,
          latency,
          decisionId,
        });
      }
    },
  });
}
