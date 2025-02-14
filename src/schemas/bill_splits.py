from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, validator

class BillSplitBase(BaseModel):
    """Base schema for bill split data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    amount: Decimal = Field(..., gt=0, description="Split amount must be greater than 0")

class BillSplitCreate(BillSplitBase):
    """Schema for creating a new bill split"""
    liability_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)

    @validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Split amount must be greater than 0")
        return v

class BillSplitUpdate(BillSplitBase):
    """Schema for updating an existing bill split"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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

    @validator('splits')
    @classmethod
    def validate_splits(cls, v, values):
        if not v:
            raise ValueError("At least one split is required")
        
        total_split = sum(split.amount for split in v)
        if 'total_amount' in values and abs(total_split - values['total_amount']) > Decimal('0.01'):
            raise ValueError(
                f"Sum of splits ({total_split}) must equal total amount ({values['total_amount']})"
            )
        
        return v

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
