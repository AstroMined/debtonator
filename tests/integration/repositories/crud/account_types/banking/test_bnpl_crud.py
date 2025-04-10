# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for BNPL account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.bnpl import BNPLAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.bnpl_schema_factories import (
    create_bnpl_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_bnpl_account(bnpl_repository: AccountRepository):
    """
    Test creating a BNPL account following the four-step pattern.
    
    Args:
        bnpl_repository: Repository fixture for BNPL accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_bnpl_account_schema(
        name="My Affirm Account",
        bnpl_provider="Affirm",
        current_balance=Decimal("400.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00"),
        payment_frequency="biweekly",
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    # Ensure only invalid fields are excluded
    invalid_fields = ["available_credit"]
    filtered_data = {
        k: v for k, v in validated_data.items() if k not in invalid_fields
    }
    result = await bnpl_repository.create_typed_account("bnpl", filtered_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, BNPLAccount)
    assert result.id is not None
    assert result.name == "My Affirm Account"
    assert result.bnpl_provider == "Affirm"
    assert result.current_balance == Decimal("400.00")
    assert result.installment_count == 4
    assert result.installments_paid == 0
    assert result.installment_amount == Decimal("100.00")
    assert result.payment_frequency == "biweekly"


async def test_get_bnpl_account(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test retrieving a BNPL account by ID.
    
    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await bnpl_repository.get(test_bnpl_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, BNPLAccount)
    assert result.id == test_bnpl_account.id
    assert result.name == test_bnpl_account.name
    assert result.bnpl_provider == test_bnpl_account.bnpl_provider


async def test_update_bnpl_account(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test updating a BNPL account.
    
    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_bnpl_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_bnpl_account_schema(
        name="Updated Affirm Account",
        installments_paid=1,  # Increment the installments paid
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await bnpl_repository.update_typed_account(
        account_id=account_id,
        account_type="bnpl",
        data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, BNPLAccount)
    assert result.id == account_id
    assert result.name == "Updated Affirm Account"
    assert result.installments_paid == 1
    # Original properties should remain unchanged
    assert result.bnpl_provider == test_bnpl_account.bnpl_provider
    assert result.installment_count == test_bnpl_account.installment_count
    assert result.installment_amount == test_bnpl_account.installment_amount


async def test_delete_bnpl_account(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test deleting (soft delete) a BNPL account.
    
    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_bnpl_account.id

    # 2. ACT: Delete the account
    result = await bnpl_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await bnpl_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True


async def test_mark_bnpl_payment_made(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test updating a BNPL account to mark a payment as made.
    
    This test demonstrates the proper fetch-update-refetch pattern that should be used
    in real application code when working with SQLAlchemy entities.
    
    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # NOTE: We deliberately use a fetch-update-refetch pattern here to properly
    # validate state changes. Due to SQLAlchemy's identity map, holding a reference
    # to an entity and then updating that same entity will update all references
    # to the object. Real application code should follow this pattern of refetching
    # entities after updates to ensure the latest state is observed.
    
    # 1. ARRANGE: Fetch initial state directly from database
    account_id = test_bnpl_account.id
    
    # Get the original values directly from the database
    account_before = await bnpl_repository.get(account_id)
    original_installments_paid = account_before.installments_paid
    original_balance = account_before.current_balance
    installment_amount = account_before.installment_amount
    
    # 2. SCHEMA: Create update data to record a payment
    update_schema = create_bnpl_account_schema(
        # Include required fields to ensure a complete update
        name=account_before.name,
        account_type="bnpl",
        bnpl_provider=account_before.bnpl_provider,
        installment_count=account_before.installment_count,
        installment_amount=account_before.installment_amount,
        payment_frequency=account_before.payment_frequency,
        original_amount=account_before.original_amount,
        # The values we want to update
        current_balance=original_balance - installment_amount,
        installments_paid=original_installments_paid + 1,
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Perform the update operation
    await bnpl_repository.update_typed_account(
        account_id=account_id,
        account_type="bnpl",
        data=validated_data
    )
    
    # 4. VERIFY: Get a fresh instance from DB to verify changes
    account_after = await bnpl_repository.get(account_id)
    
    # 5. ASSERT: Verify against the freshly loaded instance
    assert account_after is not None
    assert account_after.current_balance == original_balance - installment_amount
    assert account_after.installments_paid == original_installments_paid + 1
    
    # Document additional identity map behavior:
    # Due to SQLAlchemy's identity map, the original reference will also show the updates
    # This is EXPECTED behavior and can be verified:
    assert test_bnpl_account.installments_paid == original_installments_paid + 1


async def test_feature_flag_controls_account_creation(
    bnpl_repository: AccountRepository, feature_flag_service
):
    """
    Test that feature flags control BNPL account creation.
    
    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        feature_flag_service: Feature flag service fixture
    """
    # 1. ARRANGE: Disable the feature flag
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)

    # 2. SCHEMA: Create valid schema
    account_schema = create_bnpl_account_schema()
    validated_data = account_schema.model_dump()

    # 3. ACT & ASSERT: Should fail when flag is disabled
    with pytest.raises(ValueError) as excinfo:
        await bnpl_repository.create_typed_account(
            "bnpl", 
            validated_data, 
            feature_flag_service=feature_flag_service
        )

    # The message should contain either "not available", "not enabled", or the specific error message
    error_msg = str(excinfo.value)
    assert ("not available" in error_msg or 
            "not enabled" in error_msg or
            "not currently enabled" in error_msg)

    # Now enable the flag and retry
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)
    # Ensure only invalid fields are excluded
    invalid_fields = ["available_credit"]
    filtered_data = {
        k: v for k, v in validated_data.items() if k not in invalid_fields
    }
    result = await bnpl_repository.create_typed_account("bnpl", filtered_data)

    # 4. ASSERT: Should succeed when flag is enabled
    assert result is not None
    assert result.account_type == "bnpl"
