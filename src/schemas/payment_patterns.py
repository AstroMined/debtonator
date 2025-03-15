from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field, ConfigDict

from src.schemas import BaseSchemaValidator


class PatternType(str, Enum):
    """
    Enumeration of payment pattern types.
    
    Used to categorize different patterns of payment behavior.
    """
    REGULAR = "regular"
    IRREGULAR = "irregular"
    SEASONAL = "seasonal"
    UNKNOWN = "unknown"


class FrequencyMetrics(BaseSchemaValidator):
    """
    Schema for metrics related to payment frequency.
    
    Contains statistical measurements about the timing between payments.
    """
    average_days_between: float = Field(
        ..., 
        description="Average number of days between payments",
        ge=0
    )
    std_dev_days: float = Field(
        ..., 
        description="Standard deviation of days between payments",
        ge=0
    )
    min_days: int = Field(
        ..., 
        description="Minimum days between payments",
        ge=0
    )
    max_days: int = Field(
        ..., 
        description="Maximum days between payments",
        ge=0
    )


class AmountStatistics(BaseSchemaValidator):
    """
    Schema for statistical data about payment amounts.
    
    Contains various statistical measures of payment amounts over time.
    """
    average_amount: Decimal = Field(
        ..., 
        description="Average payment amount",
        decimal_places=2
    )
    std_dev_amount: Decimal = Field(
        ..., 
        description="Standard deviation of payment amounts",
        decimal_places=2,
        ge=0
    )
    min_amount: Decimal = Field(
        ..., 
        description="Minimum payment amount",
        decimal_places=2
    )
    max_amount: Decimal = Field(
        ..., 
        description="Maximum payment amount",
        decimal_places=2
    )
    total_amount: Decimal = Field(
        ..., 
        description="Total amount of all payments",
        decimal_places=2
    )


class SeasonalMetrics(BaseSchemaValidator):
    """
    Schema for metrics related to seasonal payment patterns.
    
    Contains statistics about payment timing relative to due dates within seasons.
    """
    avg_days_before_due: float = Field(
        ..., 
        description="Average days before due date",
        ge=0
    )
    std_dev_days: float = Field(
        ..., 
        description="Standard deviation of days before due date",
        ge=0
    )
    sample_size: int = Field(
        ..., 
        description="Number of payments in this season",
        gt=0
    )


class PaymentPatternAnalysis(BaseSchemaValidator):
    """
    Schema for comprehensive payment pattern analysis.
    
    Contains detailed analysis of payment patterns including frequency, amounts,
    and statistical measurements.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    pattern_type: PatternType = Field(
        ..., 
        description="Type of payment pattern detected"
    )
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence score between 0 and 1"
    )
    frequency_metrics: FrequencyMetrics = Field(
        ..., 
        description="Metrics about payment frequency and timing"
    )
    amount_statistics: AmountStatistics = Field(
        ..., 
        description="Statistical analysis of payment amounts"
    )
    sample_size: int = Field(
        ..., 
        gt=0, 
        description="Number of payments analyzed"
    )
    analysis_period_start: datetime = Field(
        ..., 
        description="Start date of the analysis period (UTC timezone)"
    )
    analysis_period_end: datetime = Field(
        ..., 
        description="End date of the analysis period (UTC timezone)"
    )
    suggested_category: Optional[str] = Field(
        None, 
        description="Suggested payment category based on pattern analysis",
        max_length=100
    )
    notes: Optional[List[str]] = Field(
        None, 
        description="Additional notes or observations about the pattern"
    )
    seasonal_metrics: Optional[Dict[int, SeasonalMetrics]] = Field(
        None, 
        description="Monthly or seasonal metrics, keyed by month number (1-12)"
    )
    
    # No custom validators needed - BaseSchemaValidator handles UTC validation
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        },
        json_schema_extra={
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
    )


class PaymentPatternRequest(BaseSchemaValidator):
    """
    Schema for requesting payment pattern analysis.
    
    Contains parameters for analyzing payment patterns with optional filters.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    account_id: Optional[int] = Field(
        None, 
        description="Optional account ID to filter payments",
        gt=0
    )
    category_id: Optional[str] = Field(
        None, 
        description="Optional category ID to filter payments",
        max_length=100
    )
    start_date: Optional[datetime] = Field(
        None, 
        description="Optional start date for analysis period (UTC timezone)"
    )
    end_date: Optional[datetime] = Field(
        None, 
        description="Optional end date for analysis period (UTC timezone)"
    )
    min_sample_size: int = Field(
        default=3, 
        ge=2, 
        description="Minimum number of payments required for analysis (2 for bill-specific analysis, 3 for general analysis)"
    )
    liability_id: Optional[int] = Field(
        None, 
        description="Optional liability ID to filter payments",
        gt=0
    )
    
    # No custom validators needed - BaseSchemaValidator handles UTC validation
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": 1,
                "category_id": "utilities",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "min_sample_size": 3
            }
        }
    )
