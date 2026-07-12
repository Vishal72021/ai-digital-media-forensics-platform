"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI

Base command implementation.

===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from scripts.core.command import Command
from scripts.core.metadata import CommandMetadata
from scripts.core.types import ExitCode

__all__ = [
    "BaseCommand",
]


class BaseCommand(
    Command,
    ABC,
):
    """
    Shared implementation for built-in Developer CLI commands.

    Every command owns immutable metadata and implements the
    ``run()`` execution method.
    """

    def __init__(
        self,
        metadata: CommandMetadata,
    ) -> None:
        self._metadata = metadata

    @property
    def metadata(
        self,
    ) -> CommandMetadata:
        """
        Return immutable command metadata.
        """
        return self._metadata

    @abstractmethod
    def run(
        self,
    ) -> ExitCode:
        """
        Execute the command.

        Returns
        -------
        ExitCode
            Process exit code.
        """
        raise NotImplementedError
