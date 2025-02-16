from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator


class RecommendationType(str, Enum):
    BILL_PAYMENT_TIMING = "bill_payment_timing"
    ACCOUNT_SELECTION = "account_selection"
    SPLIT_DISTRIBUTION = "split_distribution"
    CREDIT_UTILIZATION = "credit_utilization"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactMetrics(BaseModel):
    balance_impact: Decimal
    credit_utilization_impact: Optional[Decimal] = None
    risk_score: Decimal = Field(ge=0, le=100)
    savings_potential: Optional[Decimal] = None


class RecommendationBase(BaseModel):
    type: RecommendationType
    confidence: ConfidenceLevel
    impact: ImpactMetrics
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value


class BillPaymentTimingRecommendation(RecommendationBase):
    type: RecommendationType = RecommendationType.BILL_PAYMENT_TIMING
    bill_id: int
    current_due_date: datetime
    recommended_date: datetime
    reason: str
    historical_pattern_strength: Decimal = Field(ge=0, le=1)
    affected_accounts: List[int]

    @field_validator("current_due_date", "recommended_date", mode="before")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value


class RecommendationResponse(BaseModel):
    recommendations: List[BillPaymentTimingRecommendation]
    total_savings_potential: Decimal
    average_confidence: Decimal
    generated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

    @field_validator("generated_at", mode="before")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value
