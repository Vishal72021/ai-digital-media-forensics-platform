"""API exception handling."""

from app.api.exceptions.mapper import map_exception
from app.api.exceptions.registry import register_exception_handlers

__all__ = [
    "map_exception",
    "register_exception_handlers",
]
