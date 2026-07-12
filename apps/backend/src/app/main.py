"""ASGI application entry point for the Sentinel AI backend."""

from app.factory import create_application

app = create_application()
