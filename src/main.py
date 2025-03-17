from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from decimal import Decimal

from .api.response_formatter import format_response

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

# Custom decimal encoder for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

# Middleware for formatting decimal values in responses
@app.middleware("http")
async def decimal_precision_middleware(request: Request, call_next):
    # Process the request and get the response
    response = await call_next(request)
    
    # Only process JSON responses
    if response.headers.get("content-type") == "application/json":
        # Get the response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        # Parse the response body
        data = json.loads(body.decode())
        
        # Format decimal values
        formatted_data = format_response(data)
        
        # Create a new response with formatted data
        return JSONResponse(
            content=formatted_data,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    # Return the original response for non-JSON responses
    return response

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
