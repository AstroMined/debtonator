# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for BNPL account repository advanced operations.

Tests specialized methods from the bnpl repository module.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.bnpl import BNPLAccount
from src.repositories.account_types.banking.bnpl import (
    get_bnpl_accounts_by_payment_frequency,
    get_bnpl_accounts_by_provider,
    get_bnpl_accounts_with_remaining_installments,
    get_bnpl_accounts_with_upcoming_payments,
)
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.bnpl_schema_factories import (
    create_bnpl_account_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_bnpl_accounts_with_upcoming_payments(
    db_session: AsyncSession,
    test_bnpl_account: BNPLAccount,  # Payment in 14 days
    test_bnpl_account_with_upcoming_payment: BNPLAccount,  # Payment in 3 days
):
    """
    Test getting BNPL accounts with upcoming payments.

    This test verifies that the specialized repository method correctly
    identifies BNPL accounts with payments due within a specified window.

    Args:
        db_session: Database session for repository operations
        test_bnpl_account: BNPL account with payment in 14 days
        test_bnpl_account_with_upcoming_payment: BNPL account with payment in 3 days
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method with 7-day window
    accounts_with_upcoming_payments = await get_bnpl_accounts_with_upcoming_payments(
        db_session, 7
    )

    # 4. ASSERT: Verify the results
    assert len(accounts_with_upcoming_payments) >= 1

    # Check if the account with a soon payment is included
    account_ids = [account.id for account in accounts_with_upcoming_payments]
    assert test_bnpl_account_with_upcoming_payment.id in account_ids

    # Check if the account with a later payment is excluded when window is 7 days
    assert test_bnpl_account.id not in account_ids

    # Now check with a larger window (20 days) - should include both accounts
    accounts_with_payments_20_days = await get_bnpl_accounts_with_upcoming_payments(
        db_session, 20
    )
    account_ids_20_days = [account.id for account in accounts_with_payments_20_days]
    assert test_bnpl_account.id in account_ids_20_days
    assert test_bnpl_account_with_upcoming_payment.id in account_ids_20_days


@pytest.mark.asyncio
async def test_get_bnpl_accounts_by_provider(
    db_session: AsyncSession,
    test_bnpl_account: BNPLAccount,  # Affirm
    test_bnpl_account_with_upcoming_payment: BNPLAccount,  # Klarna
    test_bnpl_account_nearly_paid: BNPLAccount,  # Afterpay
):
    """
    Test getting BNPL accounts by provider.

    This test verifies that the specialized repository method correctly
    filters BNPL accounts by their provider.

    Args:
        db_session: Database session for repository operations
        test_bnpl_account: BNPL account with Affirm provider
        test_bnpl_account_with_upcoming_payment: BNPL account with Klarna provider
        test_bnpl_account_nearly_paid: BNPL account with Afterpay provider
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method for each provider
    affirm_accounts = await get_bnpl_accounts_by_provider(db_session, "Affirm")
    klarna_accounts = await get_bnpl_accounts_by_provider(db_session, "Klarna")
    afterpay_accounts = await get_bnpl_accounts_by_provider(db_session, "Afterpay")

    # 4. ASSERT: Verify the results
    assert len(affirm_accounts) >= 1
    assert all(account.bnpl_provider == "Affirm" for account in affirm_accounts)
    assert test_bnpl_account.id in [account.id for account in affirm_accounts]

    assert len(klarna_accounts) >= 1
    assert all(account.bnpl_provider == "Klarna" for account in klarna_accounts)
    assert test_bnpl_account_with_upcoming_payment.id in [
        account.id for account in klarna_accounts
    ]

    assert len(afterpay_accounts) >= 1
    assert all(account.bnpl_provider == "Afterpay" for account in afterpay_accounts)
    assert test_bnpl_account_nearly_paid.id in [
        account.id for account in afterpay_accounts
    ]


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
    await bnpl_repository.update_typed_entity(account_id, "bnpl", validated_data)

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


@pytest.mark.asyncio
async def test_get_bnpl_accounts_with_remaining_installments(
    db_session: AsyncSession,
    test_bnpl_account: BNPLAccount,  # 4 installments, 0 paid
    test_bnpl_account_with_upcoming_payment: BNPLAccount,  # 4 installments, 1 paid
    test_bnpl_account_nearly_paid: BNPLAccount,  # 4 installments, 3 paid
):
    """
    Test getting BNPL accounts with specified remaining installments.

    This test verifies that the specialized repository method correctly
    filters BNPL accounts based on their remaining installments.

    Args:
        db_session: Database session for repository operations
        test_bnpl_account: BNPL account with 4 installments, 0 paid
        test_bnpl_account_with_upcoming_payment: BNPL account with 4 installments, 1 paid
        test_bnpl_account_nearly_paid: BNPL account with 4 installments, 3 paid
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method with different thresholds
    accounts_3_or_more_remaining = await get_bnpl_accounts_with_remaining_installments(
        db_session, 3
    )
    accounts_2_or_more_remaining = await get_bnpl_accounts_with_remaining_installments(
        db_session, 2
    )
    accounts_1_or_more_remaining = await get_bnpl_accounts_with_remaining_installments(
        db_session, 1
    )

    # 4. ASSERT: Verify the results
    # 3+ remaining installments - only the first account (4 - 0 = 4 remaining)
    assert len(accounts_3_or_more_remaining) >= 1
    account_ids_3_plus = [account.id for account in accounts_3_or_more_remaining]
    assert test_bnpl_account.id in account_ids_3_plus
    # test_bnpl_account_with_upcoming_payment has 3 remaining installments (4 - 1 = 3)
    # so it should be included in the 3+ remaining results
    assert test_bnpl_account_with_upcoming_payment.id in account_ids_3_plus
    assert (
        test_bnpl_account_nearly_paid.id not in account_ids_3_plus
    )  # (4 - 3 = 1 remaining)

    # 2+ remaining installments - first two accounts
    assert len(accounts_2_or_more_remaining) >= 2
    account_ids_2_plus = [account.id for account in accounts_2_or_more_remaining]
    assert test_bnpl_account.id in account_ids_2_plus
    assert test_bnpl_account_with_upcoming_payment.id in account_ids_2_plus
    assert test_bnpl_account_nearly_paid.id not in account_ids_2_plus

    # 1+ remaining installments - all accounts
    assert len(accounts_1_or_more_remaining) >= 3
    account_ids_1_plus = [account.id for account in accounts_1_or_more_remaining]
    assert test_bnpl_account.id in account_ids_1_plus
    assert test_bnpl_account_with_upcoming_payment.id in account_ids_1_plus
    assert test_bnpl_account_nearly_paid.id in account_ids_1_plus


@pytest.mark.asyncio
async def test_get_bnpl_accounts_by_payment_frequency(
    db_session: AsyncSession,
    test_bnpl_account: BNPLAccount,  # biweekly
    test_bnpl_account_with_upcoming_payment: BNPLAccount,  # biweekly
    test_bnpl_account_nearly_paid: BNPLAccount,  # biweekly
):
    """
    Test getting BNPL accounts by payment frequency.

    This test verifies that the specialized repository method correctly
    filters BNPL accounts based on their payment frequency.

    Args:
        db_session: Database session for repository operations
        test_bnpl_account: BNPL account with biweekly payment frequency
        test_bnpl_account_with_upcoming_payment: BNPL account with biweekly payment frequency
        test_bnpl_account_nearly_paid: BNPL account with biweekly payment frequency
    """
    # 1. ARRANGE: Create an additional account with monthly frequency
    monthly_schema = create_bnpl_account_schema(
        name="Monthly Payment BNPL",
        bnpl_provider="SplitIt",
        payment_frequency="monthly",
    )
    monthly_account = BNPLAccount(**monthly_schema.model_dump())
    db_session.add(monthly_account)
    await db_session.flush()

    # 2. SCHEMA: Used for creating the monthly account

    # 3. ACT: Call the specialized repository method for each frequency
    biweekly_accounts = await get_bnpl_accounts_by_payment_frequency(
        db_session, "biweekly"
    )
    monthly_accounts = await get_bnpl_accounts_by_payment_frequency(
        db_session, "monthly"
    )

    # 4. ASSERT: Verify the results
    assert len(biweekly_accounts) >= 3
    assert all(account.payment_frequency == "biweekly" for account in biweekly_accounts)
    biweekly_ids = [account.id for account in biweekly_accounts]
    assert test_bnpl_account.id in biweekly_ids
    assert test_bnpl_account_with_upcoming_payment.id in biweekly_ids
    assert test_bnpl_account_nearly_paid.id in biweekly_ids

    assert len(monthly_accounts) >= 1
    assert all(account.payment_frequency == "monthly" for account in monthly_accounts)
    assert monthly_account.id in [account.id for account in monthly_accounts]


@pytest.mark.asyncio
async def test_repository_has_specialized_methods(bnpl_repository: AccountRepository):
    """
    Test that the repository has the specialized BNPL methods.

    This test verifies that the BNPL repository correctly includes
    all the specialized methods for BNPL account operations.

    Args:
        bnpl_repository: BNPL account repository from fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Verify the repository has specialized BNPL methods
    assert hasattr(bnpl_repository, "get_bnpl_accounts_with_upcoming_payments")
    assert callable(
        getattr(bnpl_repository, "get_bnpl_accounts_with_upcoming_payments")
    )

    assert hasattr(bnpl_repository, "get_bnpl_accounts_by_provider")
    assert callable(getattr(bnpl_repository, "get_bnpl_accounts_by_provider"))

    assert hasattr(bnpl_repository, "get_bnpl_accounts_with_remaining_installments")
    assert callable(
        getattr(bnpl_repository, "get_bnpl_accounts_with_remaining_installments")
    )

    assert hasattr(bnpl_repository, "get_bnpl_accounts_by_payment_frequency")
    assert callable(getattr(bnpl_repository, "get_bnpl_accounts_by_payment_frequency"))
