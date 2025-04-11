"""
Admin API router.

This module provides a router for administrative APIs.
"""

from fastapi import APIRouter

from src.api.admin.feature_flags import router as feature_flags_router

admin_router = APIRouter()

# Include feature flag admin router
admin_router.include_router(feature_flags_router)
