"""
Bill split schema factory functions.

This module provides factory functions for creating valid BillSplit-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from src.schemas.bill_splits import (BillSplitCreate, BillSplitInDB,
                                     BillSplitResponse, BillSplitUpdate,
                                     BillSplitValidation, BulkOperationResult,
                                     BulkSplitOperation, HistoricalAnalysis,
                                     ImpactAnalysis, OptimizationMetrics,
                                     PatternMetrics, SplitPattern,
                                     SplitSuggestion)
from tests.helpers.schema_factories.base import (MEDIUM_AMOUNT,
                                                 factory_function, utc_now)


@factory_function(BillSplitCreate)
def create_bill_split_schema(
    liability_id: int, account_id: int, amount: Optional[Decimal] = None, **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a valid BillSplitCreate schema instance.

    Args:
        liability_id: ID of the liability
        account_id: ID of the account
        amount: Split amount (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    data = {
        "liability_id": liability_id,
        "account_id": account_id,
        "amount": amount,
        **kwargs,
    }

    return data


@factory_function(BillSplitUpdate)
def create_bill_split_update_schema(
    id: int, amount: Optional[Decimal] = None, **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a valid BillSplitUpdate schema instance.

    Args:
        id: ID of the bill split to update
        amount: New split amount (defaults to 150.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitUpdate schema
    """
    if amount is None:
        amount = Decimal("150.00")

    data = {"id": id, "amount": amount, **kwargs}

    return data


@factory_function(BillSplitInDB)
def create_bill_split_in_db_schema(
    id: int,
    liability_id: int,
    account_id: int,
    amount: Optional[Decimal] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BillSplitInDB schema instance.

    Args:
        id: Unique bill split identifier
        liability_id: ID of the liability
        account_id: ID of the account
        amount: Split amount (defaults to 100.00)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitInDB schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "liability_id": liability_id,
        "account_id": account_id,
        "amount": amount,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    return data


@factory_function(BillSplitResponse)
def create_bill_split_response_schema(
    id: int,
    liability_id: int,
    account_id: int,
    amount: Optional[Decimal] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BillSplitResponse schema instance.

    Args:
        id: Unique bill split identifier
        liability_id: ID of the liability
        account_id: ID of the account
        amount: Split amount (defaults to 100.00)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitResponse schema
    """
    # Use the BillSplitInDB factory since they have the same structure
    return create_bill_split_in_db_schema(
        id=id,
        liability_id=liability_id,
        account_id=account_id,
        amount=amount,
        created_at=created_at,
        updated_at=updated_at,
        **kwargs,
    )


@factory_function(BillSplitValidation)
def create_bill_split_validation_schema(
    liability_id: int,
    total_amount: Optional[Decimal] = None,
    splits: Optional[List[BillSplitCreate]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BillSplitValidation schema instance.

    Args:
        liability_id: ID of the liability being split
        total_amount: Total amount of the liability (defaults to 300.00)
        splits: List of bill splits to validate (creates 3 if None)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitValidation schema
    """
    if total_amount is None:
        total_amount = MEDIUM_AMOUNT * Decimal("3")  # Default to 300.00

    if splits is None:
        # Create 3 splits that sum to total_amount
        split_1_amount = MEDIUM_AMOUNT
        split_2_amount = MEDIUM_AMOUNT
        split_3_amount = total_amount - split_1_amount - split_2_amount

        splits = [
            create_bill_split_schema(
                liability_id=liability_id, account_id=1, amount=split_1_amount
            ),
            create_bill_split_schema(
                liability_id=liability_id, account_id=2, amount=split_2_amount
            ),
            create_bill_split_schema(
                liability_id=liability_id, account_id=3, amount=split_3_amount
            ),
        ]

    data = {
        "liability_id": liability_id,
        "total_amount": total_amount,
        "splits": splits,
        **kwargs,
    }

    return data


@factory_function(SplitSuggestion)
def create_split_suggestion_schema(
    account_id: int,
    amount: Optional[Decimal] = None,
    confidence_score: Optional[Decimal] = None,
    reason: str = "Based on historical split patterns",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SplitSuggestion schema instance.

    Args:
        account_id: ID of the suggested account
        amount: Suggested split amount (defaults to 100.00)
        confidence_score: Confidence score between 0 and 1 (defaults to 0.75)
        reason: Explanation for the suggested split
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SplitSuggestion schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    if confidence_score is None:
        confidence_score = Decimal("0.75")

    data = {
        "account_id": account_id,
        "amount": amount,
        "confidence_score": confidence_score,
        "reason": reason,
        **kwargs,
    }

    return data


@factory_function(SplitPattern)
def create_split_pattern_schema(
    pattern_id: str = "pattern-001",
    account_splits: Optional[Dict[int, Decimal]] = None,
    total_occurrences: int = 5,
    first_seen: Optional[datetime] = None,
    last_seen: Optional[datetime] = None,
    average_total: Optional[Decimal] = None,
    confidence_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SplitPattern schema instance.

    Args:
        pattern_id: Unique identifier for the pattern
        account_splits: Mapping of account IDs to split percentages
        total_occurrences: Number of times this pattern appears
        first_seen: Date pattern was first observed
        last_seen: Date pattern was last observed
        average_total: Average total amount for this pattern
        confidence_score: Confidence score based on frequency and recency
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SplitPattern schema
    """
    now = utc_now()

    if account_splits is None:
        account_splits = {
            1: Decimal("0.5"),  # 50%
            2: Decimal("0.3"),  # 30%
            3: Decimal("0.2"),  # 20%
        }

    if first_seen is None:
        # Default to 3 months ago
        if now.month <= 3:
            first_seen = datetime(now.year - 1, now.month + 9, 15, tzinfo=now.tzinfo)
        else:
            first_seen = datetime(now.year, now.month - 3, 15, tzinfo=now.tzinfo)

    if last_seen is None:
        # Default to last month
        if now.month == 1:
            last_seen = datetime(now.year - 1, 12, 15, tzinfo=now.tzinfo)
        else:
            last_seen = datetime(now.year, now.month - 1, 15, tzinfo=now.tzinfo)

    if average_total is None:
        average_total = MEDIUM_AMOUNT * Decimal("3")  # Default to 300.00

    if confidence_score is None:
        confidence_score = Decimal("0.85")

    data = {
        "pattern_id": pattern_id,
        "account_splits": account_splits,
        "total_occurrences": total_occurrences,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "average_total": average_total,
        "confidence_score": confidence_score,
        **kwargs,
    }

    return data


@factory_function(PatternMetrics)
def create_pattern_metrics_schema(
    total_splits: int = 25,
    unique_patterns: int = 3,
    most_common_pattern: Optional[SplitPattern] = None,
    average_splits_per_bill: float = 2.5,
    account_usage_frequency: Optional[Dict[int, int]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PatternMetrics schema instance.

    Args:
        total_splits: Total number of bill splits analyzed
        unique_patterns: Number of unique split patterns found
        most_common_pattern: Most frequently occurring pattern
        average_splits_per_bill: Average number of splits per bill
        account_usage_frequency: Frequency of each account's usage
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PatternMetrics schema
    """
    if most_common_pattern is None:
        most_common_pattern = create_split_pattern_schema(total_occurrences=15)

    if account_usage_frequency is None:
        account_usage_frequency = {
            1: 20,  # Account 1 used in 20 splits
            2: 15,  # Account 2 used in 15 splits
            3: 10,  # Account 3 used in 10 splits
        }

    data = {
        "total_splits": total_splits,
        "unique_patterns": unique_patterns,
        "most_common_pattern": most_common_pattern,
        "average_splits_per_bill": average_splits_per_bill,
        "account_usage_frequency": account_usage_frequency,
        **kwargs,
    }

    return data


@factory_function(OptimizationMetrics)
def create_optimization_metrics_schema(
    credit_utilization: Optional[Dict[int, Decimal]] = None,
    balance_impact: Optional[Dict[int, Decimal]] = None,
    risk_score: Optional[Decimal] = None,
    optimization_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid OptimizationMetrics schema instance.

    Args:
        credit_utilization: Credit utilization percentage per credit account
        balance_impact: Impact on available balance per account
        risk_score: Risk score for the split configuration
        optimization_score: Overall optimization score
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create OptimizationMetrics schema
    """
    if credit_utilization is None:
        credit_utilization = {
            1: Decimal("0.4"),  # 40% utilization for account 1
            2: Decimal("0.25"),  # 25% utilization for account 2
        }

    if balance_impact is None:
        balance_impact = {
            1: Decimal("-150.00"),  # $150 negative impact on account 1
            2: Decimal("-100.00"),  # $100 negative impact on account 2
            3: Decimal("-50.00"),  # $50 negative impact on account 3
        }

    if risk_score is None:
        risk_score = Decimal("0.35")  # 35% risk

    if optimization_score is None:
        optimization_score = Decimal("0.7")  # 70% optimization

    data = {
        "credit_utilization": credit_utilization,
        "balance_impact": balance_impact,
        "risk_score": risk_score,
        "optimization_score": optimization_score,
        **kwargs,
    }

    return data


@factory_function(ImpactAnalysis)
def create_impact_analysis_schema(
    split_configuration: Optional[List[BillSplitCreate]] = None,
    metrics: Optional[OptimizationMetrics] = None,
    short_term_impact: Optional[Dict[int, Decimal]] = None,
    long_term_impact: Optional[Dict[int, Decimal]] = None,
    risk_factors: Optional[List[str]] = None,
    recommendations: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid ImpactAnalysis schema instance.

    Args:
        split_configuration: Split configuration being analyzed
        metrics: Current configuration metrics
        short_term_impact: 30-day impact per account
        long_term_impact: 90-day impact per account
        risk_factors: Identified risk factors
        recommendations: Recommendations for improvement
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create ImpactAnalysis schema
    """
    liability_id = 1  # Default liability ID

    if split_configuration is None:
        split_configuration = [
            create_bill_split_schema(
                liability_id=liability_id, account_id=1, amount=Decimal("150.00")
            ),
            create_bill_split_schema(
                liability_id=liability_id, account_id=2, amount=Decimal("100.00")
            ),
            create_bill_split_schema(
                liability_id=liability_id, account_id=3, amount=Decimal("50.00")
            ),
        ]

    if metrics is None:
        metrics = create_optimization_metrics_schema()

    if short_term_impact is None:
        short_term_impact = {
            1: Decimal("-150.00"),  # $150 negative impact on account 1
            2: Decimal("-100.00"),  # $100 negative impact on account 2
            3: Decimal("-50.00"),  # $50 negative impact on account 3
        }

    if long_term_impact is None:
        long_term_impact = {
            1: Decimal("-450.00"),  # $450 negative impact on account 1
            2: Decimal("-300.00"),  # $300 negative impact on account 2
            3: Decimal("-150.00"),  # $150 negative impact on account 3
        }

    if risk_factors is None:
        risk_factors = [
            "High credit utilization on account 1",
            "Potential overdraft on account 3 within 60 days",
        ]

    if recommendations is None:
        recommendations = [
            "Reduce split allocation to account 1 by 10%",
            "Increase split allocation to account 2 by 5%",
            "Consider additional income deposit to account 3",
        ]

    data = {
        "split_configuration": split_configuration,
        "metrics": metrics,
        "short_term_impact": short_term_impact,
        "long_term_impact": long_term_impact,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        **kwargs,
    }

    return data


@factory_function(HistoricalAnalysis)
def create_historical_analysis_schema(
    liability_id: int = 1,
    analysis_date: Optional[datetime] = None,
    patterns: Optional[List[SplitPattern]] = None,
    metrics: Optional[PatternMetrics] = None,
    category_patterns: Optional[Dict[int, List[SplitPattern]]] = None,
    seasonal_patterns: Optional[Dict[str, List[SplitPattern]]] = None,
    optimization_suggestions: Optional[List[Dict[str, Any]]] = None,
    impact_analysis: Optional[ImpactAnalysis] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid HistoricalAnalysis schema instance.

    Args:
        liability_id: ID of the liability analyzed
        analysis_date: Date analysis was performed (defaults to now)
        patterns: Identified split patterns
        metrics: Analysis metrics
        category_patterns: Split patterns grouped by category
        seasonal_patterns: Split patterns grouped by season/time period
        optimization_suggestions: Suggestions for optimizing splits
        impact_analysis: Impact analysis of current splits
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create HistoricalAnalysis schema
    """
    if analysis_date is None:
        analysis_date = utc_now()

    if patterns is None:
        patterns = [
            create_split_pattern_schema(pattern_id="pattern-001", total_occurrences=15),
            create_split_pattern_schema(pattern_id="pattern-002", total_occurrences=7),
            create_split_pattern_schema(pattern_id="pattern-003", total_occurrences=3),
        ]

    if metrics is None:
        metrics = create_pattern_metrics_schema(most_common_pattern=patterns[0])

    if category_patterns is None:
        category_patterns = {
            1: [patterns[0]],  # Category 1 has pattern-001
            2: [patterns[1], patterns[2]],  # Category 2 has pattern-002 and pattern-003
        }

    if seasonal_patterns is None:
        seasonal_patterns = {
            "winter": [patterns[0]],
            "summer": [patterns[1]],
            "holiday": [patterns[2]],
        }

    if optimization_suggestions is None:
        optimization_suggestions = []

    if impact_analysis is None:
        impact_analysis = create_impact_analysis_schema()

    data = {
        "liability_id": liability_id,
        "analysis_date": analysis_date,
        "patterns": patterns,
        "metrics": metrics,
        "category_patterns": category_patterns,
        "seasonal_patterns": seasonal_patterns,
        "optimization_suggestions": optimization_suggestions,
        "impact_analysis": impact_analysis,
        **kwargs,
    }

    return data


@factory_function(BulkSplitOperation)
def create_bulk_split_operation_schema(
    operation_type: str = "create",
    splits: Optional[List[Union[BillSplitCreate, BillSplitUpdate]]] = None,
    validate_only: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BulkSplitOperation schema instance.

    Args:
        operation_type: Type of operation (create/update)
        splits: List of bill splits to process
        validate_only: If true, only validate without executing
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BulkSplitOperation schema
    """
    if splits is None:
        if operation_type == "create":
            # Create sample BillSplitCreate instances
            splits = [
                create_bill_split_schema(
                    liability_id=1, account_id=1, amount=Decimal("150.00")
                ),
                create_bill_split_schema(
                    liability_id=1, account_id=2, amount=Decimal("100.00")
                ),
                create_bill_split_schema(
                    liability_id=1, account_id=3, amount=Decimal("50.00")
                ),
            ]
        else:  # update
            # Create sample BillSplitUpdate instances
            splits = [
                create_bill_split_update_schema(id=1, amount=Decimal("160.00")),
                create_bill_split_update_schema(id=2, amount=Decimal("110.00")),
                create_bill_split_update_schema(id=3, amount=Decimal("60.00")),
            ]

    data = {
        "operation_type": operation_type,
        "splits": splits,
        "validate_only": validate_only,
        **kwargs,
    }

    return data


@factory_function(BulkOperationResult)
def create_bulk_operation_result_schema(
    success: bool = True,
    processed_count: Optional[int] = None,
    success_count: Optional[int] = None,
    failure_count: Optional[int] = None,
    successful_splits: Optional[List[BillSplitResponse]] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BulkOperationResult schema instance.

    Args:
        success: Overall operation success status
        processed_count: Number of splits processed
        success_count: Number of successful operations
        failure_count: Number of failed operations
        successful_splits: Successfully processed splits
        errors: Errors encountered during processing
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BulkOperationResult schema
    """
    if successful_splits is None:
        successful_splits = [
            create_bill_split_response_schema(
                id=1, liability_id=1, account_id=1, amount=Decimal("150.00")
            ),
            create_bill_split_response_schema(
                id=2, liability_id=1, account_id=2, amount=Decimal("100.00")
            ),
        ]

    if errors is None:
        errors = []

    if processed_count is None:
        processed_count = len(successful_splits) + len(errors)

    if success_count is None:
        success_count = len(successful_splits)

    if failure_count is None:
        failure_count = len(errors)

    data = {
        "success": success,
        "processed_count": processed_count,
        "success_count": success_count,
        "failure_count": failure_count,
        "successful_splits": successful_splits,
        "errors": errors,
        **kwargs,
    }

    return data
