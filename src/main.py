from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all models to ensure they are registered
from . import models
from .utils.config import settings
from .api.base import api_router
from .database.base import Base
from .database.database import engine

# Create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    redirect_slashes=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug: Print all registered routes with methods
print("\nAPI Router Routes:")
for route in api_router.routes:
    print(f"API Route: {route.path}")
    for method in route.methods:
        print(f"  Method: {method}")

# Include API router
app.include_router(api_router)

# Debug: Print all app routes with methods
print("\nApp Routes:")
for route in app.routes:
    print(f"App Route: {route.path}")
    for method in route.methods:
        print(f"  Method: {method}")

@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.DESCRIPTION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }
