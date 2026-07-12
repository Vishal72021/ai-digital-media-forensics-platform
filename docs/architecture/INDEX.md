# Architecture Specification Index

This document serves as the master index of all Architecture Specifications within the Sentinel AI repository.

Each Architecture Specification defines the approved architecture for a major subsystem, service, or milestone.

For guidance on the Architecture Specification process, refer to `README.md`.

---

# Status Legend

| Status      | Description                                         |
| ----------- | --------------------------------------------------- |
| Draft       | Initial proposal under development.                 |
| In Review   | Under architectural review.                         |
| Approved    | Accepted for future implementation.                 |
| Frozen      | Architecture approved and implementation may begin. |
| Implemented | Architecture fully implemented.                     |
| Superseded  | Replaced by a newer specification.                  |

---

# Specifications

| ID        | Title              | Status | Milestone | Related ADRs       |
| --------- | ------------------ | ------ | --------- | ------------------ |
| ARCH-0001 | Backend Foundation | Draft  | W1-S4     | ADR-0002, ADR-0003 |

---

# Numbering Convention

Architecture Specifications SHALL use sequential identifiers.

Example:

* ARCH-0001
* ARCH-0002
* ARCH-0003

Identifiers SHALL NOT be reused.

Superseded specifications SHALL retain their original identifiers.

---

# Adding a New Architecture Specification

A new Architecture Specification SHOULD be created when introducing:

* A new subsystem
* A new deployable service
* A major architectural redesign
* Significant repository restructuring
* Major infrastructure changes

Each new specification SHALL be added to this index.

---

# References

* `README.md`
* `TEMPLATE.md`
* `../adr/INDEX.md`
