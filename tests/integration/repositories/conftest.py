from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Account, StatementHistory
from src.repositories.accounts import AccountRepository
from src.repositories.statement_history import StatementHistoryRepository
from tests.helpers.datetime_utils import utc_now
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.statement_history import \
    create_statement_history_schema


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def statement_history_repository(
    db_session: AsyncSession,
) -> StatementHistoryRepository:
    """Fixture for StatementHistoryRepository with test database session."""
    return StatementHistoryRepository(db_session)


@pytest_asyncio.fixture
async def test_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
) -> StatementHistory:
    """Create a test statement history entry for a credit account."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    statement_schema = create_statement_history_schema(
        account_id=test_credit_account.id,
        statement_date=utc_now() - timedelta(days=15),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=utc_now() + timedelta(days=15),
    )

    # Convert validated schema to dict for repository
    validated_data = statement_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await statement_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_accounts(
    account_repository: AccountRepository,
) -> List[Account]:
    """Create multiple test accounts of different types."""
    # 1. ARRANGE: No setup needed for this fixture

    # Create accounts of different types
    account_types = [
        ("Checking A", "checking", Decimal("1200.00")),
        ("Savings B", "savings", Decimal("5000.00")),
        ("Credit Card C", "credit", Decimal("-700.00")),
        (
            "Investment D",
            "savings",
            Decimal("10000.00"),
        ),  # Changed from "investment" to "savings"
    ]

    accounts = []
    for name, acc_type, balance in account_types:
        # 2. SCHEMA: Create and validate through Pydantic schema
        account_schema = create_account_schema(
            name=name,
            account_type=acc_type,
            available_balance=balance,
            total_limit=Decimal("3000.00") if acc_type == "credit" else None,
            available_credit=Decimal("2300.00") if acc_type == "credit" else None,
        )

        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        account = await account_repository.create(validated_data)
        accounts.append(account)

    return accounts
