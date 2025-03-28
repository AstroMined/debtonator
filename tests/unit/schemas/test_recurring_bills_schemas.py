from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.recurring_bills import (
    GenerateBillsRequest,
    RecurringBillBase,
    RecurringBillCreate,
    RecurringBillResponse,
    RecurringBillUpdate,
)


# Test valid object creation
def test_recurring_bill_base_valid():
    """Test valid recurring bill base schema"""
    data = RecurringBillBase(
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
        auto_pay=True,
    )

    assert data.bill_name == "Internet Service"
    assert data.amount == Decimal("89.99")
    assert data.day_of_month == 15
    assert data.account_id == 1
    assert data.category_id == 2
    assert data.auto_pay is True


def test_recurring_bill_base_minimal():
    """Test recurring bill base schema with minimal required fields"""
    data = RecurringBillBase(
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
    )

    assert data.bill_name == "Internet Service"
    assert data.amount == Decimal("89.99")
    assert data.day_of_month == 15
    assert data.account_id == 1
    assert data.category_id == 2
    assert data.auto_pay is False  # Default value


def test_recurring_bill_create_valid():
    """Test valid recurring bill create schema"""
    data = RecurringBillCreate(
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
        auto_pay=True,
    )

    assert data.bill_name == "Internet Service"
    assert data.amount == Decimal("89.99")
    assert data.day_of_month == 15
    assert data.account_id == 1
    assert data.category_id == 2
    assert data.auto_pay is True


def test_recurring_bill_update_valid():
    """Test valid recurring bill update schema with all fields"""
    data = RecurringBillUpdate(
        bill_name="Updated Internet Service",
        amount=Decimal("99.99"),
        day_of_month=20,
        account_id=2,
        category_id=3,
        auto_pay=False,
        active=False,
    )

    assert data.bill_name == "Updated Internet Service"
    assert data.amount == Decimal("99.99")
    assert data.day_of_month == 20
    assert data.account_id == 2
    assert data.category_id == 3
    assert data.auto_pay is False
    assert data.active is False


def test_recurring_bill_update_partial():
    """Test recurring bill update schema with partial fields"""
    # Update only amount
    data1 = RecurringBillUpdate(amount=Decimal("99.99"))
    assert data1.amount == Decimal("99.99")
    assert data1.bill_name is None
    assert data1.day_of_month is None
    assert data1.account_id is None
    assert data1.category_id is None
    assert data1.auto_pay is None
    assert data1.active is None

    # Update only active status
    data2 = RecurringBillUpdate(active=False)
    assert data2.amount is None
    assert data2.bill_name is None
    assert data2.day_of_month is None
    assert data2.account_id is None
    assert data2.category_id is None
    assert data2.auto_pay is None
    assert data2.active is False


def test_recurring_bill_response_valid():
    """Test valid recurring bill response schema"""
    now = datetime.now(timezone.utc)

    data = RecurringBillResponse(
        id=1,
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
        auto_pay=True,
        active=True,
        created_at=now,
        updated_at=now,
    )

    assert data.id == 1
    assert data.bill_name == "Internet Service"
    assert data.amount == Decimal("89.99")
    assert data.day_of_month == 15
    assert data.account_id == 1
    assert data.category_id == 2
    assert data.auto_pay is True
    assert data.active is True
    assert data.created_at == now
    assert data.updated_at == now


def test_generate_bills_request_valid():
    """Test valid generate bills request schema"""
    data = GenerateBillsRequest(month=3, year=2025)

    assert data.month == 3
    assert data.year == 2025


# Test field validations
def test_required_fields():
    """Test required fields"""
    # Test missing bill_name
    with pytest.raises(ValidationError, match="Field required"):
        RecurringBillBase(
            amount=Decimal("89.99"), day_of_month=15, account_id=1, category_id=2
        )

    # Test missing amount
    with pytest.raises(ValidationError, match="Field required"):
        RecurringBillBase(
            bill_name="Internet Service", day_of_month=15, account_id=1, category_id=2
        )

    # Test missing day_of_month
    with pytest.raises(ValidationError, match="Field required"):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            account_id=1,
            category_id=2,
        )

    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            day_of_month=15,
            category_id=2,
        )

    # Test missing category_id
    with pytest.raises(ValidationError, match="Field required"):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            day_of_month=15,
            account_id=1,
        )


def test_bill_name_length_validation():
    """Test bill_name length validation"""
    # Test empty bill_name
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        RecurringBillBase(
            bill_name="",  # Empty string
            amount=Decimal("89.99"),
            day_of_month=15,
            account_id=1,
            category_id=2,
        )

    # Test bill_name too long
    with pytest.raises(
        ValidationError, match="String should have at most 255 characters"
    ):
        RecurringBillBase(
            bill_name="X" * 256,  # 256 characters
            amount=Decimal("89.99"),
            day_of_month=15,
            account_id=1,
            category_id=2,
        )

    # Test valid bill_name boundaries
    data1 = RecurringBillBase(
        bill_name="X",  # 1 character
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
    )
    assert len(data1.bill_name) == 1

    data2 = RecurringBillBase(
        bill_name="X" * 255,  # 255 characters
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
    )
    assert len(data2.bill_name) == 255


def test_amount_validation():
    """Test amount validation"""
    # Test amount not greater than 0
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("0.00"),  # Not greater than 0
            day_of_month=15,
            account_id=1,
            category_id=2,
        )

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("-10.00"),  # Negative
            day_of_month=15,
            account_id=1,
            category_id=2,
        )

    # Test valid amount
    data = RecurringBillBase(
        bill_name="Internet Service",
        amount=Decimal("0.01"),  # Minimum valid amount
        day_of_month=15,
        account_id=1,
        category_id=2,
    )
    assert data.amount == Decimal("0.01")


def test_amount_precision_validation():
    """Test amount precision validation"""
    # Test amount with too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("89.995"),  # Too many decimal places
            day_of_month=15,
            account_id=1,
            category_id=2,
        )

    # Test amount with too many decimal places in update
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        RecurringBillUpdate(amount=Decimal("99.999"))  # Too many decimal places

    # Test valid amount precision
    data = RecurringBillBase(
        bill_name="Internet Service",
        amount=Decimal("89.99"),  # Valid precision
        day_of_month=15,
        account_id=1,
        category_id=2,
    )
    assert data.amount == Decimal("89.99")


def test_day_of_month_validation():
    """Test day_of_month validation"""
    # Test day_of_month less than 1
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 1"
    ):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            day_of_month=0,  # Less than minimum
            account_id=1,
            category_id=2,
        )

    # Test day_of_month greater than 31
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 31"
    ):
        RecurringBillBase(
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            day_of_month=32,  # Greater than maximum
            account_id=1,
            category_id=2,
        )

    # Test valid day_of_month boundaries
    data1 = RecurringBillBase(
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=1,  # Minimum valid
        account_id=1,
        category_id=2,
    )
    assert data1.day_of_month == 1

    data2 = RecurringBillBase(
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=31,  # Maximum valid
        account_id=1,
        category_id=2,
    )
    assert data2.day_of_month == 31


def test_id_field_validation():
    """Test ID field validations"""
    # These checks are not explicitly defined in the schema
    # but are a common convention in the codebase

    # Test update fields with invalid values
    # Fields should be None or valid values
    update_data = RecurringBillUpdate(
        bill_name="Updated Service", account_id=1, category_id=2
    )
    assert update_data.account_id == 1
    assert update_data.category_id == 2


def test_generate_bills_month_validation():
    """Test month validation in generate bills request"""
    # Test month less than 1
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 1"
    ):
        GenerateBillsRequest(month=0, year=2025)

    # Test month greater than 12
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 12"
    ):
        GenerateBillsRequest(month=13, year=2025)

    # Test valid month boundaries
    data1 = GenerateBillsRequest(month=1, year=2025)  # January
    assert data1.month == 1

    data2 = GenerateBillsRequest(month=12, year=2025)  # December
    assert data2.month == 12


def test_generate_bills_year_validation():
    """Test year validation in generate bills request"""
    # Test year less than 2000
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 2000"
    ):
        GenerateBillsRequest(month=3, year=1999)

    # Test year greater than 3000
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 3000"
    ):
        GenerateBillsRequest(month=3, year=3001)

    # Test valid year boundaries
    data1 = GenerateBillsRequest(month=3, year=2000)  # Minimum valid
    assert data1.year == 2000

    data2 = GenerateBillsRequest(month=3, year=3000)  # Maximum valid
    assert data2.year == 3000


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now_utc = datetime.now(timezone.utc)

    # Test naive datetime in created_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RecurringBillResponse(
            id=1,
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            day_of_month=15,
            account_id=1,
            category_id=2,
            auto_pay=True,
            active=True,
            created_at=datetime.now(),  # Naive datetime
            updated_at=now_utc,
        )

    # Test non-UTC timezone in updated_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        non_utc_tz = timezone(timedelta(hours=5))
        RecurringBillResponse(
            id=1,
            bill_name="Internet Service",
            amount=Decimal("89.99"),
            day_of_month=15,
            account_id=1,
            category_id=2,
            auto_pay=True,
            active=True,
            created_at=now_utc,
            updated_at=datetime.now().replace(tzinfo=non_utc_tz),  # Non-UTC timezone
        )

    # Test valid UTC datetimes
    data = RecurringBillResponse(
        id=1,
        bill_name="Internet Service",
        amount=Decimal("89.99"),
        day_of_month=15,
        account_id=1,
        category_id=2,
        auto_pay=True,
        active=True,
        created_at=now_utc,
        updated_at=now_utc,
    )
    # Verify the datetime fields are the same as what we provided (with UTC timezone)
    assert data.created_at == now_utc
    assert data.updated_at == now_utc
