"""
Run repository formatting.
"""

from __future__ import annotations

from scripts.commands._external import ExternalProcessCommand
from scripts.core.command import Command
from scripts.core.metadata import CommandMetadata
from scripts.core.types import ExitCode

__all__ = [
    "create_command",
]


_METADATA = CommandMetadata(
    identifier="format",
    name="Format",
    description="Format the repository.",
    category="Quality",
)


class FormatCommand(ExternalProcessCommand):
    """
    Format the repository.
    """

    def __init__(self) -> None:
        super().__init__(_METADATA)

    def run(self) -> ExitCode:
        """
        Execute repository formatting.
        """
        result = self._execute_process(
            (
                "uv",
                "run",
                "ruff",
                "format",
                ".",
            )
        )

        return result.exit_code


def create_command() -> Command:
    """
    Create a format command.
    """
    return FormatCommand()
