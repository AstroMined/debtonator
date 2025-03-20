"""
Integration tests for the BillSplitRepository.

This module contains tests for the BillSplitRepository using a real
test database to verify CRUD operations and specialized methods.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any

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
        """Test creating a bill split."""
        # Arrange
        split_data = {
            "liability_id": test_liability.id,
            "account_id": test_account.id,
            "amount": Decimal("150.00"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Act
        result = await bill_split_repository.create(split_data)
        
        # Assert
        assert result is not None
        assert result.id is not None
        assert result.liability_id == test_liability.id
        assert result.account_id == test_account.id
        assert result.amount == Decimal("150.00")
    
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
        """Test updating a bill split."""
        # Arrange
        new_amount = Decimal("175.00")
        update_data = {"amount": new_amount}
        
        # Act
        result = await bill_split_repository.update(test_bill_splits[0].id, update_data)
        
        # Assert
        assert result is not None
        assert result.id == test_bill_splits[0].id
        assert result.amount == new_amount
    
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
        """Test creating multiple bill splits in bulk."""
        # Arrange - clear out any existing splits first
        await bill_split_repository.delete_splits_for_liability(test_liability.id)
        
        splits_data = [
            {
                "account_id": test_account.id,
                "amount": Decimal("100.00"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "account_id": test_account.id,
                "amount": Decimal("200.00"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
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
