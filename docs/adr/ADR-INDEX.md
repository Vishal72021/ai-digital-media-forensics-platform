# Architecture Decision Record Index

This document provides the canonical index of Architecture Decision Records (ADRs) for Sentinel AI.

ADRs preserve significant architectural decisions, their rationale, and their long-term engineering consequences.

---

# Accepted ADRs

| ADR | Title | Decision Category |
|-----|-------|-------------------|
| ADR-0001 | Adopt a Monorepo Repository Structure | Architecture |
| ADR-0002 | Adopt FastAPI Application Factory Pattern | Backend Architecture |
| ADR-0003 | Adopt an Independent Backend Python Project | Backend Architecture |
| ADR-0004 | Authentication & Security Architecture | Security Architecture |
| ADR-0005 | Credential Storage & Password Security | Security Architecture |
| ADR-0006 | Access Token & Stateful Refresh Session Architecture | Security Architecture |
| ADR-0007 | Authorization Model — Roles & Permissions | Security Architecture |
| ADR-0008 | Browser Authentication Transport | Security Architecture |
| ADR-0009 | Recovery & Verification Capability Architecture | Security Architecture |
| ADR-0010 | Abuse Protection & Security Observability | Security Architecture |
| ADR-0011 | Security Verification & Release Gates | Security Verification Architecture |

---

# Draft ADRs

No ADRs are currently in Draft status.

---

# Superseded ADRs

No ADRs are currently superseded.

---

# Deprecated ADRs

No ADRs are currently deprecated.

---

# Rejected ADRs

No ADRs are currently recorded with Rejected status.

---

# ADR Numbering Policy

ADR identifiers are sequential and permanent.

```text
ADR-0001
ADR-0002
ADR-0003
...
```

Numbers are never reused.

If an accepted ADR is later replaced, the original ADR remains part of the repository history and is marked `Superseded` with a reference to its replacement.

---

# Wave 4 Security Architecture Baseline

Wave 4 — Authentication & Authorization establishes the following permanent security ADR baseline:

```text
ADR-0004
    Authentication & Security Architecture

ADR-0005
    Credential Storage & Password Security

ADR-0006
    Access Token & Stateful Refresh Session Architecture

ADR-0007
    Authorization Model — Roles & Permissions

ADR-0008
    Browser Authentication Transport

ADR-0009
    Recovery & Verification Capability Architecture

ADR-0010
    Abuse Protection & Security Observability

ADR-0011
    Security Verification & Release Gates
```

Together, ADR-0004 through ADR-0011 define the frozen architecture baseline governing Wave 4 implementation.

Implementation that conflicts with an accepted architectural invariant requires formal architecture review rather than silent deviation.

---

# ADR Lifecycle

```text
Draft
  |
  v
Architecture Review
  |
  v
Accepted
  |
  v
Implementation
  |
  +----------------------+
  |                      |
  v                      v
Remains Accepted     Superseded
                         |
                         v
                   Replacement ADR
```

Acceptance records the architectural decision.

Implementation status is tracked separately through project roadmaps, engineering reviews, and release documentation.

---

# Related Documentation

- `docs/adr/README.md`
- `docs/adr/ADR_TEMPLATE.md`
- `docs/architecture/`
- `docs/roadmap/`
- `docs/reviews/`
- `CONTRIBUTING.md`
- `ROADMAP.md`
