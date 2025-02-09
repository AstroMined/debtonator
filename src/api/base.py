from fastapi import APIRouter
from .v1 import api_v1_router

api_router = APIRouter()

# Include versioned routers
api_router.include_router(api_v1_router)
