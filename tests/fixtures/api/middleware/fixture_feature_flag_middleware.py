"""
Fixtures for feature flag middleware tests.

This module provides fixtures for testing the FeatureFlagMiddleware component,
including test applications, clients, and requirements configurations.
"""

import pytest
import pytest_asyncio
from typing import Dict, Any, Tuple
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient

from src.api.middleware.feature_flags import FeatureFlagMiddleware
from src.config.providers.feature_flags import InMemoryConfigProvider
from src.errors.feature_flags import FeatureDisabledError


class CallCountingProvider(InMemoryConfigProvider):
    """Config provider that counts the number of times it's called."""
    
    def __init__(self, requirements: Dict[str, Any]):
        """Initialize with requirements and a call counter."""
        super().__init__(requirements)
        self.call_count = 0
        
    async def get_all_requirements(self) -> Dict[str, Any]:
        """
        Get all requirements and increment call counter.
        
        Returns:
            Dict[str, Any]: The requirements dictionary
        """
        self.call_count += 1
        return await super().get_all_requirements()


@pytest.fixture
def test_app():
    """
    Create a minimal test FastAPI application.
    
    Returns:
        FastAPI: A minimal application for testing
    """
    app = FastAPI()
    
    @app.get("/api/v1/test-endpoint")
    def test_endpoint():
        return {"message": "success"}
        
    @app.get("/api/v1/accounts/{account_id}")
    def account_endpoint(account_id: str):
        return {"account_id": account_id, "message": "success"}
        
    @app.get("/api/v1/banking/overview")
    def banking_overview():
        return {"message": "success"}
    
    # Register exception handler
    @app.exception_handler(FeatureDisabledError)
    async def feature_disabled_handler(request: Request, exc: FeatureDisabledError):
        return JSONResponse(
            status_code=403,
            content={
                "message": str(exc),
                "code": "FEATURE_DISABLED",
                "feature_flag": exc.feature_name,
                "entity_type": exc.entity_type,
                "entity_id": exc.entity_id
            }
        )
    
    return app


@pytest_asyncio.fixture
async def test_client(test_app):
    """
    Create an AsyncClient for testing the test app.
    
    Args:
        test_app: The test FastAPI application
        
    Returns:
        AsyncClient: A client for making requests
    """
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
def api_requirements():
    """
    Provide test API requirements for the middleware.
    
    Returns:
        Dict[str, Any]: Requirements dictionary
    """
    return {
        "TEST_FEATURE": {
            "api": {
                "/api/v1/test-endpoint": ["*"]
            }
        },
        "BANKING_ACCOUNT_TYPES_ENABLED": {
            "api": {
                "/api/v1/accounts/{account_id}": ["bnpl", "ewa", "payment_app"],
                "/api/v1/banking/*": ["*"]
            }
        }
    }


@pytest.fixture
def configured_test_app(test_app, feature_flag_service, api_requirements):
    """
    Configure test app with feature flag middleware.
    
    Args:
        test_app: The test FastAPI application
        feature_flag_service: Feature flag service
        api_requirements: API requirements dictionary
    
    Returns:
        FastAPI: Configured application with middleware
    """
    config_provider = InMemoryConfigProvider(api_requirements)
    
    # Add middleware to app directly
    test_app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    return test_app


@pytest.fixture
def app_with_counting_middleware(test_app, feature_flag_service, api_requirements) -> Tuple[FastAPI, CallCountingProvider]:
    """
    Configure test app with call-counting middleware.
    
    Args:
        test_app: The test FastAPI application
        feature_flag_service: Feature flag service
        api_requirements: API requirements dictionary
    
    Returns:
        Tuple[FastAPI, CallCountingProvider]: Configured application and provider
    """
    counting_provider = CallCountingProvider(api_requirements)
    
    # Add middleware to app
    test_app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=counting_provider,
        cache_ttl=0.1  # 100ms TTL for testing
    )
    
    return test_app, counting_provider
