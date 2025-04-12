"""
Integration tests for checking account repository advanced operations.

This module tests the specialized operations in the checking account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.registry.account_types import account_type_registry
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.checking_schema_factories import (
    create_checking_account_schema,
    create_checking_account_update_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_with_type_returns_checking_account(
    account_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test that get_with_type returns a CheckingAccount instance.

    This test verifies that the repository correctly retrieves a checking account
    with the appropriate polymorphic identity.

    Args:
        account_repository: Base account repository
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the account with type information
    result = await account_repository.get_with_type(test_checking_account.id)

    # 4. ASSERT: Verify the result is a checking account
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id == test_checking_account.id
    assert result.name == test_checking_account.name
    assert result.account_type == "checking"

    # Verify checking-specific fields are loaded
    assert hasattr(result, "has_overdraft_protection")
    if hasattr(test_checking_account, "routing_number"):
        assert result.routing_number == test_checking_account.routing_number


@pytest.mark.asyncio
async def test_get_by_type_returns_only_checking_accounts(
    account_repository: AccountRepository,
    test_checking_account: CheckingAccount,
    test_savings_account,
    test_credit_account,
):
    """
    Test that get_by_type returns only checking accounts.

    This test verifies that the repository correctly filters accounts by type
    when retrieving checking accounts.

    Args:
        account_repository: Base account repository
        test_checking_account: Checking account fixture
        test_savings_account: Savings account fixture
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve accounts by type
    checking_accounts = await account_repository.get_by_type("checking")

    # 4. ASSERT: Verify only checking accounts are returned
    assert len(checking_accounts) >= 1
    assert all(isinstance(a, CheckingAccount) for a in checking_accounts)
    assert all(a.account_type == "checking" for a in checking_accounts)

    # Verify the test account is in the results
    account_ids = [a.id for a in checking_accounts]
    assert test_checking_account.id in account_ids

    # Verify other account types are not in the results
    assert test_savings_account.id not in account_ids
    assert test_credit_account.id not in account_ids


@pytest.mark.asyncio
async def test_create_typed_entity_with_checking_type(
    account_repository: AccountRepository, db_session: AsyncSession
):
    """
    Test creating a typed checking account.

    This test verifies that the repository correctly creates a checking account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        account_repository: Base account repository
        db_session: Database session
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    account_schema = create_checking_account_schema(
        name="New Checking Account",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )

    # 3. ACT: Create the account
    result = await account_repository.create_typed_entity(
        "checking",
        account_schema.model_dump(),
        registry=account_type_registry,
    )

    # 4. ASSERT: Verify the account was created correctly
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id is not None
    assert result.name == "New Checking Account"
    assert result.account_type == "checking"
    assert result.current_balance == Decimal("1000.00")
    assert result.available_balance == Decimal("1000.00")
    assert result.has_overdraft_protection is True
    assert result.overdraft_limit == Decimal("500.00")

    # Verify it was actually persisted
    persisted = await account_repository.get(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_update_typed_entity_with_checking_type(
    account_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test updating a typed checking account.

    This test verifies that the repository correctly updates a checking account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        account_repository: Base account repository
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    update_schema = create_checking_account_update_schema(
        name="Updated Checking Account",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("250.00"),
        monthly_fee=Decimal("5.99"),
    )

    # 3. ACT: Update the account
    result = await account_repository.update_typed_entity(
        test_checking_account.id,
        "checking",
        update_schema.model_dump(),
        registry=account_type_registry,
    )

    # 4. ASSERT: Verify the account was updated correctly
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id == test_checking_account.id
    assert result.name == "Updated Checking Account"
    assert result.has_overdraft_protection is True
    assert result.overdraft_limit == Decimal("250.00")
    assert result.monthly_fee == Decimal("5.99")


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
    between_400_and_1000 = (
        await checking_repository.get_checking_accounts_by_balance_range(
            Decimal("400.00"), Decimal("1000.00")
        )
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
    international_accounts = (
        await checking_repository.get_checking_accounts_with_international_features()
    )

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
    checking_repository: AccountRepository,
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
    assert callable(
        getattr(checking_repository, "get_checking_accounts_with_overdraft")
    )

    assert hasattr(checking_repository, "get_checking_accounts_by_balance_range")
    assert callable(
        getattr(checking_repository, "get_checking_accounts_by_balance_range")
    )

    assert hasattr(
        checking_repository, "get_checking_accounts_with_international_features"
    )
    assert callable(
        getattr(
            checking_repository, "get_checking_accounts_with_international_features"
        )
    )

    assert hasattr(checking_repository, "get_checking_accounts_without_fees")
    assert callable(getattr(checking_repository, "get_checking_accounts_without_fees"))
