from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.bill_splits import (
    BillSplitBase,
    BillSplitCreate,
    BillSplitInDB,
    BillSplitResponse,
    BillSplitSuggestionResponse,
    BillSplitUpdate,
    BillSplitValidation,
    BulkOperationResult,
    BulkSplitOperation,
    SplitPattern,
    SplitSuggestion,
)
from src.utils.datetime_utils import utc_now


# Test valid object creation
def test_bill_split_base_valid():
    """Test valid bill split base schema"""
    data = BillSplitBase(amount=Decimal("100.00"))
    assert data.amount == Decimal("100.00")


def test_bill_split_create_valid():
    """Test valid bill split create schema"""
    data = BillSplitCreate(amount=Decimal("100.00"), liability_id=1, account_id=2)

    assert data.amount == Decimal("100.00")
    assert data.liability_id == 1
    assert data.account_id == 2


def test_bill_split_update_valid():
    """Test valid bill split update schema"""
    data = BillSplitUpdate(id=1, amount=Decimal("150.00"))

    assert data.id == 1
    assert data.amount == Decimal("150.00")


def test_bill_split_in_db_valid():
    """Test valid bill split in DB schema"""
    now = datetime.now(timezone.utc)

    data = BillSplitInDB(
        id=1,
        liability_id=2,
        account_id=3,
        amount=Decimal("100.00"),
        created_at=now,
        updated_at=now,
    )

    assert data.id == 1
    assert data.liability_id == 2
    assert data.account_id == 3
    assert data.amount == Decimal("100.00")
    assert data.created_at == now
    assert data.updated_at == now


def test_bill_split_response_valid():
    """Test valid bill split response schema"""
    now = datetime.now(timezone.utc)

    data = BillSplitResponse(
        id=1,
        liability_id=2,
        account_id=3,
        amount=Decimal("100.00"),
        created_at=now,
        updated_at=now,
    )

    assert data.id == 1
    assert data.liability_id == 2
    assert data.account_id == 3
    assert data.amount == Decimal("100.00")
    assert data.created_at == now
    assert data.updated_at == now


def test_split_suggestion_valid():
    """Test valid split suggestion schema"""
    data = SplitSuggestion(
        account_id=1,
        amount=Decimal("75.50"),
        confidence_score=Decimal("0.85"),
        reason="Based on historical patterns",
    )

    assert data.account_id == 1
    assert data.amount == Decimal("75.50")
    assert data.confidence_score == Decimal("0.85")
    assert data.reason == "Based on historical patterns"


def test_bill_split_suggestion_response_valid():
    """Test valid bill split suggestion response schema"""
    suggestions = [
        SplitSuggestion(
            account_id=1,
            amount=Decimal("75.00"),
            confidence_score=Decimal("0.85"),
            reason="Primary account",
        ),
        SplitSuggestion(
            account_id=2,
            amount=Decimal("25.00"),
            confidence_score=Decimal("0.75"),
            reason="Secondary account",
        ),
    ]

    data = BillSplitSuggestionResponse(
        liability_id=1,
        total_amount=Decimal("100.00"),
        suggestions=suggestions,
        historical_pattern=True,
        pattern_frequency=5,
    )

    assert data.liability_id == 1
    assert data.total_amount == Decimal("100.00")
    assert len(data.suggestions) == 2
    assert data.suggestions[0].account_id == 1
    assert data.suggestions[0].amount == Decimal("75.00")
    assert data.historical_pattern is True
    assert data.pattern_frequency == 5


def test_bulk_operation_valid():
    """Test valid bulk operation schema"""
    splits = [
        BillSplitCreate(amount=Decimal("50.00"), liability_id=1, account_id=2),
        BillSplitCreate(amount=Decimal("75.00"), liability_id=1, account_id=3),
    ]

    data = BulkSplitOperation(
        operation_type="create", splits=splits, validate_only=True
    )

    assert data.operation_type == "create"
    assert len(data.splits) == 2
    assert data.validate_only is True
    assert data.splits[0].amount == Decimal("50.00")
    assert data.splits[1].amount == Decimal("75.00")


# Test field validations
def test_amount_gt_zero():
    """Test amount must be greater than zero"""
    # Test zero amount
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BillSplitBase(amount=Decimal("0.00"))

    # Test negative amount
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BillSplitBase(amount=Decimal("-10.00"))

    # Test valid positive amount
    data = BillSplitBase(amount=Decimal("0.01"))
    assert data.amount == Decimal("0.01")


def test_ids_validation():
    """Test ID fields validation"""
    # Test IDs must be greater than zero
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BillSplitCreate(amount=Decimal("100.00"), liability_id=0, account_id=1)

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BillSplitCreate(amount=Decimal("100.00"), liability_id=1, account_id=0)

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BillSplitUpdate(id=0, amount=Decimal("100.00"))


def test_required_fields():
    """Test required fields"""
    # Test missing amount
    with pytest.raises(ValidationError, match="Field required"):
        BillSplitBase()

    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        BillSplitCreate(amount=Decimal("100.00"), liability_id=1)

    # Test missing liability_id
    with pytest.raises(ValidationError, match="Field required"):
        BillSplitCreate(amount=Decimal("100.00"), account_id=1)

    # Test missing id
    with pytest.raises(ValidationError, match="Field required"):
        BillSplitUpdate(amount=Decimal("100.00"))


# Test decimal precision
def test_decimal_precision():
    """Test decimal precision validation for monetary fields"""
    # Test too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        BillSplitBase(amount=Decimal("100.123"))

    # Test valid decimal places (2 decimals)
    data = BillSplitBase(amount=Decimal("100.12"))
    assert data.amount == Decimal("100.12")

    # Test valid decimal places (1 decimal)
    data = BillSplitBase(amount=Decimal("100.1"))
    assert data.amount == Decimal("100.1")

    # Test valid decimal places (0 decimals)
    data = BillSplitBase(amount=Decimal("100"))
    assert data.amount == Decimal("100")

    # Test valid decimal places with trailing zeros
    data = BillSplitBase(amount=Decimal("100.10"))
    assert data.amount == Decimal("100.10")


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        BillSplitInDB(
            id=1,
            liability_id=2,
            account_id=3,
            amount=Decimal("100.00"),
            created_at=datetime.now(),  # Naive datetime
            updated_at=datetime.now(timezone.utc),
        )

    # Test non-UTC timezone
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        BillSplitInDB(
            id=1,
            liability_id=2,
            account_id=3,
            amount=Decimal("100.00"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )

    # Test with datetime_utils functions
    now = utc_now()
    data = BillSplitInDB(
        id=1,
        liability_id=2,
        account_id=3,
        amount=Decimal("100.00"),
        created_at=now,
        updated_at=now,
    )
    assert data.created_at == now
    assert data.updated_at == now


# Test custom validators
def test_bill_split_validation():
    """Test bill split validation with total amount"""
    # Create splits with correct total
    splits = [
        BillSplitCreate(amount=Decimal("60.00"), liability_id=1, account_id=2),
        BillSplitCreate(amount=Decimal("40.00"), liability_id=1, account_id=3),
    ]

    # Test valid splits (sum equals total)
    data = BillSplitValidation(
        liability_id=1, total_amount=Decimal("100.00"), splits=splits
    )
    assert data.liability_id == 1
    assert data.total_amount == Decimal("100.00")
    assert len(data.splits) == 2

    # Test invalid splits (sum doesn't equal total)
    splits[1].amount = Decimal("45.00")  # Now totals 105.00
    with pytest.raises(
        ValidationError, match="Sum of splits .* must equal total amount"
    ):
        BillSplitValidation(
            liability_id=1, total_amount=Decimal("100.00"), splits=splits
        )

    # Test empty splits
    with pytest.raises(ValidationError, match="At least one split is required"):
        BillSplitValidation(liability_id=1, total_amount=Decimal("100.00"), splits=[])

    # Test split validation with epsilon tolerance
    # Sum within 0.01 of total should be acceptable
    splits = [
        BillSplitCreate(amount=Decimal("33.33"), liability_id=1, account_id=2),
        BillSplitCreate(amount=Decimal("33.33"), liability_id=1, account_id=3),
        BillSplitCreate(amount=Decimal("33.33"), liability_id=1, account_id=4),
    ]
    # Total is 99.99, which is within epsilon (0.01) of 100.00
    data = BillSplitValidation(
        liability_id=1, total_amount=Decimal("100.00"), splits=splits
    )
    assert data.liability_id == 1
    assert sum(split.amount for split in data.splits) == Decimal("99.99")

    # Test the "$100 split three ways" case specifically
    splits = [
        BillSplitCreate(amount=Decimal("33.34"), liability_id=1, account_id=2),
        BillSplitCreate(amount=Decimal("33.33"), liability_id=1, account_id=3),
        BillSplitCreate(amount=Decimal("33.33"), liability_id=1, account_id=4),
    ]
    data = BillSplitValidation(
        liability_id=1, total_amount=Decimal("100.00"), splits=splits
    )
    assert data.liability_id == 1
    assert sum(split.amount for split in data.splits) == Decimal("100.00")


def test_bill_split_create_validator():
    """Test bill split create with negative amount validation (line 51)."""
    # Test the validate_amount model validator in BillSplitCreate
    # First create a valid object that passes validation
    valid_split = BillSplitCreate(
        amount=Decimal("100.00"), liability_id=1, account_id=1
    )
    assert valid_split.amount == Decimal("100.00")

    # Test zero amount - directly test the validator method
    model = BillSplitCreate(amount=Decimal("100.00"), liability_id=1, account_id=1)
    # Manually set the amount to 0 and call the validator
    object.__setattr__(model, "amount", Decimal("0"))

    # Directly call the validator method to test its behavior
    with pytest.raises(ValueError, match="Split amount must be greater than 0"):
        model.validate_amount()

    # Test negative amount
    model_neg = BillSplitCreate(amount=Decimal("100.00"), liability_id=1, account_id=1)
    # Manually set the amount to -10 and call the validator
    object.__setattr__(model_neg, "amount", Decimal("-10.00"))

    # Directly call the validator method to test its behavior
    with pytest.raises(ValueError, match="Split amount must be greater than 0"):
        model_neg.validate_amount()


def test_bulk_operation_validator():
    """Test BulkSplitOperation validators thoroughly (lines 332, 335->341, 337->341)."""
    # Test the validate_operation model validator
    validator = BulkSplitOperation.validate_operation

    # Test empty splits list validation (line 332)
    test_instance = BulkSplitOperation(
        operation_type="create",
        splits=[BillSplitCreate(amount=Decimal("50.00"), liability_id=1, account_id=2)],
    )

    # Manually set the splits to empty to test the validation
    object.__setattr__(test_instance, "splits", [])

    # This should trigger the validation on line 332
    with pytest.raises(ValueError, match="At least one split is required"):
        validator(test_instance)

    # Test mixed types for create operation (lines 335-336)
    mixed_splits = [
        BillSplitCreate(amount=Decimal("50.00"), liability_id=1, account_id=2),
        BillSplitUpdate(id=1, amount=Decimal("75.00")),
    ]

    test_instance = BulkSplitOperation(
        operation_type="create",
        splits=[BillSplitCreate(amount=Decimal("50.00"), liability_id=1, account_id=2)],
    )

    # Set mixed split list to trigger validation
    object.__setattr__(test_instance, "splits", mixed_splits)

    # This should trigger the validation on lines 335-336
    with pytest.raises(
        ValueError, match="Create operation requires BillSplitCreate instances"
    ):
        validator(test_instance)

    # Test mixed types for update operation (lines 337-341)
    test_instance = BulkSplitOperation(
        operation_type="update", splits=[BillSplitUpdate(id=1, amount=Decimal("75.00"))]
    )

    # Set mixed split list to trigger validation
    object.__setattr__(test_instance, "splits", mixed_splits)

    # This should trigger the validation on lines 337-341
    with pytest.raises(
        ValueError, match="Update operation requires BillSplitUpdate instances"
    ):
        validator(test_instance)

    # Test with all create instances for update operation - this covers the branch
    # where the first condition in line 337 is true but the second condition is false
    create_only_splits = [
        BillSplitCreate(amount=Decimal("50.00"), liability_id=1, account_id=2),
        BillSplitCreate(amount=Decimal("75.00"), liability_id=1, account_id=3),
    ]

    test_instance = BulkSplitOperation(
        operation_type="update", splits=[BillSplitUpdate(id=1, amount=Decimal("75.00"))]
    )

    # Set create-only split list to trigger validation for update operation
    object.__setattr__(test_instance, "splits", create_only_splits)

    # This should trigger the validation on lines 337-341 in a different way
    with pytest.raises(
        ValueError, match="Update operation requires BillSplitUpdate instances"
    ):
        validator(test_instance)


def test_bulk_operation_validation():
    """Test bulk operation validation"""
    # Test create operation with update models
    update_splits = [
        BillSplitUpdate(id=1, amount=Decimal("50.00")),
        BillSplitUpdate(id=2, amount=Decimal("75.00")),
    ]

    with pytest.raises(
        ValidationError, match="Create operation requires BillSplitCreate instances"
    ):
        BulkSplitOperation(operation_type="create", splits=update_splits)

    # Test update operation with create models
    create_splits = [
        BillSplitCreate(amount=Decimal("50.00"), liability_id=1, account_id=2),
        BillSplitCreate(amount=Decimal("75.00"), liability_id=1, account_id=3),
    ]

    with pytest.raises(
        ValidationError, match="Update operation requires BillSplitUpdate instances"
    ):
        BulkSplitOperation(operation_type="update", splits=create_splits)

    # Test invalid operation type
    with pytest.raises(ValidationError, match="String should match pattern"):
        BulkSplitOperation(operation_type="invalid", splits=create_splits)

    # Test empty splits
    with pytest.raises(ValidationError, match="List should have at least 1 item"):
        BulkSplitOperation(operation_type="create", splits=[])


def test_confidence_score_validation():
    """Test confidence score range validation"""
    # Test confidence score < 0
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        SplitSuggestion(
            account_id=1,
            amount=Decimal("75.50"),
            confidence_score=Decimal("-0.1"),
            reason="Based on historical patterns",
        )

    # Test confidence score > 1
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        SplitSuggestion(
            account_id=1,
            amount=Decimal("75.50"),
            confidence_score=Decimal("1.1"),
            reason="Based on historical patterns",
        )

    # Test valid boundary values
    data1 = SplitSuggestion(
        account_id=1,
        amount=Decimal("75.50"),
        confidence_score=Decimal("0"),
        reason="Based on historical patterns",
    )
    assert data1.confidence_score == Decimal("0")

    data2 = SplitSuggestion(
        account_id=1,
        amount=Decimal("75.50"),
        confidence_score=Decimal("1"),
        reason="Based on historical patterns",
    )
    assert data2.confidence_score == Decimal("1")

    # Test with 4 decimal places (should pass for percentage field)
    data3 = SplitSuggestion(
        account_id=1,
        amount=Decimal("75.50"),
        confidence_score=Decimal("0.1234"),
        reason="Based on historical patterns",
    )
    assert data3.confidence_score == Decimal("0.1234")


def test_bulk_operation_result_validation():
    """Test bulk operation result validation"""
    # Test valid result
    data = BulkOperationResult(
        success=True,
        processed_count=5,
        success_count=3,
        failure_count=2,
        successful_splits=[],
        errors=[],
    )
    assert data.success is True
    assert data.processed_count == 5
    assert data.success_count == 3
    assert data.failure_count == 2

    # Test invalid counts
    with pytest.raises(
        ValidationError,
        match="Failure count must equal processed count minus success count",
    ):
        BulkOperationResult(
            success=True,
            processed_count=5,
            success_count=3,
            failure_count=3,  # Should be 2
            successful_splits=[],
            errors=[],
        )


def test_reason_length_validation():
    """Test reason length validation"""
    # Test reason too long
    with pytest.raises(
        ValidationError, match="String should have at most 500 characters"
    ):
        SplitSuggestion(
            account_id=1,
            amount=Decimal("75.50"),
            confidence_score=0.85,
            reason="X" * 501,
        )

    # Test valid reason length
    data = SplitSuggestion(
        account_id=1, amount=Decimal("75.50"), confidence_score=0.85, reason="X" * 500
    )
    assert len(data.reason) == 500


def test_percentage_field_precision():
    """Test precision validation for percentage fields"""
    # Test valid precision for percentage fields (4 decimal places)
    pattern = SplitPattern(
        pattern_id="test",
        account_splits={1: Decimal("0.3333"), 2: Decimal("0.6667")},
        total_occurrences=10,
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
        average_total=Decimal("100.00"),
        confidence_score=Decimal("0.8765"),
    )
    assert pattern.account_splits[1] == Decimal("0.3333")
    assert pattern.account_splits[2] == Decimal("0.6667")

    # Test with different precision formats for percentage fields
    pattern = SplitPattern(
        pattern_id="test",
        account_splits={
            1: Decimal("0.5"),  # 1 decimal place
            2: Decimal("0.25"),  # 2 decimal places
            3: Decimal("0.125"),  # 3 decimal places
            4: Decimal("0.0625"),  # 4 decimal places
        },
        total_occurrences=10,
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
        average_total=Decimal("100.00"),
        confidence_score=Decimal("0.8765"),
    )
    assert pattern.account_splits[1] == Decimal("0.5")
    assert pattern.account_splits[2] == Decimal("0.25")
    assert pattern.account_splits[3] == Decimal("0.125")
    assert pattern.account_splits[4] == Decimal("0.0625")

    # Test with too many decimal places for percentage fields (5 decimal places)
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        SplitPattern(
            pattern_id="test",
            account_splits={1: Decimal("0.33333")},  # 5 decimal places
            total_occurrences=10,
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            average_total=Decimal("100.00"),
            confidence_score=Decimal("0.8765"),
        )
