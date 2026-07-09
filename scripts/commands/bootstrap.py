"""
Bootstrap the Sentinel AI development environment.
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
    identifier="bootstrap",
    name="Bootstrap",
    description="Prepare the development environment.",
    category="Development",
)


class BootstrapCommand(ExternalProcessCommand):
    """
    Bootstrap the development environment.
    """

    def __init__(self) -> None:
        super().__init__(_METADATA)

    def run(self) -> ExitCode:
        """
        Execute bootstrap.
        """

        commands = (
            ("uv", "sync"),
            ("uv", "run", "pre-commit", "install"),
        )

        for arguments in commands:
            result = self._execute_process(arguments)

            if result.failed:
                return result.exit_code

        return EXIT_SUCCESS


def create_command() -> Command:
    """
    Create a bootstrap command.
    """
    return BootstrapCommand()
