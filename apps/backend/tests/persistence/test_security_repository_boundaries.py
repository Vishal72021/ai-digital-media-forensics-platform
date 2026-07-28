"""Verification tests for security repository architecture boundaries."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import get_type_hints

from sqlalchemy.orm import Session

from app.repositories.security import (
    AuthorizationRepository,
    CredentialRepository,
    EmailVerificationRepository,
    PasswordRecoveryRepository,
    SessionRepository,
)

REPOSITORY_CLASSES = (
    AuthorizationRepository,
    CredentialRepository,
    EmailVerificationRepository,
    PasswordRecoveryRepository,
    SessionRepository,
)

EXPECTED_REPOSITORIES = {
    "AuthorizationRepository",
    "CredentialRepository",
    "EmailVerificationRepository",
    "PasswordRecoveryRepository",
    "SessionRepository",
}

FORBIDDEN_TRANSPORT_IMPORT_ROOTS = {
    "fastapi",
    "starlette",
}

FORBIDDEN_TRANSACTION_METHODS = {
    "commit",
    "rollback",
}

FORBIDDEN_SESSION_CONSTRUCTION = {
    "Session",
    "sessionmaker",
    "create_engine",
    "create_async_engine",
}


def _repository_module_paths() -> list[Path]:
    repository_directory = (
        Path(__file__).resolve().parents[2] / "src" / "app" / "repositories" / "security"
    )

    return sorted(path for path in repository_directory.glob("*.py") if path.name != "__init__.py")


def _parse_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _import_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)

        if isinstance(node, ast.ImportFrom) and node.module is not None:
            roots.add(node.module.split(".", maxsplit=1)[0])

    return roots


def _called_attribute_names(tree: ast.Module) -> set[str]:
    return {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }


def _called_names(tree: ast.Module) -> set[str]:
    return {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def test_frozen_security_repository_boundaries_are_exported() -> None:
    """The five frozen security repository boundaries remain public."""

    assert {repository.__name__ for repository in REPOSITORY_CLASSES} == EXPECTED_REPOSITORIES


def test_repositories_receive_existing_sqlalchemy_session() -> None:
    """Repositories receive transaction context instead of creating it."""

    for repository in REPOSITORY_CLASSES:
        type_hints = get_type_hints(repository.__init__)

        assert type_hints["session"] is Session


def test_repository_modules_are_transport_independent() -> None:
    """Persistence repositories must not depend on HTTP transport concerns."""

    for path in _repository_module_paths():
        imports = _import_roots(_parse_module(path))

        assert not imports & FORBIDDEN_TRANSPORT_IMPORT_ROOTS, (
            f"{path.name} imports transport dependencies: "
            f"{sorted(imports & FORBIDDEN_TRANSPORT_IMPORT_ROOTS)}"
        )


def test_repositories_do_not_complete_transactions() -> None:
    """Commit and rollback remain owned by the surrounding application boundary."""

    for path in _repository_module_paths():
        called_attributes = _called_attribute_names(_parse_module(path))

        assert not called_attributes & FORBIDDEN_TRANSACTION_METHODS, (
            f"{path.name} completes transactions: "
            f"{sorted(called_attributes & FORBIDDEN_TRANSACTION_METHODS)}"
        )


def test_repositories_do_not_construct_database_sessions_or_engines() -> None:
    """Repositories must operate on the injected persistence context."""

    for path in _repository_module_paths():
        called_names = _called_names(_parse_module(path))

        assert not called_names & FORBIDDEN_SESSION_CONSTRUCTION, (
            f"{path.name} constructs persistence infrastructure: "
            f"{sorted(called_names & FORBIDDEN_SESSION_CONSTRUCTION)}"
        )


def test_security_repository_responsibilities_remain_separated() -> None:
    """Security persistence remains decomposed into specialized repositories."""

    repository_methods = {
        CredentialRepository: {
            "add",
            "get_by_user_id",
        },
        AuthorizationRepository: {
            "get_role_by_name",
            "get_permission_by_name",
            "list_roles_for_user",
            "list_permissions_for_user",
            "add_user_role",
            "add_role_permission",
        },
        SessionRepository: {
            "add_session",
            "add_refresh_credential",
            "get_session_by_id",
            "get_refresh_by_selector",
        },
        PasswordRecoveryRepository: {
            "add",
            "get_by_digest",
            "list_outstanding_for_user",
        },
        EmailVerificationRepository: {
            "add",
            "get_by_digest",
            "list_outstanding_for_user",
        },
    }

    for repository, expected_methods in repository_methods.items():
        public_methods = {
            name
            for name, member in inspect.getmembers(repository, inspect.isfunction)
            if not name.startswith("_")
        }

        assert public_methods == expected_methods
