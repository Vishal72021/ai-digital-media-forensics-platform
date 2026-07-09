"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI

Run repository type checking.

===============================================================================
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
    identifier="typecheck",
    name="Type Check",
    description="Run MyPy static type checking.",
    category="Quality",
)


class TypeCheckCommand(ExternalProcessCommand):
    """
    Run MyPy.
    """

    def __init__(self) -> None:
        super().__init__(_METADATA)

    def run(self) -> ExitCode:
        """
        Execute MyPy.
        """
        result = self._execute_process(
            (
                "uv",
                "run",
                "mypy",
                ".",
            )
        )

        return result.exit_code


def create_command() -> Command:
    """
    Create a typecheck command.
    """
    return TypeCheckCommand()
