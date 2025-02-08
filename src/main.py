from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.base import api_router
from .database.database import create_db_and_tables
from .utils.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Bill & Cashflow Management System",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    await create_db_and_tables()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Debtonator API is running"}
