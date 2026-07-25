# Changelog

All notable changes to **Sentinel AI** will be documented in this file.

The project follows a milestone-based development process where each release represents the completion of a development wave. Releases are versioned using Semantic Versioning (SemVer).

---

## [Unreleased]

### Planned

- Wave 4 – Authentication & Authorization

---

## [v0.3.0] - 2026-07-25

### Milestone

**Wave 3 – API Foundation**

### Added

- FastAPI dependency injection foundation
- Request-scoped database session dependencies
- Repository and service dependency providers
- Shared API schema conventions
- User request and response schemas
- Pagination schemas and metadata
- Domain exception hierarchy
- Centralized API exception mapping and handling
- User creation endpoint
- User retrieval endpoint
- Paginated user listing endpoint
- User deletion endpoint
- Repository pagination support
- Service-layer pagination behavior
- Versioned user API router integration

### Engineering

- Strictly typed dependency boundaries
- Typed service pagination model
- Consistent API problem-detail responses
- Backend-local Ruff and MyPy configuration
- Pydantic MyPy integration
- Runtime email validation support
- Repository-wide pre-commit integration with the backend environment
- Python 3.13 backend toolchain alignment
- Reproducible backend dependency locking

### Validation

- User create lifecycle validated
- User retrieval lifecycle validated
- User listing and pagination validated
- User deletion lifecycle validated
- API error behavior validated
- OpenAPI schema validated
- Swagger UI endpoints validated
- Ruff linting passed
- Ruff formatting passed
- Strict MyPy validation passed
- Pre-commit quality gates passed
- Lockfile consistency validation passed
- Post-merge integration gate passed

### Documentation

- Wave 3 Engineering Review
- Updated Wave 3 Roadmap
- Wave 4 scope established as Authentication & Authorization

---

## [v0.2.0] - 2026-07-14

### Milestone

**MR-0003 – Persistence Foundation**

### Added

- SQLAlchemy 2.x persistence layer
- PostgreSQL integration
- Alembic migration framework
- Database session management
- Declarative ORM foundation
- User domain model
- Initial database schema
- Repository layer
- Service layer
- Environment-based configuration
- Production-oriented project structure

### Engineering

- Architecture-first development workflow
- Strict MyPy type checking
- Ruff formatting and linting
- Pre-commit quality gates
- Structured Git workflow
- Release engineering process

### Documentation

- Backend Architecture Overview
- Wave 2 Engineering Review
- Architecture Decision Records (ADR-0001, ADR-0002, ADR-0003)
- Release Notes for v0.2.0
- Wave 3 Roadmap
- Repository Roadmap
- Comprehensive README
- Engineering Handbook (CONTRIBUTING.md)

---

## [v0.1.0] - 2026-07-01

### Milestone

**MR-0002 – Backend Foundation**

### Added

- Repository bootstrap
- Monorepo structure
- FastAPI backend foundation
- Development tooling
- Project configuration
- Initial architecture documentation
- Development automation
- Branch protection and engineering workflow

---

## Versioning Policy

Sentinel AI follows **Semantic Versioning (SemVer)**.

- **Major** releases introduce significant architectural or platform changes.
- **Minor** releases introduce completed engineering waves and new functionality.
- **Patch** releases include bug fixes, documentation improvements, and minor enhancements.

---

## Release Process

Every release follows the same engineering lifecycle:

1. Architecture Review
2. Architecture Freeze
3. Incremental Implementation
4. Quality Validation
5. Documentation Update
6. Wave Review
7. Merge into `main`
8. Version Tag
9. GitHub Release

This process ensures that every published release is stable, reproducible, and fully documented.
