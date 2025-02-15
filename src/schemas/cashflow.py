from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, conlist

class CashflowBase(BaseModel):
    """Base schema for cashflow data"""
    forecast_date: date
    total_bills: Decimal = Field(..., ge=0)
    total_income: Decimal = Field(..., ge=0)
    balance: Decimal
    forecast: Decimal
    min_14_day: Decimal
    min_30_day: Decimal
    min_60_day: Decimal
    min_90_day: Decimal
    daily_deficit: Decimal
    yearly_deficit: Decimal
    required_income: Decimal
    hourly_rate_40: Decimal
    hourly_rate_30: Decimal
    hourly_rate_20: Decimal

class CashflowCreate(CashflowBase):
    """Schema for creating a new cashflow forecast"""
    pass

class CashflowUpdate(BaseModel):
    """Schema for updating a cashflow forecast"""
    forecast_date: Optional[date] = None
    total_bills: Optional[Decimal] = Field(None, ge=0)
    total_income: Optional[Decimal] = Field(None, ge=0)
    balance: Optional[Decimal] = None
    forecast: Optional[Decimal] = None
    min_14_day: Optional[Decimal] = None
    min_30_day: Optional[Decimal] = None
    min_60_day: Optional[Decimal] = None
    min_90_day: Optional[Decimal] = None
    daily_deficit: Optional[Decimal] = None
    yearly_deficit: Optional[Decimal] = None
    required_income: Optional[Decimal] = None
    hourly_rate_40: Optional[Decimal] = None
    hourly_rate_30: Optional[Decimal] = None
    hourly_rate_20: Optional[Decimal] = None

class CashflowInDB(CashflowBase):
    """Schema for cashflow forecast in database"""
    id: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class CashflowResponse(CashflowInDB):
    """Schema for cashflow forecast response"""
    pass

class CashflowList(BaseModel):
    """Schema for list of cashflow forecasts"""
    items: List[CashflowResponse]
    total: int

class CashflowFilters(BaseModel):
    """Schema for cashflow filtering parameters"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_balance: Optional[Decimal] = None
    max_balance: Optional[Decimal] = None

class MinimumRequired(BaseModel):
    """Schema for minimum required funds"""
    min_14_day: Decimal
    min_30_day: Decimal
    min_60_day: Decimal
    min_90_day: Decimal

class DeficitCalculation(BaseModel):
    """Schema for deficit calculations"""
    daily_deficit: Decimal
    yearly_deficit: Decimal
    required_income: Decimal

class HourlyRates(BaseModel):
    """Schema for hourly rate calculations"""
    hourly_rate_40: Decimal
    hourly_rate_30: Decimal
    hourly_rate_20: Decimal

class AccountCorrelation(BaseModel):
    """Schema for account correlation data"""
    correlation_score: Decimal = Field(..., ge=-1, le=1)
    transfer_frequency: int = Field(..., ge=0)
    common_categories: List[str]
    relationship_type: str = Field(..., pattern="^(complementary|supplementary|independent)$")

class TransferPattern(BaseModel):
    """Schema for transfer pattern data"""
    source_account_id: int
    target_account_id: int
    average_amount: Decimal
    frequency: int = Field(..., ge=0)
    typical_day_of_month: Optional[int] = Field(None, ge=1, le=31)
    category_distribution: Dict[str, Decimal]

class AccountUsagePattern(BaseModel):
    """Schema for account usage pattern data"""
    account_id: int
    primary_use: str
    average_transaction_size: Decimal
    common_merchants: List[str]
    peak_usage_days: List[int] = Field(..., max_items=31)
    category_preferences: Dict[str, Decimal]
    utilization_rate: Optional[Decimal] = Field(None, ge=0, le=1)

class BalanceDistribution(BaseModel):
    """Schema for balance distribution data"""
    account_id: int
    average_balance: Decimal
    balance_volatility: Decimal
    min_balance_30d: Decimal
    max_balance_30d: Decimal
    typical_balance_range: tuple[Decimal, Decimal]
    percentage_of_total: Decimal = Field(..., ge=0, le=1)

class AccountRiskAssessment(BaseModel):
    """Schema for account risk assessment data"""
    account_id: int
    overdraft_risk: Decimal = Field(..., ge=0, le=1)
    credit_utilization_risk: Optional[Decimal] = Field(None, ge=0, le=1)
    payment_failure_risk: Decimal = Field(..., ge=0, le=1)
    volatility_score: Decimal = Field(..., ge=0, le=1)
    overall_risk_score: Decimal = Field(..., ge=0, le=1)

class CrossAccountAnalysis(BaseModel):
    """Schema for comprehensive cross-account analysis"""
    correlations: Dict[str, Dict[str, AccountCorrelation]]
    transfer_patterns: List[TransferPattern]
    usage_patterns: Dict[int, AccountUsagePattern]
    balance_distribution: Dict[int, BalanceDistribution]
    risk_assessment: Dict[int, AccountRiskAssessment]
    timestamp: date
