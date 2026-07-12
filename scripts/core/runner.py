"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/runner.py

Purpose:
    Provides the runtime implementation responsible for executing external
    commands.

The CommandRunner is the only component in the framework that interacts
directly with subprocesses.

===============================================================================
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from time import perf_counter

from scripts.core.command_result import CommandResult
from scripts.core.console import Console
from scripts.core.exceptions import ExecutionError
from scripts.core.types import CommandArguments

__all__ = [
    "CommandRunner",
]


@dataclass(slots=True)
class CommandRunner:
    """
    Execute external processes.

    Parameters
    ----------
    console
        Console used for lifecycle messages.

    working_directory
        Working directory used when executing commands.
    """

    console: Console

    working_directory: Path

    def run(
        self,
        arguments: CommandArguments,
    ) -> CommandResult:
        """
        Execute an external command.

        Parameters
        ----------
        arguments
            Command arguments passed to the operating system.

        Returns
        -------
        CommandResult
            Immutable execution result.

        Raises
        ------
        ExecutionError
            If the process could not be started.
        """

        self.console.info(
            "Running:",
            " ".join(arguments),
        )

        start = perf_counter()

        try:
            process = subprocess.run(
                arguments,
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                check=False,
            )

        except OSError as exc:
            raise ExecutionError(f"Unable to execute command: {' '.join(arguments)}") from exc

        duration = timedelta(
            seconds=perf_counter() - start,
        )

        result = CommandResult(
            arguments=arguments,
            exit_code=process.returncode,
            duration=duration,
            stdout=process.stdout,
            stderr=process.stderr,
        )

        if result.succeeded:
            self.console.success("Command completed successfully.")
        else:
            self.console.error(
                "Command exited with code",
                result.exit_code,
            )

        return result
