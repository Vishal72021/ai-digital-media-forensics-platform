# Backend Architecture Overview

**Project:** Sentinel AI – AI Digital Media Forensics Platform

**Version:** v0.2.0

**Status:** Active

---

# Purpose

This document provides a high-level overview of the Sentinel AI backend architecture.

It serves as the primary architectural entry point for contributors before reading individual Architecture Decision Records (ADRs).

Detailed implementation decisions are documented separately in the ADR collection.

---

# Architecture Goals

The backend architecture has been designed around the following principles.

- Separation of concerns
- Single responsibility
- Layered architecture
- Explicit dependency direction
- Scalability
- Maintainability
- Testability
- Production readiness

---

# High-Level Architecture

```
                    Client Applications
                            │
                            ▼
                      FastAPI API Layer
                            │
                            ▼
                     Service Layer
                            │
                            ▼
                    Repository Layer
                            │
                            ▼
                 Persistence Infrastructure
                            │
                            ▼
                      PostgreSQL Database
```

Each layer has one clearly defined responsibility.

Dependencies always flow downward.

Lower layers never depend on higher layers.

---

# Layer Responsibilities

## API Layer

Responsibilities

- HTTP endpoints
- Request validation
- Response serialization
- Authentication (future)
- Authorization (future)

Must not contain business logic.

---

## Service Layer

Responsibilities

- Business rules
- Transaction ownership
- Repository orchestration
- Application workflows

Must not contain SQL.

---

## Repository Layer

Responsibilities

- Data persistence
- Query execution
- ORM interaction

Repositories do not own transactions.

---

## Persistence Layer

Responsibilities

- SQLAlchemy engine
- Database sessions
- Declarative base
- Alembic integration

Infrastructure only.

---

## Database

Current database

- PostgreSQL

Migration framework

- Alembic

ORM

- SQLAlchemy 2.x

---

# Current Project Structure

```
apps/backend/

src/app/

├── api/
├── core/
├── db/
├── models/
├── repositories/
├── services/
└── schemas/
```

Additional infrastructure

```
migrations/
alembic.ini
```

---

# Dependency Flow

```
API

↓

Services

↓

Repositories

↓

Database Infrastructure

↓

PostgreSQL
```

Every dependency follows this direction.

Reverse dependencies are prohibited.

---

# Architectural Principles

## Separation of Concerns

Each layer owns exactly one responsibility.

---

## Explicit Dependencies

Dependencies are injected.

Objects do not construct unrelated components internally unless explicitly documented.

---

## Transaction Ownership

Repositories

- add()
- delete()
- flush()
- refresh()

Services

- commit()
- rollback (future)

---

## Persistence Ignorance

Domain models remain independent of HTTP concerns.

---

## Configuration

Application configuration is centralized through the Settings class.

Infrastructure components consume configuration rather than maintaining duplicate configuration.

---

# Technology Stack

Framework

- FastAPI

ORM

- SQLAlchemy 2.x

Database

- PostgreSQL

Migration Tool

- Alembic

Configuration

- Pydantic Settings

Language

- Python 3.13

---

# Architecture Decision Records

The following ADRs define the detailed implementation decisions.

- ADR-0001
- ADR-0002
- ADR-0003

Future architectural changes should be documented through new ADRs rather than modifying previous decisions.

---

# Future Evolution

Planned architectural additions include

- Dependency Injection
- Authentication
- Authorization
- Background Workers
- Object Storage
- AI Processing Pipeline
- Event-driven Components
- Caching
- Monitoring
- Observability

These additions are expected to extend the existing architecture without changing the established dependency structure.

---

# Summary

The Sentinel AI backend follows a layered architecture that separates application concerns into independent components.

The architecture established in Wave 2 provides a stable foundation for future feature development while maintaining clear dependency boundaries and production-ready engineering practices.
