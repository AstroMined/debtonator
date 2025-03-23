"""
Bill split schema definitions for the API.

This module defines the schema classes for bill split data validation and serialization.
Includes schemas for creating, updating, and validating bill splits, as well as specialized
schemas for pattern analysis and optimization suggestions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union

from pydantic import Field, model_validator

from src.schemas import (BaseSchemaValidator, IntMoneyDict, IntPercentageDict,
                         MoneyDecimal, PercentageDecimal)


class BillSplitBase(BaseSchemaValidator):
    """
    Base schema for bill split data.

    Contains common fields and validation shared by all bill split schemas.
    """

    amount: MoneyDecimal = Field(
        ..., gt=0, description="Split amount must be greater than 0"
    )


class BillSplitCreate(BillSplitBase):
    """
    Schema for creating a new bill split.

    Contains validation to ensure the split amount is greater than zero.
    """

    liability_id: int = Field(..., gt=0, description="ID of the liability being split")
    account_id: int = Field(
        ..., gt=0, description="ID of the account receiving this portion of the bill"
    )

    @model_validator(mode="after")
    def validate_amount(self) -> "BillSplitCreate":
        if self.amount <= 0:
            raise ValueError("Split amount must be greater than 0")
        return self


class BillSplitUpdate(BillSplitBase):
    """
    Schema for updating an existing bill split.

    Requires the ID of the split to be updated.
    """

    id: int = Field(..., gt=0, description="ID of the split to update")


class BillSplitInDB(BillSplitBase):
    """
    Schema for bill split data as stored in the database.

    Extends the base schema with database-specific fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="Unique bill split identifier")
    liability_id: int = Field(..., description="ID of the liability being split")
    account_id: int = Field(
        ..., description="ID of the account receiving this portion of the bill"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated (UTC timezone)"
    )


class BillSplitResponse(BillSplitInDB):
    """
    Schema for bill split data in API responses.

    Inherits all fields and validation from BillSplitInDB.
    """


class BillSplitValidation(BaseSchemaValidator):
    """
    Schema for validating bill splits.

    Ensures the sum of all splits equals the total amount of the liability.
    """

    liability_id: int = Field(..., gt=0, description="ID of the liability being split")
    total_amount: MoneyDecimal = Field(
        ..., gt=0, description="Total amount of the liability"
    )
    splits: List[BillSplitCreate] = Field(
        ..., description="List of bill splits to validate"
    )

    @model_validator(mode="after")
    def validate_splits(self) -> "BillSplitValidation":
        if not self.splits:
            raise ValueError("At least one split is required")

        total_split = sum(split.amount for split in self.splits)
        if abs(total_split - self.total_amount) > Decimal("0.01"):
            raise ValueError(
                f"Sum of splits ({total_split}) must equal total amount ({self.total_amount})"
            )

        return self


class SplitSuggestion(BaseSchemaValidator):
    """
    Schema for individual split suggestion.

    Contains details about a suggested split including confidence score and reasoning.
    """

    account_id: int = Field(..., gt=0, description="ID of the suggested account")
    amount: MoneyDecimal = Field(..., gt=0, description="Suggested split amount")
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence score between 0 and 1"
    )
    reason: str = Field(
        ..., max_length=500, description="Explanation for the suggested split"
    )


class BillSplitSuggestionResponse(BaseSchemaValidator):
    """
    Schema for bill split suggestions response.

    Contains a list of suggested splits and metadata about the suggestion.
    """

    liability_id: int = Field(..., gt=0, description="ID of the liability")
    total_amount: MoneyDecimal = Field(
        ..., gt=0, description="Total amount of the liability"
    )
    suggestions: List[SplitSuggestion] = Field(
        ..., description="List of suggested splits"
    )
    historical_pattern: Optional[bool] = Field(
        default=False,
        description="Whether this suggestion is based on historical patterns",
    )
    pattern_frequency: Optional[int] = Field(
        default=None, description="Number of times this pattern was found in history"
    )


class SplitPattern(BaseSchemaValidator):
    """
    Schema for a bill split pattern.

    Represents a detected pattern in bill splitting behavior.
    """

    pattern_id: str = Field(
        ..., max_length=50, description="Unique identifier for the pattern"
    )
    account_splits: IntPercentageDict = Field(
        ..., description="Mapping of account IDs to their split percentages"
    )
    total_occurrences: int = Field(
        ..., gt=0, description="Number of times this pattern appears"
    )
    first_seen: datetime = Field(
        ..., description="Date pattern was first observed (UTC timezone)"
    )
    last_seen: datetime = Field(
        ..., description="Date pattern was last observed (UTC timezone)"
    )
    average_total: MoneyDecimal = Field(
        ..., gt=0, description="Average total amount for this pattern"
    )
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence score based on frequency and recency"
    )


class PatternMetrics(BaseSchemaValidator):
    """
    Schema for pattern analysis metrics.

    Contains aggregated metrics about bill splitting patterns.
    """

    total_splits: int = Field(..., description="Total number of bill splits analyzed")
    unique_patterns: int = Field(
        ..., description="Number of unique split patterns found"
    )
    most_common_pattern: Optional[SplitPattern] = Field(
        None, description="Most frequently occurring pattern"
    )
    average_splits_per_bill: float = Field(
        ..., description="Average number of splits per bill"
    )
    account_usage_frequency: Dict[int, int] = Field(
        ..., description="Frequency of each account's appearance in splits"
    )


class OptimizationMetrics(BaseSchemaValidator):
    """
    Schema for split optimization metrics.

    Contains metrics about the effectiveness of bill split configurations.
    """

    credit_utilization: Dict[int, PercentageDecimal] = Field(
        ..., description="Credit utilization percentage per credit account"
    )
    balance_impact: IntMoneyDict = Field(
        ..., description="Impact on available balance per account"
    )
    risk_score: PercentageDecimal = Field(
        ..., description="Risk score for the split configuration"
    )
    optimization_score: PercentageDecimal = Field(
        ..., description="Overall optimization score"
    )


class OptimizationSuggestion(BaseSchemaValidator):
    """
    Schema for split optimization suggestions.

    Contains suggestions for improving bill split configurations.
    """

    original_splits: List[BillSplitCreate] = Field(
        ..., description="Original split configuration"
    )
    suggested_splits: List[BillSplitCreate] = Field(
        ..., description="Suggested optimized splits"
    )
    improvement_metrics: OptimizationMetrics = Field(
        ..., description="Metrics showing improvement"
    )
    reasoning: List[str] = Field(
        ..., description="List of reasons for the suggested changes"
    )
    priority: int = Field(
        ..., ge=1, le=5, description="Priority level of the suggestion (1-5)"
    )


class ImpactAnalysis(BaseSchemaValidator):
    """
    Schema for split impact analysis.

    Contains analysis of how bill splits impact accounts over time.
    """

    split_configuration: List[BillSplitCreate] = Field(
        ..., description="Split configuration being analyzed"
    )
    metrics: OptimizationMetrics = Field(
        ..., description="Current configuration metrics"
    )
    short_term_impact: IntMoneyDict = Field(
        ..., description="30-day impact per account"
    )
    long_term_impact: IntMoneyDict = Field(..., description="90-day impact per account")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    recommendations: List[str] = Field(
        ..., description="Recommendations for improvement"
    )


class HistoricalAnalysis(BaseSchemaValidator):
    """
    Schema for comprehensive historical analysis results.

    Contains detailed analysis of bill splitting history and patterns.
    """

    liability_id: int = Field(..., gt=0, description="ID of the liability analyzed")
    analysis_date: datetime = Field(
        ..., description="Date analysis was performed (UTC timezone)"
    )
    patterns: List[SplitPattern] = Field(..., description="Identified split patterns")
    metrics: PatternMetrics = Field(..., description="Analysis metrics")
    category_patterns: Optional[Dict[int, List[SplitPattern]]] = Field(
        None, description="Split patterns grouped by category"
    )
    seasonal_patterns: Optional[Dict[str, List[SplitPattern]]] = Field(
        None, description="Split patterns grouped by season/time period"
    )
    optimization_suggestions: Optional[List[OptimizationSuggestion]] = Field(
        None, description="Suggestions for optimizing splits"
    )
    impact_analysis: Optional[ImpactAnalysis] = Field(
        None, description="Impact analysis of current splits"
    )


class BulkSplitOperation(BaseSchemaValidator):
    """
    Schema for bulk bill split operations.

    Used for creating or updating multiple bill splits in a single operation.
    """

    operation_type: str = Field(
        ...,
        description="Type of operation (create/update)",
        pattern="^(create|update)$",
    )
    splits: List[Union[BillSplitCreate, BillSplitUpdate]] = Field(
        ..., min_items=1, description="List of bill splits to process"
    )
    validate_only: bool = Field(
        False, description="If true, only validate the operation without executing"
    )

    @model_validator(mode="after")
    def validate_operation(self) -> "BulkSplitOperation":
        if not self.splits:
            raise ValueError("At least one split is required")

        if self.operation_type == "update":
            if not all(isinstance(split, BillSplitUpdate) for split in self.splits):
                raise ValueError("Update operation requires BillSplitUpdate instances")
        elif self.operation_type == "create":
            if not all(isinstance(split, BillSplitCreate) for split in self.splits):
                raise ValueError("Create operation requires BillSplitCreate instances")

        return self


class BulkOperationError(BaseSchemaValidator):
    """
    Schema for bulk operation errors.

    Contains details about errors encountered during bulk operations.
    """

    index: int = Field(..., description="Index of the failed split in the input list")
    split_data: Union[BillSplitCreate, BillSplitUpdate] = Field(
        ..., description="Original split data that caused the error"
    )
    error_message: str = Field(..., description="Detailed error message")
    error_type: str = Field(
        ...,
        description="Type of error (validation/processing)",
        pattern="^(validation|processing)$",
    )


class BulkOperationResult(BaseSchemaValidator):
    """
    Schema for bulk operation results.

    Contains summary and detailed results of a bulk bill split operation.
    """

    success: bool = Field(..., description="Overall operation success status")
    processed_count: int = Field(..., ge=0, description="Number of splits processed")
    success_count: int = Field(..., ge=0, description="Number of successful operations")
    failure_count: int = Field(..., ge=0, description="Number of failed operations")
    successful_splits: List[BillSplitResponse] = Field(
        default_factory=list, description="Successfully processed splits"
    )
    errors: List[BulkOperationError] = Field(
        default_factory=list, description="Errors encountered during processing"
    )

    @model_validator(mode="after")
    def validate_counts(self) -> "BulkOperationResult":
        if self.failure_count != self.processed_count - self.success_count:
            raise ValueError(
                "Failure count must equal processed count minus success count"
            )
        return self
