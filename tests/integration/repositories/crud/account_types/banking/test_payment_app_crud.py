# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for PaymentApp account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.payment_app import PaymentAppAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.payment_app_schema_factories import (
    create_payment_app_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_payment_app_account(payment_app_repository: AccountRepository):
    """
    Test creating a payment app account following the four-step pattern.
    
    Args:
        payment_app_repository: Repository fixture for payment app accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_payment_app_account_schema(
        name="My PayPal Account",
        platform="PayPal",
        current_balance=Decimal("150.00"),
        has_debit_card=True,
        card_last_four="1234",
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await payment_app_repository.create_typed_account("payment_app", validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, PaymentAppAccount)
    assert result.id is not None
    assert result.name == "My PayPal Account"
    assert result.platform == "PayPal"
    assert result.current_balance == Decimal("150.00")
    assert result.has_debit_card is True
    assert result.card_last_four == "1234"


async def test_get_payment_app_account(
    payment_app_repository: AccountRepository, test_payment_app_account: PaymentAppAccount
):
    """
    Test retrieving a payment app account by ID.
    
    Args:
        payment_app_repository: Repository fixture for payment app accounts
        test_payment_app_account: Test payment app account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await payment_app_repository.get(test_payment_app_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, PaymentAppAccount)
    assert result.id == test_payment_app_account.id
    assert result.name == test_payment_app_account.name
    assert result.platform == test_payment_app_account.platform


async def test_update_payment_app_account(
    payment_app_repository: AccountRepository, test_payment_app_account: PaymentAppAccount
):
    """
    Test updating a payment app account.
    
    Args:
        payment_app_repository: Repository fixture for payment app accounts
        test_payment_app_account: Test payment app account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_payment_app_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_payment_app_account_schema(
        name="Updated PayPal Account",
        has_debit_card=True,  # This is required when card_last_four is provided
        card_last_four="9876",
        supports_direct_deposit=True,
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account
    result = await payment_app_repository.update(account_id, validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, PaymentAppAccount)
    assert result.id == account_id
    assert result.name == "Updated PayPal Account"
    assert result.card_last_four == "9876"
    assert result.supports_direct_deposit is True
    # Original properties should remain unchanged
    assert result.platform == test_payment_app_account.platform
    assert result.current_balance == test_payment_app_account.current_balance


async def test_delete_payment_app_account(
    payment_app_repository: AccountRepository, test_payment_app_account: PaymentAppAccount
):
    """
    Test deleting (soft delete) a payment app account.
    
    Args:
        payment_app_repository: Repository fixture for payment app accounts
        test_payment_app_account: Test payment app account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_payment_app_account.id

    # 2. ACT: Delete the account
    result = await payment_app_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await payment_app_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True


async def test_feature_flag_controls_account_creation(
    db_session, feature_flag_service
):
    """
    Test that feature flags control payment app account creation through the proxy layer.
    
    Args:
        db_session: Database session fixture
        feature_flag_service: Feature flag service fixture
    """
    from src.repositories.factory import RepositoryFactory
    
    # 1. ARRANGE: Create repository with proxy and disable the feature flag
    payment_app_repository = RepositoryFactory.create_account_repository(
        db_session, account_type="payment_app", feature_flag_service=feature_flag_service
    )
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)

    # 2. SCHEMA: Create valid schema
    account_schema = create_payment_app_account_schema()
    validated_data = account_schema.model_dump()

    # 3. ACT & ASSERT: Should fail when flag is disabled with a FeatureDisabledError
    with pytest.raises(Exception) as excinfo:
        await payment_app_repository.create_typed_account("payment_app", validated_data)

    # The error should be related to features being disabled
    error_msg = str(excinfo.value)
    assert any(x in error_msg for x in ["feature", "disabled", "not enabled"])

    # Now enable the flag and retry
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)
    
    # Ensure only valid fields are included
    invalid_fields = ["available_credit"]
    filtered_data = {
        k: v for k, v in validated_data.items() if k not in invalid_fields
    }
    result = await payment_app_repository.create_typed_account("payment_app", filtered_data)

    # 4. ASSERT: Should succeed when flag is enabled
    assert result is not None
    assert result.account_type == "payment_app"
