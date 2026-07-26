# ADR-0005 — Credential Storage & Password Security

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

Wave 4 introduces password-based authentication to Sentinel AI.

The persistent `User` established by earlier waves represents canonical application identity. Wave 4 must add password credentials without collapsing identity, credentials, authentication, and authorization into one model.

Password processing also creates a high-value cryptographic boundary. Plaintext passwords must be accepted from narrowly scoped request contracts, validated, transformed through an approved password-hashing mechanism, and removed from useful application scope without being persisted or exposed through unrelated layers.

The architecture must support:

- Secure one-way password storage.
- Separation between user identity and credential state.
- Centralized password hashing and verification.
- Password-policy evolution.
- Opportunistic hash upgrades.
- Dedicated credential persistence.
- Atomic initial credential creation.
- Distinct password-change and password-reset workflows.
- Fail-closed credential processing.
- Secret-safe logging and telemetry.

This ADR records the durable credential-storage and password-security decisions established by W4-S0C Package 2.

---

# Decision

Sentinel AI SHALL treat password credentials as a dedicated security domain separate from the persistent `User` identity.

The canonical responsibility flow is:

```text
Password Policy
      |
      | candidate acceptance
      v
Password Hasher
      |
      | cryptographic transformation
      v
Credential Service / Authentication Workflow
      |
      | lifecycle orchestration
      v
Credential Repository
      |
      | persistence
      v
PostgreSQL
```

Password verification establishes only whether supplied credential material matches stored credential state. It does not itself establish authorization.

Successful authentication continues through account-eligibility evaluation and principal establishment as defined by the broader Wave 4 security architecture.

---

# Credential and Identity Separation

The persistent `User` and password credential SHALL remain separate concepts.

Conceptually:

```text
User
├── id
├── email
├── account/security identity state
├── created_at
└── updated_at

PasswordCredential
├── credential identity
├── user_id
├── password_hash
└── credential metadata
```

The relationship is conceptually:

```text
User 1 ───────── 0..1 PasswordCredential
```

for the Wave 4 password-authentication baseline.

Password hashes SHALL NOT be added to the canonical user identity merely for implementation convenience.

This preserves the distinction:

```text
User        = persistent application identity
Credential  = authentication secret representation
Principal   = authenticated actor
```

Credential persistence models SHALL NOT serve as public API response models.

---

# Plaintext Password Handling

Plaintext passwords SHALL exist only for the minimum scope required to:

1. Validate bounded password input.
2. Evaluate the canonical password acceptance policy where applicable.
3. Hash a newly established password.
4. Verify a supplied password against an existing credential.

Conceptually:

```text
HTTP Request
     |
     v
Validated Password Input
     |
     v
Credential Security Boundary
     |
     ├── policy validation
     ├── hash
     └── verify
     |
     v
Password leaves useful application scope
```

Plaintext passwords SHALL NOT be:

- Persisted.
- Logged.
- Cached.
- Returned in API responses.
- Included in exceptions.
- Included in audit payloads.
- Included in telemetry.
- Stored in `Principal`.
- Stored in `AuthenticationContext`.
- Passed through unrelated repository or service boundaries.

Python does not provide a reliable guarantee that immutable string memory can be physically zeroized immediately. Sentinel AI therefore makes no false secure-zeroization guarantee.

The architectural guarantee is minimization of plaintext exposure, lifetime, and propagation.

---

# Password Hashing Algorithm

Sentinel AI SHALL use **Argon2id** as the Wave 4 password-hashing algorithm.

Conceptually:

```text
plaintext password
        |
        v
     Argon2id
        |
        ├── unique random salt
        ├── memory cost
        ├── time cost
        └── parallelism
        |
        v
encoded password hash
```

The encoded password-hash representation SHALL contain the algorithm metadata required by the selected maintained library for verification and policy evolution.

A separate application-managed salt column SHALL NOT be introduced merely to support ordinary Argon2id verification.

Sentinel AI SHALL NOT implement password cryptographic primitives itself.

A mature, maintained cryptographic/password-hashing library SHALL provide the underlying Argon2id implementation.

---

# Password Hashing Boundary

Password hashing SHALL be exposed through a dedicated application abstraction.

Conceptually, the boundary provides behavior equivalent to:

```text
hash(password)
verify(password, encoded_hash)
needs_rehash(encoded_hash)
```

The exact Python interface, class names, library adapter, and dependency-injection wiring are implementation details.

The rest of the application SHALL NOT independently:

- Construct Argon2id hashes.
- Parse password hashes for authentication decisions.
- Implement password comparison logic.
- Select alternative password algorithms.
- Duplicate password-hashing configuration.

This creates one authoritative cryptographic boundary.

---

# Hash Policy and Evolution

Argon2id parameters SHALL be centrally configured through the security configuration architecture.

The hash policy SHALL be evolvable as security guidance, infrastructure capacity, or application requirements change.

A credential encoded under an older accepted policy MAY be upgraded opportunistically after successful verification.

Conceptually:

```text
verify existing password
        |
        v
verification succeeds
        |
        v
needs_rehash?
    /       \
  no         yes
  |           |
  v           v
continue    hash using current policy
              |
              v
        replace stored hash
```

Opportunistic rehashing SHALL NOT require storing plaintext passwords beyond the already necessary successful-verification scope.

A failed verification SHALL NOT trigger a credential upgrade.

---

# Password Acceptance Policy

Password acceptance policy and password hashing are separate responsibilities.

The password policy determines whether a candidate password is acceptable.

The password hasher determines how an accepted password is transformed and later verified.

All operations that establish a new password SHALL eventually use the same canonical password policy, including:

- Registration.
- Authenticated password change.
- Password reset/recovery.
- Future password enrollment where applicable.

Password inputs SHALL receive reasonable bounded validation before expensive cryptographic processing.

The exact password bounds and policy parameters belong to the security/API configuration contract and implementation planning where they were not otherwise frozen.

This ADR SHALL NOT invent numeric password limits that were not frozen by W4-S0C.

---

# Credential Repository Boundary

Password credential persistence SHALL use a dedicated repository boundary.

Conceptually:

```text
CredentialRepository
├── retrieve credential state
├── create credential state
├── replace password hash
└── perform credential persistence operations required by lifecycle workflows
```

The repository owns persistence behavior.

It SHALL NOT decide whether a supplied plaintext password is correct.

Responsibility remains separated as:

```text
CredentialRepository  → persistence
PasswordHasher        → cryptographic transformation
Security Service      → workflow orchestration
Password Policy       → candidate acceptance
```

The existing `UserRepository` SHALL NOT absorb password hashing, verification, or credential lifecycle responsibilities.

---

# Initial Credential Establishment

Registration that establishes a password account SHALL create the canonical user identity and initial credential atomically with the other required registration security state.

Conceptually:

```text
Registration Request
       |
       v
Normalize / Validate Identity
       |
       v
Validate Password Policy
       |
       v
Hash Password
       |
       v
Atomic Persistence
 ┌──────────────────────┐
 │ User                 │
 │ Password Credential  │
 │ Required Auth State  │
 └──────────────────────┘
       |
       v
Registration Complete
```

The system SHALL NOT leave an unintended partially initialized password account when credential creation fails.

The exact transaction and persistence mechanics are governed by the Wave 4 persistence architecture.

---

# Password Verification

Password verification SHALL compare supplied credential material against the stored one-way password representation through the approved password-hashing boundary.

Verification success means only:

```text
supplied password matches stored credential
```

It does not mean:

```text
account is eligible
principal is established
request is authorized
```

Those remain separate security stages.

Credential processing SHALL fail closed.

Conditions such as:

- Unsupported stored hash.
- Malformed encoded hash.
- Credential lookup inconsistency.
- Cryptographic subsystem failure.
- Uncertain credential state.

SHALL NOT become authentication success.

---

# Authentication Failure Disclosure

Credential workflows SHALL avoid unnecessarily revealing whether a user identity exists.

Internally, the system may distinguish conditions such as:

```text
unknown identity
incorrect credential
credential infrastructure failure
```

Externally, authentication failure behavior SHALL follow the generic authentication contract established by the authentication API architecture.

Registration password-policy errors are different: when a user is establishing a credential, actionable policy-validation failures MAY be returned through the canonical validation/domain error contract.

Timing-sensitive anti-enumeration behavior is governed by the authentication workflow, abuse-protection, and security-verification architecture.

---

# Password Change and Password Reset

Password change and password reset SHALL remain distinct security workflows.

## Password Change

Password change is initiated by an authenticated actor and requires proof of the current password.

Conceptually:

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
Hash New Password
        |
        v
Atomic Credential Replacement
        |
        v
Session / Security Consequences
```

## Password Reset

Password reset is recovery-authority driven.

It does not require possession of the current password.

Conceptually:

```text
Recovery Authority
        +
New Password
        |
        v
Validate New Password
        |
        v
Hash New Password
        |
        v
Atomic Credential Replacement
        |
        v
Session / Security Consequences
```

The two workflows MAY share internal credential-replacement primitives, but they SHALL NOT be treated as the same security operation.

Recovery authority is governed by ADR-0009.

Session and revocation consequences are governed by ADR-0006 and the final Wave 4 credential-lifecycle architecture.

---

# Reversible Password Storage

Sentinel AI SHALL NOT provide any mechanism for recovering a user's existing plaintext password.

The following patterns are prohibited:

- Reversibly encrypted password columns.
- AES-encrypted password storage for later decryption.
- Password backup fields.
- Plaintext password persistence.
- Password recovery by revealing the previous password.

Forgotten credentials SHALL be handled by secure password replacement, not recovery of the old secret.

---

# Password Pepper

Wave 4 SHALL NOT require an application-level password pepper.

The selected baseline is:

```text
Argon2id
+
unique salts
+
centrally managed hash policy
+
protected production environment
```

A pepper would introduce additional secret-management, rotation, availability, and operational-recovery requirements that are not required by the frozen Wave 4 architecture.

A future threat-model change MAY introduce a pepper only through controlled architecture review and, where required, a superseding or amending ADR.

---

# Credential Lifecycle

The conceptual password-credential lifecycle is:

```text
┌─────────────────────┐
│ No Password         │
│ Credential          │
└──────────┬──────────┘
           |
           | establish
           v
┌─────────────────────┐
│ Active Password     │
│ Credential          │
└──────────┬──────────┘
           |
     ┌─────┴─────┐
     |           |
   change      reset
     |           |
     └─────┬─────┘
           v
┌─────────────────────┐
│ Replacement Active  │
│ Credential          │
└─────────────────────┘
```

Wave 4 does not introduce password history or generalized credential-versioning requirements merely for future extensibility.

Later credential-lifecycle architecture may impose additional rules on replacement operations without changing the one-way password-storage boundary defined here.

---

# Security Observability

Credential operations are security-relevant events.

Examples include:

- Password credential established.
- Password verification failed.
- Password changed.
- Password reset.
- Password hash upgraded.

However, security telemetry SHALL NEVER contain:

- Plaintext passwords.
- Password hashes.
- Reusable credential material.

This prohibition applies to:

- Application logs.
- Security events.
- Durable audit records.
- Exception payloads.
- Tracing attributes.
- Metrics labels.
- Analytics.
- Debug output where avoidable.

Detailed event taxonomy and durable audit policy are governed by ADR-0010.

---

# Security Invariants

The following invariants are mandatory:

1. Password credentials remain separate from persistent user identity.
2. Plaintext passwords exist only within the minimum required processing scope.
3. Plaintext passwords are never persisted, logged, returned, cached, or propagated into principal/authentication context.
4. Password cryptography is centralized behind a dedicated hashing abstraction.
5. Argon2id is the Wave 4 password-hashing algorithm.
6. Password cryptography uses a mature maintained library rather than custom primitives.
7. Hash policy is centrally configured and evolvable.
8. Password verification does not itself establish authorization.
9. Successful verification may opportunistically upgrade outdated hashes.
10. Password acceptance policy remains separate from password hashing.
11. Password inputs are bounded before expensive cryptographic work.
12. Authentication failures avoid unnecessary account-existence disclosure.
13. Credential persistence has a dedicated repository boundary.
14. Credential persistence models never become public API response models.
15. Initial user and credential establishment is atomic.
16. Password change and password reset remain distinct security workflows.
17. Password replacement triggers the session/revocation consequences defined by the session and credential-lifecycle architecture.
18. Existing passwords are never reversibly encrypted or recoverable.
19. Wave 4 does not require an application-level password pepper.
20. Credential-processing uncertainty fails closed.
21. Security telemetry never contains plaintext passwords or password hashes.

---

# Alternatives Considered

## Option A — Argon2id Behind a Dedicated Credential Boundary

Use Argon2id through a maintained library, centralize hash policy, isolate credential persistence from user identity, and support policy evolution through opportunistic rehashing.

### Advantages

- Strong memory-hard password hashing.
- Clear cryptographic ownership.
- Supports future hash-policy evolution.
- Prevents credential concerns from contaminating user identity.
- Supports independent testing.
- Supports future authentication methods without redesigning `User`.

### Disadvantages

- Introduces dedicated credential components and persistence.
- Password verification is intentionally computationally expensive.
- Requires operational tuning of Argon2id parameters.

**Decision:** Accepted.

---

## Option B — Store Password Hash Directly on `users`

Add `password_hash` directly to the existing `users` table and handle verification through user persistence logic.

### Advantages

- Fewer tables and repository abstractions.
- Simpler initial schema.

### Disadvantages

- Collapses identity and credential responsibilities.
- Encourages `UserRepository` to absorb authentication behavior.
- Makes future credential methods harder to model cleanly.
- Increases risk of credential fields leaking through ordinary user serialization.

**Decision:** Rejected.

---

## Option C — Reversible Password Encryption

Encrypt passwords so the original value can later be recovered.

### Advantages

- Original password can technically be retrieved.

### Disadvantages

- Sentinel AI has no legitimate requirement to retrieve existing passwords.
- Decryption-key compromise exposes all stored passwords.
- Violates the one-way credential-storage requirement.
- Creates unnecessary key-management risk.

**Decision:** Rejected.

---

## Option D — Custom Password Cryptography

Implement password hashing directly using generic hash primitives or custom cryptographic composition.

### Advantages

- Full implementation control.

### Disadvantages

- Unnecessary cryptographic risk.
- Duplicates mature security-library functionality.
- Makes policy evolution and review harder.
- Violates the frozen requirement to use maintained cryptographic primitives.

**Decision:** Rejected.

---

## Option E — Mandatory Application-Level Pepper

Require an additional application-managed secret for all password hashes.

### Advantages

- Adds a secret outside the credential database.

### Disadvantages

- Introduces secret-management and rotation complexity.
- Adds an availability dependency.
- Complicates operational recovery.
- Not required by the frozen Wave 4 threat model.

**Decision:** Rejected for the Wave 4 baseline.

---

# Consequences

## Positive

- User identity and password credentials remain cleanly separated.
- Password storage is one-way and based on Argon2id.
- Cryptographic behavior has one authoritative boundary.
- Password hash policy can evolve without redesigning credential storage.
- Successful authentication can upgrade stale hashes incrementally.
- Credential persistence cannot accidentally become ordinary user serialization.
- Registration can preserve transactional integrity.
- Password-change and recovery workflows retain distinct security semantics.
- Credential failures fail closed.
- Secret-handling requirements are explicit and testable.

## Negative

- Wave 4 requires dedicated credential persistence and repository/service abstractions.
- Argon2id introduces intentional CPU/memory cost that must be operationally tuned.
- Opportunistic rehashing adds controlled write behavior to successful credential verification.
- Atomic credential establishment requires transaction coordination across multiple persistence concerns.
- Credential lifecycle operations require integration with session revocation and security observability.

These trade-offs are accepted because password credentials form a high-value security boundary.

---

# Risks

Primary risks include:

- Plaintext password propagation beyond the credential boundary.
- Credential hashes leaking through ORM/API serialization.
- Incorrect or inconsistent Argon2id configuration.
- Excessive hashing work becoming a resource-exhaustion vector.
- Credential verification accidentally being treated as authorization.
- Partial registration creating identity without required credential state.
- Credential-processing failures being converted into authentication success.
- Logging or tracing accidentally capturing password material.

These risks SHALL be mitigated through:

- Dedicated password-policy and hashing boundaries.
- Bounded password input validation.
- Dedicated credential persistence.
- Atomic security transactions.
- Secret-safe observability.
- Abuse controls.
- Automated password and secret-leak regression tests.
- Architecture review for any change to the cryptographic boundary.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact Python class names.
- Exact module paths.
- Exact Argon2id numeric parameters.
- Exact password length bounds where not otherwise frozen.
- Exact maintained library selection.
- Exact repository method names.
- Exact dependency-injection wiring.
- Exact migration decomposition.

Those are implementation decisions provided they preserve this ADR and the frozen Wave 4 architecture.

The persistence model established later in W4-S0C refines the password credential relation into dedicated credential persistence. Historical released migrations remain immutable; Wave 4 changes must be introduced through new Alembic revisions.

---

# Verification

ADR-0011 governs the complete Wave 4 security verification and release gates.

At minimum, implementation of this ADR requires automated evidence for:

- Password hashing and verification semantics.
- Correct-password acceptance.
- Incorrect-password rejection.
- Hash output differing from plaintext input.
- Password-policy boundary behavior.
- Consistent policy application across credential-establishment paths.
- Current-password verification during password change.
- Password-reuse restrictions where required by the final lifecycle architecture.
- Absence of plaintext passwords from persistence.
- Absence of password hashes from public response contracts.
- Absence of plaintext passwords and password hashes from logs and error output.
- Opportunistic rehash behavior.
- Fail-closed handling of malformed or unsupported credential state.
- Atomic initial credential creation.
- Migration integrity for credential persistence.

Security tests SHALL validate behavior rather than hard-code one exact Argon2id encoded hash value.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P2-01` through `ARC-P2-21`.

It is constrained by:

- W4-S0C Package 1 — Security Domain & Principal Architecture.
- W4-S0C Package 2 — Credential & Password Architecture.
- W4-S0C Package 3 — Session & Token Architecture for password-replacement session consequences.
- W4-S0C Package 6 — Persistence & Migration Architecture for durable credential storage and transactions.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture for password change/reset semantics.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.

Any implementation that conflicts with `ARC-P2-01` through `ARC-P2-21` requires formal architecture review rather than silent deviation.

---

# References

## Existing ADRs

- ADR-0001 — Adopt a Monorepo Repository Structure.
- ADR-0002 — Adopt FastAPI Application Factory Pattern.
- ADR-0003 — Adopt an Independent Backend Python Project.
- ADR-0004 — Authentication & Security Architecture.

## Wave 4 ADRs

- ADR-0006 — Access Token & Stateful Refresh Session Architecture.
- ADR-0007 — Authorization Model — Roles & Permissions.
- ADR-0008 — Browser Authentication Transport.
- ADR-0009 — Recovery & Verification Capability Architecture.
- ADR-0010 — Abuse Protection & Security Observability.
- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- W4-S0C Package 2 — Credential & Password Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.
