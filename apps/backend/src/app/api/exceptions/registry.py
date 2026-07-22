"""Exception handler registration."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.exceptions.handlers import (
    domain_exception_handler,
    unhandled_exception_handler,
)
from app.domain.exceptions import DomainException


def register_exception_handlers(app: FastAPI) -> None:
    """Register all application exception handlers."""

    app.add_exception_handler(
        DomainException,
        domain_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )
