"""
Unit tests for bill splits schema factory functions.

Tests ensure that bill splits schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime
from decimal import Decimal

from src.schemas.bill_splits import (
    BillSplitCreate,
    BillSplitInDB,
    BillSplitResponse,
    BillSplitUpdate,
    BillSplitValidation,
    BulkOperationResult,
    BulkSplitOperation,
    HistoricalAnalysis,
    ImpactAnalysis,
    OptimizationMetrics,
    PatternMetrics,
    SplitPattern,
    SplitSuggestion,
)
from src.utils.datetime_utils import utc_datetime
from tests.helpers.schema_factories.bill_splits_schema_factories import (
    create_bill_split_in_db_schema,
    create_bill_split_response_schema,
    create_bill_split_schema,
    create_bill_split_update_schema,
    create_bill_split_validation_schema,
    create_bulk_operation_result_schema,
    create_bulk_split_operation_schema,
    create_historical_analysis_schema,
    create_impact_analysis_schema,
    create_optimization_metrics_schema,
    create_pattern_metrics_schema,
    create_split_pattern_schema,
    create_split_suggestion_schema,
)


def test_create_bill_split_schema():
    """Test creating a BillSplitCreate schema with default values."""
    schema = create_bill_split_schema(liability_id=1, account_id=2)

    assert isinstance(schema, BillSplitCreate)
    assert schema.liability_id == 1
    assert schema.account_id == 2
    assert schema.amount == Decimal("100.00")


def test_create_bill_split_schema_with_custom_values():
    """Test creating a BillSplitCreate schema with custom values."""
    schema = create_bill_split_schema(
        liability_id=3, account_id=4, amount=Decimal("250.50")
    )

    assert isinstance(schema, BillSplitCreate)
    assert schema.liability_id == 3
    assert schema.account_id == 4
    assert schema.amount == Decimal("250.50")


def test_create_bill_split_update_schema():
    """Test creating a BillSplitUpdate schema with default values."""
    schema = create_bill_split_update_schema(id=5)

    assert isinstance(schema, BillSplitUpdate)
    assert schema.id == 5
    assert schema.amount == Decimal("150.00")


def test_create_bill_split_update_schema_with_custom_values():
    """Test creating a BillSplitUpdate schema with custom values."""
    schema = create_bill_split_update_schema(id=6, amount=Decimal("300.75"))

    assert isinstance(schema, BillSplitUpdate)
    assert schema.id == 6
    assert schema.amount == Decimal("300.75")


def test_create_bill_split_in_db_schema():
    """Test creating a BillSplitInDB schema with default values."""
    schema = create_bill_split_in_db_schema(id=7, liability_id=8, account_id=9)

    assert isinstance(schema, BillSplitInDB)
    assert schema.id == 7
    assert schema.liability_id == 8
    assert schema.account_id == 9
    assert schema.amount == Decimal("100.00")
    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)


def test_create_bill_split_in_db_schema_with_custom_values():
    """Test creating a BillSplitInDB schema with custom values."""
    created_at = utc_datetime(2023, 1, 15, 12, 0, 0)
    updated_at = utc_datetime(2023, 1, 20, 14, 30, 0)

    schema = create_bill_split_in_db_schema(
        id=10,
        liability_id=11,
        account_id=12,
        amount=Decimal("175.25"),
        created_at=created_at,
        updated_at=updated_at,
    )

    assert isinstance(schema, BillSplitInDB)
    assert schema.id == 10
    assert schema.liability_id == 11
    assert schema.account_id == 12
    assert schema.amount == Decimal("175.25")
    assert schema.created_at == created_at
    assert schema.updated_at == updated_at


def test_create_bill_split_response_schema():
    """Test creating a BillSplitResponse schema with default values."""
    schema = create_bill_split_response_schema(id=13, liability_id=14, account_id=15)

    assert isinstance(schema, BillSplitResponse)
    assert schema.id == 13
    assert schema.liability_id == 14
    assert schema.account_id == 15
    assert schema.amount == Decimal("100.00")
    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)


def test_create_bill_split_validation_schema():
    """Test creating a BillSplitValidation schema with default values."""
    schema = create_bill_split_validation_schema(liability_id=16)

    assert isinstance(schema, BillSplitValidation)
    assert schema.liability_id == 16
    assert schema.total_amount == Decimal("300.00")
    assert len(schema.splits) == 3

    # Check that the splits sum to the total amount
    split_sum = sum(split.amount for split in schema.splits)
    assert split_sum == Decimal("300.00")

    # Check that the liability_id matches in all splits
    for split in schema.splits:
        assert split.liability_id == 16


def test_create_bill_split_validation_schema_with_custom_values():
    """Test creating a BillSplitValidation schema with custom values."""
    custom_splits = [
        create_bill_split_schema(
            liability_id=17, account_id=18, amount=Decimal("200.00")
        ),
        create_bill_split_schema(
            liability_id=17, account_id=19, amount=Decimal("150.00")
        ),
    ]

    schema = create_bill_split_validation_schema(
        liability_id=17, total_amount=Decimal("350.00"), splits=custom_splits
    )

    assert isinstance(schema, BillSplitValidation)
    assert schema.liability_id == 17
    assert schema.total_amount == Decimal("350.00")
    assert len(schema.splits) == 2

    # Check that the splits match our custom splits
    assert schema.splits[0].account_id == 18
    assert schema.splits[0].amount == Decimal("200.00")
    assert schema.splits[1].account_id == 19
    assert schema.splits[1].amount == Decimal("150.00")


def test_create_split_suggestion_schema():
    """Test creating a SplitSuggestion schema with default values."""
    schema = create_split_suggestion_schema(account_id=20)

    assert isinstance(schema, SplitSuggestion)
    assert schema.account_id == 20
    assert schema.amount == Decimal("100.00")
    assert schema.confidence_score == Decimal("0.75")
    assert schema.reason == "Based on historical split patterns"


def test_create_split_suggestion_schema_with_custom_values():
    """Test creating a SplitSuggestion schema with custom values."""
    schema = create_split_suggestion_schema(
        account_id=21,
        amount=Decimal("275.50"),
        confidence_score=Decimal("0.90"),
        reason="Based on recent payment history",
    )

    assert isinstance(schema, SplitSuggestion)
    assert schema.account_id == 21
    assert schema.amount == Decimal("275.50")
    assert schema.confidence_score == Decimal("0.90")
    assert schema.reason == "Based on recent payment history"


def test_create_split_pattern_schema():
    """Test creating a SplitPattern schema with default values."""
    schema = create_split_pattern_schema()

    assert isinstance(schema, SplitPattern)
    assert schema.pattern_id == "pattern-001"
    assert schema.total_occurrences == 5
    assert schema.average_total == Decimal("300.00")
    assert schema.confidence_score == Decimal("0.85")

    # Check account splits
    assert len(schema.account_splits) == 3
    assert schema.account_splits[1] == Decimal("0.5")
    assert schema.account_splits[2] == Decimal("0.3")
    assert schema.account_splits[3] == Decimal("0.2")


def test_create_pattern_metrics_schema():
    """Test creating a PatternMetrics schema with default values."""
    schema = create_pattern_metrics_schema()

    assert isinstance(schema, PatternMetrics)
    assert schema.total_splits == 25
    assert schema.unique_patterns == 3
    assert schema.average_splits_per_bill == 2.5

    # Check account usage
    assert len(schema.account_usage_frequency) == 3
    assert schema.account_usage_frequency[1] == 20
    assert schema.account_usage_frequency[2] == 15
    assert schema.account_usage_frequency[3] == 10

    # Check most common pattern
    assert schema.most_common_pattern is not None
    assert schema.most_common_pattern.total_occurrences == 15


def test_create_optimization_metrics_schema():
    """Test creating an OptimizationMetrics schema with default values."""
    schema = create_optimization_metrics_schema()

    assert isinstance(schema, OptimizationMetrics)
    assert schema.risk_score == Decimal("0.35")
    assert schema.optimization_score == Decimal("0.7")

    # Check credit utilization
    assert len(schema.credit_utilization) == 2
    assert schema.credit_utilization[1] == Decimal("0.4")
    assert schema.credit_utilization[2] == Decimal("0.25")

    # Check balance impact
    assert len(schema.balance_impact) == 3
    assert schema.balance_impact[1] == Decimal("-150.00")
    assert schema.balance_impact[2] == Decimal("-100.00")
    assert schema.balance_impact[3] == Decimal("-50.00")


def test_create_impact_analysis_schema():
    """Test creating an ImpactAnalysis schema with default values."""
    schema = create_impact_analysis_schema()

    assert isinstance(schema, ImpactAnalysis)
    assert len(schema.split_configuration) == 3
    assert isinstance(schema.metrics, OptimizationMetrics)

    # Check short-term impact
    assert len(schema.short_term_impact) == 3
    assert schema.short_term_impact[1] == Decimal("-150.00")

    # Check risk factors and recommendations
    assert len(schema.risk_factors) == 2
    assert len(schema.recommendations) == 3


def test_create_historical_analysis_schema():
    """Test creating a HistoricalAnalysis schema with default values."""
    schema = create_historical_analysis_schema()

    assert isinstance(schema, HistoricalAnalysis)
    assert schema.liability_id == 1
    assert isinstance(schema.analysis_date, datetime)

    # Check patterns and metrics
    assert len(schema.patterns) == 3
    assert isinstance(schema.metrics, PatternMetrics)

    # Check category patterns
    assert len(schema.category_patterns) == 2
    assert isinstance(schema.category_patterns[1][0], SplitPattern)

    # Check seasonal patterns
    assert len(schema.seasonal_patterns) == 3
    assert "winter" in schema.seasonal_patterns
    assert "summer" in schema.seasonal_patterns
    assert "holiday" in schema.seasonal_patterns

    # Check impact analysis
    assert isinstance(schema.impact_analysis, ImpactAnalysis)


def test_create_bulk_split_operation_schema_create():
    """Test creating a BulkSplitOperation schema for create operation."""
    schema = create_bulk_split_operation_schema(operation_type="create")

    assert isinstance(schema, BulkSplitOperation)
    assert schema.operation_type == "create"
    assert len(schema.splits) == 3
    assert schema.validate_only is False

    # Check that all splits are BillSplitCreate instances
    for split in schema.splits:
        assert isinstance(split, BillSplitCreate)


def test_create_bulk_split_operation_schema_update():
    """Test creating a BulkSplitOperation schema for update operation."""
    schema = create_bulk_split_operation_schema(operation_type="update")

    assert isinstance(schema, BulkSplitOperation)
    assert schema.operation_type == "update"
    assert len(schema.splits) == 3
    assert schema.validate_only is False

    # Check that all splits are BillSplitUpdate instances
    for split in schema.splits:
        assert isinstance(split, BillSplitUpdate)


def test_create_bulk_operation_result_schema():
    """Test creating a BulkOperationResult schema with default values."""
    schema = create_bulk_operation_result_schema()

    assert isinstance(schema, BulkOperationResult)
    assert schema.success is True
    assert schema.processed_count == 2
    assert schema.success_count == 2
    assert schema.failure_count == 0
    assert len(schema.successful_splits) == 2
    assert len(schema.errors) == 0


def test_create_bulk_operation_result_schema_with_errors():
    """Test creating a BulkOperationResult schema with errors."""
    errors = [
        {
            "index": 0,
            "split_data": create_bill_split_schema(liability_id=1, account_id=1),
            "error_message": "Invalid split",
            "error_type": "validation",
        }
    ]

    schema = create_bulk_operation_result_schema(
        success=False,
        processed_count=3,
        success_count=2,
        failure_count=1,
        errors=errors,
    )

    assert isinstance(schema, BulkOperationResult)
    assert schema.success is False
    assert schema.processed_count == 3
    assert schema.success_count == 2
    assert schema.failure_count == 1
    assert len(schema.successful_splits) == 2
    assert len(schema.errors) == 1
