# Changelog

All notable changes to **Sentinel AI** will be documented in this file.

The project follows a milestone-based development process where each release represents the completion of a development wave. Releases are versioned using Semantic Versioning (SemVer).

---

## [Unreleased]

### Planned

- Wave 3 – Application Foundation
- Dependency Injection
- REST API
- Request & Response Validation
- Authentication Foundation
- Automated Testing Infrastructure

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
