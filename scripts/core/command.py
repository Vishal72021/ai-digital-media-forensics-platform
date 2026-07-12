"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/command.py

Purpose:
    Defines the protocol implemented by every Developer CLI command.

A command is a self-describing executable object that exposes immutable
metadata and a single execution method.

===============================================================================
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from scripts.core.metadata import CommandMetadata
from scripts.core.types import ExitCode

__all__ = [
    "Command",
]


@runtime_checkable
class Command(Protocol):
    """
    Protocol implemented by every Developer CLI command.

    Commands are self-describing through their metadata and expose a
    single execution entry point.
    """

    @property
    def metadata(self) -> CommandMetadata:
        """
        Return immutable metadata describing this command.
        """
        ...

    def run(self) -> ExitCode:
        """
        Execute the command.

        Returns
        -------
        ExitCode
            Process exit code returned by the command.
        """
        ...
