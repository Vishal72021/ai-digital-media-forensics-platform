"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI

Run repository linting.

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
    identifier="lint",
    name="Lint",
    description="Run Ruff linting.",
    category="Quality",
)


class LintCommand(ExternalProcessCommand):
    """
    Run Ruff linting.
    """

    def __init__(self) -> None:
        super().__init__(_METADATA)

    def run(self) -> ExitCode:
        """
        Execute linting.
        """
        result = self._execute_process(
            (
                "uv",
                "run",
                "ruff",
                "check",
                ".",
            )
        )

        return result.exit_code


def create_command() -> Command:
    """
    Create a lint command.
    """
    return LintCommand()
