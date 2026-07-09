"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI

Clean generated repository artifacts.

===============================================================================
"""

from __future__ import annotations

import shutil
from pathlib import Path

from scripts.commands import BaseCommand
from scripts.core.constants import PROJECT_ROOT
from scripts.core.exit_codes import EXIT_SUCCESS
from scripts.core.metadata import CommandMetadata
from scripts.core.types import ExitCode

__all__ = [
    "create_command",
]

_METADATA = CommandMetadata(
    identifier="clean",
    name="Clean",
    description="Remove generated repository artifacts.",
    category="Maintenance",
)


_DIRECTORIES = (
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "build",
    "dist",
)

_FILES = (".coverage",)


class CleanCommand(BaseCommand):
    """
    Remove generated repository artifacts.
    """

    def __init__(self) -> None:
        super().__init__(_METADATA)

    def run(self) -> ExitCode:
        """
        Execute repository cleanup.
        """

        for directory in _DIRECTORIES:
            self._remove_directory(PROJECT_ROOT / directory)

        for file in _FILES:
            self._remove_file(PROJECT_ROOT / file)

        return EXIT_SUCCESS

    @staticmethod
    def _remove_directory(
        path: Path,
    ) -> None:
        """
        Remove a directory if it exists.
        """

        if path.exists():
            shutil.rmtree(path)

    @staticmethod
    def _remove_file(
        path: Path,
    ) -> None:
        """
        Remove a file if it exists.
        """

        if path.exists():
            path.unlink()


def create_command() -> BaseCommand:
    """
    Create the clean command.
    """

    return CleanCommand()
