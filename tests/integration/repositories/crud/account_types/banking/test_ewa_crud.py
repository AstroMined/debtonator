# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for EWA account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.config.providers.feature_flags import InMemoryConfigProvider
from tests.helpers.feature_flag_utils import ZeroTTLConfigProvider
from src.errors.feature_flags import FeatureDisabledError
from src.models.account_types.banking.ewa import EWAAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from tests.helpers.schema_factories.account_types.banking.ewa_schema_factories import (
    create_ewa_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_ewa_account(ewa_repository: AccountRepository):
    """
    Test creating an EWA account following the four-step pattern.
    
    Args:
        ewa_repository: Repository fixture for EWA accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_ewa_account_schema(
        name="My Earnin Account",
        provider="Earnin",
        current_balance=Decimal("250.00"),
        max_advance_percentage=Decimal("50.00"),
        per_transaction_fee=Decimal("2.99"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    # Ensure only invalid fields are excluded
    invalid_fields = ["available_credit"]
    filtered_data = {
        k: v for k, v in validated_data.items() if k not in invalid_fields
    }
    result = await ewa_repository.create_typed_account("ewa", filtered_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, EWAAccount)
    assert result.id is not None
    assert result.name == "My Earnin Account"
    assert result.provider == "Earnin"
    assert result.current_balance == Decimal("250.00")
    assert result.max_advance_percentage == Decimal("50.00")
    assert result.per_transaction_fee == Decimal("2.99")


async def test_get_ewa_account(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test retrieving an EWA account by ID.
    
    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await ewa_repository.get(test_ewa_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, EWAAccount)
    assert result.id == test_ewa_account.id
    assert result.name == test_ewa_account.name
    assert result.provider == test_ewa_account.provider
    assert result.max_advance_percentage == test_ewa_account.max_advance_percentage


async def test_update_ewa_account(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test updating an EWA account.
    
    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_ewa_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_ewa_account_schema(
        name="Updated PayActiv Account",
        max_advance_percentage=Decimal("60.00"),  # Increased max advance percentage
        per_transaction_fee=Decimal("3.99"),  # Increased fee
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await ewa_repository.update_typed_account(
        account_id=account_id,
        account_type="ewa",
        data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, EWAAccount)
    assert result.id == account_id
    assert result.name == "Updated PayActiv Account"
    assert result.max_advance_percentage == Decimal("60.00")
    assert result.per_transaction_fee == Decimal("3.99")
    # Original properties should remain unchanged
    assert result.provider == test_ewa_account.provider
    assert result.current_balance == test_ewa_account.current_balance


async def test_delete_ewa_account(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test deleting (soft delete) an EWA account.
    
    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_ewa_account.id

    # 2. ACT: Delete the account
    result = await ewa_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await ewa_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True


async def test_update_ewa_account_after_advance(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test updating an EWA account after taking an advance.
    
    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_ewa_account.id
    original_balance = test_ewa_account.current_balance
    advance_amount = Decimal("50.00")

    # 2. SCHEMA: Create update data to record an advance
    update_schema = create_ewa_account_schema(
        current_balance=original_balance
        + advance_amount,  # Advance increases balance
        next_payday=test_ewa_account.next_payday,  # Keep the same payday
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account
    result = await ewa_repository.update(account_id, validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.current_balance == original_balance + advance_amount


async def test_feature_flag_controls_account_creation(
    db_session, feature_flag_service
):
    """
    Test that feature flags control EWA account creation through the proxy layer.
    
    Args:
        db_session: Database session fixture
        feature_flag_service: Feature flag service fixture
    """
    
    # 1. ARRANGE: Create a zero-TTL config provider with specific requirements
    config_provider = ZeroTTLConfigProvider({
        "EWA_ACCOUNTS_ENABLED": {
            "repository": {
                "create_typed_account": ["ewa"],
            }
        }
    })
    
    # Create repository with proxy and configure feature flags
    ewa_repository = RepositoryFactory.create_account_repository(
        db_session, 
        account_type="ewa", 
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Disable the EWA account feature flag
    await feature_flag_service.set_enabled("EWA_ACCOUNTS_ENABLED", False)

    # 2. SCHEMA: Create valid schema
    account_schema = create_ewa_account_schema()
    validated_data = account_schema.model_dump()

    # 3. ACT & ASSERT: Should fail when flag is disabled with a FeatureDisabledError
    with pytest.raises(FeatureDisabledError) as excinfo:
        await ewa_repository.create_typed_account("ewa", validated_data)

    # The error should be related to features being disabled
    error_msg = str(excinfo.value)
    assert any(x in error_msg for x in ["feature", "disabled", "not enabled"])

    # Now enable the flag and retry
    await feature_flag_service.set_enabled("EWA_ACCOUNTS_ENABLED", True)
    
    # Ensure only invalid fields are excluded
    invalid_fields = ["available_credit"]
    filtered_data = {
        k: v for k, v in validated_data.items() if k not in invalid_fields
    }
    result = await ewa_repository.create_typed_account("ewa", filtered_data)

    # 4. ASSERT: Should succeed when flag is enabled
    assert result is not None
    assert result.account_type == "ewa"
