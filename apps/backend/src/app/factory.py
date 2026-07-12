"""Application factory for the Sentinel AI backend."""

from fastapi import FastAPI

from app.core.lifespan import lifespan

APPLICATION_TITLE = "Sentinel AI"


def create_application() -> FastAPI:
    """Create and configure the Sentinel AI FastAPI application.

    Returns:
        A configured FastAPI application instance.
    """
    application = FastAPI(
        title=APPLICATION_TITLE,
        lifespan=lifespan,
    )

    return application
