"""
Integration tests for the CreditLimitHistoryRepository.

This module contains tests for the CreditLimitHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.credit_limit_history import CreditLimitHistory
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.accounts import AccountRepository
from src.schemas.credit_limit_history import CreditLimitHistoryCreate, CreditLimitHistoryUpdate
from tests.helpers.schema_factories import create_account_schema, create_credit_limit_history_schema


@pytest_asyncio.fixture
async def credit_limit_history_repository(db_session: AsyncSession) -> CreditLimitHistoryRepository:
    """Fixture for CreditLimitHistoryRepository with test database session."""
    return CreditLimitHistoryRepository(db_session)


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def test_credit_account(account_repository: AccountRepository) -> Account:
    """Create a test credit account for use in tests."""
    # Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Credit Account",
        account_type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("5000.00")
    )
    
    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()
    
    # Create account through repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_credit_limit_history(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_account: Account
) -> CreditLimitHistory:
    """Create a test credit limit history entry for use in tests."""
    # Create and validate through Pydantic schema
    history_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("5000.00"),
        effective_date=datetime.utcnow() - timedelta(days=30),
        reason="Initial credit limit"
    )
    
    # Convert validated schema to dict for repository
    validated_data = history_schema.model_dump()
    
    # Create history entry through repository
    return await credit_limit_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_credit_limit_changes(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_account: Account
) -> List[CreditLimitHistory]:
    """Create multiple credit limit history entries for testing."""
    now = datetime.utcnow()
    
    # Create base entry (already created in test_credit_limit_history)
    base_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("5000.00"),
        effective_date=now - timedelta(days=90),
        reason="Initial credit limit"
    )
    await credit_limit_history_repository.create(base_schema.model_dump())
    
    # Create increase entry
    increase_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("7500.00"),
        effective_date=now - timedelta(days=60),
        reason="Credit increase due to good payment history"
    )
    increase = await credit_limit_history_repository.create(increase_schema.model_dump())
    
    # Create decrease entry
    decrease_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("6500.00"),
        effective_date=now - timedelta(days=30),
        reason="Credit adjustment due to risk assessment"
    )
    decrease = await credit_limit_history_repository.create(decrease_schema.model_dump())
    
    # Create recent increase entry
    latest_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("8000.00"),
        effective_date=now - timedelta(days=5),
        reason="Credit increase request approved"
    )
    latest = await credit_limit_history_repository.create(latest_schema.model_dump())
    
    return [increase, decrease, latest]


class TestCreditLimitHistoryRepository:
    """
    Tests for the CreditLimitHistoryRepository.
    
    These tests follow the standard 4-step pattern (Arrange-Schema-Act-Assert)
    for repository testing, simulating proper service-to-repository validation flow.
    """
    
    @pytest.mark.asyncio
    async def test_create_credit_limit_history(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account
    ):
        """Test creating a credit limit history entry with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. SCHEMA: Create and validate through Pydantic schema
        history_schema = create_credit_limit_history_schema(
            account_id=test_credit_account.id,
            credit_limit=Decimal("10000.00"),
            reason="Credit limit increase due to excellent payment history"
        )
        
        # Convert validated schema to dict for repository
        validated_data = history_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        result = await credit_limit_history_repository.create(validated_data)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.account_id == test_credit_account.id
        assert result.credit_limit == Decimal("10000.00")
        assert result.reason == "Credit limit increase due to excellent payment history"
        assert result.effective_date is not None
    
    @pytest.mark.asyncio
    async def test_get_credit_limit_history(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_limit_history: CreditLimitHistory
    ):
        """Test retrieving a credit limit history entry by ID."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get the history entry
        result = await credit_limit_history_repository.get(test_credit_limit_history.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_limit_history.id
        assert result.account_id == test_credit_limit_history.account_id
        assert result.credit_limit == test_credit_limit_history.credit_limit
        assert result.reason == test_credit_limit_history.reason
    
    @pytest.mark.asyncio
    async def test_update_credit_limit_history(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_limit_history: CreditLimitHistory
    ):
        """Test updating a credit limit history entry with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. SCHEMA: Create and validate update data through Pydantic schema
        update_schema = CreditLimitHistoryUpdate(
            id=test_credit_limit_history.id,
            credit_limit=Decimal("12000.00"),
            reason="Updated credit limit increase"
        )
        
        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump(exclude={"id"})
        
        # 3. ACT: Pass validated data to repository
        result = await credit_limit_history_repository.update(
            test_credit_limit_history.id, 
            update_data
        )
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_limit_history.id
        assert result.credit_limit == Decimal("12000.00")
        assert result.reason == "Updated credit limit increase"
        assert result.updated_at > test_credit_limit_history.updated_at
    
    @pytest.mark.asyncio
    async def test_get_by_account(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting credit limit history entries for an account."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get history entries for the account
        results = await credit_limit_history_repository.get_by_account(test_credit_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 4  # At least 4 entries (initial + 3 changes)
        for entry in results:
            assert entry.account_id == test_credit_account.id
    
    @pytest.mark.asyncio
    async def test_get_with_account(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_limit_history: CreditLimitHistory
    ):
        """Test getting a credit limit history entry with account relationship loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get the history entry with account
        result = await credit_limit_history_repository.get_with_account(test_credit_limit_history.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_limit_history.id
        assert result.account is not None
        assert result.account.id == test_credit_limit_history.account_id
    
    @pytest.mark.asyncio
    async def test_get_by_date_range(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting credit limit history entries within a date range."""
        # 1. ARRANGE: Setup is already done with fixtures
        now = datetime.utcnow()
        start_date = now - timedelta(days=70)
        end_date = now - timedelta(days=20)
        
        # 2. ACT: Get history entries within date range
        results = await credit_limit_history_repository.get_by_date_range(
            test_credit_account.id,
            start_date,
            end_date
        )
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 2  # At least 2 entries in this range
        for entry in results:
            assert entry.account_id == test_credit_account.id
            assert entry.effective_date >= start_date
            assert entry.effective_date <= end_date
    
    @pytest.mark.asyncio
    async def test_get_latest_limit(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting the most recent credit limit history entry."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get the latest limit
        result = await credit_limit_history_repository.get_latest_limit(test_credit_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.account_id == test_credit_account.id
        assert result.credit_limit == Decimal("8000.00")  # Latest from fixture
    
    @pytest.mark.asyncio
    async def test_get_limit_at_date(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting the credit limit that was effective at a specific date."""
        # 1. ARRANGE: Setup is already done with fixtures
        now = datetime.utcnow()
        # Check limit at midpoint (should be the decrease to 6500)
        target_date = now - timedelta(days=45)
        
        # 2. ACT: Get limit at date
        result = await credit_limit_history_repository.get_limit_at_date(
            test_credit_account.id,
            target_date
        )
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.account_id == test_credit_account.id
        assert result.credit_limit == Decimal("7500.00")  # Should be the increase entry
    
    @pytest.mark.asyncio
    async def test_get_limit_increases(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting credit limit increases for an account."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get limit increases
        results = await credit_limit_history_repository.get_limit_increases(test_credit_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 2  # At least 2 increases in fixtures
        
        # Check each result is an increase
        previous_limit = None
        for entry in results:
            if previous_limit is not None:
                assert entry.credit_limit > previous_limit
            previous_limit = entry.credit_limit
    
    @pytest.mark.asyncio
    async def test_get_limit_decreases(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting credit limit decreases for an account."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get limit decreases
        results = await credit_limit_history_repository.get_limit_decreases(test_credit_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1  # At least 1 decrease in fixtures
    
    @pytest.mark.asyncio
    async def test_get_limit_change_trend(
        self,
        credit_limit_history_repository: CreditLimitHistoryRepository,
        test_credit_account: Account,
        test_credit_limit_changes: List[CreditLimitHistory]
    ):
        """Test getting credit limit change trend over time."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get limit change trend
        results = await credit_limit_history_repository.get_limit_change_trend(
            test_credit_account.id
        )
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 4  # At least 4 entries in trend
        assert "change" in results[1]  # Change should be calculated for all but first entry
        assert "change_percent" in results[1]
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(
        self,
        test_credit_account: Account
    ):
        """Test handling of validation errors that would be caught by the Pydantic schema."""
        # Try creating a schema with invalid data
        try:
            invalid_schema = CreditLimitHistoryCreate(
                account_id=test_credit_account.id,
                credit_limit=Decimal("-5000.00"),  # Invalid negative credit limit
                effective_date=datetime.utcnow()
            )
            assert False, "Schema should have raised a validation error for negative credit limit"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            assert "credit_limit" in str(e).lower()
