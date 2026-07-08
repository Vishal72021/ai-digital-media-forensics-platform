# PROJECT_BIBLE.md

# Chapter 4 --- Repository Standards

**Version:** 1.0\
**Status:** ✅ Frozen

## Purpose

This chapter defines the structure, ownership, and governance of the
Sentinel AI repository.

## Repository Layout

``` text
ai-digital-media-forensics-platform/
├── .github/
├── apps/
├── packages/
├── platform/
├── docs/
├── assets/
├── tests/
└── release/
```

## Directory Responsibilities

### apps/

Deployable applications only.

### packages/

Reusable shared libraries.

### platform/

Infrastructure, DevOps, deployment, automation.

### docs/

Architecture, handbook, ADRs, API documentation.

### assets/

Branding, diagrams, screenshots and media assets.

### tests/

Cross-application integration, end-to-end and performance tests.

### release/

Release notes and packaged artifacts.

## Repository Rules

-   One responsibility per directory.
-   No duplicate implementations.
-   No dead code.
-   No experimental code in production branches.
-   Documentation accompanies significant changes.
-   Tests accompany production features.

## Naming Conventions

-   snake_case → Python modules
-   PascalCase → Classes
-   UPPER_CASE → Constants
-   kebab-case → Documentation filenames where appropriate

## Branch Strategy

-   main
-   develop
-   feature/\*
-   release/\*
-   hotfix/\*

## Commit Strategy

Use Conventional Commits.

Examples: - feat: - fix: - refactor: - docs: - test: - chore:

## Repository Lifecycle

Idea → Discussion → Design → Design Freeze → Story → Implementation →
Testing → Review → Merge → Release

## Dependency Rules

-   Applications may depend on packages.
-   Packages must not depend on applications.
-   Infrastructure remains isolated from domain logic.
-   Cross-layer dependencies require architectural justification.

## Repository Governance

Repository structure changes require architectural review and
corresponding documentation updates.

## Chapter Summary

The repository is treated as a long-term architectural asset. Structure
changes are intentional, documented, and reviewed.
