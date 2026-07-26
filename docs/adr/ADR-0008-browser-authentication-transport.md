# ADR-0008 — Browser Authentication Transport

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

ADR-0006 establishes two authentication credentials with different security properties:

- A short-lived access JWT used for ordinary API request authority.
- A long-lived opaque refresh credential representing server-controlled authentication continuity.

These credentials cross the browser trust boundary and therefore require deliberately different transport and storage protections.

The primary browser-side threats relevant to this decision are:

- Cross-Site Scripting (XSS).
- Cross-Site Request Forgery (CSRF).
- Credential leakage through browser persistence.
- Credential leakage through URLs, logs, telemetry, analytics, or caches.
- Over-broad cookie scope.
- Misconfigured Cross-Origin Resource Sharing (CORS).
- Plaintext network transport.
- Accidental exposure of long-lived refresh authority to browser JavaScript.

No single browser credential transport eliminates all of these risks.

JavaScript-accessible storage increases credential exposure during XSS.

HttpOnly cookies prevent JavaScript from directly reading credential values, but cookies are automatically attached by the browser and therefore introduce CSRF considerations.

Sentinel AI must therefore use a transport architecture appropriate to the different risk profiles of access and refresh credentials.

This ADR records the durable decisions established by W4-S0C Package 4 — Authentication Transport Architecture.

---

# Decision

Sentinel AI SHALL use a split browser authentication transport model.

The authoritative first-party browser model is:

```text
Browser
|
+-- Access JWT
|   +-- short-lived
|   +-- ephemeral runtime memory only
|   +-- Authorization: Bearer
|
+-- Refresh Credential
    +-- opaque
    +-- designated HttpOnly cookie
    +-- Secure in production
    +-- SameSite=Lax baseline
    +-- host-scoped by default
    +-- narrowest practical authentication path
```

The resulting request architecture is:

```text
     Browser Runtime                     Browser Cookie Jar
            |                                   |
            | Access JWT                        | Refresh Credential
            |                                   |
            | Authorization: Bearer             | automatic cookie transport
            v                                   v
    Ordinary API Requests               Refresh / Logout Endpoints
            |                                   |
            v                                   v
       JWT Validation                    Session Validation
                                                |
                                                v
                                         Refresh Rotation
```

The access JWT and refresh credential SHALL NOT be transported or stored identically merely for implementation convenience.

---

# Access JWT Transport

Browser access JWTs SHALL be transported through the HTTP `Authorization` header using the Bearer authentication scheme.

Conceptually:

```text
Authorization: Bearer <access-jwt>
```

The access JWT is short-lived request authority.

It SHALL be retained only in ephemeral frontend runtime memory.

Browser authentication bearer credentials SHALL NOT be persisted in:

- `localStorage`.
- `sessionStorage`.

This architecture intentionally accepts that a successful XSS may interact with runtime application state while limiting the persistence of stolen bearer authority to the short access-token lifetime.

The access JWT SHALL NOT be moved into persistent browser storage to simplify page reload behavior.

---

# Refresh Credential Transport

The browser refresh credential SHALL be transported exclusively through a designated HttpOnly cookie.

Conceptually:

```text
Set-Cookie: <refresh-cookie>=<opaque-credential>; HttpOnly; ...
```

The raw refresh credential SHALL NOT be exposed to first-party browser JavaScript.

Browser refresh endpoints SHALL accept refresh authority only from the designated cookie transport.

They SHALL NOT additionally accept the same credential through:

- JSON request bodies.
- Form fields.
- Custom JavaScript-readable storage.
- Query parameters.
- Alternate headers added merely for convenience.

Transport singularity reduces ambiguity and prevents weaker alternate credential paths from silently bypassing the intended browser security boundary.

---

# Why the Credentials Use Different Transports

The access JWT and refresh credential have different risk profiles.

## Access JWT

The access JWT is:

- Short-lived.
- Frequently transmitted.
- Used for ordinary API requests.
- Replaceable through refresh.
- Intended for Bearer authentication.

## Refresh Credential

The refresh credential is:

- Longer-lived.
- High-value.
- Capable of continuing an authentication session.
- Rotation-enabled.
- Backed by server-controlled session state.
- Subject to replay detection and revocation.

Exposing the refresh credential to JavaScript would allow an XSS compromise to obtain longer-lived session authority.

The selected architecture therefore deliberately separates:

```text
Short-lived request authority
        |
        v
JavaScript-managed ephemeral access JWT
        |
        v
Authorization: Bearer
```

from:

```text
Long-lived session continuity
        |
        v
HttpOnly refresh cookie
        |
        v
Cookie-authenticated security endpoint
```

---

# HttpOnly Requirement

The refresh cookie SHALL use `HttpOnly`.

The browser application SHALL NOT require JavaScript access to the raw refresh credential.

Refresh behavior is performed by allowing the browser to attach the designated cookie to the appropriate authentication endpoint.

This protects the refresh credential from direct JavaScript reads.

`HttpOnly` does not eliminate XSS as a security threat and SHALL NOT be treated as a complete XSS defense.

It specifically protects the confidentiality of the cookie value from direct script access.

---

# Secure Cookie Requirement

Refresh cookies SHALL use:

```text
Secure=true
```

in production.

Production authentication SHALL require HTTPS.

The production architecture SHALL NOT transmit authentication credentials over plain HTTP.

Development environments may require environment-appropriate handling, but production security guarantees SHALL NOT be weakened to match local development convenience.

---

# SameSite Policy

`SameSite=Lax` is the default refresh-cookie policy for the Wave 4 browser architecture.

This default is part of the selected deployment and CSRF assumptions.

`SameSite=None` SHALL NOT be adopted casually.

A move to `SameSite=None` requires explicit security review and corresponding reassessment of CSRF defenses.

The architecture SHALL NOT assume that `SameSite` alone is sufficient CSRF protection.

---

# Cookie Path Scope

Refresh cookies SHALL use the narrowest practical authentication path.

The refresh credential SHALL NOT be attached to every API route merely because broad cookie scope is simpler to configure.

Conceptually:

```text
preferred:
    authentication-specific path

rejected default:
    Path=/
    when broad application-wide attachment is unnecessary
```

The exact cookie path is an implementation/configuration concern constrained by this rule.

---

# Cookie Domain Scope

Refresh cookies SHALL be host-scoped by default.

Broad parent-domain cookies require explicit justification.

The architecture rejects a broad domain such as:

```text
Domain=.example.com
```

as a default merely to simplify cross-subdomain behavior.

A broader domain increases the number of hosts participating in the credential trust boundary.

Any such expansion requires deliberate review.

---

# CSRF Defense

Because the refresh credential is automatically attached by the browser, cookie-authenticated security endpoints cross a CSRF trust boundary.

Cookie-authenticated security endpoints SHALL validate trusted request origin as part of CSRF defense.

This includes applicable state-changing authentication operations such as refresh and logout.

Conceptually:

```text
Cookie-Authenticated Security Request
                |
                v
       Validate Request Origin
                |
          +-----+-----+
          |           |
       trusted      untrusted
          |           |
          v           v
       continue      reject
```

The exact trusted-origin set is centralized configuration.

A request being `POST` does not itself provide CSRF protection.

---

# Synchronizer CSRF Tokens

Synchronizer CSRF tokens are NOT universally required under the selected Wave 4 baseline.

This is conditional on the frozen transport and deployment assumptions, including:

- The selected refresh-cookie model.
- `SameSite=Lax` baseline.
- Explicit trusted-origin validation.
- Explicit CORS configuration.
- Narrow cookie scope.

If these assumptions change, the CSRF architecture SHALL be reassessed.

In particular, changes such as `SameSite=None` or materially different cross-site deployment requirements may require stronger or additional CSRF controls.

The absence of a universal synchronizer token in the baseline SHALL NOT be interpreted as permission to remove CSRF analysis from cookie-authenticated operations.

---

# CORS

CORS SHALL use an explicit trusted-origin allowlist.

Credentialed CORS SHALL NEVER be combined with wildcard origins.

The following configuration is prohibited:

```text
Access-Control-Allow-Origin: *
+
credentialed browser requests
```

CORS is a browser cross-origin access-control mechanism.

It SHALL NOT be treated as:

- Authentication.
- Authorization.
- Standalone CSRF protection.

The authentication architecture must remain secure even when these responsibilities are considered separately.

---

# URL Credential Prohibition

Access and refresh credentials SHALL NOT be transported through URL query parameters.

Examples such as:

```text
/api/v1/resource?access_token=...
/api/v1/auth/refresh?refresh_token=...
```

are prohibited.

URLs may propagate into:

- Browser history.
- Reverse-proxy logs.
- Application logs.
- Analytics.
- Referrer information.
- Monitoring systems.
- Support tooling.

Authentication credentials therefore remain outside URL transport.

---

# Logging, Telemetry, Errors, and Analytics

Authentication credentials SHALL be excluded or redacted from:

- Application logs.
- Structured security logs.
- Error responses.
- Exception messages.
- Tracing attributes.
- Metrics labels.
- Telemetry.
- Analytics.
- Debug output where avoidable.

This prohibition includes:

- Access JWTs.
- Raw refresh credentials.
- Cookie values containing authentication secrets.

Operational observability SHALL NOT require credential disclosure.

Detailed security observability policy is governed by ADR-0010.

---

# Cache Control

Authentication responses carrying credentials or security-sensitive principal state SHALL use non-cacheable semantics appropriate to the endpoint.

This includes applicable responses such as:

- Login.
- Refresh.
- Current-principal responses.

Security-sensitive authentication responses SHALL NOT be allowed to become reusable shared/intermediary cache artifacts.

Exact HTTP cache headers are implementation/API concerns constrained by this architecture.

---

# Login Transport

Successful browser login SHALL return the access credential through the response representation while establishing refresh authority through `Set-Cookie`.

Conceptually:

```text
POST /auth/login
        |
        v
Authentication succeeds
        |
        +--> Response body: access JWT
        |
        +--> Set-Cookie: opaque refresh credential
```

The refresh credential SHALL NOT be duplicated into the JSON response.

This preserves the browser confidentiality boundary:

```text
JavaScript
   |
   +--> receives access JWT
   |
   X--> cannot read raw refresh credential
```

The exact response schema and cookie name are governed by the API/configuration architecture.

---

# Refresh Transport

Successful browser refresh SHALL:

1. Receive the refresh credential through the designated HttpOnly cookie.
2. Validate and rotate refresh authority according to ADR-0006.
3. Establish the successor refresh credential through `Set-Cookie`.
4. Return a new access credential through the response representation.

Conceptually:

```text
HttpOnly Refresh Cookie
        |
        v
POST /auth/refresh
        |
        v
Validate Session
        |
        v
Atomic Refresh Rotation
        |
        +--> Set-Cookie: successor refresh credential
        |
        +--> Response body: new access JWT
```

The refresh credential SHALL NOT enter ordinary Pydantic request-body contracts for the first-party browser flow.

---

# Logout Transport

Browser logout SHALL coordinate three effects:

```text
Logout
  |
  +--> revoke server-side authentication session
  |
  +--> expire refresh cookie
  |
  +--> frontend discards in-memory access JWT
```

Revocation of the durable session immediately terminates refresh authority.

As established by ADR-0006, an already-issued stateless access JWT may remain usable until its short expiration unless another frozen security mechanism explicitly requires request-time invalidation.

The frontend SHALL discard its in-memory access JWT when logout succeeds.

---

# Cookie Deletion Semantics

Cookie scope attributes used when deleting the refresh cookie SHALL match the attributes required to target the cookie that was originally established.

The implementation SHALL NOT assume that setting an empty cookie under different path/domain semantics reliably removes the original authentication cookie.

Cookie establishment and deletion configuration SHALL therefore be centrally consistent.

---

# First-Party Browser Baseline

The first-party browser is the authoritative Wave 4 client transport model.

Wave 4 SHALL NOT weaken the browser security model to make hypothetical future clients easier to support.

Future transports such as:

- CLI clients.
- Native mobile applications.
- Service-to-service clients.

require explicit transport design appropriate to their threat models.

They MAY reuse lower-level authentication/session semantics where appropriate, but SHALL NOT force browser refresh credentials into JavaScript-readable or otherwise weaker transport.

---

# WebSocket Transport

WebSocket authentication transport is deferred until Sentinel AI has a realtime protocol architecture.

Wave 4 SHALL NOT invent a WebSocket token transport merely for hypothetical future compatibility.

When realtime protocols are introduced, authentication transport must be explicitly designed for that protocol and its lifecycle.

---

# Configuration Boundary

The following exact values are intentionally left to centralized configuration and the authentication API implementation:

- Refresh-cookie name.
- Exact cookie path.
- Deployment origins.
- Trusted-origin allowlist.
- Environment-specific HTTPS/cookie behavior consistent with this ADR.

These implementation choices SHALL preserve the frozen transport invariants.

Application-wide authentication transport policy SHALL NOT be scattered across endpoint-local constants.

---

# Transport and Application-Layer Separation

Cookie extraction, Bearer extraction, CORS integration, CSRF transport checks, `Set-Cookie`, and cookie deletion are transport responsibilities.

Session/token services SHALL remain independent of FastAPI request and cookie objects except through explicit transport adapters.

Conceptually:

```text
HTTP Request
    |
    v
Transport Adapter
    |
    +--> extract Bearer credential
    +--> extract refresh cookie
    +--> validate transport security context
    |
    v
Application / Security Service
```

The lower security layers operate on security concepts rather than framework-specific request objects.

---

# Security Invariants

The following invariants are mandatory:

1. Browser access JWTs are transported through `Authorization: Bearer`.
2. Browser access JWTs are retained only in ephemeral frontend runtime memory.
3. Authentication bearer credentials are not persisted in `localStorage` or `sessionStorage`.
4. Browser refresh credentials are transported exclusively through a designated HttpOnly cookie.
5. Refresh cookies use `Secure=true` in production.
6. `SameSite=Lax` is the default refresh-cookie policy.
7. `SameSite=None` requires explicit security review and CSRF reassessment.
8. Refresh cookies use the narrowest practical authentication path.
9. Refresh cookies are host-scoped by default.
10. Production authentication requires HTTPS.
11. Cookie-authenticated security endpoints validate trusted request origin as part of CSRF defense.
12. Synchronizer CSRF tokens are not universally required under the selected baseline but must be reconsidered if transport/deployment assumptions change.
13. CORS uses an explicit trusted-origin allowlist.
14. Credentialed CORS is never combined with wildcard origins.
15. CORS is not authentication, authorization, or standalone CSRF protection.
16. Refresh credentials are never exposed to first-party browser JavaScript.
17. Browser refresh endpoints accept refresh credentials only from the designated cookie transport.
18. Access and refresh credentials are prohibited from URL query parameters.
19. Authentication credentials are excluded/redacted from logs, errors, telemetry, and analytics.
20. Authentication responses carrying credentials/security-sensitive state use non-cacheable semantics.
21. Login returns access authority through the response representation and establishes refresh authority through `Set-Cookie`.
22. Refresh rotates the HttpOnly refresh credential through `Set-Cookie` and returns a new access credential.
23. Logout revokes the server session, expires the refresh cookie, and requires the frontend to discard its in-memory access JWT.
24. Cookie scope attributes used for deletion match those used to establish the refresh cookie.
25. First-party browser transport is the Wave 4 authoritative client model.
26. Future CLI/mobile/service authentication transports require explicit design rather than weakening the browser flow.
27. WebSocket authentication transport is deferred until realtime protocol architecture exists.
28. Cookie names, exact paths, and deployment origins remain configuration/API concerns constrained by this architecture.

---

# Alternatives Considered

## Option A — Access and Refresh Credentials in Browser Persistent Storage

Store access and refresh credentials in `localStorage` or `sessionStorage`.

### Advantages

- Straightforward frontend implementation.
- Credentials survive page reloads.
- JavaScript can explicitly control both credentials.

### Disadvantages

- Long-lived refresh authority becomes directly readable by JavaScript.
- XSS can convert a runtime compromise into persistent session theft.
- Expands credential exposure.
- Conflicts with the frozen refresh confidentiality boundary.

**Decision:** Rejected.

---

## Option B — Both Credentials in HttpOnly Cookies

Store both access and refresh credentials in HttpOnly cookies and authenticate ordinary API requests through automatically attached cookies.

### Advantages

- JavaScript cannot directly read either credential.
- Browser credential persistence is straightforward.

### Disadvantages

- Ordinary authenticated API requests become cookie-authenticated.
- CSRF protection becomes a broad concern across authenticated state-changing endpoints.
- Removes the deliberate Bearer-token boundary for ordinary API requests.
- Does not match the selected split-risk transport architecture.

**Decision:** Rejected for the Wave 4 browser baseline.

---

## Option C — Bearer Access JWT + HttpOnly Refresh Cookie

Keep the short-lived access JWT in ephemeral browser runtime memory and send it through `Authorization: Bearer`, while transporting long-lived refresh authority exclusively through a protected HttpOnly cookie.

### Advantages

- Limits long-lived refresh-secret exposure to JavaScript.
- Ordinary API requests are not automatically cookie-authenticated.
- Preserves standard Bearer semantics for API access.
- Keeps refresh authority server-controlled and rotation-compatible.
- Separates XSS and CSRF exposure according to credential risk.
- Supports explicit CSRF protection at cookie-authenticated security endpoints.

### Disadvantages

- Frontend must manage ephemeral access-token state.
- Page reloads require refresh/bootstrap behavior.
- Cookie-authenticated refresh/logout still require CSRF defenses.
- Requires careful CORS and cookie configuration.
- Requires coordinated logout behavior.

**Decision:** Accepted.

---

## Option D — Refresh Credential Returned in JSON

Return both access and refresh credentials to browser JavaScript.

### Advantages

- Simple client implementation.
- No cookie handling required.

### Disadvantages

- Exposes long-lived session authority to JavaScript.
- Weakens the selected XSS exposure boundary.
- Encourages persistent browser storage.
- Conflicts with the designated refresh-cookie transport.

**Decision:** Rejected.

---

## Option E — Multiple Refresh Credential Input Locations

Accept refresh credentials from cookies, request bodies, headers, or query parameters for convenience.

### Advantages

- Flexible client integration.

### Disadvantages

- Creates ambiguous security semantics.
- Expands attack surface.
- Makes logging/redaction harder.
- Allows weaker alternate paths to bypass the intended browser transport.
- Complicates API documentation and testing.

**Decision:** Rejected for the first-party browser flow.

---

## Option F — Wildcard Credentialed CORS

Allow credentialed browser requests from arbitrary origins.

### Advantages

- Minimal cross-origin configuration.

### Disadvantages

- Destroys the explicit browser origin trust boundary.
- Conflicts with secure credentialed browser transport.
- Is prohibited by the frozen CORS architecture.

**Decision:** Rejected.

---

## Option G — Broad Parent-Domain Refresh Cookie

Set the refresh cookie broadly across a parent domain by default.

### Advantages

- Easier cross-subdomain access.

### Disadvantages

- Expands the number of hosts within the credential trust boundary.
- Increases consequences of compromise or misconfiguration on sibling hosts.
- Violates least-scope credential handling.

**Decision:** Rejected as the default.

---

## Option H — Refresh Cookie on Every API Path

Use an application-wide cookie path even when refresh authority is only needed by authentication endpoints.

### Advantages

- Simple configuration.

### Disadvantages

- Causes unnecessary credential attachment.
- Broadens exposure.
- Violates narrowest-practical-scope policy.

**Decision:** Rejected as the default.

---

## Option I — Plain HTTP Production Authentication

Permit production authentication credentials over unencrypted HTTP.

### Advantages

- None sufficient to justify the security loss.

### Disadvantages

- Exposes credentials to network interception.
- Prevents the required production `Secure` cookie guarantee.
- Violates the production trust boundary.

**Decision:** Rejected.

---

# Consequences

## Positive

- Long-lived refresh credentials are not readable by first-party browser JavaScript.
- Access authority remains short-lived and uses explicit Bearer transport.
- Persistent browser bearer storage is prohibited.
- CSRF-sensitive operations are limited to the cookie-authenticated security boundary rather than every ordinary Bearer-authenticated request.
- Cookie scope and domain are minimized.
- Production authentication is HTTPS-only.
- CORS has an explicit trust boundary.
- Credential leakage through URLs is prohibited.
- Login, refresh, and logout have explicit transport semantics.
- The browser architecture remains compatible with stateful refresh rotation from ADR-0006.
- Future client types can receive dedicated transport designs without weakening the browser model.

## Negative

- Frontend runtime state management is more complex than persistent token storage.
- Browser reload/bootstrap behavior requires refresh orchestration.
- Refresh and logout require explicit CSRF controls.
- Cookie configuration must remain consistent across establishment and deletion.
- Deployment origin changes can affect CORS, cookie, and CSRF assumptions.
- Cross-site deployment requirements may require revisiting the baseline `SameSite` and CSRF strategy.

These trade-offs are accepted because the selected architecture gives the long-lived refresh credential stronger browser protection while preserving explicit Bearer semantics for short-lived request authority.

---

# Risks

Primary risks include:

- Frontend developers persisting access JWTs for convenience.
- Refresh credentials accidentally entering JavaScript-readable responses.
- Refresh endpoints accepting credentials from multiple locations.
- `SameSite` changes occurring without CSRF reassessment.
- Trusted-origin validation being omitted from cookie-authenticated operations.
- Credentialed CORS being misconfigured.
- Cookie domain/path being broader than required.
- Logout failing to remove the actual refresh cookie because deletion attributes differ.
- Credentials appearing in logs or telemetry.
- Security-sensitive authentication responses being cached.
- Production environments accidentally allowing insecure transport.
- Future client requirements silently weakening the browser architecture.

These risks SHALL be mitigated through:

- Centralized authentication transport configuration.
- Dedicated cookie helpers/adapters.
- Explicit origin validation.
- CORS allowlists.
- Transport-focused automated tests.
- Credential leakage tests.
- Cache-control verification.
- HTTPS production configuration.
- Architecture review for transport changes.
- Security verification under ADR-0011.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact refresh-cookie name.
- Exact cookie path.
- Exact deployment origins.
- Exact trusted-origin values.
- Exact frontend state-management library.
- Exact HTTP helper implementation.
- Exact FastAPI dependency/helper names.
- Exact CORS middleware wiring.
- Exact cache-control header helper.
- Exact local-development cookie configuration.
- Exact API schema field names beyond the frozen transport semantics.

Those are implementation/configuration decisions provided they preserve `ARC-P4-01` through `ARC-P4-28`.

The authentication API architecture refines the endpoint contracts for login, refresh, logout, and principal retrieval without changing this transport boundary.

Any proposal to persist browser bearer credentials, expose refresh credentials to JavaScript, remove required CSRF controls, broaden credentialed CORS, or materially change cookie scope/transport requires architecture review.

---

# Verification

ADR-0011 governs the complete Wave 4 security verification and release gates.

At minimum, implementation of this ADR requires automated evidence for:

- Access JWT transport through `Authorization: Bearer`.
- Absence of persistent browser bearer storage in the supported frontend architecture.
- Refresh credential issuance through the designated HttpOnly cookie.
- Production `Secure` cookie behavior.
- Baseline `SameSite=Lax` behavior.
- Refresh-cookie path constraints.
- Host-scoped cookie behavior by default.
- Trusted-origin validation for cookie-authenticated security operations.
- Explicit CORS trusted-origin configuration.
- Rejection of credentialed wildcard CORS configuration.
- Refresh credentials not being returned in JSON.
- Refresh credentials not being accepted through ordinary request bodies for the browser flow.
- Authentication credentials not being accepted from URL query parameters.
- Credential redaction/exclusion from logs, errors, telemetry, and analytics.
- Non-cacheable semantics for applicable authentication responses.
- Login establishing refresh authority via `Set-Cookie`.
- Refresh rotating refresh authority via `Set-Cookie`.
- Logout revoking the server session and expiring the refresh cookie.
- Cookie deletion using compatible scope attributes.
- CSRF-negative-path behavior.
- Cross-origin negative-path behavior.
- Production HTTPS assumptions.
- Transport compatibility with ADR-0006 session rotation and revocation.

Changes to deployment assumptions SHALL trigger review of the corresponding CSRF, CORS, `SameSite`, and cookie-scope verification matrix.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P4-01` through `ARC-P4-28`.

It is constrained by:

- ADR-0004 — Authentication & Security Architecture.
- ADR-0006 — Access Token & Stateful Refresh Session Architecture.
- W4-S0C Package 4 — Authentication Transport Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.

Any implementation that conflicts with the frozen browser transport invariants requires formal architecture review rather than silent deviation.

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

## Wave 4 ADRs

- ADR-0009 — Recovery & Verification Capability Architecture.
- ADR-0010 — Abuse Protection & Security Observability.
- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- W4-S0C Package 3 — Session & Token Architecture.
- W4-S0C Package 4 — Authentication Transport Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.
