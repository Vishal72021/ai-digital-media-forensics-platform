# ADR-0001 — Adopt a Monorepo Repository Structure

| Property | Value |
|----------|-------|
| **Status** | Accepted |
| **Decision Category** | Repository Architecture |
| **Date** | 2026-07-08 |
| **Authors** | Forensix AI Engineering Team |
| **Supersedes** | None |
| **Superseded By** | None |

---

# Context

Sentinel AI is envisioned as a long-term, production-grade AI Digital Media Forensics Platform rather than a single backend application.

The platform is expected to evolve into a collection of related systems, including but not limited to:

- Backend API
- Frontend web application
- Shared Python libraries
- Shared TypeScript libraries
- SDKs
- Infrastructure-as-Code
- CI/CD automation
- Documentation
- AI models
- Internal tooling
- Deployment configurations

These components will evolve together and share a common architecture, release cadence, documentation, and engineering standards.

A repository structure must therefore support coordinated development while remaining scalable and maintainable over the lifetime of the project.

---

# Decision

Sentinel AI will adopt a **Monorepo** architecture.

All applications, shared packages, infrastructure code, documentation, automation, and engineering assets will reside within a single Git repository.

The repository will be organized into clearly defined top-level domains, including:

```text
apps/
packages/
platform/
docs/
assets/
templates/
tests/
release/
.github/
```

Each directory has a single, well-defined responsibility and ownership.

Applications may depend on shared packages, while shared packages remain independent of individual applications.

This structure is defined in the Project Bible and governed by the Repository Standards chapter.

---

# Alternatives Considered

## Option 1 — Monorepo (Selected)

### Advantages

- Single source of truth.
- Unified engineering standards.
- Shared tooling configuration.
- Simplified dependency management.
- Easier code sharing.
- Atomic cross-project changes.
- Centralized documentation.
- Simplified CI/CD pipelines.
- Consistent versioning strategy.
- Better developer onboarding.

### Disadvantages

- Larger repository over time.
- CI pipelines require careful optimization.
- Requires disciplined repository governance.

---

## Option 2 — Polyrepo

Separate repositories for each major component.

### Advantages

- Smaller repositories.
- Independent release cycles.
- Component isolation.

### Disadvantages

- Configuration duplication.
- More difficult dependency synchronization.
- Increased maintenance overhead.
- Fragmented documentation.
- Higher onboarding complexity.

---

## Option 3 — Hybrid Repository Model

Separate repositories with shared infrastructure repositories.

### Advantages

- Partial isolation.
- Shared infrastructure.

### Disadvantages

- Increased architectural complexity.
- Multiple dependency graphs.
- Difficult repository governance.
- Less suitable for a portfolio project demonstrating full-stack engineering.

---

# Decision Rationale

The engineering goals of Sentinel AI prioritize:

- Maintainability
- Shared architecture
- Consistent engineering standards
- Unified documentation
- Reproducible development
- Incremental feature delivery

A monorepo best supports these goals by enabling coordinated evolution of every component within a single engineering workflow.

Although the repository will grow over time, the benefits of centralized governance, shared tooling, and atomic changes outweigh the operational overhead.

---

# Consequences

## Positive

- One canonical repository.
- Unified Project Bible.
- Shared coding standards.
- Shared quality gates.
- Centralized Architecture Decision Records.
- Simplified contributor onboarding.
- Easier cross-component refactoring.
- Consistent release management.
- Improved traceability from design to implementation.

## Negative

- Repository size will increase over time.
- CI/CD pipelines must be designed carefully to avoid unnecessary work.
- Repository structure must remain disciplined to prevent architectural drift.

---

# Risks

Potential risks include:

- Excessive coupling between components.
- Uncontrolled growth of shared packages.
- Long-running CI workflows.
- Reduced clarity if repository boundaries are not respected.

These risks will be mitigated through:

- Clean Architecture principles.
- Repository Standards.
- Architecture Decision Records.
- Strict package ownership.
- Automated quality gates.
- Incremental architectural reviews.

---

# Implementation Notes

This decision establishes the foundational repository layout introduced during:

- Phase 1
- Wave 1
- Story W1-S1 — Repository Bootstrap

Future stories must comply with the repository structure defined by this ADR unless a subsequent ADR formally supersedes this decision.

---

# Compliance

All future additions to the repository must:

- Respect established top-level directory responsibilities.
- Avoid introducing duplicate architectural concerns.
- Follow the Repository Standards defined in the Project Bible.
- Document significant structural changes through new ADRs.

---

# Related Documentation

- Project Bible — Chapter 1: Product Definition
- Project Bible — Chapter 3: Engineering Philosophy
- Project Bible — Chapter 4: Repository Standards
- ADR-INDEX.md

---

# References

- Monorepo.tools — Monorepo Concepts
- Google Engineering Practices
- Microsoft Engineering System
- Build Systems à la Carte (Mokhov et al.)

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0 | 2026-07-08 | Initial accepted version. |
