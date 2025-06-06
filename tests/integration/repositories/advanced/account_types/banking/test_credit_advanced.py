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
from src.services.accounts import AccountService
from src.utils.datetime_utils import ensure_utc, utc_now
from tests.helpers.schema_factories.account_types.banking.credit_schema_factories import (
    create_credit_account_schema,
    create_credit_account_update_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_with_type_returns_credit_account(
    repository: AccountRepository, test_credit_account: CreditAccount
):
    """
    Test that get_with_type returns a CreditAccount instance.

    This test verifies that the repository correctly retrieves a credit account
    with the appropriate polymorphic identity.

    Args:
        repository: Base account repository
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the account with type information
    result = await repository.get_with_type(test_credit_account.id)

    # 4. ASSERT: Verify the result is a credit account
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id == test_credit_account.id
    assert result.name == test_credit_account.name
    assert result.account_type == "credit"

    # Verify credit-specific fields are loaded
    assert hasattr(result, "credit_limit")
    if hasattr(test_credit_account, "apr"):
        assert result.apr == test_credit_account.apr


@pytest.mark.asyncio
async def test_get_by_type_returns_only_credit_accounts(
    repository: AccountRepository,
    test_credit_account: CreditAccount,
    test_checking_account,
    test_savings_account,
):
    """
    Test that get_by_type returns only credit accounts.

    This test verifies that the repository correctly filters accounts by type
    when retrieving credit accounts.

    Args:
        repository: Base account repository
        test_credit_account: Credit account fixture
        test_checking_account: Checking account fixture
        test_savings_account: Savings account fixture
    """
    # 1. ARRANGE: Repository and test accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve accounts by type
    credit_accounts = await repository.get_by_type("credit")

    # 4. ASSERT: Verify only credit accounts are returned
    assert len(credit_accounts) >= 1
    assert all(isinstance(a, CreditAccount) for a in credit_accounts)
    assert all(a.account_type == "credit" for a in credit_accounts)

    # Verify the test account is in the results
    account_ids = [a.id for a in credit_accounts]
    assert test_credit_account.id in account_ids

    # Verify other account types are not in the results
    assert test_checking_account.id not in account_ids
    assert test_savings_account.id not in account_ids


@pytest.mark.asyncio
async def test_create_typed_entity_with_credit_type(
    repository: AccountRepository,
    account_service: AccountService,
    db_session: AsyncSession,
):
    """
    Test creating a typed credit account using service for business logic.

    This test verifies that the repository correctly creates a credit account
    with the service calculating the business logic values, following ADR-012.

    Args:
        repository: Base account repository
        account_service: Account service for business logic
        db_session: Database session
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    account_schema = create_credit_account_schema(
        name="New Credit Account",
        current_balance=Decimal("-500.00"),
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("3000.00"),
        available_credit=Decimal("2500.00"),
        apr=Decimal("15.99"),
    )

    # 3. ACT: Create the account
    result = await repository.create_typed_entity("credit", account_schema.model_dump())

    # 4. ASSERT: Verify the account was created correctly
    assert result is not None
    assert isinstance(result, CreditAccount)

    # Calculate available credit using the service (business logic) per ADR-012
    available_credit = await account_service.get_available_credit_amount(result)
    assert available_credit == Decimal("2500.00")

    # Verify other properties
    assert result.id is not None
    assert result.name == "New Credit Account"
    assert result.account_type == "credit"
    assert result.current_balance == Decimal("-500.00")
    assert result.available_balance == Decimal("-500.00")
    assert result.credit_limit == Decimal("3000.00")
    assert result.apr == Decimal("15.99")

    # Verify it was actually persisted
    persisted = await repository.get(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_update_typed_entity_with_credit_type(
    repository: AccountRepository,
    account_service: AccountService,
    test_credit_account: CreditAccount,
):
    """
    Test updating a typed credit account.

    This test verifies that the repository correctly updates a credit account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        repository: Base account repository
        account_service: Account service for business logic
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    update_schema = create_credit_account_update_schema(
        name="Updated Credit Account",
        apr=Decimal("14.99"),
        rewards_program="Travel Points",
        autopay_status="minimum",
    )

    # 3. ACT: Update the account
    result = await repository.update_typed_entity(
        test_credit_account.id, "credit", update_schema.model_dump()
    )

    # 4. ASSERT: Verify the account was updated correctly
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id == test_credit_account.id
    assert result.name == "Updated Credit Account"
    assert result.apr == Decimal("14.99")
    assert result.rewards_program == "Travel Points"
    assert result.autopay_status == "minimum"


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
        # Use ensure_utc to add timezone info for the database datetime
        statement_due_date = ensure_utc(account.statement_due_date)
        days_until_due = (statement_due_date - now).days
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

    # Filter out 'total_limit' which was removed from the model
    low_util_data = {
        k: v for k, v in low_util_schema.model_dump().items() if k != "total_limit"
    }
    mid_util_data = {
        k: v for k, v in mid_util_schema.model_dump().items() if k != "total_limit"
    }
    high_util_data = {
        k: v for k, v in high_util_schema.model_dump().items() if k != "total_limit"
    }

    low_util = CreditAccount(**low_util_data)
    mid_util = CreditAccount(**mid_util_data)
    high_util = CreditAccount(**high_util_data)

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

    # Remove total_limit which was removed from the model
    if "total_limit" in no_statement_data:
        del no_statement_data["total_limit"]

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

    # Remove total_limit which was removed from the model
    if "total_limit" in no_autopay_data:
        del no_autopay_data["total_limit"]

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
