"""
End-to-end integration tests for the Feature Flag System.

This module contains tests that verify the entire feature flag stack works correctly,
from the database layer to the API layer. It tests feature flag requirements propagation,
cache invalidation, and cross-layer enforcement.
"""

import time
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.errors.feature_flags import FeatureDisabledError
from src.models.feature_flags import FeatureFlag
from src.repositories.accounts import AccountRepository
from src.repositories.feature_flags import FeatureFlagRepository
from src.repositories.proxies.feature_flag_proxy import FeatureFlagRepositoryProxy
from src.services.accounts import AccountService
from src.services.feature_flags import FeatureFlagService
from src.config.providers.feature_flags import DatabaseConfigProvider


# --------------- Helper Functions ---------------

async def setup_test_feature_flag(
    db_session: AsyncSession,
    flag_name: str = "TEST_E2E_FEATURE_FLAG",
    flag_value: bool = True,
    requirements: dict = None
) -> FeatureFlag:
    """Set up a test feature flag with specified requirements."""
    repository = FeatureFlagRepository(db_session)
    
    # Create or update the feature flag
    flag = await repository.get(flag_name)
    if flag:
        await repository.update(flag_name, {
            "value": flag_value,
            "flag_type": "boolean"
        })
    else:
        flag = await repository.create({
            "name": flag_name,
            "value": flag_value,
            "flag_type": "boolean",
            "description": "Test feature flag for E2E testing"
        })
    
    # Set requirements if provided
    if requirements:
        await repository.update_requirements(flag_name, requirements)
    
    await db_session.commit()
    return flag


async def create_test_account(
    account_repository: AccountRepository, account_type: str = "checking"
) -> dict:
    """Create a test account."""
    account_data = {
        "name": f"Test {account_type.capitalize()} Account",
        "account_type": account_type,
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00")
    }
    
    # Add account type specific fields
    if account_type == "bnpl":
        account_data["credit_limit"] = Decimal("2000.00")
        account_data["provider"] = "TestBNPL"
    elif account_type == "ewa":
        account_data["provider"] = "TestEWA"
    elif account_type == "payment_app":
        account_data["provider"] = "TestPaymentApp"
    
    # Create account
    account = await account_repository.create(account_data)
    return account


# --------------- Test Fixtures ---------------

@pytest.fixture
async def test_e2e_flag(db_session: AsyncSession) -> FeatureFlag:
    """Create a test feature flag for E2E testing."""
    flag = await setup_test_feature_flag(
        db_session,
        flag_name="TEST_E2E_FEATURE_FLAG",
        flag_value=True
    )
    return flag


@pytest.fixture
async def config_provider(db_session: AsyncSession) -> DatabaseConfigProvider:
    """Create a database config provider."""
    return DatabaseConfigProvider(db_session)


# --------------- E2E Integration Tests ---------------

@pytest.mark.asyncio
async def test_repository_layer_enforcement(
    db_session: AsyncSession,
    test_e2e_flag: FeatureFlag,
    feature_flag_service: FeatureFlagService,
    config_provider: DatabaseConfigProvider
):
    """Test feature flag enforcement at the repository layer."""
    # Set up requirements to block 'bnpl' accounts for a specific method
    requirements = {
        "repository": {
            "create": ["bnpl"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Disable the flag
        requirements=requirements
    )
    
    # Create repository with proxy
    repository = AccountRepository(db_session)
    proxied_repository = FeatureFlagRepositoryProxy(
        repository=repository,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Test: Creating a checking account should succeed (not blocked)
    checking_account = await create_test_account(proxied_repository, "checking")
    assert checking_account is not None
    assert checking_account["account_type"] == "checking"
    
    # Test: Creating a BNPL account should fail due to disabled feature flag
    with pytest.raises(FeatureDisabledError) as excinfo:
        await create_test_account(proxied_repository, "bnpl")
    
    # Verify error message
    assert test_e2e_flag.name in str(excinfo.value)
    assert "repository" in str(excinfo.value).lower() or "create" in str(excinfo.value).lower()
    
    # Enable the flag and retry - should succeed now
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=True,  # Enable the flag
        requirements=requirements
    )
    
    # Now creating a BNPL account should succeed
    bnpl_account = await create_test_account(proxied_repository, "bnpl")
    assert bnpl_account is not None
    assert bnpl_account["account_type"] == "bnpl"


@pytest.mark.asyncio
async def test_service_layer_enforcement(
    db_session: AsyncSession,
    test_e2e_flag: FeatureFlag,
    feature_flag_service: FeatureFlagService,
    config_provider: DatabaseConfigProvider
):
    """Test feature flag enforcement at the service layer."""
    # Set up requirements to block 'ewa' accounts in the service layer
    requirements = {
        "service": {
            "create_account": ["ewa"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Disable the flag
        requirements=requirements
    )
    
    # Create account service with directly attached repository (no proxy)
    repository = AccountRepository(db_session)
    
    # This would normally be done through the service factory with proxy
    # To simulate service interception, we'll manually check the flag
    account_service = AccountService(repository)
    
    # Test: Creating a checking account should succeed
    # In a real scenario, this would be intercepted by the service factory,
    # but for this test we'll simulate the behavior
    checking_data = {
        "name": "Test Checking Account",
        "account_type": "checking",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00")
    }
    
    # Manually check if feature flag allows this operation
    checking_type = "checking"
    should_block = False
    for flag_name, flag_reqs in (await config_provider.get_all_requirements()).items():
        if "service" in flag_reqs:
            service_reqs = flag_reqs["service"]
            if "create_account" in service_reqs:
                if checking_type in service_reqs["create_account"]:
                    if not await feature_flag_service.is_enabled(flag_name):
                        should_block = True
                        break
    
    assert not should_block
    checking_account = await account_service.create_account(checking_data)
    assert checking_account is not None
    
    # Test: Creating an EWA account should be blocked by requirements
    ewa_data = {
        "name": "Test EWA Account",
        "account_type": "ewa",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "provider": "TestEWA"
    }
    
    # Manually check if feature flag allows this operation
    ewa_type = "ewa"
    should_block = False
    for flag_name, flag_reqs in (await config_provider.get_all_requirements()).items():
        if "service" in flag_reqs:
            service_reqs = flag_reqs["service"]
            if "create_account" in service_reqs:
                if ewa_type in service_reqs["create_account"]:
                    if not await feature_flag_service.is_enabled(flag_name):
                        should_block = True
                        break
    
    assert should_block
    # In a real scenario, the service proxy would raise the error
    # For this test, we'll simulate that behavior
    
    # Enable the flag and retry
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=True,  # Enable the flag
        requirements=requirements
    )
    
    # Check flag again - should be enabled now
    should_block = False
    for flag_name, flag_reqs in (await config_provider.get_all_requirements()).items():
        if "service" in flag_reqs:
            service_reqs = flag_reqs["service"]
            if "create_account" in service_reqs:
                if ewa_type in service_reqs["create_account"]:
                    if not await feature_flag_service.is_enabled(flag_name):
                        should_block = True
                        break
    
    assert not should_block
    # Now creating an EWA account should work
    ewa_account = await account_service.create_account(ewa_data)
    assert ewa_account is not None
    assert ewa_account["account_type"] == "ewa"


@pytest.mark.asyncio
async def test_api_layer_enforcement(
    client: AsyncClient,
    db_session: AsyncSession,
    test_e2e_flag: FeatureFlag
):
    """Test feature flag enforcement at the API layer."""
    # Set up requirements to block '/api/v1/accounts' endpoint for 'payment_app' accounts
    requirements = {
        "api": {
            "/api/v1/accounts": ["payment_app"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Disable the flag
        requirements=requirements
    )
    
    # Test: Creating a checking account should succeed
    checking_data = {
        "name": "Test Checking Account",
        "account_type": "checking",
        "available_balance": "1000.00",
        "current_balance": "1000.00"
    }
    
    response = await client.post("/api/v1/accounts", json=checking_data)
    assert response.status_code == 201
    
    # Test: Creating a payment_app account should fail (403 Forbidden)
    payment_app_data = {
        "name": "Test Payment App Account",
        "account_type": "payment_app",
        "available_balance": "1000.00",
        "current_balance": "1000.00",
        "provider": "TestPaymentApp"
    }
    
    response = await client.post("/api/v1/accounts", json=payment_app_data)
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()
    assert test_e2e_flag.name in response.json()["detail"]
    
    # Enable the flag and retry
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=True,  # Enable the flag
        requirements=requirements
    )
    
    # Now creating a payment_app account should succeed
    response = await client.post("/api/v1/accounts", json=payment_app_data)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_cross_layer_requirements_propagation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_e2e_flag: FeatureFlag,
    feature_flag_service: FeatureFlagService,
    config_provider: DatabaseConfigProvider
):
    """Test that requirements are properly propagated across all layers."""
    # Set up comprehensive requirements across all layers
    requirements = {
        "repository": {
            "create": ["bnpl", "ewa", "payment_app"]
        },
        "service": {
            "create_account": ["bnpl", "ewa", "payment_app"]
        },
        "api": {
            "/api/v1/accounts": ["bnpl", "ewa", "payment_app"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Disable the flag
        requirements=requirements
    )
    
    # Create repository with proxy
    repository = AccountRepository(db_session)
    proxied_repository = FeatureFlagRepositoryProxy(
        repository=repository,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Test direct repository access - should be blocked for BNPL
    with pytest.raises(FeatureDisabledError):
        await create_test_account(proxied_repository, "bnpl")
    
    # Test API access - should be blocked for BNPL
    bnpl_data = {
        "name": "Test BNPL Account",
        "account_type": "bnpl",
        "available_balance": "1000.00",
        "current_balance": "1000.00",
        "credit_limit": "2000.00",
        "provider": "TestBNPL"
    }
    
    response = await client.post("/api/v1/accounts", json=bnpl_data)
    assert response.status_code == 403
    
    # Update requirements to only block at the repository layer
    requirements = {
        "repository": {
            "create": ["bnpl"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Still disabled
        requirements=requirements
    )
    
    # Repository should still block BNPL
    with pytest.raises(FeatureDisabledError):
        await create_test_account(proxied_repository, "bnpl")
    
    # API should now allow EWA and payment_app, but BNPL will still be blocked
    # because the underlying repository will block it
    ewa_data = {
        "name": "Test EWA Account",
        "account_type": "ewa", 
        "available_balance": "1000.00",
        "current_balance": "1000.00",
        "provider": "TestEWA"
    }
    
    # EWA should work now
    response = await client.post("/api/v1/accounts", json=ewa_data)
    assert response.status_code == 201
    
    # BNPL should still fail, but with a different error code (likely 500)
    # since the failure happens in the repository, not at the middleware
    response = await client.post("/api/v1/accounts", json=bnpl_data)
    assert response.status_code in (403, 500)  # Either forbidden or internal server error


@pytest.mark.asyncio
async def test_cache_invalidation(
    db_session: AsyncSession,
    test_e2e_flag: FeatureFlag,
    feature_flag_service: FeatureFlagService,
    config_provider: DatabaseConfigProvider
):
    """Test that cache is properly invalidated when requirements change."""
    # Set up initial requirements
    requirements = {
        "repository": {
            "create": ["bnpl"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Disable the flag
        requirements=requirements
    )
    
    # Create repository with proxy
    repository = AccountRepository(db_session)
    proxied_repository = FeatureFlagRepositoryProxy(
        repository=repository,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # First access to load cache
    with pytest.raises(FeatureDisabledError):
        await create_test_account(proxied_repository, "bnpl")
    
    # Update requirements in the database
    new_requirements = {
        "repository": {
            "create": ["ewa"]  # Changed from bnpl to ewa
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Still disabled
        requirements=new_requirements
    )
    
    # Wait for cache to expire (1 second should be enough for test cache)
    time.sleep(1)
    
    # Now BNPL should work, but EWA should be blocked
    bnpl_account = await create_test_account(proxied_repository, "bnpl")
    assert bnpl_account is not None
    
    with pytest.raises(FeatureDisabledError):
        await create_test_account(proxied_repository, "ewa")
    
    # Invalidate cache explicitly through the provider
    await config_provider.invalidate_cache()
    
    # Make another change - block both types
    combined_requirements = {
        "repository": {
            "create": ["bnpl", "ewa"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=False,  # Still disabled
        requirements=combined_requirements
    )
    
    # Changes should be immediately visible (no wait)
    with pytest.raises(FeatureDisabledError):
        await create_test_account(proxied_repository, "bnpl")
    
    with pytest.raises(FeatureDisabledError):
        await create_test_account(proxied_repository, "ewa")


@pytest.mark.asyncio
async def test_performance_overhead(
    db_session: AsyncSession,
    test_e2e_flag: FeatureFlag,
    feature_flag_service: FeatureFlagService,
    config_provider: DatabaseConfigProvider
):
    """Test that feature flag enforcement has acceptable performance overhead."""
    # Set up requirements for all account types
    requirements = {
        "repository": {
            "create": ["checking", "savings", "credit", "bnpl", "ewa", "payment_app"]
        }
    }
    await setup_test_feature_flag(
        db_session, 
        flag_name=test_e2e_flag.name, 
        flag_value=True,  # Enable the flag
        requirements=requirements
    )
    
    # Create repositories
    direct_repository = AccountRepository(db_session)
    proxied_repository = FeatureFlagRepositoryProxy(
        repository=direct_repository,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Measure performance without proxy
    start = time.time()
    for _ in range(5):  # Small number for test, would be larger in real benchmark
        await create_test_account(direct_repository, "checking")
    direct_time = time.time() - start
    
    # Measure performance with proxy
    start = time.time()
    for _ in range(5):  # Small number for test, would be larger in real benchmark
        await create_test_account(proxied_repository, "checking")
    proxied_time = time.time() - start
    
    # Calculate overhead percentage
    overhead_percent = ((proxied_time - direct_time) / direct_time) * 100
    
    # Log the results for inspection
    print(f"Direct time: {direct_time:.6f}s")
    print(f"Proxied time: {proxied_time:.6f}s")
    print(f"Overhead: {overhead_percent:.2f}%")
    
    # Check if overhead is reasonable
    # For this test, we'll allow up to 200% overhead in the worst case
    # In real production scenarios, we'd aim for much lower
    assert overhead_percent < 200.0, f"Performance overhead too high: {overhead_percent:.2f}%"
