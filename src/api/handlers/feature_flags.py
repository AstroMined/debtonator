"""
Exception handlers for feature flag related errors.

This module provides FastAPI exception handlers for the feature flag error classes,
converting domain exceptions to appropriate HTTP responses.

This is part of the implementation of ADR-024: Feature Flag System.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.errors.feature_flags import FeatureFlagError
from src.errors.utils import feature_flag_error_to_http_exception

# Configure logger
logger = logging.getLogger(__name__)


async def feature_flag_exception_handler(
    request: Request, exc: FeatureFlagError
) -> JSONResponse:
    """
    Convert feature flag domain errors to HTTP responses.

    This handler uses the centralized error conversion utility to ensure
    consistent error handling across the application.

    Args:
        request: The FastAPI request
        exc: The feature flag error

    Returns:
        JSONResponse: Appropriate HTTP response for the error
    """
    # Log the error
    logger.info(
        f"Feature flag error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__,
            "details": getattr(exc, "details", {}),
        },
    )

    # Convert to HTTP exception
    http_exc = feature_flag_error_to_http_exception(exc)

    # Return JSON response
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )
