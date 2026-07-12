# ADR-0002: Adopt FastAPI Application Factory Pattern

## Status

Accepted

---

## Context

Sentinel AI is being designed as an enterprise-grade AI Digital Media Forensics Platform with a long-term roadmap that includes database integrations, background workers, AI model serving, observability, authentication, and cloud deployment.

As the application grows, application startup will require coordinated initialization of multiple infrastructure components, including:

* Configuration
* Logging
* Middleware
* Exception handlers
* API routing
* Database connections
* Background task orchestration
* Health checks
* Observability
* Security components

Instantiating the `FastAPI` application directly inside the ASGI entry point would tightly couple application construction with application execution, making testing, extensibility, and future initialization logic more difficult.

---

## Decision

The backend shall adopt the Application Factory pattern.

Application construction shall be centralized within a single factory function:

```python
create_application() -> FastAPI
```

The ASGI entry point (`main.py`) shall only expose the application instance:

```python
from app.factory import create_application

app = create_application()
```

No other module shall instantiate `FastAPI` directly.

All future application configuration shall be composed within the factory, including but not limited to:

* Application metadata
* Lifespan management
* Middleware
* Exception handlers
* API routers
* Dependency overrides
* OpenAPI customization
* Observability configuration

---

## Consequences

### Positive

* Establishes a single composition root for the application.
* Simplifies testing by allowing isolated application instances.
* Centralizes startup configuration.
* Prevents duplicated initialization logic.
* Supports future dependency injection patterns.
* Encourages clean architectural boundaries.

### Negative

* Introduces an additional abstraction layer compared to direct instantiation.
* Requires all application initialization to remain coordinated through the factory.

---

## Alternatives Considered

### Instantiate FastAPI directly in `main.py`

Rejected.

While suitable for small applications, direct instantiation does not scale well as startup responsibilities increase and makes centralized configuration more difficult.

### Global application object

Rejected.

A globally constructed application couples initialization with module import order and reduces flexibility for testing and future runtime customization.

---

## References

* FastAPI Application Structure
* Clean Architecture Principles
* Sentinel AI Architectural Guidelines
