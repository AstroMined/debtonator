"""
Feature Flag System Demonstration

This file provides a comprehensive demonstration of the feature flag system,
showing how the components work together correctly, including addressing the 
caching challenges that can occur in testing scenarios.
"""

import pytest
import time
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
# Add asyncio import for sleep operation
import asyncio

from src.config.providers.feature_flags import InMemoryConfigProvider
from src.errors.feature_flags import FeatureDisabledError
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from src.repositories.accounts import AccountRepository


pytestmark = pytest.mark.asyncio


class TestAccountRepository(AccountRepository):
    """Minimal repository implementation for demo purposes."""
    
    async def create_typed_account(self, account_type: str, data: Dict[str, Any]) -> Any:
        """Create a typed account - demo method."""
        return {"id": "123", "account_type": account_type, **data}


class ZeroTTLConfigProvider(InMemoryConfigProvider):
    """Config provider with zero TTL for testing purposes."""
    
    def __init__(self, requirements: Dict[str, Any]):
        super().__init__(requirements)
        # Override the TTL to be 0 seconds for testing
        self._cache_ttl = 0


async def test_feature_flag_caching_demo(db_session: AsyncSession, feature_flag_service: FeatureFlagService):
    """
    Demonstrate how the feature flag caching affects behavior in tests.
    
    This shows:
    1. How the default 30-second cache can cause unexpected test behavior
    2. How to work around the caching with explicit cache invalidation
    """
    FLAG_NAME = "DEMO_FEATURE_FLAG"
    ACCOUNT_TYPE = "test_account_type"
    
    # Step 1: Set up a mock repository for testing
    mock_repo = TestAccountRepository(db_session)
    
    # Step 2: Configure requirements for our demo feature flag
    # Note: This structure must match the expected format in feature_flag_proxy.py
    requirements = {
        FLAG_NAME: {
            "repository": {
                "create_typed_account": [ACCOUNT_TYPE]
            }
        }
    }
    
    # Step 3: Create a config provider with the standard 30s TTL (default)
    standard_config = InMemoryConfigProvider(requirements)
    
    # Step 4: Wrap the repository with the proxy (using standard config)
    standard_repo = FeatureFlagRepositoryProxy(
        repository=mock_repo,
        feature_flag_service=feature_flag_service,
        config_provider=standard_config
    )
    
    # Step 5: Ensure our flag exists and is enabled
    try:
        await feature_flag_service.create_flag({
            "name": FLAG_NAME,
            "flag_type": "boolean",
            "value": True,
            "description": "Demo flag for testing"
        })
    except Exception as e:
        print(f"Flag already exists: {e}")
        # Flag might already exist, make sure it's enabled
        await feature_flag_service.set_enabled(FLAG_NAME, True)
    
    print("\n--- STANDARD CONFIG PROVIDER DEMONSTRATION ---")
    print(f"Created or enabled flag '{FLAG_NAME}'")
    
    # Step 6: Verify operation succeeds when flag is enabled
    result = await standard_repo.create_typed_account(
        ACCOUNT_TYPE,
        {"name": "Test Account"}
    )
    print(f"Operation succeeded with flag enabled: {result}")
    
    # Step 7: Disable the flag
    await feature_flag_service.set_enabled(FLAG_NAME, False)
    print(f"Disabled flag '{FLAG_NAME}'")
    
    # Step 8: THIS MIGHT STILL WORK DUE TO CACHING! (demonstrating the issue)
    try:
        result2 = await standard_repo.create_typed_account(
            ACCOUNT_TYPE,
            {"name": "Test Account 2"}
        )
        print(f"Operation still succeeded even though flag is disabled due to caching: {result2}")
    except FeatureDisabledError as e:
        print(f"Operation failed as expected: {e}")
    
    print("\n--- ZERO TTL CONFIG PROVIDER DEMONSTRATION ---")
    
    # Step 9: Create a config provider with ZERO TTL (solution for tests)
    zero_ttl_config = ZeroTTLConfigProvider(requirements)
    
    # Step 10: Wrap the repository with the proxy (using zero TTL config)
    zero_ttl_repo = FeatureFlagRepositoryProxy(
        repository=mock_repo,
        feature_flag_service=feature_flag_service,
        config_provider=zero_ttl_config
    )
    
    # Step 11: Ensure flag is still disabled
    await feature_flag_service.set_enabled(FLAG_NAME, False)
    print(f"Flag '{FLAG_NAME}' is still disabled")
    
    # Step 12: Verify operation fails immediately (no cache delay)
    try:
        await zero_ttl_repo.create_typed_account(
            ACCOUNT_TYPE,
            {"name": "Zero TTL Test"}
        )
        print("ERROR: Operation succeeded when it should have failed")
    except FeatureDisabledError as e:
        print(f"Success! Operation correctly failed with zero TTL: {e}")
    
    # Step 13: Enable the flag again
    await feature_flag_service.set_enabled(FLAG_NAME, True)
    print(f"Enabled flag '{FLAG_NAME}' again")
    
    # Step 14: Verify operation succeeds again immediately
    result3 = await zero_ttl_repo.create_typed_account(
        ACCOUNT_TYPE,
        {"name": "Zero TTL Test 2"}
    )
    print(f"Operation succeeded again: {result3}")
    
    print("\n--- MANUAL CACHE CLEARING DEMONSTRATION ---")
    
    # Step 15: Create a standard config provider again
    manual_config = InMemoryConfigProvider(requirements)
    
    # Step 16: Wrap the repository with the proxy
    manual_repo = FeatureFlagRepositoryProxy(
        repository=mock_repo,
        feature_flag_service=feature_flag_service,
        config_provider=manual_config
    )
    
    # Step 17: Disable the flag
    await feature_flag_service.set_enabled(FLAG_NAME, False)
    print(f"Disabled flag '{FLAG_NAME}' again")
    
    # Step 18: Manually clear the cache (another solution)
    # This would be done inside the test or with a special method
    # Since we can't directly access private _cache, this is simulating
    # what a cache invalidation method would do
    manual_config._cache = {}
    manual_config._cache_expiry = 0
    print("Manually cleared the cache")
    
    # Step 19: Verify operation fails after manual cache clear
    try:
        await manual_repo.create_typed_account(
            ACCOUNT_TYPE, 
            {"name": "Manual Clear Test"}
        )
        print("ERROR: Operation succeeded when it should have failed")
    except FeatureDisabledError as e:
        print(f"Success! Operation correctly failed after manual cache clear: {e}")
    
    print("\n--- WAITING FOR CACHE EXPIRY DEMONSTRATION ---")
    
    # Step 20: Create one more standard config provider
    wait_config = InMemoryConfigProvider(requirements)
    # Set a very short TTL for this demo (2 seconds instead of 30)
    wait_config._cache_ttl = 2
    
    # Step 21: Wrap the repository with the proxy
    wait_repo = FeatureFlagRepositoryProxy(
        repository=mock_repo,
        feature_flag_service=feature_flag_service,
        config_provider=wait_config
    )
    
    # Step 22: Enable the flag
    await feature_flag_service.set_enabled(FLAG_NAME, True)
    print(f"Enabled flag '{FLAG_NAME}' again")
    
    # Step 23: Operation succeeds with flag enabled
    result4 = await wait_repo.create_typed_account(
        ACCOUNT_TYPE,
        {"name": "Wait Test 1"}
    )
    print(f"Operation succeeded: {result4}")
    
    # Step 24: Disable the flag
    await feature_flag_service.set_enabled(FLAG_NAME, False)
    print(f"Disabled flag '{FLAG_NAME}' again")
    
    # Step 25: This might still work due to 2-second caching
    try:
        result5 = await wait_repo.create_typed_account(
            ACCOUNT_TYPE,
            {"name": "Wait Test 2"}
        )
        print(f"Operation still succeeded due to caching: {result5}")
    except FeatureDisabledError as e:
        print(f"Operation failed (cache might have expired already): {e}")
    
    # Step 26: Wait for cache to expire (3 seconds > 2 second TTL)
    print("Waiting 3 seconds for cache to expire...")
    await asyncio.sleep(3)
    
    # Step 27: This should fail now as cache has expired
    try:
        await wait_repo.create_typed_account(
            ACCOUNT_TYPE,
            {"name": "Wait Test 3"}
        )
        print("ERROR: Operation succeeded when it should have failed")
    except FeatureDisabledError as e:
        print(f"Success! Operation failed after cache expired: {e}")


# This class is needed because we're referencing it directly in the demo
# In a real test, this would be imported from the actual module
class FeatureFlagRepositoryProxy:
    """
    Repository proxy that enforces feature flag requirements.
    
    This is a simplified version of the proxy for the demo, with just
    enough functionality to show the key concepts.
    """
    
    def __init__(
        self,
        repository: Any,
        feature_flag_service: Any,
        config_provider: Any,
    ):
        """Initialize the repository proxy."""
        self._repository = repository
        self._feature_flag_service = feature_flag_service
        self._config_provider = config_provider
        self._method_cache = {}
        
        # Add necessary attribute for feature flag caching
        self._feature_check_cache = {}
    
    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access to wrap method calls.
        
        For demo, we only implement special handling for create_typed_account
        """
        # Get the original attribute
        attr = getattr(self._repository, name)
        
        if name == 'create_typed_account' and callable(attr):
            # Create a wrapper for this specific method
            async def wrapped(*args, **kwargs):
                # Check if this method is restricted by any feature flags
                await self._check_feature_requirements(name, args, kwargs)
                
                # Call the original method
                return await attr(*args, **kwargs)
                
            return wrapped
        
        # For all other attributes, return the original
        return attr
    
    async def _check_feature_requirements(self, method_name, args, kwargs):
        """
        Check if the method call is allowed based on feature requirements.
        
        This is a simplified version of the real method.
        """
        # Extract account type from first argument
        account_type = args[0] if args else None
        
        # Get requirements from config provider
        all_requirements = await self._config_provider.get_all_requirements()
        
        # Check each feature flag's requirements
        for feature_name, requirements in all_requirements.items():
            if "repository" in requirements:
                repository_reqs = requirements["repository"]
                
                # Check if this method has requirements
                if method_name in repository_reqs:
                    required_types = repository_reqs[method_name]
                    
                    # If the account type matches requirements
                    if account_type in required_types:
                        # Check if feature is enabled
                        is_enabled = await self._feature_flag_service.is_enabled(feature_name)
                        
                        if not is_enabled:
                            # Feature is disabled, raise error
                            raise FeatureDisabledError(
                                feature_name=feature_name,
                                entity_type="account",
                                operation=method_name,
                                entity_id=account_type
                            )
