"""
===============================================================================

Sentinel AI
AI Digital Media Forensics Platform

Developer CLI Framework

File:
    scripts/core/exceptions.py

Purpose:
    Defines the exception hierarchy for the Sentinel AI Developer CLI.

The framework exposes a single root exception (`DeveloperCLIError`)
from which all framework-specific exceptions derive.

This allows callers to either handle specific failures or catch every
Developer CLI error through a single base class.

===============================================================================
"""

from __future__ import annotations

__all__ = [
    "DeveloperCLIError",
    "ConfigurationError",
    "DiscoveryError",
    "ValidationError",
    "ExecutionError",
    "CommandNotFoundError",
]


class DeveloperCLIError(Exception):
    """
    Base exception for the Sentinel AI Developer CLI.

    All framework-specific exceptions derive from this class.
    """


class ConfigurationError(DeveloperCLIError):
    """
    Raised when the Developer CLI configuration is invalid.

    Examples
    --------
    - Invalid project structure.
    - Missing required configuration.
    - Unsupported runtime configuration.
    """


class DiscoveryError(DeveloperCLIError):
    """
    Raised when command discovery fails.

    Examples
    --------
    - Commands package cannot be imported.
    - Command module is malformed.
    - Discovery process encounters an unrecoverable error.
    """


class ValidationError(DeveloperCLIError):
    """
    Raised when a command fails framework validation.

    Examples
    --------
    - Missing metadata.
    - Missing run() implementation.
    - Invalid command contract.
    """


class ExecutionError(DeveloperCLIError):
    """
    Raised when a command cannot be executed successfully.

    Examples
    --------
    - External process execution failure.
    - Runtime command failure.
    """


class CommandNotFoundError(DeveloperCLIError):
    """
    Raised when a requested command does not exist.

    Examples
    --------
    User requests:

        verify

    Available commands:

        bootstrap
        clean
        lint

    In this case, the requested command cannot be located.
    """
