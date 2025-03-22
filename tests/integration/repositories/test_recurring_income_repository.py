"""
Integration tests for the RecurringIncomeRepository.

This module contains tests for the RecurringIncomeRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
RecurringIncomeRepository, ensuring proper validation flow and relationship
loading.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.recurring_income import RecurringIncome
from src.repositories.accounts import AccountRepository
from src.repositories.recurring_income import RecurringIncomeRepository

# Import schema and schema factories - essential part of the validation pattern
from src.schemas.income import RecurringIncomeCreate, RecurringIncomeUpdate
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.recurring_income import (
    create_recurring_income_schema,
    create_recurring_income_update_schema,
)


@pytest_asyncio.fixture
async def recurring_income_repository(db_session: AsyncSession) -> RecurringIncomeRepository:
    """Fixture for RecurringIncomeRepository with test database session."""
    return RecurringIncomeRepository(db_session)


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def test_account(account_repository: AccountRepository) -> Account:
    """Fixture to create a test account for recurring income."""
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
async def test_secondary_account(account_repository: AccountRepository) -> Account:
    """Fixture to create a second test account for recurring income."""
    # Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Secondary Account",
        account_type="savings",
        available_balance=Decimal("500.00"),
    )
    
    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()
    
    # Create account through repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_recurring_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_account: Account
) -> RecurringIncome:
    """Fixture to create a test recurring income."""
    # Create and validate through Pydantic schema
    income_schema = create_recurring_income_schema(
        source="Monthly Salary",
        amount=Decimal("2000.00"),
        day_of_month=15,
        account_id=test_account.id,
        auto_deposit=True,
    )
    
    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()
    
    # Create recurring income through repository
    return await recurring_income_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_recurring_incomes(
    recurring_income_repository: RecurringIncomeRepository,
    test_account: Account,
    test_secondary_account: Account,
) -> List[RecurringIncome]:
    """Fixture to create multiple recurring income entries for testing."""
    # Create multiple recurring income entries with various attributes
    income_data = [
        {
            "source": "Monthly Salary",
            "amount": Decimal("3000.00"),
            "day_of_month": 15,
            "account_id": test_account.id,
            "auto_deposit": True,
            "active": True,
        },
        {
            "source": "Freelance Work",
            "amount": Decimal("500.00"),
            "day_of_month": 1,
            "account_id": test_account.id,
            "auto_deposit": False,
            "active": True,
        },
        {
            "source": "Rental Income",
            "amount": Decimal("1200.00"),
            "day_of_month": 5,
            "account_id": test_secondary_account.id,
            "auto_deposit": True,
            "active": True,
        },
        {
            "source": "Dividend Payments",
            "amount": Decimal("250.00"),
            "day_of_month": 20,
            "account_id": test_secondary_account.id,
            "auto_deposit": False,
            "active": False,  # Inactive income
        },
    ]
    
    # Create the recurring income entries using the repository
    created_incomes = []
    for data in income_data:
        # Create and validate through Pydantic schema
        income_schema = create_recurring_income_schema(**data)
        
        # Convert validated schema to dict for repository
        validated_data = income_schema.model_dump()
        
        # Create recurring income through repository
        income = await recurring_income_repository.create(validated_data)
        created_incomes.append(income)
        
    return created_incomes


class TestRecurringIncomeRepository:
    """
    Tests for the RecurringIncomeRepository.
    
    These tests follow the standard Arrange-Schema-Act-Assert pattern for
    repository testing, simulating proper service-to-repository validation flow.
    """
    
    @pytest.mark.asyncio
    async def test_create_recurring_income(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_account: Account,
    ):
        """Test creating a recurring income with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. SCHEMA: Create and validate through Pydantic schema
        income_schema = create_recurring_income_schema(
            source="Side Gig Income",
            amount=Decimal("750.00"),
            day_of_month=10,
            account_id=test_account.id,
            auto_deposit=False,
        )
        
        # Convert validated schema to dict for repository
        validated_data = income_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        result = await recurring_income_repository.create(validated_data)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.source == "Side Gig Income"
        assert result.amount == Decimal("750.00")
        assert result.day_of_month == 10
        assert result.account_id == test_account.id
        assert result.auto_deposit is False
        assert result.active is True  # Default value
        assert result.created_at is not None
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_get_recurring_income(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test retrieving a recurring income by ID."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get the recurring income
        result = await recurring_income_repository.get(test_recurring_income.id)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.source == test_recurring_income.source
        assert result.amount == test_recurring_income.amount
        assert result.day_of_month == test_recurring_income.day_of_month
        assert result.account_id == test_recurring_income.account_id
        assert result.auto_deposit == test_recurring_income.auto_deposit
        assert result.active == test_recurring_income.active
    
    @pytest.mark.asyncio
    async def test_update_recurring_income(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test updating a recurring income with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. SCHEMA: Create and validate update data through Pydantic schema
        update_schema = create_recurring_income_update_schema(
            source="Updated Salary",
            amount=Decimal("2500.00"),
            auto_deposit=False,
        )
        
        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        result = await recurring_income_repository.update(
            test_recurring_income.id, update_data
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.source == "Updated Salary"
        assert result.amount == Decimal("2500.00")
        assert result.auto_deposit is False
        assert result.day_of_month == test_recurring_income.day_of_month  # Unchanged
        assert result.account_id == test_recurring_income.account_id  # Unchanged
        assert result.updated_at > test_recurring_income.updated_at
    
    @pytest.mark.asyncio
    async def test_delete_recurring_income(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test deleting a recurring income."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Delete the recurring income
        result = await recurring_income_repository.delete(test_recurring_income.id)
        
        # 4. ASSERT: Verify the operation results
        assert result is True
        
        # Verify it's actually deleted
        deleted_income = await recurring_income_repository.get(test_recurring_income.id)
        assert deleted_income is None
    
    @pytest.mark.asyncio
    async def test_get_by_source(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test getting recurring income by source name."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get recurring income by source
        results = await recurring_income_repository.get_by_source("Salary")
        
        # 4. ASSERT: Verify the operation results
        assert len(results) >= 1  # Should get at least 1 income with "Salary" in source
        for income in results:
            assert "salary" in income.source.lower()
    
    @pytest.mark.asyncio
    async def test_get_by_account(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_account: Account,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test getting recurring income for a specific account."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get recurring income for the account
        results = await recurring_income_repository.get_by_account(test_account.id)
        
        # 4. ASSERT: Verify the operation results
        assert len(results) >= 2  # Should get at least 2 incomes for this account
        for income in results:
            assert income.account_id == test_account.id
            # Relationship should be loaded
            assert income.account is not None
            assert income.account.id == test_account.id
    
    @pytest.mark.asyncio
    async def test_get_active_income(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test getting active recurring income records."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get active recurring income
        results = await recurring_income_repository.get_active_income()
        
        # 4. ASSERT: Verify the operation results
        assert len(results) >= 3  # Should get at least 3 active incomes
        for income in results:
            assert income.active is True
            # Relationship should be loaded
            assert income.account is not None
    
    @pytest.mark.asyncio
    async def test_get_by_day_of_month(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test getting recurring income for a specific day of the month."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get recurring income for day 15
        results = await recurring_income_repository.get_by_day_of_month(15)
        
        # 4. ASSERT: Verify the operation results
        assert len(results) >= 1  # Should get at least 1 income for day 15
        for income in results:
            assert income.day_of_month == 15
            # Relationship should be loaded
            assert income.account is not None
    
    @pytest.mark.asyncio
    async def test_get_with_income_entries(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test getting a recurring income with its income entries."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get the recurring income with income entries
        result = await recurring_income_repository.get_with_income_entries(
            test_recurring_income.id
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert hasattr(result, "income_entries")
        # May be empty list if no income entries have been created yet
    
    @pytest.mark.asyncio
    async def test_get_with_account(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test getting a recurring income with its account."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get the recurring income with account
        result = await recurring_income_repository.get_with_account(
            test_recurring_income.id
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.account is not None
        assert result.account.id == test_recurring_income.account_id
        assert result.account.name is not None
    
    @pytest.mark.asyncio
    async def test_get_with_relationships(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test getting a recurring income with all relationships loaded."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get the recurring income with relationships
        result = await recurring_income_repository.get_with_relationships(
            test_recurring_income.id
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.account is not None
        assert result.account.id == test_recurring_income.account_id
        assert hasattr(result, "income_entries")
        # Category might be None if not set
    
    @pytest.mark.asyncio
    async def test_toggle_active(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test toggling the active status of a recurring income."""
        # 1. ARRANGE: Get current status
        initial_active = test_recurring_income.active
        
        # 2. SCHEMA: Not needed for this method as it uses ID only
        
        # 3. ACT: Toggle active status
        result = await recurring_income_repository.toggle_active(
            test_recurring_income.id
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.active is not initial_active  # Should be toggled
        
        # Toggle back to verify
        result = await recurring_income_repository.toggle_active(
            test_recurring_income.id
        )
        assert result.active is initial_active  # Should be back to original
    
    @pytest.mark.asyncio
    async def test_toggle_auto_deposit(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test toggling the auto_deposit status of a recurring income."""
        # 1. ARRANGE: Get current status
        initial_auto_deposit = test_recurring_income.auto_deposit
        
        # 2. SCHEMA: Not needed for this method as it uses ID only
        
        # 3. ACT: Toggle auto_deposit status
        result = await recurring_income_repository.toggle_auto_deposit(
            test_recurring_income.id
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.auto_deposit is not initial_auto_deposit  # Should be toggled
        
        # Toggle back to verify
        result = await recurring_income_repository.toggle_auto_deposit(
            test_recurring_income.id
        )
        assert result.auto_deposit is initial_auto_deposit  # Should be back to original
    
    @pytest.mark.asyncio
    async def test_update_day_of_month(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_recurring_income: RecurringIncome,
    ):
        """Test updating the day_of_month for a recurring income."""
        # 1. ARRANGE: Choose a new day
        new_day = 25 if test_recurring_income.day_of_month != 25 else 20
        
        # 2. SCHEMA: Not needed for this method as it uses ID and int only
        
        # 3. ACT: Update day_of_month
        result = await recurring_income_repository.update_day_of_month(
            test_recurring_income.id, new_day
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_recurring_income.id
        assert result.day_of_month == new_day
    
    @pytest.mark.asyncio
    async def test_get_monthly_total(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_account: Account,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test calculating the total monthly amount of recurring income."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get monthly total for account
        total = await recurring_income_repository.get_monthly_total(test_account.id)
        
        # 4. ASSERT: Verify the operation results
        assert total > 0
        
        # Calculate expected total manually for verification
        expected_total = sum(
            income.amount
            for income in test_multiple_recurring_incomes
            if income.account_id == test_account.id and income.active
        )
        assert total == expected_total
    
    @pytest.mark.asyncio
    async def test_get_upcoming_deposits(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test getting estimated upcoming deposits."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get upcoming deposits for next 30 days
        results = await recurring_income_repository.get_upcoming_deposits(days=30)
        
        # 4. ASSERT: Verify the operation results
        assert len(results) >= 3  # Should get at least 3 upcoming deposits (active incomes)
        
        # First deposit projection should have expected fields
        first_deposit = results[0]
        assert "source" in first_deposit
        assert "amount" in first_deposit
        assert "projected_date" in first_deposit
        assert "account_id" in first_deposit
        assert "recurring_id" in first_deposit
        
        # Verify projected dates are in the future
        today = datetime.now()
        for deposit in results:
            assert deposit["projected_date"] >= today
    
    @pytest.mark.asyncio
    async def test_find_by_pattern(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test finding recurring income by pattern in source name."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Find recurring income by pattern
        results = await recurring_income_repository.find_by_pattern("free")
        
        # 4. ASSERT: Verify the operation results
        assert len(results) >= 1  # Should get at least 1 income with "free" in source
        for income in results:
            assert "free" in income.source.lower()
            # Relationship should be loaded
            assert income.account is not None
    
    @pytest.mark.asyncio
    async def test_get_total_by_source(
        self,
        recurring_income_repository: RecurringIncomeRepository,
        test_multiple_recurring_incomes: List[RecurringIncome],
    ):
        """Test calculating total amount for recurring incomes by source pattern."""
        # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
        
        # 3. ACT: Get total by source pattern
        total = await recurring_income_repository.get_total_by_source("salary")
        
        # 4. ASSERT: Verify the operation results
        assert total > 0
        
        # Calculate expected total manually for verification
        expected_total = sum(
            income.amount
            for income in test_multiple_recurring_incomes
            if "salary" in income.source.lower() and income.active
        )
        assert total == expected_total
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(
        self,
        test_account: Account,
    ):
        """Test handling invalid data that would normally be caught by schema validation."""
        # Try creating a schema with invalid data and expect it to fail validation
        try:
            invalid_schema = RecurringIncomeCreate(
                source="Invalid Income",
                amount=Decimal("-50.00"),  # Invalid negative amount
                day_of_month=15,
                account_id=test_account.id,
                auto_deposit=False,
            )
            assert False, "Schema should have raised a validation error for negative amount"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            assert "amount" in str(e).lower() and "greater than" in str(e).lower()
        
        # Try with invalid day_of_month
        try:
            invalid_schema = RecurringIncomeCreate(
                source="Invalid Income",
                amount=Decimal("50.00"),
                day_of_month=32,  # Invalid day
                account_id=test_account.id,
                auto_deposit=False,
            )
            assert False, "Schema should have raised a validation error for invalid day"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            assert "day_of_month" in str(e).lower()
