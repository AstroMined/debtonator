"""
Integration tests for the AccountRepository.

This module contains tests for the AccountRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.accounts import AccountRepository
from src.repositories.statement_history import StatementHistoryRepository
from tests.helpers.datetime_utils import (
    utc_now, days_ago, days_from_now, datetime_equals, datetime_greater_than
)
from tests.helpers.schema_factories.accounts import (
    create_account_schema, create_account_update_schema)
from tests.helpers.schema_factories.statement_history import \
    create_statement_history_schema

pytestmark = pytest.mark.asyncio


async def test_get_by_name(
    account_repository: AccountRepository, test_checking_account: Account
):
    """Test getting an account by name."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get account by name
    result = await account_repository.get_by_name(test_checking_account.name)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_checking_account.id
    assert result.name == test_checking_account.name


async def test_get_with_statement_history(
    account_repository: AccountRepository,
    test_credit_account: Account,
    test_statement_history: StatementHistory,
):
    """Test getting an account with its statement history loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get account with statement history
    result = await account_repository.get_with_statement_history(test_credit_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_credit_account.id
    assert hasattr(result, "statement_history")
    assert len(result.statement_history) >= 1

    # Check that statement history is loaded correctly
    statement = result.statement_history[0]
    assert statement.account_id == test_credit_account.id


async def test_get_with_relationships(
    account_repository: AccountRepository,
    test_credit_account: Account,
    test_statement_history: StatementHistory,
):
    """Test getting an account with multiple relationships loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get account with specified relationships
    result = await account_repository.get_with_relationships(
        test_credit_account.id,
        include_statements=True,
        include_balance_history=True,
        include_credit_limit_history=True,
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_credit_account.id
    assert hasattr(result, "statement_history")
    assert hasattr(result, "balance_history")
    assert hasattr(result, "credit_limit_history")

    # Check that statement history is loaded correctly
    assert len(result.statement_history) >= 1
    statement = result.statement_history[0]
    assert statement.account_id == test_credit_account.id


async def test_get_accounts_with_statements(
    account_repository: AccountRepository,
    test_credit_account: Account,
    test_statement_history: StatementHistory,
):
    """Test getting accounts with statement history loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get all accounts with statements
    results = await account_repository.get_accounts_with_statements()

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1

    # Find our test credit account
    found_account = False
    for account in results:
        if account.id == test_credit_account.id:
            found_account = True
            assert hasattr(account, "statement_history")
            assert len(account.statement_history) >= 1
            break

    assert found_account, "Test credit account not found in results"


async def test_get_active_accounts(
    account_repository: AccountRepository,
    test_multiple_accounts: List[Account],
):
    """Test getting all active accounts."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get all active accounts
    results = await account_repository.get_active_accounts()

    # 3. ASSERT: Verify the operation results
    assert len(results) >= len(test_multiple_accounts)

    # Verify all test accounts are in the results
    test_account_ids = {account.id for account in test_multiple_accounts}
    result_account_ids = {account.id for account in results}
    assert test_account_ids.issubset(result_account_ids)


async def test_get_by_type(
    account_repository: AccountRepository,
    test_multiple_accounts: List[Account],
):
    """Test getting accounts by type."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get accounts by type (checking)
    results = await account_repository.get_by_type("checking")

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1
    for account in results:
        assert account.type == "checking"

    # Also test with credit type
    credit_results = await account_repository.get_by_type("credit")
    assert len(credit_results) >= 1
    for account in credit_results:
        assert account.type == "credit"


async def test_update_balance(
    account_repository: AccountRepository, test_checking_account: Account
):
    """Test updating an account balance."""
    # 1. ARRANGE: Setup is already done with fixtures
    original_balance = test_checking_account.available_balance
    amount_change = Decimal("250.00")

    # 2. ACT: Update the account balance
    result = await account_repository.update_balance(
        test_checking_account.id, amount_change
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_checking_account.id
    assert result.available_balance == original_balance + amount_change


async def test_update_balance_credit_account(
    account_repository: AccountRepository, test_credit_account: Account
):
    """Test updating a credit account balance which should update available credit."""
    # 1. ARRANGE: Setup is already done with fixtures
    original_balance = test_credit_account.available_balance
    original_credit = test_credit_account.available_credit
    amount_change = Decimal("-200.00")  # Increasing debt (more negative balance)

    # 2. ACT: Update the credit account balance
    result = await account_repository.update_balance(
        test_credit_account.id, amount_change
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_credit_account.id
    assert result.available_balance == original_balance + amount_change
    # For credit accounts, available credit should decrease when balance becomes more negative
    assert result.available_credit == original_credit - abs(amount_change)


async def test_update_statement_balance(
    account_repository: AccountRepository, test_credit_account: Account
):
    """Test updating an account's statement balance and date."""
    # 1. ARRANGE: Setup is already done with fixtures
    new_statement_balance = Decimal("750.00")
    statement_date = utc_now()

    # 2. ACT: Update statement balance and date
    result = await account_repository.update_statement_balance(
        test_credit_account.id, new_statement_balance, statement_date
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_credit_account.id
    assert result.last_statement_balance == new_statement_balance
    
    # Use proper timezone-aware comparison for dates
    assert datetime_equals(result.last_statement_date, statement_date, ignore_microseconds=True)


async def test_find_accounts_with_low_balance(
    account_repository: AccountRepository,
    test_multiple_accounts: List[Account],
):
    """Test finding accounts with balance below threshold."""
    # 1. ARRANGE: Setup is already done with fixtures
    threshold = Decimal("1500.00")

    # 2. ACT: Find accounts with low balance
    results = await account_repository.find_accounts_with_low_balance(threshold)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should find checking and credit accounts
    for account in results:
        assert account.available_balance < threshold


async def test_find_credit_accounts_near_limit(
    account_repository: AccountRepository, test_credit_account: Account
):
    """Test finding credit accounts near their credit limit."""
    # 1. ARRANGE: Setup is already done with fixtures
    # First update the credit account to be closer to limit
    update_data = {
        "available_balance": Decimal("-1800.00"),  # Close to total_limit of 2000
        "available_credit": Decimal("200.00"),
    }
    await account_repository.update(test_credit_account.id, update_data)

    # 2. ACT: Find credit accounts near limit (90% by default)
    results = await account_repository.find_credit_accounts_near_limit()

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1

    # Verify our test account is in the results
    found_account = False
    for account in results:
        if account.id == test_credit_account.id:
            found_account = True
            # Verify it's actually near limit
            assert account.type == "credit"
            assert account.total_limit is not None
            assert account.available_credit is not None
            assert account.available_credit < (account.total_limit * Decimal("0.1"))
            break

    assert found_account, "Test credit account not found in near-limit accounts"


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema."""
    # Try creating a schema with invalid data
    try:
        invalid_schema = create_account_schema(
            name="",  # Invalid empty name
            account_type="invalid_type",  # Invalid account type
            available_balance=None,  # Missing required field
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert (
            "name" in error_str
            or "type" in error_str
            or "available_balance" in error_str
        )
