"""HTTP client for sidecar — decide/evidence calls with circuit breaker.

Circuit breaker: after _BREAKER_THRESHOLD consecutive 5xx responses,
fail closed to deny-all for _BREAKER_COOLDOWN seconds. Recovers on
any successful health check.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx
from pydantic import ValidationError

from qortara_governance.exceptions import QortaraSidecarUnavailable
from qortara_governance.protocol_version import PROTOCOL_VERSION
from qortara_protocol import ActionDecision, ActionRequest, DecisionKind, EvidenceRecord

_BREAKER_THRESHOLD = 5
_BREAKER_COOLDOWN_S = 30.0
_DEFAULT_TIMEOUT_S = 10.0


@dataclass
class _BreakerState:
    consecutive_failures: int = 0
    tripped_at: float = 0.0


def _deny_all(rationale: str) -> ActionDecision:
    return ActionDecision(
        decision_kind=DecisionKind.DENY,
        policy_version_sha256="circuit-breaker",
        rationale=rationale,
        policy_pack_id="sdk-circuit-breaker",
        ts=time.time(),
    )


class SidecarClient:
    """httpx-based sidecar client with circuit breaker and deny-closed failure."""

    def __init__(
        self,
        endpoint: str,
        tenant_key: str | None,
        *,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._headers: dict[str, str] = {}
        if tenant_key:
            self._headers["Ocp-Apim-Subscription-Key"] = tenant_key
        self._client = httpx.Client(
            base_url=self._endpoint, headers=self._headers, timeout=timeout_s
        )
        self._breaker = _BreakerState()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SidecarClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _breaker_tripped(self) -> bool:
        if self._breaker.consecutive_failures < _BREAKER_THRESHOLD:
            return False
        if (time.time() - self._breaker.tripped_at) > _BREAKER_COOLDOWN_S:
            self._breaker.consecutive_failures = 0
            return False
        return True

    def _record_success(self) -> None:
        self._breaker.consecutive_failures = 0

    def _record_failure(self) -> None:
        self._breaker.consecutive_failures += 1
        if self._breaker.consecutive_failures >= _BREAKER_THRESHOLD:
            self._breaker.tripped_at = time.time()

    def decide(
        self, request: ActionRequest, tool_input: object = None
    ) -> ActionDecision:
        """POST /v0.1/decisions — returns ActionDecision; deny-all on breaker trip.

        `tool_input` is accepted for interface parity with in-process decision
        sources but is intentionally NOT inlined onto the wire (payload privacy);
        the sidecar receives a reference, never the raw arguments.
        """
        del tool_input
        if self._breaker_tripped():
            return _deny_all("sidecar circuit breaker tripped — deny-closed")
        try:
            resp = self._client.post(
                f"/{PROTOCOL_VERSION}/decisions", json=request.model_dump(mode="json")
            )
            if resp.status_code >= 500:
                self._record_failure()
                return _deny_all(f"sidecar 5xx: {resp.status_code}")
            resp.raise_for_status()
            decision = ActionDecision.model_validate(resp.json())
            self._record_success()
            return decision
        except (httpx.RequestError, httpx.HTTPStatusError):
            self._record_failure()
            return _deny_all("sidecar unreachable — deny-closed")
        except (ValidationError, ValueError):
            # Malformed 2xx body (bad JSON / schema). Fail closed and count it
            # toward the breaker — a misbehaving sidecar must not allow.
            self._record_failure()
            return _deny_all("sidecar returned a malformed decision — deny-closed")

    def submit_evidence(self, records: list[EvidenceRecord]) -> None:
        """POST /v0.1/evidence — best-effort; failures are logged but not raised."""
        if self._breaker_tripped() or not records:
            return
        payload = [r.model_dump(mode="json") for r in records]
        try:
            self._client.post(f"/{PROTOCOL_VERSION}/evidence", json=payload)
            self._record_success()
        except httpx.RequestError:
            self._record_failure()

    def health(self) -> bool:
        """GET /v0.1/health — returns True on 2xx; resets breaker on success."""
        try:
            resp = self._client.get(f"/{PROTOCOL_VERSION}/health")
            ok = 200 <= resp.status_code < 300
            if ok:
                self._record_success()
            return ok
        except httpx.RequestError:
            return False

    def require_reachable(self) -> None:
        """Raise QortaraSidecarUnavailable if health check fails."""
        if not self.health():
            raise QortaraSidecarUnavailable(f"sidecar at {self._endpoint} unreachable")
