# W4-S0D Implementation Plan

**Project:** Sentinel AI - AI Digital Media Forensics Platform
**Wave:** 4
**Stage:** W4-S0D
**Focus:** Authentication & Authorization Implementation Planning
**Status:** Complete / Frozen
**Target Release:** v0.4.0
**Architecture Authority:** ADR-0004 through ADR-0011
**Prerequisites:** W4-S0B Requirements Frozen; W4-S0C Architecture Frozen

---

# Purpose

This document is the canonical implementation-planning baseline for Sentinel AI Wave 4.

W4-S0B defined what the authentication and authorization platform must guarantee. W4-S0C translated those guarantees into frozen architecture and ADRs. W4-S0D translates that architecture into implementation responsibilities, dependency boundaries, verification expectations, and the execution sequence used to build Wave 4.

Accepted ADRs remain authoritative over implementation convenience.

---

# Frozen Planning Packages

| Package | Responsibility | Status |
|---|---|---|
| P1 | Security Domain & Principal Implementation Planning | Frozen |
| P2 | Persistence & Transaction Boundary Planning | Frozen |
| P3 | Authentication API & Contract Planning | Frozen |
| P4 | Credential & Password Security Implementation Planning | Frozen |
| P5 | Access Token Implementation Planning | Frozen |
| P6 | Stateful Refresh Session Implementation Planning | Frozen |
| P7 | Principal Establishment & Authentication Boundary Planning | Frozen |
| P8 | Authorization & Policy Implementation Planning | Frozen |
| P9 | Registration, Login, Refresh & Logout Workflow Planning | Frozen |
| P10 | Password Change, Recovery, Reset & Credential Lifecycle Planning | Frozen |
| P11 | Browser Authentication Transport & CSRF Implementation Planning | Frozen |
| P12 | Abuse Protection, Security Observability & Security Verification / Release-Gate Planning | Frozen |

All accepted package contracts are frozen implementation constraints.

---

# Cross-Cutting Implementation Invariants

- Persistence and security-domain state remain authoritative.
- Cookies, headers, telemetry, metrics, and browser state never become security authority.
- Recovery capability is not a Principal, access token, or refresh credential.
- CSRF proof grants no authentication or authorization authority.
- Network address is an abuse signal, not identity.
- Security core does not depend on FastAPI, cookies, CORS, CSRF, or vendor observability infrastructure.
- Repositories perform persistence operations but do not own application transaction commits.
- Raw refresh and recovery secrets are never persisted as authoritative database values.
- Security secrets are forbidden from logs, events, and metrics.
- Authentication, authorization, recovery, token validation, CSRF, and security configuration fail closed according to frozen contracts.
- Authorization is centralized and default-deny.

---

# Architecture Authority

| ADR | Authority |
|---|---|
| ADR-0004 | Authentication and Security Architecture |
| ADR-0005 | Credential Storage and Password Security |
| ADR-0006 | Access Token and Stateful Refresh Session Architecture |
| ADR-0007 | Authorization Model, Roles and Permissions |
| ADR-0008 | Browser Authentication Transport |
| ADR-0009 | Recovery and Verification Capability Architecture |
| ADR-0010 | Abuse Protection and Security Observability |
| ADR-0011 | Security Verification and Release Gates |

---

# Wave 4 Implementation Decomposition

| Sprint | Goal |
|---|---|
| W4-S1 | Security Domain Foundation |
| W4-S2 | Credential & Password Security |
| W4-S3 | Access Token Infrastructure |
| W4-S4 | Stateful Refresh Sessions |
| W4-S5 | Principal & Authentication Boundary |
| W4-S6 | Authorization Policy Engine |
| W4-S7 | Registration & Login |
| W4-S8 | Refresh & Logout |
| W4-S9 | Password Change |
| W4-S10 | Recovery & Password Reset |
| W4-S11 | Browser Authentication Security |
| W4-S12 | Abuse Protection & Security Observability |
| W4-S13 | Security Verification & Hardening |
| W4-S14 | Wave 4 Release Closure |

The P1-P12 planning packages are not implemented literally in numeric order. This sequence follows implementation dependencies.

---

# Dependency Sequence

```text
                         W4-S1
                            |
                            v
                         W4-S2
                            |
                  +---------+---------+
                  |                   |
                  v                   v
               W4-S3               W4-S4
                  |                   |
                  +---------+---------+
                            |
                            v
                         W4-S5
                            |
                            v
                         W4-S6
                            |
                            v
                         W4-S7
                            |
                            v
                         W4-S8
                            |
                            v
                         W4-S9
                            |
                            v
                        W4-S10
                            |
                            v
                        W4-S11
                            |
                            v
                        W4-S12
                            |
                            v
                        W4-S13
                            |
                            v
                        W4-S14
```

---

# Sprint Package Baseline

## W4-S1 - Security Domain Foundation

1. S1-P1 - Security Domain Types
2. S1-P2 - Credential Persistence
3. S1-P3 - Account Security State
4. S1-P4 - Authorization Persistence
5. S1-P5 - Refresh Session Persistence
6. S1-P6 - Recovery Capability Persistence
7. S1-P7 - Security Repository Boundaries
8. S1-P8 - Wave 4 Foundation Migration
9. S1-P9 - Persistence Verification

No authentication HTTP workflow is introduced in W4-S1.

## W4-S2 - Credential & Password Security

1. Password policy
2. Password hashing
3. Password verification
4. Credential service
5. Anti-enumeration/dummy verification path
6. Credential replacement
7. Security configuration
8. Unit and persistence verification

## W4-S3 - Access Token Infrastructure

1. Token configuration
2. Claim model
3. Token issuer
4. Token verifier
5. Required-claim validation
6. Purpose, issuer, and audience enforcement
7. Controlled clock/time boundary
8. Token adversarial verification

## W4-S4 - Stateful Refresh Sessions

1. Refresh credential generation
2. Selector/verifier architecture
3. Session creation
4. Session verification
5. Atomic rotation
6. Revocation
7. Replay detection
8. Replay containment
9. Subject/session revocation operations
10. PostgreSQL concurrency verification

## W4-S5 - Principal & Authentication Boundary

1. Principal domain object
2. Subject resolver
3. Authentication eligibility evaluation
4. Current authorization-state resolution
5. Authentication dependency/adapter
6. Anonymous and authenticated boundaries
7. Authentication failure taxonomy
8. Principal integration verification

## W4-S6 - Authorization Policy Engine

1. Authorization requirement model
2. Capability evaluation
3. Role mapping
4. SELF evaluation
5. Resource/ownership context
6. PRIVILEGED semantics
7. Default-deny policy engine
8. FastAPI authorization adapters
9. Authorization verification matrix
10. IDOR/adversarial verification

## W4-S7 - Registration & Login

1. Registration schemas
2. Registration workflow
3. Atomic security-identity creation
4. Registration endpoint
5. Login schemas
6. Login workflow
7. Anti-enumeration integration
8. Refresh-session creation
9. Access-token issuance
10. API/integration verification

## W4-S8 - Refresh & Logout

1. Refresh application workflow
2. Current subject/security-state revalidation
3. Current authorization reconstruction
4. Rotation integration
5. Replay integration
6. Logout workflow
7. Idempotent logout semantics
8. API contracts
9. Concurrency integration verification
10. Core authentication lifecycle verification

## W4-S9 - Password Change

1. Password-change schema
2. Current-password verification
3. Credential replacement
4. Required session action
5. Transaction ownership
6. Endpoint
7. Rollback verification
8. Credential lifecycle verification

## W4-S10 - Recovery & Password Reset

1. Recovery capability generation
2. Recovery verifier
3. Recovery issuance
4. Delivery port
5. Anti-enumeration behavior
6. Capability verification
7. Atomic capability consumption
8. Password reset
9. Session containment
10. Recovery endpoints
11. PostgreSQL concurrent-consumption verification
12. Complete recovery lifecycle verification

## W4-S11 - Browser Authentication Security

1. Browser transport configuration
2. Access credential extraction
3. Refresh cookie writer
4. Refresh cookie extraction
5. Refresh rotation transport
6. Cookie clearing
7. CSRF implementation
8. Origin policy
9. CORS configuration
10. Authentication cache controls
11. Recovery browser hardening
12. Browser adversarial verification

## W4-S12 - Abuse Protection & Security Observability

1. Abuse-policy configuration
2. Rate-limit abstraction
3. Shared/distributed abuse-state adapter
4. Login abuse protection
5. Registration abuse protection
6. Recovery abuse protection
7. Refresh/security abuse integration
8. Security-event taxonomy
9. Security-event schema
10. Event-emitter abstraction
11. Redaction
12. Security metrics
13. Correlation
14. Observability verification

## W4-S13 - Security Verification & Hardening

1. Authentication adversarial matrix
2. Token adversarial matrix
3. Refresh adversarial matrix
4. Authorization/IDOR matrix
5. Recovery adversarial matrix
6. Browser/CSRF matrix
7. Abuse-control matrix
8. No-secret regression suite
9. Architecture conformance checks
10. Security configuration tests
11. Migration verification
12. Complete security lifecycle suite

## W4-S14 - Wave 4 Release Closure

1. Requirement traceability
2. ADR implementation traceability
3. Verification evidence
4. Migration evidence
5. Final security review
6. Documentation synchronization
7. CHANGELOG update
8. Roadmap closure
9. Release-candidate validation
10. Wave 4 freeze

---

# Verification Model

```text
Unit
  |
  v
Service
  |
  v
PostgreSQL Persistence
  |
  v
API / Integration
  |
  v
Adversarial
  |
  v
Cross-Package Lifecycle
```

Security-critical PostgreSQL concurrency semantics are verified against PostgreSQL rather than inferred solely from mocks or SQLite.

Negative paths, denial paths, replay, concurrency, enumeration, privilege escalation, IDOR, CSRF, secret leakage, and configuration failure are first-class verification targets.

---

# Release Gates

Mandatory Wave 4 gates include, as applicable:

- Ruff
- Ruff format
- MyPy strict
- pre-commit
- unit verification
- service verification
- PostgreSQL persistence verification
- API/integration verification
- adversarial security verification
- architecture-conformance verification
- migration verification
- secret-leak verification
- requirement traceability
- ADR traceability
- final security review

A mandatory security-gate failure blocks release. Code coverage percentage alone is not security proof.

---

# Git Execution Strategy

Default branch pattern:

```text
feature/w4-s1-security-domain-foundation
feature/w4-s2-credential-password-security
feature/w4-s3-access-token-infrastructure
feature/w4-s4-stateful-refresh-sessions
feature/w4-s5-principal-authentication-boundary
feature/w4-s6-authorization-policy-engine
feature/w4-s7-registration-login
feature/w4-s8-refresh-logout
feature/w4-s9-password-change
feature/w4-s10-recovery-password-reset
feature/w4-s11-browser-authentication-security
feature/w4-s12-abuse-security-observability
feature/w4-s13-security-verification-hardening
feature/w4-s14-wave-4-release-closure
```

Each sprint is independently reviewable before merging into `develop`.

---

# Sprint Execution Protocol

```text
Sprint Start
    |
    v
Repository Inspection
    |
    v
Package Design
    |
    v
Package Freeze
    |
    v
Implementation
    |
    v
Focused Verification
    |
    v
Integration Verification
    |
    v
Static Quality Gates
    |
    v
Diff Review
    |
    v
Stage Exact Files
    |
    v
Staged Diff Review
    |
    v
Commit
    |
    v
Push / Review / Merge
    |
    v
Sprint Closure
```

Code for an implementation package is not written before its package design is reviewed and frozen.

---

# Traceability Chain

```text
W4-S0B Requirement
        |
        v
W4-S0C Architecture
        |
        v
ADR-0004 ... ADR-0011
        |
        v
W4-S0D Implementation Contract
        |
        v
W4-S1 ... W4-S12 Implementation
        |
        v
W4-S13 Verification
        |
        v
W4-S14 Release Evidence
```

---

# Change Control

This implementation plan is frozen.

Implementation may refine non-semantic details such as internal class names, module organization, helper decomposition, test fixture organization, and adapter naming.

Implementation must not silently change authentication authority, credential semantics, refresh rotation/replay behavior, Principal semantics, authorization semantics, recovery capability semantics, browser transport security, abuse-protection guarantees, observability secret boundaries, or mandatory verification/release gates.

A proposed change to a frozen security decision requires architecture review and, where applicable, a new or superseding ADR before implementation.

---

# W4-S0D Closure

W4-S0D is complete when P1 through P12 and the W4-S1 through W4-S14 execution decomposition are accepted as the canonical implementation baseline.

**W4-S0D Status: COMPLETE / FROZEN**

---

# Immediate Next Step

Begin **W4-S1 - Security Domain Foundation / P1 - Security Domain Types**.

No persistence model, migration, repository, authentication endpoint, or security workflow is implemented before S1-P1's required domain vocabulary and invariants are inspected, designed, reviewed, and frozen.
