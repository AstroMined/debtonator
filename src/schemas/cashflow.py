from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field, conlist

class CashflowBase(BaseModel):
    """Base schema for cashflow data"""
    forecast_date: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
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
    forecast_date: Optional[datetime] = None
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

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
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
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

class CustomForecastParameters(BaseModel):
    """Schema for custom forecast parameters"""
    start_date: datetime
    end_date: datetime
    include_pending: bool = True
    account_ids: Optional[List[int]] = None
    categories: Optional[List[str]] = None
    confidence_threshold: Decimal = Field(default=Decimal('0.8'), ge=0, le=1)
    include_recurring: bool = True
    include_historical_patterns: bool = True

class CustomForecastResult(BaseModel):
    """Schema for custom forecast results"""
    date: datetime
    projected_balance: Decimal
    projected_income: Decimal
    projected_expenses: Decimal
    confidence_score: Decimal = Field(..., ge=0, le=1)
    contributing_factors: Dict[str, Decimal]
    risk_factors: Dict[str, Decimal]

class CustomForecastResponse(BaseModel):
    """Schema for custom forecast response"""
    parameters: CustomForecastParameters
    results: List[CustomForecastResult]
    overall_confidence: Decimal = Field(..., ge=0, le=1)
    summary_statistics: Dict[str, Decimal]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

class HistoricalTrendMetrics(BaseModel):
    """Schema for historical trend metrics"""
    average_daily_change: Decimal
    volatility: Decimal
    trend_direction: str = Field(..., pattern="^(increasing|decreasing|stable)$")
    trend_strength: Decimal = Field(..., ge=0, le=1)
    seasonal_factors: Dict[str, Decimal]
    confidence_score: Decimal = Field(..., ge=0, le=1)

class HistoricalPeriodAnalysis(BaseModel):
    """Schema for analyzing specific historical periods"""
    period_start: datetime
    period_end: datetime
    average_balance: Decimal
    peak_balance: Decimal
    lowest_balance: Decimal
    total_inflow: Decimal
    total_outflow: Decimal
    net_change: Decimal
    significant_events: List[Dict[str, str]]

class SeasonalityAnalysis(BaseModel):
    """Schema for seasonal patterns"""
    monthly_patterns: Dict[int, Decimal]  # 1-12 for months
    day_of_week_patterns: Dict[int, Decimal]  # 0-6 for days
    day_of_month_patterns: Dict[int, Decimal]  # 1-31 for days
    holiday_impacts: Dict[str, Decimal]
    seasonal_strength: Decimal = Field(..., ge=0, le=1)

class HistoricalTrendsResponse(BaseModel):
    """Schema for historical trends analysis response"""
    metrics: HistoricalTrendMetrics
    period_analysis: List[HistoricalPeriodAnalysis]
    seasonality: SeasonalityAnalysis
    timestamp: datetime

class AccountForecastRequest(BaseModel):
    """Schema for account-specific forecast request"""
    account_id: int
    start_date: datetime
    end_date: datetime
    include_pending: bool = True
    include_recurring: bool = True
    include_transfers: bool = True
    confidence_threshold: Decimal = Field(default=Decimal('0.8'), ge=0, le=1)

class AccountForecastMetrics(BaseModel):
    """Schema for account-specific forecast metrics"""
    average_daily_balance: Decimal
    minimum_projected_balance: Decimal
    maximum_projected_balance: Decimal
    average_inflow: Decimal
    average_outflow: Decimal
    projected_low_balance_dates: List[datetime]
    credit_utilization: Optional[Decimal] = Field(None, ge=0, le=1)  # Only for credit accounts
    balance_volatility: Decimal
    forecast_confidence: Decimal = Field(..., ge=0, le=1)

class AccountForecastResult(BaseModel):
    """Schema for account-specific forecast result"""
    date: datetime
    projected_balance: Decimal
    projected_inflow: Decimal
    projected_outflow: Decimal
    confidence_score: Decimal = Field(..., ge=0, le=1)
    contributing_transactions: List[Dict[str, Union[Decimal, str]]]
    warning_flags: List[str] = Field(default_factory=list)

class AccountForecastResponse(BaseModel):
    """Schema for account-specific forecast response"""
    account_id: int
    forecast_period: tuple[datetime, datetime]
    metrics: AccountForecastMetrics
    daily_forecasts: List[AccountForecastResult]
    overall_confidence: Decimal = Field(..., ge=0, le=1)
    timestamp: datetime

class CrossAccountAnalysis(BaseModel):
    """Schema for comprehensive cross-account analysis"""
    correlations: Dict[str, Dict[str, AccountCorrelation]]
    transfer_patterns: List[TransferPattern]
    usage_patterns: Dict[int, AccountUsagePattern]
    balance_distribution: Dict[int, BalanceDistribution]
    risk_assessment: Dict[int, AccountRiskAssessment]
    timestamp: datetime
