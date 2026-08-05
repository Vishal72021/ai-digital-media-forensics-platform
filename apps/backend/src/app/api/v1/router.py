"""API version 1 router."""

from fastapi import APIRouter

from app.api.v1.authentication import authentication_router
from app.api.v1.health import health_router
from app.api.v1.users import users_router

v1_router = APIRouter(
    prefix="/api/v1",
)

v1_router.include_router(health_router)
v1_router.include_router(authentication_router)
v1_router.include_router(users_router)
