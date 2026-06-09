# Qor-logic Meta Ledger

## Chain Status: ACTIVE
## Genesis: 2026-06-09T06:55:38Z

---

### Entry #1: GENESIS

**Timestamp**: 2026-06-09T06:55:38Z
**Phase**: BOOTSTRAP
**Author**: Governor
**Risk Grade**: L3

**Content Hash**:
SHA256(CONCEPT.md + ARCHITECTURE_PLAN.md) = 75e90e2febcaebc343387fe9091fcc28dc501b1d3148ca00bd5195dbbd19ab9f

**Previous Hash**: GENESIS (no predecessor)

**Decision**: Project DNA initialized for `qortara-governance` (existing Alpha codebase). Lifecycle: ALIGN/ENCODE complete. Security path detected — `/qor-audit` mandatory before implementation.

---

### Entry #2: GATE TRIBUNAL

**Timestamp**: 2026-06-09T07:00:00Z
**Phase**: GATE
**Author**: Judge
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT.md) = 987b9891ed743f12e70d356dbda617d01dc17e1fb371f1d214f61fd75bc5e90b

**Previous Hash**: 75e90e2febcaebc343387fe9091fcc28dc501b1d3148ca00bd5195dbbd19ab9f

**Chain Hash**:
SHA256(content_hash + previous_hash) = d2f8e1656e717ddd6daf833fb13764e0102941e54db22324858156410c324eb6

**Decision**: Genesis blueprint cleared all binding passes (prompt-injection, security-L3, OWASP, ghost-UI, razor, dependency, macro-architecture, infrastructure-alignment, filter-stage, orphan). Documentation-only artifact; no violations. PASS authorizes DNA/docs only — every future `/qor-implement` cycle touching `src/` re-enters its own L3 tribunal. Plan.json gate absent (genesis); operator override recorded.

---

### Entry #3: GATE TRIBUNAL — Phase 01 (D1 version drift)

**Timestamp**: 2026-06-09T07:12:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L1
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase01.md) = ea3ed0b59b5d4bd061599f99f9c201b00a3689148cec9b6c8310dc392d20bf74

**Previous Hash**: 987b9891ed743f12e70d356dbda617d01dc17e1fb371f1d214f61fd75bc5e90b

**Chain Hash**:
SHA256(content_hash + previous_hash) = a8cc27026a6030a7927f27a6e88219c3cd12336bca797dadadf472bceea44929

**Decision**: Plan to align runtime `__version__` 0.2.0 → 0.2.1 + add functional consistency test cleared all binding passes. No violations. Cleared for /qor-implement.

---

### Entry #4: SEAL — Phase 01 (D1 version drift)

**Timestamp**: 2026-06-09T07:20:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L1
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(__init__.py + test_version_consistency.py) = 63802c1f363839238f5db6176d1fbcc3cb7106004ad80a14b3ed4e41707c5682

**Previous Hash**: ea3ed0b59b5d4bd061599f99f9c201b00a3689148cec9b6c8310dc392d20bf74

**Chain Hash**:
SHA256(content_hash + previous_hash) = 1d5bb0416176aa6bcc74490a6196904b9fcba07cc02abe3d133da6f15d7c622b

**Decision**: Reality == Promise. `__version__` = 0.2.1; full suite 57 passed / 2 skipped; ruff clean; prose-lint clean. FEATURE_INDEX FX-version Verified; BACKLOG D1 closed. Publish actions (git tag `v0.2.1`) held at Review Boundary.

---

### Entry #5: GATE TRIBUNAL — Phase 02 (B4 threat model)

**Timestamp**: 2026-06-09T07:26:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L1
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase02.md) = 15ef5bf47405f15a50b26bbf8de304d4ae3877348618231821794b78e5a80494

**Previous Hash**: 63802c1f363839238f5db6176d1fbcc3cb7106004ad80a14b3ed4e41707c5682

**Chain Hash**:
SHA256(content_hash + previous_hash) = 64889b2a3c1b2336e406ac90b8e72018dd643714d7039881410d9a17c69786c9

**Decision**: Doc-only plan for `docs/security/THREAT-MODEL.md` cleared all binding passes (test/feature exempt). No violations. Cleared for /qor-implement.

---

### Entry #6: SEAL — Phase 02 (B4 threat model)

**Timestamp**: 2026-06-09T07:30:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L1
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(THREAT-MODEL.md) = 1269f0702dc6d8363576b44fd3b8019a019cdad7f2fdade24e2af99d5532d332

**Previous Hash**: 15ef5bf47405f15a50b26bbf8de304d4ae3877348618231821794b78e5a80494

**Chain Hash**:
SHA256(content_hash + previous_hash) = 08c1a6afedbceee15958e19e9e2d0dc0580ee6f26960729664aab15e95771607

**Decision**: Reality == Promise. THREAT-MODEL.md covers all 16 §11.1 threats + §7.3 bypass model + fail-closed posture; governance-health passes; registered in GOVERNANCE_INDEX Tier 2; BACKLOG B4 closed. No publish action pending.

---

### Entry #7: GATE TRIBUNAL — Phase 03 (B2 protocol/exception contracts)

**Timestamp**: 2026-06-09T07:36:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase03.md) = fdc1587a46be7b61fbbb79c7a99558b09a7eb9fd62afe195b34b833f13b23f98

**Previous Hash**: 1269f0702dc6d8363576b44fd3b8019a019cdad7f2fdade24e2af99d5532d332

**Chain Hash**:
SHA256(content_hash + previous_hash) = 2870e6b667924b3945310730197c7c517d8d729b899778025b7aa8032c0d063a

**Decision**: Plan to promote `v0.1` literal to `PROTOCOL_VERSION` constant + add `QortaraProtocolMismatch` + freeze exception `__all__` cleared all binding passes (L2). Additive/non-breaking. Cleared for /qor-implement.

---

### Entry #8: SEAL — Phase 03 (B2 protocol/exception contracts)

**Timestamp**: 2026-06-09T07:42:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(protocol_version.py + exceptions.py + client.py + __init__.py + test_protocol_versioning.py) = dce542a4f6c9d37677ce1db9f3ed1166cfe62126223679dbc91414d893487972

**Previous Hash**: fdc1587a46be7b61fbbb79c7a99558b09a7eb9fd62afe195b34b833f13b23f98

**Chain Hash**:
SHA256(content_hash + previous_hash) = 8c67baf7c0271290aedfb9d59abe0b23b50df7de2e3f1b2f5454346e0fdd8748

**Decision**: Reality == Promise. `PROTOCOL_VERSION` drives all 3 sidecar endpoints; `require_compatible_protocol` fails closed on major mismatch; exception `__all__` frozen + `QortaraProtocolMismatch` added. Full suite 61 passed / 2 skipped; ruff + prose-lint clean. FEATURE_INDEX FX-protocol-version + FX-exceptions Verified; BACKLOG B2 closed (B2-followup opened). No publish action pending.

---
*Chain integrity: VALID*
*Batch 1 (D1/B4/B2) complete. Next: auto-dev batch 2 — next 3 priorities (S1, S2, B1).*

---

### Entry #9: GATE TRIBUNAL — Phase 04 (S1 sidecar scaffold)

**Timestamp**: 2026-06-09T07:52:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: PASS (documented limitation: auth deferred to S2)

**Content Hash**:
SHA256(AUDIT_REPORT-phase04.md) = e0114fe96ba37b8ee79eef4cf3e72a6b25014329e77a14ee4284d2d8be403d31

**Previous Hash**: dce542a4f6c9d37677ce1db9f3ed1166cfe62126223679dbc91414d893487972

**Chain Hash**:
SHA256(content_hash + previous_hash) = eb198f591a02bdcaf2420926c6f5a4820e987460bafe7e93ac0e7740b5803eb7

**Decision**: L3 sidecar-scaffold plan cleared all binding passes. Core invariant fail-closed default-deny; no fail-open/mock-auth/unsafe-deser; loopback-only. Auth/TLS explicitly deferred to S2 (documented limitation, not a violation). Cleared for /qor-implement.

---

### Entry #10: SEAL — Phase 04 (S1 sidecar scaffold)

**Timestamp**: 2026-06-09T08:00:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: SEALED (local hold; scaffold)

**Content Hash**:
SHA256(qortara_sidecar/{__init__,policy,evaluator,app,__main__}.py + pyproject.toml) = 1cb69d0addaee5a0145145b578717a7b0ac4f6718f70e840ab06359821a66ab3

**Previous Hash**: e0114fe96ba37b8ee79eef4cf3e72a6b25014329e77a14ee4284d2d8be403d31

**Chain Hash**:
SHA256(content_hash + previous_hash) = 4016811d5b7094791527aed34244aa1161eb3ba32a231bf78b8445ce3e14aa75

**Decision**: Reality == Promise. New package `qortara-governance-sidecar` (evaluator + policy + app + entry); 18 tests pass (fail-closed default-deny asserted); combined suite 79 passed / 2 skipped; ruff + prose-lint clean; `uv sync` registers the member. FEATURE_INDEX +3 Verified; BACKLOG S1 → scaffold-done. Scaffold scope per operator authorization; hardening (auth/TLS) is S2. No publish action pending.

---
*Chain integrity: VALID*
*Next required action: Phase 05 (S2 authenticated transport)*

---

### Entry #11: GATE TRIBUNAL — Phase 05 (S2 authenticated transport)

**Timestamp**: 2026-06-09T08:06:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase05.md) = 299878d45abd36fef77bc75e201bbd22dd138380808d57b9cac29d0cbf5fc639

**Previous Hash**: 1cb69d0addaee5a0145145b578717a7b0ac4f6718f70e840ab06359821a66ab3

**Chain Hash**:
SHA256(content_hash + previous_hash) = 85e6ebece1aee547bf4122c56a237f92e6d2089ef1525f4c62bb30c200e7068f

**Decision**: L3 auth plan cleared all binding passes. Constant-time compare, reject-by-default, no hardcoded/logged token, no fail-open. Closes threat-model 2/3/16. Cleared for /qor-implement.

---

### Entry #12: SEAL — Phase 05 (S2 authenticated transport)

**Timestamp**: 2026-06-09T08:12:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(auth.py + app.py + __main__.py + test_auth.py) = bb5970e9f73ef855d910d5afbfd2896fbc7303109a888f1b8f9363bd7f816905

**Previous Hash**: 299878d45abd36fef77bc75e201bbd22dd138380808d57b9cac29d0cbf5fc639

**Chain Hash**:
SHA256(content_hash + previous_hash) = 3d5c62e07d5707a9906ac31944b28586435ab70271d31f53965400e5eba3b829

**Decision**: Reality == Promise. Bearer-token enforcement on sensitive endpoints (constant-time, reject-by-default, token never logged); health/version stay unauth; 28 sidecar tests pass (18 S1 + 10 auth, backward-compatible). ruff + prose-lint clean. FEATURE_INDEX +1 Verified; BACKLOG S2 → sidecar-side done. Closes threat-model 2/3/16 on the sidecar. No publish action pending.

---
*Chain integrity: VALID*
*Next required action: Phase 06 (B1 conformance suite)*

---

### Entry #13: GATE TRIBUNAL — Phase 06 (B1 conformance suite)

**Timestamp**: 2026-06-09T08:21:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase06.md) = d747d665e121732c507feb43d02d0415a563de122839873c9c13dea8e41a19b5

**Previous Hash**: bb5970e9f73ef855d910d5afbfd2896fbc7303109a888f1b8f9363bd7f816905

**Chain Hash**:
SHA256(content_hash + previous_hash) = c2e57cc79f05b85c0ee21a776fefd4b8e8e501881c82c490cf6b5be34f54229b

**Decision**: L2 conformance-suite plan cleared all binding passes. All 7 tests behavioral (execution-or-not + exception type). Cleared for /qor-implement.

---

### Entry #14: SEAL — Phase 06 (B1 conformance suite)

**Timestamp**: 2026-06-09T08:28:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(tests/conformance/test_basetool_dispatch.py) = 17539e776ce5e408e4719c288fa165acf6c18388a78e76ab50bef395bc8adee4

**Previous Hash**: d747d665e121732c507feb43d02d0415a563de122839873c9c13dea8e41a19b5

**Chain Hash**:
SHA256(content_hash + previous_hash) = 28abe5d2e390512a950e96e5243a36986739d2128de83b5931c0c4b64be8ad7c

**Decision**: Reality == Promise. 7 conformance tests pass: BaseTool sync+async × allow/deny/require_approval, exempt bypass, no-context boundary. Combined suite 96 passed / 2 skipped; ruff + prose-lint clean. FEATURE_INDEX FX-enforcement-dispatch Verified; BACKLOG B1 → core done (B1-followup opened). No publish action pending.

---
*Chain integrity: VALID*
*Batch 2 (S1/S2/B1) complete. All 6 cycles sealed. Awaiting operator review (Review Boundary).*

---

### Entry #15: GATE TRIBUNAL — Phase 07 (ADR-0001 Increment A: extend-on-AGT)

**Timestamp**: 2026-06-09T09:02:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase07.md) = 28f1aeb1e0acf670ceab40dad4658f01c249490901beea34f0360e025ab665fe

**Previous Hash**: 17539e776ce5e408e4719c288fa165acf6c18388a78e76ab50bef395bc8adee4

**Chain Hash**:
SHA256(content_hash + previous_hash) = dc92525c27ef8d0c0aea73cd604de539be087ee6f414b0afe6618c3fe94c068a

**Decision**: Increment A (depend on agent-governance-toolkit[full]==4.0.0 + probe; retire S1 sidecar scaffold; reposition docs) cleared all binding passes incl. Self-Application vs ADR-0001 (no vendor, no AGT-internal modification). L3 enforcement re-base deferred to Increment B. Cleared for /qor-implement.

---

### Entry #16: SEAL — Phase 07 (ADR-0001 Increment A: extend-on-AGT)

**Timestamp**: 2026-06-09T09:20:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(pyproject.toml + agt.py + test_agt_dependency.py + ci.yml) = d38597e8e9cc4f87ab96faaccb66d97875d8ddb17a8a62401ad31b64fc98591a

**Previous Hash**: 28f1aeb1e0acf670ceab40dad4658f01c249490901beea34f0360e025ab665fe

**Chain Hash**:
SHA256(content_hash + previous_hash) = b6eba9d4b87f415e7fb0fb6a35257513ea16246d7b96d2651097d0957211300d

**Decision**: Reality == Promise (with two recorded amendments). qortara now depends on **AGT** library components `agent-governance-toolkit-{core,protocols,integrations}==4.0.0` (not `[full]` — drops `-cli`); `agt.py` probe + test confirm `-core` resolves. **Python floor raised 3.10 → 3.11** (AGT requirement; operator-approved compat decision; classifier + CI matrix updated). S1/S2 sidecar scaffold **retired** (package deleted; `uv sync` drops the member). Docs (CONCEPT, ARCHITECTURE_PLAN, both READMEs) repositioned to "extends AGT." Full langchain suite 70 passed / 2 skipped; ruff + prose-lint + governance-health clean. FEATURE_INDEX reconciled (5 Verified); BACKLOG S1/S2 reframed. **Audit caveat recorded**: dry-run resolvability check missed AGT's 3.11 floor (see AUDIT_REPORT-phase07 addendum). **Increment B (L3, next cycle):** wire the dispatch patch into AGT's engine + reconcile `qortara_protocol` ↔ `agent-governance-toolkit-protocols`.

---
*Chain integrity: VALID*
*Next required action: Increment B (L3) — dispatch-patch → AGT engine + protocol reconcile*

---

### Entry #17: GATE TRIBUNAL — Phase 08 (ADR-0001 Increment B: dispatch → AGT engine)

**Timestamp**: 2026-06-09T09:42:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: PASS (documented limitation: arg-safety needs arg threading — follow-up)

**Content Hash**:
SHA256(AUDIT_REPORT-phase08.md) = 177b9c016faf8d2c30a534bf6702d8e12ba7b30b3a5ff704c6270527f4b3d433

**Previous Hash**: d38597e8e9cc4f87ab96faaccb66d97875d8ddb17a8a62401ad31b64fc98591a

**Chain Hash**:
SHA256(content_hash + previous_hash) = 87fcf8e0978a1ea76a409e88dd2aae756ab41e6779f49cc436d79eef95834757

**Decision**: L3 plan to add `AgtDecisionClient` (drop-in decision source over AGT in-process `PolicyEngine.check_violation`) + `init_agt` cleared all binding passes incl. Self-Application vs ADR-0001. Fail-closed preserved; existing SidecarClient path unchanged. Cleared for /qor-implement.

---

### Entry #18: SEAL — Phase 08 (ADR-0001 Increment B: dispatch → AGT engine)

**Timestamp**: 2026-06-09T09:55:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(agt_engine.py + __init__.py + test_agt_enforcement.py) = 82fff138debaa3fbab5314ce7e8157312a0527883c0428853f16ea3ab7b34a73

**Previous Hash**: 177b9c016faf8d2c30a534bf6702d8e12ba7b30b3a5ff704c6270527f4b3d433

**Chain Hash**:
SHA256(content_hash + previous_hash) = 06af0f94ebd1ded4c6051d107bbf5534e8c36d271646f82f8643f1147fbb593a

**Decision**: Reality == Promise. `AgtDecisionClient` routes the real `BaseTool.invoke` dispatch patch into AGT's in-process `agent_control_plane.PolicyEngine` (verified by read); `init_agt(agent_id, allowed_tools)` is the one-call local entry. 5 conformance tests pass (allow runs once / unlisted → `QortaraPolicyDenied` / `init_agt` end-to-end); full langchain suite 75 passed / 2 skipped; ruff + prose clean; SidecarClient path unregressed. FEATURE_INDEX FX-agt-enforcement Verified (6 total); BACKLOG S1 closed, S2 largely moot (in-process). **Documented limitation:** AGT arg-safety checks need tool args threaded through `build_tool_action` (privacy tradeoff) — open follow-up. No publish action pending.

---
*Chain integrity: VALID*
*Increment B complete. Follow-ups: arg-safety threading; qortara_protocol↔agent-governance-toolkit-protocols reconcile; sidecar/client/launcher cleanup; LangGraph ToolNode AGT wiring.*

---

### Entry #19: RESEARCH BRIEF — AxonFlow comparative

**Timestamp**: 2026-06-09T10:10:00Z
**Phase**: RESEARCH
**Author**: Analyst
**Risk Grade**: L1

**Content Hash**:
SHA256(research-brief-axonflow-2026-06-09.md) = 8342cb1324df22bc5b40eb034fadc8a3708df037186b21380d1786612c5b2d12

**Previous Hash**: 82fff138debaa3fbab5314ce7e8157312a0527883c0428853f16ea3ab7b34a73

**Chain Hash**:
SHA256(content_hash + previous_hash) = 1fe16284b454928030288a9b5ad8c8a3b1f00ec20f9f3802feb9eed9f4c09cd2

**Decision**: AxonFlow verified real — source-available (BSL 1.1) Go runtime AI control plane; inline gateway/proxy/SDK enforcement, framework-agnostic, no native LangChain dispatch interception. It is an **AGT-class control plane (peer to qortara's foundation), not a direct qortara competitor**. qortara's moat (in-process `BaseTool.invoke` dispatch-path interception / AGT #73 closure) is orthogonal and uncovered by AxonFlow's route-through model. Advisory only; no architecture change (ADR-0001 stands). Brief: `docs/research-brief-axonflow-2026-06-09.md`.

---
*Chain integrity: VALID*
*Next required action: resume arg-safety threading follow-up (Increment B follow-up)*

---

### Entry #20: GATE TRIBUNAL — Phase 09 (AGT arg-safety threading)

**Timestamp**: 2026-06-09T10:27:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase09.md) = b9ef92565edaae34c6593f3f52f73881d92351f9690e5f526b5799240202af48

**Previous Hash**: 8342cb1324df22bc5b40eb034fadc8a3708df037186b21380d1786612c5b2d12

**Chain Hash**:
SHA256(content_hash + previous_hash) = 481d2ac9eb35074e332f853ee92f8fec9b4d07df8cd5ce27bbc63880bcc3bdfe

**Decision**: L3 plan to thread `tool_input` into the in-process AGT decision (enabling arg-safety checks; wire privacy preserved) cleared all binding passes. Net security improvement; caller contract enumerated. Cleared for /qor-implement.

---

### Entry #21: SEAL — Phase 09 (AGT arg-safety threading)

**Timestamp**: 2026-06-09T10:40:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(agt_engine.py + client.py + tool_patches.py + test_agt_arg_safety.py + conftest.py) = 5849dbb214a32ee14f5c8e9627c96801ad8055124043bfff4d9cd934a2d864d5

**Previous Hash**: b9ef92565edaae34c6593f3f52f73881d92351f9690e5f526b5799240202af48

**Chain Hash**:
SHA256(content_hash + previous_hash) = b2c181228a65a7e30e79829a765abc1bd9df75f56b52ce7225b087f56a1719cd

**Decision**: Reality == Promise. `_decide_or_raise` threads `tool_input` to `client.decide(request, tool_input)`; `AgtDecisionClient` feeds it to AGT's in-process `check_violation` (SQL/code/path/endpoint checks now fire); `SidecarClient` accepts-and-ignores it (wire privacy preserved, verified by a body-inspection test). 4 arg-safety tests pass; full suite 79 passed / 2 skipped; ruff + prose clean. **Caller-contract miss corrected mid-cycle:** `tests/conftest.py` fake `decide` also needed the new param (5 patch-suite tests failed, then fixed) — enumeration had missed it. FEATURE_INDEX FX-agt-enforcement updated; BACKLOG arg-safety follow-up closed.

---
*Chain integrity: VALID*
*Increment B arg-safety follow-up complete. Remaining roadmap follow-ups: qortara_protocol↔agent-governance-toolkit-protocols reconcile; sidecar/client/launcher cleanup; LangGraph ToolNode AGT wiring.*

---

### Entry #22: RESEARCH CORRECTION — AxonFlow brief (operator feedback)

**Timestamp**: 2026-06-09T10:55:00Z
**Phase**: RESEARCH
**Author**: Analyst
**Risk Grade**: L1

**Content Hash**:
SHA256(research-brief-axonflow-2026-06-09.md, amended) = 316fb1ac9d5a2188abdb1da9a3b12cb198393f34d59894166eda52cf335be410

**Previous Hash**: 5849dbb214a32ee14f5c8e9627c96801ad8055124043bfff4d9cd934a2d864d5

**Chain Hash**:
SHA256(content_hash + previous_hash) = f9ebca36503a92b22005ff6530a0be349885874a50f1378eb84b0bb0e033a9ec

**Decision**: Operator corrected the brief on two axes (supersedes Entry #19's breadth/positioning rows). (1) **Breadth retracted as a gap** — qortara depends on the *full* AGT library surface, so it inherits AGT-class breadth + the dispatch moat (parity-plus, not narrow). (2) **PAMA upstream authoritative decision engine** added as a third architecture tier (centralized + governed adaptive-state), beyond AxonFlow's documented scope. **PAMA is operator-asserted** — absent from AGT/installed packages/working tree; roadmap §24/§26 references it once without expanding the acronym; canonical definition/source still owed (flagged, not fabricated).

---
*Chain integrity: VALID*
*Open item: obtain canonical PAMA definition/source to substantiate the upstream-authoritative tier in the brief.*

---

### Entry #23: RESEARCH BRIEF — Documentation alignment audit

**Timestamp**: 2026-06-09T11:20:00Z
**Phase**: RESEARCH
**Author**: Analyst
**Risk Grade**: L1

**Content Hash**:
SHA256(research-brief-docs-alignment-2026-06-09.md) = 3613a7aeb913468c18f84f1d787faf01037edc545fb368440f740fe4f408d2c6

**Previous Hash**: 316fb1ac9d5a2188abdb1da9a3b12cb198393f34d59894166eda52cf335be410

**Chain Hash**:
SHA256(content_hash + previous_hash) = 3e485b9b077171681ab9f70564221c7eed20b22d9dab0deba723a1a214ee2adc

**Decision**: 6 documentation-alignment drift clusters detected, all L1 (docs-only): ARCHITECTURE_PLAN body (self-contradictory, still sidecar), SYSTEM_STATE (lists deleted sidecar package + Python 3.10), README/package Quickstart (bare init() vs init_agt()), pyproject "sidecar SDK" description, THREAT-MODEL sidecar-centric, CONTRIBUTING/SECURITY sidecar-client framing. Pulled ARCHITECTURE-BOUNDARIES/CONCEPT/ADR-0001 layering verified ALIGNED. Historical artifacts (ADR/component-map/plans/ledger/briefs) explicitly out of scope. Feeds the /qor-auto-dev-1 remediation cycle.

---
*Chain integrity: VALID*
*Next required action: /qor-auto-dev-1 — remediate the 6 doc-alignment drifts*

---

### Entry #24: GATE TRIBUNAL — Phase 10 (documentation alignment)

**Timestamp**: 2026-06-09T11:32:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L1
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase10.md) = 45744e0ba96c0e182fad90b7f4e5cb20b6ea80983ceca8b17596fbeb0133d33c

**Previous Hash**: 3613a7aeb913468c18f84f1d787faf01037edc545fb368440f740fe4f408d2c6

**Chain Hash**:
SHA256(content_hash + previous_hash) = cbf1bf628bd57b50a1c66a10c0665239dc0c79ee32be71fcaf09e5e5429de3cf

**Decision**: Docs-only realignment plan (8 forward-facing files → AGT-in-process; historical artifacts excluded) cleared all binding passes (test/feature exempt). Cleared for /qor-implement.

---

### Entry #25: SEAL — Phase 10 (documentation alignment)

**Timestamp**: 2026-06-09T11:45:00Z
**Phase**: SEAL (substantiate, local — Review Boundary)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L1
**Verdict**: SEALED (local hold)

**Content Hash**:
SHA256(ARCHITECTURE_PLAN + SYSTEM_STATE + README + pkg README + pyproject + THREAT-MODEL + CONTRIBUTING + SECURITY) = fb7b7f12cd682d2958eadc3d4ddaeee498c8189acea6cff029a8fa3aacc421f7

**Previous Hash**: 45744e0ba96c0e182fad90b7f4e5cb20b6ea80983ceca8b17596fbeb0133d33c

**Chain Hash**:
SHA256(content_hash + previous_hash) = 0e34d01829004436148a320a2c70027c8b268c35551af64eb972f861c8756d9a

**Decision**: Reality == Promise. All 6 alignment drifts resolved: ARCHITECTURE_PLAN body → AGT-in-process (sidecar demoted to optional remote-daemon); SYSTEM_STATE refreshed to Phase-09 reality (deleted sidecar pkg, Python 3.11, 79 passed/2 skipped); root+pkg README Quickstart → `init_agt()`; pyproject description de-"sidecar-SDK"-ed; THREAT-MODEL re-scoped (threats 2/3 = remote-daemon-only); CONTRIBUTING/SECURITY reframed (AGT in-process primary). **Scope note:** also aligned `[tool.mypy] python_version` 3.10→3.11 (same pivot, surfaced by the verify re-grep). Historical artifacts untouched. governance-health clean; full suite 79 passed/2 skipped (no regression); residual stale markers cleared.

---
*Chain integrity: VALID*
*Documentation aligned to AGT-foundation reality. Open follow-ups unchanged: protocol reconcile; sidecar/client/launcher cleanup; LangGraph ToolNode → AGT.*

---

### Entry #26: SESSION SEAL — substantiation (local hold)

**Timestamp**: 2026-06-09T11:55:00Z
**Phase**: SUBSTANTIATE
**Author**: Judge
**Risk Grade**: L3 (session spans L1–L3 phases)
**Verdict**: PASS — Reality == Promise
**Version**: 0.2.1 (held; no bump/tag this seal — Review Boundary local-hold)

**Merkle Seal**:
content_hash SHA256(SYSTEM_STATE.md) = 774bd1262878e96218f34a51332a92adb0b07d1ec91da05926cb47aba5da1cf1
previous_hash = fb7b7f12cd682d2958eadc3d4ddaeee498c8189acea6cff029a8fa3aacc421f7
chain/merkle = f632c71ae40f6148869ca6b558ba211f157378500a03788130fef4e698706757

**Reality Audit**: all ARCHITECTURE_PLAN-described src files exist (`agt.py`, `agt_engine.py`, `client.py`, `exceptions.py`, `protocol_version.py`, `patches/tool_patches.py`, `__init__.py`); the retired `qortara-governance-sidecar` package is confirmed absent. No MISSING; no unplanned drift.

**Functional**: full langchain suite **79 passed / 2 skipped**; ruff + prose-lint clean; governance-health clean.

**Gates**: skill_admission PASS · gate_skill_matrix 0-broken · secret_scanner clean (exit 0). **SKIP (Phase 75 declarative tolerance):** `intent_lock` — this session sealed per-phase via the `/qor-auto-dev-1` orchestrator rather than a single formal `/qor-implement` lock; `gate_chain_completeness` phase-min 52 — session phases are 01–10 (grandfathered). `gate_skipped_prerequisite_absent` recorded for the absent intent-lock path.

**Feature Inventory**: Total 6 / verified 6 / unverified 0 / n/a 0.

**Session scope sealed**: Phases 01–10 (genesis audit → D1/B4/B2 → S1/S2/B1 → ADR-0001 Increment A → Increment B → arg-safety → docs alignment) + 3 research briefs (AxonFlow, AxonFlow correction, docs-alignment). 26 ledger entries; chain VALID.

**Provenance correction (recorded)**: AGT has been foundational from inception — NOT a pivot. The genesis bootstrap's "independent alternative to AGT" framing was an analyst error, corrected Phase 07; "AGT pivot" in process artifacts means "correction of the genesis framing." See CONCEPT.md provenance note.

**Decision**: Session substantiated and sealed locally. Review Boundary honored — **no commit, tag, push, or publish**. All work remains in the working tree for operator review.

---
*Chain integrity: VALID — SESSION SEALED (local hold)*
*Next action (operator-gated): commit the sealed working tree, then /qor-repo-release. Both cross the Review Boundary and require explicit go-ahead.*

> **Post-seal continuation (operator-authorized):** session committed (`586a818`) + pushed; PR #13 opened (no tag/PyPI; no AI footer per operator). Phases 11+ append below.

---

### Entry #27: GATE TRIBUNAL — Phase 11 (CI security + compliance gates)

**Timestamp**: 2026-06-09T12:17:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase11.md) = 5ba3835958abec07d60442d4cfb0c31bf73c604d0fd0171af88c888d6cbf2d0e

**Previous Hash**: 774bd1262878e96218f34a51332a92adb0b07d1ec91da05926cb47aba5da1cf1

**Chain Hash**:
SHA256(content_hash + previous_hash) = 6b33871ceb1fa01c54db47a5054e8d4ff4fc121beee13584ab89f01287d5541c

**Decision**: Plan to add `security.yml` + `compliance.yml` CI gates cleared all binding passes (tools grounded as public/installable). Net security posture improvement. Cleared for /qor-implement.

---

### Entry #28: SEAL — Phase 11 (CI security + compliance gates)

**Timestamp**: 2026-06-09T12:25:00Z
**Phase**: SEAL (substantiate, local — Review Boundary: commit+push to PR #13, no tag/PyPI)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L2
**Verdict**: SEALED

**Content Hash**:
SHA256(security.yml + compliance.yml) = ae6d1941a422d26d563a23a1e5e54e860797b580d523a764cf6569cc6b5aa0ba

**Previous Hash**: 5ba3835958abec07d60442d4cfb0c31bf73c604d0fd0171af88c888d6cbf2d0e

**Chain Hash**:
SHA256(content_hash + previous_hash) = 8e49c1090cadfeb6bbabb17497d800bec53a9f421b0156b05fcb8e30a4b6d4cf

**Decision**: Reality == Promise. `security.yml` (pip-audit / bandit / CycloneDX SBOM / gitleaks) + `compliance.yml` (governance-health HARD / verify-ledger HARD / SSDF-AI-Act report) added; both YAML-valid; local gate parity clean. Hard gates: secrets + governance-health + ledger. Report-only (follow-up to harden): pip-audit / bandit / SBOM / SSDF report. SOC 2 scoped as evidence-emission (SBOM + ai_provenance), not a pass/fail gate. Committed + pushed to PR #13.

---
*Chain integrity: VALID*
*CI gates added. Open follow-ups: harden report-only gates to blocking; protocol reconcile; sidecar cleanup; LangGraph ToolNode → AGT.*

---

### Entry #29: HOTFIX — green PR #13 CI (format / mypy / gitleaks)

**Timestamp**: 2026-06-09T12:40:00Z
**Phase**: HOTFIX (routine — formatting/lint/CI per auto-dev escalation)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L1

**Content Hash**:
SHA256(pyproject.toml + __init__.py + security.yml) = 8222f1eeadef05ab7846314dd1fcc9422c3a2c1709f917e6076d27a82ef1538e

**Previous Hash**: ae6d1941a422d26d563a23a1e5e54e860797b580d523a764cf6569cc6b5aa0ba

**Chain Hash**:
SHA256(content_hash + previous_hash) = 59cfe7424c8faaedbe3673a54ef734bc9aaabca314b33c19d7d51ec2c7970032

**Decision**: First CI run on PR #13 — `governance` PASS, `scan` PASS; `test` + `secrets` FAILED. Root causes + fixes: (1) `ci.yml` runs `ruff format --check` + `mypy` (which I had not run locally) — ran `ruff format` on 7 files; added mypy override for `agent_control_plane.*` (no py.typed) + `# type: ignore[arg-type]` on the AgtDecisionClient drop-in. (2) `gitleaks-action@v2` requires a paid license for org repos — replaced with the gitleaks **binary** (Apache-2.0), `--no-git` working-tree scan. Local parity now green: ruff format-check + lint + mypy (0 issues) + pytest 79/2. Re-pushed to PR #13.

---
*Chain integrity: VALID*
*Tracking PR #13 CI to green (re-run after this push).*

> **PR #13 CI green** (run 2, commit c92f4bb): test (3.11/3.12/3.13), scan, secrets, governance all pass.

---

### Entry #30: GATE TRIBUNAL — Phase 12 (ToolNode arg-safety + PR#13 doc fixes)

**Timestamp**: 2026-06-09T13:02:00Z
**Phase**: GATE
**Author**: Judge (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase12.md) = 0b460662f9a504ae40bb86883089b1f300509feb372b89be870c7cf94353a919

**Previous Hash**: 8222f1eeadef05ab7846314dd1fcc9422c3a2c1709f917e6076d27a82ef1538e

**Chain Hash**:
SHA256(content_hash + previous_hash) = b4ea13c4a730550c3ca380cfe79e545c29383cbdbddcc7c5a28ad83a5b26d663

**Decision**: Plan to close P1 (ToolNode arg-safety bypass — thread `tool_input` to AGT, parity with BaseTool) + P2a/P2b doc fixes cleared all binding passes. Security-coverage improvement; fail-closed preserved. Cleared for /qor-implement. (P2c roadmap on PR #11 = separate branch, out of scope.)

---

### Entry #31: SEAL — Phase 12 (ToolNode arg-safety + PR#13 doc fixes)

**Timestamp**: 2026-06-09T13:10:00Z
**Phase**: SEAL (substantiate, local — commit+push to PR #13)
**Author**: Specialist (auto-dev orchestration)
**Risk Grade**: L3
**Verdict**: SEALED

**Content Hash**:
SHA256(langgraph_patches.py + test_agt_toolnode_arg_safety.py + pkg README.md) = 8af7f37c505a6efe86aff46cf6cc48faf08aef40d275657768ee9b5fabdd7cb2

**Previous Hash**: 0b460662f9a504ae40bb86883089b1f300509feb372b89be870c7cf94353a919

**Chain Hash**:
SHA256(content_hash + previous_hash) = 72f74bbce21d122ccd7504e547cc1b0eb9960764e30392a31fcc49af9c99820c

**Decision**: Reality == Promise. **P1 closed:** `_extract_tool_calls` now returns (name, args) and `_decide_each` threads args as `tool_input` → AGT runs SQL/code/path checks on the ToolNode path (parity with BaseTool); 4 new conformance tests (incl. allow-listed `database_query` + `DROP` → `QortaraPolicyDenied`). **P2a/P2b closed:** README data-handling corrected (sidecar sends normalized ActionRequest, not raw args; arg checks are in-process AGT only); Python compat 3.10 removed in 3 spots (table + "Requires" line + compat). Full suite **83 passed / 2 skipped**; ruff format-check + lint + mypy(0) clean. **P2c (PR #11 roadmap)** = separate branch, flagged to operator. Committed + pushed to PR #13.

---
*Chain integrity: VALID*
*PR #13 review findings P1/P2a/P2b resolved. Open: P2c roadmap update on PR #11 (operator-sequenced); harden report-only CI gates.*

> **Deep-audit red team (4 parallel subagents):** brief at `docs/research-brief-deep-audit-redteam-2026-06-09.md`; ~6 confirmed CRITICAL, 1 CRITICAL refuted. CRITICAL set remediated in Phase 13 below.

---

### Entry #32: GATE TRIBUNAL — Phase 13 (red-team CRITICAL remediation)

**Timestamp**: 2026-06-09T14:02:00Z
**Phase**: GATE
**Author**: Judge (deep-audit bundle)
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(AUDIT_REPORT-phase13.md) = 095086c61b6735ae408c93f4374c05293668fa8a0ab8db9cc854f785da2b9002

**Previous Hash**: 8af7f37c505a6efe86aff46cf6cc48faf08aef40d275657768ee9b5fabdd7cb2

**Chain Hash**:
SHA256(content_hash + previous_hash) = 61d657ec1eb2eb65ced68dd43bd9a444e46af581c8f16865c68de6f8e733302d

**Decision**: Plan to close GAP-SEC-02/03/04/05/06 (non-allow verdicts fail-closed; malformed-2xx deny; engine-exception deny; ToolNode.ainvoke patched; arg-safety honest + opt-in capability_aliases) cleared all binding passes. Fail-closed-ward; AGT internals untouched. Cleared for /qor-implement.

---

### Entry #33: SEAL — Phase 13 (red-team CRITICAL remediation)

**Timestamp**: 2026-06-09T14:20:00Z
**Phase**: SEAL (substantiate, local — commit+push to PR #13)
**Author**: Specialist (deep-audit remediate bundle)
**Risk Grade**: L3
**Verdict**: SEALED

**Content Hash**:
SHA256(tool_patches + langgraph_patches + client + agt_engine + __init__) = f6b5219b10dbeeb6161d6ef59c7ee38881128fe5424c7b41277998af6f7f3ca3

**Previous Hash**: 095086c61b6735ae408c93f4374c05293668fa8a0ab8db9cc854f785da2b9002

**Chain Hash**:
SHA256(content_hash + previous_hash) = 3fa335eb22aa411f1dc6a3cb25894a2a73f31c9eef4eb7cfcc7b8fd55640a17c

**Decision**: Reality == Promise. Confirmed CRITICAL set RESOLVED: **SEC-02** shared `enforce_decision` permits only ALLOW/EXEMPT/OBSERVE (DOWNGRADE/REDACT/SANDBOX/unknown → deny-closed), used by both BaseTool + ToolNode paths; **SEC-03** `client.decide` catches `ValidationError`/`ValueError` → deny + breaker; **SEC-04** `AgtDecisionClient.decide` try/except → fail-closed DENY; **SEC-06** `ToolNode.ainvoke` patched + restored; **SEC-05** honest docstring + opt-in `capability_aliases` (+ `init_agt` passthrough) + boundary test. 18 adversarial tests; full suite **97 passed / 2 skipped**; ruff format-check + lint + mypy(0) clean. Brief GAP-SEC-02/03/04/05/06 marked RESOLVED. Deferred items (GAP-CAP-01, SEC-01/07/08, CFG-01, CI-01/02, DOC-01, MED/LOW) tracked in the brief.

---

### Entry #34: GATE TRIBUNAL — Phase 14 (SEC-01 + CFG-01 plan)

**Timestamp**: 2026-06-09T15:05:00Z
**Phase**: GATE (plan + audit)
**Author**: Judge (auto-dev-1)
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(plan-qor-phase14-sec01-cfg01-honest-config.md) = a51e344f75a6616207fe5f1ca1ccd443cf61f3500c5a1b8187be390cc3f7c05d

**Previous Hash**: f6b5219b10dbeeb6161d6ef59c7ee38881128fe5424c7b41277998af6f7f3ca3

**Chain Hash**:
SHA256(content_hash + previous_hash) = 86ea6fd112db3609bbba7d2bad984be3d42e9372605265aadd952690ace60126

**Decision**: Plan to close deferred HIGH GAP-SEC-01 (ungoverned-dispatch warning, escalatable to fail-closed) + GAP-CFG-01 (implement OBSERVE shadow mode for real; remove dead `offline_policy_path`) cleared all binding passes. Security pass: OBSERVE is an explicit default-off named mode that logs every would-be block — not silent error fail-open; ENFORCE byte-unchanged; SEC-02/03/04 fail-closed paths intact upstream. Razor: no new module/dep/config (reuses `PolicyMode` + stdlib `warnings`). `require_compatible_protocol` init-wiring held out of scope (health endpoint exposes no peer version). Cleared for /qor-implement.

---

### Entry #35: SEAL — Phase 14 (SEC-01 ungoverned-dispatch signal + CFG-01 honest config)

**Timestamp**: 2026-06-09T15:20:00Z
**Phase**: SEAL (substantiate, local — commit+push to PR #13)
**Author**: Judge (auto-dev-1)
**Risk Grade**: L3
**Verdict**: SEALED

**Content Hash**:
SHA256(tool_patches + langgraph_patches + registry + config + __init__ + exceptions) = bdda8f368309d4444b0e03b3d49c16fed27af1cd03ec0403779adea3339e96fe

**Previous Hash**: a51e344f75a6616207fe5f1ca1ccd443cf61f3500c5a1b8187be390cc3f7c05d

**Chain Hash**:
SHA256(content_hash + previous_hash) = 9d31e6ad33825aff00a87aa0d0fa49a8a1be484d4f626cc5ec2097a85cc55954

**Decision**: Reality == Promise. **GAP-SEC-01 RESOLVED** — `warn_missing_context()` emits `QortaraUngovernedDispatchWarning` on no-context dispatch on both BaseTool and ToolNode paths (shared helper, can't diverge); exempt tools don't warn; escalating the category to an error via the stdlib `warnings` filter makes ungoverned dispatch fail closed. **GAP-CFG-01 RESOLVED** — `policy_mode=observe` is now a real shadow/dry-run mode (evaluate + log would-be block at WARNING, never raise), threaded `init`/`init_agt`→`apply_patches(observe=)`→adapters→`enforce_decision(observe=)`; `init_agt` gained `policy_mode=`; dead `offline_policy_path`/`QORTARA_OFFLINE_POLICY` removed (air-gapped path is `init_agt`, ADR-0001); README config table corrected (was advertising both unimplemented features). 13 new behavioral/adversarial tests (observe-never-raises-but-logs, enforce-still-raises regression, no-context-warns, filter→error fail-closed, exempt-no-warn, init_agt observe). Full suite **110 passed / 2 skipped**; ruff format-check + lint + mypy(0) clean. Brief GAP-SEC-01/CFG-01 marked RESOLVED.

---

### Entry #36: GATE TRIBUNAL — Phase 15 (SEC-08 + CAP-01 plan)

**Timestamp**: 2026-06-09T16:10:00Z
**Phase**: GATE (plan + audit)
**Author**: Judge (auto-dev-1)
**Risk Grade**: L3
**Verdict**: PASS

**Content Hash**:
SHA256(plan-qor-phase15-sec08-cap01-chokepoint-approval.md) = a901c288ac38ae72ef3a8aebac6729b267ad51f15be27019d222bb800526cdbe

**Previous Hash**: bdda8f368309d4444b0e03b3d49c16fed27af1cd03ec0403779adea3339e96fe

**Chain Hash**:
SHA256(content_hash + previous_hash) = 50dfd0759096ad0aa1b834215da38d84dae256440500faa9156fbc65d4c9724c

**Decision**: Plan to close deferred HIGH GAP-SEC-08 (relocate the enforcement chokepoint from `invoke`/`ainvoke` to the `run`/`arun` funnel that both call — verified against langchain_core 1.4.2; `BaseTool` has no `__call__`) + GAP-CAP-01 (honest decision-model docs: AGT in-process is binary allow/deny; `require_approval`/transform kinds are sidecar/hosted plane) cleared all binding passes. Security: `run`/`arun` is a strict superset funnel → strictly more coverage, one decision per dispatch (no double-enforcement); `_run`/`_arun` private impls documented as the cooperative-process boundary (THREAT-MODEL §5). Razor: deeper hook, no new surface; CAP-01 docs+tests only (no speculative AGT extension, ADR-0001). Cleared for /qor-implement.

---

### Entry #37: SEAL — Phase 15 (SEC-08 run/arun chokepoint + CAP-01 honest decision model)

**Timestamp**: 2026-06-09T16:25:00Z
**Phase**: SEAL (substantiate, local — commit+push to PR #13)
**Author**: Judge (auto-dev-1)
**Risk Grade**: L3
**Verdict**: SEALED

**Content Hash**:
SHA256(tool_patches.py) = b3d0b661f85bd9e7c6495bb7afba551f1d2cae0548ff77db831379c1ccfd87d2

**Previous Hash**: a901c288ac38ae72ef3a8aebac6729b267ad51f15be27019d222bb800526cdbe

**Chain Hash**:
SHA256(content_hash + previous_hash) = 2919d2606fd8a1b32f50fd3f7d5f9e97a165a4bbd0c5581825cbb8869222c9e4

**Decision**: Reality == Promise. **GAP-SEC-08 RESOLVED** — `tool_patches` now patches `BaseTool.run`/`.arun` (the funnel `invoke`/`ainvoke` call) with signature-agnostic pass-through wrappers; a direct `tool.run(...)`/`tool.arun(...)` is now governed (was the bypass), `invoke`/`ainvoke` still governed *through* run (one decision, no double-enforcement); double-install guard + byte-identical unpatch track run/arun. `_run`/`_arun` documented as the cooperative-process boundary (THREAT-MODEL §5, README). **GAP-CAP-01 RESOLVED (docs+boundary)** — README decision model now states the in-process AGT engine is binary allow/deny while `require_approval`/`downgrade`/`redact`/`sandbox` are sidecar/hosted-plane kinds the SDK routes (require_approval→QortaraApprovalRequired; unimplemented transform kinds→deny-closed); diagram corrected (`run()`, in-process/sidecar). 6 new conformance tests (direct run/arun governed, invoke-still-governed regression, run/arun-wrapped + invoke-untouched, AGT-binary boundary, sidecar require_approval→approval); 3 patch-internals tests re-pointed invoke→run. Full suite **116 passed / 2 skipped**; ruff format-check + lint + mypy(0) clean. Brief GAP-SEC-08/CAP-01 marked RESOLVED.

---
*Chain integrity: VALID*
*Red-team CRITICAL set + deferred HIGH SEC-01/CFG-01/SEC-08/CAP-01 closed. Remaining deferred: SEC-07 (unpatch/exempt hardening), CI-01/02 (CI gate hardening), DOC-01(rest), require_compatible_protocol wiring, MED/LOW.*
