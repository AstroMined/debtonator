# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for PaymentApp account repository advanced operations.

Tests specialized methods from the payment_app repository module.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.payment_app import PaymentAppAccount
from src.repositories.account_types.banking.payment_app import (
    get_payment_app_accounts_by_platform,
    get_payment_app_accounts_with_debit_cards,
    get_payment_app_accounts_with_direct_deposit,
    get_payment_app_accounts_with_linked_accounts,
)
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.payment_app_schema_factories import (
    create_payment_app_account_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_payment_app_accounts_by_platform(
    db_session: AsyncSession,
    test_payment_app_account: PaymentAppAccount,  # PayPal
):
    """
    Test getting payment app accounts by platform.
    
    This test verifies that the specialized repository method correctly
    filters payment app accounts by their platform.
    
    Args:
        db_session: Database session for repository operations
        test_payment_app_account: Payment app account with PayPal platform
    """
    # 1. ARRANGE: Create additional accounts with different platforms
    # First account comes from fixture (PayPal platform)

    # Create Venmo account
    venmo_schema = create_payment_app_account_schema(
        name="Test Venmo Account", platform="Venmo"
    )
    venmo_account = PaymentAppAccount(**venmo_schema.model_dump())
    db_session.add(venmo_account)

    # Create another PayPal account
    paypal_schema = create_payment_app_account_schema(
        name="Another PayPal Account", platform="PayPal"
    )
    paypal_account = PaymentAppAccount(**paypal_schema.model_dump())
    db_session.add(paypal_account)

    await db_session.flush()

    # 2. SCHEMA: Used for creating the test accounts

    # 3. ACT: Call the specialized repository method
    paypal_accounts = await get_payment_app_accounts_by_platform(
        db_session, "PayPal"
    )
    venmo_accounts = await get_payment_app_accounts_by_platform(db_session, "Venmo")

    # 4. ASSERT: Verify the results
    assert len(paypal_accounts) == 2
    assert all(account.platform == "PayPal" for account in paypal_accounts)

    assert len(venmo_accounts) == 1
    assert venmo_accounts[0].platform == "Venmo"


@pytest.mark.asyncio
async def test_get_payment_app_accounts_with_debit_cards(
    db_session: AsyncSession,
    test_payment_app_account: PaymentAppAccount,  # Has debit card
    test_payment_app_account_with_linked_accounts: PaymentAppAccount,  # No debit card
):
    """
    Test getting payment app accounts with debit cards.
    
    This test verifies that the specialized repository method correctly
    identifies payment app accounts that have debit cards.
    
    Args:
        db_session: Database session for repository operations
        test_payment_app_account: Payment app account with debit card
        test_payment_app_account_with_linked_accounts: Payment app account without debit card
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    accounts_with_debit_cards = await get_payment_app_accounts_with_debit_cards(
        db_session
    )

    # 4. ASSERT: Verify the results
    assert len(accounts_with_debit_cards) >= 1
    assert all(account.has_debit_card for account in accounts_with_debit_cards)

    # Verify that the test_payment_app_account is included (has debit card)
    account_ids = [account.id for account in accounts_with_debit_cards]
    assert test_payment_app_account.id in account_ids

    # Verify that the test_payment_app_account_with_linked_accounts is not included (no debit card)
    assert test_payment_app_account_with_linked_accounts.id not in account_ids


@pytest.mark.asyncio
async def test_get_payment_app_accounts_with_linked_accounts(
    db_session: AsyncSession,
    test_payment_app_account: PaymentAppAccount,  # No linked accounts
    test_payment_app_account_with_linked_accounts: PaymentAppAccount,  # Has linked accounts
):
    """
    Test getting payment app accounts with linked accounts.
    
    This test verifies that the specialized repository method correctly
    identifies payment app accounts that have linked accounts.
    
    Args:
        db_session: Database session for repository operations
        test_payment_app_account: Payment app account without linked accounts
        test_payment_app_account_with_linked_accounts: Payment app account with linked accounts
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    accounts_with_linked = await get_payment_app_accounts_with_linked_accounts(
        db_session
    )

    # 4. ASSERT: Verify the results
    assert len(accounts_with_linked) >= 1
    assert all(account.linked_account_ids for account in accounts_with_linked)

    # Verify that the test_payment_app_account_with_linked_accounts is included
    account_ids = [account.id for account in accounts_with_linked]
    assert test_payment_app_account_with_linked_accounts.id in account_ids

    # Verify that the test_payment_app_account is not included (no linked accounts)
    assert test_payment_app_account.id not in account_ids


@pytest.mark.asyncio
async def test_get_payment_app_accounts_with_direct_deposit(
    db_session: AsyncSession,
    test_payment_app_account: PaymentAppAccount,  # No direct deposit
    test_payment_app_account_with_linked_accounts: PaymentAppAccount,  # Has direct deposit
):
    """
    Test getting payment app accounts with direct deposit enabled.
    
    This test verifies that the specialized repository method correctly
    identifies payment app accounts that support direct deposit.
    
    Args:
        db_session: Database session for repository operations
        test_payment_app_account: Payment app account without direct deposit
        test_payment_app_account_with_linked_accounts: Payment app account with direct deposit
    """
    # 1. ARRANGE: Accounts are set up via fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    accounts_with_direct_deposit = (
        await get_payment_app_accounts_with_direct_deposit(db_session)
    )

    # 4. ASSERT: Verify the results
    assert len(accounts_with_direct_deposit) >= 1
    assert all(
        account.supports_direct_deposit for account in accounts_with_direct_deposit
    )

    # Verify that the test_payment_app_account_with_linked_accounts is included
    account_ids = [account.id for account in accounts_with_direct_deposit]
    assert test_payment_app_account_with_linked_accounts.id in account_ids

    # Verify that the test_payment_app_account is not included (no direct deposit)
    assert test_payment_app_account.id not in account_ids


@pytest.mark.asyncio
async def test_repository_has_specialized_methods(
    payment_app_repository: AccountRepository
):
    """
    Test that the repository has the specialized payment app methods.
    
    This test verifies that the payment app repository correctly includes
    all the specialized methods for payment app account operations.
    
    Args:
        payment_app_repository: Payment app account repository from fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Verify the repository has specialized payment app methods
    assert hasattr(payment_app_repository, "get_payment_app_accounts_by_platform")
    assert callable(getattr(payment_app_repository, "get_payment_app_accounts_by_platform"))

    assert hasattr(payment_app_repository, "get_payment_app_accounts_with_debit_cards")
    assert callable(
        getattr(payment_app_repository, "get_payment_app_accounts_with_debit_cards")
    )

    assert hasattr(payment_app_repository, "get_payment_app_accounts_with_linked_accounts")
    assert callable(
        getattr(payment_app_repository, "get_payment_app_accounts_with_linked_accounts")
    )

    assert hasattr(payment_app_repository, "get_payment_app_accounts_with_direct_deposit")
    assert callable(
        getattr(payment_app_repository, "get_payment_app_accounts_with_direct_deposit")
    )
