"""@qortara_exempt — opt-out marker for tools that must bypass enforcement."""

from __future__ import annotations

from typing import TypeVar

_EXEMPT_ATTR = "__qortara_exempt__"

# Module-private sentinel. Exemption is keyed on object IDENTITY with this marker,
# not on a truthy value (GAP-SEC-07 defense-in-depth): a coincidental or injected
# `setattr(tool, "__qortara_exempt__", True)` does NOT exempt — only this decorator
# (or code that imports this private object) can. This raises the bar for accidental
# / casual bypass; it is NOT a defense against hostile in-process code, which can
# import the marker and is out of scope per THREAT-MODEL §5.
_EXEMPT_MARKER = object()

T = TypeVar("T")


def qortara_exempt(obj: T) -> T:
    """Mark a tool class or instance as exempt from Qortara policy enforcement.

    Exempt tools still emit evidence (decision_kind=exempt) for audit completeness,
    but never trigger policy evaluation or deny responses. Exemption is recognized
    only via this decorator (the marker is identity-checked), so a stray truthy
    attribute does not silently disable enforcement.
    """
    setattr(obj, _EXEMPT_ATTR, _EXEMPT_MARKER)
    return obj


def is_exempt(obj: object) -> bool:
    """Return True iff the object or its class carries the exact exempt marker."""
    if getattr(obj, _EXEMPT_ATTR, None) is _EXEMPT_MARKER:
        return True
    cls = type(obj)
    return getattr(cls, _EXEMPT_ATTR, None) is _EXEMPT_MARKER
