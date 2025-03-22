"""
Integration tests for the LiabilityRepository.

This module contains tests for the LiabilityRepository using the
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
from src.models.categories import Category
from src.models.liabilities import Liability, LiabilityStatus
from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.schemas.liabilities import (
    LiabilityCreate,
    LiabilityUpdate,
)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema


@pytest_asyncio.fixture
async def liability_repository(db_session: AsyncSession) -> LiabilityRepository:
    """Fixture for LiabilityRepository with test database session."""
    return LiabilityRepository(db_session)


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def category_repository(db_session: AsyncSession) -> CategoryRepository:
    """Fixture for CategoryRepository with test database session."""
    return CategoryRepository(db_session)


@pytest_asyncio.fixture
async def test_account(account_repository: AccountRepository) -> Account:
    """Create a test account for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Checking Account",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    
    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_category(category_repository: CategoryRepository) -> Category:
    """Create a test category for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    category_schema = create_category_schema(
        name="Test Bill Category",
        description="Test category for bill tests",
    )
    
    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    return await category_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_liability(
    liability_repository: LiabilityRepository,
    test_account: Account,
    test_category: Category,
) -> Liability:
    """Create a test liability for use in tests."""
    # 1. ARRANGE: Setup is already done with fixtures
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    due_date = datetime.utcnow() + timedelta(days=30)
    liability_schema = create_liability_schema(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=due_date,
        category_id=test_category.id,
        primary_account_id=test_account.id,
        status=LiabilityStatus.PENDING,
    )
    
    # Convert validated schema to dict for repository
    validated_data = liability_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    return await liability_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_liabilities(
    liability_repository: LiabilityRepository,
    test_account: Account,
    test_category: Category,
) -> List[Liability]:
    """Create multiple test liabilities with different due dates."""
    # 1. ARRANGE: Setup dates for different liabilities
    now = datetime.utcnow()
    due_dates = [
        now + timedelta(days=5),   # Soon due
        now + timedelta(days=15),  # Medium term
        now + timedelta(days=30),  # Long term
        now - timedelta(days=5),   # Overdue
    ]
    
    liabilities = []
    for i, due_date in enumerate(due_dates):
        # 2. SCHEMA: Create and validate through Pydantic schema
        liability_schema = create_liability_schema(
            name=f"Test Bill {i+1}",
            amount=Decimal(f"{(i+1) * 50}.00"),
            due_date=due_date,
            category_id=test_category.id,
            primary_account_id=test_account.id,
            paid=(i == 2),  # Make one of them paid
            recurring=(i % 2 == 0),  # Make some recurring
        )
        
        # Convert validated schema to dict for repository
        validated_data = liability_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        liability = await liability_repository.create(validated_data)
        liabilities.append(liability)
    
    return liabilities


class TestLiabilityRepository:
    """
    Tests for the LiabilityRepository.

    These tests follow the standard 4-step pattern (Arrange-Schema-Act-Assert)
    for repository testing, simulating proper service-to-repository validation flow.
    """

    @pytest.mark.asyncio
    async def test_create_liability(
        self,
        liability_repository: LiabilityRepository,
        test_account: Account,
        test_category: Category,
    ):
        """Test creating a liability with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        due_date = datetime.utcnow() + timedelta(days=30)
        
        # 2. SCHEMA: Create and validate through Pydantic schema
        liability_schema = create_liability_schema(
            name="Test Monthly Bill",
            amount=Decimal("75.50"),
            due_date=due_date,
            category_id=test_category.id,
            primary_account_id=test_account.id,
            description="Monthly service bill",
        )
        
        # Convert validated schema to dict for repository
        validated_data = liability_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        result = await liability_repository.create(validated_data)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.name == "Test Monthly Bill"
        assert result.amount == Decimal("75.50")
        assert result.due_date == due_date
        assert result.category_id == test_category.id
        assert result.primary_account_id == test_account.id
        assert result.description == "Monthly service bill"
        assert result.paid is False
        assert result.status == LiabilityStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_liability(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test retrieving a liability by ID."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get the liability by ID
        result = await liability_repository.get(test_liability.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert result.name == test_liability.name
        assert result.amount == test_liability.amount
        assert result.due_date == test_liability.due_date
        assert result.category_id == test_liability.category_id
        assert result.primary_account_id == test_liability.primary_account_id

    @pytest.mark.asyncio
    async def test_update_liability(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test updating a liability with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. SCHEMA: Create and validate update data through Pydantic schema
        update_schema = LiabilityUpdate(
            id=test_liability.id,
            name="Updated Bill Name",
            amount=Decimal("150.00"),
            description="Updated description",
        )
        
        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump(exclude={"id"})
        
        # 3. ACT: Pass validated data to repository
        result = await liability_repository.update(test_liability.id, update_data)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert result.name == "Updated Bill Name"
        assert result.amount == Decimal("150.00")
        assert result.description == "Updated description"
        # Fields not in update_data should remain unchanged
        assert result.due_date == test_liability.due_date
        assert result.category_id == test_liability.category_id
        assert result.primary_account_id == test_liability.primary_account_id
        assert result.updated_at > test_liability.updated_at

    @pytest.mark.asyncio
    async def test_delete_liability(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test deleting a liability."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Delete the liability
        result = await liability_repository.delete(test_liability.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is True
        
        # Verify the liability is actually deleted
        deleted_check = await liability_repository.get(test_liability.id)
        assert deleted_check is None

    @pytest.mark.asyncio
    async def test_get_with_splits(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test getting a liability with its splits loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        # Note: In a complete test, we would create bill splits for this liability
        
        # 2. ACT: Get the liability with splits
        result = await liability_repository.get_with_splits(test_liability.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert hasattr(result, "splits")  # Ensure splits attribute exists
        # In a real test, we would verify splits are loaded correctly

    @pytest.mark.asyncio
    async def test_get_with_payments(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test getting a liability with its payments loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        # Note: In a complete test, we would create payments for this liability
        
        # 2. ACT: Get the liability with payments
        result = await liability_repository.get_with_payments(test_liability.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert hasattr(result, "payments")  # Ensure payments attribute exists
        # In a real test, we would verify payments are loaded correctly

    @pytest.mark.asyncio
    async def test_get_with_relationships(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test getting a liability with multiple relationships loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get the liability with multiple relationships
        result = await liability_repository.get_with_relationships(
            liability_id=test_liability.id,
            include_primary_account=True,
            include_category=True,
            include_splits=True,
            include_payments=True,
        )
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert hasattr(result, "primary_account")  # Ensure relationship attributes exist
        assert hasattr(result, "category")
        assert hasattr(result, "splits")
        assert hasattr(result, "payments")
        # In a real test, we would verify relationships are loaded correctly

    @pytest.mark.asyncio
    async def test_get_bills_due_in_range(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting bills due within a date range."""
        # 1. ARRANGE: Setup is already done with fixtures
        now = datetime.utcnow()
        start_date = now
        end_date = now + timedelta(days=20)
        
        # 2. ACT: Get bills due in range
        results = await liability_repository.get_bills_due_in_range(start_date, end_date)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 2  # Should find at least 2 bills due within 20 days
        for liability in results:
            assert liability.due_date >= start_date
            assert liability.due_date <= end_date
            assert liability.paid is False  # By default, include_paid is False

    @pytest.mark.asyncio
    async def test_get_bills_due_in_range_with_paid(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting bills due within a date range including paid bills."""
        # 1. ARRANGE: Setup is already done with fixtures
        now = datetime.utcnow()
        start_date = now
        end_date = now + timedelta(days=40)  # Include all future bills
        
        # 2. ACT: Get bills due in range, including paid
        results = await liability_repository.get_bills_due_in_range(
            start_date, end_date, include_paid=True
        )
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 3  # Should find at least 3 bills (2 unpaid, 1 paid)
        paid_count = sum(1 for bill in results if bill.paid)
        assert paid_count >= 1  # At least one paid bill in results

    @pytest.mark.asyncio
    async def test_get_bills_by_category(
        self,
        liability_repository: LiabilityRepository,
        test_category: Category,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting bills filtered by category."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get bills by category
        results = await liability_repository.get_bills_by_category(test_category.id)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1
        for liability in results:
            assert liability.category_id == test_category.id
            assert liability.paid is False  # By default, include_paid is False

    @pytest.mark.asyncio
    async def test_get_recurring_bills(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting recurring bills."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get recurring bills
        results = await liability_repository.get_recurring_bills()
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 2  # Should find at least 2 recurring bills
        for liability in results:
            assert liability.recurring is True

    @pytest.mark.asyncio
    async def test_find_bills_by_status(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test finding bills with a specific status."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Find bills by status
        results = await liability_repository.find_bills_by_status(LiabilityStatus.PENDING)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1
        for liability in results:
            assert liability.status == LiabilityStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_bills_for_account(
        self,
        liability_repository: LiabilityRepository,
        test_account: Account,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting bills associated with a specific account."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get bills for account
        results = await liability_repository.get_bills_for_account(test_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 3  # Should find at least 3 unpaid bills
        for liability in results:
            assert liability.primary_account_id == test_account.id
            assert liability.paid is False  # By default, include_paid is False

    @pytest.mark.asyncio
    async def test_get_upcoming_payments(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting upcoming bills due within specified days."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get upcoming payments (due in next 10 days)
        results = await liability_repository.get_upcoming_payments(days=10)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1  # Should find at least 1 bill due in 10 days
        now = datetime.utcnow()
        for liability in results:
            # Verify each bill is due within the next 10 days
            assert liability.due_date >= now
            assert liability.due_date <= now + timedelta(days=10)
            assert liability.paid is False

    @pytest.mark.asyncio
    async def test_get_overdue_bills(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting overdue bills."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get overdue bills
        results = await liability_repository.get_overdue_bills()
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1  # Should find at least 1 overdue bill
        now = datetime.utcnow()
        for liability in results:
            assert liability.due_date < now
            assert liability.paid is False

    @pytest.mark.asyncio
    async def test_mark_as_paid(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test marking a liability as paid."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Mark the liability as paid
        result = await liability_repository.mark_as_paid(test_liability.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert result.paid is True
        assert result.status == LiabilityStatus.PAID

    @pytest.mark.asyncio
    async def test_reset_payment_status(
        self,
        liability_repository: LiabilityRepository,
        test_liability: Liability,
    ):
        """Test resetting a liability payment status to unpaid."""
        # 1. ARRANGE: First mark as paid
        await liability_repository.mark_as_paid(test_liability.id)
        
        # 2. ACT: Reset payment status
        result = await liability_repository.reset_payment_status(test_liability.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_liability.id
        assert result.paid is False
        assert result.status == LiabilityStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_monthly_liability_amount(
        self,
        liability_repository: LiabilityRepository,
        test_multiple_liabilities: List[Liability],
    ):
        """Test getting total liability amount for a specific month."""
        # 1. ARRANGE: Setup is already done with fixtures
        now = datetime.utcnow()
        
        # 2. ACT: Get monthly liability amount
        total = await liability_repository.get_monthly_liability_amount(
            now.year, now.month
        )
        
        # 3. ASSERT: Verify the operation results
        assert total is not None
        assert total > Decimal("0")  # Should have some bills for this month

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test handling of validation errors that would be caught by the Pydantic schema."""
        # Try creating a schema with invalid data
        try:
            invalid_schema = LiabilityCreate(
                name="",  # Invalid empty name
                amount=Decimal("-10.00"),  # Invalid negative amount
                due_date=datetime.utcnow() - timedelta(days=10),  # Invalid past date
                category_id=1,
                primary_account_id=1,
            )
            assert False, "Schema should have raised a validation error"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            error_str = str(e).lower()
            assert "name" in error_str or "amount" in error_str or "due_date" in error_str
