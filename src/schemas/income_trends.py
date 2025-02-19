from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class FrequencyType(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"

class IncomePattern(BaseModel):
    """Pattern identified in income data"""
    source: str = Field(..., min_length=1, max_length=255)
    frequency: FrequencyType
    average_amount: Decimal = Field(..., gt=0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    last_occurrence: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    next_predicted: Optional[datetime] = None

    @field_validator("last_occurrence", "next_predicted", mode="before")
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

class PeriodType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class SeasonalityMetrics(BaseModel):
    """Seasonal patterns in income"""
    period: PeriodType
    peak_months: List[int] = Field(..., min_items=1, max_items=12)  # 1-12 representing months
    trough_months: List[int] = Field(..., min_items=1, max_items=12)  # 1-12 representing months
    variance_coefficient: float = Field(..., ge=0.0)
    confidence_score: float = Field(ge=0.0, le=1.0)

    @field_validator("peak_months", "trough_months")
    @classmethod
    def validate_months(cls, value: List[int]) -> List[int]:
        if not all(1 <= month <= 12 for month in value):
            raise ValueError("Months must be between 1 and 12")
        if len(set(value)) != len(value):
            raise ValueError("Duplicate months are not allowed")
        return value

class SourceStatistics(BaseModel):
    """Statistical analysis for an income source"""
    source: str = Field(..., min_length=1, max_length=255)
    total_occurrences: int = Field(..., gt=0)
    total_amount: Decimal = Field(..., ge=0)
    average_amount: Decimal = Field(..., gt=0)
    min_amount: Decimal = Field(..., ge=0)
    max_amount: Decimal = Field(..., gt=0)
    standard_deviation: float = Field(..., ge=0.0)
    reliability_score: float = Field(ge=0.0, le=1.0)

    @field_validator("max_amount")
    @classmethod
    def validate_max_amount(cls, v: Decimal, values: dict) -> Decimal:
        if "min_amount" in values and v < values["min_amount"]:
            raise ValueError("max_amount must be greater than or equal to min_amount")
        return v

class IncomeTrendsAnalysis(BaseModel):
    """Complete income trends analysis"""
    patterns: List[IncomePattern] = Field(..., min_items=1)
    seasonality: Optional[SeasonalityMetrics] = None
    source_statistics: List[SourceStatistics] = Field(..., min_items=1)
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    data_start_date: datetime
    data_end_date: datetime
    overall_predictability_score: float = Field(ge=0.0, le=1.0)

    @field_validator("analysis_date", "data_start_date", "data_end_date", mode="before")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value

    @field_validator("data_end_date")
    @classmethod
    def validate_date_range(cls, v: datetime, values: dict) -> datetime:
        if "data_start_date" in values and v < values["data_start_date"]:
            raise ValueError("data_end_date must be after data_start_date")
        return v

class IncomeTrendsRequest(BaseModel):
    """Request parameters for trends analysis"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = Field(None, min_length=1, max_length=255)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)

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

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        if v and "start_date" in values and values["start_date"] and v < values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "source": "salary",
                "min_confidence": 0.7
            }
        }
