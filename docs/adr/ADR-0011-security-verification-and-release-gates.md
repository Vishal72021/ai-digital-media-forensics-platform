# ADR-0011 — Security Verification & Release Gates

| Property | Value |
|----------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-26 |
| **Authors** | Forensix AI Engineering Team |
| **Decision Category** | Security Verification Architecture |
| **Supersedes** | None |
| **Superseded By** | None |

---

# Context

W4-S0C Packages 1 through 9 define Sentinel AI's Wave 4 authentication, authorization, credential, session, transport, recovery, abuse-protection, and security-observability invariants.

Those invariants are not sufficiently protected if they remain true only because the current implementation happens to behave correctly.

A security regression can preserve an endpoint's happy path while silently weakening:

- Password storage.
- JWT validation.
- Authorization.
- Session revocation.
- Refresh rotation.
- Recovery single-use semantics.
- Anti-enumeration.
- CSRF protection.
- CORS policy.
- Cookie security.
- Secret exclusion.
- Abuse controls.
- Durable audit consistency.
- Migration integrity.

Wave 4 therefore requires an explicit verification architecture.

The governing principle is:

> Critical security properties require automated regression evidence at the layer where those properties can actually be proven.

This ADR records the durable architecture decisions established by W4-S0C Package 10 — Security Verification & Testing Architecture.

Package 10 is frozen as:

```text
ARC-P10-01 -> ARC-P10-49
Architecture gates: 50/50 PASS
```

The package defines the testing architecture and release contract rather than every individual test implementation.

---

# Decision

Sentinel AI SHALL treat security verification as a first-class architecture responsibility and a release-blocking contract.

Verification SHALL use multiple layers:

```text
                         +---------------+
                         | Security E2E  |
                         +-------+-------+
                                 |
                     +-----------+-----------+
                     | API / Integration     |
                     +-----------+-----------+
                                 |
                  +--------------+--------------+
                  | Persistence / Concurrency   |
                  +--------------+--------------+
                                 |
             +-------------------+-------------------+
             | Unit / Domain / Cryptographic Tests  |
             +---------------------------------------+
```

Different security invariants SHALL be tested at the layer capable of proving them.

A mocked unit test SHALL NOT be treated as sufficient evidence for a PostgreSQL concurrency invariant.

An endpoint returning the expected status code SHALL NOT by itself prove the required security consequence.

A passing generic test command SHALL NOT replace the mandatory Wave 4 security verification matrix.

---

# Security Test Taxonomy

Security tests SHALL remain identifiable as a first-class verification category while participating in the normal backend test suite.

A conceptual organization is:

```text
tests/
├── unit/
│   └── security/
├── integration/
│   └── security/
├── api/
│   └── auth/
└── security/
```

The exact directories are implementation decisions.

The required conceptual categories are:

- Unit/domain/cryptographic verification.
- Persistence and concurrency verification.
- API contract verification.
- Integration verification.
- Adversarial/security regression verification.
- End-to-end verification where required.

Test organization SHALL make it possible to identify and execute security verification intentionally.

---

# Testing Foundation

Wave 4 SHALL establish a pytest-based backend testing foundation.

The baseline testing stack SHALL include:

- `pytest`.
- `pytest-asyncio`.
- HTTPX for HTTP/API testing.
- Appropriate database and infrastructure testing support.

The architecture does not require a large collection of overlapping testing frameworks.

Additional libraries MAY be introduced when they provide a demonstrated verification capability rather than merely duplicating existing tooling.

---

# Test Infrastructure Isolation

Automated security verification SHALL execute against controlled test infrastructure.

Tests SHALL NOT depend on:

- A developer's ordinary local database state.
- Production PostgreSQL.
- Production Redis.
- Real production secrets.
- A real email provider.
- Other uncontrolled production services.

Conceptually:

```text
Test
  |
  v
Isolated Application Configuration
  |
  v
Isolated Persistence / Cache / Delivery Dependencies
  |
  v
Deterministic Assertions
```

Application behavior tests SHALL remain self-contained.

External vulnerability databases or scanner update mechanisms may require controlled network access independently of application behavior tests.

---

# PostgreSQL Semantic Fidelity

PostgreSQL-specific security and persistence invariants SHALL be verified against PostgreSQL.

SQLite SHALL NOT be treated as authoritative proof for properties depending on:

- PostgreSQL transactions.
- Constraints.
- UUID behavior.
- Timezone-aware timestamps.
- Row locking.
- Concurrent token/capability consumption.
- Unique indexes.
- Other PostgreSQL-specific semantics.

SQLite MAY be used for unrelated convenience tests if implementation planning finds value in it, but it cannot substitute for PostgreSQL-backed evidence where the frozen architecture depends on PostgreSQL behavior.

---

# Database Test Independence

Security integration tests SHALL be independently repeatable.

The result of a security test SHALL NOT depend on state left by a previous test.

Acceptable implementation mechanisms may include:

- Transaction rollback.
- Per-test schemas/databases.
- Fixture-managed cleanup.
- Containerized ephemeral databases.

The exact isolation mechanism is not frozen.

The invariant is:

```text
test ordering
     |
     X
must not influence security outcome
```

---

# Password Hashing Verification

Password tests SHALL verify behavior rather than one fixed encoded hash string.

At minimum, tests SHALL prove:

```text
plaintext password -> stored hash
correct password    -> verifies
incorrect password  -> rejects
stored value        != plaintext
```

Tests SHALL NOT couple correctness to a single exact encoded hash output.

The suite SHALL preserve the security property rather than implementation-specific randomness or encoding details.

---

# Password Policy Verification

The canonical password policy SHALL receive boundary verification.

Coverage SHALL include defined behavior for cases such as:

```text
valid password       -> PASS
too short            -> FAIL
too long             -> FAIL
policy-invalid       -> FAIL
empty password       -> FAIL
Unicode edge cases   -> defined behavior
```

Policy consistency SHALL be verified across every credential-establishment path that exists in the final Wave 4 architecture, including:

- Registration.
- Authenticated password change.
- Password reset/recovery.
- Enrollment where applicable.

Password change verification SHALL also prove the dual-proof requirement:

```text
valid authentication + correct current password   -> allowed
valid authentication + incorrect current password -> denied
invalid authentication + correct password          -> denied
```

Password reuse rules SHALL receive explicit regression coverage.

---

# Secret Persistence Verification

Automated persistence-facing tests SHALL verify that raw credential and capability secrets are absent after issuance.

This includes, where applicable:

- Plaintext passwords.
- Raw refresh credentials.
- Raw recovery capabilities.
- Raw email-verification capabilities.

Only the one-way representations permitted by the frozen architecture may remain in persistence.

Successful workflow behavior is insufficient if raw secrets are also stored.

---

# Adversarial Access-Token Verification

Access-token verification SHALL include adversarial manipulation.

At minimum:

```text
valid signature             -> ACCEPT
modified payload            -> REJECT
modified signature          -> REJECT
expired token               -> REJECT
wrong issuer                -> REJECT
wrong audience              -> REJECT
unsupported algorithm       -> REJECT
missing required claims     -> REJECT
malformed token             -> REJECT
```

Accepted algorithms SHALL come from trusted configuration.

Tests SHALL guard against an implementation that accepts a token-controlled algorithm merely because the JWT header declares it.

Exact required claims remain governed by the frozen session/token architecture.

---

# Authorization Matrix Verification

Authorization SHALL be verified through explicit permission matrices containing both positive and negative decisions.

Conceptually:

| Principal state | Required permission | Expected result |
|---|---|---|
| Authenticated and permitted | Present | Allow |
| Authenticated but not permitted | Absent | Deny |
| Unauthenticated | — | Authentication failure |
| Malformed authentication | — | Authentication failure |

Where multiple roles contribute permissions, effective permission composition SHALL be tested.

Security verification SHALL also cover:

- Zero-role behavior.
- Zero-permission behavior.
- Unknown roles.
- Unknown permissions.
- Resource ownership predicates.
- Self-resource versus broader-resource authority.
- Multi-role permission composition.
- Fail-closed policy evaluation.

A single "administrator can access endpoint" test is not sufficient proof of the authorization architecture.

---

# Default-Deny Regression Protection

Protected operations SHALL explicitly exercise their authentication and authorization requirements.

Tests SHALL guard against accidental removal of security dependencies from protected routes.

Where practical, contract tests SHALL detect protected operations that no longer declare or enforce the required security boundary.

Security verification must ask both:

```text
Does authorized access work?
```

and:

```text
Does unauthorized access reliably fail?
```

---

# Registration Privilege Injection

Registration tests SHALL deliberately attempt client-side privilege injection.

Inputs may include forbidden authority fields such as:

```json
{
  "email": "user@example.com",
  "password": "example",
  "role": "admin",
  "permissions": ["*"]
}
```

Such input SHALL NOT result in client-selected authorization state.

Depending on the final request-schema policy, forbidden fields may be rejected outright or otherwise prevented from influencing authority.

The security invariant is that registration input cannot establish privilege.

---

# Refresh Rotation Verification

Refresh verification SHALL prove the complete state transition.

Conceptually:

```text
login
  |
  v
R1 issued
  |
  v
refresh(R1)
  |
  +--> R1 consumed
  +--> R2 issued
           |
           v
      refresh(R2)
           |
           +--> R2 consumed
           +--> R3 issued
```

Assertions SHALL cover both:

- External API behavior.
- Internal durable persistence state.

Testing only the returned HTTP response is insufficient.

---

# Refresh Replay Verification

Refresh replay tests SHALL prove more than rejection.

For example:

```text
R1 issued
  |
  v
R1 refreshed successfully
  |
  v
R1 replayed
  |
  +--> DENIED
  +--> required durable session consequence
  +--> required security observability
```

The suite SHALL verify the defensive consequences required by the frozen session and observability architectures.

A test asserting only a `401` response does not fully verify refresh replay handling.

---

# Concurrent Refresh Verification

Single-use refresh semantics SHALL be tested under actual concurrency.

Conceptually:

```text
                    R1
                   /  \
                  /    \
          Request A    Request B
              |            |
              +------|-----+
                     v

             EXACTLY ONE SUCCESS
```

The system SHALL NOT permit:

```text
A -> R2
B -> R3
```

from the same refresh generation.

Concurrency-sensitive refresh behavior SHALL be tested against the real persistence semantics required by the architecture.

---

# Recovery Concurrency Verification

Recovery capability single-use semantics SHALL also be tested under concurrency.

Conceptually:

```text
Recovery Capability T
       /       \
      /         \
 Reset A       Reset B
      \         /
       \       /
    exactly one authoritative
      credential replacement
```

The losing operation SHALL NOT overwrite the winner's password.

Sequential reuse tests are necessary but insufficient proof of this invariant.

---

# Verification Capability Concurrency

Email-verification capability consumption SHALL likewise preserve at-most-one authoritative consumption.

Concurrent and replayed consumption SHALL remain safe according to the frozen API contract.

Tests SHALL verify the resulting authoritative verification state, not merely one response code.

---

# Session Revocation Verification

Session-revocation tests SHALL use multiple independent sessions.

At minimum, the suite SHALL prove:

```text
logout
-> current session refresh authority unusable

logout-all
-> all of that user's session refresh authority unusable

password change
-> every pre-existing session unusable for refresh

password reset
-> every pre-existing session unusable for refresh
```

Where other frozen security-state transitions require session invalidation, those consequences SHALL also be verified.

---

# Cross-User Isolation

Security integration tests SHALL explicitly verify isolation between users.

Given:

```text
User A
User B
```

User A SHALL NOT be able to:

- Revoke User B's sessions.
- Change User B's credentials.
- Consume User B's recovery state through identifiers.
- Acquire User B's roles or permissions.
- Read User B's protected principal state without explicit authorization.

Cross-user isolation applies across:

- Credentials.
- Sessions.
- Recovery.
- Verification where applicable.
- Authorization state.

---

# Anti-Enumeration Verification

Anti-enumeration guarantees SHALL be protected by API-level equivalence tests.

Recovery and verification initiation tests SHALL compare states such as:

- Known identity.
- Unknown identity.
- Unverified identity.
- Ineligible account.

Assertions SHOULD compare externally observable properties such as:

- HTTP status.
- Response schema.
- Security-relevant headers.
- Other stable public contract behavior.

Tests SHALL guard against obvious identity-dependent response differences that would create an account-existence oracle.

---

# Timing Enumeration

Ordinary CI SHALL NOT rely on brittle wall-clock equality assertions such as:

```text
response times must differ by less than 2 ms
```

Perfect constant-time HTTP behavior is not realistic because database access, password hashing, scheduling, and infrastructure introduce variance.

Implementation SHOULD avoid obvious timing fast paths where practical.

Timing-sensitive side-channel analysis belongs to targeted security review rather than unstable ordinary CI thresholds.

---

# CSRF Verification

Cookie-authenticated state-changing operations covered by the browser transport architecture SHALL receive explicit CSRF negative-path testing.

At minimum:

```text
legitimate request             -> ACCEPT
missing required CSRF proof    -> REJECT
invalid CSRF proof             -> REJECT
hostile cross-origin request   -> REJECT
```

CSRF correctness SHALL be proven through behavior, not merely by inspecting configuration.

---

# CORS Verification

CORS tests SHALL inspect actual behavior and response headers.

At minimum:

```text
trusted origin
-> permitted according to configuration

untrusted origin
-> not granted credentialed CORS access

wildcard origin + credentials
-> forbidden configuration
```

Tests SHALL guard against configuration drift that broadens credentialed cross-origin access.

---

# Cookie Security Verification

Login, refresh, and logout transport tests SHALL verify the actual refresh-cookie contract.

Assertions SHALL cover the frozen transport semantics, including:

- `HttpOnly`.
- Production `Secure`.
- `SameSite`.
- Cookie `Path`.
- Expiry / `Max-Age` behavior.
- Compatible deletion behavior.
- Raw refresh credential absence from JSON.

The suite SHALL preserve the separation between access-token and refresh-token transport.

---

# Security Error Contract Verification

Security API tests SHALL verify canonical error contracts in addition to status codes.

Where applicable, cases include:

- `401`.
- `403`.
- `409`.
- `422`.
- `429`.

Assertions SHALL include:

- Canonical response envelope.
- Correct status.
- Stable error classification where frozen.
- No stack trace.
- No secret leakage.

---

# Secret-Leak Regression Testing

The security suite SHALL contain dedicated regression tests for secret leakage.

Recognizable test-only sentinel values SHOULD be injected, for example:

```text
SENTINEL_TEST_PASSWORD_...
SENTINEL_TEST_REFRESH_...
SENTINEL_TEST_RECOVERY_...
```

The test harness SHALL exercise relevant success and failure paths and inspect captured logs and error output.

Those recognizable secret values SHALL NOT appear.

Equivalent checks SHALL protect:

- Access JWTs.
- `Authorization` values.
- Credential-bearing response bodies.
- `Set-Cookie`.
- Recovery capabilities.
- Verification capabilities.
- Other reusable credential material.

Security review alone is not considered sufficient proof of this requirement.

---

# Durable Audit Transaction Verification

Tests SHALL verify transactional consistency between security-state changes and required durable audit events.

For a transition such as password replacement, successful verification should prove the complete state:

```text
credential replaced
+
required sessions revoked
+
durable audit event created
```

A forced transaction failure SHALL prove rollback consistency:

```text
credential replacement rolled back
session revocation rolled back
durable audit event absent
```

Where the application boundary intentionally exposes no ordinary audit mutation operations, verification SHOULD reinforce that append-oriented architecture where practical.

---

# Abuse-Control Verification

Rate-limit tests SHALL cover defined behavior:

```text
under limit       -> normal behavior
at boundary       -> defined behavior
over limit        -> 429 / applicable suppression behavior
window recovery   -> allowed again
```

Tests SHALL NOT wait real production-duration windows.

Time and limits SHALL be configurable or controllable for deterministic verification.

Multi-dimensional controls SHALL be tested.

Examples include:

```text
many identities from one source
-> network control eventually acts

one identity from many simulated sources
-> identity control eventually acts
```

This prevents the implementation from silently collapsing the layered P9 architecture into an IP-only mechanism.

---

# Enumeration-Safe Throttling

Abuse-control tests SHALL explicitly verify that throttling does not regress anti-enumeration guarantees.

Existing and unknown identities SHALL be exercised under throttled conditions.

Externally observable behavior SHALL NOT become an obvious account-existence oracle merely because identity-scoped abuse state exists.

---

# Delivery Suppression Verification

The following P9 invariant SHALL receive dedicated regression coverage:

```text
Recovery capability R1 is valid
        |
attacker floods recovery requests
        |
new delivery is suppressed
        |
R1 remains valid
```

unless an actual replacement capability is legitimately issued according to the frozen lifecycle architecture.

Delivery suppression SHALL NOT accidentally invalidate an existing valid recovery or verification capability.

---

# Abuse-Infrastructure Fault Injection

Once the exact degraded-mode policy is selected within the P9 implementation boundary, tests SHALL fault-inject abuse-infrastructure failures.

Scenarios SHALL include applicable failures such as:

- Store timeout.
- Connection failure.
- Atomic-operation failure.

Verification SHALL prove:

```text
documented degraded behavior
+
required security telemetry
```

and SHALL reject silent protection bypass.

---

# Controlled Delivery Testing

Automated recovery and verification tests SHALL NOT require a real email provider.

They SHALL use a controlled delivery adapter/test double.

Conceptually:

```text
Verification / Recovery Service
            |
            v
     Fake Delivery Adapter
            |
            v
      Captured Message
```

Test infrastructure MAY expose the raw test recovery or verification capability to the test harness so the workflow can continue.

That exception exists only inside controlled test infrastructure.

Production persistence and logging rules remain unchanged:

```text
production:
raw capability -> designated delivery only

test:
raw capability -> fake delivery capture -> test client
```

---

# Migration Verification

Wave 4 migration verification SHALL begin from the actual released Wave 3 persistence state.

It SHALL NOT be considered sufficient to test only:

```text
create_all(current_models)
```

The required model is:

```text
released v0.3.0 schema
        |
        v
Wave 4 Alembic upgrade
        |
        v
expected v0.4.0 schema
```

This preserves the architectural rule that released historical migrations remain immutable.

---

# Migration Data Preservation

Migration tests SHALL create representative Wave 3 data before applying Wave 4 migrations.

After upgrade, tests SHALL verify preservation of existing user data, including relevant properties such as:

- User identity.
- Email.
- Existing identifiers.
- Existing timestamps.

They SHALL also verify:

```text
email_verified_at = NULL
```

for pre-Wave-4 users unless genuine verification evidence exists.

Migration SHALL NOT fabricate email-verification evidence.

---

# Downgrade Verification

Alembic downgrade behavior SHALL be mechanically verified where the migration is designed to be reversible.

If a security migration is intentionally irreversible, that fact SHALL be documented explicitly.

The architecture does not require unsafe fake reversibility merely to satisfy a generic downgrade convention.

---

# OpenAPI Security Contract Verification

Generated OpenAPI SHALL be regression-tested against the frozen authentication API contract.

Verification SHALL include, where applicable:

- Bearer security scheme exists.
- Protected operations declare required security.
- Public operations do not accidentally require Bearer authentication.
- Expected response models are represented.

This protects against runtime/documentation security drift.

---

# Forbidden Public Schema Fields

Generated API schemas SHALL be checked for credential and security-internal leakage.

Public response contracts SHALL NOT expose fields such as:

- Password.
- Password hash.
- Raw refresh credential.
- Token digest.
- Credential internals.
- Recovery/verification secrets.
- Other prohibited security-internal state.

Schema regression tests are required because sensitive fields can leak through generated contracts even when one runtime response path happens not to return them.

---

# Property-Based Testing

Property-based testing MAY provide additional value for areas such as:

- Token parsing.
- Password input boundaries.
- Permission combinations.

It is not a mandatory Wave 4 release dependency.

The baseline SHALL first achieve deterministic security-invariant coverage.

No specific property-based testing library is frozen.

---

# Fuzzing

Dedicated fuzzing infrastructure is not a mandatory v0.4.0 release dependency.

Basic malformed-input and adversarial tests ARE mandatory.

Dedicated fuzz campaigns MAY be introduced in later security-hardening work without changing this ADR.

---

# Dependency Vulnerability Gate

Wave 4 release verification SHALL include automated dependency vulnerability analysis.

The exact scanner is not frozen.

The required invariant is:

```text
known dependency vulnerabilities
        |
        v
visible before release approval
```

Scanner/tool selection belongs to implementation/tooling planning.

---

# Repository Secret Gate

Repository and CI security gates SHALL include automated secret detection appropriate for preventing credential material from entering version control.

The gate SHALL address accidental inclusion of material such as:

- JWT private keys.
- Database credentials.
- Redis credentials.
- Email-provider secrets.
- Production environment values.
- Other credential material.

The exact secret-scanning product is not frozen.

---

# Static Quality Gates

Existing static quality controls such as:

- Ruff.
- MyPy.
- Pre-commit.

remain necessary.

They SHALL NOT be treated as substitutes for security testing.

A dedicated security static analyzer MAY be added if it produces useful signal.

Wave 4 does not require stacking security scanners merely for tool-count or badge value.

---

# Security-Invariant Coverage

Wave 4 SHALL NOT define security approval as a magical raw line-coverage percentage.

`100%` line coverage does not prove security correctness.

A test can execute a permission branch without proving its denial behavior.

Coverage metrics MAY be used to identify untested code, but release approval SHALL prioritize explicit security-invariant coverage.

---

# Mandatory Wave 4 Security Verification Matrix

Before v0.4.0 can receive release approval, the mandatory security matrix SHALL pass:

| ID | Verification Category |
|---|---|
| `SEC-01` | Password hashing |
| `SEC-02` | Password policy |
| `SEC-03` | Registration privilege isolation |
| `SEC-04` | Login failure behavior |
| `SEC-05` | JWT validation |
| `SEC-06` | Authentication dependency |
| `SEC-07` | Authorization matrix |
| `SEC-08` | Refresh rotation |
| `SEC-09` | Refresh replay |
| `SEC-10` | Concurrent refresh |
| `SEC-11` | Logout/session revocation |
| `SEC-12` | Logout-all |
| `SEC-13` | Password change |
| `SEC-14` | Password recovery |
| `SEC-15` | Recovery single-use |
| `SEC-16` | Concurrent recovery |
| `SEC-17` | Email verification |
| `SEC-18` | Enumeration resistance |
| `SEC-19` | CSRF |
| `SEC-20` | CORS |
| `SEC-21` | Cookie security |
| `SEC-22` | Error contracts |
| `SEC-23` | Secret leakage |
| `SEC-24` | Rate limiting |
| `SEC-25` | Delivery throttling |
| `SEC-26` | Abuse-store degradation |
| `SEC-27` | Security events |
| `SEC-28` | Durable audit |
| `SEC-29` | Migration integrity |
| `SEC-30` | OpenAPI security contract |
| `SEC-31` | Dependency vulnerability gate |
| `SEC-32` | Repository secret gate |

The release contract is an explicit security verification matrix, not merely an undifferentiated `pytest` pass.

---

# CI Verification Layers

CI SHALL separate fast developer feedback from infrastructure-backed security verification while requiring the complete mandatory suite before release.

The conceptual gates are:

```text
PR Gate
├── lint
├── format
├── type-check
├── unit tests
├── API tests
└── security regression tests

Integration Gate
├── PostgreSQL
├── Redis / abuse infrastructure where applicable
├── migrations
├── concurrency
└── fault injection

Release Gate
├── all previous gates
├── dependency security scan
├── secret scan
└── final security matrix
```

Exact GitHub Actions workflow names, job decomposition, caching, and runner configuration belong to implementation/operations work.

---

# Production-Safety Guardrails

Security test infrastructure SHALL include safeguards against destructive integration or migration operations running against production environments.

A test process SHALL NOT accidentally discover a production `DATABASE_URL` and apply migrations to it.

Where practical, test configuration SHALL actively reject unsafe production targets.

Equivalent safety controls SHOULD apply to other destructive or stateful infrastructure used by the security suite.

---

# Deterministic Security Time

Time-dependent security behavior SHALL be designed for deterministic verification.

This applies to behavior such as:

- Access-token expiry.
- Session expiry.
- Rate-limit expiry.
- Recovery expiry.
- Verification expiry.

Tests SHALL NOT rely on production-duration sleeps such as:

```text
sleep(901)
```

where a controllable/injectable time abstraction or short test configuration can verify the same invariant deterministically.

---

# Cryptographic Randomness and Testability

Production cryptographic randomness SHALL NOT be weakened merely to make tests predictable.

Production token/capability generation must remain cryptographically secure.

Tests SHOULD verify observable properties.

Where deterministic behavior is genuinely necessary, an explicitly test-scoped secure-token provider abstraction MAY be injected.

Testability SHALL NOT cause insecure deterministic generation to enter production security code.

---

# Security Test Helpers

Reusable test helpers are appropriate for operations such as:

- Create a verified user.
- Authenticate a user.
- Create a second session.
- Extract a capability from fake delivery.
- Grant a role.
- Grant a permission.
- Advance a test clock.

Helpers SHALL NOT hide the security assertion being tested.

A test for refresh replay, for example, should still visibly demonstrate the replay and required defensive consequence rather than reducing the entire security property to an opaque helper call.

---

# Negative and Adversarial Testing

Negative and adversarial cases are mandatory components of Wave 4 security verification.

Security tests SHALL intentionally ask:

```text
What must never work?
```

not only:

```text
Does the happy path work?
```

Every major security operation requires negative-path coverage appropriate to its threat model.

---

# Security Regression Policy

When a confirmed security defect can be safely and deterministically reproduced, remediation SHALL include a regression test.

The expected lifecycle is:

```text
security defect discovered
        |
        v
reproduce with failing automated test
        |
        v
fix implementation
        |
        v
test becomes permanent regression protection
```

This prevents previously fixed security failures from silently returning.

---

# Ordinary CI Network Independence

Ordinary application security CI SHALL NOT depend on:

- Email-provider availability.
- Third-party authentication-provider availability.
- General internet connectivity.
- External production Redis.
- Other uncontrolled production infrastructure.

Security application behavior tests remain self-contained.

Vulnerability-analysis tooling may use its own controlled update mechanism where necessary.

---

# Architecture-to-Test Traceability

Critical frozen security decisions SHALL be traceable to automated verification categories.

Examples include:

```text
ARC-P3-xx
    |
    v
SEC-08 / SEC-09 / SEC-10

ARC-P5-xx
    |
    v
SEC-07

ARC-P8-xx
    |
    v
SEC-13 -> SEC-18

ARC-P9-xx
    |
    v
SEC-23 -> SEC-28
```

The exact many-to-many traceability artifact may be refined during implementation planning.

The invariant is that critical architecture decisions can be followed through:

```text
Architecture Decision
        |
        v
Implementation
        |
        v
Automated Verification
```

---

# Release-Blocking Rule

Failure of a mandatory Wave 4 security verification gate SHALL block release approval.

The rule is:

```text
mandatory security gate fails
        |
        v
v0.4.0 CANNOT RELEASE
```

A failing mandatory gate SHALL NOT be bypassed merely because:

- The test is described as "probably flaky".
- The behavior "works locally".
- The endpoint succeeds manually.
- The failure is deferred until after merge.

The gate must be formally resolved before release approval.

This release-blocking rule is part of the Wave 4 definition of done.

---

# Security Invariants

The following P10 invariants are mandatory:

1. Security verification uses layered unit, persistence, integration, and end-to-end tests rather than one testing layer.
2. Security tests are identifiable as a first-class verification category.
3. Wave 4 uses a pytest-based asynchronous/API backend testing foundation.
4. Security tests execute against isolated test infrastructure and do not require production credentials/services.
5. PostgreSQL-specific security and persistence invariants are verified against PostgreSQL.
6. Security integration tests are independently repeatable and state-isolated.
7. Password tests verify hashing semantics without coupling to one fixed encoded hash.
8. Password-policy verification covers boundaries and all credential-establishment paths.
9. Raw credential and capability secrets are verified absent from persistence.
10. Access-token tests include adversarial claim, signature, algorithm, and expiry manipulation.
11. Authorization uses explicit positive/negative permission matrices.
12. Tests verify default-deny behavior and guard against missing security dependencies.
13. Registration tests attempt privilege injection and prove clients cannot select authority.
14. Refresh rotation is verified as both API behavior and durable state transition.
15. Refresh replay verification includes denial, durable consequences, and security observability.
16. Concurrent refresh proves one refresh generation cannot rotate successfully more than once.
17. Recovery capability consumption is tested under concurrency.
18. Session-revocation verification uses multiple independent sessions.
19. Cross-user isolation is explicitly verified.
20. Anti-enumeration is protected through API-level equivalence testing.
21. CI avoids brittle wall-clock equality assertions for enumeration resistance.
22. CSRF defenses receive negative integration testing.
23. Cookie tests verify transport attributes and access/refresh separation.
24. Security API tests verify canonical error contracts, not only status codes.
25. Recognizable test secrets are used to detect leakage into logs/errors.
26. Tests verify transactional consistency between security-state changes and required durable audit.
27. Abuse-control tests use deterministic/configurable time and limits.
28. Throttling tests explicitly preserve anti-enumeration.
29. Delivery suppression tests prove existing valid capabilities are not accidentally invalidated.
30. Abuse-infrastructure failures are fault-injected against the selected degraded-mode policy.
31. Recovery/verification tests use controlled delivery adapters rather than real providers.
32. Migration verification begins from the released Wave 3 persistence state.
33. Migration tests preserve existing data and do not fabricate verification evidence.
34. Supported downgrade behavior is tested; intentional irreversibility is documented.
35. Generated OpenAPI security declarations are regression-tested.
36. Public API schema tests prohibit credential/security-internal fields.
37. Property-based testing remains optional rather than release-mandatory.
38. Release verification includes automated dependency vulnerability analysis.
39. Repository security gates include automated secret detection.
40. Release approval prioritizes security-invariant coverage over raw line-coverage percentages.
41. The mandatory release gate contains the explicit `SEC-01` through `SEC-32` matrix.
42. CI separates fast feedback from infrastructure-backed verification while requiring the complete release suite.
43. Test infrastructure protects production environments from destructive test/migration execution.
44. Time-dependent security behavior is deterministically testable without production-duration waits.
45. Testability does not weaken production cryptographic randomness.
46. Negative and adversarial cases are mandatory.
47. Confirmed reproducible security defects receive permanent regression tests.
48. Critical frozen security decisions are traceable to automated verification categories.
49. Failure of a mandatory Wave 4 security gate blocks release approval.

---

# Alternatives Considered

## Option A — Rely Primarily on Manual Security Testing

### Advantages

- Low initial test implementation effort.
- Flexible exploratory investigation.

### Disadvantages

- Security regressions are easy to reintroduce.
- Results are not deterministic.
- Concurrency and migration behavior are difficult to reproduce consistently.
- Release evidence is weak.

**Decision:** Rejected as the Wave 4 verification model.

---

## Option B — API Integration Tests Only

### Advantages

- Tests realistic HTTP behavior.
- Simple conceptual suite.

### Disadvantages

- Does not directly prove cryptographic/domain behavior.
- Does not adequately prove persistence/concurrency invariants.
- Can miss internal state-transition failures.
- Makes failure diagnosis harder.

**Decision:** Rejected as the sole verification layer.

---

## Option C — Layered Security Verification

Use unit/domain, persistence/concurrency, API/integration, and security/end-to-end verification according to the invariant being proven.

### Advantages

- Matches tests to responsibility boundaries.
- Supports deterministic security regression.
- Provides real concurrency and persistence evidence.
- Improves architecture-to-test traceability.

### Disadvantages

- More infrastructure and suite organization.
- Some gates are more expensive to execute.

**Decision:** Accepted.

---

## Option D — SQLite as Authoritative Integration Database

### Advantages

- Lightweight.
- Fast.
- Easy local setup.

### Disadvantages

- Does not faithfully prove required PostgreSQL locking, constraint, UUID, transaction, timestamp, and concurrency semantics.

**Decision:** Rejected for PostgreSQL-dependent security invariants.

---

## Option E — Real PostgreSQL for Persistence-Sensitive Security Tests

### Advantages

- Verifies the actual persistence semantics the architecture depends on.
- Supports authoritative concurrency testing.
- Reduces production/test semantic drift.

### Disadvantages

- Requires test infrastructure.
- Slower than pure in-memory testing.

**Decision:** Accepted.

---

## Option F — Sequential Tests for Single-Use Credentials

### Advantages

- Easy to implement.
- Proves ordinary replay rejection.

### Disadvantages

- Cannot prove concurrent at-most-once consumption.
- Can miss race conditions that issue multiple successors or overwrite credentials.

**Decision:** Rejected as sufficient evidence.

---

## Option G — Real Email Provider in Automated Security Tests

### Advantages

- Exercises the actual provider.

### Disadvantages

- Adds network dependence.
- Introduces credentials and external availability.
- Makes tests slower and less deterministic.
- Risks sending real messages.

**Decision:** Rejected for ordinary automated verification.

---

## Option H — Controlled Delivery Adapter

### Advantages

- Deterministic.
- No external network or production credentials.
- Allows controlled workflow continuation.
- Preserves production secret-storage boundaries.

### Disadvantages

- Provider-specific integration still requires separate verification where needed.

**Decision:** Accepted.

---

## Option I — Fixed Wall-Clock Sleeps for Expiry Tests

### Advantages

- Simple implementation.

### Disadvantages

- Slow.
- Flaky.
- Makes CI impractical for production-duration security windows.

**Decision:** Rejected.

---

## Option J — Raw Line Coverage as Security Release Gate

### Advantages

- Easy single-number metric.
- Familiar CI reporting.

### Disadvantages

- Execution does not prove security assertions.
- Positive-path coverage can hide missing negative cases.
- Encourages metric optimization rather than invariant verification.

**Decision:** Rejected as proof of security.

---

## Option K — Explicit Security Verification Matrix

### Advantages

- Makes release requirements reviewable.
- Maps security domains to verification.
- Prevents a generic green test command from hiding missing security coverage.
- Supports architecture traceability.

### Disadvantages

- Requires maintenance as security architecture evolves.

**Decision:** Accepted.

---

## Option L — Allow Release With Known Mandatory Security Gate Failure

### Advantages

- Can reduce schedule impact.

### Disadvantages

- Makes the security release contract optional.
- Permits known regression into production.
- Undermines the architecture freeze.

**Decision:** Rejected.

---

# Consequences

## Positive

- Wave 4 security architecture gains an explicit automated proof contract.
- Security properties are verified at appropriate layers.
- PostgreSQL concurrency semantics receive real integration evidence.
- Refresh and recovery races become release-blocking concerns.
- Authorization receives explicit positive and negative matrices.
- Anti-enumeration receives regression protection.
- CSRF, CORS, and cookie transport receive behavior-level verification.
- Secret leakage receives dedicated sentinel-based tests.
- Durable audit consistency is tested transactionally.
- Abuse controls receive deterministic and fault-injected verification.
- Wave 3-to-Wave 4 migration integrity becomes part of release evidence.
- OpenAPI security contracts are protected from drift.
- Dependency and repository-secret risks enter the release gate.
- Architecture decisions become traceable to implementation and tests.
- Future security bugs become permanent regression tests where reproducible.
- Mandatory security failures cannot be silently waived for v0.4.0.

## Negative

- The backend requires additional testing dependencies and infrastructure.
- CI requires PostgreSQL and applicable abuse-control infrastructure.
- Concurrency, migration, and fault-injection tests increase suite cost.
- Release approval becomes intentionally stricter.
- Test configuration requires production-safety safeguards.
- Security fixtures/helpers require disciplined design.
- Some implementation boundaries must support controllable time and test adapters.
- The security matrix requires ongoing maintenance as architecture evolves.

These costs are accepted because security architecture without repeatable verification would leave critical invariants vulnerable to silent regression.

---

# Risks

Primary risks include:

- Over-relying on mocked tests for persistence-sensitive security behavior.
- Using SQLite as false proof of PostgreSQL concurrency correctness.
- Testing only happy paths.
- Treating a status code as proof of a complete security transition.
- Missing concurrent refresh or recovery races.
- Failing to test cross-user isolation.
- Regressing anti-enumeration through response or throttling behavior.
- Assuming CSRF/CORS configuration is correct without negative behavior tests.
- Leaking credentials through logs while endpoint tests still pass.
- Testing only fresh schema creation and missing real upgrade failures.
- Fabricating verification evidence during migration.
- OpenAPI exposing security-internal fields despite runtime code appearing safe.
- Security tests accidentally connecting to production infrastructure.
- Long sleeps producing slow/flaky expiry tests.
- Weakening production randomness for test determinism.
- Treating line coverage as security assurance.
- Allowing a failing mandatory security gate to become normalized technical debt.

These risks SHALL be mitigated by the frozen P10 invariants and the mandatory release matrix in this ADR.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact test directory layout.
- Exact pytest fixture names.
- Exact fixture scopes.
- Exact PostgreSQL test-container mechanism.
- Exact database cleanup/isolation mechanism.
- Exact Redis test infrastructure.
- Exact concurrency orchestration primitive.
- Exact fake-delivery adapter class name.
- Exact clock abstraction.
- Exact token-provider abstraction.
- Exact helper function names.
- Exact dependency vulnerability scanner.
- Exact repository secret scanner.
- Exact optional static security analyzer.
- Exact coverage-reporting tool.
- Exact GitHub Actions workflow/job names.
- Exact CI runner topology.
- Exact test parallelization strategy.
- Exact property-based testing library.
- Exact future fuzzing infrastructure.
- Exact architecture-to-test traceability file format.

Those are implementation/tooling decisions provided they preserve `ARC-P10-01` through `ARC-P10-49`.

A proposal that replaces PostgreSQL-backed proof with SQLite for PostgreSQL-specific security invariants, removes mandatory concurrency verification, permits ordinary security CI to depend on production services, weakens cryptographic randomness for tests, or allows a mandatory security gate to fail without blocking release conflicts with this ADR.

---

# Verification of This ADR

Implementation compliance with ADR-0011 SHALL be demonstrated through the mandatory `SEC-01` through `SEC-32` verification matrix.

The final security-verification architecture must provide evidence for:

- Layered test execution.
- Isolated infrastructure.
- PostgreSQL semantic fidelity.
- Test independence.
- Password hashing and policy behavior.
- Secret persistence exclusion.
- JWT adversarial rejection.
- Authorization matrices and default-deny behavior.
- Registration privilege isolation.
- Refresh rotation, replay, and concurrency.
- Recovery single-use and concurrency.
- Verification capability behavior.
- Multi-session revocation.
- Cross-user isolation.
- Anti-enumeration.
- CSRF and CORS negative paths.
- Cookie security.
- Canonical error contracts.
- Secret leakage detection.
- Durable audit consistency.
- Layered rate limiting.
- Enumeration-safe throttling.
- Delivery suppression semantics.
- Abuse-store fault handling.
- Controlled delivery adapters.
- Wave 3-to-Wave 4 migration integrity.
- Data preservation and no fabricated verification evidence.
- Supported downgrade behavior.
- OpenAPI security declarations.
- Public-schema secret exclusion.
- Dependency vulnerability analysis.
- Repository secret scanning.
- Production-safety test guardrails.
- Deterministic time behavior.
- Secure cryptographic testability.
- Negative/adversarial coverage.
- Regression-test policy.
- Architecture-to-test traceability.
- Release blocking on mandatory gate failure.

Functional endpoint success alone is insufficient evidence of Wave 4 security compliance.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P10-01` through `ARC-P10-49`.

W4-S0C Package 10 passed all 50 architecture review gates.

It establishes the verification contract for the complete Wave 4 security architecture and SHALL be interpreted together with:

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
- W4-S0C Package 12 — Final Architecture Freeze.

W4-S0C Package 12 further establishes that mandatory P10 verification is part of the Wave 4 definition of done.

Any implementation that weakens the mandatory verification contract or release-blocking semantics requires formal architecture review rather than silent deviation.

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
- ADR-0009 — Recovery & Verification Capability Architecture.
- ADR-0010 — Abuse Protection & Security Observability.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
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
- W4-S0C Package 11 — Architecture Consolidation & ADR Set.
- W4-S0C Package 12 — Final Architecture Freeze.
