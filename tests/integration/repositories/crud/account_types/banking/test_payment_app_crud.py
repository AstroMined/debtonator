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
    result = await payment_app_repository.create_typed_account(
        "payment_app", validated_data
    )

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
    payment_app_repository: AccountRepository,
    test_payment_app_account: PaymentAppAccount,
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
    payment_app_repository: AccountRepository,
    test_payment_app_account: PaymentAppAccount,
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

    # 3. ACT: Update the account using typed update method
    result = await payment_app_repository.update_typed_account(
        account_id=account_id, account_type="payment_app", data=validated_data
    )

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
    payment_app_repository: AccountRepository,
    test_payment_app_account: PaymentAppAccount,
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
