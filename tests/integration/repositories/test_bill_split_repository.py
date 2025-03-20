"""
Integration tests for the BillSplitRepository using the standard validation pattern.

This test file demonstrates the proper validation flow for repository tests,
simulating how services call repositories in the actual application flow.
It follows the standard pattern:

1. Arrange: Set up test data and dependencies
2. Schema: Create and validate data through Pydantic schemas
3. Act: Pass validated data to repository methods
4. Assert: Verify the repository operation results

Integration tests for the BillSplitRepository.

This module contains tests for the BillSplitRepository using a real
test database to verify CRUD operations and specialized methods.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any

# Import schemas for validation - this is an essential part of the pattern
from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate, BillSplitBase

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability, LiabilityStatus
from src.models.bill_splits import BillSplit
from src.repositories.bill_splits import BillSplitRepository
from src.core.decimal_precision import DecimalPrecision


@pytest_asyncio.fixture
async def bill_split_repository(db_session: AsyncSession) -> BillSplitRepository:
    """Fixture for BillSplitRepository with test database session."""
    return BillSplitRepository(db_session)


@pytest_asyncio.fixture
async def test_account(db_session: AsyncSession) -> Account:
    """Fixture to create a test account for bill splits."""
    account = Account(
        name="Test Account",
        type="credit",
        available_balance=Decimal("-100.00"),
        total_limit=Decimal("5000.00"),
        last_statement_balance=Decimal("100.00"),
        last_statement_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_liability(db_session: AsyncSession, test_account: Account) -> Liability:
    """Fixture to create a test liability."""
    liability = Liability(
        name="Test Bill",
        amount=Decimal("300.00"),
        due_date=datetime.utcnow() + timedelta(days=15),
        category_id=1,  # Would need a real category in a complete test
        primary_account_id=test_account.id,
        status=LiabilityStatus.PENDING,
        recurring=False,
        paid=False,
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(liability)
    await db_session.flush()
    await db_session.refresh(liability)
    return liability


@pytest_asyncio.fixture
async def test_bill_splits(
    db_session: AsyncSession, 
    test_liability: Liability, 
    test_account: Account
) -> List[BillSplit]:
    """Fixture to create test bill splits."""
    # Create three splits for the test liability
    splits = [
        BillSplit(
            liability_id=test_liability.id,
            account_id=test_account.id,
            amount=Decimal("100.00"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        BillSplit(
            liability_id=test_liability.id,
            account_id=test_account.id,
            amount=Decimal("100.00"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        BillSplit(
            liability_id=test_liability.id,
            account_id=test_account.id,
            amount=Decimal("100.00"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    for split in splits:
        db_session.add(split)
    
    await db_session.flush()
    
    # Refresh each split to get updated data
    for split in splits:
        await db_session.refresh(split)
    
    return splits


class TestBillSplitRepository:
    """
    Tests for the BillSplitRepository.
    
    These tests verify that the repository correctly handles CRUD operations
    and specialized queries for bill splits.
    """
    
    @pytest.mark.asyncio
    async def test_create_bill_split(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_liability: Liability,
        test_account: Account,
        db_session: AsyncSession
    ):
        """Test creating a bill split with proper validation flow."""
        # Arrange & Schema: Create and validate through Pydantic schema
        bill_split_schema = BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_account.id,
            amount=Decimal("150.00")
        )
        
        # Convert validated schema to dict for repository (simulating service flow)
        validated_data = bill_split_schema.model_dump()
        
        # Act: Pass validated data to repository
        result = await bill_split_repository.create(validated_data)
        
        # Assert: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.liability_id == test_liability.id
        assert result.account_id == test_account.id
        assert result.amount == Decimal("150.00")
        
        # Verify additional schema elements were properly handled
        assert result.created_at is not None  # Automatically added by repository
    
    @pytest.mark.asyncio
    async def test_get_bill_split(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit]
    ):
        """Test retrieving a bill split by ID."""
        # Act
        result = await bill_split_repository.get(test_bill_splits[0].id)
        
        # Assert
        assert result is not None
        assert result.id == test_bill_splits[0].id
        assert result.liability_id == test_bill_splits[0].liability_id
        assert result.account_id == test_bill_splits[0].account_id
        assert result.amount == test_bill_splits[0].amount
    
    @pytest.mark.asyncio
    async def test_update_bill_split(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit]
    ):
        """Test updating a bill split with proper validation flow."""
        # Arrange & Schema: Create and validate update data through Pydantic schema
        bill_split_id = test_bill_splits[0].id
        new_amount = Decimal("175.00")
        
        update_schema = BillSplitUpdate(
            id=bill_split_id,
            amount=new_amount
        )
        
        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump()
        # Remove id from the update data as it's passed separately to the update method
        update_id = update_data.pop("id")
        
        # Act: Pass validated data to repository
        result = await bill_split_repository.update(bill_split_id, {"amount": new_amount})
        
        # Assert: Verify the operation results
        assert result is not None
        assert result.id == bill_split_id
        assert result.amount == new_amount
        assert result.updated_at is not None  # Should be automatically updated
    
    @pytest.mark.asyncio
    async def test_delete_bill_split(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit]
    ):
        """Test deleting a bill split."""
        # Act
        result = await bill_split_repository.delete(test_bill_splits[0].id)
        
        # Assert
        assert result is True
        
        # Verify it's actually deleted
        deleted_split = await bill_split_repository.get(test_bill_splits[0].id)
        assert deleted_split is None
    
    @pytest.mark.asyncio
    async def test_get_with_relationships(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit]
    ):
        """Test getting a bill split with relationships loaded."""
        # Act
        result = await bill_split_repository.get_with_relationships(test_bill_splits[0].id)
        
        # Assert
        assert result is not None
        assert result.liability is not None
        assert result.account is not None
        assert result.liability.id == test_bill_splits[0].liability_id
        assert result.account.id == test_bill_splits[0].account_id
    
    @pytest.mark.asyncio
    async def test_get_splits_for_bill(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_liability: Liability
    ):
        """Test getting all splits for a specific bill."""
        # Act
        results = await bill_split_repository.get_splits_for_bill(test_liability.id)
        
        # Assert
        assert len(results) == 3
        for split in results:
            assert split.liability_id == test_liability.id
            assert split.liability is not None
            assert split.account is not None
    
    @pytest.mark.asyncio
    async def test_get_splits_for_account(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_account: Account
    ):
        """Test getting all splits for a specific account."""
        # Act
        results = await bill_split_repository.get_splits_for_account(test_account.id)
        
        # Assert
        assert len(results) == 3
        for split in results:
            assert split.account_id == test_account.id
            assert split.liability is not None
            assert split.account is not None
    
    @pytest.mark.asyncio
    async def test_bulk_create_splits(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_liability: Liability,
        test_account: Account,
        db_session: AsyncSession
    ):
        """Test creating multiple bill splits in bulk with proper validation flow."""
        # Arrange - clear out any existing splits first
        await bill_split_repository.delete_splits_for_liability(test_liability.id)
        
        # Create and validate through Pydantic schemas
        split_schemas = [
            BillSplitCreate(
                liability_id=test_liability.id,  # Will be overridden in bulk_create_splits
                account_id=test_account.id,
                amount=Decimal("100.00")
            ),
            BillSplitCreate(
                liability_id=test_liability.id,  # Will be overridden in bulk_create_splits
                account_id=test_account.id,
                amount=Decimal("200.00")
            )
        ]
        
        # Convert validated schemas to dicts for repository
        splits_data = [schema.model_dump() for schema in split_schemas]
        
        # Remove liability_id as it will be provided by the bulk_create_splits method
        for split_data in splits_data:
            split_data.pop("liability_id")
        
        # Act
        results = await bill_split_repository.bulk_create_splits(test_liability.id, splits_data)
        
        # Assert
        assert len(results) == 2
        assert results[0].liability_id == test_liability.id
        assert results[1].liability_id == test_liability.id
        assert results[0].amount == Decimal("100.00")
        assert results[1].amount == Decimal("200.00")
        
        # Verify in database
        db_splits = await bill_split_repository.get_splits_for_bill(test_liability.id)
        assert len(db_splits) == 2
    
    @pytest.mark.asyncio
    async def test_delete_splits_for_liability(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_liability: Liability
    ):
        """Test deleting all splits for a liability."""
        # Act
        count = await bill_split_repository.delete_splits_for_liability(test_liability.id)
        
        # Assert
        assert count == 3
        
        # Verify in database
        remaining_splits = await bill_split_repository.get_splits_for_bill(test_liability.id)
        assert len(remaining_splits) == 0
    
    @pytest.mark.asyncio
    async def test_calculate_split_totals(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_liability: Liability
    ):
        """Test calculating the total amount of all splits for a liability."""
        # Act
        total = await bill_split_repository.calculate_split_totals(test_liability.id)
        
        # Assert
        expected_total = sum(split.amount for split in test_bill_splits)
        assert total == expected_total
    
    @pytest.mark.asyncio
    async def test_get_account_split_totals(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_account: Account
    ):
        """Test calculating total splits for an account."""
        # Act
        total = await bill_split_repository.get_account_split_totals(test_account.id)
        
        # Assert
        expected_total = sum(split.amount for split in test_bill_splits)
        assert total == expected_total
    
    @pytest.mark.asyncio
    async def test_get_split_distribution(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_liability: Liability,
        test_account: Account
    ):
        """Test getting the distribution of splits across accounts."""
        # Act
        distribution = await bill_split_repository.get_split_distribution(test_liability.id)
        
        # Assert
        assert test_account.id in distribution
        expected_total = sum(split.amount for split in test_bill_splits)
        assert distribution[test_account.id] == expected_total
    
    @pytest.mark.asyncio
    async def test_get_splits_with_liability_details(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit],
        test_account: Account
    ):
        """Test getting splits with liability details."""
        # Act
        results = await bill_split_repository.get_splits_with_liability_details(test_account.id)
        
        # Assert
        assert len(results) == 3
        for split in results:
            assert split.account_id == test_account.id
            assert split.liability is not None
            assert split.account is not None
    
    @pytest.mark.asyncio
    async def test_get_recent_split_patterns(
        self, 
        bill_split_repository: BillSplitRepository, 
        test_bill_splits: List[BillSplit]
    ):
        """Test analyzing recent split patterns."""
        # Act
        patterns = await bill_split_repository.get_recent_split_patterns(days=30)
        
        # Assert
        assert len(patterns) > 0
        liability_id, distribution = patterns[0]
        assert liability_id is not None
        assert len(distribution) > 0

    @pytest.mark.asyncio
    async def test_validation_error_handling(
        self,
        bill_split_repository: BillSplitRepository,
        test_liability: Liability,
        test_account: Account
    ):
        """Test handling invalid data that would normally be caught by schema validation."""
        # Try creating a schema with invalid data and expect it to fail validation
        try:
            invalid_schema = BillSplitCreate(
                liability_id=test_liability.id,
                account_id=test_account.id,
                amount=Decimal("-50.00")  # Invalid negative amount
            )
            assert False, "Schema should have raised a validation error for negative amount"
        except ValueError as e:
            # This is the expected path - schema validation should catch the error
            assert "greater than 0" in str(e) or "must be greater than 0" in str(e)

        # This illustrates why schema validation in tests is important - it prevents invalid
        # data from ever reaching the repository
