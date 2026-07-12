# Architecture Decision Records (ADRs)

## Purpose

Architecture Decision Records (ADRs) document significant technical and architectural decisions made throughout the development of Sentinel AI.

Rather than relying on commit history, meeting notes, or tribal knowledge, ADRs provide a permanent, reviewable, and version-controlled record explaining why important decisions were made.

Every accepted ADR becomes part of the engineering history of the project.

---

# Objectives

The ADR process exists to:

- Record architectural decisions.
- Preserve engineering rationale.
- Document alternatives that were considered.
- Improve onboarding for future contributors.
- Reduce repeated architectural discussions.
- Provide historical context for future changes.

---

# When to Create an ADR

Create an ADR whenever a decision significantly affects the architecture or long-term evolution of the project.

Examples include:

- Repository structure
- Technology selection
- Framework adoption
- Build systems
- Dependency management
- Deployment architecture
- Security architecture
- Data storage strategy
- API versioning strategy
- Authentication mechanisms
- Observability strategy

Routine implementation details should **not** become ADRs.

---

# ADR Lifecycle

```text
Idea
    ↓
Discussion
    ↓
Draft ADR
    ↓
Review
    ↓
Accepted
    ↓
Implementation
```

An ADR should be accepted before implementation begins whenever practical.

---

# ADR Status Values

Every ADR must include one of the following statuses.

| Status | Meaning |
|---------|---------|
| Draft | Under discussion |
| Accepted | Approved for implementation |
| Superseded | Replaced by a newer ADR |
| Deprecated | No longer recommended |
| Rejected | Considered but not adopted |

---

# Numbering

ADRs use sequential numbering.

Examples:

- ADR-0001
- ADR-0002
- ADR-0003

Numbers are never reused.

Superseded ADRs remain part of the repository history.

---

# File Naming Convention

```
ADR-0001-short-title.md
```

Examples:

```
ADR-0001-adopt-monorepo.md

ADR-0002-adopt-uv.md

ADR-0003-adopt-hatchling.md
```

---

# Repository Structure

```
docs/
└── adr/
    ├── README.md
    ├── ADR_TEMPLATE.md
    ├── ADR-INDEX.md
    ├── ADR-0001-*.md
    ├── ADR-0002-*.md
    └── ...
```

---

# Principles

Every ADR should:

- Explain the problem.
- Explain the chosen solution.
- Document rejected alternatives.
- Describe consequences.
- Be concise.
- Be immutable after acceptance except for editorial improvements.

---

# References

- Project Bible
- Engineering Handbook
- Architecture Documentation
