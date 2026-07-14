# Wave 3 Roadmap

**Project:** Sentinel AI – AI Digital Media Forensics Platform

**Wave:** 3

**Status:** Planned

**Prerequisite:** Wave 2 Complete (Persistence Foundation)

---

# Overview

Wave 3 transitions Sentinel AI from infrastructure development to application development.

With the backend architecture established during Wave 2, this wave focuses on exposing application capabilities through APIs, strengthening dependency management, improving validation, and establishing the foundation for authentication and testing.

The objective is to make the backend usable by client applications while preserving the architectural principles established in previous waves.

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

# Proposed Stories

## W3-S1

Dependency Injection Foundation

Deliverables

- Database dependency
- Service dependency
- Repository dependency
- FastAPI dependency wiring

---

## W3-S2

Request & Response Schemas

Deliverables

- User request schemas
- User response schemas
- Validation models
- Serialization conventions

---

## W3-S3

User API

Deliverables

- Create User endpoint
- Get User endpoint
- List Users endpoint
- Delete User endpoint

---

## W3-S4

Authentication Foundation

Deliverables

- Password hashing
- Registration service
- Login service
- Authentication utilities

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

---

# Expected Outcome

At the conclusion of Wave 3, Sentinel AI will evolve from a backend platform into a functional web service capable of supporting authenticated client applications through a stable, versioned REST API.

Wave 3 establishes the application layer while preserving the architectural foundations delivered in Waves 1 and 2.
