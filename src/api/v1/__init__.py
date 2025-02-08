from fastapi import APIRouter
from .bills import router as bills_router

api_v1_router = APIRouter()

api_v1_router.include_router(bills_router, prefix="/bills", tags=["bills"])
