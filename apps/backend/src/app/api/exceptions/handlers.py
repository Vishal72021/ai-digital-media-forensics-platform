"""FastAPI exception handlers."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.exceptions.mapper import (
    map_exception,
    map_unhandled_exception,
)
from app.domain.exceptions import DomainException


async def domain_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Handle all domain exceptions."""

    assert isinstance(exception, DomainException)

    problem = map_exception(exception)

    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json"),
    )


async def unhandled_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions."""

    problem = map_unhandled_exception(exception)

    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json"),
    )
