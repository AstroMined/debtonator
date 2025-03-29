from datetime import date
from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability
from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate, BulkSplitOperation
from src.services.bill_splits import BillSplitService


@pytest.fixture(scope="function")
async def test_category(db_session):
    category = Category(
        name="Test Category",
        description="Test Description",
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(category)
    await db_session.flush()
    return category


@pytest.fixture(scope="function")
async def test_accounts(db_session):
    accounts = [
        Account(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-500"),
            total_limit=Decimal("1000"),
            created_at=date.today(),
            updated_at=date.today(),
        ),
        Account(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000"),
            created_at=date.today(),
            updated_at=date.today(),
        ),
    ]
    for account in accounts:
        db_session.add(account)
    await db_session.flush()
    return accounts


@pytest.fixture(scope="function")
async def test_liability(db_session, test_category, test_accounts):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("300"),
        due_date=date.today(),
        category_id=test_category.id,
        primary_account_id=test_accounts[0].id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        recurring=False,
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(liability)
    await db_session.flush()
    return liability


async def test_bulk_create_success(db_session, test_liability, test_accounts):
    service = BillSplitService(db_session)

    # Create bulk operation with two splits
    splits = [
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[0].id,
            amount=Decimal("100"),
        ),
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[1].id,
            amount=Decimal("200"),
        ),
    ]

    operation = BulkSplitOperation(operation_type="create", splits=splits)

    result = await service.process_bulk_operation(operation)

    assert result.success is True
    assert result.processed_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0
    assert len(result.successful_splits) == 2
    assert len(result.errors) == 0

    # Verify splits were created in database
    total = await service.calculate_split_totals(test_liability.id)
    assert total == Decimal("300")


async def test_bulk_create_partial_failure(db_session, test_liability, test_accounts):
    service = BillSplitService(db_session)

    # Create bulk operation with one valid and one invalid split
    splits = [
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[0].id,
            amount=Decimal("100"),
        ),
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[1].id,
            amount=Decimal("2000"),  # Exceeds available balance
        ),
    ]

    operation = BulkSplitOperation(operation_type="create", splits=splits)

    result = await service.process_bulk_operation(operation)

    assert result.success is False
    assert result.processed_count == 2
    assert result.success_count == 1
    assert result.failure_count == 1
    assert len(result.successful_splits) == 1
    assert len(result.errors) == 1
    assert "insufficient balance" in result.errors[0].error_message.lower()

    # Verify only valid split was created
    total = await service.calculate_split_totals(test_liability.id)
    assert total == Decimal("100")


async def test_bulk_update(db_session, test_liability, test_accounts):
    service = BillSplitService(db_session)

    # First create some splits
    split1 = await service.create_bill_split(
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[0].id,
            amount=Decimal("100"),
        )
    )
    split2 = await service.create_bill_split(
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[1].id,
            amount=Decimal("200"),
        )
    )

    # Update both splits
    updates = [
        BillSplitUpdate(amount=Decimal("150"), id=split1.id),
        BillSplitUpdate(amount=Decimal("150"), id=split2.id),
    ]

    operation = BulkSplitOperation(operation_type="update", splits=updates)

    result = await service.process_bulk_operation(operation)

    assert result.success is True
    assert result.processed_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    # Verify updates were applied
    total = await service.calculate_split_totals(test_liability.id)
    assert total == Decimal("300")


async def test_validate_bulk_operation(db_session, test_liability, test_accounts):
    service = BillSplitService(db_session)

    # Create bulk operation with one valid and one invalid split
    splits = [
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[0].id,
            amount=Decimal("100"),
        ),
        BillSplitCreate(
            liability_id=test_liability.id,
            account_id=test_accounts[1].id,
            amount=Decimal("2000"),  # Exceeds available balance
        ),
    ]

    operation = BulkSplitOperation(operation_type="create", splits=splits)

    # Validate without executing
    result = await service.validate_bulk_operation(operation)

    assert result.success is False
    assert result.processed_count == 2
    assert result.success_count == 1
    assert result.failure_count == 1
    assert len(result.errors) == 1
    assert "insufficient balance" in result.errors[0].error_message.lower()

    # Verify no splits were actually created
    total = await service.calculate_split_totals(test_liability.id)
    assert total == Decimal("0")


async def test_bulk_operation_transaction_rollback(
    db_session, test_liability, test_accounts
):
    service = BillSplitService(db_session)

    # Create bulk operation with invalid liability ID to trigger transaction error
    splits = [
        BillSplitCreate(
            liability_id=999999,  # Non-existent liability
            account_id=test_accounts[0].id,
            amount=Decimal("100"),
        )
    ]

    operation = BulkSplitOperation(operation_type="create", splits=splits)

    result = await service.process_bulk_operation(operation)

    assert result.success is False
    assert len(result.errors) == 1
    assert result.errors[0].error_type == "validation"

    # Verify no splits were created due to rollback
    total = await service.calculate_split_totals(test_liability.id)
    assert total == Decimal("0")
