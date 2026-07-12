"""Application factory for the Sentinel AI backend."""

from fastapi import FastAPI


def create_application() -> FastAPI:
    """Create and configure the Sentinel AI FastAPI application.

    Returns:
        A configured FastAPI application instance.
    """
    APPLICATION_TITLE = "Sentinel AI"

    application = FastAPI(
        title=APPLICATION_TITLE,
    )

    return application
