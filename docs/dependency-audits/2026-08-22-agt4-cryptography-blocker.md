# Dependency audit: AGT cryptography security blocker

**Date:** 2026-08-22  
**Owner:** MythologIQ Labs / Qortara Governance  
**Tracking:** #28 and #26  
**Authority:** local evidence only; Microsoft AGT and AgentTrust are read-only upstream dependencies for parent project `MythologIQ-Labs-LLC/Myth-Tech-Forge#247`.

## Initial AGT 4.0.0 finding

With Qortara Governance pinned to AGT 4.0.0, the resolved environment contained `cryptography==48.0.1`. `pip-audit` reported:

```text
cryptography 48.0.1  PYSEC-2026-3552  fix 50.0.0
cryptography 48.0.1  PYSEC-2026-3553  fix 49.0.0
cryptography 48.0.1  PYSEC-2026-3554  fix 49.0.0
```

AGT `v4.0.0` core declares:

```text
cryptography>=46.0.7,<49.0
```

That release cannot resolve either fixed version.

## AGT 5.0.0 migration probe

Draft PR #31 migrated the Qortara in-process foundation probe to the published:

```text
agent-governance-toolkit-core==5.0.0
```

and removed the unused direct Qortara pins on the separate 4.x `protocols` and `integrations` distributions.

Hosted evidence on the exact PR head shows:

- dependency resolution succeeds on Python 3.11, 3.12 and 3.13;
- Ruff lint and format checks pass;
- mypy passes;
- the complete Qortara unit/conformance suite passes on all supported Python versions;
- the langchain-core/langgraph compatibility-floor suite passes;
- compliance passes;
- gitleaks passes;
- Bandit executes independently and reports no medium/high findings;
- SBOM generation succeeds.

This empirically establishes that Qortara's existing `PolicyEngine.add_constraint(...)` / `check_violation(...)` integration is functionally compatible with the published AGT 5.0.0 package under the current test surface.

## Remaining published-release blocker

The AGT `v5.0.0` release tag declares:

```text
cryptography>=46.0.7,<50.0
agentrust-trace>=0.2.0,<0.3.0
```

The published environment therefore resolves `cryptography==49.0.0`. The current audit then reports one remaining vulnerability:

```text
cryptography 49.0.0  PYSEC-2026-3552  fix 50.0.0
```

So AGT 5.0.0 improves the result from three advisories to one, but the published release still cannot resolve the required `cryptography==50.0.0` fix.

## Upstream-current evidence

Current AGT source on `main` has already widened the core cryptography range to `<51.0`, and AGT's public dependency-audit documentation records successful testing with `cryptography==50.0.0` in current code paths.

That is useful evidence that the constraint has been addressed in upstream source. It is **not** authorization for Qortara Governance to consume an unreleased branch or Git dependency in place of a published release.

## Decision

1. Keep `pip-audit` blocking.
2. Do not add `--ignore-vuln` merely to restore a green badge.
3. Do not override a published AGT release's declared cryptography upper bound.
4. Do not make Qortara's distributed package depend on AGT `main` or another unreleased Git revision solely to clear this audit.
5. Keep AGT 5.0.0 compatibility evidence in #31 because it proves the major-version policy seam is viable.
6. Treat the final `PYSEC-2026-3552` result as a published-upstream-release dependency blocker until an AGT release permits the fixed cryptography version, or until a separately authorized dependency strategy is adopted.
7. Re-run the same blocking security gate on the exact future migrated head. Remediation evidence appends to this finding rather than replacing it.

## Boundary attribution

```text
Qortara Governance CI/security baseline
    -> reproducible and functioning

Qortara Governance AGT 4 -> 5 policy seam
    -> functionally compatible in hosted CI

Published AGT 5.0.0 dependency metadata
    -> constrains cryptography below the remaining fixed version

Microsoft AGT upstream
    -> read-only dependency source for this project
    -> no issue/comment/PR or other upstream write is authorized here
```

This classification keeps the security result red without falsely attributing the remaining advisory to Qortara application code or hiding it behind a successful integration test suite.
