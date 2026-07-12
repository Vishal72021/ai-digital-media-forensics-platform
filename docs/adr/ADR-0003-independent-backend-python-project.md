# ADR-0003: Adopt an Independent Backend Python Project

- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Authors:** Sentinel AI Engineering Team

---

# Context

The Sentinel AI Digital Media Forensics Platform is being developed as a long-lived monorepository that will contain multiple independently evolving applications and shared engineering assets.

The backend API represents a standalone deployable service with its own lifecycle, dependencies, tooling, and release process.

Managing backend dependencies from the repository root would tightly couple the backend to unrelated applications, reduce isolation, and complicate dependency management as additional applications are introduced.

To support maintainability and scalability, the backend must be developed as an independent Python project while remaining part of the monorepository.

---

# Decision

The backend SHALL be implemented as an independent Python project located under:

```text
apps/backend/
```

The backend project SHALL maintain its own:

- `pyproject.toml`
- `uv.lock`
- virtual environment
- runtime dependencies
- development dependencies
- tooling configuration

The backend SHALL adopt the modern Python `src` layout.

```text
apps/backend/

├── pyproject.toml
├── uv.lock
├── src/
│   └── app/
└── tests/
```

Repository-wide tooling (for example pre-commit hooks) MAY remain centralized when they govern the entire monorepository.

---

# Consequences

## Advantages

- Clear separation between applications.
- Independent dependency management.
- Independent build and validation workflows.
- Easier future extraction into standalone repositories if required.
- Better scalability for additional applications within the monorepository.

## Trade-offs

- Duplicate tooling configuration across projects.
- Separate dependency lock files.
- Additional repository structure.

These trade-offs are acceptable given the long-term maintainability benefits.

---

# Implementation

This decision was implemented by **MR-0002 – Backend Application Foundation**.

Implementation includes:

- Independent backend project structure.
- Backend-local dependency management.
- Backend-local development tooling.
- Modern `src` package layout.
- Independent validation workflow.
- Backend application bootstrap.

---

# Alternatives Considered

## Single Repository Python Project

Manage all Python dependencies from the repository root.

**Rejected**

This approach tightly couples independent applications and does not scale well as the platform grows.

---

# Related Documents

- ARCH-0001 – Backend Application Foundation
- MR-0002 – Backend Application Foundation Review
