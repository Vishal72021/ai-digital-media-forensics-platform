"""Logging configuration for the Sentinel AI backend."""

import logging


def configure_logging() -> None:
    """Configure application logging.

    Logging configuration will be expanded in future milestones as the
    backend introduces structured logging and observability.
    """
    logging.basicConfig(
        level=logging.INFO,
    )
