"""qortara-governance-langchain — LangChain + LangGraph governance SDK.

Public API:
    init(tenant_key=..., ...) -> None
    unpatch_all() -> None  # test teardown only
    QortaraCallbackHandler (for manual registration on Chain/Agent)
    qortara_exempt (decorator marking tools to skip enforcement)
    QortaraPolicyDenied / QortaraApprovalRequired / QortaraSidecarUnavailable
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qortara_governance import contract
from qortara_governance.agt_engine import AgtDecisionClient, AgtPolicyAdapter
from qortara_governance.callback import QortaraCallbackHandler
from qortara_governance.client import SidecarClient
from qortara_governance.config import Config, PolicyMode, load_config
from qortara_governance.context import AgentContext, get_context, set_context
from qortara_governance.decorators import is_exempt, qortara_exempt
from qortara_governance.doctor import GovernanceStatus, collect_status
from qortara_governance.evidence import decision_evidence, execution_evidence
from qortara_governance.evidence_sink import EvidenceSink, OTelEvidenceSink
from qortara_governance.exceptions import (
    QortaraApprovalRequired,
    QortaraAuthenticationError,
    QortaraConfigurationError,
    QortaraError,
    QortaraInsecureTransportWarning,
    QortaraPolicyDenied,
    QortaraProtocolMismatch,
    QortaraSidecarUnavailable,
    QortaraTimeout,
    QortaraUngovernedDispatchWarning,
)
from qortara_governance.launcher import launch
from qortara_governance.patches import apply_patches, unpatch_all
from qortara_governance.protocol_version import (
    PROTOCOL_VERSION,
    require_compatible_protocol,
)

__version__ = "0.2.1"

__all__ = [
    "PROTOCOL_VERSION",
    "AgentContext",
    "AgtDecisionClient",
    "AgtPolicyAdapter",
    "Config",
    "EvidenceSink",
    "GovernanceStatus",
    "OTelEvidenceSink",
    "PolicyMode",
    "QortaraApprovalRequired",
    "QortaraAuthenticationError",
    "QortaraCallbackHandler",
    "QortaraConfigurationError",
    "QortaraError",
    "QortaraInsecureTransportWarning",
    "QortaraPolicyDenied",
    "QortaraProtocolMismatch",
    "QortaraSidecarUnavailable",
    "QortaraTimeout",
    "QortaraUngovernedDispatchWarning",
    "collect_status",
    "contract",
    "decision_evidence",
    "execution_evidence",
    "get_context",
    "init",
    "init_agt",
    "is_exempt",
    "qortara_exempt",
    "require_compatible_protocol",
    "set_context",
    "unpatch_all",
]


@dataclass(frozen=True)
class _InitFingerprint:
    """Identifies an init configuration so re-init can be a clean no-op or error.

    `mode` is "sidecar" (init) or "agt" (init_agt); `params` holds the
    mode-specific identifying arguments. Shared by both entry points so a second
    init/init_agt with identical args is idempotent and any mismatch (including
    mixing the two) raises one consistent error (GAP-C-1).
    """

    mode: str
    params: tuple[Any, ...]


_FINGERPRINT: _InitFingerprint | None = None
# The adapter installed by init_agt(), returned again on an idempotent re-call.
_AGT_ADAPTER: AgtPolicyAdapter | None = None

_REINIT_ERROR = (
    "qortara_governance already initialized with different arguments. "
    "Call qortara_governance.unpatch_all() before re-initializing."
)


def _is_observe(mode: PolicyMode) -> bool:
    return mode is PolicyMode.OBSERVE


def init(
    *,
    tenant_key: str | None = None,
    sidecar_endpoint: str | None = None,
    policy_mode: str | PolicyMode | None = None,
    evidence_sink: EvidenceSink | None = None,
) -> None:
    """Initialize Qortara Governance for this process.

    Calling twice with the same args is a no-op. Calling twice with different
    args raises RuntimeError — call unpatch_all() first if reconfiguring.

    `policy_mode` defaults to `enforce` (deny decisions raise). `observe` is a
    shadow/dry-run mode: policy is still evaluated and every would-be block is
    logged at WARNING via the `qortara_governance` logger, but nothing is raised.
    `evidence_sink` (opt-in) receives decision/execution evidence from the dispatch
    path; the default (None) emits nothing and leaves the hot path unchanged. The
    sink is not part of the re-init fingerprint.

    On first call:
    - Resolves config (env > kwarg > default)
    - Launches sidecar subprocess (if no QORTARA_SIDECAR_ENDPOINT)
    - Verifies sidecar reachability
    - Installs BaseTool.run / ToolNode.invoke patches
    """
    global _FINGERPRINT

    config = load_config(
        sidecar_endpoint=sidecar_endpoint,
        tenant_key=tenant_key,
        policy_mode=policy_mode,
    )
    new_fp = _InitFingerprint(
        "sidecar",
        (config.sidecar_endpoint, config.tenant_key, config.policy_mode),
    )

    if _FINGERPRINT is not None:
        if _FINGERPRINT == new_fp:
            return
        raise RuntimeError(_REINIT_ERROR)

    launch_result = launch(existing_endpoint=config.sidecar_endpoint)
    client = SidecarClient(launch_result.endpoint, config.tenant_key)
    client.require_reachable()
    apply_patches(
        client, observe=_is_observe(config.policy_mode), evidence_sink=evidence_sink
    )
    _FINGERPRINT = new_fp


def init_agt(
    agent_id: str,
    allowed_tools: list[str],
    *,
    capability_aliases: dict[str, str] | None = None,
    policy_mode: str | PolicyMode = PolicyMode.ENFORCE,
    evidence_sink: EvidenceSink | None = None,
) -> AgtPolicyAdapter:
    """Initialize in-process enforcement backed by Microsoft AGT (ADR-0001).

    Installs the dispatch patch with an AGT-backed decision source — no sidecar
    needed locally (this is also the supported air-gapped / offline path). `agent_id`
    is the AGT policy role; `allowed_tools` is its allow-list (default-deny for
    everything else). `capability_aliases` maps your tool names onto AGT-recognized
    capability names (e.g. {"sql_db_query": "database_query"}) so AGT's
    argument-level checks reach them. `policy_mode=observe` runs shadow/dry-run
    (log would-be blocks, never raise). Returns the adapter so the caller can grant
    further roles. Set an AgentContext(agent_id=...) so the patch enforces on this
    agent's dispatches.
    """
    global _FINGERPRINT, _AGT_ADAPTER

    if isinstance(policy_mode, PolicyMode):
        mode = policy_mode
    elif policy_mode in {m.value for m in PolicyMode}:
        mode = PolicyMode(policy_mode)
    else:
        raise QortaraConfigurationError(
            f"Invalid policy_mode={policy_mode!r}; must be 'enforce' or 'observe'"
        )
    new_fp = _InitFingerprint(
        "agt",
        (
            agent_id,
            tuple(allowed_tools),
            tuple(sorted((capability_aliases or {}).items())),
            mode,
        ),
    )

    if _FINGERPRINT is not None:
        if _FINGERPRINT == new_fp and _AGT_ADAPTER is not None:
            return _AGT_ADAPTER  # idempotent re-call: same active adapter
        raise RuntimeError(_REINIT_ERROR)

    adapter = AgtPolicyAdapter(capability_aliases=capability_aliases).allow(
        agent_id, allowed_tools
    )
    # AgtDecisionClient structurally satisfies DecisionClient (the patch layer's
    # contract), so no cast is needed.
    apply_patches(
        AgtDecisionClient(adapter),
        observe=_is_observe(mode),
        evidence_sink=evidence_sink,
    )
    _FINGERPRINT = new_fp
    _AGT_ADAPTER = adapter
    return adapter


# Keep direct exports for test teardown reach-through.
_unpatch_all_original = unpatch_all


def _unpatch_and_reset() -> None:
    global _FINGERPRINT, _AGT_ADAPTER
    _unpatch_all_original()
    _FINGERPRINT = None
    _AGT_ADAPTER = None


# Override the exported name so tests / users get fingerprint reset too.
unpatch_all = _unpatch_and_reset  # type: ignore[assignment]
