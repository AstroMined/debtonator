import json
import logging
from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Import all models to ensure they are registered
from .api.base import api_router
from .api.handlers.feature_flags import feature_flag_exception_handler
from .api.middleware.feature_flags import FeatureFlagMiddleware
from .api.response_formatter import format_response
from .config.providers.feature_flags import DatabaseConfigProvider
from .database.base import Base
from .database.database import engine, get_db
from .errors.feature_flags import FeatureFlagError
from .registry.account_registry_init import register_account_types
from .registry.account_types import (
    RegistryNotInitializedException,
    account_type_registry,
)
from .repositories.feature_flags import FeatureFlagRepository
from .services.feature_flags import FeatureFlagService
from .utils.config import settings
from .utils.feature_flags.feature_flags import get_registry


# Create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize registries and database

    # Initialize account type registry first (no async dependencies)
    register_account_types()

    # Verify account type registry was properly initialized
    try:
        types = account_type_registry.get_all_types()
        logger.info(f"Account type registry initialized with {len(types)} types")
    except RegistryNotInitializedException as e:
        logger.error(f"Account type registry initialization failed: {str(e)}")
        raise RuntimeError("Failed to initialize account type registry") from e

    # Create database tables
    await create_tables()

    # Initialize feature flag registry from database
    async for db_session in get_db:
        try:
            # Create repository and service
            repository = FeatureFlagRepository(db_session)
            registry = get_registry()
            service = FeatureFlagService(registry=registry, repository=repository)

            # Initialize service to load flags from database into registry
            await service.initialize()
            logger.info("Feature flag registry initialized from database")

            # Set up feature flag middleware
            try:
                # Create config provider
                config_provider = DatabaseConfigProvider(db_session)

                # Add middleware to app
                app.add_middleware(
                    FeatureFlagMiddleware,
                    feature_flag_service=service,
                    config_provider=config_provider,
                )
                logger.info("Feature flag middleware initialized")
            except Exception as e:
                logger.error(f"Failed to initialize feature flag middleware: {e}")

            break  # Successfully initialized, exit the loop
        except Exception as e:
            logger.error(f"Failed to initialize feature flags: {e}")
            # Session will be automatically closed when the loop exits

    yield  # App runs here

    # Shutdown logic could go here if needed
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    redirect_slashes=False,
    lifespan=lifespan,
)

# Configure logger
logger = logging.getLogger(__name__)


# Add validation error handlers for debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors with detailed logging for debugging.
    """
    try:
        body = await request.body()
        body_str = body.decode() if body else "No body"
    except Exception as e:
        body_str = f"Error reading body: {str(e)}"

    logger.error(f"Request validation error: {exc.errors()}")
    logger.error(f"Request path: {request.url.path}")
    logger.error(f"Request body: {body_str}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "path": request.url.path, "body": body_str},
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors with detailed logging for debugging.
    """
    logger.error(f"Pydantic validation error: {exc}")
    logger.error(f"Request path: {request.url.path}")

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "path": request.url.path,
        },
    )


# Register feature flag exception handler
app.add_exception_handler(FeatureFlagError, feature_flag_exception_handler)


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
            headers=dict(response.headers),
        )

    # Return the original response for non-JSON responses
    return response


# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.DESCRIPTION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }
