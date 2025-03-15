from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from src.schemas import BaseSchemaValidator

class AccountImpact(BaseSchemaValidator):
    """
    Schema for representing the impact of a decision on an account.
    
    Contains current and projected metrics for the account.
    """
    account_id: int = Field(
        ..., 
        description="ID of the account being analyzed",
        gt=0
    )
    current_balance: Decimal = Field(
        ..., 
        description="Current balance in the account",
        decimal_places=2
    )
    projected_balance: Decimal = Field(
        ..., 
        description="Projected balance after the analyzed action",
        decimal_places=2
    )
    current_credit_utilization: Optional[Decimal] = Field(
        None, 
        description="Current credit utilization percentage (if applicable)",
        decimal_places=2,
        ge=0, 
        le=100
    )
    projected_credit_utilization: Optional[Decimal] = Field(
        None, 
        description="Projected credit utilization percentage after the analyzed action",
        decimal_places=2,
        ge=0, 
        le=100
    )
    risk_score: int = Field(
        ...,
        description="Risk score from 0-100, with lower being less risky",
        ge=0, 
        le=100
    )

class CashflowImpact(BaseSchemaValidator):
    """
    Schema for representing the impact of a decision on cashflow.
    
    Contains financial metrics for a specific date in the cashflow timeline.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date for this cashflow snapshot (UTC timezone)"
    )
    total_bills: Decimal = Field(
        ..., 
        description="Total bills due on this date",
        decimal_places=2,
        ge=0
    )
    available_funds: Decimal = Field(
        ..., 
        description="Available funds on this date",
        decimal_places=2
    )
    projected_deficit: Optional[Decimal] = Field(
        None, 
        description="Projected deficit amount if available funds are insufficient",
        decimal_places=2
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation

class RiskFactor(BaseSchemaValidator):
    """
    Schema for representing a risk factor in the impact analysis.
    
    Contains information about a specific risk associated with a financial decision.
    """
    name: str = Field(
        ..., 
        description="Name of the risk factor",
        max_length=100
    )
    severity: int = Field(
        ..., 
        description="Severity rating from 0-100, with higher being more severe",
        ge=0, 
        le=100
    )
    description: str = Field(
        ..., 
        description="Detailed description of the risk factor",
        max_length=500
    )

class SplitImpactAnalysis(BaseSchemaValidator):
    """
    Schema for comprehensive analysis of bill split impacts.
    
    Contains detailed analysis of how a bill split configuration affects accounts,
    cashflow, and overall financial risk.
    """
    total_amount: Decimal = Field(
        ..., 
        description="Total amount of the liability being analyzed",
        decimal_places=2,
        gt=0
    )
    account_impacts: List[AccountImpact] = Field(
        ..., 
        description="Impacts on individual accounts"
    )
    cashflow_impacts: List[CashflowImpact] = Field(
        ..., 
        description="Impacts on cashflow over time"
    )
    risk_factors: List[RiskFactor] = Field(
        ..., 
        description="Identified risk factors"
    )
    overall_risk_score: int = Field(
        ..., 
        description="Overall risk score from 0-100, with lower being less risky",
        ge=0, 
        le=100
    )
    recommendations: List[str] = Field(
        ..., 
        description="Recommendations based on the analysis"
    )

class SplitImpactRequest(BaseSchemaValidator):
    """
    Schema for requesting a bill split impact analysis.
    
    Contains parameters for analyzing the impact of a specific bill split configuration.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    liability_id: int = Field(
        ..., 
        description="ID of the liability to analyze",
        gt=0
    )
    splits: List[dict] = Field(
        ..., 
        description="Split configuration to analyze"
    )
    analysis_period_days: int = Field(
        default=90, 
        description="Number of days to include in the analysis period",
        ge=14, 
        le=365
    )
    start_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Start date for the analysis period (UTC timezone)"
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation
