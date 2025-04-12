"""
Integration tests for credit account repository advanced operations.

This module tests the specialized operations in the credit account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.repositories.accounts import AccountRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.account_types.banking.credit_schema_factories import (
    create_credit_account_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_credit_accounts_with_upcoming_payments(
    credit_repository: AccountRepository,
    test_credit_with_due_date: CreditAccount,
    test_credit_account: CreditAccount,
    db_session: AsyncSession,
):
    """
    Test getting credit accounts with payments due in the next X days.

    This test verifies that the specialized repository method correctly
    identifies credit accounts with upcoming payment due dates.

    Args:
        credit_repository: Credit account repository
        test_credit_with_due_date: Credit account with upcoming due date
        test_credit_account: Regular credit account
        db_session: Database session
    """
    # 1. ARRANGE: Ensure test_credit_account has a due date in the distant future
    far_future = utc_now() + timedelta(days=45)
    test_credit_account.statement_due_date = far_future
    await db_session.flush()

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Call the specialized repository method
    upcoming_payments = (
        await credit_repository.get_credit_accounts_with_upcoming_payments(days=20)
    )

    # 4. ASSERT: Verify the results
    assert len(upcoming_payments) >= 1

    # Verify account with upcoming due date is included
    account_ids = [a.id for a in upcoming_payments]
    assert test_credit_with_due_date.id in account_ids

    # Verify account with far future due date is excluded
    assert test_credit_account.id not in account_ids

    # All accounts should have due dates within the next 20 days
    now = utc_now()
    for account in upcoming_payments:
        assert account.statement_due_date is not None
        days_until_due = (account.statement_due_date - now).days
        assert 0 <= days_until_due <= 20


@pytest.mark.asyncio
async def test_get_credit_accounts_by_utilization(
    credit_repository: AccountRepository, db_session: AsyncSession
):
    """
    Test getting credit accounts by utilization range.

    This test verifies that the specialized repository method correctly
    filters credit accounts based on their credit utilization percentage.

    Args:
        credit_repository: Credit account repository
        db_session: Database session
    """
    # 1. ARRANGE: Create accounts with different utilization rates
    low_util_schema = create_credit_account_schema(
        name="Low Utilization",
        current_balance=Decimal("-500.00"),  # 10% utilization
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("5000.00"),
        available_credit=Decimal("4500.00"),
    )

    mid_util_schema = create_credit_account_schema(
        name="Mid Utilization",
        current_balance=Decimal("-3000.00"),  # 30% utilization
        available_balance=Decimal("-3000.00"),
        credit_limit=Decimal("10000.00"),
        available_credit=Decimal("7000.00"),
    )

    high_util_schema = create_credit_account_schema(
        name="High Utilization",
        current_balance=Decimal("-8000.00"),  # 80% utilization
        available_balance=Decimal("-8000.00"),
        credit_limit=Decimal("10000.00"),
        available_credit=Decimal("2000.00"),
    )

    low_util = CreditAccount(**low_util_schema.model_dump())
    mid_util = CreditAccount(**mid_util_schema.model_dump())
    high_util = CreditAccount(**high_util_schema.model_dump())

    db_session.add_all([low_util, mid_util, high_util])
    await db_session.flush()

    # 2. SCHEMA: Used for creating the test accounts

    # 3. ACT: Call the specialized repository method
    mid_range_accounts = await credit_repository.get_credit_accounts_by_utilization(
        min_percent=25, max_percent=60
    )

    # 4. ASSERT: Verify the results
    assert len(mid_range_accounts) >= 1

    # Verify correct accounts are included/excluded
    account_ids = [a.id for a in mid_range_accounts]
    assert mid_util.id in account_ids
    assert low_util.id not in account_ids
    assert high_util.id not in account_ids

    # All accounts should have utilization within the specified range
    for account in mid_range_accounts:
        utilization = abs(account.current_balance) / account.credit_limit * 100
        assert 25 <= utilization <= 60


@pytest.mark.asyncio
async def test_get_credit_accounts_by_statement_status(
    credit_repository: AccountRepository,
    test_credit_with_due_date: CreditAccount,
    db_session: AsyncSession,
):
    """
    Test getting credit accounts with or without open statements.

    This test verifies that the specialized repository methods correctly
    identify credit accounts based on their statement status.

    Args:
        credit_repository: Credit account repository
        test_credit_with_due_date: Credit account with statement
        db_session: Database session
    """
    # 1. ARRANGE: Create an account with no statement
    no_statement_schema = create_credit_account_schema(
        name="No Statement",
        current_balance=Decimal("-1500.00"),
        available_balance=Decimal("-1500.00"),
        credit_limit=Decimal("5000.00"),
        available_credit=Decimal("3500.00"),
    )

    # Modify the schema data to set statement fields to None
    no_statement_data = no_statement_schema.model_dump()
    no_statement_data["statement_balance"] = None
    no_statement_data["statement_due_date"] = None

    no_statement = CreditAccount(**no_statement_data)
    db_session.add(no_statement)
    await db_session.flush()

    # 2. SCHEMA: Used for creating the test account

    # 3. ACT: Call the specialized repository methods
    with_statement = await credit_repository.get_credit_accounts_with_open_statements()
    without_statement = await credit_repository.get_credit_accounts_without_statements()

    # 4. ASSERT: Verify the results for accounts with statements
    assert len(with_statement) >= 1
    with_ids = [a.id for a in with_statement]
    assert test_credit_with_due_date.id in with_ids
    assert no_statement.id not in with_ids

    # All accounts should have statement balance and due date
    for account in with_statement:
        assert account.statement_balance is not None
        assert account.statement_due_date is not None

    # Verify the results for accounts without statements
    assert len(without_statement) >= 1
    without_ids = [a.id for a in without_statement]
    assert no_statement.id in without_ids
    assert test_credit_with_due_date.id not in without_ids

    # All accounts should have no statement balance or due date
    for account in without_statement:
        assert account.statement_balance is None or account.statement_due_date is None


@pytest.mark.asyncio
async def test_get_credit_accounts_with_autopay(
    credit_repository: AccountRepository,
    test_credit_with_rewards: CreditAccount,
    db_session: AsyncSession,
):
    """
    Test getting credit accounts with autopay enabled.

    This test verifies that the specialized repository method correctly
    identifies credit accounts that have autopay enabled.

    Args:
        credit_repository: Credit account repository
        test_credit_with_rewards: Credit account with autopay
        db_session: Database session
    """
    # 1. ARRANGE: Create an account without autopay
    no_autopay_schema = create_credit_account_schema(
        name="No Autopay",
        current_balance=Decimal("-1000.00"),
        available_balance=Decimal("-1000.00"),
        credit_limit=Decimal("5000.00"),
        available_credit=Decimal("4000.00"),
    )

    # Modify the schema data to set autopay_status to "none"
    no_autopay_data = no_autopay_schema.model_dump()
    no_autopay_data["autopay_status"] = "none"

    no_autopay = CreditAccount(**no_autopay_data)
    db_session.add(no_autopay)
    await db_session.flush()

    # 2. SCHEMA: Used for creating the test account

    # 3. ACT: Call the specialized repository method
    with_autopay = await credit_repository.get_credit_accounts_with_autopay()

    # 4. ASSERT: Verify the results
    assert len(with_autopay) >= 1

    # Verify account with autopay is included
    account_ids = [a.id for a in with_autopay]
    assert test_credit_with_rewards.id in account_ids

    # Verify account without autopay is excluded
    assert no_autopay.id not in account_ids

    # All accounts should have autopay enabled (not 'none')
    for account in with_autopay:
        assert account.autopay_status is not None
        assert account.autopay_status != "none"


@pytest.mark.asyncio
async def test_repository_has_specialized_methods(credit_repository: AccountRepository):
    """
    Test that the repository has the specialized credit methods.

    This test verifies that the credit repository correctly includes
    all the specialized methods for credit account operations.

    Args:
        credit_repository: Credit account repository
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Verify the repository has specialized credit methods
    assert hasattr(credit_repository, "get_credit_accounts_with_upcoming_payments")
    assert callable(
        getattr(credit_repository, "get_credit_accounts_with_upcoming_payments")
    )

    assert hasattr(credit_repository, "get_credit_accounts_by_utilization")
    assert callable(getattr(credit_repository, "get_credit_accounts_by_utilization"))

    assert hasattr(credit_repository, "get_credit_accounts_with_open_statements")
    assert callable(
        getattr(credit_repository, "get_credit_accounts_with_open_statements")
    )

    assert hasattr(credit_repository, "get_credit_accounts_without_statements")
    assert callable(
        getattr(credit_repository, "get_credit_accounts_without_statements")
    )

    assert hasattr(credit_repository, "get_credit_accounts_with_autopay")
    assert callable(getattr(credit_repository, "get_credit_accounts_with_autopay"))
