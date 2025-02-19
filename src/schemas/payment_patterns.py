from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PatternType(str, Enum):
    REGULAR = "regular"
    IRREGULAR = "irregular"
    SEASONAL = "seasonal"
    UNKNOWN = "unknown"


class FrequencyMetrics(BaseModel):
    average_days_between: float = Field(..., description="Average number of days between payments")
    std_dev_days: float = Field(..., description="Standard deviation of days between payments")
    min_days: int = Field(..., description="Minimum days between payments")
    max_days: int = Field(..., description="Maximum days between payments")


class AmountStatistics(BaseModel):
    average_amount: Decimal = Field(..., description="Average payment amount")
    std_dev_amount: Decimal = Field(..., description="Standard deviation of payment amounts")
    min_amount: Decimal = Field(..., description="Minimum payment amount")
    max_amount: Decimal = Field(..., description="Maximum payment amount")
    total_amount: Decimal = Field(..., description="Total amount of all payments")


class SeasonalMetrics(BaseModel):
    avg_days_before_due: float = Field(..., description="Average days before due date")
    std_dev_days: float = Field(..., description="Standard deviation of days before due date")
    sample_size: int = Field(..., description="Number of payments in this season")


class PaymentPatternAnalysis(BaseModel):
    pattern_type: PatternType
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    frequency_metrics: FrequencyMetrics
    amount_statistics: AmountStatistics
    sample_size: int = Field(..., gt=0, description="Number of payments analyzed")
    analysis_period_start: datetime
    analysis_period_end: datetime
    suggested_category: Optional[str] = None
    notes: Optional[List[str]] = None
    seasonal_metrics: Optional[Dict[int, SeasonalMetrics]] = None

    @field_validator("analysis_period_start", "analysis_period_end", mode="before")
    @classmethod
    def validate_timezone(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        json_schema_extra = {
            "example": {
                "pattern_type": "REGULAR",
                "confidence_score": 0.95,
                "frequency_metrics": {
                    "average_days_between": 30.5,
                    "std_dev_days": 1.2,
                    "min_days": 29,
                    "max_days": 32
                },
                "amount_statistics": {
                    "average_amount": "150.00",
                    "std_dev_amount": "10.00",
                    "min_amount": "140.00",
                    "max_amount": "160.00",
                    "total_amount": "1500.00"
                },
                "sample_size": 10,
                "analysis_period_start": "2024-01-01T00:00:00Z",
                "analysis_period_end": "2024-12-31T23:59:59Z"
            }
        }


class PaymentPatternRequest(BaseModel):
    account_id: Optional[int] = None
    category_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_sample_size: int = Field(default=3, ge=2, description="Minimum number of payments required for analysis (2 for bill-specific analysis, 3 for general analysis)")
    liability_id: Optional[int] = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def validate_timezone(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": 1,
                "category_id": "utilities",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "min_sample_size": 3
            }
        }
