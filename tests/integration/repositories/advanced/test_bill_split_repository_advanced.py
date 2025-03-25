"""
Integration tests for the BillSplitRepository using the standard validation pattern.

This test file demonstrates the proper validation flow for repository tests,
simulating how services call repositories in the actual application flow.
It follows the standard pattern:

1. Arrange: Set up test data and dependencies
2. Schema: Create and validate data through Pydantic schemas
3. Act: Pass validated data to repository methods
4. Assert: Verify the repository operation results
"""

from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability
from src.repositories.accounts import AccountRepository
from src.repositories.bill_splits import BillSplitRepository
from src.repositories.liabilities import LiabilityRepository
from src.schemas.accounts import AccountCreate
from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate
from src.schemas.liabilities import LiabilityCreate
from tests.helpers.datetime_utils import utc_now, days_ago, days_from_now, datetime_equals, datetime_greater_than
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.bill_splits import create_bill_split_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema

pytestmark = pytest.mark.asyncio


async def test_get_with_relationships(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
):
    """Test getting a bill split with relationships loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the bill split with relationships
    result = await bill_split_repository.get_with_relationships(test_bill_splits[0].id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_bill_splits[0].id

    # Check that relationships are properly loaded
    assert hasattr(result, "liability")
    assert result.liability is not None
    assert result.liability.id == test_bill_splits[0].liability_id

    assert hasattr(result, "account")
    assert result.account is not None
    assert result.account.id == test_bill_splits[0].account_id


async def test_get_splits_for_bill(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_liability: Liability,
):
    """Test getting all splits for a specific bill."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get splits for the liability
    results = await bill_split_repository.get_splits_for_bill(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert len(results) == 3
    for split in results:
        assert split.liability_id == test_liability.id
        assert hasattr(split, "liability")
        assert split.liability is not None
        assert hasattr(split, "account")
        assert split.account is not None


async def test_get_splits_for_account(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_checking_account: Account,
):
    """Test getting all splits for a specific account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get splits for the account
    results = await bill_split_repository.get_splits_for_account(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) == 3
    for split in results:
        assert split.account_id == test_checking_account.id
        assert hasattr(split, "liability")
        assert split.liability is not None
        assert hasattr(split, "account")
        assert split.account is not None


async def test_get_splits_in_date_range(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_checking_account: Account,
    test_liability: Liability,
):
    """Test getting splits for an account within a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    start_date = days_ago(30)  # Use the helper function
    end_date = days_from_now(30)  # Use the helper function

    # 2. ACT: Get splits in date range
    results = await bill_split_repository.get_splits_in_date_range(
        test_checking_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) == 3  # All test splits should be in this range
    for split in results:
        assert split.account_id == test_checking_account.id
        # Use proper timezone-aware comparison
        assert datetime_greater_than(split.liability.due_date, start_date) or datetime_equals(split.liability.due_date, start_date)
        assert datetime_greater_than(end_date, split.liability.due_date) or datetime_equals(end_date, split.liability.due_date)


async def test_get_splits_by_amount_range(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
):
    """Test getting splits with amounts in a specific range."""
    # 1. ARRANGE: Setup is already done with fixtures
    min_amount = Decimal("50.00")
    max_amount = Decimal("150.00")

    # 2. ACT: Get splits in amount range
    results = await bill_split_repository.get_splits_by_amount_range(
        min_amount, max_amount
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # At least our test splits
    for split in results:
        assert split.amount >= min_amount
        assert split.amount <= max_amount


async def test_bulk_create_splits(
    bill_split_repository: BillSplitRepository,
    test_liability: Liability,
    test_checking_account: Account,
    test_second_account: Account,
):
    """Test creating multiple bill splits in bulk with proper validation flow."""
    # 1. ARRANGE: Clear out any existing splits first
    await bill_split_repository.delete_splits_for_liability(test_liability.id)

    # 2. SCHEMA: Create and validate through Pydantic schemas
    split_schemas = [
        create_bill_split_schema(
            liability_id=test_liability.id,  # Will be overridden in bulk_create_splits
            account_id=test_checking_account.id,
            amount=Decimal("100.00"),
        ),
        create_bill_split_schema(
            liability_id=test_liability.id,  # Will be overridden in bulk_create_splits
            account_id=test_second_account.id,
            amount=Decimal("200.00"),
        ),
    ]

    # Convert validated schemas to dicts for repository
    splits_data = [schema.model_dump() for schema in split_schemas]

    # Remove liability_id as it will be provided by the bulk_create_splits method
    for split_data in splits_data:
        split_data.pop("liability_id")

    # 3. ACT: Pass validated data to repository
    results = await bill_split_repository.bulk_create_splits(
        test_liability.id, splits_data
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) == 2
    assert results[0].liability_id == test_liability.id
    assert results[1].liability_id == test_liability.id
    assert results[0].amount == Decimal("100.00")
    assert results[1].amount == Decimal("200.00")

    # Verify in database
    db_splits = await bill_split_repository.get_splits_for_bill(test_liability.id)
    assert len(db_splits) == 2


async def test_delete_splits_for_liability(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_liability: Liability,
):
    """Test deleting all splits for a liability."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete all splits for the liability
    count = await bill_split_repository.delete_splits_for_liability(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert count == 3  # Should have deleted 3 splits

    # Verify in database
    remaining_splits = await bill_split_repository.get_splits_for_bill(
        test_liability.id
    )
    assert len(remaining_splits) == 0


async def test_calculate_split_totals(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_liability: Liability,
):
    """Test calculating the total amount of all splits for a liability."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Calculate split totals
    total = await bill_split_repository.calculate_split_totals(test_liability.id)

    # 3. ASSERT: Verify the operation results
    expected_total = sum(split.amount for split in test_bill_splits)
    assert total == expected_total


async def test_get_account_split_totals(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_checking_account: Account,
):
    """Test calculating total splits for an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Calculate account split totals
    total = await bill_split_repository.get_account_split_totals(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    expected_total = sum(split.amount for split in test_bill_splits)
    assert total == expected_total


async def test_get_account_split_totals_with_date_range(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_checking_account: Account,
):
    """Test calculating total splits for an account within a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    start_date = utc_now() - timedelta(days=30)
    end_date = utc_now() + timedelta(days=30)

    # 2. ACT: Calculate account split totals within date range
    total = await bill_split_repository.get_account_split_totals(
        test_checking_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    expected_total = sum(split.amount for split in test_bill_splits)
    assert total == expected_total


async def test_get_split_distribution(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_liability: Liability,
    test_checking_account: Account,
):
    """Test getting the distribution of splits across accounts."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get split distribution
    distribution = await bill_split_repository.get_split_distribution(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert test_checking_account.id in distribution
    expected_total = sum(split.amount for split in test_bill_splits)
    assert distribution[test_checking_account.id] == expected_total


async def test_get_splits_with_liability_details(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_checking_account: Account,
):
    """Test getting splits with liability details."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get splits with liability details
    results = await bill_split_repository.get_splits_with_liability_details(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) == 3
    for split in results:
        assert split.account_id == test_checking_account.id
        assert split.liability is not None
        assert split.account is not None


async def test_get_splits_with_liability_details_paid_only(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
    test_checking_account: Account,
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test getting splits with liability details, filtered to paid only."""
    # 1. ARRANGE: Mark the liability as paid
    await liability_repository.update(test_liability.id, {"paid": True})

    # 2. ACT: Get paid splits with liability details
    results = await bill_split_repository.get_splits_with_liability_details(
        test_checking_account.id, paid_only=True
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) == 3
    for split in results:
        assert split.account_id == test_checking_account.id
        assert split.liability is not None
        assert split.liability.paid is True
        assert split.account is not None


async def test_get_recent_split_patterns(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
):
    """Test analyzing recent split patterns."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get recent split patterns
    patterns = await bill_split_repository.get_recent_split_patterns(days=30)

    # 3. ASSERT: Verify the operation results
    assert len(patterns) > 0
    liability_id, distribution = patterns[0]
    assert liability_id is not None
    assert len(distribution) > 0


async def test_validation_error_handling():
    """Test handling invalid data that would normally be caught by schema validation."""
    # Try creating a schema with invalid data and expect it to fail validation
    try:
        invalid_schema = BillSplitCreate(
            liability_id=1,
            account_id=1,
            amount=Decimal("-50.00"),  # Invalid negative amount
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is the expected path - schema validation should catch the error
        error_str = str(e).lower()
        assert "greater than 0" in error_str or "must be greater than 0" in error_str

    # This illustrates why schema validation in tests is important - it prevents invalid
    # data from ever reaching the repository
