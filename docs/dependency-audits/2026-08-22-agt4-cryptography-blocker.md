# Dependency audit: AGT 4.0.0 cryptography security blocker

**Date:** 2026-08-22  
**Owner:** MythologIQ Labs / Qortara Governance  
**Tracking:** #28, with AGT modernization owned by #26  
**Authority:** local evidence only; Microsoft AGT and AgentTrust are read-only upstream dependencies for parent project `MythologIQ-Labs-LLC/Myth-Tech-Forge#247`.

## Summary

The Qortara Governance security workflow currently fails correctly because the resolved Python environment contains `cryptography==48.0.1`, and `pip-audit` reports three known vulnerabilities:

```text
cryptography 48.0.1  PYSEC-2026-3552  fix 50.0.0
cryptography 48.0.1  PYSEC-2026-3553  fix 49.0.0
cryptography 48.0.1  PYSEC-2026-3554  fix 49.0.0
```

This finding must not be suppressed merely to make CI green.

## Owning dependency constraint

`qortara-governance-langchain==0.2.1` currently pins the Microsoft AGT Python packages at `4.0.0`.

The public AGT `v4.0.0` core package declares:

```text
cryptography>=46.0.7,<49.0
```

That upper bound prevents resolving either `cryptography>=49.0.0` or `cryptography>=50.0.0`, which are the fix levels reported by the current audit.

Therefore adding a local `cryptography>=49` or `>=50` requirement to Qortara Governance while retaining AGT 4.0.0 would create an incompatible dependency set rather than remediate the vulnerability.

## Current-line evidence

The current public AGT `5.0.0` source widens the core dependency to:

```text
cryptography>=46.0.7,<51.0
```

AGT's public dependency-audit documentation also records successful testing of `cryptography==50.0.0` in current code paths.

This is evidence that the security blocker is coupled to Qortara Governance's legacy AGT 4.x foundation, not evidence that Qortara may blindly version-bump. Issue #26 owns semantic/API reconciliation from AGT 4.x to the current line.

## Decision

1. Keep `pip-audit` blocking.
2. Do not add `--ignore-vuln` for these advisories merely to restore a green badge.
3. Do not override AGT 4.0.0's declared cryptography range.
4. Restore the independent CI/lint baseline under #28.
5. Treat the dependency audit as an explicit owned blocker until #26 provides a tested current-AGT migration path that can resolve a non-vulnerable cryptography version.
6. Re-run the same security gate on the exact migrated head. The remediation evidence must append to this finding rather than erase it.

## Boundary attribution

```text
Qortara Governance repository baseline
    -> security gate is functioning correctly

Qortara Governance AGT 4.0.0 integration
    -> constrains cryptography below the reported fixed versions

Microsoft AGT upstream
    -> read-only dependency source for this project
    -> no issue/comment/PR or other upstream write is authorized here
```

This classification prevents the proving-ground contract PR from being blamed for a dependency finding it did not introduce while still refusing to manufacture a false-green security result.
