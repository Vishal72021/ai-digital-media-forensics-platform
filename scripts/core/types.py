from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal

__all__ = [
    "ExitCode",
    "CommandArguments",
    "CommandCategory",
    "CommandName",
    "CommandRegistry",
    "FileSystemPath",
]
type ExitCode = int
type CommandName = str
type CommandArguments = tuple[str, ...]
type CommandCategory = Literal["Development", "Quality", "Maintenance", "Release", "Infrastructure"]
type CommandRegistry = Mapping[CommandName, str]
type FileSystemPath = Path
