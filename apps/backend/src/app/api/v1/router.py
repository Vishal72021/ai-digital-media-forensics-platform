"""API version 1 router."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)
