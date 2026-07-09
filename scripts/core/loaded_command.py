"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/loaded_command.py

Purpose:
    Defines the runtime representation of a validated Developer CLI command.

A LoadedCommand is created only after a command has been successfully
discovered and validated. It provides convenient access to the command's
metadata while delegating execution to the wrapped command instance.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.core.command import Command
from scripts.core.metadata import CommandMetadata
from scripts.core.types import ExitCode

__all__ = [
    "LoadedCommand",
]


@dataclass(frozen=True, slots=True)
class LoadedCommand:
    """
    Represents a validated Developer CLI command.

    Parameters
    ----------
    command
        Command instance that satisfies the framework contract.
    """

    command: Command

    @property
    def metadata(self) -> CommandMetadata:
        """
        Return the immutable metadata describing the wrapped command.
        """
        return self.command.metadata

    @property
    def identifier(self) -> str:
        """
        Return the canonical command identifier.
        """
        return self.metadata.identifier

    @property
    def name(self) -> str:
        """
        Return the human-readable command name.
        """
        return self.metadata.name

    @property
    def description(self) -> str:
        """
        Return the command description.
        """
        return self.metadata.description

    @property
    def category(self) -> str:
        """
        Return the command category.
        """
        return self.metadata.category

    @property
    def hidden(self) -> bool:
        """
        Return whether the command is hidden from standard help output.
        """
        return self.metadata.hidden

    @property
    def experimental(self) -> bool:
        """
        Return whether the command is marked as experimental.
        """
        return self.metadata.experimental

    def run(self) -> ExitCode:
        """
        Execute the wrapped command.

        Returns
        -------
        ExitCode
            Exit code returned by the command.
        """
        return self.command.run()
