from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import Field

from src.schemas import BaseSchemaValidator


class RecommendationType(str, Enum):
    """
    Enumeration of recommendation types provided by the system.
    
    These categories help organize different types of financial recommendations.
    """
    BILL_PAYMENT_TIMING = "bill_payment_timing"
    ACCOUNT_SELECTION = "account_selection"
    SPLIT_DISTRIBUTION = "split_distribution"
    CREDIT_UTILIZATION = "credit_utilization"


class ConfidenceLevel(str, Enum):
    """
    Enumeration of confidence levels for recommendations.
    
    Indicates how confident the system is about a recommendation.
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactMetrics(BaseSchemaValidator):
    """
    Schema for metrics describing the impact of a recommendation.
    
    Contains financial measurements of how a recommendation would affect accounts.
    """
    balance_impact: Decimal = Field(
        ..., 
        description="Impact on account balance in currency units",
        decimal_places=2
    )
    credit_utilization_impact: Optional[Decimal] = Field(
        None, 
        description="Impact on credit utilization percentage (if applicable)",
        decimal_places=2,
        ge=0, 
        le=100
    )
    risk_score: Decimal = Field(
        ..., 
        description="Risk score from 0-100, with lower being less risky",
        ge=0, 
        le=100, 
        decimal_places=1
    )
    savings_potential: Optional[Decimal] = Field(
        None, 
        description="Potential savings in currency units",
        decimal_places=2,
        ge=0
    )


class RecommendationBase(BaseSchemaValidator):
    """
    Base schema for all recommendation types.
    
    Contains common fields and validation shared by all recommendation types.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    type: RecommendationType = Field(
        ..., 
        description="Type of recommendation"
    )
    confidence: ConfidenceLevel = Field(
        ..., 
        description="Confidence level in the recommendation"
    )
    impact: ImpactMetrics = Field(
        ..., 
        description="Metrics describing the impact of implementing this recommendation"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the recommendation was created (UTC timezone)"
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation


class BillPaymentTimingRecommendation(RecommendationBase):
    """
    Schema for bill payment timing recommendations.
    
    Contains specific fields for recommendations about when to pay bills.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    type: RecommendationType = RecommendationType.BILL_PAYMENT_TIMING
    bill_id: int = Field(
        ..., 
        description="ID of the bill this recommendation relates to",
        gt=0
    )
    current_due_date: datetime = Field(
        ..., 
        description="Current scheduled due date for the bill (UTC timezone)"
    )
    recommended_date: datetime = Field(
        ..., 
        description="Recommended date to pay the bill (UTC timezone)"
    )
    reason: str = Field(
        ..., 
        description="Explanation of why this recommendation is being made",
        max_length=500
    )
    historical_pattern_strength: Decimal = Field(
        ..., 
        description="Strength of historical pattern supporting this recommendation (0-1)",
        ge=0, 
        le=1, 
        decimal_places=2
    )
    affected_accounts: List[int] = Field(
        ..., 
        description="IDs of accounts that would be affected by this recommendation"
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation


class RecommendationResponse(BaseSchemaValidator):
    """
    Schema for response containing multiple recommendations.
    
    Used for returning a batch of recommendations with summary metrics.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    recommendations: List[BillPaymentTimingRecommendation] = Field(
        ..., 
        description="List of bill payment timing recommendations"
    )
    total_savings_potential: Decimal = Field(
        ..., 
        description="Total potential savings across all recommendations",
        decimal_places=2,
        ge=0
    )
    average_confidence: Decimal = Field(
        ..., 
        description="Average confidence level across all recommendations (0-1)",
        ge=0, 
        le=1, 
        decimal_places=2
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when these recommendations were generated (UTC timezone)"
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation
