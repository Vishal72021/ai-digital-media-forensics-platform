"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/discovery.py

Purpose:
    Discovers available Developer CLI command modules.

Discovery is intentionally side-effect free. It only scans the
command package and returns a registry mapping command identifiers
to module paths.

===============================================================================
"""

from __future__ import annotations

import pkgutil

from scripts import commands
from scripts.core.types import CommandRegistry

__all__ = [
    "discover_commands",
]

_COMMANDS_PACKAGE = "scripts.commands"


def discover_commands() -> CommandRegistry:
    """
    Discover all available command modules.

    Returns
    -------
    CommandRegistry
        Mapping of command identifiers to module paths.
    """

    registry: dict[str, str] = {}

    for module in pkgutil.iter_modules(commands.__path__):
        if module.name.startswith("_"):
            continue

        registry[module.name] = f"{_COMMANDS_PACKAGE}.{module.name}"

    return dict(sorted(registry.items()))
