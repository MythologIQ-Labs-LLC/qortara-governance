# Restricted Package Boundary

## Public repository rule

`qortara-governance` is a public enforcement and framework-adapter repository.

It must build, test, install, and operate without access to restricted internal Qortara packages or organization-private source repositories.

## Allowed dependencies

This repository may depend on:

- public PyPI packages;
- public source repositories;
- Microsoft Agent Governance Toolkit and other approved public foundations;
- documented public Qortara request, response, adapter, enforcement, and sidecar contracts;
- local test fixtures that contain no proprietary implementation or credentials.

Hosted Qortara capabilities are consumed through approved authenticated service contracts. They are not imported into this public package as private source or restricted build dependencies.

## Prohibited dependencies and credentials

This repository must not:

- install restricted organization packages in public CI;
- require GitHub Packages organization credentials;
- store a personal access token, package token, or organization-wide secret;
- infer package access from organization membership;
- import private Oversight, Compliance, billing, entitlement, risk, or orchestration implementation;
- copy proprietary hosted algorithms into public adapters;
- make local enforcement dependent on a hosted service;
- expose private repository topology through generated documentation or package metadata.

## Contract direction

The supported direction is:

```text
public agent framework
  -> qortara-governance public adapter
  -> public local enforcement contract
  -> optional authenticated hosted API contract
```

The unsupported direction is:

```text
public package build
  -> restricted internal package
  -> private implementation imported into the public artifact
```

## CI expectation

Pull-request and release workflows must succeed using only the permissions required for public repository contents and public package publication.

A workflow requesting `packages: read` for an organization-restricted package requires an explicit architecture and security review. It must not be introduced as a convenience workaround.

## Authority boundary

This public repository owns framework-specific dispatch interception and public enforcement contracts.

It does not own:

- private hosted risk algorithms;
- Qortara account, billing, or entitlement authority;
- Qortara SDLC product composition;
- private operator read models;
- private compliance evidence semantics;
- external product authority.

Bicameral and other external products remain optional third-party integration targets. They receive no package or repository access through this public project.
