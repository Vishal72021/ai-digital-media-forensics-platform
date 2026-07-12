"""Application lifespan management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    """Manage the application lifecycle.

    Args:
        application: The FastAPI application instance.

    Yields:
        Control back to the FastAPI application.
    """
    del application

    yield
