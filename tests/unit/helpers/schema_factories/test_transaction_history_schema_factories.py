"""
Unit tests for transaction history schema factory functions.

Tests ensure that transaction history schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime
from decimal import Decimal

from src.schemas.transaction_history import (
    TransactionHistoryCreate,
    TransactionHistoryInDB,
    TransactionHistoryList,
    TransactionHistoryUpdate,
)
from src.utils.datetime_utils import utc_datetime
from tests.helpers.schema_factories.transaction_history_schema_factories import (
    create_transaction_history_in_db_schema,
    create_transaction_history_list_schema,
    create_transaction_history_schema,
    create_transaction_history_update_schema,
)


def test_create_transaction_history_schema():
    """Test creating a TransactionHistoryCreate schema with default values."""
    schema = create_transaction_history_schema(account_id=1)

    assert isinstance(schema, TransactionHistoryCreate)
    assert schema.account_id == 1
    assert schema.amount == Decimal("100.00")
    assert schema.description == "Test Transaction"
    assert schema.transaction_type == "debit"
    # reference_id and reference_type fields don't exist in the schema
    assert isinstance(schema.transaction_date, datetime)


def test_create_transaction_history_schema_with_custom_values():
    """Test creating a TransactionHistoryCreate schema with custom values."""
    transaction_date = utc_datetime(2023, 7, 15)

    schema = create_transaction_history_schema(
        account_id=2,
        transaction_date=transaction_date,
        amount=Decimal("250.75"),
        description="Salary Deposit",
        transaction_type="credit",
        # reference_id and reference_type fields don't exist in the schema
    )

    assert isinstance(schema, TransactionHistoryCreate)
    assert schema.account_id == 2
    assert schema.transaction_date == transaction_date
    assert schema.amount == Decimal("250.75")
    assert schema.description == "Salary Deposit"
    assert schema.transaction_type == "credit"


def test_create_transaction_history_in_db_schema():
    """Test creating a TransactionHistoryInDB schema with default values."""
    schema = create_transaction_history_in_db_schema(id=1, account_id=3)

    assert isinstance(schema, TransactionHistoryInDB)
    assert schema.id == 1
    assert schema.account_id == 3
    assert schema.amount == Decimal("100.00")
    assert schema.description == "Test Transaction"
    assert schema.transaction_type == "debit"
    assert isinstance(schema.transaction_date, datetime)
    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)


def test_create_transaction_history_in_db_schema_with_custom_values():
    """Test creating a TransactionHistoryInDB schema with custom values."""
    transaction_date = utc_datetime(2023, 8, 10)
    created_at = utc_datetime(2023, 8, 10, 12, 0)
    updated_at = utc_datetime(2023, 8, 11, 9, 30)

    schema = create_transaction_history_in_db_schema(
        id=2,
        account_id=4,
        transaction_date=transaction_date,
        amount=Decimal("500.00"),
        description="Rent Payment",
        transaction_type="debit",
        created_at=created_at,
        updated_at=updated_at,
    )

    assert isinstance(schema, TransactionHistoryInDB)
    assert schema.id == 2
    assert schema.account_id == 4
    assert schema.transaction_date == transaction_date
    assert schema.amount == Decimal("500.00")
    assert schema.description == "Rent Payment"
    assert schema.transaction_type == "debit"
    assert schema.created_at == created_at
    assert schema.updated_at == updated_at


def test_create_transaction_history_list_schema():
    """Test creating a TransactionHistoryList schema with default values."""
    schema = create_transaction_history_list_schema()

    assert isinstance(schema, TransactionHistoryList)
    assert len(schema.items) == 2
    assert schema.total == 2

    # Check that the default items were created correctly
    assert schema.items[0].id == 1
    assert schema.items[0].transaction_type == "debit"
    assert schema.items[1].id == 2
    assert schema.items[1].transaction_type == "credit"
    assert schema.items[1].description == "Deposit"


def test_create_transaction_history_list_schema_with_custom_items():
    """Test creating a TransactionHistoryList schema with custom items."""
    custom_items = [
        create_transaction_history_in_db_schema(
            id=3, account_id=5, amount=Decimal("100.00"), description="Grocery Shopping"
        ),
        create_transaction_history_in_db_schema(
            id=4,
            account_id=5,
            amount=Decimal("1200.00"),
            description="Monthly Salary",
            transaction_type="credit",
        ),
        create_transaction_history_in_db_schema(
            id=5, account_id=5, amount=Decimal("50.00"), description="Internet Bill"
        ),
    ]

    schema = create_transaction_history_list_schema(
        items=custom_items,
        total=15,  # Total available transactions could be more than the page
    )

    assert isinstance(schema, TransactionHistoryList)
    assert len(schema.items) == 3
    assert schema.total == 15

    # Check our custom items are in the list
    assert schema.items[0].id == 3
    assert schema.items[0].description == "Grocery Shopping"
    assert schema.items[1].id == 4
    assert schema.items[1].description == "Monthly Salary"
    assert schema.items[2].id == 5
    assert schema.items[2].description == "Internet Bill"


def test_create_transaction_history_update_schema_empty():
    """Test creating a TransactionHistoryUpdate schema with no specified values."""
    schema = create_transaction_history_update_schema(id=6)

    assert isinstance(schema, TransactionHistoryUpdate)
    assert schema.amount is None
    assert schema.description is None
    assert schema.transaction_date is None


def test_create_transaction_history_update_schema_with_values():
    """Test creating a TransactionHistoryUpdate schema with specified values."""
    transaction_date = utc_datetime(2023, 9, 1)

    schema = create_transaction_history_update_schema(
        id=7,
        amount=Decimal("125.50"),
        description="Updated Transaction Description",
        transaction_date=transaction_date,
    )

    assert isinstance(schema, TransactionHistoryUpdate)
    assert schema.amount == Decimal("125.50")
    assert schema.description == "Updated Transaction Description"
    assert schema.transaction_date == transaction_date
