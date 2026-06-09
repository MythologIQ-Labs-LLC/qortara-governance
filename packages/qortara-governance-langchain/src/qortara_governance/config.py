"""Config resolution — env vars with kwarg overrides and defaults.

Precedence: init() kwarg > env var > default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class PolicyMode(str, Enum):
    ENFORCE = "enforce"
    OBSERVE = "observe"


@dataclass(frozen=True)
class Config:
    sidecar_endpoint: str | None
    tenant_key: str | None
    policy_mode: PolicyMode


_VALID_MODES = {m.value for m in PolicyMode}


def _env_policy_mode(raw: str | None) -> PolicyMode:
    if raw is None:
        return PolicyMode.ENFORCE
    if raw not in _VALID_MODES:
        raise ValueError(
            f"Invalid QORTARA_POLICY_MODE={raw!r}; must be one of {_VALID_MODES}"
        )
    return PolicyMode(raw)


def load_config(
    *,
    sidecar_endpoint: str | None = None,
    tenant_key: str | None = None,
    policy_mode: str | PolicyMode | None = None,
) -> Config:
    """Resolve configuration. Kwarg overrides env, env overrides default."""
    endpoint = sidecar_endpoint or os.environ.get("QORTARA_SIDECAR_ENDPOINT")
    key = tenant_key or os.environ.get("QORTARA_TENANT_KEY")

    if policy_mode is None:
        mode = _env_policy_mode(os.environ.get("QORTARA_POLICY_MODE"))
    elif isinstance(policy_mode, PolicyMode):
        mode = policy_mode
    else:
        if policy_mode not in _VALID_MODES:
            raise ValueError(
                f"Invalid policy_mode={policy_mode!r}; must be one of {_VALID_MODES}"
            )
        mode = PolicyMode(policy_mode)

    return Config(
        sidecar_endpoint=endpoint,
        tenant_key=key,
        policy_mode=mode,
    )
