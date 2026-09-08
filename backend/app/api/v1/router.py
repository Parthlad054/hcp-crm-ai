"""
api/v1/router.py — Central API v1 router.

Assembles all sub-routers under the /api/v1 prefix.
main.py includes this single router instead of registering each one individually.
"""
from fastapi import APIRouter

from app.api.v1 import auth, chat, follow_ups, hcps, health, interactions, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(hcps.router, prefix="/hcps", tags=["hcps"])
api_router.include_router(follow_ups.router, prefix="/follow-ups", tags=["follow-ups"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
