"""Domain exception to API schema mapper."""

from __future__ import annotations

from http import HTTPStatus

from pydantic import AnyUrl

from app.api.schemas.errors import ProblemDetails
from app.domain.exceptions import (
    ConflictException,
    DomainException,
    InfrastructureException,
    ResourceNotFoundException,
    ValidationException,
)


def map_exception(exception: DomainException) -> ProblemDetails:
    """Map a domain exception to an RFC 9457 problem details schema."""

    match exception:
        case ResourceNotFoundException():
            status = HTTPStatus.NOT_FOUND
            title = "Resource Not Found"
            problem_type = "resource-not-found"

        case ConflictException():
            status = HTTPStatus.CONFLICT
            title = "Conflict"
            problem_type = "conflict"

        case ValidationException():
            status = HTTPStatus.UNPROCESSABLE_ENTITY
            title = "Validation Failed"
            problem_type = "validation"

        case InfrastructureException():
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            title = "Infrastructure Error"
            problem_type = "infrastructure"

        case _:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            title = "Internal Server Error"
            problem_type = "internal-server-error"

    return ProblemDetails(
        type=AnyUrl(f"https://api.sentinelai.dev/problems/{problem_type}"),
        title=title,
        status=status.value,
        detail=str(exception),
    )


def map_unhandled_exception(_: Exception) -> ProblemDetails:
    """Map an unexpected exception to a generic problem details schema."""

    return ProblemDetails(
        type=AnyUrl("about:blank"),
        title="Internal Server Error",
        status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        detail="An unexpected error occurred.",
    )
