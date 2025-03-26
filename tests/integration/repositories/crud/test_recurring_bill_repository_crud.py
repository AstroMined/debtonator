"""
Integration tests for the RecurringBillRepository.

This module contains tests for the RecurringBillRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.recurring_bills import RecurringBill
from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.repositories.recurring_bills import RecurringBillRepository
from src.schemas.recurring_bills import (RecurringBillCreate,
                                         RecurringBillUpdate)
from src.utils.datetime_utils import (datetime_equals,
                                          datetime_greater_than, utc_now)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.recurring_bills import \
    create_recurring_bill_schema

pytestmark = pytest.mark.asyncio


async def test_create_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_checking_account: Account,
    test_category: Category,
):
    """Test creating a recurring bill with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    bill_schema = create_recurring_bill_schema(
        bill_name="New Test Bill",
        amount=Decimal("75.00"),
        day_of_month=10,
        account_id=test_checking_account.id,
        category_id=test_category.id,
        auto_pay=True,
    )

    # Convert validated schema to dict for repository
    validated_data = bill_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await recurring_bill_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.bill_name == "New Test Bill"
    assert result.amount == Decimal("75.00")
    assert result.day_of_month == 10
    assert result.account_id == test_checking_account.id
    assert result.category_id == test_category.id
    assert result.auto_pay is True
    assert result.active is True  # Default when created
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test retrieving a recurring bill by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the recurring bill by ID
    result = await recurring_bill_repository.get(test_recurring_bill.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_bill.id
    assert result.bill_name == test_recurring_bill.bill_name
    assert result.amount == test_recurring_bill.amount
    assert result.day_of_month == test_recurring_bill.day_of_month
    assert result.account_id == test_recurring_bill.account_id
    assert result.category_id == test_recurring_bill.category_id
    assert result.auto_pay == test_recurring_bill.auto_pay
    assert result.active == test_recurring_bill.active


async def test_update_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test updating a recurring bill with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Store original timestamp before update
    original_updated_at = test_recurring_bill.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = RecurringBillUpdate(
        bill_name="Updated Bill Name",
        amount=Decimal("125.00"),
        day_of_month=20,
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude_unset=True)

    # 3. ACT: Pass validated data to repository
    result = await recurring_bill_repository.update(test_recurring_bill.id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_bill.id
    assert result.bill_name == "Updated Bill Name"
    assert result.amount == Decimal("125.00")
    assert result.day_of_month == 20
    # Fields not in update_data should remain unchanged
    assert result.account_id == test_recurring_bill.account_id
    assert result.category_id == test_recurring_bill.category_id
    assert result.auto_pay == test_recurring_bill.auto_pay
    assert result.active == test_recurring_bill.active

    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test deleting a recurring bill."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the recurring bill
    result = await recurring_bill_repository.delete(test_recurring_bill.id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the bill is actually deleted
    deleted_check = await recurring_bill_repository.get(test_recurring_bill.id)
    assert deleted_check is None
