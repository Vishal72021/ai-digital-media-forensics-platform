# ADR-0007 — Authorization Model — Roles & Permissions

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

Wave 4 requires Sentinel AI to determine what an authenticated principal is permitted to do.

Authentication and authorization are separate security stages:

```text
Authentication
"Who are you?"

Authorization
"What are you allowed to do?"
```

A valid access credential establishes authenticated identity. It does not by itself establish permission to perform an operation.

Sentinel AI requires an authorization architecture capable of supporting:

- Authenticated-only operations.
- Administrative operations.
- Fine-grained permissions.
- Resource ownership.
- Least privilege.
- Multiple roles.
- Privilege changes.
- Deny-by-default behavior.
- Centralized policy enforcement.
- Independently testable authorization rules.
- Future resource-specific policy expansion.

The architecture must avoid distributing hard-coded role checks throughout endpoints and services while also avoiding an unnecessarily complex enterprise policy system before such complexity is required.

This ADR records the durable authorization decisions established by W4-S0C Package 5.

---

# Decision

Sentinel AI SHALL use **role-based authority assignment with permission-based application enforcement**.

The canonical model is:

```text
USER
  |
  | 0..N
  v
ROLE
  |
  | 0..N
  v
PERMISSION
  |
  v
Policy Registry
  |
  +---------------------+
  |                     |
  v                     v
Capability Policy   Resource Policy
  |                     |
  +----------+----------+
             |
             v
         ALLOW / DENY
```

Roles are administrative bundles of permissions.

Application authorization SHALL generally evaluate permissions and resource relationships rather than scattered hard-coded role names.

At runtime:

```text
Access JWT
    |
    v
Authenticated Principal
    |
    +-- user identity
    +-- session identity
    +-- compact server-issued role identifiers
             |
             v
      Server-Owned Policy
             |
             v
      Effective Authority
             |
             v
      Resource Relationship
             |
             v
         ALLOW / DENY
```

Authorization is deny-by-default.

---

# Authentication and Authorization Separation

Authentication establishes a trusted principal.

Authorization evaluates that principal against policy and, where required, the target resource.

The security chain remains:

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
Authorization Policy
       |
       +--> ALLOW
       |
       +--> DENY
```

A successful authentication result SHALL NOT imply authorization to arbitrary operations.

Likewise, authorization logic SHALL NOT become responsible for validating passwords, refresh credentials, or other authentication secrets.

---

# Role-Based Assignment

Users MAY hold zero or more roles.

Roles MAY contain zero or more permissions.

Conceptually:

```text
User
  |
  +--> Role A
  |      +--> Permission 1
  |      +--> Permission 2
  |
  +--> Role B
         +--> Permission 2
         +--> Permission 3
```

The effective permission set is composed from the principal's recognized active roles.

Roles exist primarily to make authority assignment manageable.

They SHALL NOT become the primary application policy primitive.

Application code SHOULD generally ask:

```text
Does this principal have permission X?
```

rather than:

```text
Is this principal role Y?
```

where the required operation is fundamentally capability-based.

---

# Permission-Based Enforcement

Permissions represent application capabilities.

Permission identifiers SHALL follow the conceptual convention:

```text
resource:action[:scope]
```

Examples are illustrative only:

```text
user:read:self
user:read:any
user:delete:any
media:create
analysis:execute
```

The exact Wave 4 role and permission catalog is an implementation-planning and persistence/API concern constrained by this architecture.

This ADR does not invent the final catalog.

Where ownership affects access, self-scoped authority and broader authority SHOULD be explicit rather than inferred from role names.

Conceptually:

```text
user:read:self
        vs
user:read:any
```

---

# No Arbitrary Direct User Permissions

Arbitrary direct per-user permission grants are excluded from the Wave 4 baseline.

Authority assignment therefore follows:

```text
User
  |
  v
Roles
  |
  v
Permissions
```

rather than:

```text
User
  +--> Roles
  +--> Arbitrary Permission Overrides
```

This keeps the initial authority model understandable and auditable.

A future requirement for direct grants requires architecture review rather than silent addition.

---

# No Explicit Negative Permissions

Explicit deny permissions are excluded from the Wave 4 baseline.

The effective permission model is composed from recognized active role grants, while authorization remains deny-by-default when the required authority is absent.

This avoids precedence complexity such as:

```text
Role A grants permission
Role B denies permission
User has both
```

before Sentinel AI has a demonstrated requirement for such semantics.

---

# Deny by Default

Authorization SHALL be deny-by-default.

Conceptually:

```text
required policy
      |
      v
can authority be positively established?
      |
   +--+--+
   |     |
  yes    no / unknown / failure
   |     |
   v     v
 ALLOW  DENY
```

Absence of recognized authority never implies permission.

Unknown or malformed authorization state SHALL NOT widen access.

---

# No Implicit Administrative Bypass

No role SHALL implicitly bypass authorization.

The Wave 4 baseline SHALL NOT contain a universal:

```text
if admin:
    allow_everything
```

or:

```text
if is_superuser:
    bypass_policy()
```

Administrative roles receive authority through explicit permissions like every other role.

This means privileged access remains visible in the policy model and can be independently tested.

---

# Effective Permissions

Effective permissions SHALL be composed from recognized active roles using server-owned role-to-permission semantics.

Conceptually:

```text
Principal Roles
      |
      v
Recognized Active Roles
      |
      v
Server-Owned Role -> Permission Mapping
      |
      v
Effective Permissions
```

Unknown roles contribute zero permissions.

Unknown authority identifiers SHALL NEVER grant capabilities.

Client-supplied role or permission assertions SHALL NEVER establish trusted authority.

---

# Access JWT Authority Boundary

Access JWTs SHALL NOT contain the canonical complete permission set.

They MAY contain compact server-issued role identifiers to support efficient bounded-staleness authorization.

Conceptually:

```text
Access JWT
  |
  +-- subject / identity
  +-- session identity
  +-- compact role identifiers
  +-- temporal/security claims
```

Then:

```text
role identifiers
      |
      v
server-owned policy mapping
      |
      v
effective permissions
```

Role-to-permission semantics remain server-owned.

This prevents a large canonical permission catalog from becoming embedded into every access credential and keeps policy ownership within the application.

The exact access-token claim representation is an implementation decision provided it preserves this boundary.

---

# Bounded Authority Staleness

Because short-lived access JWTs may contain compact role identifiers, privilege reductions are subject to the bounded-staleness model established by ADR-0006.

When a privilege assignment changes:

```text
Role Assignment Change
        |
        v
Persist Authorization State
        |
        v
Revoke Affected Sessions
        |
        v
New Authentication / Access Issuance
        |
        v
New Authority Snapshot
```

Existing access authority after a privilege reduction remains bounded by the short access-token lifetime.

Privilege elevation SHALL require newly issued authority.

A stale credential SHALL NOT acquire newly granted privileges merely because the server-side role assignment changed.

---

# Resource Authorization

Permissions alone are insufficient where access depends on the relationship between the principal and the target resource.

Sentinel AI SHALL therefore support resource policies that combine capability checks with resource predicates.

Conceptually:

```text
Principal
   +
Required Permission
   +
Target Resource
   |
   v
Resource Policy
   |
   +--> ownership?
   +--> relationship?
   +--> resource state?
   |
   v
ALLOW / DENY
```

For example, an operation may require:

```text
permission: user:read:self
+
resource.user_id == principal.user_id
```

while broader authority may use a different explicit permission.

Resource ownership SHALL NOT be inferred merely because a principal is authenticated.

---

# Policy Architecture

Authorization policies SHALL be:

- Centralized.
- Declarative where practical.
- Reusable.
- Composable.
- Independently testable.
- Deny-by-default.

Policy composition SHALL support both:

- Permission predicates.
- Resource predicates.

Conceptually:

```text
Policy
├── requires permission
├── optional resource relationship
├── optional domain invariant
└── decision
```

The exact Python policy API, decorators, dependency adapters, and internal module structure are implementation details.

The architectural requirement is that authorization semantics do not become scattered across unrelated endpoints.

---

# Repository Boundary

Repository classes SHALL NOT own authorization policy.

Repositories answer persistence questions.

Authorization answers policy questions.

The architecture therefore rejects patterns such as:

```text
UserRepository.delete_if_admin(...)
```

or repositories that independently interpret role names and permissions.

A repository MAY support constrained queries required by an already-authorized use case, but it SHALL NOT become the source of authorization semantics.

---

# Domain Security Invariants

Not every security rule belongs exclusively at the HTTP boundary.

Domain security invariants SHALL remain enforceable below the HTTP layer where business correctness requires them.

API authorization and domain invariants serve different purposes:

```text
API Policy
    |
    v
May this principal request this operation?

Domain Invariant
    |
    v
Is this state transition valid regardless of transport?
```

Passing an endpoint-level permission check SHALL NOT disable domain-level correctness rules.

---

# Authentication vs Authorization Failure Semantics

Missing or invalid authentication and authenticated policy denial SHALL remain distinguishable.

Conceptually:

```text
No valid authenticated principal
        |
        v
Authentication Failure
        |
        v
401 semantics
```

versus:

```text
Valid authenticated principal
        |
        v
Policy denies operation
        |
        v
Authorization Failure
        |
        v
403 semantics
```

These failures integrate with the centralized exception-mapping architecture established before Wave 4.

Domain/application authorization services SHALL NOT require FastAPI-specific exceptions as their canonical failure representation.

---

# Resource Existence Confidentiality

Resource policies MAY intentionally hide resource existence where confidentiality requires it.

Therefore, not every policy denial must necessarily reveal:

```text
resource exists but you cannot access it
```

The API architecture may map selected resource authorization failures to non-disclosing semantics when required by the resource's confidentiality policy.

This behavior SHALL be deliberate and testable rather than accidental.

---

# Unknown Authority State

Unknown roles or authority identifiers grant no permissions.

Examples include:

```text
roles = ["future_role"]
```

when the running application does not recognize `future_role`.

That role contributes zero authority.

Similarly:

- Unknown permission identifiers.
- Malformed authority claims.
- Unknown policy identifiers.
- Failed policy resolution.

SHALL NOT create access.

---

# Authorization Failure Behavior

Authorization evaluation SHALL fail closed.

Examples include:

- Unknown role.
- Malformed role claim.
- Unknown permission mapping.
- Policy evaluation failure.
- Required resource relationship unavailable.
- Authorization persistence inconsistency.
- Uncertain authority state.

The result SHALL be denial, not implicit allowance.

Operational failures MAY be separately observable, but uncertainty SHALL NOT establish permission.

---

# Authorization Caching

Distributed authorization caching is not required for the Wave 4 baseline.

The initial role/permission policy set is expected to remain sufficiently small for straightforward application-owned policy definitions and/or the database-backed assignment model established by the persistence architecture.

Redis or equivalent distributed infrastructure SHALL NOT be introduced solely for role-to-permission caching without a demonstrated requirement and architecture review.

---

# Auditability

Security-sensitive authorization activity SHALL support auditability.

Relevant events include, where appropriate:

- Administrative operations.
- Permission denials.
- Role assignment changes.
- Account disablement.
- Credential/security changes involving privileged authority.

This ADR does NOT require indiscriminate durable logging of every successful ordinary permission check.

Detailed risk-based security-event and audit policy is governed by ADR-0010.

Authorization telemetry SHALL preserve the secret-redaction and privacy boundaries established by the broader security architecture.

---

# Tenancy

Tenant- and organization-aware authorization are deferred until Sentinel AI has an actual tenancy model.

Wave 4 SHALL NOT invent tenant identifiers, organization memberships, tenant roles, or tenant-scoped authorization merely for hypothetical future extensibility.

When tenancy is introduced, its resource and authorization model requires explicit architecture design.

---

# Security Invariants

The following invariants are mandatory:

1. Authentication and authorization remain separate security stages.
2. Sentinel AI uses RBAC for authority assignment with permission-based application enforcement.
3. Roles are administrative bundles of permissions rather than the primary policy primitive.
4. Application policy generally evaluates permissions rather than hard-coded role names.
5. Users may hold zero or more roles.
6. Roles may contain zero or more permissions.
7. Arbitrary direct per-user permission grants are excluded from the Wave 4 baseline.
8. Effective permissions are composed from recognized active roles.
9. Explicit negative permissions are excluded from the Wave 4 baseline.
10. Authorization is deny-by-default.
11. No role implicitly bypasses authorization.
12. No universal superuser authorization bypass exists in the Wave 4 baseline.
13. Access JWTs do not contain the canonical complete permission set.
14. Access JWTs may contain compact server-issued role identifiers.
15. Role-to-permission semantics remain server-owned.
16. Client-supplied role or permission assertions never establish authority.
17. Privilege changes revoke affected authentication sessions.
18. Existing access authority after privilege reduction is bounded by short access-token expiration.
19. Privilege elevation requires newly issued authority.
20. Resource ownership/relationship policy complements permission checks where required.
21. Permission identifiers follow the conceptual `resource:action[:scope]` convention.
22. Self versus broader resource authority is explicit where ownership affects access.
23. Authorization policies are centralized, reusable, composable, and independently testable.
24. Policy composition supports permission and resource predicates.
25. Repositories do not own authorization policy.
26. Domain security invariants remain enforceable below the HTTP layer.
27. Missing/invalid authentication and authenticated policy denial preserve distinct semantics.
28. Resource policies may intentionally hide resource existence where confidentiality requires it.
29. Unknown roles or authority identifiers grant no permissions.
30. Authorization evaluation failures fail closed.
31. Distributed authorization caching is not required for Wave 4.
32. Authorization security events support auditability.
33. Tenant/organization authorization is deferred until a tenancy model exists.
34. Exact initial role and permission catalogs remain implementation-planning concerns constrained by this architecture.

---

# Alternatives Considered

## Option A — RBAC with Permission-Based Enforcement

Assign roles to users, map roles to permissions, and make application policies primarily evaluate permissions and resource relationships.

### Advantages

- Roles remain manageable administrative bundles.
- Permissions provide fine-grained application semantics.
- Supports multiple roles.
- Supports least privilege.
- Avoids scattered role-name checks.
- Supports reusable resource policies.
- Keeps authority semantics server-owned.
- Scales naturally into later Sentinel AI resources.

### Disadvantages

- Requires role and permission persistence/policy definitions.
- Requires explicit policy composition.
- Privilege changes must integrate with session invalidation.
- More structure than simple role checks.

**Decision:** Accepted.

---

## Option B — Scattered Role Checks

Authorize directly with endpoint/service conditions such as:

```text
if role == admin
```

### Advantages

- Minimal initial implementation.
- Easy to understand for a very small application.

### Disadvantages

- Distributes policy throughout the codebase.
- Couples application behavior to role names.
- Encourages role proliferation.
- Makes policy review and testing difficult.
- Makes least-privilege evolution harder.

**Decision:** Rejected.

---

## Option C — Pure Direct Permission Assignment

Assign individual permissions directly to each user without roles.

### Advantages

- Fine-grained authority.
- Direct representation of capabilities.

### Disadvantages

- Creates operational complexity.
- Makes authority assignment difficult to manage.
- Produces repetitive per-user state.
- Weakens administrative consistency.

**Decision:** Not selected for the Wave 4 baseline.

---

## Option D — Complete Permission Set Embedded in JWT

Put the principal's canonical effective permission set directly in each access token.

### Advantages

- Authorization can be evaluated without role-to-permission resolution.
- Simple request-side capability checks.

### Disadvantages

- Duplicates canonical policy state into tokens.
- Can produce large tokens.
- Increases stale authorization state.
- Couples token representation to the full permission catalog.
- Weakens server ownership of role-to-permission semantics.

**Decision:** Rejected.

---

## Option E — Administrator / Superuser Allow-All Bypass

Allow a special role or boolean to bypass ordinary authorization.

### Advantages

- Simple administrative access.
- Fewer explicit privileged permissions.

### Disadvantages

- Violates least privilege.
- Creates hidden authority outside the normal policy model.
- Makes privileged behavior harder to audit and test.
- Expands the impact of role-assignment mistakes.

**Decision:** Rejected.

---

## Option F — Authorization Inside Repositories

Place authorization decisions directly inside persistence repositories.

### Advantages

- Persistence queries and policy checks can be colocated.

### Disadvantages

- Mixes persistence and policy responsibilities.
- Makes policy reuse difficult.
- Makes independent testing harder.
- Couples security semantics to storage implementation.

**Decision:** Rejected.

---

## Option G — Trust Client-Supplied Roles or Permissions

Accept role or permission assertions from request payloads, headers, or other client-controlled values.

### Advantages

- Minimal server-side resolution.

### Disadvantages

- Client-controlled input would establish privilege.
- Violates the security trust boundary.
- Enables direct privilege escalation.

**Decision:** Rejected.

---

## Option H — Unknown Policy Means Allow

Permit an operation when authorization state cannot be resolved.

### Advantages

- Fewer availability failures.

### Disadvantages

- Converts uncertainty into privilege.
- Violates deny-by-default.
- Creates catastrophic fail-open behavior.

**Decision:** Rejected.

---

## Option I — Introduce Tenant Authorization During Wave 4

Add tenant IDs, organization roles, and tenant-scoped policies before tenancy exists.

### Advantages

- Anticipates possible future requirements.

### Disadvantages

- Invents unsupported domain concepts.
- Adds persistence and policy complexity.
- Risks designing the wrong tenancy model before product requirements exist.

**Decision:** Rejected for Wave 4.

---

# Consequences

## Positive

- Authorization remains distinct from authentication.
- Roles are manageable without becoming hard-coded application policy.
- Permissions provide fine-grained, reusable authority semantics.
- The model supports multiple roles and least privilege.
- Default-deny behavior is explicit.
- Administrative authority remains inside the normal policy system.
- Resource ownership can be evaluated explicitly.
- Client-controlled authority assertions cannot establish privilege.
- Policy can be independently tested.
- Privilege changes integrate with session invalidation.
- The architecture can extend to future Sentinel AI resources without redesigning the core authorization model.

## Negative

- Wave 4 requires explicit role, permission, and mapping concepts.
- Authorization policy introduces additional application structure.
- Privilege changes require coordination with authentication-session revocation.
- Resource-level authorization requires resource context in applicable policies.
- Short-lived JWTs create intentionally bounded, rather than instantaneous, convergence after privilege reduction.
- The model requires careful distinction between policy checks and domain invariants.

These trade-offs are accepted because centralized permission-based authorization provides a stable security foundation for later Sentinel AI capabilities.

---

# Risks

Primary risks include:

- Developers scattering hard-coded role checks through routes.
- Administrative roles becoming implicit allow-all mechanisms.
- Complete permission catalogs leaking into JWTs.
- Client-supplied authority being trusted.
- Unknown roles accidentally inheriting authority.
- Policy evaluation failing open.
- Repository code becoming an authorization layer.
- Ownership checks being omitted for self-scoped operations.
- Privilege reductions failing to revoke affected sessions.
- Stale access tokens being treated as if they immediately reflect newly granted privileges.
- Premature tenant concepts contaminating the authorization model.

These risks SHALL be mitigated through:

- Centralized policy definitions.
- Permission-based enforcement.
- Explicit resource predicates.
- Deny-by-default behavior.
- Session invalidation on privilege change.
- Bounded access-token lifetime.
- Authorization-specific automated tests.
- Architecture review for authority-model changes.
- Security observability for sensitive authorization events.

---

# Implementation Notes

This ADR intentionally does not freeze:

- Exact Python class names.
- Exact policy helper names.
- Exact module paths.
- Exact initial role catalog.
- Exact initial permission catalog.
- Exact role identifiers.
- Exact database index selection.
- Exact repository method names.
- Exact policy decorator/dependency API.
- Exact access-JWT role claim name.
- Exact dependency-injection wiring.
- Exact migration decomposition.

Those are implementation decisions provided they preserve `ARC-P5-01` through `ARC-P5-34`.

The persistence architecture refines the relational representation of:

```text
roles
permissions
user_roles
role_permissions
```

without changing the policy model defined here.

Released historical migrations remain immutable; Wave 4 authorization persistence must be introduced through new Alembic revisions.

---

# Verification

ADR-0011 governs the complete Wave 4 security verification and release gates.

At minimum, implementation of this ADR requires automated evidence for:

- Authentication and authorization separation.
- Permission-based policy enforcement.
- Multi-role permission composition.
- Zero-role behavior.
- Zero-permission behavior.
- Deny-by-default behavior.
- Absence of administrator/superuser bypass.
- Unknown-role denial.
- Unknown-permission denial.
- Malformed authority-state denial.
- Client-supplied authority rejection.
- Self-resource authorization.
- Broader-resource authorization.
- Resource ownership mismatch denial.
- Permission and resource predicate composition.
- Authentication failure versus authorization denial semantics.
- Confidential resource non-disclosure where specified.
- Privilege reduction session invalidation.
- Privilege elevation requiring newly issued authority.
- Access JWTs not carrying the canonical complete permission set.
- Repository boundaries not becoming policy ownership.
- Domain invariants remaining enforceable independently of endpoint authorization.
- Authorization evaluation failure remaining fail-closed.
- Sensitive authorization events being observable according to ADR-0010.

Functional endpoint success alone is insufficient evidence that authorization policy is correctly enforced.

---

# Related Architecture Decisions

This ADR durably records the decisions frozen as:

- `ARC-P5-01` through `ARC-P5-34`.

It is constrained by:

- W4-S0C Package 1 — Security Domain & Principal Architecture.
- W4-S0C Package 3 — Session & Token Architecture.
- W4-S0C Package 5 — Authorization & Policy Architecture.
- W4-S0C Package 6 — Persistence & Migration Architecture.
- W4-S0C Package 7 — Authentication API Architecture.
- W4-S0C Package 9 — Abuse Protection & Security Observability Architecture.
- W4-S0C Package 10 — Security Verification & Testing Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.

Any implementation that conflicts with the frozen authorization invariants requires formal architecture review rather than silent deviation.

---

# References

## Existing ADRs

- ADR-0001 — Adopt a Monorepo Repository Structure.
- ADR-0002 — Adopt FastAPI Application Factory Pattern.
- ADR-0003 — Adopt an Independent Backend Python Project.
- ADR-0004 — Authentication & Security Architecture.
- ADR-0005 — Credential Storage & Password Security.
- ADR-0006 — Access Token & Stateful Refresh Session Architecture.

## Wave 4 ADRs

- ADR-0008 — Browser Authentication Transport.
- ADR-0009 — Recovery & Verification Capability Architecture.
- ADR-0010 — Abuse Protection & Security Observability.
- ADR-0011 — Security Verification & Release Gates.

## Project Documentation

- Sentinel AI Engineering Handbook.
- Sentinel AI Backend Architecture.
- W4-S0C Package 5 — Authorization & Policy Architecture.
- W4-S0C Package 6 — Persistence & Migration Architecture.
- W4-S0C Package 12 — Final Architecture Freeze.
