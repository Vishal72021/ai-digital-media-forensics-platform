"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/console.py

Purpose:
    Provides a lightweight abstraction over standard console output for the
    Sentinel AI Developer CLI.

The Console is responsible only for formatting and writing user-facing
messages to stdout and stderr.

It intentionally does not implement logging, colors, timestamps,
verbosity levels, or Rich integration. Those concerns belong to future
enhancements.

===============================================================================
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Final, TextIO

__all__ = [
    "Console",
]


_INFO_PREFIX: Final[str] = "[INFO]"
_SUCCESS_PREFIX: Final[str] = "[ OK ]"
_WARNING_PREFIX: Final[str] = "[WARN]"
_ERROR_PREFIX: Final[str] = "[FAIL]"


@dataclass(slots=True)
class Console:
    """
    Lightweight console output service.

    Parameters
    ----------
    stdout
        Stream used for informational output.

    stderr
        Stream used for warning and error output.
    """

    stdout: TextIO = field(default_factory=lambda: sys.stdout)

    stderr: TextIO = field(default_factory=lambda: sys.stderr)

    def info(self, *parts: object, sep: str = " ") -> None:
        """
        Write an informational message.
        """
        self._write(
            self.stdout,
            _INFO_PREFIX,
            *parts,
            sep=sep,
        )

    def success(self, *parts: object, sep: str = " ") -> None:
        """
        Write a success message.
        """
        self._write(
            self.stdout,
            _SUCCESS_PREFIX,
            *parts,
            sep=sep,
        )

    def warning(self, *parts: object, sep: str = " ") -> None:
        """
        Write a warning message.
        """
        self._write(
            self.stderr,
            _WARNING_PREFIX,
            *parts,
            sep=sep,
        )

    def error(self, *parts: object, sep: str = " ") -> None:
        """
        Write an error message.
        """
        self._write(
            self.stderr,
            _ERROR_PREFIX,
            *parts,
            sep=sep,
        )

    @staticmethod
    def _write(
        stream: TextIO,
        prefix: str,
        *parts: object,
        sep: str,
    ) -> None:
        """
        Format and write a message to the specified stream.

        Parameters
        ----------
        stream
            Destination output stream.

        prefix
            Message prefix.

        parts
            Objects to be written.

        sep
            Separator used when joining message parts.
        """
        message = sep.join(str(part) for part in parts)

        print(
            f"{prefix} {message}",
            file=stream,
        )
