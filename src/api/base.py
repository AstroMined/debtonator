from fastapi import APIRouter
from .v1 import api_v1_router
from ..utils.config import settings

api_router = APIRouter()

# Include versioned routers
api_router.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
