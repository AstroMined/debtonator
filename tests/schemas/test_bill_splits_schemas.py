from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

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
    BulkOperationError,
    BulkOperationResult,
    BulkSplitOperation,
    HistoricalAnalysis,
    ImpactAnalysis,
    OptimizationMetrics,
    OptimizationSuggestion,
    PatternMetrics,
    SplitPattern,
    SplitSuggestion,
)


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
    now = datetime.now(ZoneInfo("UTC"))

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
    now = datetime.now(ZoneInfo("UTC"))

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
        confidence_score=0.85,
        reason="Based on historical patterns",
    )

    assert data.account_id == 1
    assert data.amount == Decimal("75.50")
    assert data.confidence_score == 0.85
    assert data.reason == "Based on historical patterns"


def test_bill_split_suggestion_response_valid():
    """Test valid bill split suggestion response schema"""
    suggestions = [
        SplitSuggestion(
            account_id=1,
            amount=Decimal("75.00"),
            confidence_score=0.85,
            reason="Primary account",
        ),
        SplitSuggestion(
            account_id=2,
            amount=Decimal("25.00"),
            confidence_score=0.75,
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
    """Test decimal precision validation"""
    # Test too many decimal places
    with pytest.raises(
        ValidationError, match="Decimal input should have no more than 2 decimal places"
    ):
        BillSplitBase(amount=Decimal("100.123"))

    # Test valid decimal places
    data = BillSplitBase(amount=Decimal("100.12"))
    assert data.amount == Decimal("100.12")


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        BillSplitInDB(
            id=1,
            liability_id=2,
            account_id=3,
            amount=Decimal("100.00"),
            created_at=datetime.now(),  # Naive datetime
            updated_at=datetime.now(ZoneInfo("UTC")),
        )

    # Test non-UTC timezone
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        BillSplitInDB(
            id=1,
            liability_id=2,
            account_id=3,
            amount=Decimal("100.00"),
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )


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
    with pytest.raises(ValidationError, match="Input should have at least 1 item"):
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
            confidence_score=-0.1,
            reason="Based on historical patterns",
        )

    # Test confidence score > 1
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        SplitSuggestion(
            account_id=1,
            amount=Decimal("75.50"),
            confidence_score=1.1,
            reason="Based on historical patterns",
        )

    # Test valid boundary values
    data1 = SplitSuggestion(
        account_id=1,
        amount=Decimal("75.50"),
        confidence_score=0,
        reason="Based on historical patterns",
    )
    assert data1.confidence_score == 0

    data2 = SplitSuggestion(
        account_id=1,
        amount=Decimal("75.50"),
        confidence_score=1,
        reason="Based on historical patterns",
    )
    assert data2.confidence_score == 1


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
