# Shadow Genome

## Purpose

The Shadow Genome documents **failure modes** — approaches that were rejected, patterns that failed, and lessons learned. This creates institutional memory to prevent repeated mistakes.

---

## Failure Categories

| Code | Category | Description |
|------|----------|-------------|
| `COMPLEXITY_VIOLATION` | Section 4 Razor breach | Function/file too long, nesting too deep |
| `SECURITY_STUB` | Incomplete security | Placeholder marker left in auth/security code |
| `GHOST_PATH` | Disconnected UI | UI element without backend handler |
| `HALLUCINATION` | Invalid dependency | Library that doesn't exist or wasn't verified |
| `ORPHAN` | Dead code | File not connected to build path |
| `SPEC_DRIFT` | Blueprint mismatch | Implementation doesn't match specification |
| `CHAIN_BREAK` | Merkle violation | Hash chain integrity compromised |

---

## Failure Log

No failures recorded yet. This is the genesis state of the chain — the genome is
seeded empty and populated by `/qor-audit` when a verdict is VETO, or by
implementation/refactor cycles when a rejected approach is captured.

<!--
Each future failure is documented with:
- Date and iteration
- What was attempted
- Why it failed
- Pattern to avoid
- Resolution (if any)
-->

---

## Pattern Library (Extracted Lessons)

No patterns extracted yet. Patterns are aggregated once a failure type recurs
3 or more times.

---

## Failure Statistics

| Category | Count | Last Occurrence |
|----------|-------|-----------------|
| COMPLEXITY_VIOLATION | 0 | — |
| SECURITY_STUB | 0 | — |
| GHOST_PATH | 0 | — |
| HALLUCINATION | 0 | — |
| ORPHAN | 0 | — |
| SPEC_DRIFT | 0 | — |
| CHAIN_BREAK | 0 | — |

**Total Failures Recorded**: 0
**Failures Resolved**: 0
**Patterns Extracted**: 0

---

## Usage Notes

1. **Add entries when**:
   - `/qor-audit` returns VETO
   - Implementation fails Section 4 checks
   - Dead code is discovered
   - Any rejected approach

2. **Review entries when**:
   - Starting similar work
   - Seeing repeated violations
   - Onboarding new contributors

3. **Extract patterns when**:
   - Same failure type occurs 3+ times
   - A clear anti-pattern emerges

---

*Shadow Genome maintained by The Qor-logic Judge*
*"Learn from failure to prevent its repetition."*
