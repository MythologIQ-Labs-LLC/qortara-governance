# Plan: Phase 11 — CI security + compliance gates

**change_class**: feature

**doc_tier**: standard

**boundaries**:
- limitations: First-cut CI gates. Hard gates: secret scan, governance-health, ledger verify. Report-only (non-blocking) initially: pip-audit, bandit, SBOM, SSDF/AI-Act report — hardened to blocking in a later pass once baseline is clean. SOC 2 is evidence-emission (SBOM + provenance artifacts), not a pass/fail gate.
- non_goals: No release/tag/PyPI; no change to package code.
- exclusions: Runtime enforcement code untouched.

## Open Questions

None. Tool availability verified: `pip-audit`, `bandit`, `cyclonedx-py` are public PyPI; `gitleaks/gitleaks-action@v2` is free for public repos; **`qor-logic==0.103.1` resolves from public PyPI** (`uv pip install --dry-run qor-logic --no-config` → would install) so CI can run `governance-health` / `verify-ledger` / `compliance report` (all confirmed exit 0 locally).

## Phase 1: Add security + compliance workflows

### Affected Files

- `.github/workflows/security.yml` (NEW) — on PR + push to main: `pip-audit` (dep vulns), `bandit` (Python SAST/OWASP), CycloneDX SBOM (artifact), and `gitleaks` secret scan.
- `.github/workflows/compliance.yml` (NEW) — on PR + push to main: install `qor-logic`; run `governance-health` (HARD: fails on DAMAGED/INCOMPLETE), `verify-ledger` (HARD: chain integrity), `compliance report` (SSDF/AI-Act, informational artifact).

### Changes

Two GitHub Actions workflows mirroring `ci.yml`'s uv setup. Hard gates fail the PR; report-only gates surface findings + artifacts without blocking (commented for later hardening). No package code changes.

### Unit Tests

None — CI configuration. Validation: YAML parses (`python -c "import yaml; yaml.safe_load(open(f))"`) and the referenced commands/tools are confirmed installable (grounded above). The authoritative test is the workflows executing on this PR.

## Feature Inventory Touches

_Empty — CI/infra + governance; touches no `src/`._

## Definition of Done

- **D1**: PRs to `main` run code-quality (existing `ci.yml`) + security (secrets/SAST/dep-vuln/SBOM) + compliance (governance-health/ledger/SSDF-AI-Act) automatically.
- **D2**: `security.yml` + `compliance.yml` present and YAML-valid.
- **D3**: META_LEDGER GATE+SEAL; committed to PR #13 (no tag/PyPI).
- **D4.d**: Waiver — CI config has no local unit test; validation = YAML parse + tool-availability grounding + live execution on PR #13. **Follow-up**: harden report-only gates to blocking after baseline triage.

## CI Commands

- `python -c "import yaml,sys; [yaml.safe_load(open(p)) for p in sys.argv[1:]]" .github/workflows/security.yml .github/workflows/compliance.yml` — YAML validity.
- `qor-logic governance-health --profile skill-entry` — gate parity locally.
