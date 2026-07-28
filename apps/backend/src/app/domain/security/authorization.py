"""Authorization domain types."""

from typing import NewType

RoleName = NewType("RoleName", str)
"""Server-owned authorization role identifier."""

PermissionName = NewType("PermissionName", str)
"""Server-owned authorization permission identifier."""
