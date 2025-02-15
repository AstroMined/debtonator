from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

class BillSplitBase(BaseModel):
    """Base schema for bill split data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    amount: Decimal = Field(..., gt=0, description="Split amount must be greater than 0")

class BillSplitCreate(BillSplitBase):
    """Schema for creating a new bill split"""
    liability_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)

    @model_validator(mode='after')
    def validate_amount(self) -> 'BillSplitCreate':
        if self.amount <= 0:
            raise ValueError("Split amount must be greater than 0")
        return self

class BillSplitUpdate(BillSplitBase):
    """Schema for updating an existing bill split"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: int = Field(..., gt=0, description="ID of the split to update")

class BillSplitInDB(BillSplitBase):
    """Schema for bill split data as stored in the database"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    liability_id: int
    account_id: int
    created_at: date
    updated_at: date

class BillSplitResponse(BillSplitInDB):
    """Schema for bill split data in API responses"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BillSplitValidation(BaseModel):
    """Schema for validating bill splits"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    liability_id: int = Field(..., gt=0)
    total_amount: Decimal = Field(..., gt=0)
    splits: List[BillSplitCreate]

    @model_validator(mode='after')
    def validate_splits(self) -> 'BillSplitValidation':
        if not self.splits:
            raise ValueError("At least one split is required")
        
        total_split = sum(split.amount for split in self.splits)
        if abs(total_split - self.total_amount) > Decimal('0.01'):
            raise ValueError(
                f"Sum of splits ({total_split}) must equal total amount ({self.total_amount})"
            )
        
        return self

class SplitSuggestion(BaseModel):
    """Schema for individual split suggestion"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    account_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    reason: str = Field(..., description="Explanation for the suggested split")

class BillSplitSuggestionResponse(BaseModel):
    """Schema for bill split suggestions response"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    liability_id: int = Field(..., gt=0)
    total_amount: Decimal = Field(..., gt=0)
    suggestions: List[SplitSuggestion]
    historical_pattern: Optional[bool] = Field(
        default=False, 
        description="Whether this suggestion is based on historical patterns"
    )
    pattern_frequency: Optional[int] = Field(
        default=None,
        description="Number of times this pattern was found in history"
    )

class SplitPattern(BaseModel):
    """Schema for a bill split pattern"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    pattern_id: str = Field(..., description="Unique identifier for the pattern")
    account_splits: Dict[int, Decimal] = Field(
        ..., 
        description="Mapping of account IDs to their split percentages"
    )
    total_occurrences: int = Field(..., gt=0, description="Number of times this pattern appears")
    first_seen: date = Field(..., description="Date pattern was first observed")
    last_seen: date = Field(..., description="Date pattern was last observed")
    average_total: Decimal = Field(..., gt=0, description="Average total amount for this pattern")
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence score based on frequency and recency"
    )

class PatternMetrics(BaseModel):
    """Schema for pattern analysis metrics"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_splits: int = Field(..., description="Total number of bill splits analyzed")
    unique_patterns: int = Field(..., description="Number of unique split patterns found")
    most_common_pattern: Optional[SplitPattern] = Field(
        None, 
        description="Most frequently occurring pattern"
    )
    average_splits_per_bill: float = Field(
        ..., 
        description="Average number of splits per bill"
    )
    account_usage_frequency: Dict[int, int] = Field(
        ..., 
        description="Frequency of each account's appearance in splits"
    )

class OptimizationMetrics(BaseModel):
    """Schema for split optimization metrics"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    credit_utilization: Dict[int, float] = Field(
        ...,
        description="Credit utilization percentage per credit account"
    )
    balance_impact: Dict[int, Decimal] = Field(
        ...,
        description="Impact on available balance per account"
    )
    risk_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Risk score for the split configuration"
    )
    optimization_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Overall optimization score"
    )

class OptimizationSuggestion(BaseModel):
    """Schema for split optimization suggestions"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    original_splits: List[BillSplitCreate] = Field(
        ...,
        description="Original split configuration"
    )
    suggested_splits: List[BillSplitCreate] = Field(
        ...,
        description="Suggested optimized splits"
    )
    improvement_metrics: OptimizationMetrics = Field(
        ...,
        description="Metrics showing improvement"
    )
    reasoning: List[str] = Field(
        ...,
        description="List of reasons for the suggested changes"
    )
    priority: int = Field(
        ...,
        ge=1,
        le=5,
        description="Priority level of the suggestion (1-5)"
    )

class ImpactAnalysis(BaseModel):
    """Schema for split impact analysis"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    split_configuration: List[BillSplitCreate] = Field(
        ...,
        description="Split configuration being analyzed"
    )
    metrics: OptimizationMetrics = Field(
        ...,
        description="Current configuration metrics"
    )
    short_term_impact: Dict[int, Decimal] = Field(
        ...,
        description="30-day impact per account"
    )
    long_term_impact: Dict[int, Decimal] = Field(
        ...,
        description="90-day impact per account"
    )
    risk_factors: List[str] = Field(
        ...,
        description="Identified risk factors"
    )
    recommendations: List[str] = Field(
        ...,
        description="Recommendations for improvement"
    )

class HistoricalAnalysis(BaseModel):
    """Schema for comprehensive historical analysis results"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    liability_id: int = Field(..., gt=0)
    analysis_date: date = Field(..., description="Date analysis was performed")
    patterns: List[SplitPattern] = Field(..., description="Identified split patterns")
    metrics: PatternMetrics = Field(..., description="Analysis metrics")
    category_patterns: Optional[Dict[int, List[SplitPattern]]] = Field(
        None,
        description="Split patterns grouped by category"
    )
    seasonal_patterns: Optional[Dict[str, List[SplitPattern]]] = Field(
        None,
        description="Split patterns grouped by season/time period"
    )
    optimization_suggestions: Optional[List[OptimizationSuggestion]] = Field(
        None,
        description="Suggestions for optimizing splits"
    )
    impact_analysis: Optional[ImpactAnalysis] = Field(
        None,
        description="Impact analysis of current splits"
    )

class BulkSplitOperation(BaseModel):
    """Schema for bulk bill split operations"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    operation_type: str = Field(
        ..., 
        description="Type of operation (create/update)",
        pattern="^(create|update)$"
    )
    splits: List[Union[BillSplitCreate, BillSplitUpdate]] = Field(
        ...,
        min_items=1,
        description="List of bill splits to process"
    )
    validate_only: bool = Field(
        False,
        description="If true, only validate the operation without executing"
    )

    @model_validator(mode='after')
    def validate_operation(self) -> 'BulkSplitOperation':
        if not self.splits:
            raise ValueError("At least one split is required")
        
        if self.operation_type == 'update':
            if not all(isinstance(split, BillSplitUpdate) for split in self.splits):
                raise ValueError("Update operation requires BillSplitUpdate instances")
        elif self.operation_type == 'create':
            if not all(isinstance(split, BillSplitCreate) for split in self.splits):
                raise ValueError("Create operation requires BillSplitCreate instances")
        
        return self

class BulkOperationError(BaseModel):
    """Schema for bulk operation errors"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    index: int = Field(..., description="Index of the failed split in the input list")
    split_data: Union[BillSplitCreate, BillSplitUpdate] = Field(
        ..., 
        description="Original split data that caused the error"
    )
    error_message: str = Field(..., description="Detailed error message")
    error_type: str = Field(..., description="Type of error (validation/processing)")

class BulkOperationResult(BaseModel):
    """Schema for bulk operation results"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = Field(..., description="Overall operation success status")
    processed_count: int = Field(..., ge=0, description="Number of splits processed")
    success_count: int = Field(..., ge=0, description="Number of successful operations")
    failure_count: int = Field(..., ge=0, description="Number of failed operations")
    successful_splits: List[BillSplitResponse] = Field(
        default_factory=list,
        description="Successfully processed splits"
    )
    errors: List[BulkOperationError] = Field(
        default_factory=list,
        description="Errors encountered during processing"
    )

    @model_validator(mode='after')
    def validate_counts(self) -> 'BulkOperationResult':
        if self.failure_count != self.processed_count - self.success_count:
            raise ValueError("Failure count must equal processed count minus success count")
        return self
