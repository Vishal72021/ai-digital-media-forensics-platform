"""Application factory for the Sentinel AI backend."""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.lifespan import lifespan
from app.core.logging import configure_logging

APPLICATION_TITLE = "Sentinel AI"
APPLICATION_DESCRIPTION = "Backend API for the Sentinel AI Digital Media Forensics Platform."
APPLICATION_VERSION = "0.1.0"


def create_application() -> FastAPI:
    """Create and configure the Sentinel AI FastAPI application.

    Returns:
        A configured FastAPI application instance.
    """
    configure_logging()

    application = FastAPI(
        title=APPLICATION_TITLE,
        description=APPLICATION_DESCRIPTION,
        version=APPLICATION_VERSION,
        lifespan=lifespan,
    )

    application.include_router(api_router)

    return application
