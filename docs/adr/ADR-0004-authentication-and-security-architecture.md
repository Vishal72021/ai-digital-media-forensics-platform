# ADR-0004 — Authentication & Security Architecture

| Property | Value |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-26 |
| **Authors** | Forensix AI Engineering Team |
| **Decision Category** | Security Architecture |
| **Supersedes** | None |
| **Superseded By** | None |

---

# Context

Wave 3 established the API foundation for Sentinel AI, including dependency injection, service and repository boundaries, centralized exception handling, typed configuration, API versioning, SQLAlchemy persistence, PostgreSQL integration, and Alembic migrations.

Wave 4 introduces Authentication & Authorization for release `v0.4.0`.

Authentication and authorization affect several security-sensitive areas of the backend:

- Identity and principal establishment.
- Credential management.
- Authentication.
- Session management.
- Token issuance and validation.
- Authorization.
- Password recovery.
- Email verification.
- Abuse protection.
- Security observability.
- Security verification.

These capabilities must integrate with the existing backend architecture rather than form an isolated authentication subsystem.

A common security architecture is therefore required to define responsibility boundaries, preserve the dependency direction established by previous waves, and provide the architectural foundation for the specialized security decisions documented in ADR-0005 through ADR-0011.

---

# Decision

Sentinel AI will implement authentication and authorization as cooperating security capabilities integrated into the existing layered backend architecture.

The canonical dependency direction remains:

```text
HTTP / FastAPI
      |
      v
API / Transport
      |
      v
Application / Security Services
      |
      v
Domain
      |
      v
Persistence / Infrastructure
```

Wave 4 extends this architecture. It does not introduce a parallel authentication stack.

Authentication and authorization remain separate responsibilities.

Authentication establishes a trusted principal.

Authorization determines whether that principal is permitted to perform an operation.

```text
Credential / Token
        |
        v
Authentication
        |
        v
Principal
        |
        v
Authorization
        |
        +-- Allow
        +-- Deny
```

Client-controlled input must never directly establish trusted identity, roles, permissions, or privilege.

---

# Responsibility Boundaries

## API / Transport

The API and transport layer owns HTTP-specific concerns, including:

- Request parsing.
- Response construction.
- Authentication credential extraction.
- Cookie handling.
- CSRF transport enforcement.
- HTTP authentication and authorization semantics.
- OpenAPI contracts.
- Adaptation of transport-derived request information.

Framework-specific request objects and transport details must not become the application or domain security model.

Where application services require request-derived information, the transport layer must adapt that information into framework-independent application context.

## Application / Security Services

Application and security services orchestrate security use cases, including:

- Authentication.
- Credential lifecycle operations.
- Session lifecycle operations.
- Authorization.
- Recovery.
- Verification.
- Abuse-control coordination.
- Security-event coordination.

Application security services must remain independent of FastAPI-specific request and exception types unless a transport adapter explicitly owns that integration.

## Domain

The domain layer represents security concepts, rules, and failures independently of HTTP and infrastructure concerns.

This includes concepts such as:

- Authenticated principals.
- Roles and permissions.
- Security state.
- Domain security failures.
- Security lifecycle invariants.

## Persistence / Infrastructure

Persistence and infrastructure provide implementations required by the security architecture.

PostgreSQL remains authoritative for durable security state.

Ephemeral distributed infrastructure may support operational concerns such as abuse-control accounting, but it must not replace PostgreSQL as the authoritative source for durable identity, credential, session, authorization, capability-consumption, or audit state.

---

# Security Responsibility Decomposition

Wave 4 security behavior must not be concentrated into a single monolithic authentication component.

The architecture separates the following responsibilities conceptually:

```text
Authentication
Credential Security
Session Management
Token Operations
Authorization
Recovery
Verification
Abuse Protection
Security Observability
Security Verification
```

Concrete class names, module names, and internal implementation structures may evolve during implementation provided these responsibility boundaries and the specialized Wave 4 ADRs remain satisfied.

---

# Security State

Security state with independent lifecycle semantics should remain independently modeled rather than accumulating unrelated responsibilities directly on the user entity.

Conceptually:

```text
User
 |
 +-- Credential State
 +-- Session State
 +-- Authorization Relationships
 +-- Recovery / Verification Capabilities
 +-- Security Audit State
```

The exact persistence model is governed by the specialized Wave 4 architecture decisions and implementation design.

Released Alembic migration history is immutable.

Wave 4 schema evolution must occur through new migration revisions.

Migration logic must not fabricate credential, verification, authorization, or other security evidence for existing users.

---

# Transaction and Concurrency Boundaries

Security operations that represent one authoritative state transition must preserve the transaction semantics required by that operation.

Examples include:

- Refresh credential rotation.
- Password recovery.
- Password change.
- Session revocation.
- Recovery capability consumption.
- Verification capability consumption.
- Security state changes coupled with required durable audit state.

A security transition that requires atomic behavior must not be implemented as independently committed partial state changes.

Single-use security authority must preserve the following invariant:

```text
Concurrent consumption
        |
        v
At most one authoritative success
```

Application-level validity checks alone are insufficient where concurrent requests could violate single-use semantics.

The persistence implementation must provide the required concurrency guarantees.

---

# Dependency Injection

Wave 4 extends the dependency injection foundation established during Wave 3.

Security dependencies must be supplied through application composition rather than instantiated directly inside API endpoints.

These dependencies may include:

- Password security components.
- Token services.
- Authentication services.
- Session services.
- Authorization services.
- Recovery and verification services.
- Abuse-protection services.
- Security observability components.

The exact dependency graph may evolve during implementation provided it preserves the frozen architecture boundaries.

---

# Exception Handling

Wave 4 security failures integrate with the centralized exception-handling architecture established during Wave 3.

The expected direction remains:

```text
Security / Domain Failure
        |
        v
Domain or Application Exception
        |
        v
Central Exception Mapping
        |
        v
Canonical HTTP Error Response
```

Domain and application security services must not use transport-specific HTTP exceptions as their canonical failure model.

Authentication and authorization failures must preserve their distinct API semantics.

---

# Configuration

Security configuration extends the existing typed configuration architecture.

Security configuration may include:

- Password policy.
- Token lifetimes.
- Token issuer and audience.
- Cryptographic key references.
- Cookie policy.
- CSRF policy.
- CORS policy.
- Recovery and verification capability lifetimes.
- Abuse-control thresholds.
- Delivery controls.

Application-wide security policy must not be scattered across endpoint-local constants.

Secrets must not be committed to repository configuration.

---

# Security Invariants

Wave 4 implementation must preserve the following architecture-level invariants:

1. Authentication and authorization remain distinct.
2. Client-controlled input cannot establish trusted privilege.
3. Security responsibilities retain explicit ownership.
4. Raw reusable secrets are not persisted when one-way verification is sufficient.
5. Durable security authority remains server-controlled where required by the security model.
6. Multi-state security transitions preserve their required atomicity.
7. Single-use security authority permits at most one authoritative successful consumption.
8. Transport concerns do not leak into domain or application security services without an explicit adaptation boundary.
9. Wave 4 extends the existing backend architecture rather than creating a parallel security stack.
10. Security-sensitive behavior requires automated verification evidence.

Detailed security mechanisms are defined by the specialized Wave 4 ADRs.

---

# Specialized Security Decisions

This ADR establishes the umbrella architecture.

The following decisions are intentionally delegated to dedicated ADRs:

| ADR | Decision |
|-----|----------|
| ADR-0005 | Credential Storage & Password Security |
| ADR-0006 | Access Token & Stateful Refresh Session Architecture |
| ADR-0007 | Authorization Model — Roles & Permissions |
| ADR-0008 | Browser Authentication Transport |
| ADR-0009 | Recovery & Verification Capability Architecture |
| ADR-0010 | Abuse Protection & Security Observability |
| ADR-0011 | Security Verification & Release Gates |

Those ADRs refine this architecture and must remain consistent with it unless a later accepted ADR explicitly supersedes an affected decision.

---

# Alternatives Considered

## Option A — Integrated Layered Security Architecture

Integrate authentication and authorization into the existing API, application, domain, persistence, and infrastructure architecture while maintaining explicit security responsibility boundaries.

### Advantages

- Preserves the existing backend architecture.
- Maintains explicit responsibility ownership.
- Supports independent testing.
- Keeps application security logic framework-independent.
- Supports transactionally correct security state transitions.
- Improves architecture traceability.
- Supports incremental implementation.

### Disadvantages

- Requires multiple cooperating security components.
- Requires explicit persistence and transaction design.
- Requires broader security testing.

**Decision:** Accepted.

---

## Option B — Monolithic Authentication Service

Place credential handling, authentication, sessions, authorization, recovery, and related security behavior inside one authentication service.

### Advantages

- Smaller initial component count.
- Lower short-term implementation overhead.

### Disadvantages

- Combines responsibilities with different lifecycle semantics.
- Produces high coupling.
- Reduces independent testability.
- Makes future security evolution harder.
- Encourages authentication and authorization concerns to become entangled.

**Decision:** Rejected.

---

## Option C — Stateless Token-Only Architecture

Use signed tokens as the primary source of both authentication and session authority without durable server-controlled refresh-session state.

### Advantages

- Reduced server-side session persistence.
- Simple request-side token verification.

### Disadvantages

- Conflicts with the frozen Wave 4 session architecture.
- Weakens centralized session revocation.
- Complicates refresh credential replay handling.
- Does not provide the required server-controlled refresh authority.

**Decision:** Rejected.

---

## Option D — Transport-Coupled Security Architecture

Allow application security services to depend directly on FastAPI requests, cookies, HTTP exceptions, and related transport concepts.

### Advantages

- Less adaptation code.
- Faster initial endpoint implementation.

### Disadvantages

- Couples application security logic to FastAPI.
- Reduces independent testability.
- Violates established service boundaries.
- Makes transport evolution more difficult.

**Decision:** Rejected.

---

# Consequences

## Positive

- Security responsibilities have explicit architectural ownership.
- Authentication and authorization remain separate.
- Wave 3 architectural boundaries remain intact.
- Application security behavior remains independently testable.
- Durable security authority has a defined persistence boundary.
- Atomic and concurrency-sensitive operations have explicit architectural requirements.
- Framework-specific concerns remain at the transport boundary.
- Specialized security decisions can be documented independently.
- Wave 4 can be implemented incrementally against a stable architecture contract.

## Negative

- Authentication and authorization require several cooperating components rather than one authentication module.
- Additional security persistence and migrations are required.
- Transaction and concurrency requirements increase implementation complexity.
- Abuse protection may require distributed operational infrastructure.
- Security verification requires more extensive testing than ordinary API functionality.

These trade-offs are accepted because authentication and authorization form a critical security boundary for Sentinel AI.

---

# Risks

The principal architectural risks are:

- Security responsibilities drifting across layers.
- Authentication and authorization becoming implicitly coupled.
- Transport concerns leaking into application services.
- Incorrect transaction boundaries producing partial security state.
- Concurrent operations violating single-use security guarantees.
- Security state becoming unnecessarily concentrated on the user entity.
- Implementation shortcuts weakening frozen security invariants.

These risks are mitigated through:

- Architecture-aligned implementation packages.
- Dedicated security ADRs.
- Explicit dependency injection.
- Centralized exception mapping.
- Database transaction and concurrency controls.
- Automated security verification.
- Architecture traceability during implementation review.

---

# Implementation Notes

This ADR governs the umbrella security architecture for:

- **Phase:** Phase 2
- **Wave:** Wave 4
- **Focus:** Authentication & Authorization
- **Release Target:** `v0.4.0`

Wave 4 production implementation must proceed through reviewable, architecture-aligned implementation packages.

Implementation details such as module names, class names, repository method names, helper functions, dependency wiring, and migration decomposition may evolve where they do not alter frozen security responsibilities, contracts, or invariants.

Any proposed implementation change that alters a frozen security invariant, responsibility boundary, or major architecture relationship requires architecture review before implementation.

---

# Verification

Compliance with this ADR must be demonstrated through the security verification strategy defined by ADR-0011.

Applicable evidence will include:

- Static quality gates.
- Unit tests.
- Integration tests.
- PostgreSQL-backed persistence tests.
- Migration tests.
- Authentication tests.
- Authorization tests.
- Security lifecycle tests.
- Concurrency tests.
- Adversarial security tests.
- Secret-handling verification.

Functional endpoint behavior alone is not sufficient evidence of architecture compliance.

---

# References

## Existing ADRs

- ADR-0001 — Adopt a Monorepo Repository Structure.
- ADR-0002 — Adopt FastAPI Application Factory Pattern.
- ADR-0003 — Adopt an Independent Backend Python Project.

## Wave 4 ADRs

- ADR-0005 — Credential Storage & Password Security.
- ADR-0006 — Access Token & Stateful Refresh Session Architecture.
- ADR-0007 — Authorization Model — Roles & Permissions.
- ADR-0008 — Browser Authentication Transport.
- ADR-0009 — Recovery & Verification Capability Architecture.
- ADR-0010 — Abuse Protection & Security Observability.
- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- Wave 3 Review.
- Wave 4 architecture baseline established by W4-S0A, W4-S0B, and W4-S0C.
