# Qortara Governance Beta Launch Architectural Roadmap

**Status:** Proposed execution plan  
**Target milestone:** Public Beta  
**Repository:** `MythologIQ-Labs-LLC/qortara-governance`  
**Primary package:** `qortara-governance-langchain`  
**Current maturity:** Alpha  
**Document owner:** Qortara Governance maintainers  
**Last updated:** 2026-06-09

## 1. Purpose

This roadmap defines the architecture, engineering work, release gates, and operational expectations required to move `qortara-governance` from an alpha-stage LangChain/LangGraph enforcement SDK into a credible public Beta.

The Beta must not be treated as a cosmetic version change. It must represent a material transition from a promising enforcement prototype into a package that developers can install, run, evaluate, troubleshoot, and operate in controlled production-like environments with explicit limitations.

The repository currently provides a framework adapter that intercepts LangChain and LangGraph tool dispatch and routes each tool call through a policy decision point. That core mechanism is valuable, but the current package remains incomplete as a self-contained product because:

- the default initialization path requires a `qortara-governance-sidecar` executable that is not delivered by this repository;
- the public API is still marked Alpha and may change;
- the package does not yet demonstrate full end-to-end fidelity against a released sidecar;
- compatibility is declared broadly rather than proven through a maintained version matrix;
- deployment, observability, support, upgrade, rollback, and incident behavior are not yet defined to Beta quality;
- hosted Qortara Cloud functionality is referenced but remains outside this repository's executable boundary;
- only the LangChain/LangGraph adapter exists today;
- release metadata contains at least one package/runtime version mismatch.

The Beta launch will focus on one narrow promise:

> Qortara Governance provides a reliable, fail-closed, inspectable policy enforcement point for LangChain and LangGraph tool dispatch, with a complete local runtime path and a stable integration contract.

Everything not required to make that promise true is secondary.

## 2. Beta product definition

### 2.1 What the Beta is

The Beta is:

- an installable Python SDK for LangChain and LangGraph;
- a distributable local policy sidecar or equivalent embedded runtime;
- a synchronous enforcement point on the native tool-dispatch path;
- a deterministic decision client supporting `allow`, `deny`, `require_approval`, and `exempt`;
- a fail-closed runtime when policy evaluation becomes unavailable;
- a local-only deployment option using policy packs;
- a documented hosted integration option when Qortara Cloud is configured;
- an evidence-producing enforcement layer with stable event and decision contracts;
- a package with verified compatibility against an explicit LangChain/LangGraph matrix;
- a release with end-to-end tests, upgrade guidance, rollback guidance, and known limitations.

### 2.2 What the Beta is not

The Beta is not:

- a complete enterprise governance platform;
- a replacement for AGT or other runtime governance systems;
- a general-purpose policy authoring UI;
- a full multi-tenant evidence ledger;
- a compliance reporting suite;
- a cross-organization identity federation product;
- a production SLA commitment;
- proof that every possible LangChain execution path is governed;
- support for CrewAI, LlamaIndex, AutoGen, or every future framework;
- a guarantee of compatibility with untested dependency versions;
- a guarantee that monkey-patching or runtime interception can never be bypassed by hostile in-process code.

The Beta must state these boundaries plainly. Product credibility improves when the repository does not pretend to be five products wearing one trench coat.

## 3. Architectural target state

The Beta architecture should consist of five explicit layers.

```text
Application / Agent Runtime
        |
        v
Qortara Framework Adapter
  - LangChain BaseTool interception
  - LangGraph ToolNode interception
  - context propagation
  - exemption handling
        |
        v
Qortara Decision Client
  - request normalization
  - timeout handling
  - circuit breaker
  - retry policy
  - response validation
  - trace propagation
        |
        v
Qortara Local Sidecar
  - policy loading
  - policy evaluation
  - decision generation
  - evidence creation
  - signing
  - health/readiness
  - optional hosted sync
        |
        +--------------------------+
        |                          |
        v                          v
Local Policy Pack            Qortara Cloud
  - offline rules              - policy distribution
  - local operation            - tenant identity
  - air-gapped support         - centralized evidence
                               - approvals
                               - retention
```

### 3.1 Layer ownership

#### Framework adapter

Owns:

- interception of supported execution paths;
- conversion of tool invocation into a normalized governance request;
- propagation of agent, trace, tool, and execution context;
- enforcement of the returned decision;
- raising stable SDK exceptions;
- exemption semantics;
- restoration of patched behavior during controlled teardown.

Must not own:

- policy semantics;
- evidence signing;
- hosted tenancy;
- approval workflow implementation;
- long-term storage;
- framework-independent governance policy.

#### Decision client

Owns:

- sidecar connectivity;
- request and response protocol validation;
- authentication headers or tenant credentials;
- transport timeout and retry behavior;
- circuit breaker state;
- fail-closed behavior;
- protocol compatibility checks;
- stable error translation.

Must not own:

- LangChain-specific dispatch logic;
- policy evaluation;
- sidecar process lifecycle beyond launcher coordination;
- business-level approval decisions.

#### Sidecar

Owns:

- local policy-pack loading and validation;
- deterministic evaluation;
- decision artifact generation;
- evidence canonicalization and signing;
- health, readiness, and version endpoints;
- policy cache behavior;
- hosted sync when configured;
- policy freshness and expiration handling;
- local decision audit output.

Must not silently:

- allow when policy is unavailable;
- downgrade malformed policy to permissive behavior;
- ignore protocol incompatibility;
- treat missing tenant identity as trusted;
- claim durable evidence retention unless it actually provides it.

#### Qortara Cloud

Cloud functionality is optional for Beta local use. When used, it owns:

- policy distribution;
- tenant-scoped configuration;
- hosted approval URLs and workflows;
- centralized evidence collection;
- retention and audit surfaces;
- cross-organization trust or federation, if available.

The SDK and local sidecar must remain usable without Qortara Cloud when a valid local policy pack is provided.

## 4. Beta launch principles

The implementation must follow these principles.

### 4.1 Complete the narrow path before broadening framework coverage

The LangChain/LangGraph path must become complete before adding sibling packages. A second incomplete adapter would improve the logo wall while making the product less supportable.

### 4.2 A clean installation must produce a working local path

The documented quickstart must work on a clean supported environment without requiring an undocumented executable, private repository, or manually assembled sidecar.

### 4.3 Fail closed must be observable, bounded, and recoverable

A fail-closed system that only produces a mysterious exception is secure in the same sense that unplugging the server is secure. Beta must expose why evaluation failed, how long the breaker remains open, and what an operator can do next.

### 4.4 Public contracts must stabilize before feature expansion

The following must be versioned and treated as Beta contracts:

- configuration fields;
- initialization behavior;
- decision request schema;
- decision response schema;
- exception classes;
- sidecar health and version endpoints;
- evidence event schema;
- exemption behavior;
- compatibility policy.

### 4.5 Claims must be test-backed

Any claim such as "every native tool dispatch passes through" must be supported by a named conformance suite covering the paths included in that claim.

### 4.6 Hosted capability must degrade honestly

If hosted policy, approval, or evidence services are unavailable, the system must follow documented behavior. It must not silently substitute local allow behavior unless the active policy explicitly authorizes such fallback.

## 5. Workstream A: Sidecar delivery and runtime completion

This is the highest-priority workstream because the current default SDK path depends on the sidecar executable.

### 5.1 Select the Beta delivery model

The maintainers must select and document one of these models:

#### Option A: Separate sidecar package

Publish a separately versioned package or binary distribution, such as:

- `qortara-governance-sidecar` on PyPI with an installed console script;
- platform-specific binaries attached to GitHub releases;
- a container image for daemon deployment.

Advantages:

- independent sidecar lifecycle;
- language-neutral future clients;
- clear process boundary;
- easier daemon and container operation.

Risks:

- multi-artifact compatibility burden;
- platform packaging complexity;
- two-package installation can fail partially;
- version skew must be managed explicitly.

#### Option B: Sidecar bundled with the Python package

Bundle the sidecar runtime inside `qortara-governance-langchain` or a shared Python package and expose a console entry point.

Advantages:

- clean installation path;
- fewer user steps;
- simpler Beta onboarding.

Risks:

- tighter SDK/runtime coupling;
- larger wheel;
- less suitable if the sidecar is implemented in another language;
- more complex platform-specific wheel publishing.

#### Option C: Embedded evaluator for local mode, sidecar for daemon/hosted mode

Provide an in-process deterministic evaluator for local policy packs while retaining the sidecar protocol for external deployment.

Advantages:

- simplest local path;
- no subprocess requirement for offline use;
- external sidecar remains available for stronger process isolation.

Risks:

- duplicated evaluation logic unless implemented as a shared core;
- local and daemon behavior may drift;
- in-process enforcement weakens the trust boundary.

### 5.2 Recommended Beta decision

For Beta, use a **shared evaluation core with two launch modes**:

1. a packaged local sidecar executable for the default path;
2. an externally managed daemon endpoint for containers, Kubernetes, shared hosts, or controlled enterprise environments.

Avoid implementing a second independent embedded evaluator unless the evaluation core can be reused without semantic drift.

### 5.3 Sidecar minimum feature set

The Beta sidecar must provide:

- `/health/live` endpoint;
- `/health/ready` endpoint;
- `/version` endpoint;
- `/v1/decisions/evaluate` endpoint;
- policy-pack loading from a configured local path;
- policy schema validation;
- deterministic decision generation;
- explicit decision reason and policy identifier;
- decision latency measurement;
- RFC 8785 canonicalization where evidence signing requires it;
- Ed25519 signing where currently claimed;
- SHA-256 content hashes;
- local evidence output;
- trace-context propagation;
- configuration validation at startup;
- structured logging;
- graceful shutdown;
- predictable exit codes;
- startup failure on invalid required configuration;
- protocol version negotiation or compatibility rejection.

### 5.4 Sidecar packaging acceptance criteria

- `pip install qortara-governance-langchain` installs every artifact required for the default quickstart, or the quickstart explicitly installs both required packages.
- `qortara_governance.init()` succeeds on a clean supported environment.
- The spawned sidecar binds only to loopback by default.
- The launcher verifies readiness, not merely TCP acceptability.
- The sidecar reports a protocol version compatible with the SDK.
- Unsupported version combinations fail with an actionable error.
- Subprocess stdout and stderr cannot deadlock because unread pipes fill.
- Child process cleanup is tested for normal exit, exception exit, keyboard interrupt, and parent termination.
- External-daemon mode remains supported.
- Sidecar release artifacts are signed or accompanied by verifiable checksums.

### 5.5 Launcher corrections

The launcher should be revised to:

- call a readiness endpoint rather than accepting any TCP connection;
- capture and surface startup diagnostics;
- avoid blocking pipes by routing logs appropriately;
- use a process group or platform-appropriate child lifecycle strategy;
- support configurable startup timeout;
- verify executable version before patching framework dispatch;
- return structured launch metadata;
- expose whether the runtime was spawned, reused, or externally configured;
- distinguish binary-missing, startup-failed, readiness-timeout, protocol-mismatch, and authentication errors.

## 6. Workstream B: Stable SDK initialization and configuration

### 6.1 Configuration contract

Beta configuration must have a single documented precedence order. The current documentation and implementation should be reconciled so there is no ambiguity between keyword arguments, environment variables, policy files, and defaults.

Recommended precedence:

```text
explicit init() arguments
  -> environment variables
  -> configuration file
  -> documented defaults
```

Configuration should support:

- `tenant_key`;
- `sidecar_endpoint`;
- `policy_mode`;
- `offline_policy_path`;
- `request_timeout_ms`;
- `startup_timeout_ms`;
- `circuit_breaker_cooldown_ms`;
- `evidence_output_path`;
- `log_level`;
- `trace_enabled`;
- `fail_behavior`, restricted to approved values;
- `protocol_version`, when explicit pinning is required.

### 6.2 Initialization semantics

Beta must define:

- whether `init()` is process-global;
- whether multiple isolated clients are supported;
- what happens in worker processes;
- what happens after `fork()`;
- behavior in notebooks and hot-reload servers;
- idempotency behavior;
- reconfiguration behavior;
- teardown behavior;
- thread safety;
- async compatibility;
- import-order requirements.

Recommended Beta rule:

> `init()` is process-global, idempotent for an identical normalized configuration, and rejects conflicting reinitialization.

That matches the current direction and should be documented as an intentional contract.

### 6.3 Version consistency

The runtime `__version__`, package metadata, release tag, wheel metadata, changelog, and sidecar compatibility range must be generated from one source of truth.

Acceptance criteria:

- `importlib.metadata.version("qortara-governance-langchain")` equals `qortara_governance.__version__`;
- release tags match package versions;
- the sidecar reports its own semantic version and protocol version;
- CI fails on version mismatch.

## 7. Workstream C: Enforcement-path correctness

### 7.1 Supported paths

The Beta must explicitly enumerate supported dispatch paths rather than relying on generic claims.

At minimum, test and document:

- direct `BaseTool.invoke`;
- direct `BaseTool.ainvoke`;
- tools invoked through `AgentExecutor`;
- tools invoked through `create_tool_calling_agent`;
- tools invoked through native OpenAI tool-calling agents where LangChain routes through supported dispatch;
- LangGraph `ToolNode.invoke`;
- LangGraph async tool execution;
- multiple tools in one turn;
- dynamically selected tools;
- nested tool calls where supported;
- sub-agent tools where dispatch enters a supported interception point;
- exempt tools;
- errors raised by the underlying tool;
- retries performed by the framework;
- streaming paths where tool dispatch occurs.

### 7.2 Patch architecture

The patching mechanism must be:

- idempotent;
- reversible for testing and controlled shutdown;
- safe under repeated imports;
- compatible with supported framework versions;
- detectable when another library has already patched the same method;
- explicit about patch ordering;
- resistant to accidental double evaluation;
- capable of preserving original signatures and metadata where practical.

### 7.3 Bypass model

The Beta documentation must include an honest bypass model.

The adapter protects supported dispatch paths in a cooperative application process. It does not protect against:

- code that directly calls the underlying tool function outside LangChain dispatch;
- malicious code that restores or replaces patched methods;
- unsupported framework internals;
- dynamically imported framework versions outside the compatibility matrix;
- subprocesses or remote workers that do not initialize the SDK;
- alternate tool execution paths not routed through the patched interfaces.

This limitation does not invalidate the product. It defines the boundary customers must understand.

### 7.4 Conformance suite

Create a named conformance suite under a path such as:

```text
tests/conformance/
  test_basetool_sync.py
  test_basetool_async.py
  test_agent_executor.py
  test_tool_calling_agent.py
  test_langgraph_toolnode.py
  test_multi_tool.py
  test_dynamic_tools.py
  test_exemptions.py
  test_fail_closed.py
  test_approval.py
  test_trace_propagation.py
  test_bypass_expectations.py
```

Each test should state:

- the framework path under test;
- the expected number of policy evaluations;
- the expected decision behavior;
- whether the underlying tool executed;
- the emitted evidence behavior;
- the expected trace correlation;
- the supported dependency versions.

## 8. Workstream D: Decision protocol and error model

### 8.1 Decision request

The Beta request schema should include:

- protocol version;
- request ID;
- trace ID and span context;
- timestamp;
- tenant identity when hosted;
- agent identity or declared subject;
- framework and framework version;
- adapter version;
- tool name;
- normalized tool identifier;
- tool arguments or a redacted representation;
- argument classification metadata where available;
- execution scope;
- exemption status;
- policy mode;
- relevant agent context;
- retry or attempt number;
- parent decision reference when nested.

### 8.2 Decision response

The Beta response schema should include:

- decision ID;
- decision state;
- rationale;
- policy ID;
- policy version or content hash;
- approval URL when required;
- decision expiration;
- evidence reference;
- trace correlation;
- sidecar version;
- protocol version;
- redaction directives where applicable;
- transformation output only if transform behavior is intentionally supported.

### 8.3 Stable exceptions

The public exception hierarchy should include:

```text
QortaraError
  QortaraPolicyDenied
  QortaraApprovalRequired
  QortaraSidecarUnavailable
  QortaraProtocolMismatch
  QortaraConfigurationError
  QortaraPolicyInvalid
  QortaraDecisionMalformed
  QortaraAuthenticationError
  QortaraTimeout
```

Each exception should expose structured fields and stable string behavior.

### 8.4 Timeout and retry rules

Policy decisions sit on the execution path, so retries must be conservative.

Recommended Beta defaults:

- no automatic retry for a completed deny or approval decision;
- one bounded retry only for clearly transient transport failure before any decision is received;
- idempotency key on every evaluation request;
- total timeout lower than the application's own tool timeout;
- fail closed after timeout;
- explicit circuit breaker cooldown;
- no unbounded exponential retry on the agent's critical path.

## 9. Workstream E: Local policy packs

### 9.1 Policy-pack requirements

A local policy pack must be:

- versioned;
- schema-validated;
- deterministic;
- human-readable;
- hashable;
- optionally signed;
- scoped to supported decision inputs;
- explicit about defaults;
- explicit about missing-field behavior;
- testable without running a full agent.

### 9.2 Policy schema

The Beta policy schema should define:

- pack ID and version;
- schema version;
- default decision;
- rule priority;
- tool selectors;
- identity selectors;
- argument predicates;
- environment or scope predicates;
- decision outcome;
- rationale;
- approval metadata;
- expiration;
- exemptions;
- evidence requirements.

### 9.3 Policy CLI

Provide a CLI with commands such as:

```bash
qortara-governance policy validate policy.yaml
qortara-governance policy test policy.yaml fixtures.json
qortara-governance policy hash policy.yaml
qortara-governance policy explain policy.yaml --tool send_email --args request.json
qortara-governance sidecar run --policy policy.yaml
qortara-governance doctor
```

The `doctor` command should verify:

- Python version;
- package version;
- sidecar availability;
- sidecar compatibility;
- policy readability;
- policy validity;
- local port binding;
- hosted credentials when configured;
- connectivity to configured endpoint;
- effective configuration with secrets redacted.

## 10. Workstream F: Evidence, signing, and audit behavior

### 10.1 Evidence contract

Every evaluated dispatch should produce an evidence event unless policy explicitly disables local persistence and the documentation states the resulting limitations.

Evidence should include:

- decision ID;
- request hash;
- timestamp;
- tool identity;
- subject identity;
- decision;
- policy ID and version hash;
- sidecar version;
- adapter version;
- trace identifiers;
- approval reference where applicable;
- execution outcome when observable;
- exemption state;
- signature metadata.

### 10.2 Distinguish decision evidence from execution evidence

The Beta must not claim that a signed allow decision proves the tool executed.

Use separate event types:

```text
DecisionIssued
ToolExecutionStarted
ToolExecutionSucceeded
ToolExecutionFailed
ToolExecutionBlocked
ApprovalRequired
ApprovalResolved
```

Where the SDK cannot reliably observe an execution outcome, it must not fabricate one.

### 10.3 Signing key handling

If Ed25519 signing is included in Beta:

- key generation must be explicit;
- key storage location must be documented;
- permissions must be restricted;
- rotation behavior must be defined;
- ephemeral subprocess keys must be clearly identified as ephemeral;
- hosted keys and local keys must not be conflated;
- public verification material must be retrievable;
- evidence must identify the signing key ID;
- signature verification must have test vectors.

### 10.4 Evidence privacy

Tool arguments may contain credentials, personal data, source code, health data, financial data, or customer information.

Beta must support:

- argument omission;
- field-level redaction;
- hashing of selected values;
- maximum payload size;
- content classification hints;
- local-only evidence mode;
- documented hosted transmission behavior;
- retention controls when hosted.

Default evidence should favor minimization over convenient surveillance.

## 11. Workstream G: Security hardening

### 11.1 Threat model

Create `docs/security/THREAT-MODEL.md` covering:

- bypass of patched dispatch;
- sidecar impersonation;
- local port hijacking;
- malicious policy packs;
- stale policy reuse;
- tenant-key theft;
- argument exfiltration;
- approval URL tampering;
- decision replay;
- protocol downgrade;
- dependency compromise;
- signing-key compromise;
- evidence tampering;
- denial of service through sidecar failure;
- policy confusion between observe and enforce modes.

### 11.2 Local transport security

For subprocess mode:

- bind to `127.0.0.1` or platform-equivalent local transport only;
- use an ephemeral authentication token passed securely to the child;
- reject unauthenticated local requests;
- prefer Unix domain sockets on supported platforms where practical;
- prevent another local process from racing the selected port;
- validate the child process identity where feasible;
- avoid exposing tenant secrets in process arguments.

### 11.3 External-daemon security

For daemon mode:

- support HTTPS;
- validate certificates by default;
- support token or mTLS authentication;
- reject plaintext remote endpoints unless explicitly enabled for development;
- document proxy behavior;
- define maximum request size;
- define rate-limiting expectations;
- avoid logging secrets.

### 11.4 Supply-chain controls

Beta release CI should include:

- dependency lockfiles;
- dependency vulnerability scanning;
- secret scanning;
- static analysis;
- linting;
- type checking;
- test execution;
- build reproducibility checks where practical;
- generated SBOM;
- artifact checksums;
- provenance attestation for published artifacts;
- protected publishing via trusted publisher or OIDC.

## 12. Workstream H: Observability and operations

### 12.1 Structured logs

SDK and sidecar logs should include:

- timestamp;
- severity;
- component;
- request ID;
- decision ID;
- trace ID;
- tool identifier;
- latency;
- decision;
- error category;
- circuit-breaker state;
- policy version;
- sidecar version.

Logs must not include raw tool arguments by default.

### 12.2 Metrics

Expose or record:

- decision count by outcome;
- decision latency;
- transport failures;
- timeout count;
- circuit-breaker transitions;
- policy-load failures;
- malformed requests;
- malformed responses;
- approval-required count;
- exempt-call count;
- sidecar restart count;
- unsupported-path warnings;
- evidence-write failures.

### 12.3 Tracing

W3C trace context should propagate:

```text
agent invocation
  -> framework dispatch
  -> Qortara adapter
  -> sidecar evaluation
  -> hosted policy service, when used
  -> tool execution
```

Beta must test trace propagation rather than merely documenting it.

### 12.4 Operator diagnostics

Provide:

- `qortara-governance doctor`;
- sidecar health and readiness endpoints;
- effective configuration output with secrets redacted;
- current policy ID and hash;
- SDK/sidecar compatibility output;
- circuit-breaker status;
- recent local decision diagnostics;
- clear remediation instructions for common failures.

## 13. Workstream I: Compatibility and dependency policy

### 13.1 Supported version matrix

Replace broad unbounded compatibility claims with a tested matrix.

Example Beta matrix:

| Component | Supported Beta range | Verification |
|---|---:|---|
| Python | 3.10, 3.11, 3.12, 3.13 | CI matrix |
| `langchain-core` | selected tested minor ranges | conformance suite |
| `langchain` | selected tested minor ranges | integration suite |
| `langgraph` | selected tested minor ranges | integration suite |
| Operating systems | Linux, Windows, macOS | install and smoke tests |

Exact version ranges must be determined from current test results.

### 13.2 Dependency upper bounds

For Beta, use compatible upper bounds for dependencies whose internal dispatch APIs are patched.

For example, avoid treating `langchain-core>=0.3` as indefinitely safe. Runtime patching against internal or semi-public dispatch behavior requires active compatibility management.

### 13.3 Compatibility CI

CI should run:

- minimum supported versions;
- latest supported versions;
- pre-release or canary versions in a non-blocking job;
- all supported Python versions;
- all supported operating systems for packaging smoke tests.

### 13.4 Compatibility failure behavior

At initialization:

- detect installed framework versions;
- warn or fail for known-incompatible versions;
- emit a precise compatibility message;
- provide a documented override only for development;
- never silently claim enforcement on an unverified path.

## 14. Workstream J: Testing strategy

### 14.1 Test pyramid

#### Unit tests

Cover:

- configuration normalization;
- decision parsing;
- exception construction;
- circuit breaker;
- retry and timeout behavior;
- exemption detection;
- patch idempotency;
- protocol validation;
- policy schema validation;
- evidence canonicalization;
- signature verification.

#### Integration tests

Cover:

- SDK to real sidecar;
- local policy pack loading;
- allow, deny, approval, and exempt behavior;
- sidecar restart;
- protocol mismatch;
- malformed policy;
- unavailable sidecar;
- hosted endpoint simulation;
- evidence creation and verification.

#### Framework conformance tests

Cover every advertised LangChain and LangGraph execution path.

#### Packaging tests

On clean environments:

- install wheel from built artifact;
- import package;
- invoke `init()`;
- spawn sidecar;
- load sample policy;
- allow one tool;
- deny one tool;
- uninstall cleanly.

#### Failure-injection tests

Cover:

- sidecar crash during evaluation;
- timeout;
- malformed response;
- invalid signature;
- stale policy;
- unreadable policy file;
- port conflict;
- exhausted disk for local evidence;
- network loss in hosted mode;
- approval service unavailable;
- duplicate request replay.

### 14.2 Coverage expectations

Code coverage should be treated as a diagnostic, not a substitute for scenario fidelity.

Beta gates should require:

- high coverage on decision, configuration, circuit-breaker, and protocol modules;
- explicit conformance tests for every public enforcement claim;
- end-to-end tests using the actual released sidecar artifact;
- zero skipped tests in the required release matrix unless documented as platform-specific exclusions.

## 15. Workstream K: Release engineering

### 15.1 Versioning

Use semantic versioning.

Recommended Beta version:

```text
0.5.0b1
```

or, if the project prefers simplified pre-1.0 semantics:

```text
0.5.0
```

The repository must clearly state what Beta means. Avoid calling a release `1.0 Beta`, a phrase engineered to confuse every dependency resolver and procurement reviewer simultaneously.

### 15.2 Release artifacts

Publish:

- Python wheel;
- source distribution;
- sidecar package or binary artifacts;
- checksums;
- SBOM;
- provenance attestation;
- changelog;
- compatibility matrix;
- migration notes;
- sample policy pack;
- signed release notes where supported.

### 15.3 Automated publishing

Use trusted publishing with OIDC for PyPI. Avoid long-lived package tokens.

Release workflow should:

1. validate version consistency;
2. run required CI matrix;
3. build SDK and sidecar artifacts;
4. run clean-install smoke tests against built artifacts;
5. generate SBOM and checksums;
6. publish TestPyPI prerelease;
7. run installation tests from TestPyPI;
8. require maintainer approval;
9. publish production prerelease;
10. create GitHub release and attach artifacts;
11. verify published metadata and installation.

### 15.4 Rollback

Because PyPI artifacts cannot be replaced safely, rollback means:

- yank a broken release;
- publish a corrected patch prerelease;
- document the affected versions;
- preserve protocol compatibility where possible;
- provide a known-good pin.

The Beta docs must include rollback instructions for SDK and sidecar.

## 16. Workstream L: Documentation and developer experience

### 16.1 Required documentation

Before Beta:

```text
docs/
  BETA-LAUNCH-ARCHITECTURAL-ROADMAP.md
  architecture/
    OVERVIEW.md
    SIDECAR.md
    DECISION-PROTOCOL.md
    ENFORCEMENT-BOUNDARY.md
  security/
    THREAT-MODEL.md
    DATA-HANDLING.md
  operations/
    INSTALLATION.md
    CONFIGURATION.md
    TROUBLESHOOTING.md
    UPGRADE-AND-ROLLBACK.md
  compatibility/
    MATRIX.md
  policies/
    POLICY-PACK-SPEC.md
    EXAMPLES.md
  beta/
    KNOWN-LIMITATIONS.md
    RELEASE-CHECKLIST.md
```

### 16.2 Quickstart requirements

The Quickstart must be verified in CI exactly as written.

It should include:

1. environment creation;
2. package installation;
3. a complete sample policy;
4. initialization;
5. one allowed tool;
6. one denied tool;
7. one approval-required tool if hosted approval is available;
8. expected output;
9. cleanup;
10. troubleshooting link.

No ellipses may conceal required executable code in the canonical quickstart.

### 16.3 Example applications

Provide runnable examples:

- basic sync LangChain agent;
- async LangChain agent;
- LangGraph ToolNode;
- local offline policy pack;
- external sidecar daemon;
- hosted policy mode;
- evidence verification;
- exemption behavior;
- failure and circuit-breaker handling.

### 16.4 Known limitations

The Beta limitations document must state:

- supported framework versions;
- unsupported dispatch paths;
- cooperative in-process trust boundary;
- hosted service dependencies;
- data-handling risks;
- sidecar deployment limitations;
- absence of SLA;
- API stability expectations;
- migration expectations before 1.0.

## 17. Workstream M: Governance and support process

### 17.1 Issue templates

Add templates for:

- bug report;
- compatibility regression;
- policy behavior question;
- security report redirect;
- feature request;
- sidecar startup failure;
- bypass report.

### 17.2 Support expectations

For Beta, publish:

- supported channels;
- expected best-effort response posture;
- required diagnostic information;
- security disclosure path;
- supported release window;
- deprecation policy.

### 17.3 Deprecation policy

Recommended Beta rule:

- public APIs may still change before 1.0;
- breaking changes require release notes and migration guidance;
- deprecated APIs remain for at least one minor Beta release when practical;
- protocol compatibility is maintained across a documented adjacent range;
- emergency security changes may bypass the normal deprecation window.

## 18. Workstream N: Hosted integration boundary

The repository currently references Qortara Cloud Governance. Beta must make the hosted boundary real or reduce the claim.

### 18.1 Minimum hosted contract

If hosted mode is included in Beta, define:

- tenant-key format;
- authentication behavior;
- policy synchronization;
- cache behavior;
- policy expiration;
- offline behavior;
- approval request creation;
- approval URL semantics;
- evidence upload behavior;
- retry and failure behavior;
- tenant isolation assumptions;
- data residency and retention documentation.

### 18.2 Hosted-unavailable behavior

Document behavior for:

- no network before startup;
- network loss after startup;
- expired cached policy;
- approval service unavailable;
- evidence upload unavailable;
- invalid tenant credentials;
- revoked tenant key;
- server protocol mismatch.

### 18.3 Beta scope decision

The maintainers must choose one:

#### Beta with hosted preview

Include hosted policy and approval as clearly labeled preview features, with local enforcement remaining the stable Beta core.

#### Beta local-first only

Remove or soften hosted claims until the hosted service contract is ready.

The second option is preferable to publishing architecture fiction.

## 19. Milestone sequence

### Milestone 0: Repository truth and baseline

**Goal:** Make repository claims match executable reality.

Tasks:

- reconcile version mismatch;
- inventory source files, tests, and package artifacts;
- identify sidecar source and ownership;
- document current supported paths;
- document current known gaps;
- create the Beta project board or issue milestone;
- map all roadmap tasks to issues.

Exit criteria:

- current-state architecture documented;
- every Beta blocker represented by an issue;
- no README claim lacks an owner or test plan.

### Milestone 1: Complete local runtime

**Goal:** Clean install and local execution work.

Tasks:

- package sidecar;
- implement readiness and version endpoints;
- revise launcher;
- validate protocol compatibility;
- provide sample policy pack;
- add clean-install smoke test;
- implement `doctor` basics.

Exit criteria:

- clean environment can install, initialize, allow, deny, and shut down;
- no external undocumented artifact required;
- failure messages are actionable.

### Milestone 2: Stabilize protocol and SDK API

**Goal:** Freeze Beta contracts.

Tasks:

- version request and response schemas;
- stabilize exceptions;
- finalize configuration precedence;
- finalize timeout, retry, and circuit-breaker behavior;
- generate versions from one source;
- document API compatibility expectations.

Exit criteria:

- protocol fixtures committed;
- backward-compatibility tests exist;
- public API reviewed and documented;
- version consistency enforced by CI.

### Milestone 3: Enforcement conformance

**Goal:** Prove supported LangChain/LangGraph paths.

Tasks:

- build conformance suite;
- test sync and async paths;
- test LangGraph paths;
- test dynamic and nested patterns where claimed;
- test exemptions;
- document bypass boundary;
- add framework version matrix.

Exit criteria:

- every supported path has a passing named test;
- unsupported paths are documented;
- compatibility matrix is generated from tested jobs.

### Milestone 4: Security and evidence hardening

**Goal:** Make failure and evidence behavior trustworthy.

Tasks:

- threat model;
- local sidecar authentication;
- evidence schema;
- signature test vectors;
- redaction and minimization;
- replay protection;
- supply-chain controls;
- secret handling review;
- dependency scanning.

Exit criteria:

- threat model reviewed;
- no unauthenticated sidecar decision endpoint in default mode;
- evidence signatures verify;
- sensitive arguments are not logged by default;
- release artifacts include SBOM and checksums.

### Milestone 5: Observability and operations

**Goal:** Make the Beta diagnosable.

Tasks:

- structured logs;
- metrics;
- trace propagation tests;
- `doctor` command completion;
- troubleshooting guide;
- upgrade and rollback guide;
- sidecar lifecycle diagnostics.

Exit criteria:

- common failures can be diagnosed without reading source;
- trace correlation works across adapter and sidecar;
- operator guidance exists for every documented failure category.

### Milestone 6: Beta documentation and examples

**Goal:** Make evaluation possible without maintainer intervention.

Tasks:

- complete architecture docs;
- verify quickstart in CI;
- publish runnable examples;
- publish limitations;
- publish compatibility matrix;
- publish policy-pack specification;
- update root and package READMEs.

Exit criteria:

- a new user can complete the quickstart from a clean machine;
- every example is exercised in CI or scheduled validation;
- Beta limitations are visible before installation.

### Milestone 7: Release candidate

**Goal:** Validate the exact artifacts intended for Beta.

Tasks:

- build `beta.1` artifacts;
- publish to TestPyPI;
- test all supported platforms;
- run failure-injection suite;
- run dependency and security scans;
- conduct maintainer release review;
- test upgrade from latest Alpha;
- test rollback to known-good version;
- collect pilot feedback.

Exit criteria:

- no unresolved release-blocking defects;
- no critical or high known vulnerabilities without accepted mitigation;
- clean-install tests pass from published artifacts;
- release checklist signed off.

### Milestone 8: Public Beta

**Goal:** Publish a supportable Beta with honest boundaries.

Tasks:

- publish artifacts;
- publish release notes;
- create GitHub release;
- update status badges;
- open Beta feedback discussion;
- monitor installation and compatibility reports;
- triage regressions rapidly;
- publish known issues.

Exit criteria:

- package and sidecar install successfully;
- documentation points to Beta limitations;
- monitoring and support channels are active;
- no Alpha-only claims remain in current docs unless historically labeled.

## 20. Beta release gates

The Beta must not launch until every mandatory gate passes.

### Gate A: Installation

- clean install works on supported Python versions;
- sidecar dependency is delivered and discoverable;
- default initialization succeeds;
- uninstall and reinstall succeed.

### Gate B: Enforcement

- supported dispatch paths are conformance-tested;
- deny prevents tool execution;
- approval-required prevents tool execution;
- allow executes exactly once;
- exempt executes according to documented evidence behavior;
- sidecar unavailability fails closed.

### Gate C: Protocol

- request and response schemas are versioned;
- malformed responses fail closed;
- SDK and sidecar incompatibility is detected;
- idempotency behavior is tested.

### Gate D: Security

- local sidecar requests are authenticated;
- secrets are not logged;
- threat model exists;
- evidence signatures verify;
- dependency and secret scans pass;
- release artifacts include SBOM and checksums.

### Gate E: Compatibility

- explicit tested version matrix exists;
- minimum and maximum supported dependency jobs pass;
- unsupported versions produce warnings or failure;
- all supported operating-system smoke tests pass.

### Gate F: Operations

- health and readiness endpoints work;
- structured logs exist;
- diagnostics identify common failures;
- upgrade and rollback instructions exist;
- child process cleanup is tested.

### Gate G: Documentation

- quickstart works exactly as written;
- limitations are published;
- architecture and data flow are documented;
- sample policies are valid;
- support and security reporting paths are visible.

### Gate H: Release quality

- version metadata is consistent;
- changelog is complete;
- release candidate has been installed from published artifacts;
- no critical release blockers remain;
- maintainer sign-off is recorded.

## 21. Release blocker definitions

### Critical blocker

Any issue that:

- allows a denied tool to execute;
- silently fails open;
- leaks secrets or sensitive tool arguments by default;
- permits unauthenticated decision injection;
- corrupts or fabricates evidence;
- makes the default installation path unusable;
- causes broad incompatibility across the supported matrix.

Critical blockers prevent release.

### High blocker

Any issue that:

- causes repeated or missing policy evaluation;
- breaks a documented supported dispatch path;
- prevents reliable sidecar cleanup;
- makes protocol mismatch undetectable;
- breaks evidence verification;
- produces misleading approval behavior;
- causes common supported environments to fail installation.

High blockers prevent release unless formally accepted with narrow scope and visible documentation. For a public Beta, such exceptions should be rare.

### Medium issue

An issue that:

- affects non-default configuration;
- degrades diagnostics;
- affects a documented edge case without bypassing enforcement;
- causes incomplete observability;
- impacts optional hosted preview behavior.

Medium issues may ship if documented and scheduled.

## 22. Proposed repository changes

The Beta effort should produce or revise at least:

```text
packages/qortara-governance-langchain/
  src/qortara_governance/
    __init__.py
    client.py
    config.py
    launcher.py
    patches.py
    protocol.py
    diagnostics.py
    exceptions.py
    evidence.py
  tests/
    unit/
    integration/
    conformance/
    packaging/

packages/qortara-governance-sidecar/   # exact form depends on implementation language
  src/
  tests/
  pyproject.toml or language-equivalent build files

examples/
  basic_langchain/
  async_langchain/
  langgraph_toolnode/
  offline_policy/
  external_daemon/
  hosted_preview/

docs/
  BETA-LAUNCH-ARCHITECTURAL-ROADMAP.md
  architecture/
  security/
  operations/
  compatibility/
  policies/
  beta/

.github/workflows/
  ci.yml
  compatibility.yml
  packaging.yml
  security.yml
  release.yml
```

## 23. Issue decomposition

The roadmap should be converted into an umbrella issue with linked implementation issues.

Recommended issue set:

1. Package and publish the Qortara sidecar.
2. Replace TCP-only startup detection with readiness verification.
3. Add SDK/sidecar protocol version negotiation.
4. Unify package and runtime version sources.
5. Stabilize Beta configuration and initialization contract.
6. Define decision request and response schemas.
7. Expand stable exception hierarchy.
8. Implement bounded timeout, retry, idempotency, and circuit breaker behavior.
9. Define and validate local policy-pack schema.
10. Add policy validation and doctor CLI.
11. Build LangChain/LangGraph conformance suite.
12. Define and test the supported compatibility matrix.
13. Document and test bypass boundaries.
14. Define evidence event schema and execution-event separation.
15. Implement signing-key lifecycle and signature fixtures.
16. Add data minimization and redaction.
17. Add authenticated local sidecar transport.
18. Add external-daemon TLS and authentication requirements.
19. Write threat model.
20. Add structured logs, metrics, and tracing tests.
21. Add packaging and clean-install tests.
22. Add failure-injection suite.
23. Add SBOM, checksums, provenance, and trusted publishing.
24. Write installation, configuration, troubleshooting, upgrade, and rollback docs.
25. Add runnable examples.
26. Publish known limitations and support policy.
27. Define hosted preview contract or remove unsupported hosted claims.
28. Run Beta release candidate validation.

## 24. Prioritization

### Must have for Beta

- sidecar delivery;
- clean-install quickstart;
- stable initialization;
- version alignment;
- protocol versioning;
- allow/deny/approval/exempt correctness;
- fail-closed behavior;
- conformance suite;
- compatibility matrix;
- threat model;
- authenticated local transport;
- evidence integrity;
- redaction and data-handling documentation;
- structured diagnostics;
- release automation;
- limitations and rollback documentation.

### Should have for Beta

- hosted policy preview;
- hosted approval flow;
- metrics export;
- full `doctor` command;
- external daemon container image;
- trace correlation examples;
- policy explanation CLI.

### May follow after Beta

- CrewAI adapter;
- LlamaIndex adapter;
- AutoGen adapter;
- enterprise fleet controls;
- advanced policy authoring UI;
- regulated-industry policy packs;
- centralized capability registry;
- adaptive-state governance from the broader Qortara architecture;
- hardware-rooted verification.

The post-Beta items must not delay the narrow enforcement Beta unless they reveal a foundational defect.

## 25. Success criteria

The Beta is successful when an independent developer can:

1. install the package on a supported environment;
2. run the exact Quickstart without undocumented setup;
3. apply a local policy pack;
4. confirm that an allowed tool executes;
5. confirm that a denied tool does not execute;
6. confirm that approval-required pauses execution;
7. inspect a decision and its evidence;
8. understand what data crossed the sidecar boundary;
9. diagnose an unavailable sidecar;
10. identify supported framework versions;
11. upgrade or roll back safely;
12. understand the enforcement boundary and its limitations.

The Beta is architecturally credible when maintainers can additionally:

- reproduce all release artifacts;
- verify SDK and sidecar compatibility;
- identify policy and evidence versions for an incident;
- run the complete conformance matrix;
- distinguish a framework regression from a sidecar regression;
- publish a corrective release without manually reconstructing the process.

## 26. Explicit non-goals for the Beta milestone

To prevent scope drift, the following do not block Beta:

- multiple framework adapters;
- full Qortara Cloud feature parity;
- formal compliance certification;
- enterprise SLAs;
- a graphical policy editor;
- broad agent memory governance;
- PAMA or governed adaptive-state implementation;
- full multi-agent identity federation;
- confidential-computing integration;
- hardware attestation;
- production claims beyond the documented Beta scope.

These are valid future directions. They are also excellent ways to avoid finishing the thing directly in front of us.

## 27. Final architectural decision

The Beta launch will prioritize a complete, test-backed, local-first LangChain/LangGraph enforcement path over breadth.

The release is approved only when:

```text
install
  -> initialize
  -> intercept supported dispatch
  -> evaluate through a delivered sidecar
  -> enforce deterministically
  -> fail closed on uncertainty
  -> produce verifiable evidence
  -> expose actionable diagnostics
  -> operate within a tested compatibility matrix
```

That sequence is the Beta product.

Everything else is supporting capability, hosted extension, or future roadmap.
