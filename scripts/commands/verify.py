"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI

Run the complete repository verification pipeline.

===============================================================================
"""

from __future__ import annotations

from scripts.commands._external import ExternalProcessCommand
from scripts.core.command import Command
from scripts.core.exit_codes import EXIT_SUCCESS
from scripts.core.metadata import CommandMetadata
from scripts.core.types import ExitCode

__all__ = [
    "create_command",
]

_METADATA = CommandMetadata(
    identifier="verify",
    name="Verify",
    description="Run the complete repository verification pipeline.",
    category="Quality",
)

_COMMANDS = (
    (
        "uv",
        "run",
        "ruff",
        "format",
        ".",
    ),
    (
        "uv",
        "run",
        "ruff",
        "check",
        ".",
    ),
    (
        "uv",
        "run",
        "mypy",
        ".",
    ),
    (
        "uv",
        "run",
        "pre-commit",
        "run",
        "--all-files",
    ),
)


class VerifyCommand(ExternalProcessCommand):
    """
    Run the repository verification pipeline.
    """

    def __init__(self) -> None:
        super().__init__(_METADATA)

    def run(self) -> ExitCode:
        """
        Execute the verification pipeline.
        """

        for arguments in _COMMANDS:
            result = self._execute_process(arguments)

            if result.failed:
                return result.exit_code

        return EXIT_SUCCESS


def create_command() -> Command:
    """
    Create the verify command.
    """

    return VerifyCommand()
