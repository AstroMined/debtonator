from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


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

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure analysis period dates are UTC
        if self.analysis_period_start and not self.analysis_period_start.tzinfo:
            self.analysis_period_start = self.analysis_period_start.replace(tzinfo=timezone.utc)
        if self.analysis_period_end and not self.analysis_period_end.tzinfo:
            self.analysis_period_end = self.analysis_period_end.replace(tzinfo=timezone.utc)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PaymentPatternRequest(BaseModel):
    account_id: Optional[int] = None
    category_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_sample_size: int = Field(default=3, ge=2, description="Minimum number of payments required for analysis (2 for bill-specific analysis, 3 for general analysis)")
    liability_id: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure any provided dates are UTC
        if self.start_date and not self.start_date.tzinfo:
            self.start_date = self.start_date.replace(tzinfo=timezone.utc)
        if self.end_date and not self.end_date.tzinfo:
            self.end_date = self.end_date.replace(tzinfo=timezone.utc)
