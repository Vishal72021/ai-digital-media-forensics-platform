# Contributing to Sentinel AI

First and foremost, thank you for your interest in contributing to **Sentinel AI**.

Whether you are improving the architecture, implementing new features, fixing bugs, expanding documentation, writing tests, or proposing new ideas, your contribution helps move the project closer to its vision of becoming a production-grade AI Digital Media Forensics Platform.

Unlike many open-source projects that focus primarily on feature development, Sentinel AI places equal emphasis on **software engineering discipline**. Every contribution is expected to uphold the project's standards for architecture, code quality, documentation, and maintainability.

This document serves as the **Engineering Handbook** for Sentinel AI. It describes the development philosophy, engineering workflow, coding standards, review process, and release practices that guide every milestone.

---

## Table of Contents

- [Purpose](#purpose)
- [Engineering Philosophy](#engineering-philosophy)
  - [Architecture Before Implementation](#1-architecture-before-implementation)
  - [Incremental Development](#2-incremental-development)
  - [Separation of Concerns](#3-separation-of-concerns)
  - [Production-Oriented Engineering](#4-production-oriented-engineering)
  - [Documentation-Driven Development](#5-documentation-driven-development)
  - [Continuous Quality](#6-continuous-quality)
- [Core Engineering Principles](#core-engineering-principles)
- [Project Organization](#project-organization)
  - [Repository Structure](#repository-structure)
  - [Directory Responsibilities](#directory-responsibilities)
- [Development Workflow](#development-workflow)
- [Git Workflow](#git-workflow)
  - [Branch Strategy](#branch-strategy)
  - [Main Branch](#main-branch)
  - [Develop Branch](#develop-branch)
  - [Feature Branches](#feature-branches)
- [Commit Convention](#commit-convention)
  - [Commit Types](#commit-types)
- [Coding Standards](#coding-standards)
  - [General Guidelines](#general-guidelines)
  - [Python Standards](#python-standards)
  - [Layer Responsibilities](#layer-responsibilities)
  - [Dependency Management](#dependency-management)
- [Documentation Standards](#documentation-standards)
- [Quality Gates](#quality-gates)
- [Pull Request Checklist](#pull-request-checklist)
- [Definition of Done](#definition-of-done)
- [Code Review](#code-review)
  - [Review Objectives](#review-objectives)
  - [Architectural Review](#architectural-review)
- [Release Process](#release-process)
  - [Release Lifecycle](#release-lifecycle)
  - [Release Checklist](#release-checklist)
- [Continuous Improvement](#continuous-improvement)
- [Thank You](#thank-you)

--

# Purpose

The objective of this guide is to ensure that every contribution:

- Preserves the architectural integrity of the platform.
- Follows established engineering standards.
- Maintains long-term maintainability.
- Integrates cleanly into the existing codebase.
- Includes appropriate documentation.
- Meets all quality validation requirements before review.

By following these practices, contributors help ensure that Sentinel AI evolves as a cohesive and scalable software platform rather than a collection of isolated features.

---

# Engineering Philosophy

Sentinel AI is built around an **architecture-first development methodology**.

Rather than immediately implementing features, development begins with understanding the problem, designing an appropriate solution, reviewing the architecture, and documenting key decisions before writing production code.

This philosophy emphasizes deliberate engineering over rapid implementation and aims to minimize technical debt while supporting long-term scalability.

The following principles guide every engineering decision throughout the project.

---

## 1. Architecture Before Implementation

Every significant feature begins with architectural planning.

Before implementation starts:

- Requirements are understood.
- Architectural options are evaluated.
- The preferred design is reviewed.
- The architecture is frozen.
- Implementation proceeds only after approval.

Major architectural decisions are documented using **Architecture Decision Records (ADRs)** to ensure that design choices remain transparent and reproducible.

---

## 2. Incremental Development

Development is divided into small, reviewable milestones.

Large implementations are intentionally avoided in favor of incremental progress that can be validated independently.

Every milestone should leave the project in a stable, releasable state.

---

## 3. Separation of Concerns

Each component should have one clearly defined responsibility.

Examples include:

- API layer for HTTP concerns.
- Service layer for business logic.
- Repository layer for persistence.
- Infrastructure layer for technical integrations.

Responsibilities should never overlap unnecessarily.

---

## 4. Production-Oriented Engineering

Sentinel AI is developed as though it were intended for long-term production use.

Engineering quality is considered equally important as functionality.

Every contribution should improve one or more of the following:

- Maintainability
- Readability
- Scalability
- Testability
- Documentation
- Reliability

---

## 5. Documentation-Driven Development

Documentation evolves together with the implementation.

New architectural decisions, engineering reviews, release notes, and roadmap updates should accompany the code whenever applicable.

Documentation is considered part of the feature—not an optional afterthought.

---

## 6. Continuous Quality

Every change is expected to satisfy the project's automated quality standards before review.

Quality validation includes formatting, linting, static type checking, and pre-commit verification.

Automation is used to maintain consistency across the project while allowing contributors to focus on solving engineering problems.

---

# Core Engineering Principles

Every contribution should strive to uphold the following principles.

| Principle | Description |
|-----------|-------------|
| **Single Responsibility** | Every module should have one well-defined purpose. |
| **Explicit Dependencies** | Dependencies should be injected or clearly declared rather than hidden. |
| **Consistency** | Follow existing project conventions instead of introducing new patterns unnecessarily. |
| **Readability** | Code should be understandable before it is optimized. |
| **Scalability** | Design with future growth in mind rather than immediate convenience. |
| **Maintainability** | Prefer simple, extensible solutions over complex abstractions. |
| **Documentation** | Architectural decisions and implementation details should be documented when appropriate. |
| **Quality** | Every contribution should pass all quality gates before review. |

These principles provide the foundation upon which every engineering decision within Sentinel AI is evaluated.

---

# Project Organization

Sentinel AI is organized to promote clear separation between application code, engineering documentation, and development tooling. Every top-level directory has a well-defined purpose, making the repository easier to navigate and maintain as the project grows.

The project follows a modular monorepo structure, allowing multiple applications and shared tooling to coexist while remaining independently maintainable.

## Repository Structure

```text
Sentinel AI
│
├── apps/
│   └── backend/                 FastAPI backend application
│
├── docs/
│   ├── architecture/            Architecture documentation & ADRs
│   ├── release-notes/           Release documentation
│   ├── reviews/                 Engineering milestone reviews
│   ├── roadmap/                 Wave planning
│   └── design/                  Design specifications
│
├── scripts/                     Development automation
│
├── README.md                    Project overview
├── ROADMAP.md                   Long-term product roadmap
├── CONTRIBUTING.md              Engineering handbook
├── CHANGELOG.md                 Release history
└── LICENSE                      Project license
```

## Directory Responsibilities

| Directory | Responsibility |
|-----------|----------------|
| **apps/** | Contains all production applications developed within Sentinel AI. |
| **apps/backend/** | Backend services, APIs, persistence, business logic, and infrastructure. |
| **docs/** | Engineering documentation, architectural decisions, milestone reviews, and planning artifacts. |
| **scripts/** | Automation scripts used during development and maintenance. |

Every new file should have a clear purpose and belong to the most appropriate directory. Contributors should avoid introducing unnecessary folders or duplicate organizational structures.

---

# Development Workflow

Sentinel AI follows a structured engineering workflow designed to reduce technical debt, encourage thoughtful design, and ensure every feature is implemented consistently.

Every milestone progresses through the same lifecycle.

```text
Requirements
      │
      ▼
Architecture Review
      │
      ▼
Architecture Freeze
      │
      ▼
Incremental Implementation
      │
      ▼
Quality Validation
      │
      ▼
Documentation Update
      │
      ▼
Pull Request Review
      │
      ▼
Merge into Develop
      │
      ▼
Release Review
      │
      ▼
Merge into Main
      │
      ▼
Version Tag & Release
```

Each stage has a specific objective and should not be skipped.

---

## 1. Requirements

Every milestone begins by understanding the problem being solved.

Contributors should clearly define:

- The objective.
- The expected outcome.
- Architectural constraints.
- Scope boundaries.

A well-understood problem significantly reduces unnecessary implementation changes later.

---

## 2. Architecture Review

Before implementation begins, the proposed architecture is reviewed.

The review evaluates:

- Overall design.
- Layer responsibilities.
- Dependency direction.
- Scalability.
- Maintainability.
- Consistency with existing architecture.

Large implementation efforts should never begin without architectural agreement.

---

## 3. Architecture Freeze

Once the design has been approved, it becomes the implementation contract.

During implementation:

- Avoid redesigning components.
- Avoid introducing new architectural patterns without discussion.
- Focus on executing the approved design.

If significant architectural changes become necessary, pause implementation and perform another architecture review.

---

## 4. Incremental Implementation

Implementation should be divided into small, reviewable packages.

Each package should:

- Solve one clearly defined problem.
- Compile successfully.
- Pass all quality gates.
- Integrate cleanly with previous work.

Large unreviewable commits should be avoided.

---

## 5. Quality Validation

Before any code review, contributors must verify that the implementation satisfies all automated quality checks.

These include:

- Formatting
- Linting
- Static type checking
- Pre-commit validation
- Migration verification (when applicable)

No feature should proceed to review while failing automated validation.

---

## 6. Documentation Update

Documentation evolves together with implementation.

Depending on the scope of the change, contributors may need to update:

- Architecture documentation
- ADRs
- Release notes
- Roadmaps
- README
- Developer documentation

Documentation should accurately reflect the current state of the project.

---

## 7. Pull Request Review

Every completed milestone is submitted through a Pull Request.

Reviews should evaluate:

- Architectural consistency.
- Code quality.
- Documentation completeness.
- Validation results.
- Overall maintainability.

Feedback should be constructive, objective, and focused on improving the project.

---

## 8. Integration

Completed features are merged into the **develop** branch after successful review.

The **develop** branch serves as the integration branch for active development.

The **main** branch is reserved for stable milestone releases.

---

## 9. Release

At the completion of a wave:

- Engineering review is performed.
- Documentation is finalized.
- Release notes are prepared.
- The release is merged into **main**.
- A version tag is created.
- A GitHub Release is published.

This ensures every release is stable, documented, and reproducible.

---

# Engineering Lifecycle

The engineering lifecycle can be summarized as:

```text
Think
   ↓
Design
   ↓
Review
   ↓
Freeze
   ↓
Build
   ↓
Validate
   ↓
Document
   ↓
Review
   ↓
Release
```

Following this process consistently has been fundamental to the successful delivery of the Sentinel AI platform and will continue to guide future development.

---

# Git Workflow

Sentinel AI follows a structured Git workflow that separates feature development, integration, and stable releases.

The objective is to ensure that the **main** branch always represents a stable and releasable state while allowing active development to continue safely within **develop**.

## Branch Strategy

```
                     feature/wX-sY
                           │
                           ▼
                     Pull Request
                           │
                           ▼
                        develop
                           │
                 Wave Review & Validation
                           │
                           ▼
                     Pull Request
                           │
                           ▼
                          main
                           │
                           ▼
                    Version Tag & Release
```

### Main Branch

The **main** branch always contains stable, production-ready releases.

Direct commits to **main** are not permitted.

Only reviewed and validated milestone releases should be merged into this branch.

---

### Develop Branch

The **develop** branch serves as the primary integration branch.

Completed features are merged here after successful implementation and review.

Every development wave is assembled and validated on this branch before being promoted to **main**.

---

### Feature Branches

All implementation work must be performed on feature branches.

Feature branches should be created from **develop**.

Naming convention:

```text
feature/w3-s1
feature/w3-s2
feature/w4-s1
```

Each branch should represent a single engineering story or milestone.

---

# Commit Convention

Sentinel AI follows the Conventional Commits specification to maintain a clean and meaningful project history.

## Format

```text
<type>(scope): short description
```

Example:

```text
feat(api): implement user registration endpoint

build(persistence): configure SQLAlchemy session factory

docs(release): finalize wave 2 documentation

refactor(repository): simplify query construction
```

---

## Commit Types

| Type | Purpose |
|------|---------|
| **feat** | New functionality |
| **fix** | Bug fixes |
| **build** | Build system, infrastructure, configuration |
| **docs** | Documentation updates |
| **refactor** | Internal improvements without behavior changes |
| **test** | Tests and testing infrastructure |
| **chore** | Maintenance tasks |

Commits should remain focused on a single logical change.

Avoid combining unrelated changes into a single commit.

---

# Coding Standards

Code should prioritize readability, maintainability, and consistency over unnecessary complexity.

## General Guidelines

- Write self-explanatory code.
- Prefer descriptive names over abbreviations.
- Keep functions focused on one responsibility.
- Minimize duplication.
- Avoid premature optimization.
- Follow existing project conventions.

---

## Python Standards

All production code should:

- Use Python type hints.
- Include meaningful docstrings.
- Follow PEP 8 conventions.
- Prefer composition over inheritance when appropriate.
- Avoid global mutable state.

---

## Layer Responsibilities

Contributors should respect architectural boundaries.

| Layer | Responsibility |
|--------|----------------|
| API | HTTP requests and responses |
| Services | Business logic and workflows |
| Repositories | Persistence operations |
| Models | Domain representation |
| Infrastructure | Database, configuration, external integrations |

Business logic should never bypass the Service layer.

Repositories should never implement business rules.

---

## Dependency Management

Dependencies should be explicit.

Avoid hidden coupling between modules.

Where practical, components should receive their collaborators through dependency injection rather than constructing them internally.

---

# Documentation Standards

Documentation is considered part of every contribution.

Depending on the scope of the change, contributors should update:

- README
- ROADMAP
- ADRs
- Architecture documentation
- Release notes
- Engineering reviews
- API documentation (future)

Documentation should accurately describe the current implementation.

Outdated documentation should be corrected as part of the same contribution.

---

# Quality Gates

Every contribution must successfully pass the project's automated validation before review.

## Code Formatting

```bash
uv run ruff format .
```

---

## Linting

```bash
uv run ruff check . --fix

uv run ruff check .
```

---

## Static Type Checking

```bash
uv run mypy src
```

---

## Pre-commit Validation

From the repository root:

```bash
uv run pre-commit run --all-files
```

---

## Database Validation

When database changes are introduced:

```bash
uv run alembic current

uv run alembic upgrade head
```

Migration scripts should be reviewed before they are committed.

---

# Pull Request Checklist

Before opening a Pull Request, verify that:

- Architecture follows the approved design.
- All quality gates pass successfully.
- Code is fully documented where appropriate.
- Related documentation has been updated.
- Commit history is clean and meaningful.
- No temporary debugging code remains.
- The implementation is ready for review.

Pull Requests should clearly explain:

- What changed.
- Why it changed.
- Any architectural implications.
- Any follow-up work that remains.

---

# Definition of Done

A contribution is considered complete only when:

- Implementation is finished.
- Quality gates pass.
- Documentation is updated.
- Review feedback has been addressed.
- The feature has been merged into **develop**.

Completion is defined by engineering quality rather than code alone.

---

# Code Review

Every contribution to Sentinel AI undergoes code review before it is integrated into the project.

The objective of code review is not only to identify defects but also to ensure architectural consistency, maintainability, readability, and long-term sustainability.

Reviews should remain collaborative, constructive, and focused on improving the overall quality of the project.

---

## Review Objectives

During review, contributors should evaluate whether the implementation:

- Solves the intended problem.
- Preserves the approved architecture.
- Respects layer responsibilities.
- Maintains readability and consistency.
- Avoids unnecessary complexity.
- Includes appropriate documentation.
- Passes all quality validation requirements.

Code review is considered an engineering discussion rather than a gatekeeping exercise.

---

## Architectural Review

Certain changes require architectural discussion before they are approved.

Examples include:

- Introducing a new dependency.
- Creating a new architectural layer.
- Changing dependency direction.
- Modifying project structure.
- Introducing new design patterns.
- Changing public interfaces.
- Significant database schema redesign.

When architectural uncertainty exists, discussion should occur before implementation continues.

---

# Release Process

Sentinel AI follows milestone-based releases.

Individual features are grouped into engineering waves, and completed waves become official project releases.

The release process ensures every published version is stable, documented, and reproducible.

---

## Release Lifecycle

```text
Feature Branch
      │
      ▼
Architecture Review
      │
      ▼
Implementation
      │
      ▼
Quality Validation
      │
      ▼
Documentation Update
      │
      ▼
Pull Request
      │
      ▼
Merge into Develop
      │
      ▼
Wave Review
      │
      ▼
Release Documentation
      │
      ▼
Merge into Main
      │
      ▼
Version Tag
      │
      ▼
GitHub Release
```

Every stage contributes to the quality of the final release.

---

## Release Checklist

Before a wave is merged into **main**, verify that:

### Engineering

- All planned stories are complete.
- Architectural objectives have been achieved.
- Technical debt has been reviewed.
- Outstanding risks have been documented.

### Quality

- Ruff formatting passes.
- Ruff linting passes.
- MyPy passes.
- Pre-commit hooks pass.
- Database migrations are validated.

### Documentation

- README reflects the current project state.
- ROADMAP has been updated.
- Architecture documentation is current.
- Wave review has been completed.
- Release notes have been prepared.
- CHANGELOG has been updated.

### Repository

- Feature branches have been merged into **develop**.
- Develop has been fully validated.
- Pull Request to **main** has been reviewed.
- Release tag has been created.
- GitHub Release has been published.

---

# Definition of Done

A feature is considered complete only when all of the following are true:

- The implementation satisfies its functional requirements.
- The approved architecture has been respected.
- All quality gates pass successfully.
- Documentation has been updated.
- Review feedback has been resolved.
- The feature has been merged into **develop**.

A release is considered complete only when:

- Wave review has been approved.
- Documentation has been finalized.
- The release has been merged into **main**.
- A version tag has been created.
- The corresponding GitHub Release has been published.

Completion is measured by engineering quality rather than code volume.

---

# Continuous Improvement

Sentinel AI is an evolving project.

Engineering practices, tooling, workflows, and architectural guidelines will continue to improve as the platform grows.

Contributors are encouraged to propose improvements not only to the implementation but also to the engineering process itself.

Constructive discussion and continuous refinement are essential parts of building a sustainable software platform.

---

# Thank You

Every contribution—whether it is code, documentation, testing, architectural review, or design discussion—helps strengthen Sentinel AI.

By contributing thoughtfully and following the engineering practices described in this handbook, you help ensure that the project remains maintainable, scalable, and valuable to future contributors.

Thank you for helping build Sentinel AI.

---

<div align="center">

## Sentinel AI

### Engineering First. AI Second.

*Building trust in digital media through explainable AI and production-grade software engineering.*

**Current Release**

**v0.2.0 – Persistence Foundation**

**Next Milestone**

**Wave 3 – Application Foundation**

</div>
