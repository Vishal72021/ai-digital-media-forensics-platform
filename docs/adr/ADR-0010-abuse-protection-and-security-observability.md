# ADR-0010 — Abuse Protection & Security Observability

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

Sentinel AI's authentication and authorization architecture defines how legitimate security operations behave.

Correct authentication logic alone is not sufficient for a production security boundary.

The same operations can be deliberately abused through:

- Credential stuffing.
- Password guessing.
- Account enumeration.
- Registration flooding.
- Password-recovery flooding.
- Email-verification flooding.
- Refresh-token replay and repeated refresh abuse.
- Resource exhaustion.
- Distributed attacks.
- Identity-targeted denial of service.
- Log-based secret leakage.
- High-cardinality telemetry abuse.
- Undetected authorization attacks.

Wave 4 therefore requires a defensive control plane around authentication, authorization, credential lifecycle, and recovery.

The conceptual architecture is:

```text
                         HTTP Request
                              |
                              v
                     Request Context
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          Abuse Protection          Authentication
                 |                         |
                 |                         v
                 |                    Authorization
                 |                         |
                 +------------+------------+
                              |
                              v
                       Security Events
                         /          \
                        /            \
                       v              v
               Operational       Durable Audit
                Telemetry         Persistence
                       |
                       v
                 Metrics / Logs
                       |
                       v
                 Wave 8 Alerting
```

This ADR records the durable architecture decisions established by W4-S0C Package 9 — Abuse Protection & Security Observability.

---

# Decision

Sentinel AI SHALL implement layered abuse protection and structured security observability as first-class security architecture.

Abuse protection SHALL NOT rely on one global request counter.

Security evaluation MAY combine:

```text
network identity
        +
normalized identity
        +
endpoint / operation
        +
session
        +
capability fingerprint
        |
        v
Abuse Decision
   /    |    \
  v     v     v
Allow  Delay  Deny
```

Production abuse-control state SHALL use shared ephemeral infrastructure capable of atomic distributed accounting.

Operational telemetry and durable security audit SHALL remain distinct concepts.

Security secrets SHALL be excluded from both.

---

# Protected Security Surface

At minimum, abuse controls apply to the security-sensitive operations represented by:

```text
POST /auth/register
POST /auth/login
POST /auth/refresh

POST /auth/password/change
POST /auth/password/recovery
POST /auth/password/reset

POST /auth/email/verification
POST /auth/email/verify
```

Authenticated logout operations MAY also receive normal platform rate limiting, but they are not equivalent credential-guessing surfaces.

Controls SHALL be selected according to the threat characteristics of each operation rather than applying one identical counter everywhere.

---

# Layered Abuse Signals

Abuse protection SHALL support multiple independent dimensions.

Candidate dimensions include:

- Network identity.
- Network identity + operation.
- Privacy-preserving normalized identity.
- Identity + operation.
- Authentication session.
- Token/capability fingerprint.
- Endpoint/security operation.

Not every operation requires every dimension.

For example, login benefits from both:

```text
source network
      +
normalized login identity
```

because network-only controls can be bypassed through distributed sources, while identity-only controls can be weaponized to deny service to a known victim.

Layered controls SHALL therefore be used where the threat model requires them.

---

# Privacy-Preserving Identity Keys

Where an identity participates in an abuse-control key, raw identity values SHOULD NOT be placed directly into shared infrastructure keys where practical.

Conceptually:

```text
normalized email
      |
      v
privacy-preserving / keyed derivation
      |
      v
abuse-control identity key
```

This reduces unnecessary identity exposure through:

- Shared caches.
- Operational tooling.
- Debugging.
- Infrastructure inspection.
- Telemetry.

The exact derivation mechanism is an implementation decision constrained by the privacy requirement.

---

# Shared Ephemeral Abuse State

Production abuse-control state SHALL use shared ephemeral infrastructure.

It SHALL NOT use process-local memory as the authoritative distributed mechanism.

This pattern is insufficient:

```text
attempts[ip] += 1
```

because with multiple application replicas:

```text
Pod A
Pod B
Pod C
```

each process would otherwise maintain an independent budget.

Restarts would also erase process-local state.

Abuse counters also SHALL NOT be modeled as ordinary primary PostgreSQL persistence for every request merely to provide rate limiting.

The architectural responsibility is:

```text
durable security state
    -> PostgreSQL where defined by other ADRs

ephemeral distributed abuse state
    -> shared ephemeral infrastructure
```

The exact technology is not frozen by this ADR, though Redis-style shared ephemeral infrastructure is compatible with the architecture.

---

# Distributed Accounting Semantics

The selected abuse-control mechanism SHALL provide:

- Atomic distributed updates.
- Bounded sustained request rates.
- Bounded burst capacity.
- Automatic expiry/decay appropriate to the algorithm.
- Multi-instance consistency.

Token-bucket, sliding-window, or equivalent mechanisms MAY be used.

The ADR freezes behavioral guarantees rather than one algorithm or library.

A mechanism that allows multiple application replicas to independently grant full request budgets does not satisfy this architecture.

---

# Centralized Configuration

Abuse thresholds and windows SHALL be centrally configurable and independently tunable by security operation.

Conceptually:

```text
LOGIN_IP_LIMIT
LOGIN_IDENTITY_LIMIT

REGISTER_IP_LIMIT

RECOVERY_IP_LIMIT
RECOVERY_IDENTITY_LIMIT

VERIFICATION_IP_LIMIT
VERIFICATION_IDENTITY_LIMIT

REFRESH_LIMIT
```

The exact names and numeric values are not frozen.

Values such as:

```text
5 attempts / minute
10 requests / hour
```

SHALL NOT be scattered as endpoint-local constants.

Operational tuning must not require redesigning the architecture.

---

# Authentication Failure and Account Lockout

Repeated failed authentication SHALL trigger abuse resistance, not automatic administrative account disablement.

The baseline explicitly rejects:

```text
attacker knows victim identity
        |
        v
submit bad passwords repeatedly
        |
        v
victim account administratively disabled
```

as a normal anti-brute-force strategy.

Hard account disablement based solely on repeated authentication failure creates an identity-targeted denial-of-service primitive.

Administrative account status remains a distinct security state.

---

# Throttling Behavior

Repeated abuse MAY justify progressively stronger throttling.

However, throttling SHALL NOT intentionally occupy application workers through long request sleeps.

Patterns such as:

```text
await sleep(30)
```

for large numbers of abusive requests can themselves create resource exhaustion.

Explicit rejection with retry semantics is preferred over holding worker capacity unnecessarily.

---

# Rate-Limit Response Semantics

When an explicit rate limit is exceeded, the API SHALL use `429 Too Many Requests` semantics.

Where appropriate, a safe `Retry-After` value MAY be provided.

Responses SHALL NOT expose sensitive internal abuse state such as:

- Exact identity-specific attempt budgets.
- Internal scores.
- Counter keys.
- Whether an identity exists.
- Detailed defensive thresholds beyond what is intentionally public.

---

# Enumeration Resistance

Abuse controls SHALL preserve the anti-enumeration guarantees established by the authentication and recovery architecture.

The rate limiter itself must not become an identity oracle.

For example, this is prohibited:

```text
existing identity
    -> identity counter exists
    -> 429

unknown identity
    -> no identity counter
    -> neutral 202
```

when that externally distinguishable behavior would reveal account existence.

Identity-scoped abuse controls must be structured so that observable behavior does not trivially disclose whether the supplied identity maps to an account.

Internal security classification MAY remain richer than the external API response.

---

# Request Throttling and Delivery Throttling

Inbound request throttling and outbound delivery throttling are separate controls.

For recovery and email verification, the architecture distinguishes:

```text
Client Request
      |
      v
Request Abuse Control
      |
      v
Capability Workflow
      |
      v
Outbound Delivery Control
      |
      v
Email Provider
```

A request being allowed does not imply unlimited outbound email delivery.

This distinction protects against:

- Email bombing.
- Provider-cost abuse.
- Recovery flooding.
- Verification flooding.

---

# Suppressed Delivery and Existing Capabilities

Suppressing a new outbound delivery because of delivery throttling SHALL NOT automatically invalidate an already valid capability merely as a side effect of the delivery decision.

Capability lifecycle remains governed by the recovery/verification architecture.

Delivery throttling and capability validity are separate security concerns.

---

# Structured Security Events

Security-relevant transitions SHALL emit stable structured event types.

Security events SHOULD cover meaningful operations such as:

- Authentication success/failure.
- Rate-limit decisions.
- Refresh failure/replay.
- Password credential changes.
- Recovery requests and completion.
- Email verification activity.
- Session revocation.
- Authorization denial.
- Role/permission changes when those operations exist.
- Account-status changes.
- Abuse-store degraded mode.

Exact event names are an implementation concern, but the taxonomy SHALL be stable enough for machine processing and security investigation.

---

# Machine-Readable Telemetry

Security telemetry SHALL be structured and machine-readable.

The system SHALL NOT depend on parsing arbitrary human log prose to determine core security events.

Safe event structure may contain fields such as:

```text
event_type
timestamp
request_id / correlation_id
actor
subject
operation
outcome
safe failure classification
safe network context
safe resource category
```

Fields SHALL be governed by secret exclusion and data minimization.

---

# Internal and External Failure Classification

Internal security telemetry MAY distinguish failures more precisely than the public API.

For example, internally:

```text
unknown identity
wrong password
unverified identity
revoked session
expired session
replayed refresh credential
rate limited
```

may be useful classifications.

Externally, the API may intentionally collapse multiple conditions to preserve:

- Enumeration resistance.
- Security boundaries.
- Stable public contracts.

Observability SHALL NOT force internal diagnostic detail into public responses.

---

# Operational Telemetry vs Durable Audit

Wave 4 distinguishes two observability categories.

## Operational Security Telemetry

Used for:

- Logs.
- Metrics.
- Security-event streams.
- Investigation support.
- Alertable signals.

This category is designed for resilient/best-effort external delivery and operational analysis.

## Durable Security Audit

Used for high-value security state transitions that require historical accountability.

Examples include:

- Password replacement.
- All-session revocation where security-relevant.
- Role assignment/removal.
- Permission mutation.
- Administrative account-status changes.
- Other high-value authority transitions defined by the architecture.

These records require stronger persistence guarantees.

Operational telemetry SHALL NOT be treated as a substitute for durable audit where durable history is required.

---

# Append-Oriented Durable Audit

High-value security transitions SHALL create durable append-oriented audit records.

Normal application-domain workflows SHALL NOT mutate historical audit facts through ordinary:

```text
UPDATE security_audit_events
DELETE security_audit_events
```

operations.

Audit records represent historical security facts.

Retention, governance, archival, or legally required deletion are separate controlled concerns and do not convert audit into normal mutable domain state.

---

# Actor and Subject Semantics

Durable audit SHALL preserve the distinction between actor and subject.

For example:

```text
Admin A disables User B

actor   = Admin A
subject = User B
```

For a user changing their own password:

```text
actor   = User B
subject = User B
```

Anonymous security activity is valid.

Login, registration, recovery, and verification operations may occur before authentication, so:

```text
actor_user_id = NULL
```

MUST be representable where appropriate.

The audit architecture SHALL NOT pretend every security event has an authenticated actor.

---

# Correlation Identifiers

Security events SHALL carry correlation identifiers sufficient to connect related application and infrastructure activity.

Investigations must be able to follow an operation across relevant boundaries such as:

```text
HTTP request
     |
     v
application/security service
     |
     v
database transition
     |
     v
delivery infrastructure
     |
     v
security telemetry
```

Request IDs form the baseline.

Future distributed tracing MAY add trace identifiers without replacing the correlation requirement.

---

# Trusted Network Identity

Client-network identity SHALL be derived through trusted transport infrastructure.

Security services SHALL NOT blindly trust arbitrary client-supplied forwarding headers.

Deployments behind reverse proxies, gateways, or cloud ingress require explicit trusted-proxy boundaries before forwarded network information is treated as the client network identity.

Raw network data SHALL be normalized through the security/request-context boundary rather than scattered through application services.

---

# Client Metadata

Client-provided metadata such as `User-Agent` MAY support:

- Incident investigation.
- Session context.
- Abuse correlation.
- Operational analysis.

It remains untrusted client input.

It SHALL NOT become:

- An authentication factor.
- Proof of device identity.
- Trusted security authority.

Client metadata SHALL be bounded appropriately before storage or logging.

---

# Centralized Secret Redaction

Secret redaction is a cross-cutting observability requirement.

It SHALL NOT depend on every endpoint author remembering to redact individual fields.

At minimum, redaction/exclusion applies to:

- `password`.
- `current_password`.
- `new_password`.
- `Authorization`.
- Access tokens.
- Refresh credentials.
- Recovery capabilities.
- Verification capabilities.
- Authentication cookie values.
- `Set-Cookie` credential values.
- Other reusable credential material.

The policy applies across:

- Application logs.
- Exception logging.
- Generic request/response logging.
- APM instrumentation.
- Security telemetry.
- Audit metadata.
- Analytics.

---

# Credential Payload and Capability URL Logging

Authentication request bodies containing credential material SHALL NOT be dumped through generic request-body logging.

For example:

```json
{
  "email": "user@example.com",
  "password": "secret"
}
```

must not become ordinary log payload.

Capability-bearing URLs likewise require exclusion from generic logging because recovery or verification secrets may appear in them.

Authentication responses such as login and refresh also require protection because they contain access JWTs.

Generic middleware SHALL NOT indiscriminately log complete credential-bearing requests or responses.

---

# Security Metrics

Security observability SHOULD expose aggregate metrics such as:

- Authentication attempts.
- Authentication failures.
- Rate-limit decisions.
- Refresh failures.
- Refresh replay detections.
- Recovery requests.
- Verification requests.
- Authorization denials.
- Degraded abuse-control state.

Metric labels SHALL be:

- Bounded.
- Non-secret.
- Low cardinality.
- Operationally meaningful.

This is prohibited:

```text
auth_failures{email="user@example.com"}
```

Identity values, tokens, request IDs, and similarly unbounded identifiers SHALL NOT become routine metric labels.

---

# Alerting Boundary

Wave 4 SHALL emit security signals suitable for alerting.

Examples of potentially meaningful signals include:

- Sharp authentication-failure spikes.
- Refresh replay anomalies.
- Recovery-request spikes.
- Verification-request spikes.
- Authorization-denial surges.
- Rate-limit saturation.
- Abuse-store degraded mode.

Wave 4 does not own the final production alert-routing and escalation infrastructure.

That operational responsibility belongs primarily to Wave 8.

This ADR therefore freezes the production of alertable signals, not a particular pager, SIEM, escalation route, or on-call policy.

---

# Authorization Observability

Meaningful authorization denials SHOULD produce structured security telemetry.

Conceptually:

```text
principal
    |
    v
permission requirement
    |
    v
DENY
    |
    +--> 403 / applicable confidentiality semantics
    |
    +--> AUTHORIZATION_DENIED security event
```

Safe metadata MAY include:

- Principal identifier.
- Required permission identifier.
- Resource category.
- Request/correlation identifier.

Arbitrary resource contents SHALL NOT be dumped into security telemetry.

---

# Successful Authorization Audit Noise

Routine successful authorization checks SHALL NOT generate durable audit records by default.

Doing so would create high-volume low-value audit noise.

Ordinary request telemetry MAY represent normal successful request activity where needed.

Durable audit is reserved for security-relevant state transitions and high-value authority changes.

---

# External Observability Failure

Authentication and authorization SHALL NOT synchronously depend on an external logging/APM/telemetry vendor being available.

An external telemetry outage SHALL NOT directly become an authentication outage.

This rule applies to operational telemetry delivery.

It does not weaken the stronger consistency requirement for durable local security audit records where the architecture requires them.

---

# Transactional Audit Consistency

For transactional security-state changes requiring durable audit, the durable audit record SHALL be persisted consistently with the corresponding local state transition.

Conceptually:

```text
BEGIN

replace password
revoke sessions
insert durable security audit event

COMMIT
```

The architecture SHOULD NOT produce:

```text
security state committed
        |
        X
durable audit fact lost
```

where the transition is defined as requiring durable audit.

External log shipping or telemetry export occurs outside that local transactional guarantee.

---

# Audit Data Minimization

Durable audit does not mean storing complete request or object snapshots.

Audit payloads SHALL contain only information necessary to answer questions such as:

- What happened?
- When did it happen?
- Who initiated it, if authenticated?
- Who or what was affected?
- Which request/correlation context applies?
- What safe event classification applies?

Audit SHALL NOT contain:

- Passwords.
- Credential hashes.
- Raw access/refresh credentials.
- Recovery/verification secrets.
- Entire HTTP requests.
- Entire ORM objects.
- Arbitrary full exception objects.

---

# Ephemeral Abuse State vs Security History

Rate-limit state and security history are distinct.

A successful authentication MAY affect ephemeral throttling state according to the configured algorithm.

It SHALL NOT erase historical security telemetry describing prior failed attempts.

Conceptually:

```text
ephemeral throttle state
        !=
historical security evidence
```

Successful login does not make earlier attack activity cease to have occurred.

---

# CAPTCHA

CAPTCHA or equivalent interactive challenge mechanisms are not mandatory Wave 4 dependencies.

They MAY be introduced later as escalation controls if abuse evidence warrants them.

Wave 4 avoids requiring CAPTCHA because it introduces concerns such as:

- Third-party dependency.
- Accessibility.
- Frontend coupling.
- Privacy.
- Bot adaptation.

Adding an optional future challenge layer must preserve the frozen anti-enumeration and security boundaries.

---

# Browser Fingerprinting

Wave 4 SHALL NOT introduce invasive persistent browser fingerprinting as an authentication or abuse-control primitive.

Ordinary contextual signals MAY include:

- Network context.
- Bounded User-Agent metadata.
- Session identity.
- Request patterns.

Persistent cross-session fingerprinting is outside the baseline.

---

# Abuse-Store Failure and Degraded Mode

Failure of the shared abuse-control infrastructure SHALL follow an explicit degraded-mode policy.

The system SHALL NOT silently transform:

```text
abuse store unavailable
        |
        v
unlimited security requests
```

without observable security signaling.

At the same time, the architecture does not globally require pure fail-closed behavior that makes every authentication operation unavailable whenever the abuse store is unreachable.

Risk may differ by operation.

A bounded local emergency fallback MAY be used where implementation/operations design approves it, but such fallback SHALL NOT claim distributed guarantees.

The exact endpoint-specific degraded behavior is intentionally deferred to implementation/operations planning.

What is frozen is that degraded operation is:

- Explicit.
- Bounded according to the selected policy.
- Observable.
- Not silently equivalent to disabling protection.

---

# UTC Security Time Semantics

Security expiry, abuse-control, event, and audit timestamps SHALL use consistent UTC-based time semantics.

Application code SHALL use timezone-aware security timestamps.

Security logic SHALL NOT inconsistently compare local server time with persisted timezone-aware values.

This applies across security concerns such as:

- Capability expiration.
- Session expiration.
- Rate-limit windows.
- Audit timestamps.
- Security-event timestamps.

---

# Security Request Context

Cross-cutting security metadata SHALL flow through a reusable request-context boundary.

Conceptually:

```text
SecurityRequestContext
├── request_id / correlation_id
├── normalized network identity
├── bounded client metadata
└── authenticated principal, when available
```

The exact class or data structure is not frozen.

Infrastructure/DI SHALL construct the context and supply it to application/security services.

Services SHALL NOT manually reconstruct transport metadata independently.

---

# Framework Independence

Security services SHALL remain independent of FastAPI transport objects.

This dependency direction is required:

```text
FastAPI Request
      |
      v
Request-Context Adapter
      |
      v
SecurityRequestContext
      |
      v
Application / Security Service
```

This is rejected:

```text
Security Service
      |
      v
from fastapi import Request
```

merely to obtain request/security metadata.

Framework-independent context preserves:

- Testability.
- Separation of concerns.
- Transport independence.
- Reuse outside HTTP handlers.
- Clean application-layer boundaries.

---

# Security Invariants

The following invariants are mandatory:

1. Abuse protection uses layered security signals.
2. Counters may be network-, identity-, session-, capability-, and endpoint-scoped.
3. Identity rate-limit keys avoid raw identity values where practical.
4. Production abuse state uses shared ephemeral infrastructure.
5. Distributed accounting is atomic and bounds sustained and burst traffic.
6. Thresholds and windows are centrally configurable per operation.
7. Failed authentication does not automatically disable accounts.
8. Throttling avoids long application-worker sleeps.
9. Explicit throttling uses `429` and safe retry semantics.
10. Abuse controls preserve anti-enumeration guarantees.
11. Request and outbound-delivery throttling are separate controls.
12. Suppressed delivery does not invalidate an existing valid capability.
13. Security transitions emit stable structured event types.
14. Security telemetry is machine-readable.
15. Internal failure classification may be richer than external API errors.
16. High-value security transitions use durable append-oriented audit.
17. Normal application flows cannot mutate historical audit records.
18. Security telemetry carries correlation identifiers.
19. Network identity honors trusted proxy boundaries.
20. Client metadata is untrusted contextual information.
21. Secret redaction is centralized and cross-cutting.
22. Credential payloads and capability URLs are excluded from generic request logging.
23. Security metrics use bounded, non-sensitive labels.
24. Wave 4 produces alertable signals; Wave 8 owns production alert routing.
25. Routine successful authorization does not create durable audit noise.
26. External telemetry failure does not directly cause authentication failure.
27. Transactional security changes persist corresponding durable audit consistently.
28. Audit payloads follow data minimization.
29. CAPTCHA remains optional escalation architecture.
30. Invasive browser fingerprinting is outside the baseline.
31. Abuse-store outages use an explicit observable degraded-mode policy.
32. Security time semantics are UTC-based.
33. Security metadata flows through reusable request context.
34. Security services remain independent of FastAPI `Request`.

---

# Alternatives Considered

## Option A — Single Global Request Counter

Apply one shared request threshold to all authentication operations.

### Advantages

- Simple implementation.
- Minimal configuration.

### Disadvantages

- Does not model operation-specific threats.
- Weak against distributed attacks.
- Can create denial-of-service effects across unrelated operations.
- Provides poor identity-targeted protection.

**Decision:** Rejected.

---

## Option B — IP-Only Rate Limiting

Throttle security operations solely by source IP.

### Advantages

- Simple keying.
- No identity-derived state required.

### Disadvantages

- Distributed attackers can rotate source addresses.
- Shared networks can unfairly affect many legitimate users.
- Does not directly bound attacks against one identity.

**Decision:** Rejected as the sole mechanism.

---

## Option C — Identity-Only Rate Limiting

Throttle solely by normalized account identity.

### Advantages

- Directly limits repeated attempts against one identity.

### Disadvantages

- Attackers can deliberately exhaust a victim's budget.
- Creates identity-targeted denial-of-service pressure.
- Does not constrain broad attacks across many identities.

**Decision:** Rejected as the sole mechanism.

---

## Option D — Layered Network + Identity + Operation Controls

Combine independent abuse dimensions according to endpoint risk.

### Advantages

- Better resistance to distributed credential attacks.
- Better resistance to identity-targeted attacks.
- Supports operation-specific tuning.
- Extensible to session/capability controls.

### Disadvantages

- More configuration and operational complexity.
- Requires shared distributed state.

**Decision:** Accepted.

---

## Option E — Process-Local Production Counters

Keep counters in each application process.

### Advantages

- Very simple.
- No additional infrastructure.

### Disadvantages

- Each replica grants an independent budget.
- Restarts erase protection state.
- Cannot provide authoritative distributed limits.

**Decision:** Rejected for production authority.

---

## Option F — PostgreSQL as Per-Request Rate-Limit Store

Persist normal abuse counters in the primary relational database.

### Advantages

- Durable and shared.
- Existing infrastructure.

### Disadvantages

- Abuse state is ephemeral operational state.
- Adds unnecessary write pressure to primary persistence.
- Couples high-volume throttling to durable application storage.

**Decision:** Rejected as the normal abuse-state architecture.

---

## Option G — Shared Ephemeral Distributed Abuse Store

Use shared ephemeral infrastructure with atomic operations and expiry.

### Advantages

- Multi-instance consistency.
- Natural TTL/expiry.
- Supports atomic counters/buckets.
- Separates ephemeral abuse state from durable security persistence.

### Disadvantages

- Adds infrastructure dependency.
- Requires explicit degraded-mode behavior.

**Decision:** Accepted.

---

## Option H — Hard Account Lockout After Repeated Failures

Administratively disable an account after a fixed number of incorrect passwords.

### Advantages

- Strongly stops further password attempts against that account.

### Disadvantages

- Easy victim-targeted denial of service.
- Conflates abuse throttling with administrative account state.
- Requires recovery/unlock lifecycle.

**Decision:** Rejected for the baseline.

---

## Option I — Long Server-Side Sleep for Throttling

Keep abusive requests open while intentionally delaying their response.

### Advantages

- Slows individual clients.

### Disadvantages

- Occupies application workers.
- Can amplify resource exhaustion.
- Scales poorly under attack.

**Decision:** Rejected as the primary throttling mechanism.

---

## Option J — One Throttle for Request and Email Delivery

Use the same counter for inbound recovery/verification requests and outbound email sends.

### Advantages

- Fewer controls.

### Disadvantages

- Conflates API abuse and provider/delivery abuse.
- Cannot independently tune provider-cost and request pressure.
- Weakens recovery/verification delivery control.

**Decision:** Rejected.

---

## Option K — Log Everything for Security Investigation

Persist complete requests, responses, tokens, bodies, and objects.

### Advantages

- Maximum raw diagnostic data.

### Disadvantages

- Leaks credentials and capability secrets.
- Creates privacy and retention risk.
- Produces high-volume noisy data.
- Violates data minimization.

**Decision:** Rejected.

---

## Option L — Structured, Minimized Security Events

Emit stable machine-readable events with safe bounded metadata.

### Advantages

- Supports automated analysis.
- Supports correlation.
- Reduces secret leakage.
- Provides stable operational semantics.

### Disadvantages

- Requires event taxonomy and discipline.

**Decision:** Accepted.

---

## Option M — External Telemetry Vendor as Authentication Dependency

Fail authentication when external log/APM delivery fails.

### Advantages

- Ensures telemetry delivery before returning success.

### Disadvantages

- Converts observability outages into authentication outages.
- Couples security availability to a remote vendor.
- Confuses operational telemetry with durable audit.

**Decision:** Rejected.

---

## Option N — Durable Audit as Ordinary Mutable Domain Data

Allow normal application workflows to update/delete historical security audit records.

### Advantages

- Familiar CRUD semantics.

### Disadvantages

- Weakens historical accountability.
- Allows normal flows to rewrite security history.
- Blurs audit and business state.

**Decision:** Rejected.

---

## Option O — Transactionally Consistent Local Durable Audit

Persist required durable audit records consistently with the corresponding local security-state transition.

### Advantages

- Avoids committed high-value state without the required audit fact.
- Provides coherent local security history.
- Separates local audit durability from external telemetry shipping.

### Disadvantages

- Adds transaction complexity.
- Audit persistence failure can affect transitions that require durable audit.

**Decision:** Accepted.

---

## Option P — Mandatory CAPTCHA

Require CAPTCHA for Wave 4 authentication workflows.

### Advantages

- Adds interactive bot resistance.

### Disadvantages

- Third-party dependency.
- Accessibility concerns.
- Privacy implications.
- Frontend coupling.
- Not justified as a universal baseline without abuse evidence.

**Decision:** Rejected as a mandatory baseline; retained as optional escalation architecture.

---

## Option Q — Persistent Browser Fingerprinting

Create a cross-session browser fingerprint for authentication or abuse decisions.

### Advantages

- Adds another correlation signal.

### Disadvantages

- Privacy-invasive.
- Fingerprints can be unstable or spoofed.
- Introduces complexity not required by the frozen threat model.

**Decision:** Rejected for Wave 4.

---

# Consequences

## Positive

- Credential stuffing and brute-force attacks receive layered resistance.
- Distributed attacks cannot trivially bypass per-process counters.
- Identity-targeted lockout denial of service is reduced.
- Recovery and verification flooding receive both request and delivery controls.
- Anti-enumeration remains preserved through the abuse layer.
- Abuse thresholds remain operationally tunable.
- Security events become machine-readable and correlatable.
- High-value security transitions receive durable audit history.
- Operational telemetry and durable audit have clear failure semantics.
- Secret redaction becomes centralized rather than endpoint-specific.
- Security metrics remain usable without leaking identities or creating uncontrolled cardinality.
- Wave 8 receives an alertable security-signal foundation.
- Degraded abuse-control operation becomes explicit and observable.
- Security services remain independent of FastAPI request objects.

## Negative

- Production requires shared ephemeral abuse-control infrastructure.
- Abuse-control configuration becomes a security-sensitive operational concern.
- Distributed atomic accounting adds implementation complexity.
- Degraded-mode behavior must be explicitly designed and tested.
- Durable audit introduces persistence and transaction requirements.
- Request-context infrastructure must carry security metadata consistently.
- Observability pipelines require centralized redaction and schema discipline.
- Some raw diagnostic convenience is intentionally sacrificed to protect secrets and privacy.
- Final production alert routing remains deferred to the operations architecture.

These trade-offs are accepted because abuse resistance and security visibility are part of the effective authentication boundary, not optional operational decoration.

---

# Risks

Primary risks include:

- Using only IP-based throttling and remaining vulnerable to distributed attacks.
- Using only identity-based throttling and enabling victim lockout denial of service.
- Process-local counters silently weakening limits across replicas.
- Raw emails leaking through abuse-store keys.
- Abuse-store failure silently disabling protection.
- Rate-limit behavior becoming an account-enumeration oracle.
- Request throttling failing to constrain outbound recovery/verification delivery.
- Long request sleeps creating worker exhaustion.
- Credential material leaking through generic request/response logging.
- Capability-bearing URLs leaking through telemetry.
- Authentication tokens appearing in APM or exception payloads.
- Sensitive or unbounded values becoming metric labels.
- External telemetry outages causing authentication outages.
- Durable security transitions committing without required audit facts.
- Normal application code mutating audit history.
- Untrusted forwarding headers being treated as client network identity.
- User-Agent/device metadata being treated as authentication proof.
- Services becoming coupled to FastAPI transport objects.
- Local-time inconsistencies corrupting expiry, audit, or abuse semantics.

These risks SHALL be mitigated through the frozen invariants in this ADR and verified under ADR-0011.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact abuse-control product/provider.
- Exact Redis deployment topology.
- Exact rate-limiting library.
- Exact token-bucket/sliding-window implementation.
- Exact numeric thresholds.
- Exact windows.
- Exact burst capacities.
- Exact identity-key derivation primitive.
- Exact rate-limit key names.
- Exact security-event names.
- Exact event schema field names.
- Exact durable audit table schema.
- Exact audit retention period.
- Exact logging/APM vendor.
- Exact metrics backend.
- Exact alerting platform.
- Exact production alert thresholds.
- Exact CAPTCHA provider.
- Exact endpoint-by-endpoint degraded-mode fallback.
- Exact `SecurityRequestContext` class name.
- Exact FastAPI dependency/adapter names.
- Exact module paths.

Those are implementation or operations decisions provided they preserve `ARC-P9-01` through `ARC-P9-34`.

A process-local-only production limiter, silent fail-open abuse-store outage, raw-identity metric labels, credential-bearing generic request logging, mutable ordinary audit history, or direct FastAPI `Request` dependency in application security services conflicts with this ADR.

---

# Verification

ADR-0011 governs the complete Wave 4 security verification and release gates.

At minimum, implementation of this ADR requires automated evidence for:

- Layered abuse-control evaluation.
- Network-scoped throttling.
- Identity-scoped throttling where applicable.
- Operation/endpoint-scoped throttling.
- Distributed multi-instance accounting.
- Atomic abuse-state updates.
- Bounded sustained request behavior.
- Bounded burst behavior.
- Centralized per-operation configuration.
- Privacy-preserving identity abuse keys.
- Repeated failed login not administratively disabling an account.
- Throttling without long worker sleeps.
- Correct `429` semantics.
- Safe retry behavior.
- No sensitive internal counter disclosure.
- Enumeration resistance while throttled.
- Recovery-request throttling.
- Verification-request throttling.
- Outbound recovery-delivery throttling.
- Outbound verification-delivery throttling.
- Suppressed delivery not accidentally invalidating an existing capability.
- Stable structured security-event emission.
- Machine-readable security telemetry.
- Internal/external failure-classification separation.
- Durable audit creation for required high-value transitions.
- Append-oriented audit behavior under normal application flows.
- Actor/subject semantics.
- Anonymous security-event/audit support.
- Correlation identifier propagation.
- Trusted-proxy network-identity handling.
- Rejection of arbitrary forwarding headers as trusted identity.
- Bounded untrusted client metadata.
- Central secret-redaction behavior.
- Credential request bodies absent from generic logging.
- Capability-bearing URLs absent from generic logging.
- Authentication credential responses absent from generic logging.
- Tokens/cookies absent from security telemetry and audit metadata.
- Bounded low-cardinality security metric labels.
- Authorization-denial security telemetry.
- Routine successful authorization not generating durable audit noise.
- External telemetry outage not directly breaking authentication.
- Transactional consistency between required security-state changes and durable audit.
- Audit data minimization.
- Historical security telemetry not erased by successful authentication.
- CAPTCHA absence not weakening mandatory baseline controls.
- No invasive browser fingerprinting dependency.
- Explicit observable abuse-store degraded mode.
- UTC-based security timestamps.
- Reusable security request-context propagation.
- Application/security services remaining independent of FastAPI `Request`.

Production approval of the public credential, recovery, and verification surface SHALL require evidence that the relevant P9 controls are active.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P9-01` through `ARC-P9-34`.

W4-S0C Package 9 passed all 37 architecture review gates and resolves the abuse-protection dependency established by `ARC-P8-23`.

It is constrained by:

- W4-S0C Package 1 — Security Domain & Principal Architecture.
- W4-S0C Package 2 — Credential & Password Architecture.
- W4-S0C Package 3 — Session & Token Architecture.
- W4-S0C Package 4 — Authentication Transport Architecture.
- W4-S0C Package 5 — Authorization & Policy Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze and amendment ledger.

Any implementation that conflicts with the frozen abuse-protection or security-observability invariants requires formal architecture review rather than silent deviation.

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

## Wave 4 ADRs

- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- W4-S0C Package 5 — Authorization & Policy Architecture.
- W4-S0C Package 8 — Recovery & Credential Lifecycle Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.
