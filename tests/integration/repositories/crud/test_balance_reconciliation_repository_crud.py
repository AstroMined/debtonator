"""
Integration tests for the BalanceReconciliationRepository.

This module contains tests for the BalanceReconciliationRepository using the
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
from src.models.balance_reconciliation import BalanceReconciliation
from src.repositories.accounts import AccountRepository
from src.repositories.balance_reconciliation import \
    BalanceReconciliationRepository
from src.schemas.balance_reconciliation import (BalanceReconciliationCreate,
                                                BalanceReconciliationUpdate)
from tests.helpers.datetime_utils import (datetime_equals,
                                          datetime_greater_than, utc_now)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.balance_reconciliation import \
    create_balance_reconciliation_schema

pytestmark = pytest.mark.asyncio


async def test_create_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
):
    """Test creating a balance reconciliation entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    reconciliation_schema = create_balance_reconciliation_schema(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1050.00"),
        reason="Monthly balance verification",
    )

    # Convert validated schema to dict for repository
    validated_data = reconciliation_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await balance_reconciliation_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.account_id == test_checking_account.id
    assert result.previous_balance == Decimal("1000.00")
    assert result.new_balance == Decimal("1050.00")
    assert result.adjustment_amount == Decimal("50.00")
    assert result.reason == "Monthly balance verification"
    assert result.reconciliation_date is not None


async def test_get_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_balance_reconciliation: BalanceReconciliation,
):
    """Test retrieving a balance reconciliation entry by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the reconciliation entry
    result = await balance_reconciliation_repository.get(test_balance_reconciliation.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_reconciliation.id
    assert result.account_id == test_balance_reconciliation.account_id
    assert result.previous_balance == test_balance_reconciliation.previous_balance
    assert result.new_balance == test_balance_reconciliation.new_balance
    assert result.adjustment_amount == test_balance_reconciliation.adjustment_amount
    assert result.reason == test_balance_reconciliation.reason


async def test_update_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_balance_reconciliation: BalanceReconciliation,
):
    """Test updating a balance reconciliation entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_balance_reconciliation.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = BalanceReconciliationUpdate(
        id=test_balance_reconciliation.id,
        new_balance=Decimal("1075.25"),
        reason="Updated reconciliation with corrected balance",
    )

    # Calculate new adjustment amount
    adjustment_amount = (
        Decimal("1075.25") - test_balance_reconciliation.previous_balance
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})
    update_data["adjustment_amount"] = adjustment_amount

    # 3. ACT: Pass validated data to repository
    result = await balance_reconciliation_repository.update(
        test_balance_reconciliation.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_reconciliation.id
    assert result.new_balance == Decimal("1075.25")
    assert result.adjustment_amount == adjustment_amount
    assert result.reason == "Updated reconciliation with corrected balance"

    # Compare against stored original timestamp
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )
