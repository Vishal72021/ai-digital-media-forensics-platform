# W4-S0C Architecture Review

**Project:** Sentinel AI — AI Digital Media Forensics Platform

**Wave:** 4

**Stage:** W4-S0C

**Focus:** Authentication & Authorization Architecture

**Status:** Approved / Architecture Frozen

**Review Date:** 2026-07-26

**Target Release:** v0.4.0

**Prerequisite:** W4-S0B Authentication & Authorization Requirements — Complete / Frozen

---

# Executive Summary

W4-S0C establishes and freezes the authentication and authorization architecture for Sentinel AI Wave 4.

The stage translates the frozen W4-S0B security requirements from statements of required behavior into explicit architectural decisions governing identity, credentials, sessions, authentication transport, authorization, persistence, security APIs, recovery, abuse protection, observability, and verification.

The architecture was decomposed into twelve ordered packages. Packages 1 through 10 define the security architecture and its verification model, Package 11 consolidates the permanent Architecture Decision Record baseline, and Package 12 performs the final cross-package architecture freeze.

W4-S0C is approved for closure.

This approval means the architecture is sufficiently defined for implementation planning. It does **not** mean Wave 4 implementation or the v0.4.0 release is complete.

---

# Review Scope

This review evaluates whether W4-S0C has:

- Translated the frozen W4-S0B requirements into implementable architecture.
- Established coherent security-domain boundaries.
- Resolved credential and password architecture.
- Resolved access-token and refresh-session architecture.
- Resolved browser authentication transport.
- Established centralized authorization policy.
- Defined persistence and migration boundaries.
- Defined authentication API boundaries.
- Defined recovery and credential-lifecycle behavior.
- Defined abuse protection and security observability.
- Defined security verification and release gates.
- Consolidated permanent ADRs.
- Established architecture change-control expectations.
- Reached a state suitable for implementation decomposition.

---

# Architecture Packages Reviewed

## Package 1 — Security Domain & Principal Architecture

**Status:** Frozen

Established the security-domain model and authenticated principal architecture.

Key outcomes include:

- Explicit separation between application user identity and security state.
- A first-class authenticated principal abstraction.
- Clear ownership of security concerns.
- Dependency direction that prevents transport or persistence concerns from becoming the security-domain model.

---

## Package 2 — Credential & Password Architecture

**Status:** Frozen

Established credential isolation and password-security boundaries.

Key outcomes include:

- Passwords are handled through dedicated credential/security boundaries.
- Plaintext passwords are never persisted.
- Password verification is centralized.
- Password policy is canonical across credential-establishment workflows.
- Credential internals are excluded from public application contracts.

---

## Package 3 — Session & Token Architecture

**Status:** Frozen

Established the access-token and stateful refresh-session model.

Key outcomes include:

- Short-lived access credentials.
- Stateful refresh authority.
- Refresh rotation.
- Replay detection.
- Durable revocation.
- Session lifecycle semantics.
- Separation between access-token validation and refresh-session authority.

---

## Package 4 — Authentication Transport Architecture

**Status:** Frozen

Established browser authentication transport.

Key outcomes include:

- Bearer transport for access credentials.
- Secure HttpOnly cookie transport for refresh credentials.
- CSRF protection for applicable cookie-authenticated state-changing operations.
- Explicit CORS boundaries.
- Secure cookie semantics.
- Separation between access-token and refresh-token transport.

---

## Package 5 — Authorization & Policy Architecture

**Status:** Frozen

Established centralized authorization architecture.

Key outcomes include:

- Roles and permissions as explicit authorization concepts.
- Effective permission composition.
- Ownership predicates.
- Self versus privileged authority.
- Default-deny behavior.
- Centralized policy enforcement rather than scattered role comparisons.

---

## Package 6 — Persistence & Migration Architecture

**Status:** Frozen

Established the security persistence model and migration boundaries.

Key outcomes include:

- Explicit persistence for security state where durable authority is required.
- Credential, session, authorization, recovery, verification, and security-state boundaries.
- Forward migration from the released Wave 3 persistence state.
- Preservation of existing users.
- No fabricated email-verification evidence for pre-Wave-4 users.
- Historical released migrations remain immutable.

---

## Package 7 — Authentication API Architecture

**Status:** Frozen

Established the public authentication API boundary.

The architecture covers applicable workflows including:

- Registration.
- Login.
- Request authentication.
- Refresh.
- Logout.
- Session management.
- Security-sensitive account operations.

The API architecture preserves separation between public transport schemas and security-internal persistence state.

---

## Package 8 — Recovery & Credential-Lifecycle Architecture

**Status:** Frozen

Established security-sensitive credential lifecycle workflows.

Key outcomes include:

- Authenticated password change.
- Password recovery.
- Password reset.
- Email verification.
- Single-use capability semantics.
- Concurrency-safe capability consumption.
- Credential replacement consequences.
- Required session invalidation.
- Enumeration-resistant public behavior.

---

## Package 9 — Abuse Protection & Security Observability Architecture

**Status:** Frozen

Established defensive controls around public security workflows.

Key outcomes include:

- Layered throttling.
- Privacy-preserving abuse-control identity keys.
- Separate request and delivery controls.
- Enumeration-safe throttling.
- Security event generation.
- Durable append-oriented audit.
- Transactional consistency where security-state transitions require audit.
- Centralized secret redaction.
- Safe security metrics.
- Trusted-proxy boundaries.
- Explicit degraded-mode handling.

---

## Package 10 — Security Verification & Testing Architecture

**Status:** Frozen

Established the automated verification contract for Wave 4 security.

Key outcomes include:

- Layered unit, persistence, integration, API, and adversarial verification.
- PostgreSQL-backed verification for PostgreSQL-sensitive invariants.
- Refresh and recovery concurrency testing.
- Authorization matrix testing.
- CSRF, CORS, and cookie verification.
- Secret-leak regression testing.
- Abuse-control and fault-injection verification.
- Migration verification from the released Wave 3 schema.
- OpenAPI security-contract regression testing.
- Dependency vulnerability analysis.
- Repository secret detection.
- Mandatory `SEC-01` through `SEC-32` release verification matrix.
- Mandatory security-gate failure blocks v0.4.0 release approval.

---

## Package 11 — Architecture Consolidation & ADR Set

**Status:** Frozen

Consolidated the permanent Wave 4 architecture decisions into the ADR baseline.

The accepted Wave 4 ADR set is:

| ADR | Decision |
|---|---|
| ADR-0004 | Authentication & Security Architecture |
| ADR-0005 | Credential Storage & Password Security |
| ADR-0006 | Access Token & Stateful Refresh Session Architecture |
| ADR-0007 | Authorization Model — Roles & Permissions |
| ADR-0008 | Browser Authentication Transport |
| ADR-0009 | Recovery & Verification Capability Architecture |
| ADR-0010 | Abuse Protection & Security Observability |
| ADR-0011 | Security Verification & Release Gates |

No ADR-0012 is required for W4-S0C.

---

## Package 12 — Final Architecture Freeze

**Status:** Frozen

Package 12 establishes the final W4-S0C architecture freeze.

The freeze means:

```text
Frozen W4-S0B Requirements
          |
          v
Frozen W4-S0C Architecture
          |
          v
Accepted ADR Baseline
          |
          v
Implementation Planning
```

Implementation may refine mechanics that were intentionally left open, but it may not silently weaken or contradict frozen security invariants.

Material conflicts require formal architecture review.

---

# Cross-Package Architecture Review

The W4-S0C packages form a coherent dependency sequence:

```text
Security Domain & Principal
            |
            v
Credential & Password
            |
            v
Session & Token
            |
            v
Authentication Transport
            |
            v
Authorization & Policy
            |
            v
Persistence & Migration
            |
            v
Authentication API
            |
            v
Recovery & Credential Lifecycle
            |
            v
Abuse Protection & Observability
            |
            v
Security Verification
            |
            v
ADR Consolidation
            |
            v
Architecture Freeze
```

This ordering prevents persistence tables, endpoints, or framework mechanics from defining security architecture prematurely.

The architecture proceeds from domain and security guarantees toward persistence, workflows, defensive controls, and verification.

---

# Requirements Traceability

W4-S0C remains subordinate to the frozen W4-S0B requirements.

The governing traceability model is:

```text
W4-S0B Security Requirement
            |
            v
W4-S0C Architecture Decision
            |
            v
ADR
            |
            v
W4-S0D Implementation Package
            |
            v
Implementation
            |
            v
Automated Verification
```

Implementation planning must preserve this chain.

Where a proposed implementation cannot satisfy a frozen requirement or architecture decision, the conflict must be surfaced explicitly rather than resolved through undocumented deviation.

---

# Security Boundary Review

The architecture establishes explicit boundaries for:

- Identity.
- Authenticated principals.
- Credentials.
- Password verification.
- Access credentials.
- Refresh authority.
- Session state.
- Authorization state.
- Browser transport.
- Recovery capabilities.
- Verification capabilities.
- Abuse-control state.
- Security events.
- Durable audit.
- Security verification.

These concerns are no longer treated as incidental endpoint behavior.

They form a dedicated security architecture for the platform.

---

# Persistence Review

The architecture does not introduce persistence objects merely because they appear useful.

Durable state is justified by required security semantics.

The persistence architecture must preserve the released Wave 3 user state while adding only the security state required by the frozen Wave 4 design.

Released historical migrations remain immutable.

Wave 4 migrations must be validated as upgrades from the released v0.3.0 schema rather than only against freshly created current models.

---

# Verification Review

Security verification is part of the architecture rather than post-implementation cleanup.

ADR-0011 establishes a mandatory `SEC-01` through `SEC-32` security verification matrix.

The matrix includes coverage of:

- Password security.
- Registration privilege isolation.
- JWT validation.
- Authentication.
- Authorization.
- Refresh rotation and replay.
- Concurrency.
- Session revocation.
- Password lifecycle.
- Recovery and verification.
- Enumeration resistance.
- CSRF.
- CORS.
- Cookie security.
- Error contracts.
- Secret leakage.
- Rate limiting and delivery throttling.
- Abuse-store degradation.
- Security events.
- Durable audit.
- Migration integrity.
- OpenAPI security contracts.
- Dependency vulnerabilities.
- Repository secrets.

Failure of a mandatory security gate blocks v0.4.0 release approval.

---

# Architecture Decision Record Review

The permanent Wave 4 ADR baseline consists of ADR-0004 through ADR-0011.

All eight ADRs are accepted.

The ADR index is updated to reflect the repository's actual ADR history and the Wave 4 security architecture baseline.

Together, these ADRs provide the durable record for implementation and future architecture review.

---

# Open Implementation Decisions

W4-S0C intentionally leaves implementation mechanics open where freezing them would not improve architectural correctness.

Examples may include:

- Exact module and class names.
- Exact test directory structure.
- Exact fixture names.
- Exact PostgreSQL test-isolation mechanism.
- Exact CI job names.
- Exact vulnerability scanner.
- Exact secret scanner.
- Exact rate-limit storage implementation details within the frozen semantics.
- Exact security-event schema mechanics within the frozen observability contract.
- Exact helper abstractions used for deterministic test time.

These decisions belong to W4-S0D or implementation work.

They may not weaken the frozen architecture.

---

# Architecture Change Control

W4-S0C closure activates architecture change control for Wave 4 implementation.

The governing rule is:

```text
Implementation discovery
        |
        v
Does it preserve frozen architecture?
        |
   +----+----+
   |         |
  YES        NO
   |         |
   v         v
Implement   Architecture Review
```

A code change, migration, test shortcut, framework constraint, or tooling choice is not sufficient justification for silently violating an accepted ADR.

If implementation evidence demonstrates that a frozen decision must change, the architecture must be reviewed formally and the relevant ADR lifecycle followed.

---

# Closure Assessment

W4-S0C satisfies its closure criteria.

## Requirements Architecture

**PASS**

The architecture is derived from the frozen W4-S0B security requirements.

## Domain Architecture

**PASS**

Identity, principals, credentials, sessions, authorization, recovery, abuse protection, and verification have explicit boundaries.

## Architecture Package Completion

**PASS**

Packages 1 through 12 are complete and frozen.

## ADR Baseline

**PASS**

ADR-0004 through ADR-0011 are accepted as the permanent Wave 4 security ADR baseline.

## Cross-Package Consistency

**PASS**

The architecture packages form a coherent dependency sequence without requiring implementation to redefine security policy.

## Persistence Safety

**PASS**

Wave 4 architecture preserves the released Wave 3 persistence baseline and requires migration-based evolution.

## Verification Architecture

**PASS**

Mandatory security verification is defined and release-blocking.

## Implementation Readiness

**PASS**

The architecture is sufficiently defined to proceed to implementation planning and decomposition.

---

# Final Decision

**W4-S0C — Authentication & Authorization Architecture is APPROVED and FROZEN.**

The project may proceed to:

```text
W4-S0D — Implementation Planning & Decomposition
```

Wave 4 implementation has not yet started, and v0.4.0 remains unreleased.

Future implementation must conform to:

- Frozen W4-S0B requirements.
- Frozen W4-S0C architecture.
- ADR-0004 through ADR-0011.
- Mandatory security verification requirements.

Any material architectural deviation requires formal review.

---

# Next Stage

The next engineering stage is W4-S0D.

W4-S0D will convert the frozen architecture into implementation-ready packages with explicit:

- Dependency order.
- Migration order.
- Code boundaries.
- Test boundaries.
- Security-verification mapping.
- Integration gates.
- Review boundaries.
- Commit boundaries.

W4-S0D is an implementation-planning activity, not an opportunity to silently redesign W4-S0C.

---

# Conclusion

W4-S0C completes Sentinel AI's Wave 4 security architecture phase.

The platform now has a frozen architectural contract governing authentication, credentials, sessions, authorization, browser transport, recovery, persistence, abuse protection, security observability, and verification.

The architecture is approved for implementation planning.

**W4-S0C Status: COMPLETE / FROZEN**
