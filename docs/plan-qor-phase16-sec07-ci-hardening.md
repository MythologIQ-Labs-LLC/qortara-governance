# Plan — Phase 16: SEC-07 bypass-surface hardening + CI-01/02 gate hardening

**Risk Grade**: L3 (touches enforcement internals + security CI gates)
**iteration**: ready-for-audit
**Author**: Governor (auto-dev-1)
**Target**: deferred red-team items GAP-SEC-07 (HIGH), GAP-CI-01 (HIGH), GAP-CI-02 (MED)
**Cycle scope**: SEC-07 + CI-01 + CI-02 only. No expansion.

## Framing (honesty up front)
GAP-SEC-07 lives **inside the cooperative-process boundary** (THREAT-MODEL §5): the SDK
explicitly does **not** defend against hostile in-process code that restores patched methods
or imports internals. This cycle is **defense-in-depth** — it removes a gratuitous bypass
handle and raises the bar for *accidental/casual* exemption. It does **not** claim to defend
against a determined in-process adversary, and THREAT-MODEL §5 stays as-is.

## Evidence (verified)
- `__qortara_original__` is **written** on all four dispatch wrappers (`tool_patches.py:142,155`,
  `langgraph_patches.py:94,109`) but **read nowhere** — `unpatch` uses the returned `originals`
  dict; only `__qortara_wrapped__` is consumed (double-install guard + tests). It is pure
  bypass-aid ("here is the original method, restore me").
- `qortara_exempt` sets `__qortara_exempt__ = True`; `is_exempt` treats **any truthy value** as
  exempt (`decorators.py:18,24-27`). So `setattr(tool, "__qortara_exempt__", True)` from anywhere
  — or an accidental attribute collision — silently disables enforcement for that tool.
- `security.yml`: pip-audit + bandit are `|| true` (report-only); locally both exit **0** today
  (`bandit -r src -ll` → 0 issues; `pip-audit` → no known vulns). gitleaks tarball is downloaded
  with no integrity check (curl | tar). Authoritative SHA256 for `gitleaks_8.21.2_linux_x64.tar.gz`
  (from the release `checksums.txt`): `5bc41815076e6ed6ef8fbecc9d9b75bcae31f39029ceb55da08086315316e3ba`.

## Promise (Definition of Done)

### D1 — Vision
The SDK exposes no gratuitous bypass handle, exemption requires the official decorator (not a
coincidental bool), and the security CI gates that *can* block actually block.

### D2 — Code
1. **SEC-07a**: remove `wrapper.__qortara_original__ = original` from all four wrappers
   (`tool_patches` sync+async, `langgraph_patches` sync+async). `__qortara_wrapped__` stays
   (load-bearing). `unpatch` is unaffected (uses `originals`).
2. **SEC-07b**: gate exemption on a module-private sentinel. `qortara_exempt` sets
   `__qortara_exempt__ = _EXEMPT_MARKER` (a module-level `object()`); `is_exempt` returns True
   only when the instance- or class-attr **is** that exact marker (`is` identity, not truthiness).
   A raw `setattr(tool, "__qortara_exempt__", True)` no longer exempts — only the decorator
   (or code that imports the private marker) can. Docstring documents this as defense-in-depth.

### D3 — Governance (CI)
3. **CI-01**: drop `|| true` from **bandit** and **pip-audit** in `security.yml` so they block
   the PR (both pass clean today). pip-audit carries a comment documenting the
   `--ignore-vuln GHSA-…` escape for a future unfixable transitive advisory. **SBOM stays
   tolerant** (`|| true`) — it is artifact generation, not a security finding; failing the build
   on a CycloneDX tooling hiccup adds no security value (rationale stated inline).
4. **CI-02**: pin the gitleaks download — verify the tarball against the hardcoded SHA256
   (`echo "<sha>  <file>" | sha256sum -c -`) **before** extraction; abort on mismatch.

### D4 — Empirical
- `test_raw_exempt_attr_does_not_exempt` — `setattr(tool, "__qortara_exempt__", True)` is NOT
  exempt (still governed → denied under scripted DENY); the SEC-07b boundary.
- `test_decorator_still_exempts` — `@qortara_exempt` still exempts (regression).
- `test_wrappers_do_not_expose_original` — patched `BaseTool.run`/`.arun` have no
  `__qortara_original__` attribute (SEC-07a).
- CI gates: validated by the security workflow run on the PR (bandit/pip-audit now blocking,
  gitleaks checksum-verified) — tracked to green.

## Section 4 Razor
No new module/dep. Deletes an attribute; swaps a bool for an identity sentinel; edits YAML.

## Blast radius
`__qortara_original__` removal: nothing reads it (verified). Sentinel exempt: existing
`@qortara_exempt` usages unaffected (decorator still the API); only raw-attr exemption (never a
supported path) stops working. CI: bandit/pip-audit clean today → no spurious red; if a future
advisory lands, the documented `--ignore-vuln` escape applies. gitleaks pin is version-locked to
8.21.2 (already pinned); a version bump must update the hash (noted in a comment).

## Non-goals
- Defending against hostile in-process code (out of boundary, THREAT-MODEL §5 — unchanged).
- `require_compatible_protocol` wiring, GAP-DOC-01(rest), MED/LOW — deferred.

## Review Boundary
Commit + push to PR #13. NO tag, NO PyPI. No AI footer.
