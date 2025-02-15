from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


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
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BillPaymentTimingRecommendation(RecommendationBase):
    type: RecommendationType = RecommendationType.BILL_PAYMENT_TIMING
    bill_id: int
    current_due_date: date
    recommended_date: date
    reason: str
    historical_pattern_strength: Decimal = Field(ge=0, le=1)
    affected_accounts: List[int]


class RecommendationResponse(BaseModel):
    recommendations: List[BillPaymentTimingRecommendation]
    total_savings_potential: Decimal
    average_confidence: Decimal
