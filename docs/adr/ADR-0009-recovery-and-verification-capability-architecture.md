# ADR-0009 — Recovery & Verification Capability Architecture

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

Sentinel AI requires a secure credential lifecycle after a password has been established.

Users must be able to:

- Change a password while authenticated.
- Recover access when the current password is unavailable.
- Establish verified ownership of the email address used as the recovery channel.
- Replace compromised credentials.
- Terminate pre-existing refresh authority after credential replacement.
- Consume recovery and verification authority exactly once.
- Avoid exposing account existence through public recovery and verification workflows.

These operations are not interchangeable.

The canonical lifecycle is:

```text
                    PASSWORD CREDENTIAL
                           |
             +-------------+-------------+
             |                           |
             v                           v
      Authenticated Change        Unauthenticated Recovery
             |                           |
     current password                  email
             |                           |
             v                           v
       verify identity          issue recovery capability
             |                           |
             v                           v
        new password              prove possession
             |                           |
             +-------------+-------------+
                           |
                           v
                    replace credential
                           |
                           v
                    revoke sessions
                           |
                           v
                  fresh authentication
```

Secure email recovery also requires an important trust distinction:

```text
email address stored on account
              !=
verified ownership of that address
```

The mere presence of `users.email` is not sufficient evidence that the address can safely authorize credential recovery.

Wave 4 therefore requires explicit email-verification state and explicit verification capabilities.

This ADR records the durable decisions established by W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.

---

# Decision

Sentinel AI SHALL treat:

- Password enrollment.
- Authenticated password change.
- Password recovery/reset.
- Email verification.

as distinct security operations with explicit authority requirements and lifecycle consequences.

The canonical security chain is:

```text
Registration
    |
    v
Email Verification
    |
    v
Authentication
    |
    v
Session Lifecycle
    |
    v
Credential Change / Recovery
    |
    v
Session Revocation
    |
    v
Fresh Authentication
```

Password recovery and email verification SHALL use dedicated opaque, random, short-lived, purpose-constrained, single-use capabilities backed by durable server-side state.

Raw capability secrets SHALL NOT be persisted.

---

# Credential Lifecycle Separation

Password enrollment, password change, and password recovery SHALL remain distinct operations.

## Enrollment

Enrollment establishes a password credential where the relevant workflow permits credential establishment.

## Password Change

Password change is performed by an authenticated principal who also proves knowledge of the currently active password.

## Password Recovery

Password recovery is driven by a dedicated recovery capability and does not require possession of the current password.

The operations MAY share lower-level credential replacement primitives, but their authority checks and security semantics SHALL remain distinct.

---

# Authenticated Password Change

Password change SHALL require:

```text
Authenticated Principal
        +
Current Password
        +
New Password
        |
        v
Verify Current Credential
        |
        v
Validate New Password
        |
        v
Reject Current-Password Reuse
        |
        v
Hash With Current Configuration
        |
        v
Atomic Credential Replacement
        |
        v
Revoke Pre-Existing Sessions
        |
        v
Fresh Authentication
```

Possession of an access JWT alone is insufficient to replace the password.

The current password SHALL be reverified.

This provides an explicit reauthentication boundary for a high-value security operation.

---

# Canonical Password Policy

Every newly established password SHALL use the canonical password policy defined by the credential architecture.

This applies consistently to:

- Initial password establishment.
- Authenticated password change.
- Password reset after recovery.

Recovery SHALL NOT become a weaker path for establishing a password that normal registration or password change would reject.

Successful replacement SHALL hash the new password using the current password-hashing configuration.

---

# Current Password Reuse

Replacing the currently active password with the same password SHALL be rejected.

Wave 4 does not introduce speculative generalized password-history requirements.

The frozen requirement is specifically that the new credential must not simply reproduce the currently active password.

A broader password-history system requires separate architecture justification if introduced later.

---

# Password Replacement and Session Authority

Successful password replacement SHALL revoke all pre-existing authentication sessions for the user.

This applies to both:

- Authenticated password change.
- Password reset through recovery.

The selected security boundary is:

```text
Password Replaced
       |
       v
Revoke All Existing Sessions
       |
       v
Existing Refresh Authority Destroyed
       |
       v
Fresh Authentication Required
```

Wave 4 does not preserve the current session after password change.

This deliberately avoids special semantics such as:

```text
revoke all sessions except session X
```

and establishes a clean fresh-authentication boundary after credential replacement.

---

# Existing Access JWTs After Credential Replacement

Credential replacement SHALL immediately destroy refresh authority by revoking the pre-existing authentication sessions.

It SHALL NOT introduce a database session lookup into every ordinary access-JWT-authenticated request solely to make password replacement invalidate already-issued access JWTs immediately.

Therefore:

```text
credential replacement
        |
        +--> refresh/session authority: revoked immediately
        |
        +--> existing access JWT:
             remains bounded by short stateless expiration
```

This preserves the ordinary-request efficiency architecture established by ADR-0006.

The short access-token lifetime remains the bound on residual already-issued access authority.

---

# Password Recovery Initiation

The recovery initiation operation is public.

Conceptually:

```text
POST /api/v1/auth/password/recovery
```

Its responsibility is to request issuance and delivery of narrowly scoped password-recovery authority.

It does not itself replace a password.

Recovery initiation SHALL resist identity enumeration.

The following internal states SHALL NOT produce externally distinguishable account-discovery behavior:

- Identity exists.
- Identity does not exist.
- User has no applicable password credential.
- Account is not recovery-eligible.
- Recovery cannot be issued for another internal eligibility reason.

The external response SHALL remain neutral.

Conceptually:

```text
202 Accepted

"If the account is eligible, recovery instructions will be sent."
```

Exact response prose is an API-schema implementation concern.

---

# Recovery Eligibility

Internally, recovery capability issuance requires the applicable security conditions, including:

```text
user exists
AND account permits recovery
AND verified recovery address exists
AND credential/recovery state is eligible
```

External anti-enumeration behavior remains independent of this internal eligibility decision.

The system MAY internally classify and observe the actual reason for non-issuance without exposing that reason through the public recovery contract.

---

# Recovery Capability

Password recovery SHALL use a dedicated opaque recovery capability.

The capability SHALL be:

- Cryptographically random.
- High entropy.
- Unguessable.
- Short-lived.
- Single-use.
- Purpose-constrained to password recovery.

It SHALL NOT be:

- A normal access JWT.
- A refresh credential.
- A user UUID.
- An encoded email address.
- A session identifier.

Conceptually:

```text
Cryptographically Secure Random Secret
                 |
                 +--> raw value -> delivery to user
                 |
                 v
         one-way digest
                 |
                 v
           PostgreSQL
```

Recovery authority is server-controlled and explicitly consumable.

---

# Recovery Capability Persistence

Only a one-way representation of the recovery capability SHALL be persisted.

The raw recovery secret exists only within the minimum required lifecycle:

```text
generation
    |
    v
delivery
    |
    v
user presentation
```

The conceptual persistence model is:

```text
password_recovery_tokens
├── id
├── user_id
├── token_digest
├── created_at
├── expires_at
├── consumed_at
└── revoked_at
```

Semantic timestamps represent lifecycle state.

A recovery capability is usable only when the authoritative state indicates that:

```text
digest matches
AND consumed_at IS NULL
AND revoked_at IS NULL
AND now < expires_at
AND account remains recovery-eligible
```

The exact SQLAlchemy model, indexes, constraints, and migration decomposition remain implementation concerns constrained by these semantics.

---

# Recovery Capability Supersession

Issuing a new recovery capability SHALL invalidate older outstanding recovery capabilities for the same applicable account/recovery context.

This prevents multiple independently valid outstanding recovery links from accumulating unnecessarily.

Historical security state MAY remain durably represented rather than being deleted.

The architecture therefore supports explicit revocation state.

---

# Recovery Expiration

Recovery capabilities SHALL expire.

The recovery TTL SHALL be centralized security configuration.

Exact numeric lifetime is intentionally not frozen by this ADR.

Endpoint-local or service-local hard-coded recovery lifetimes are prohibited.

---

# Atomic Recovery Completion

Password recovery completion is a security-critical multi-state transition and SHALL execute atomically.

Conceptually:

```text
BEGIN

Validate Recovery Capability
        |
        v
Lock / Enforce Single Consumption
        |
        v
Validate New Password
        |
        v
Hash New Password
        |
        v
Replace Credential
        |
        v
Consume Recovery Capability
        |
        v
Revoke Pre-Existing Sessions
        |
        v
Invalidate Applicable Outstanding Recovery Authority

COMMIT
```

A failure in the authoritative transition SHALL NOT leave a state where, for example:

- The password changed but the recovery capability remains reusable.
- The capability was consumed but credential replacement did not complete.
- Sessions remain refreshable after successful password replacement.
- Concurrent requests both establish authoritative successor state.

The exact database locking primitive is an implementation concern.

The atomicity invariant is not.

---

# Single-Use and Concurrency

Recovery capability consumption SHALL succeed at most once.

For concurrent presentation of the same valid capability:

```text
same capability
      |
      +--> request A
      |
      +--> request B
```

the authoritative result SHALL satisfy:

```text
successful consumptions <= 1
```

Application-level pre-checks alone are insufficient evidence of this invariant.

Persistence and transaction semantics SHALL enforce the single-use property under concurrency.

---

# Recovery Replay

Presentation of an already consumed recovery capability SHALL be denied.

Replay SHALL be observable as a security-relevant event according to ADR-0010.

Recovery replay SHALL NOT automatically disable the entire account merely because a consumed capability was presented again.

The architecture distinguishes:

```text
deny and observe suspected replay
```

from:

```text
automatically disable account
```

The latter is not part of the Wave 4 baseline.

---

# Verified Recovery Channel

Email-based password recovery SHALL require previously verified ownership of the recovery address.

The existence of an email address on the user record is not sufficient recovery authority.

The architecture therefore requires explicit evidence:

```text
users.email_verified_at
```

with semantics:

```text
NULL
    -> email ownership not verified

timestamp
    -> email ownership established at that time
```

A redundant `email_verified` boolean SHALL NOT be introduced as the canonical verification state.

---

# Verification State and Account State

Email-verification state and general account status are separate security facts.

Conceptually:

```text
account_status
    -> administrative / account eligibility state

email_verified_at
    -> evidence of email ownership
```

The system SHALL NOT overload general account status merely to represent email verification unless a future architecture explicitly changes the lifecycle model.

---

# Email Verification Requirement for Password Login

Wave 4 password authentication SHALL require a verified primary email.

The baseline lifecycle is:

```text
Registration
    |
    v
Account Created
    |
    v
Email Verification Required
    |
    v
Email Verified
    |
    v
Password Authentication Eligible
```

Authentication failure disclosure remains governed by the generic authentication contract.

The public login flow SHALL NOT become an account-enumeration mechanism by exposing detailed verification or identity state unnecessarily.

---

# Email Verification API

Secure email recovery requires explicit email-verification operations.

Wave 4 therefore adds:

```text
POST /api/v1/auth/email/verification
POST /api/v1/auth/email/verify
```

Conceptually:

```text
POST /email/verification
        |
        v
request / resend verification capability
        |
        v
enumeration-resistant external response
```

and:

```text
POST /email/verify
        |
        v
present verification capability
        |
        v
atomically consume capability
        |
        v
set email_verified_at
```

Successful email verification SHALL NOT automatically authenticate the user.

Registration, verification, and authentication remain separate security ceremonies.

---

# Verification Capability

Email-verification capabilities SHALL use the same core security primitives as recovery capabilities:

- Opaque random secret.
- High entropy.
- Digest-only persistence.
- Short expiration.
- Single use.
- Atomic consumption.
- Purpose constraint.
- Explicit invalidation/revocation state where required.

However, verification and recovery authority SHALL remain semantically distinct.

A verification capability cannot authorize password reset.

A recovery capability cannot establish arbitrary email ownership.

---

# Explicit Capability Persistence

Wave 4 SHALL use explicit persistence concepts for email verification and password recovery.

Conceptually:

```text
email_verification_tokens
password_recovery_tokens
```

The baseline SHALL NOT introduce a premature generic table such as:

```text
security_tokens
    purpose = EMAIL_VERIFICATION | PASSWORD_RECOVERY | ...
```

merely because the capabilities share some mechanical properties.

Their lifecycle semantics remain explicit and independently evolvable.

---

# Email Verification Persistence

The conceptual verification persistence model is:

```text
email_verification_tokens
├── id
├── user_id
├── token_digest
├── created_at
├── expires_at
├── consumed_at
└── revoked_at
```

Issuing a new verification capability SHALL invalidate prior outstanding verification capabilities for the applicable user/address context.

Verification capability consumption SHALL satisfy the same at-most-once concurrency invariant required for recovery capabilities.

---

# Atomic Verification Completion

Successful verification conceptually executes:

```text
BEGIN

Validate Verification Capability
        |
        v
Atomically Consume Capability
        |
        v
users.email_verified_at = now()
        |
        v
Invalidate Applicable Outstanding Verification Capabilities

COMMIT
```

The operation SHALL NOT establish an authenticated session merely because verification succeeded.

---

# Existing User Migration

Wave 4 migration SHALL NOT fabricate email-verification evidence.

For pre-Wave-4 users:

```text
email_verified_at = NULL
```

unless authoritative evidence of prior verification actually exists.

A migration timestamp is not proof that the user controlled the email address.

Historical released migrations remain immutable.

The new verification state and capability persistence SHALL be introduced through new Wave 4 Alembic revisions.

---

# Delivery Abstraction

Recovery and verification delivery SHALL use an infrastructure abstraction.

Application/security workflow code SHALL NOT directly embed provider-specific delivery concerns such as:

- SMTP connection handling.
- Provider API calls.
- Provider-specific templates.
- Delivery transport configuration.

Conceptually:

```text
Recovery / Verification Service
              |
              v
       Delivery Port
              |
              v
    Email Provider Adapter
```

The exact email provider is outside this ADR.

---

# Transaction Boundary and External Delivery

External delivery calls SHALL NOT execute as though they were part of the authoritative database transaction.

A remote email provider cannot participate in the PostgreSQL transaction with equivalent rollback semantics.

The architecture SHALL therefore preserve a truthful boundary between:

```text
authoritative durable security transition
```

and:

```text
external delivery side effect
```

Implementation planning SHALL define the reliable coordination mechanism without pretending a remote provider call is transactionally atomic with the database.

This ADR does not freeze the exact delivery reliability mechanism.

---

# Capability Exposure

Verification and recovery capabilities SHALL NOT be echoed in API responses.

Raw capabilities are delivered only through the designated delivery workflow and later accepted only by their dedicated capability-consumption endpoints.

They SHALL NOT be included in:

- Normal API response representations.
- Logs.
- Security-event payloads.
- Analytics.
- Telemetry.

---

# Capability-Bearing URLs

Browser recovery and verification workflows may necessarily carry a raw capability in a user-facing URL.

This creates leakage risks through:

- Browser history.
- Referrer headers.
- Analytics.
- Reverse-proxy logs.
- Unrelated third-party resources.

The backend architecture therefore requires that:

- Capabilities are accepted only by their dedicated endpoints.
- Capabilities are never echoed back.
- Capability secrets are excluded from logs and telemetry.

Frontend handling of capability-bearing URLs SHALL avoid unnecessarily propagating those URLs to unrelated origins and should exchange the capability promptly.

Detailed frontend implementation belongs to the corresponding frontend architecture.

---

# Secret-Safe Logging

Credential and capability secrets are prohibited from application and security log payloads.

This applies even during exception handling.

Prohibited values include:

- Plaintext passwords.
- Password hashes.
- Raw recovery capabilities.
- Raw email-verification capabilities.
- Reusable authentication credential material.

Security observability is governed by ADR-0010 and SHALL preserve this secret boundary.

---

# Abuse-Protection Dependency

Public credential, verification, and recovery workflows are abuse targets.

The relevant public security surface includes operations such as:

```text
/register
/login
/email/verification
/email/verify
/password/recovery
/password/reset
```

These workflows SHALL NOT receive Wave 4 production approval without the abuse controls defined by ADR-0010 / W4-S0C Package 9.

This includes protection against concerns such as:

- Credential guessing.
- Enumeration.
- Recovery flooding.
- Verification flooding.
- Capability abuse.
- Resource exhaustion.

Exact abuse-control mechanics are not defined by this ADR.

---

# Authentication API Surface Amendment

W4-S0C Package 7 originally froze the baseline authentication/session API surface to six operations:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/logout-all
GET  /api/v1/auth/me
```

Package 8 identified a security dependency that requires credential-lifecycle and verified-recovery operations.

The Wave 4 security API surface is therefore explicitly extended with:

```text
POST /api/v1/auth/password/change
POST /api/v1/auth/password/recovery
POST /api/v1/auth/password/reset

POST /api/v1/auth/email/verification
POST /api/v1/auth/email/verify
```

The resulting candidate Wave 4 security surface contains eleven operations.

This is a controlled amendment, not a silent contradiction of the Package 7 freeze.

The authoritative amendment is:

```text
ARC-P7-22 Amendment 1

The baseline authentication/session surface remains
the six P7 operations.

Credential lifecycle and verified-recovery operations
defined by P8 extend the Wave 4 security API surface.
```

---

# Persistence Extension

The Wave 4 persistence model is extended conceptually to include:

```text
users
├── email_verified_at
│
├── user_credentials
│
├── authentication_sessions
│   └── session_refresh_tokens
│
├── user_roles
│   └── roles
│       └── role_permissions
│           └── permissions
│
├── email_verification_tokens
│
└── password_recovery_tokens
```

These additions SHALL be introduced through new Wave 4 Alembic revisions.

Historical released migration files SHALL NOT be rewritten to make these concepts appear to have existed previously.

---

# Credential Compromise Boundary

The complete recovery response to suspected credential compromise is:

```text
                    ACCOUNT COMPROMISE
                           |
                           v
                  Password Recovery
                           |
                    recovery proof
                           |
                           v
                    New Password
                           |
              +------------+------------+
              |            |            |
              v            v            v
       old credential   sessions    recovery token
          replaced       revoked       consumed
                            |
                            v
                     refresh authority
                          destroyed
                            |
                            v
                       LOGIN AGAIN
```

This establishes a coherent post-compromise boundary.

---

# Security Invariants

The following invariants are mandatory:

1. Enrollment, password change, and password recovery are distinct security operations.
2. Password change requires authentication plus current-password verification.
3. All newly established passwords use the canonical password policy.
4. Replacement with the currently active password is rejected.
5. Password replacement revokes all pre-existing sessions.
6. Recovery initiation is identity-enumeration resistant.
7. Recovery uses a dedicated opaque, random, short-lived, single-use capability.
8. Only recovery-token digests are persisted.
9. New recovery issuance invalidates older outstanding recovery capabilities.
10. Recovery TTL is centralized configuration.
11. Recovery completion is an atomic security transaction.
12. Recovery capability consumption succeeds at most once.
13. Recovery replay is denied and observed without automatic account disablement.
14. Email recovery requires previously verified email ownership.
15. Email ownership evidence uses `email_verified_at`.
16. Dedicated email-verification API operations support secure recovery.
17. Verification and recovery capabilities remain explicit persistence concepts.
18. Migration never fabricates verification evidence.
19. Wave 4 password login requires a verified primary email.
20. Verification/recovery delivery uses an infrastructure abstraction.
21. Password replacement does not introduce normal-request database lookups for existing access JWTs.
22. Credential and capability secrets are prohibited from logs.
23. Public credential/recovery endpoints require Package 9 abuse controls before production approval.
24. Successful password replacement always uses the current password-hashing configuration.
25. Verification and recovery capabilities are never echoed in API responses.
26. External delivery calls do not execute as though they were part of the database transaction.
27. Credential replacement immediately destroys refresh authority while existing access JWTs retain their bounded stateless lifetime.
28. Package 8 explicitly amends Package 7's API-surface freeze to add credential lifecycle and verification operations.

---

# Alternatives Considered

## Option A — Authenticated Password Change with Current-Password Verification

Require both an authenticated principal and successful verification of the currently active password before replacement.

### Advantages

- Establishes explicit reauthentication for a high-value operation.
- Reduces the impact of a stolen but unattended authenticated session.
- Preserves separation between session possession and credential replacement authority.

### Disadvantages

- Adds an additional user interaction.
- Requires credential verification during password change.

**Decision:** Accepted.

---

## Option B — Access Token Alone Authorizes Password Change

Allow any currently authenticated session to replace the password without current-password verification.

### Advantages

- Simpler user experience.
- Less credential verification work.

### Disadvantages

- A stolen authenticated session can directly replace the account credential.
- Weakens the security boundary around credential replacement.
- Conflicts with the frozen reauthentication requirement.

**Decision:** Rejected.

---

## Option C — Preserve Current Session After Password Replacement

Revoke other sessions while preserving the session performing the password change.

### Advantages

- User remains signed in.
- Avoids an immediate new login ceremony.

### Disadvantages

- Requires special trust semantics for one pre-existing session.
- Weakens the clean credential-replacement boundary.
- Creates additional exception logic around session invalidation.

**Decision:** Rejected for the Wave 4 baseline.

---

## Option D — Revoke All Pre-Existing Sessions After Password Replacement

Terminate all existing refresh authority after successful password change or reset and require fresh authentication.

### Advantages

- Establishes a simple and strong post-replacement boundary.
- Removes pre-existing long-lived session authority.
- Provides coherent compromise recovery semantics.
- Avoids special-case session preservation.

### Disadvantages

- User must authenticate again.
- All devices lose refresh authority.

**Decision:** Accepted.

---

## Option E — JWT Recovery Token

Represent password-recovery authority as a signed self-contained JWT.

### Advantages

- Can be validated cryptographically without a capability lookup.
- Familiar token format.

### Disadvantages

- Single-use consumption requires additional state anyway.
- Revocation requires server-controlled state.
- Replay detection requires state.
- Duplicates semantics already naturally represented by an opaque server-backed capability.

**Decision:** Rejected for Wave 4 recovery.

---

## Option F — Stateful Opaque Recovery Capability

Use a cryptographically random opaque secret whose digest and lifecycle state are persisted server-side.

### Advantages

- Natural single-use semantics.
- Explicit revocation.
- Explicit expiration.
- Atomic consumption.
- Replay detection.
- No trusted client-side recovery state.

### Disadvantages

- Requires durable persistence and transactional consumption.
- Requires capability lookup.

**Decision:** Accepted.

---

## Option G — Store Raw Recovery / Verification Tokens

Persist the raw capability value.

### Advantages

- Simple lookup.

### Disadvantages

- Database compromise directly reveals usable recovery authority.
- Violates the one-way secret-storage boundary.
- Unnecessarily increases impact of persistence disclosure.

**Decision:** Rejected.

---

## Option H — Treat Stored Email as Verified Recovery Authority

Permit password recovery merely because an email address exists on the user record.

### Advantages

- No email-verification lifecycle required.
- Smaller API and persistence surface.

### Disadvantages

- Stored address does not prove ownership.
- Creates an unjustified credential-recovery trust assumption.
- Weakens recovery security.

**Decision:** Rejected.

---

## Option I — Generic Security Capability Table

Store verification and recovery capabilities in one generalized `security_tokens` table distinguished by a purpose field.

### Advantages

- Reuses persistence structure.
- Fewer tables.

### Disadvantages

- Introduces a generic abstraction before future capability semantics are known.
- Can blur purpose-specific lifecycle rules.
- Makes security concepts less explicit.

**Decision:** Rejected for the Wave 4 baseline.

---

## Option J — Explicit Verification and Recovery Persistence

Use separate persistence concepts for email-verification and password-recovery capabilities.

### Advantages

- Security semantics remain explicit.
- Independent lifecycle evolution remains possible.
- Purpose confusion is reduced.
- Persistence mirrors the domain concepts.

### Disadvantages

- Some structural duplication.
- Additional repository/migration concepts.

**Decision:** Accepted.

---

## Option K — Automatically Mark Existing Users Verified During Migration

Set `email_verified_at` to the migration timestamp for pre-Wave-4 users.

### Advantages

- Existing users can immediately use verified-email recovery.
- Avoids a verification migration experience.

### Disadvantages

- Fabricates security evidence that does not exist.
- Treats migration execution as proof of email ownership.
- Violates the frozen evidence boundary.

**Decision:** Rejected.

---

## Option L — Perform Email Delivery Inside the Database Transaction

Call the external email provider while treating delivery as part of the credential/capability database transaction.

### Advantages

- Appears procedurally simple.

### Disadvantages

- External provider calls cannot participate in PostgreSQL rollback semantics.
- Holds security transactions open across network operations.
- Creates misleading atomicity assumptions.
- Couples persistence correctness to provider availability.

**Decision:** Rejected.

---

## Option M — Automatic Account Disablement on Recovery Replay

Disable the account whenever an already-consumed recovery capability is presented.

### Advantages

- Aggressive response to suspected abuse.

### Disadvantages

- Enables denial-of-service against users if stale links are replayed.
- Treats every replay as proof of account compromise.
- Exceeds the frozen Wave 4 response requirement.

**Decision:** Rejected.

---

# Consequences

## Positive

- Credential enrollment, change, and recovery have explicit authority boundaries.
- Password replacement requires fresh security proof appropriate to the workflow.
- All password-establishment paths use one canonical policy and current hashing configuration.
- Recovery does not reveal account existence.
- Recovery and verification capabilities are server-controlled, revocable, expiring, and single-use.
- Raw capability secrets are not stored.
- Concurrent capability consumption has an explicit at-most-one-success invariant.
- Email recovery is grounded in verified ownership rather than stored-address assumption.
- Existing users are not granted fabricated verification evidence.
- Password replacement destroys pre-existing refresh authority.
- Ordinary access-token requests remain locally verifiable without new session database lookups.
- Provider-specific delivery remains outside credential-domain logic.
- The P7 API-surface change is explicit and traceable.
- The architecture establishes a coherent post-compromise recovery boundary.

## Negative

- Wave 4 requires additional verification and recovery persistence.
- Existing pre-Wave-4 users may need to verify their email before using recovery.
- Password change logs the user out of all pre-existing sessions.
- Capability consumption requires transaction and concurrency controls.
- Recovery and verification require external delivery infrastructure.
- Delivery reliability must be coordinated without pretending external calls share database transaction semantics.
- Short-lived already-issued access JWTs remain usable until their bounded expiration after credential replacement.
- Public recovery and verification endpoints require abuse-control infrastructure before production approval.

These trade-offs are accepted because credential recovery is itself an authority-establishment mechanism and must receive security guarantees comparable to the authentication system it can replace.

---

# Risks

Primary risks include:

- Recovery initiation becoming an account-enumeration oracle.
- Recovery or verification secrets being stored raw.
- Multiple concurrent requests consuming one capability successfully.
- Older outstanding recovery capabilities remaining usable after newer issuance.
- Password replacement failing to revoke pre-existing refresh authority.
- Existing users being incorrectly marked verified during migration.
- Recovery being allowed against an unverified email address.
- Verification capability being confused with recovery authority.
- Provider calls being incorrectly treated as transactionally atomic.
- Capability-bearing URLs leaking through logs, analytics, referrers, or unrelated origins.
- Secrets appearing in exception logging.
- Public recovery/verification endpoints being deployed without abuse controls.
- Password reset bypassing the canonical password policy.
- Implementation adding ordinary request-time session lookups to compensate for access-token residual lifetime.

These risks SHALL be mitigated through:

- Enumeration-resistant public responses.
- Digest-only capability persistence.
- Expiration and revocation state.
- Atomic capability consumption.
- Real concurrency testing.
- Session revocation during credential replacement.
- Explicit `email_verified_at` evidence.
- Separate verification and recovery persistence concepts.
- Delivery abstraction and truthful transaction boundaries.
- Secret-safe logging and observability.
- P9 abuse controls.
- ADR-0011 verification and release gates.
- Architecture traceability for the P7 amendment.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact recovery capability byte length.
- Exact verification capability byte length.
- Exact digest algorithm where not otherwise frozen.
- Exact recovery TTL.
- Exact verification TTL.
- Exact SQL locking primitive.
- Exact SQL indexes.
- Exact Python class names.
- Exact module paths.
- Exact repository method names.
- Exact service names.
- Exact delivery provider.
- Exact delivery reliability mechanism.
- Exact email templates.
- Exact API response prose.
- Exact abuse-control thresholds.
- Exact migration decomposition.
- Exact frontend recovery/verification URL handling implementation.

Those are implementation decisions provided they preserve `ARC-P8-01` through `ARC-P8-28`.

Released historical migrations remain immutable.

Wave 4 schema evolution SHALL introduce verification state and capability persistence through new Alembic revisions.

Any implementation proposal that weakens capability single-use semantics, stores raw capability secrets, permits unverified-email recovery, preserves pre-existing refresh authority after credential replacement, or fabricates verification evidence requires architecture review.

---

# Verification

ADR-0011 governs the complete Wave 4 security verification and release gates.

At minimum, implementation of this ADR requires automated evidence for:

- Separation of enrollment, password change, and password recovery.
- Authentication requirement for password change.
- Current-password reauthentication.
- Canonical password-policy enforcement during change and reset.
- Current-password reuse rejection.
- Current password-hashing configuration on replacement.
- Revocation of all pre-existing sessions after password replacement.
- Immediate destruction of pre-existing refresh authority.
- Bounded residual access-JWT behavior without ordinary request-time session lookups.
- Enumeration-resistant recovery initiation.
- Recovery eligibility not leaking through the public contract.
- Cryptographically secure opaque recovery capability generation.
- Raw recovery capability absence from persistence.
- Recovery capability expiration.
- New recovery issuance invalidating older outstanding recovery authority.
- Successful recovery capability consumption.
- Recovery capability replay rejection.
- Recovery replay observability.
- Concurrent recovery consumption yielding at most one authoritative success.
- Atomic password-reset transition.
- Verified-email requirement for recovery.
- Correct `email_verified_at` semantics.
- Password-login verified-email requirement.
- Enumeration-resistant verification request behavior.
- Cryptographically secure opaque verification capability generation.
- Raw verification capability absence from persistence.
- Verification capability expiration.
- New verification issuance invalidating older outstanding verification authority.
- Successful verification capability consumption.
- Concurrent verification consumption yielding at most one authoritative success.
- Atomic verification-state transition.
- Verification success not implicitly creating an authenticated session.
- Recovery capability being unable to establish email verification.
- Verification capability being unable to authorize password reset.
- Pre-Wave-4 migration not fabricating verification evidence.
- Capability secrets absent from API responses.
- Credential/capability secrets absent from logs, errors, telemetry, and analytics.
- Delivery-provider abstraction boundary.
- External delivery not being treated as database-transaction atomic.
- P9 abuse controls on public credential/recovery/verification workflows.
- Persistence migration integrity for verification and recovery concepts.
- Correct implementation of the controlled P7 API-surface amendment.

Concurrency-sensitive capability behavior SHALL be tested against the real persistence semantics required by the architecture rather than being considered proven solely through mocked unit tests.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P8-01` through `ARC-P8-28`.

It also records the controlled Package 7 amendment:

- `ARC-P7-22 Amendment 1` — credential-lifecycle and verified-recovery operations extend the previously frozen six-operation authentication/session API surface.

It is constrained by:

- W4-S0C Package 1 — Security Domain & Principal Architecture.
- W4-S0C Package 2 — Credential & Password Architecture.
- W4-S0C Package 3 — Session & Token Architecture.
- W4-S0C Package 4 — Authentication Transport Architecture.
- W4-S0C Package 6 — Persistence & Migration Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze and amendment ledger.

Any implementation that conflicts with the frozen recovery, verification, credential-replacement, or capability invariants requires formal architecture review rather than silent deviation.

---

# References

## Existing ADRs

- ADR-0001 — Adopt a Monorepo Repository Structure.
- ADR-0002 — Adopt FastAPI Application Factory Pattern.
- ADR-0003 — Adopt an Independent Backend Python Project.
- ADR-0004 — Authentication & Security Architecture.
- ADR-0005 — Credential Storage & Password Security.
- ADR-0006 — Access Token & Stateful Refresh Session Architecture.
- ADR-0007 — Authorization Model — Roles & Permissions.
- ADR-0008 — Browser Authentication Transport.

## Wave 4 ADRs

- ADR-0010 — Abuse Protection & Security Observability.
- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- W4-S0C Package 6 — Persistence & Migration Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.
