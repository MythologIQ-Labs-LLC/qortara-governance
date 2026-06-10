"""Patch-lifecycle registry — single public surface."""

from __future__ import annotations

from qortara_governance.patches.registry import (
    apply_patches,
    get_client,
    get_evidence_sink,
    get_observe,
    is_patched,
    unpatch_all,
)

__all__ = [
    "apply_patches",
    "get_client",
    "get_evidence_sink",
    "get_observe",
    "is_patched",
    "unpatch_all",
]
