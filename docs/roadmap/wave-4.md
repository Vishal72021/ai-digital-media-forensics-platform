# Wave 4 Roadmap

**Project:** Sentinel AI — AI Digital Media Forensics Platform

**Wave:** 4

**Status:** In Progress

**Release:** v0.4.0

**Focus:** Authentication & Authorization

**Prerequisite:** Wave 3 Complete (API Foundation)

---

# Overview

Wave 4 establishes the authentication and authorization security platform for Sentinel AI.

Wave 3 delivered the versioned REST API, dependency injection, transport schemas, centralized exception handling, pagination, and the user lifecycle API. Wave 4 builds on those boundaries by introducing the security domain, credential lifecycle, authenticated principals, sessions, authorization policy, browser authentication transport, recovery and verification workflows, abuse protection, security observability, and release-blocking security verification.

Wave 4 follows the architecture-first engineering lifecycle:

```text
Security Requirements
        |
        v
Security Architecture
        |
        v
Architecture Decision Records
        |
        v
Architecture Freeze
        |
        v
Implementation Planning
        |
        v
Implementation
        |
        v
Security Verification
        |
        v
Release Review
```

The v0.4.0 release is not complete until the frozen security architecture has been implemented and the mandatory security verification gates have passed.

---

# Wave 4 Lifecycle

| Stage | Focus | Status |
|---|---|---|
| W4-S0B | Authentication & Authorization Requirements | Complete / Frozen |
| W4-S0C | Authentication & Authorization Architecture | Complete / Frozen |
| W4-S0D | Implementation Planning & Decomposition | Next |
| Wave 4 Implementation | Security platform implementation | Not Started |
| Wave 4 Verification | Mandatory security verification | Not Started |
| v0.4.0 Release | Authentication & Authorization | Not Released |

Completion of W4-S0C freezes the architecture. It does **not** mark Wave 4 or v0.4.0 complete.

---

# Wave Objectives

The finalized Wave 4 objectives are to:

- Establish an authenticated security principal model.
- Introduce secure credential and password handling.
- Implement access-token and stateful refresh-session architecture.
- Establish secure browser authentication transport.
- Introduce centralized authorization using roles, permissions, ownership, and default-deny policy.
- Extend persistence through forward-only security migrations.
- Expose authentication and credential-lifecycle APIs.
- Implement password recovery and email-verification capabilities.
- Introduce layered abuse protection and security observability.
- Establish automated security verification and release-blocking security gates.
- Preserve the application boundaries established in Waves 2 and 3.

---

# W4-S0B — Authentication & Authorization Requirements

**Status:** Complete / Frozen

W4-S0B defines what Sentinel AI's authentication and authorization platform must guarantee.

The requirements baseline establishes security expectations around:

- Identity and authenticated principals.
- Credential handling.
- Password security.
- Authentication state.
- Session lifecycle.
- Authorization.
- Ownership and privileged operations.
- Browser transport.
- Recovery and verification.
- Revocation.
- Abuse protection.
- Security observability.
- Verification and release safety.

W4-S0C architecture decisions are required to trace back to this frozen requirements baseline.

---

# W4-S0C — Authentication & Authorization Architecture

**Status:** Complete / Frozen

W4-S0C translates the frozen security requirements into an implementable architecture.

## Architecture Packages

### Package 1 — Security Domain & Principal Architecture

Defines:

- Security-domain boundaries.
- Authenticated principal semantics.
- Relationship between identity and security state.
- Layer ownership and dependency direction.

### Package 2 — Credential & Password Architecture

Defines:

- Credential isolation.
- Password hashing and verification boundaries.
- Password policy.
- Credential lifecycle and secret-handling rules.

### Package 3 — Session & Token Architecture

Defines:

- Access-token architecture.
- Stateful refresh sessions.
- Rotation and replay handling.
- Revocation and session lifecycle.

### Package 4 — Authentication Transport Architecture

Defines:

- Bearer access-token transport.
- Secure refresh-cookie transport.
- CSRF protection.
- CORS and browser security boundaries.

### Package 5 — Authorization & Policy Architecture

Defines:

- Roles.
- Permissions.
- Principal authorization state.
- Ownership predicates.
- Self versus privileged access.
- Default-deny enforcement.

### Package 6 — Persistence & Migration Architecture

Defines:

- Security persistence boundaries.
- Credential/session/recovery/authorization state.
- Migration strategy.
- Preservation of existing Wave 3 user data.

### Package 7 — Authentication API Architecture

Defines the public security API contract for:

- Registration.
- Login.
- Authentication.
- Refresh.
- Logout.
- Session management.
- Security-sensitive account operations.

### Package 8 — Recovery & Credential-Lifecycle Architecture

Defines:

- Password change.
- Password recovery.
- Password reset.
- Email verification.
- Single-use capability semantics.
- Credential replacement and revocation consequences.

### Package 9 — Abuse Protection & Security Observability Architecture

Defines:

- Layered throttling.
- Privacy-preserving abuse-control keys.
- Delivery suppression.
- Security events.
- Durable audit.
- Secret redaction.
- Safe metrics.
- Degraded-mode behavior.

### Package 10 — Security Verification & Testing Architecture

Defines:

- Layered security testing.
- PostgreSQL-backed integration verification.
- Concurrency testing.
- Adversarial testing.
- Migration verification.
- Secret-leakage testing.
- Security release gates.

### Package 11 — Architecture Consolidation & ADR Set

Consolidates the architecture into the permanent ADR baseline.

### Package 12 — Final Architecture Freeze

Performs the cross-package architecture review and freezes W4-S0C for implementation.

---

# Architecture Decision Record Baseline

W4-S0C establishes the following accepted ADRs:

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

These ADRs form the frozen Wave 4 security architecture baseline.

Implementation that conflicts with a frozen architectural invariant requires formal architecture review rather than silent deviation.

---

# W4-S0D — Implementation Planning & Decomposition

**Status:** Next

W4-S0D converts the frozen architecture into implementation-ready work packages.

Its purpose is to determine:

- Implementation sequence.
- Package boundaries.
- Dependency order.
- Database migration sequence.
- Test delivery sequence.
- Integration gates.
- Security verification mapping.
- Commit and review boundaries.

W4-S0D may refine implementation mechanics, but it must not silently redesign the frozen W4-S0C architecture.

---

# Implementation Scope

Wave 4 implementation is expected to deliver the frozen architecture across the following areas:

- Security-domain models and contracts.
- Credential persistence and password services.
- Access-token issuance and validation.
- Stateful refresh-session persistence and rotation.
- Authentication dependencies.
- Registration and login workflows.
- Logout and session revocation.
- Authorization policy enforcement.
- Role and permission persistence.
- Browser cookie and CSRF controls.
- Password change and recovery.
- Email verification.
- Abuse controls and rate limiting.
- Security events and durable audit.
- Security test infrastructure.
- Migration and OpenAPI verification.
- Dependency and secret security gates.

Exact implementation packages are intentionally deferred to W4-S0D.

---

# Mandatory Security Verification

Wave 4 release approval requires the security verification architecture defined by ADR-0011.

The mandatory matrix covers `SEC-01` through `SEC-32`, including:

- Password security.
- Registration privilege isolation.
- JWT validation.
- Authentication and authorization.
- Refresh rotation and replay.
- Concurrency.
- Session revocation.
- Password recovery and verification.
- Enumeration resistance.
- CSRF, CORS, and cookie security.
- Secret leakage.
- Abuse controls.
- Security events and durable audit.
- Migration integrity.
- OpenAPI security contracts.
- Dependency vulnerability analysis.
- Repository secret detection.

A failing mandatory security gate blocks v0.4.0 release approval.

---

# Success Criteria

Wave 4 is considered complete only when:

- W4-S0B requirements remain satisfied.
- W4-S0C architecture remains satisfied.
- W4-S0D implementation planning is complete.
- Authentication and authorization implementation is complete.
- Required security migrations are complete.
- Security APIs are integrated.
- Authorization policy is enforced.
- Credential and session lifecycle behavior is operational.
- Recovery and verification workflows are operational.
- Abuse protection and security observability are operational.
- Mandatory security verification passes.
- Repository quality gates pass.
- Final Wave 4 engineering review is approved.
- v0.4.0 release documentation is complete.

---

# Deferred Work

Wave 4 does not introduce the later platform capabilities assigned to subsequent waves, including:

- Media platform implementation.
- Media upload and object-storage workflows.
- AI inference pipelines.
- Model serving.
- Forensics processing.
- Frontend platform implementation.
- Cloud and operations platform implementation beyond security infrastructure required by Wave 4.

Those capabilities remain assigned to later milestones.

---

# Expected Outcome

At the conclusion of Wave 4, Sentinel AI will evolve from an unauthenticated API platform into a security-aware application platform with explicit identity, credential, session, authorization, recovery, abuse-control, observability, and verification boundaries.

The resulting v0.4.0 security foundation will become a prerequisite for the media, AI, frontend, and cloud capabilities delivered in subsequent waves.
