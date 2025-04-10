"""
Integration tests for checking account repository advanced operations.

This module tests the specialized operations in the checking account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.repositories.accounts import AccountRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.account_types.banking.checking_schema_factories import (
    create_checking_account_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_checking_accounts_with_overdraft(
    checking_repository: AccountRepository,
    test_checking_account: CheckingAccount,
    db_session: AsyncSession,
):
    """
    Test getting checking accounts with overdraft protection.
    
    This test verifies that the specialized repository method correctly
    identifies checking accounts that have overdraft protection enabled.
    
    Args:
        checking_repository: Checking account repository
        test_checking_account: Checking account fixture
        db_session: Database session
    """
    # 1. ARRANGE: Create an account with overdraft protection
    overdraft_schema = create_checking_account_schema(
        name="With Overdraft",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )
    
    overdraft_account = CheckingAccount(**overdraft_schema.model_dump())
    db_session.add(overdraft_account)
    await db_session.flush()

    # Ensure the test_checking_account has overdraft protection disabled
    if test_checking_account.has_overdraft_protection:
        test_checking_account.has_overdraft_protection = False
        await db_session.flush()

    # 2. SCHEMA: Used for creating the test account

    # 3. ACT: Call the specialized repository method
    with_overdraft = await checking_repository.get_checking_accounts_with_overdraft()

    # 4. ASSERT: Verify the results
    assert len(with_overdraft) >= 1  # Should at least have the account we just created
    assert all(a.has_overdraft_protection for a in with_overdraft)

    # Verify the overdraft account is in the results
    account_ids = [a.id for a in with_overdraft]
    assert overdraft_account.id in account_ids

    # Verify the test account without overdraft is not in the results
    assert test_checking_account.id not in account_ids


@pytest.mark.asyncio
async def test_get_checking_accounts_by_balance_range(
    checking_repository: AccountRepository, db_session: AsyncSession
):
    """
    Test getting checking accounts within a balance range.
    
    This test verifies that the specialized repository method correctly
    filters checking accounts based on their available balance.
    
    Args:
        checking_repository: Checking account repository
        db_session: Database session
    """
    # 1. ARRANGE: Create accounts with different balances
    low_balance_schema = create_checking_account_schema(
        name="Low Balance",
        current_balance=Decimal("100.00"),
        available_balance=Decimal("100.00"),
    )
    
    mid_balance_schema = create_checking_account_schema(
        name="Mid Balance",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
    )
    
    high_balance_schema = create_checking_account_schema(
        name="High Balance",
        current_balance=Decimal("1500.00"),
        available_balance=Decimal("1500.00"),
    )

    low_balance = CheckingAccount(**low_balance_schema.model_dump())
    mid_balance = CheckingAccount(**mid_balance_schema.model_dump())
    high_balance = CheckingAccount(**high_balance_schema.model_dump())

    db_session.add_all([low_balance, mid_balance, high_balance])
    await db_session.flush()

    # 2. SCHEMA: Used for creating the test accounts

    # 3. ACT: Call the specialized repository method
    between_400_and_1000 = await checking_repository.get_checking_accounts_by_balance_range(
        Decimal("400.00"), Decimal("1000.00")
    )

    # 4. ASSERT: Verify the results
    assert len(between_400_and_1000) >= 1  # Should at least have mid_balance

    # Verify correct accounts are in the results
    account_ids = [a.id for a in between_400_and_1000]
    assert mid_balance.id in account_ids
    assert low_balance.id not in account_ids
    assert high_balance.id not in account_ids

    # All accounts should have balances within the range
    assert all(
        Decimal("400.00") <= a.available_balance <= Decimal("1000.00")
        for a in between_400_and_1000
    )


@pytest.mark.asyncio
async def test_get_checking_accounts_with_international_features(
    checking_repository: AccountRepository,
    test_international_checking: CheckingAccount,
    test_checking_account: CheckingAccount,
):
    """
    Test getting checking accounts with international features.
    
    This test verifies that the specialized repository method correctly
    identifies checking accounts that have international banking features.
    
    Args:
        checking_repository: Checking account repository
        test_international_checking: International checking account fixture
        test_checking_account: Regular checking account fixture
    """
    # 1. ARRANGE: Accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    international_accounts = await checking_repository.get_checking_accounts_with_international_features()

    # 4. ASSERT: Verify the results
    assert len(international_accounts) >= 1

    # Verify the international account is in the results
    account_ids = [a.id for a in international_accounts]
    assert test_international_checking.id in account_ids

    # Verify regular checking account is not in the results (assuming it doesn't have international features)
    assert test_checking_account.id not in account_ids

    # All accounts should have at least one international feature
    for account in international_accounts:
        has_international_feature = (
            account.iban is not None
            or account.swift_bic is not None
            or account.sort_code is not None
            or account.branch_code is not None
            or account.account_format != "local"
        )
        assert has_international_feature


@pytest.mark.asyncio
async def test_get_checking_accounts_without_fees(
    checking_repository: AccountRepository, db_session: AsyncSession
):
    """
    Test getting checking accounts without monthly fees.
    
    This test verifies that the specialized repository method correctly
    identifies checking accounts that don't have monthly fees.
    
    Args:
        checking_repository: Checking account repository
        db_session: Database session
    """
    # 1. ARRANGE: Create accounts with and without fees
    with_fee_schema = create_checking_account_schema(
        name="With Fee",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        monthly_fee=Decimal("10.00"),
    )
    
    no_fee_schema = create_checking_account_schema(
        name="No Fee",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        monthly_fee=Decimal("0.00"),
    )
    
    null_fee_schema = create_checking_account_schema(
        name="Null Fee",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    # Set monthly_fee to None after creation since schema might not allow None
    null_fee_data = null_fee_schema.model_dump()
    null_fee_data["monthly_fee"] = None

    with_fee = CheckingAccount(**with_fee_schema.model_dump())
    no_fee = CheckingAccount(**no_fee_schema.model_dump())
    null_fee = CheckingAccount(**null_fee_data)

    db_session.add_all([with_fee, no_fee, null_fee])
    await db_session.flush()

    # 2. SCHEMA: Used for creating the test accounts

    # 3. ACT: Call the specialized repository method
    fee_free_accounts = await checking_repository.get_checking_accounts_without_fees()

    # 4. ASSERT: Verify the results
    assert len(fee_free_accounts) >= 2  # Should have no_fee and null_fee

    # Verify correct accounts are in the results
    account_ids = [a.id for a in fee_free_accounts]
    assert no_fee.id in account_ids
    assert null_fee.id in account_ids
    assert with_fee.id not in account_ids

    # All accounts should have no fees or null fees
    for account in fee_free_accounts:
        assert account.monthly_fee is None or account.monthly_fee == 0


@pytest.mark.asyncio
async def test_repository_has_specialized_methods(
    checking_repository: AccountRepository
):
    """
    Test that the repository has the specialized checking methods.
    
    This test verifies that the checking repository correctly includes
    all the specialized methods for checking account operations.
    
    Args:
        checking_repository: Checking account repository
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Verify the repository has specialized checking methods
    assert hasattr(checking_repository, "get_checking_accounts_with_overdraft")
    assert callable(getattr(checking_repository, "get_checking_accounts_with_overdraft"))

    assert hasattr(checking_repository, "get_checking_accounts_by_balance_range")
    assert callable(getattr(checking_repository, "get_checking_accounts_by_balance_range"))

    assert hasattr(checking_repository, "get_checking_accounts_with_international_features")
    assert callable(getattr(checking_repository, "get_checking_accounts_with_international_features"))

    assert hasattr(checking_repository, "get_checking_accounts_without_fees")
    assert callable(getattr(checking_repository, "get_checking_accounts_without_fees"))
