from __future__ import annotations

from typing import Final

__all__ = [
    "EXIT_SUCCESS",
    "EXIT_FAILURE",
    "EXIT_INVALID_USAGE",
    "EXIT_CONFIGURATION_ERROR",
    "EXIT_EXTERNAL_COMMAND_ERROR",
]
EXIT_SUCCESS: Final[int] = 0
EXIT_FAILURE: Final[int] = 1
EXIT_INVALID_USAGE: Final[int] = 2
EXIT_CONFIGURATION_ERROR: Final[int] = 3
EXIT_EXTERNAL_COMMAND_ERROR: Final[int] = 4
