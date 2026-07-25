# Wave 3 Roadmap

**Project:** Sentinel AI – AI Digital Media Forensics Platform

**Wave:** 3

**Status:** Complete

**Release:** v0.3.0

**Completed:** 2026-07-25

**Prerequisite:** Wave 2 Complete (Persistence Foundation)

---

# Overview

Wave 3 transitions Sentinel AI from infrastructure development to application development.

With the backend architecture established during Wave 2, this wave focuses on exposing application capabilities through APIs, strengthening dependency management, improving validation, and establishing the foundation for authentication and testing.

The objective is to make the backend usable by client applications while preserving the architectural principles established in previous waves.

---

## Scope Finalization

During Wave 3 architecture review, the milestone scope was refined to focus exclusively on the API Foundation.

Authentication and authorization were separated into **Wave 4 – v0.4.0** to preserve clear architectural boundaries and avoid coupling API foundation work with security infrastructure.

Automated testing infrastructure was also deferred from the original Wave 3 proposal and is not part of the v0.3.0 release scope.

The finalized Wave 3 scope consists of:

- Dependency injection
- API schemas and validation
- Centralized exception handling
- User service behavior
- Repository pagination
- User lifecycle API endpoints
- Router integration
- OpenAPI validation
- Final integration validation

---

# Wave Objectives

The primary objectives of Wave 3 are:

- Introduce dependency injection.
- Build the API layer.
- Introduce request and response schemas.
- Implement exception handling.
- Establish authentication foundations.
- Introduce automated testing.
- Strengthen application boundaries.

---

# Engineering Themes

## Theme 1 – Application Layer

Focus:

Expose backend functionality through REST APIs.

Expected deliverables:

- API routers
- Endpoint registration
- Versioned APIs
- Dependency injection
- Request lifecycle

---

## Theme 2 – Validation

Focus:

Ensure reliable request validation.

Expected deliverables:

- Request schemas
- Response schemas
- Input validation
- Output serialization

---

## Theme 3 – Authentication Foundation

Focus:

Prepare the backend for authenticated access.

Expected deliverables:

- Password hashing
- Authentication services
- User registration workflow
- Login workflow
- Security utilities

---

## Theme 4 – Error Handling

Focus:

Introduce consistent application error handling.

Expected deliverables:

- Domain exceptions
- API exception handlers
- Error response model
- Validation error handling

---

## Theme 5 – Testing Foundation

Focus:

Establish automated testing.

Expected deliverables:

- Pytest configuration
- Repository tests
- Service tests
- API tests
- Test fixtures

---

# Delivered Stories

## W3-S1 – Dependency Injection Foundation

- Database dependency
- Repository dependency
- Service dependency
- FastAPI dependency wiring

## W3-S2 – API Schemas Foundation

- Shared schema conventions
- User request schemas
- User response schemas
- Pagination schemas
- Serialization and validation conventions

## W3-S3 – Exception Handling Framework

- Domain exception hierarchy
- API exception mapping
- Centralized exception handlers
- Consistent problem-detail responses

## W3-S4 – User API Foundation

### Package A – Service Behavior

- User service business behavior
- Domain exception translation
- Transaction handling

### Package B – Repository Pagination

- Offset/limit repository pagination
- Service pagination orchestration
- Pagination metadata

### Package C – User API (Create & Retrieve)

- Create user endpoint
- Retrieve user endpoint

### Package D – User API (List & Delete)

- Paginated user listing endpoint
- User deletion endpoint

### Package E – Integration & Validation

- API router integration
- OpenAPI validation
- Swagger UI validation
- Complete user lifecycle validation
- Final quality-gate validation

---

# Success Criteria

Wave 3 is considered complete when:

- REST API is operational.
- Dependency injection is established.
- User management endpoints are available.
- Validation is enforced.
- Authentication foundation exists.
- Automated tests are passing.

---

# Risks

Potential risks include:

- Authentication complexity
- Dependency injection design
- Test infrastructure
- API versioning decisions

These risks will be mitigated through Architecture Decision Records before implementation.

---

# Deferred Work

The following items remain outside the scope of Wave 3:

- Media upload
- AI inference pipeline
- Background processing
- Object storage integration
- Notification services
- Real-time processing
- Distributed task queues

These capabilities belong to later milestones.

## Deferred to Wave 4

- Authentication
- Authorization
- Password hashing
- Registration workflow
- Login workflow
- Security utilities

---

# Expected Outcome

At the conclusion of Wave 3, Sentinel AI will evolve from a backend platform into a functional web service capable of supporting authenticated client applications through a stable, versioned REST API.

Wave 3 establishes the application layer while preserving the architectural foundations delivered in Waves 1 and 2.
