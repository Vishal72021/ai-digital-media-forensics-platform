"""
Developer CLI entrypoint.
"""

from __future__ import annotations

import argparse

from scripts.core.console import Console
from scripts.core.discovery import discover_commands
from scripts.core.exceptions import (
    CommandNotFoundError,
    DeveloperCLIError,
)
from scripts.core.loader import CommandLoader

__all__ = [
    "main",
]


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the CLI argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="tasks",
        description="Sentinel AI Developer CLI",
    )

    parser.add_argument(
        "command",
        help="Developer command to execute.",
    )

    return parser


def main() -> int:
    """
    CLI entrypoint.
    """

    parser = _build_parser()

    args = parser.parse_args()

    registry = discover_commands()

    module_path = registry.get(args.command)

    if module_path is None:
        raise CommandNotFoundError(f"Unknown command '{args.command}'.")

    loader = CommandLoader()

    loaded = loader.load(module_path)

    return loaded.run()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeveloperCLIError as exc:
        Console().error(exc)
        raise SystemExit(1) from exc
