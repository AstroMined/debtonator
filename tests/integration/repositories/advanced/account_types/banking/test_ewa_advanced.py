# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for EWA account repository advanced operations.

Tests specialized methods from the ewa repository module.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.ewa import EWAAccount
from src.repositories.account_types.banking.ewa import (
    get_ewa_accounts_approaching_payday,
    get_ewa_accounts_by_advance_percentage,
    get_ewa_accounts_by_provider,
    get_ewa_accounts_with_no_transaction_fee,
)
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.ewa_schema_factories import (
    create_ewa_account_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_ewa_accounts_approaching_payday(
    db_session: AsyncSession,
    test_ewa_account: EWAAccount,  # Payday in 7 days
    test_ewa_account_approaching_payday: EWAAccount,  # Payday in 2 days
):
    """
    Test getting EWA accounts with approaching paydays.

    This test verifies that the specialized repository method correctly
    identifies EWA accounts with paydays approaching within a specified window.

    Args:
        db_session: Database session for repository operations
        test_ewa_account: EWA account with payday in 7 days
        test_ewa_account_approaching_payday: EWA account with payday in 2 days
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method with 3-day window
    accounts_with_approaching_payday = await get_ewa_accounts_approaching_payday(
        db_session, 3
    )

    # 4. ASSERT: Verify the results
    assert len(accounts_with_approaching_payday) >= 1

    # Check if the account with an imminent payday is included
    account_ids = [account.id for account in accounts_with_approaching_payday]
    assert test_ewa_account_approaching_payday.id in account_ids

    # Check if the account with a later payday is excluded when window is 3 days
    assert test_ewa_account.id not in account_ids

    # Now check with a larger window (10 days) - should include both accounts
    accounts_with_paydays_10_days = await get_ewa_accounts_approaching_payday(
        db_session, 10
    )
    account_ids_10_days = [account.id for account in accounts_with_paydays_10_days]
    assert test_ewa_account.id in account_ids_10_days
    assert test_ewa_account_approaching_payday.id in account_ids_10_days


@pytest.mark.asyncio
async def test_get_ewa_accounts_by_provider(
    db_session: AsyncSession,
    test_ewa_account: EWAAccount,  # PayActiv
    test_ewa_account_approaching_payday: EWAAccount,  # DailyPay
    test_ewa_account_no_transaction_fee: EWAAccount,  # Employer Direct
):
    """
    Test getting EWA accounts by provider.

    This test verifies that the specialized repository method correctly
    filters EWA accounts by their provider.

    Args:
        db_session: Database session for repository operations
        test_ewa_account: EWA account with PayActiv provider
        test_ewa_account_approaching_payday: EWA account with DailyPay provider
        test_ewa_account_no_transaction_fee: EWA account with Employer Direct provider
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method for each provider
    payactiv_accounts = await get_ewa_accounts_by_provider(db_session, "PayActiv")
    dailypay_accounts = await get_ewa_accounts_by_provider(db_session, "DailyPay")
    employer_direct_accounts = await get_ewa_accounts_by_provider(
        db_session, "Employer Direct"
    )

    # 4. ASSERT: Verify the results
    assert len(payactiv_accounts) >= 1
    assert all(account.provider == "PayActiv" for account in payactiv_accounts)
    assert test_ewa_account.id in [account.id for account in payactiv_accounts]

    assert len(dailypay_accounts) >= 1
    assert all(account.provider == "DailyPay" for account in dailypay_accounts)
    assert test_ewa_account_approaching_payday.id in [
        account.id for account in dailypay_accounts
    ]

    assert len(employer_direct_accounts) >= 1
    assert all(
        account.provider == "Employer Direct" for account in employer_direct_accounts
    )
    assert test_ewa_account_no_transaction_fee.id in [
        account.id for account in employer_direct_accounts
    ]


@pytest.mark.asyncio
async def test_get_ewa_accounts_by_advance_percentage(
    db_session: AsyncSession,
    test_ewa_account: EWAAccount,  # 50%
    test_ewa_account_approaching_payday: EWAAccount,  # 50%
    test_ewa_account_no_transaction_fee: EWAAccount,  # 75%
):
    """
    Test getting EWA accounts with a specific advance percentage range.

    This test verifies that the specialized repository method correctly
    filters EWA accounts based on their maximum advance percentage.

    Args:
        db_session: Database session for repository operations
        test_ewa_account: EWA account with 50% max advance
        test_ewa_account_approaching_payday: EWA account with 50% max advance
        test_ewa_account_no_transaction_fee: EWA account with 75% max advance
    """
    # 1. ARRANGE: Create an additional account with a 25% max advance
    low_percentage_schema = create_ewa_account_schema(
        name="Limited Advance EWA",
        provider="Even",
        max_advance_percentage=Decimal("25.00"),
    )
    low_percentage_account = EWAAccount(**low_percentage_schema.model_dump())
    db_session.add(low_percentage_account)
    await db_session.flush()

    # 2. SCHEMA: Used for creating the low percentage account

    # 3. ACT: Call the specialized repository method with different ranges
    # Range: 20-30%
    low_range_accounts = await get_ewa_accounts_by_advance_percentage(
        db_session, Decimal("20.00"), Decimal("30.00")
    )

    # Range: 45-55%
    mid_range_accounts = await get_ewa_accounts_by_advance_percentage(
        db_session, Decimal("45.00"), Decimal("55.00")
    )

    # Range: 70-80%
    high_range_accounts = await get_ewa_accounts_by_advance_percentage(
        db_session, Decimal("70.00"), Decimal("80.00")
    )

    # 4. ASSERT: Verify the results
    # Low range should include the 25% account
    assert len(low_range_accounts) >= 1
    low_range_ids = [account.id for account in low_range_accounts]
    assert low_percentage_account.id in low_range_ids

    # Mid range should include the 50% accounts
    assert len(mid_range_accounts) >= 2
    mid_range_ids = [account.id for account in mid_range_accounts]
    assert test_ewa_account.id in mid_range_ids
    assert test_ewa_account_approaching_payday.id in mid_range_ids

    # High range should include the 75% account
    assert len(high_range_accounts) >= 1
    high_range_ids = [account.id for account in high_range_accounts]
    assert test_ewa_account_no_transaction_fee.id in high_range_ids


@pytest.mark.asyncio
async def test_get_ewa_accounts_with_no_transaction_fee(
    db_session: AsyncSession,
    test_ewa_account: EWAAccount,  # Has $5.00 fee
    test_ewa_account_approaching_payday: EWAAccount,  # Has $2.99 fee
    test_ewa_account_no_transaction_fee: EWAAccount,  # Has $0.00 fee
):
    """
    Test getting EWA accounts with no transaction fee.

    This test verifies that the specialized repository method correctly
    identifies EWA accounts that don't charge transaction fees.

    Args:
        db_session: Database session for repository operations
        test_ewa_account: EWA account with $5.00 transaction fee
        test_ewa_account_approaching_payday: EWA account with $2.99 transaction fee
        test_ewa_account_no_transaction_fee: EWA account with $0.00 transaction fee
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    no_fee_accounts = await get_ewa_accounts_with_no_transaction_fee(db_session)

    # 4. ASSERT: Verify the results
    assert len(no_fee_accounts) >= 1
    no_fee_ids = [account.id for account in no_fee_accounts]

    # Check that only the no-fee account is included
    assert test_ewa_account_no_transaction_fee.id in no_fee_ids

    # Check that fee-charging accounts are excluded
    assert test_ewa_account.id not in no_fee_ids
    assert test_ewa_account_approaching_payday.id not in no_fee_ids


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
        current_balance=original_balance + advance_amount,  # Advance increases balance
        next_payday=test_ewa_account.next_payday,  # Keep the same payday
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account
    result = await ewa_repository.update_typed_entity(account_id, "ewa", validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.current_balance == original_balance + advance_amount


@pytest.mark.asyncio
async def test_repository_has_specialized_methods(ewa_repository: AccountRepository):
    """
    Test that the repository has the specialized EWA methods.

    This test verifies that the EWA repository correctly includes
    all the specialized methods for EWA account operations.

    Args:
        ewa_repository: EWA account repository from fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Verify the repository has specialized EWA methods
    assert hasattr(ewa_repository, "get_ewa_accounts_approaching_payday")
    assert callable(getattr(ewa_repository, "get_ewa_accounts_approaching_payday"))

    assert hasattr(ewa_repository, "get_ewa_accounts_by_provider")
    assert callable(getattr(ewa_repository, "get_ewa_accounts_by_provider"))

    assert hasattr(ewa_repository, "get_ewa_accounts_by_advance_percentage")
    assert callable(getattr(ewa_repository, "get_ewa_accounts_by_advance_percentage"))

    assert hasattr(ewa_repository, "get_ewa_accounts_with_no_transaction_fee")
    assert callable(getattr(ewa_repository, "get_ewa_accounts_with_no_transaction_fee"))
