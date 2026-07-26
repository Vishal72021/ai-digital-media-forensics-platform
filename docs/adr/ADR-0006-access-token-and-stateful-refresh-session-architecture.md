# ADR-0006 — Access Token & Stateful Refresh Session Architecture

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

Wave 4 requires authenticated continuity while preserving bounded credential lifetime, server-controlled revocation, multi-device sessions, refresh replay protection, password/security-state invalidation, and efficient ordinary API requests.

A purely stateless authentication design cannot satisfy all of these requirements cleanly.

Long-lived bearer JWTs weaken logout and revocation semantics because a cryptographically valid token remains usable until expiry. Fully stateless access-and-refresh JWT designs similarly make reliable refresh revocation and replay handling difficult without introducing state that effectively recreates a session system.

At the opposite extreme, a traditional server-side session lookup for every authenticated request provides strong revocation semantics but imposes shared-state access on the normal request path.

Sentinel AI therefore requires an architecture that separates:

- Short-lived request authority.
- Long-lived authentication continuity.
- Durable server-controlled session authority.
- Refresh credential secrecy.
- Refresh rotation and replay detection.
- Session revocation.
- Concurrent refresh correctness.
- Access-token validation.
- Session expiration.
- Multi-device authentication.

This ADR records the durable session and token decisions established by W4-S0C Package 3.

---

# Decision

Sentinel AI SHALL use a hybrid access-token and stateful refresh-session architecture.

The canonical model is:

```text
Authentication
      |
      v
┌──────────────────────────────┐
│ Short-Lived Access JWT       │
│                              │
│ • ordinary API requests      │
│ • locally verifiable         │
│ • not persisted individually │
└──────────────┬───────────────┘
               |
               | short-lived request authority
               |
               +
               |
┌──────────────v───────────────┐
│ Opaque Refresh Credential    │
│                              │
│ • long-lived continuity      │
│ • server-controlled session  │
│ • digest persisted only      │
│ • rotated on every use       │
│ • replay detectable          │
└──────────────┬───────────────┘
               |
               v
      PostgreSQL Session State
```

Ordinary authenticated requests use locally verifiable short-lived JWT access credentials.

Long-lived authentication continuity uses opaque refresh credentials backed by durable server-side authentication-session state.

PostgreSQL is the authoritative Wave 4 session store.

---

# Separation of Access Authority and Session Authority

Access tokens and authentication sessions SHALL remain distinct security concepts.

## Access JWT

An access JWT represents short-lived request authority.

It is:

- Signed.
- Short-lived.
- Locally verifiable.
- Presented frequently during ordinary API access.
- Not persisted individually as authoritative session state.

## Authentication Session

An authentication session represents longer-lived, server-controlled authentication continuity.

It is:

- Durable.
- Revocable.
- Associated with refresh authority.
- Independently manageable.
- Subject to absolute expiration.
- Subject to inactivity expiration.
- A target for security-state invalidation.

The architecture SHALL NOT treat a valid access JWT as equivalent to a durable authentication session.

---

# Access Tokens

Ordinary authenticated API access SHALL use short-lived signed JWTs.

Conceptually:

```text
Request
   |
   v
Access JWT
   |
   v
Verifier-Controlled Validation
   |
   v
Authenticated Principal
   |
   v
Authorization
```

Access JWTs SHALL NOT be persisted individually in PostgreSQL merely to support ordinary request authentication.

This allows normal authenticated requests to remain locally verifiable without a session-database lookup on every request.

The trade-off is explicit:

```text
session revoked
      |
      +--> refresh authority terminates immediately
      |
      └--> already-issued access authority remains bounded
           by the access JWT's short expiration
```

The architecture SHALL NOT claim instantaneous revocation of already-issued access JWTs when no request-time session lookup occurs.

---

# JWT Validation

JWT validation SHALL explicitly enforce the verifier-controlled security contract.

At minimum, validation SHALL enforce the configured:

- Signature algorithm.
- Cryptographic signature.
- Issuer.
- Audience.
- Expiration.
- Required claims.

The verifier SHALL control which algorithms are acceptable.

Token-controlled algorithm selection SHALL NOT weaken verification policy.

JWT validation failures SHALL fail closed.

Malformed, expired, incorrectly signed, incorrectly issued, incorrectly targeted, or otherwise invalid tokens SHALL NOT establish a principal.

Sentinel AI SHALL use a mature maintained JWT/cryptographic library.

Custom JWT signing, parsing, or cryptographic implementations are prohibited.

---

# JWT Claims

Access JWT claims SHALL remain minimal.

Claims MAY contain only the identity, session, temporal, and authority-related information required by the frozen authentication and authorization architecture.

They SHALL NOT contain:

- Passwords.
- Password hashes.
- Refresh credentials.
- Recovery capabilities.
- Verification capabilities.
- Other reusable credential secrets.

The exact authority representation associated with access JWTs is governed by ADR-0007.

The transport mechanism for access JWTs is governed by ADR-0008.

---

# Stateful Refresh Authority

Long-lived authentication continuity SHALL use opaque refresh credentials backed by server-side authentication-session state.

A refresh credential SHALL NOT contain trusted client-side session state.

Possession of the opaque credential proves only possession of that secret. The server determines the authoritative session state.

Conceptually:

```text
Opaque Refresh Credential
          |
          v
One-Way Lookup / Verification
          |
          v
Authoritative Session State
          |
          ├── active/revoked
          ├── user identity
          ├── expiry state
          ├── refresh state
          └── security lifecycle state
```

The client SHALL NOT be trusted to assert session validity through refresh-token contents.

---

# Refresh Credential Storage

Raw refresh credentials SHALL NEVER be persisted.

Only a one-way representation suitable for secure server-side lookup or verification SHALL be stored.

Conceptually:

```text
raw refresh credential
          |
          v
one-way transformation
          |
          v
persisted refresh representation
```

A database compromise therefore SHALL NOT directly expose reusable raw refresh credentials from the refresh-token persistence records.

The exact one-way representation and implementation library are implementation decisions provided they preserve this invariant.

---

# Refresh Rotation

Refresh credentials SHALL rotate after every successful use.

The lifecycle is:

```text
refresh-A
    |
    v
successful refresh
    |
    +--> new access JWT
    |
    └--> refresh-B

refresh-A = consumed
```

Then:

```text
refresh-B
    |
    v
successful refresh
    |
    +--> new access JWT
    |
    └--> refresh-C

refresh-B = consumed
```

A successfully consumed refresh credential SHALL NOT remain valid as reusable refresh authority.

Rotation limits the useful lifetime of a stolen credential and creates a basis for replay detection.

---

# Atomic Refresh Rotation

Refresh credential consumption and successor establishment SHALL form one authoritative atomic security transition.

The required concurrency invariant is:

```text
                  refresh-A
                     |
          ┌──────────┴──────────┐
          |                     |
      request 1             request 2
          |                     |
          v                     v
              concurrent use
                     |
                     v
          AT MOST ONE SUCCESS
```

The system SHALL NOT permit two concurrent requests to successfully produce two independent valid successor refresh credentials from the same predecessor.

Application-level check-then-update logic is insufficient where concurrent requests could violate this invariant.

The persistence implementation SHALL provide the required transactional/concurrency guarantee.

---

# Refresh Replay Detection

Reuse of a previously consumed refresh credential SHALL be treated as suspected credential replay.

Conceptually:

```text
refresh-A
    |
    v
legitimate successful rotation
    |
    v
refresh-A consumed
    |
    v
later reuse of refresh-A
    |
    v
suspected replay
    |
    v
revoke affected authentication session
    |
    v
fresh authentication required
```

Replay detection SHALL fail closed.

Replay of one session's consumed refresh credential SHALL target the affected session according to the frozen architecture rather than silently granting new authentication authority.

Security observability for replay events is governed by ADR-0010.

---

# Multiple Authentication Sessions

A user MAY maintain multiple independent authentication sessions.

Conceptually:

```text
User
├── Session A — browser/device context
├── Session B — browser/device context
└── Session C — browser/device context
```

Each authentication session SHALL be independently revocable.

This supports current-session logout without requiring every legitimate session to terminate.

The architecture SHALL also support revocation of all authentication sessions belonging to a user when required by a security lifecycle event.

---

# Logout

Normal logout SHALL revoke the current server-side authentication session.

After successful logout:

```text
current session
      |
      v
revoked
      |
      +--> refresh authority unusable immediately
      |
      └--> existing access JWT remains bounded by
           its short configured expiration
```

Logout therefore guarantees immediate termination of refresh authority and bounded termination of already-issued access authority.

Browser credential cleanup and cookie semantics are governed by ADR-0008.

---

# Logout-All

The session architecture SHALL support revocation of all authentication sessions for a user.

Conceptually:

```text
user_id
   |
   v
all active authentication sessions
   |
   v
revoke
```

This capability supports security workflows such as credential compromise response and explicit logout-all behavior.

The public API contract for logout-all is governed by the authentication API architecture.

---

# Password Change Consequences

Password replacement is a security event that affects session authority.

W4-S0C Package 3 originally allowed policy-controlled preservation of the current authenticated session while revoking other sessions.

The later frozen credential-lifecycle architecture strengthened the final Wave 4 behavior: password replacement revokes all pre-existing sessions.

Accordingly, the authoritative Wave 4 lifecycle behavior SHALL be interpreted together with ADR-0009 and the final architecture amendment ledger.

No implementation may use the earlier Package 3 flexibility to weaken the later frozen credential-lifecycle rule.

---

# Password Reset Consequences

Password reset SHALL revoke all authentication sessions and require fresh authentication.

Conceptually:

```text
Password Recovery
       |
       v
Password Replaced
       |
       v
Revoke All Sessions
       |
       v
Destroy Existing Refresh Authority
       |
       v
Fresh Authentication Required
```

This establishes a clear post-compromise boundary.

---

# Account Disablement

Account disablement SHALL revoke all authentication sessions associated with the account.

The system SHALL NOT preserve long-lived refresh authority for an account that has become ineligible to authenticate.

Already-issued access JWT behavior remains bounded by the short access-token lifetime unless another frozen security mechanism explicitly requires stronger request-time invalidation.

---

# Privilege and Security-State Changes

Privilege or other security-state changes MAY require session revocation.

The authorization architecture determines which authority changes require invalidation.

Conceptually:

```text
security / privilege state change
             |
             v
persist authoritative change
             |
             v
revoke affected sessions
             |
             v
future authentication / token issuance
             |
             v
new authority state
```

The detailed authority model is governed by ADR-0007.

---

# Session Expiration

Authentication sessions SHALL support both:

- Non-renewable absolute expiration.
- Inactivity expiration.

## Absolute Expiration

An authentication session SHALL have a maximum lifetime that refresh activity cannot extend indefinitely.

Conceptually:

```text
session created
      |
      |---------------- maximum lifetime ----------------|
      |
      v
absolute expiration

refresh activity cannot move this boundary indefinitely
```

## Inactivity Expiration

A session MAY become invalid after a configured period without qualifying activity.

This limits dormant long-lived session authority.

Exact access-token, inactivity, and absolute-session lifetimes SHALL be centralized security configuration.

They SHALL NOT be scattered as endpoint-local or service-local constants.

This ADR intentionally does not invent exact lifetime values that were not frozen by W4-S0C.

---

# PostgreSQL as Authoritative Session Store

PostgreSQL SHALL be the initial authoritative store for durable authentication-session and refresh-rotation state.

Conceptually:

```text
PostgreSQL
└── authentication_sessions
    └── refresh-token / rotation state
```

This provides durable:

- Session identity.
- Revocation state.
- Refresh authority.
- Rotation state.
- Expiration state.
- Concurrency enforcement.

Redis or equivalent distributed session infrastructure is NOT required for the Wave 4 baseline.

Redis SHALL NOT silently become authoritative session persistence merely for implementation convenience.

A future move of authoritative session state away from PostgreSQL requires architecture review.

---

# Ordinary Request Efficiency

Ordinary authenticated requests SHALL NOT require a PostgreSQL session lookup solely to validate every access JWT.

The selected architecture deliberately separates:

```text
Normal API Request
        |
        v
Short-Lived Access JWT
        |
        v
Local Verification
        |
        v
Principal
```

from:

```text
Refresh / Session Operation
        |
        v
Opaque Refresh Credential
        |
        v
Stateful Verification
        |
        v
Atomic Rotation / Revocation
        |
        +--> New Access JWT
        └--> New Refresh Credential
```

This keeps the normal request path efficient while retaining server-controlled long-lived session authority.

---

# Failure Behavior

Token and session processing SHALL fail closed.

Examples include:

- Invalid JWT signature.
- Unsupported or unexpected JWT algorithm.
- Missing required claim.
- Incorrect issuer.
- Incorrect audience.
- Expired access token.
- Unknown refresh credential.
- Revoked session.
- Expired session.
- Consumed refresh credential.
- Refresh-state inconsistency.
- Persistence failure during refresh rotation.
- Cryptographic verification failure.
- Uncertain session state.

None of these conditions may establish or extend authenticated authority.

Internal operational failures MAY be distinguished from ordinary authentication failures for observability, but uncertainty SHALL NOT become authentication success.

---

# Transport Independence

This ADR defines credential semantics and session lifecycle, not browser transport.

The following concerns are explicitly governed by ADR-0008:

- `Authorization: Bearer` transport.
- Browser runtime storage.
- Refresh cookies.
- `HttpOnly`.
- `Secure`.
- `SameSite`.
- CSRF defenses.
- CORS.
- Cookie scope.
- Cookie deletion.

Session/token services SHALL NOT depend on FastAPI request or cookie objects merely because the first-party browser transport uses those mechanisms.

---

# Security Invariants

The following invariants are mandatory:

1. Sentinel AI uses a hybrid access-token/stateful-session architecture.
2. Ordinary authenticated API requests use short-lived signed JWT access tokens.
3. Long-lived authentication continuity uses opaque refresh credentials backed by server-controlled session state.
4. PostgreSQL is the Wave 4 authoritative authentication-session store.
5. Access JWTs are not persisted individually as the session database.
6. Refresh credentials contain no trusted client-side session state.
7. Raw refresh credentials are never persisted.
8. Refresh credentials rotate after every successful use.
9. Refresh credential consumption and successor establishment are atomic.
10. A consumed refresh credential cannot legitimately rotate twice.
11. Reuse of consumed refresh authority is treated as suspected replay and revokes the affected session.
12. Users may maintain multiple independent sessions.
13. Sessions are independently revocable.
14. Logout immediately terminates refresh authority for the current session.
15. Existing access authority after logout remains bounded by short JWT expiration.
16. The architecture supports revocation of all sessions for a user.
17. Password replacement follows the final frozen credential-lifecycle session-revocation policy.
18. Password reset revokes all sessions and requires fresh authentication.
19. Account disablement revokes all authentication sessions.
20. Privilege/security-state changes can trigger session revocation.
21. Sessions have non-renewable absolute expiration.
22. Sessions support inactivity expiration.
23. JWT validation explicitly enforces verifier-controlled algorithm, signature, issuer, audience, expiration, and required claims.
24. JWT claims remain minimal and contain no credential secrets.
25. Custom JWT/cryptographic implementations are prohibited.
26. Exact token/session lifetimes are centralized configuration.
27. Token/session validation uncertainty fails closed.
28. Authorization representation is governed by the authorization architecture.
29. Credential transport is governed by the authentication transport architecture.
30. Redis or equivalent distributed session infrastructure is not required for the Wave 4 baseline.

---

# Alternatives Considered

## Option A — Hybrid Short-Lived JWT + Stateful Opaque Refresh Session

Use short-lived locally verifiable access JWTs for ordinary requests and opaque rotating refresh credentials backed by durable server-side session state.

### Advantages

- Efficient ordinary request validation.
- Strong server-controlled refresh revocation.
- Supports logout and logout-all.
- Supports multiple devices.
- Supports refresh rotation.
- Supports replay detection.
- Supports bounded access authority.
- Avoids storing access tokens individually.
- Avoids mandatory distributed session infrastructure for Wave 4.

### Disadvantages

- More complex than a token-only architecture.
- Requires durable session persistence.
- Requires concurrency-safe refresh rotation.
- Already-issued access JWTs cannot be instantly revoked without additional request-time state checks.

**Decision:** Accepted.

---

## Option B — Long-Lived JWT Only

Issue a long-lived signed JWT and use it as both request and continuity authority.

### Advantages

- Simple implementation.
- No server-side refresh-session state.
- Local verification.

### Disadvantages

- Weak logout semantics.
- Weak server-side revocation.
- Account disablement and compromise response remain delayed until token expiry.
- Encourages excessively long bearer authority.

**Decision:** Rejected.

---

## Option C — Stateless JWT Access + Stateless JWT Refresh

Issue both access and refresh credentials as stateless signed JWTs.

### Advantages

- Local token verification.
- Reduced explicit session persistence.

### Disadvantages

- Reliable refresh revocation becomes difficult.
- Replay detection requires additional state.
- Rotation semantics recreate state indirectly.
- Conflicts with the required server-controlled refresh authority.

**Decision:** Rejected.

---

## Option D — Traditional Server-Side Session Lookup on Every Request

Use an opaque session identifier and validate server-side session state for every authenticated request.

### Advantages

- Strong immediate revocation semantics.
- Simple centralized session authority.

### Disadvantages

- Every authenticated request depends on shared session-state access.
- Adds database/shared-store pressure to the normal request path.
- Would likely require additional distributed session infrastructure as scale grows.
- Unnecessary for the current Sentinel AI architecture.

**Decision:** Not selected for the Wave 4 baseline.

---

## Option E — Redis as Authoritative Session Store

Use Redis or equivalent distributed ephemeral infrastructure as the authoritative authentication-session database.

### Advantages

- Fast shared session access.
- Natural distributed availability for session lookups.

### Disadvantages

- Introduces additional mandatory infrastructure.
- Conflicts with the frozen durable-authority boundary.
- Unnecessary because ordinary access requests do not require session lookups.
- Changes the authoritative persistence model.

**Decision:** Rejected for the Wave 4 baseline.

---

# Consequences

## Positive

- Ordinary API requests remain locally verifiable.
- Long-lived authentication continuity remains server-controlled.
- Refresh credentials can be independently revoked.
- Raw refresh secrets are not stored.
- Rotation limits reusable refresh authority.
- Replay can be detected.
- Concurrent refresh consumption has an explicit correctness invariant.
- Multiple device sessions are supported.
- Logout and logout-all have clear semantics.
- Password reset and account disablement can terminate refresh authority.
- Session lifetime is bounded by both absolute and inactivity expiration.
- PostgreSQL remains the durable authority without introducing unnecessary session infrastructure.

## Negative

- Session and token behavior requires multiple cooperating components.
- Refresh operations require durable database access.
- Rotation requires transaction and concurrency controls.
- Replay handling adds lifecycle complexity.
- Short-lived access JWTs may remain usable until expiration after server-side session revocation.
- Token signing/verification key management becomes a security-critical operational concern.
- Session expiration and revocation behavior require extensive automated verification.

These trade-offs are accepted because the architecture balances request efficiency with server-controlled long-lived authentication authority.

---

# Risks

Primary risks include:

- Refresh credentials being persisted raw.
- Concurrent refresh requests producing multiple successors.
- Consumed refresh credentials being accepted again.
- JWT validation trusting token-controlled algorithms.
- JWT claims becoming overloaded with sensitive or stale security state.
- Access-token lifetimes becoming too long and weakening bounded revocation.
- Session expiration being accidentally renewable beyond the absolute lifetime.
- Revocation state becoming inconsistent with refresh state.
- PostgreSQL transaction logic failing to preserve single-use semantics.
- Implementation silently introducing request-time session lookups everywhere.
- Redis or another cache becoming authoritative session state without architecture review.
- Session/token secrets leaking through logs or telemetry.

These risks SHALL be mitigated through:

- One-way refresh credential persistence.
- Atomic refresh rotation.
- Concurrency tests.
- Replay tests.
- Strict JWT validation.
- Centralized security configuration.
- Short access-token lifetimes.
- Explicit session expiration checks.
- Secret-safe observability.
- PostgreSQL-backed integration testing.
- Architecture traceability during implementation review.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact Python class names.
- Exact module paths.
- Exact JWT library.
- Exact cryptographic signing algorithm or key representation where not otherwise frozen.
- Exact access-token lifetime.
- Exact session inactivity lifetime.
- Exact session absolute lifetime.
- Exact refresh credential byte length.
- Exact refresh digest implementation.
- Exact database locking primitive.
- Exact SQL indexes.
- Exact repository method names.
- Exact dependency-injection wiring.
- Exact migration decomposition.

Those are implementation decisions provided they preserve the frozen architecture.

The persistence implementation established by W4-S0C Package 6 refines the durable model around authentication sessions and refresh-token state. Released historical migrations remain immutable; Wave 4 schema evolution must use new Alembic revisions.

Any implementation proposal that replaces stateful refresh sessions with stateless refresh JWTs, stores raw refresh credentials, treats Redis as authoritative session persistence, or otherwise changes these responsibility boundaries requires formal architecture review.

---

# Verification

ADR-0011 governs the complete Wave 4 security verification and release gates.

At minimum, implementation of this ADR requires automated evidence for:

- Valid access JWT acceptance.
- Invalid signature rejection.
- Unexpected algorithm rejection.
- Issuer validation.
- Audience validation.
- Expiration validation.
- Required-claim validation.
- Minimal/secret-safe JWT claims.
- Session creation.
- Independent multi-session behavior.
- Current-session revocation.
- All-session revocation.
- Absolute session expiration.
- Inactivity expiration.
- Raw refresh credential absence from persistence.
- Successful refresh rotation.
- Predecessor invalidation after rotation.
- Refresh replay detection.
- Affected-session revocation after replay.
- Concurrent refresh consumption yielding at most one authoritative success.
- Revoked-session refresh rejection.
- Expired-session refresh rejection.
- Password-reset session revocation.
- Password-replacement session consequences required by the final lifecycle architecture.
- Account-disable session revocation.
- Privilege/security-state invalidation behavior where applicable.
- Fail-closed persistence and cryptographic failure handling.
- Secret exclusion from logs, errors, and telemetry.
- PostgreSQL-backed session persistence behavior.

Concurrency-sensitive refresh behavior SHALL be tested against the real persistence semantics required by the architecture rather than being considered proven solely through mocked unit tests.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P3-01` through `ARC-P3-29`.

It SHALL be interpreted together with later frozen Wave 4 refinements, particularly the credential-lifecycle session-revocation rules.

It is constrained by:

- W4-S0C Package 1 — Security Domain & Principal Architecture.
- W4-S0C Package 2 — Credential & Password Architecture.
- W4-S0C Package 3 — Session & Token Architecture.
- W4-S0C Package 4 — Authentication Transport Architecture.
- W4-S0C Package 5 — Authorization & Policy Architecture.
- W4-S0C Package 6 — Persistence & Migration Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze and amendment ledger.

Any implementation that conflicts with the frozen session/token invariants requires formal architecture review rather than silent deviation.

---

# References

## Existing ADRs

- ADR-0001 — Adopt a Monorepo Repository Structure.
- ADR-0002 — Adopt FastAPI Application Factory Pattern.
- ADR-0003 — Adopt an Independent Backend Python Project.
- ADR-0004 — Authentication & Security Architecture.
- ADR-0005 — Credential Storage & Password Security.

## Wave 4 ADRs

- ADR-0007 — Authorization Model — Roles & Permissions.
- ADR-0008 — Browser Authentication Transport.
- ADR-0009 — Recovery & Verification Capability Architecture.
- ADR-0010 — Abuse Protection & Security Observability.
- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- W4-S0C Package 3 — Session & Token Architecture.
- W4-S0C Package 6 — Persistence & Migration Architecture.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.
