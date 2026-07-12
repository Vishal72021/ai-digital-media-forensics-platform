"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/loader.py

Purpose:
    Provides the runtime implementation responsible for importing,
    instantiating, and validating Developer CLI commands.

The CommandLoader is the only component responsible for converting a
Python module into a validated LoadedCommand.

===============================================================================
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from types import ModuleType
from typing import cast

from scripts.core.command import Command
from scripts.core.exceptions import (
    DiscoveryError,
    ValidationError,
)
from scripts.core.loaded_command import LoadedCommand
from scripts.core.metadata import CommandMetadata

__all__ = [
    "CommandLoader",
]

_FACTORY_FUNCTION_NAME = "create_command"


class CommandLoader:
    """
    Load and validate Developer CLI commands.
    """

    def load(
        self,
        module_path: str,
    ) -> LoadedCommand:
        """
        Load a command from a Python module.

        Parameters
        ----------
        module_path
            Fully qualified Python module path.

        Returns
        -------
        LoadedCommand
            Validated command ready for execution.

        Raises
        ------
        DiscoveryError
            If the module cannot be imported.

        ValidationError
            If the module does not satisfy the command contract.
        """

        module = self._import_module(module_path)

        factory = self._load_factory(module)

        command = self._instantiate_command(factory)

        self._validate_command(command)

        self._validate_metadata(command.metadata)

        return LoadedCommand(command=command)

    def _import_module(
        self,
        module_path: str,
    ) -> ModuleType:
        """
        Import a command module.
        """

        try:
            return importlib.import_module(module_path)

        except ImportError as exc:
            raise DiscoveryError(f"Unable to import command module '{module_path}'.") from exc

    def _load_factory(
        self,
        module: ModuleType,
    ) -> Callable[[], Command]:
        """
        Retrieve the command factory from a module.
        """

        factory = getattr(
            module,
            _FACTORY_FUNCTION_NAME,
            None,
        )

        if factory is None:
            raise ValidationError(
                f"Missing '{_FACTORY_FUNCTION_NAME}()' in module '{module.__name__}'."
            )

        if not callable(factory):
            raise ValidationError(
                f"'{_FACTORY_FUNCTION_NAME}' is not callable in '{module.__name__}'."
            )

        return cast(
            Callable[[], Command],
            factory,
        )

    def _instantiate_command(
        self,
        factory: Callable[[], Command],
    ) -> Command:
        """
        Instantiate a command using the module factory.
        """

        command = factory()

        if not isinstance(command, Command):
            raise ValidationError("Factory did not return a valid Command.")

        return command

    def _validate_command(
        self,
        command: Command,
    ) -> None:
        """
        Validate the instantiated command.
        """

        if not hasattr(command, "metadata"):
            raise ValidationError("Command does not expose metadata.")

        if not hasattr(command, "run"):
            raise ValidationError("Command does not implement run().")

    def _validate_metadata(
        self,
        metadata: CommandMetadata,
    ) -> None:
        """
        Validate command metadata.
        """

        if not metadata.identifier.strip():
            raise ValidationError("Command identifier cannot be empty.")

        if not metadata.name.strip():
            raise ValidationError("Command name cannot be empty.")

        if not metadata.description.strip():
            raise ValidationError("Command description cannot be empty.")
