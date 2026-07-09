"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/command_result.py

Purpose:
    Defines the immutable runtime representation of an executed command.

A CommandResult captures the outcome of executing an external process.
It is produced by the CommandRunner and consumed by higher-level
components such as the CLI, reporting, logging, or future telemetry.

This module intentionally contains no execution logic.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from scripts.core.exit_codes import EXIT_SUCCESS
from scripts.core.types import CommandArguments, ExitCode

__all__ = [
    "CommandResult",
]


@dataclass(frozen=True, slots=True)
class CommandResult:
    """
    Immutable representation of an executed command.

    Parameters
    ----------
    arguments
        Exact argument vector passed to the operating system.

    exit_code
        Exit code returned by the process.

    duration
        Total execution time.

    stdout
        Standard output captured from the process.

    stderr
        Standard error captured from the process.
    """

    arguments: CommandArguments

    exit_code: ExitCode

    duration: timedelta

    stdout: str = ""

    stderr: str = ""

    @property
    def succeeded(self) -> bool:
        """
        Return whether the command completed successfully.
        """
        return self.exit_code == EXIT_SUCCESS

    @property
    def failed(self) -> bool:
        """
        Return whether the command failed.
        """
        return not self.succeeded

    @property
    def command_line(self) -> str:
        """
        Return the executed command as a human-readable string.

        Returns
        -------
        str
            Command joined by spaces.
        """
        return " ".join(self.arguments)

    @property
    def duration_seconds(self) -> float:
        """
        Return the execution duration in seconds.

        Returns
        -------
        float
            Duration expressed in seconds.
        """
        return self.duration.total_seconds()
