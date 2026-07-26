"""Account security domain types."""

from enum import StrEnum


class AccountStatus(StrEnum):
    """Administrative account status."""

    ACTIVE = "active"
    DISABLED = "disabled"
