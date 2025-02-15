from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class AccountImpact(BaseModel):
    account_id: int
    current_balance: Decimal
    projected_balance: Decimal
    current_credit_utilization: Optional[Decimal] = None
    projected_credit_utilization: Optional[Decimal] = None
    risk_score: int = Field(ge=0, le=100)

class CashflowImpact(BaseModel):
    date: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    total_bills: Decimal
    available_funds: Decimal
    projected_deficit: Optional[Decimal] = None

class RiskFactor(BaseModel):
    name: str
    severity: int = Field(ge=0, le=100)
    description: str

class SplitImpactAnalysis(BaseModel):
    total_amount: Decimal
    account_impacts: List[AccountImpact]
    cashflow_impacts: List[CashflowImpact]
    risk_factors: List[RiskFactor]
    overall_risk_score: int = Field(ge=0, le=100)
    recommendations: List[str]

class SplitImpactRequest(BaseModel):
    liability_id: int
    splits: List[dict]
    analysis_period_days: int = Field(default=90, ge=14, le=365)
