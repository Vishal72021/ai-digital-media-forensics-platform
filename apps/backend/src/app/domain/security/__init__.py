"""Security domain types."""

from app.domain.security.account import AccountStatus
from app.domain.security.authorization import PermissionName, RoleName

__all__ = [
    "AccountStatus",
    "PermissionName",
    "RoleName",
]
