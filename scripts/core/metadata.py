"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/metadata.py

Purpose:
    Defines immutable metadata describing Developer CLI commands.

Command metadata contains descriptive information used by discovery,
help generation, validation, and command registration.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from scripts.core.types import CommandCategory

__all__ = [
    "CommandMetadata",
]


@dataclass(
    frozen=True,
    slots=True,
)
class CommandMetadata:
    """
    Immutable metadata describing a Developer CLI command.

    Parameters
    ----------
    identifier
        Canonical internal command identifier.

    name
        Human-readable command name.

    description
        Brief description displayed in CLI help.

    category
        Functional command category.

    aliases
        Alternative command names.

    hidden
        Whether the command should be omitted from normal help output.

    experimental
        Indicates that the command is experimental and may change.
    """

    identifier: str

    name: str

    description: str

    category: CommandCategory

    aliases: tuple[str, ...] = field(default_factory=tuple)

    hidden: bool = False

    experimental: bool = False

    def matches(self, command_name: str) -> bool:
        """
        Determine whether a command name matches this command.

        Parameters
        ----------
        command_name
            Command entered by the user.

        Returns
        -------
        bool
            True if the identifier or any alias matches.
        """
        return command_name == self.identifier or command_name in self.aliases
