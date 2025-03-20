"""
Integration tests for the TransactionHistoryRepository.

This module contains tests for the TransactionHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.accounts import AccountRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.transaction_history import (
    TransactionHistoryCreate,
    TransactionHistoryUpdate,
)
from tests.helpers.schema_factories import (
    create_account_schema,
    create_transaction_history_schema,
)


@pytest_asyncio.fixture
async def transaction_history_repository(
    db_session: AsyncSession,
) -> TransactionHistoryRepository:
    """Fixture for TransactionHistoryRepository with test database session."""
    return TransactionHistoryRepository(db_session)


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def test_account(account_repository: AccountRepository) -> Account:
    """Create a test account for use in tests."""
    # Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Checking Account",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # Create account through repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_transaction_history(
    transaction_history_repository: TransactionHistoryRepository, test_account: Account
) -> TransactionHistory:
    """Create a test transaction history entry for use in tests."""
    # Create and validate through Pydantic schema
    transaction_schema = create_transaction_history_schema(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        description="Initial deposit",
    )

    # Convert validated schema to dict for repository
    validated_data = transaction_schema.model_dump()

    # Create transaction entry through repository
    return await transaction_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_transactions(
    transaction_history_repository: TransactionHistoryRepository, test_account: Account
) -> List[TransactionHistory]:
    """Create multiple transaction history entries for testing."""
    now = datetime.utcnow()

    # Transaction data with mixed types and amounts
    transaction_data = [
        {
            "amount": Decimal("500.00"),
            "transaction_type": TransactionType.CREDIT,
            "description": "Salary deposit",
            "days_ago": 30,
        },
        {
            "amount": Decimal("75.50"),
            "transaction_type": TransactionType.DEBIT,
            "description": "Grocery shopping",
            "days_ago": 25,
        },
        {
            "amount": Decimal("120.00"),
            "transaction_type": TransactionType.DEBIT,
            "description": "Electricity bill",
            "days_ago": 20,
        },
        {
            "amount": Decimal("200.00"),
            "transaction_type": TransactionType.CREDIT,
            "description": "Refund",
            "days_ago": 15,
        },
        {
            "amount": Decimal("35.00"),
            "transaction_type": TransactionType.DEBIT,
            "description": "Gas",
            "days_ago": 10,
        },
        {
            "amount": Decimal("50.00"),
            "transaction_type": TransactionType.DEBIT,
            "description": "Dinner",
            "days_ago": 5,
        },
        {
            "amount": Decimal("250.00"),
            "transaction_type": TransactionType.CREDIT,
            "description": "Side job income",
            "days_ago": 2,
        },
    ]

    # Create the transactions
    created_transactions = []
    for data in transaction_data:
        schema = create_transaction_history_schema(
            account_id=test_account.id,
            amount=data["amount"],
            transaction_type=data["transaction_type"],
            description=data["description"],
            transaction_date=now - timedelta(days=data["days_ago"]),
        )

        transaction = await transaction_history_repository.create(schema.model_dump())
        created_transactions.append(transaction)

    return created_transactions


class TestTransactionHistoryRepository:
    """
    Tests for the TransactionHistoryRepository.

    These tests follow the standard 4-step pattern (Arrange-Schema-Act-Assert)
    for repository testing, simulating proper service-to-repository validation flow.
    """

    @pytest.mark.asyncio
    async def test_create_transaction_history(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
    ):
        """Test creating a transaction history entry with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. SCHEMA: Create and validate through Pydantic schema
        transaction_schema = create_transaction_history_schema(
            account_id=test_account.id,
            amount=Decimal("150.00"),
            transaction_type=TransactionType.DEBIT,
            description="Test purchase",
        )

        # Convert validated schema to dict for repository
        validated_data = transaction_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        result = await transaction_history_repository.create(validated_data)

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.account_id == test_account.id
        assert result.amount == Decimal("150.00")
        assert result.transaction_type == TransactionType.DEBIT
        assert result.description == "Test purchase"
        assert result.transaction_date is not None

    @pytest.mark.asyncio
    async def test_get_transaction_history(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_transaction_history: TransactionHistory,
    ):
        """Test retrieving a transaction history entry by ID."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get the transaction entry
        result = await transaction_history_repository.get(test_transaction_history.id)

        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_transaction_history.id
        assert result.account_id == test_transaction_history.account_id
        assert result.amount == test_transaction_history.amount
        assert result.transaction_type == test_transaction_history.transaction_type
        assert result.description == test_transaction_history.description

    @pytest.mark.asyncio
    async def test_update_transaction_history(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_transaction_history: TransactionHistory,
    ):
        """Test updating a transaction history entry with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. SCHEMA: Create and validate update data through Pydantic schema
        update_schema = TransactionHistoryUpdate(
            id=test_transaction_history.id,
            amount=Decimal("125.00"),
            description="Updated transaction description",
        )

        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump(exclude={"id"})

        # 3. ACT: Pass validated data to repository
        result = await transaction_history_repository.update(
            test_transaction_history.id, update_data
        )

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_transaction_history.id
        assert result.amount == Decimal("125.00")
        assert result.description == "Updated transaction description"
        assert (
            result.transaction_type == test_transaction_history.transaction_type
        )  # Unchanged
        assert result.updated_at > test_transaction_history.updated_at

    @pytest.mark.asyncio
    async def test_get_by_account(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test getting transaction history entries for an account."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get transaction entries for the account
        results = await transaction_history_repository.get_by_account(test_account.id)

        # 3. ASSERT: Verify the operation results
        assert len(results) >= 7  # At least 7 entries from fixture
        for entry in results:
            assert entry.account_id == test_account.id

    @pytest.mark.asyncio
    async def test_get_with_account(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_transaction_history: TransactionHistory,
    ):
        """Test getting a transaction history entry with account relationship loaded."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get the transaction entry with account
        result = await transaction_history_repository.get_with_account(
            test_transaction_history.id
        )

        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_transaction_history.id
        assert result.account is not None
        assert result.account.id == test_transaction_history.account_id

    @pytest.mark.asyncio
    async def test_get_by_date_range(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test getting transaction history entries within a date range."""
        # 1. ARRANGE: Setup is already done with fixtures
        now = datetime.utcnow()
        start_date = now - timedelta(days=22)
        end_date = now - timedelta(days=8)

        # 2. ACT: Get transaction entries within date range
        results = await transaction_history_repository.get_by_date_range(
            test_account.id, start_date, end_date
        )

        # 3. ASSERT: Verify the operation results
        assert len(results) >= 3  # Should get at least 3 entries in this range
        for entry in results:
            assert entry.account_id == test_account.id
            assert entry.transaction_date >= start_date
            assert entry.transaction_date <= end_date

    @pytest.mark.asyncio
    async def test_get_by_type(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test getting transaction history entries by type."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get credit transactions
        credit_results = await transaction_history_repository.get_by_type(
            test_account.id, TransactionType.CREDIT
        )

        # Get debit transactions
        debit_results = await transaction_history_repository.get_by_type(
            test_account.id, TransactionType.DEBIT
        )

        # 3. ASSERT: Verify the operation results
        assert len(credit_results) >= 3  # At least 3 credit transactions in fixture
        for entry in credit_results:
            assert entry.account_id == test_account.id
            assert entry.transaction_type == TransactionType.CREDIT

        assert len(debit_results) >= 4  # At least 4 debit transactions in fixture
        for entry in debit_results:
            assert entry.account_id == test_account.id
            assert entry.transaction_type == TransactionType.DEBIT

    @pytest.mark.asyncio
    async def test_search_by_description(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test searching transaction history entries by description."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Search for transactions with 'deposit' in description
        results = await transaction_history_repository.search_by_description(
            test_account.id, "deposit"
        )

        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1  # At least 1 transaction has 'deposit' in description
        for entry in results:
            assert entry.account_id == test_account.id
            assert "deposit" in entry.description.lower()

    @pytest.mark.asyncio
    async def test_get_total_by_type(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test calculating total amount for transactions of a specific type."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get total credit amount
        credit_total = await transaction_history_repository.get_total_by_type(
            test_account.id, TransactionType.CREDIT
        )

        # Get total debit amount
        debit_total = await transaction_history_repository.get_total_by_type(
            test_account.id, TransactionType.DEBIT
        )

        # 3. ASSERT: Verify the operation results
        assert credit_total >= Decimal(
            "950.00"
        )  # Sum of credit transactions in fixture
        assert debit_total >= Decimal("280.50")  # Sum of debit transactions in fixture

    @pytest.mark.asyncio
    async def test_get_transaction_count(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test counting transactions by type."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get transaction counts by type
        counts = await transaction_history_repository.get_transaction_count(
            test_account.id
        )

        # 3. ASSERT: Verify the operation results
        assert TransactionType.CREDIT.value in counts
        assert TransactionType.DEBIT.value in counts
        assert (
            counts[TransactionType.CREDIT.value] >= 3
        )  # At least 3 credit transactions in fixture
        assert (
            counts[TransactionType.DEBIT.value] >= 4
        )  # At least 4 debit transactions in fixture

    @pytest.mark.asyncio
    async def test_get_net_change(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test calculating net change in account balance from transactions."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get net change
        net_change = await transaction_history_repository.get_net_change(
            test_account.id
        )

        # 3. ASSERT: Verify the operation results
        # Net change should be credits - debits (950.00 - 280.50 = 669.50)
        assert net_change >= Decimal("650.00")

    @pytest.mark.asyncio
    async def test_get_monthly_totals(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
        test_multiple_transactions: List[TransactionHistory],
    ):
        """Test getting monthly transaction totals."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get monthly totals
        monthly_totals = await transaction_history_repository.get_monthly_totals(
            test_account.id, months=2
        )

        # 3. ASSERT: Verify the operation results
        assert len(monthly_totals) >= 1  # At least 1 month of data

        for month_data in monthly_totals:
            assert "month" in month_data
            assert "credits" in month_data
            assert "debits" in month_data
            assert "net" in month_data
            assert month_data["net"] == month_data["credits"] - month_data["debits"]

    @pytest.mark.asyncio
    async def test_get_transaction_patterns(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
    ):
        """Test identifying recurring transaction patterns."""
        # 1. ARRANGE: Create recurring transactions with same description
        now = datetime.utcnow()

        # Create several grocery transactions weekly
        for week in range(1, 5):
            schema = create_transaction_history_schema(
                account_id=test_account.id,
                amount=Decimal("75.00"),
                transaction_type=TransactionType.DEBIT,
                description="Weekly Grocery Shopping",
                transaction_date=now - timedelta(days=week * 7),
            )
            await transaction_history_repository.create(schema.model_dump())

        # Create monthly bill payments
        for month in range(1, 3):
            schema = create_transaction_history_schema(
                account_id=test_account.id,
                amount=Decimal("120.00"),
                transaction_type=TransactionType.DEBIT,
                description="Monthly Internet Bill",
                transaction_date=now - timedelta(days=month * 30),
            )
            await transaction_history_repository.create(schema.model_dump())

        # 2. ACT: Analyze transaction patterns
        patterns = await transaction_history_repository.get_transaction_patterns(
            test_account.id
        )

        # 3. ASSERT: Verify the operation results
        assert len(patterns) >= 2  # At least 2 patterns (grocery and internet)

        has_grocery_pattern = False
        has_bill_pattern = False

        for pattern in patterns:
            if "grocery" in pattern["description"].lower():
                has_grocery_pattern = True
                assert pattern["count"] >= 4
                if "pattern_type" in pattern:
                    assert "weekly" in pattern["pattern_type"].lower()

            if "internet" in pattern["description"].lower():
                has_bill_pattern = True
                assert pattern["count"] >= 2
                if "pattern_type" in pattern:
                    assert "month" in pattern["pattern_type"].lower()

        assert has_grocery_pattern
        assert has_bill_pattern

    @pytest.mark.asyncio
    async def test_bulk_create_transactions(
        self,
        transaction_history_repository: TransactionHistoryRepository,
        test_account: Account,
    ):
        """Test creating multiple transactions in bulk."""
        # 1. ARRANGE: Prepare multiple transaction schemas
        now = datetime.utcnow()

        transaction_schemas = [
            create_transaction_history_schema(
                account_id=test_account.id,
                amount=Decimal("25.00"),
                transaction_type=TransactionType.DEBIT,
                description="Coffee shop",
                transaction_date=now - timedelta(days=1),
            ),
            create_transaction_history_schema(
                account_id=test_account.id,
                amount=Decimal("45.00"),
                transaction_type=TransactionType.DEBIT,
                description="Restaurant",
                transaction_date=now - timedelta(days=2),
            ),
            create_transaction_history_schema(
                account_id=test_account.id,
                amount=Decimal("60.00"),
                transaction_type=TransactionType.DEBIT,
                description="Gas station",
                transaction_date=now - timedelta(days=3),
            ),
        ]

        # Convert schemas to dicts
        transaction_data = [schema.model_dump() for schema in transaction_schemas]

        # 2. ACT: Bulk create transactions
        results = await transaction_history_repository.bulk_create_transactions(
            test_account.id, transaction_data
        )

        # 3. ASSERT: Verify the operation results
        assert len(results) == 3
        assert all(tx.account_id == test_account.id for tx in results)
        assert any(tx.description == "Coffee shop" for tx in results)
        assert any(tx.description == "Restaurant" for tx in results)
        assert any(tx.description == "Gas station" for tx in results)

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test handling of validation errors that would be caught by the Pydantic schema."""
        # Try creating a schema with invalid data
        try:
            invalid_schema = TransactionHistoryCreate(
                account_id=999,
                amount=Decimal("-10.00"),  # Negative amount
                transaction_type=TransactionType.CREDIT,
                transaction_date=datetime.utcnow(),
            )
            assert (
                False
            ), "Schema should have raised a validation error for negative amount"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            assert "amount" in str(e).lower()
