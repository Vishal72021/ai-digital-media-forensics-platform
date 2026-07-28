"""Authorization persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole


class AuthorizationRepository:
    """Provides persistence operations for authorization state."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_role_by_name(self, name: str) -> Role | None:
        """Return a role by its server-owned name."""
        statement = select(Role).where(Role.name == name)
        return self._session.scalar(statement)

    def get_permission_by_name(self, name: str) -> Permission | None:
        """Return a permission by its server-owned name."""
        statement = select(Permission).where(Permission.name == name)
        return self._session.scalar(statement)

    def list_roles_for_user(self, user_id: UUID) -> list[Role]:
        """Return the roles assigned to a user."""
        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return list(self._session.scalars(statement).all())

    def list_permissions_for_user(self, user_id: UUID) -> list[Permission]:
        """Return permissions granted to a user through assigned roles."""
        statement = (
            select(Permission)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(
                UserRole,
                UserRole.role_id == RolePermission.role_id,
            )
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        return list(self._session.scalars(statement).all())

    def add_user_role(self, user_role: UserRole) -> UserRole:
        """Add a user-role assignment to the current transaction."""
        self._session.add(user_role)
        return user_role

    def add_role_permission(
        self,
        role_permission: RolePermission,
    ) -> RolePermission:
        """Add a role-permission assignment to the current transaction."""
        self._session.add(role_permission)
        return role_permission
