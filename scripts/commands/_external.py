"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI

Shared base class for commands that execute external processes.

===============================================================================
"""

from __future__ import annotations

from scripts.commands import BaseCommand
from scripts.core.command_result import CommandResult
from scripts.core.console import Console
from scripts.core.constants import PROJECT_ROOT
from scripts.core.metadata import CommandMetadata
from scripts.core.runner import CommandRunner
from scripts.core.types import CommandArguments

__all__ = [
    "ExternalProcessCommand",
]


class ExternalProcessCommand(BaseCommand):
    """
    Base class for commands that execute external processes.
    """

    def __init__(self, metadata: CommandMetadata) -> None:
        """
        Lazily create a command runner.
        """
        super().__init__(metadata)
        self._runner = CommandRunner(
            console=Console(),
            working_directory=PROJECT_ROOT,
        )

    def _execute_process(
        self,
        arguments: CommandArguments,
    ) -> CommandResult:
        return self._runner.run(arguments)
