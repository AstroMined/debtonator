from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Union, Tuple

from pydantic import Field, ConfigDict

from src.schemas import BaseSchemaValidator

class CashflowBase(BaseSchemaValidator):
    """
    Base schema for cashflow data.
    
    Contains all the core fields required for cashflow forecasting.
    All datetime fields are stored in UTC timezone.
    """
    forecast_date: datetime = Field(
        default_factory=datetime.now,  # BaseSchemaValidator handles UTC validation
        description="Date and time of forecast in UTC timezone"
    )
    total_bills: Decimal = Field(
        ..., 
        ge=0,
        decimal_places=2,
        description="Total amount of bills in forecast period"
    )
    total_income: Decimal = Field(
        ..., 
        ge=0,
        decimal_places=2, 
        description="Total amount of income in forecast period"
    )
    balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Current balance across all accounts"
    )
    forecast: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected balance at end of forecast period"
    )
    min_14_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 14 days"
    )
    min_30_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 30 days"
    )
    min_60_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 60 days"
    )
    min_90_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 90 days"
    )
    daily_deficit: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average daily deficit amount"
    )
    yearly_deficit: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected yearly deficit"
    )
    required_income: Decimal = Field(
        ...,
        decimal_places=2,
        description="Income required to cover bills with tax consideration"
    )
    hourly_rate_40: Decimal = Field(
        ...,
        decimal_places=2,
        description="Hourly rate needed at 40 hours per week"
    )
    hourly_rate_30: Decimal = Field(
        ...,
        decimal_places=2,
        description="Hourly rate needed at 30 hours per week"
    )
    hourly_rate_20: Decimal = Field(
        ...,
        decimal_places=2,
        description="Hourly rate needed at 20 hours per week"
    )

class CashflowCreate(CashflowBase):
    """
    Schema for creating a new cashflow forecast.
    
    Extends the base schema without adding additional fields.
    """
    pass

class CashflowUpdate(BaseSchemaValidator):
    """
    Schema for updating a cashflow forecast.
    
    All fields are optional to allow partial updates.
    """
    forecast_date: Optional[datetime] = Field(
        None,
        description="Date and time of forecast in UTC timezone"
    )
    total_bills: Optional[Decimal] = Field(
        None, 
        ge=0,
        decimal_places=2,
        description="Total amount of bills in forecast period"
    )
    total_income: Optional[Decimal] = Field(
        None, 
        ge=0,
        decimal_places=2,
        description="Total amount of income in forecast period"
    )
    balance: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Current balance across all accounts"
    )
    forecast: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Projected balance at end of forecast period"
    )
    min_14_day: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Minimum funds required for next 14 days"
    )
    min_30_day: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Minimum funds required for next 30 days"
    )
    min_60_day: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Minimum funds required for next 60 days"
    )
    min_90_day: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Minimum funds required for next 90 days"
    )
    daily_deficit: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Average daily deficit amount"
    )
    yearly_deficit: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Projected yearly deficit"
    )
    required_income: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Income required to cover bills with tax consideration"
    )
    hourly_rate_40: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Hourly rate needed at 40 hours per week"
    )
    hourly_rate_30: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Hourly rate needed at 30 hours per week"
    )
    hourly_rate_20: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Hourly rate needed at 20 hours per week"
    )

class CashflowInDB(CashflowBase):
    """
    Schema for cashflow forecast in database.
    
    Includes system-generated fields like ID and timestamps.
    All datetime fields are stored in UTC timezone.
    """
    id: int = Field(..., description="Unique identifier for the cashflow record")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when the record was last updated in UTC timezone"
    )

class CashflowResponse(CashflowInDB):
    """
    Schema for cashflow forecast response.
    
    Extends the database schema for API responses.
    """
    pass

class CashflowList(BaseSchemaValidator):
    """
    Schema for list of cashflow forecasts.
    
    Used for paginated responses of multiple cashflow records.
    """
    items: List[CashflowResponse] = Field(
        ...,
        description="List of cashflow forecast records"
    )
    total: int = Field(
        ...,
        description="Total number of records available"
    )

class CashflowFilters(BaseSchemaValidator):
    """
    Schema for cashflow filtering parameters.
    
    Used to filter cashflow forecasts by date range and balance thresholds.
    All datetime fields are stored in UTC timezone.
    """
    start_date: Optional[datetime] = Field(
        None,
        description="Filter cashflows starting from this date in UTC timezone"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Filter cashflows until this date in UTC timezone"
    )
    min_balance: Optional[Decimal] = Field(
        None,
        description="Minimum balance threshold for filtering"
    )
    max_balance: Optional[Decimal] = Field(
        None,
        description="Maximum balance threshold for filtering"
    )

class MinimumRequired(BaseSchemaValidator):
    """
    Schema for minimum required funds.
    
    Contains minimum funds required for different time periods.
    """
    min_14_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 14 days"
    )
    min_30_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 30 days"
    )
    min_60_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 60 days"
    )
    min_90_day: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum funds required for next 90 days"
    )

class DeficitCalculation(BaseSchemaValidator):
    """
    Schema for deficit calculations.
    
    Contains various deficit metrics for financial planning.
    """
    daily_deficit: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average daily deficit amount"
    )
    yearly_deficit: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected yearly deficit"
    )
    required_income: Decimal = Field(
        ...,
        decimal_places=2,
        description="Income required to cover bills with tax consideration"
    )

class HourlyRates(BaseSchemaValidator):
    """
    Schema for hourly rate calculations.
    
    Contains hourly rates needed at different weekly work hours.
    """
    hourly_rate_40: Decimal = Field(
        ...,
        decimal_places=2,
        description="Hourly rate needed at 40 hours per week"
    )
    hourly_rate_30: Decimal = Field(
        ...,
        decimal_places=2,
        description="Hourly rate needed at 30 hours per week"
    )
    hourly_rate_20: Decimal = Field(
        ...,
        decimal_places=2,
        description="Hourly rate needed at 20 hours per week"
    )

class AccountCorrelation(BaseSchemaValidator):
    """
    Schema for account correlation data.
    
    Describes the relationship between two accounts based on transaction patterns.
    """
    correlation_score: Decimal = Field(
        ..., 
        ge=-1, 
        le=1,
        decimal_places=2,
        description="Correlation coefficient between accounts (-1 to 1)"
    )
    transfer_frequency: int = Field(
        ..., 
        ge=0,
        description="Number of transfers between accounts per month"
    )
    common_categories: List[str] = Field(
        ...,
        max_length=100,
        description="Categories commonly used across both accounts"
    )
    relationship_type: str = Field(
        ..., 
        pattern="^(complementary|supplementary|independent)$",
        description="Type of relationship between accounts"
    )

class TransferPattern(BaseSchemaValidator):
    """
    Schema for transfer pattern data.
    
    Describes patterns of fund transfers between accounts.
    """
    source_account_id: int = Field(
        ...,
        description="ID of the source account for transfers"
    )
    target_account_id: int = Field(
        ...,
        description="ID of the target account for transfers"
    )
    average_amount: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average amount transferred"
    )
    frequency: int = Field(
        ..., 
        ge=0,
        description="Number of transfers per month"
    )
    typical_day_of_month: Optional[int] = Field(
        None, 
        ge=1, 
        le=31,
        description="Day of month when transfers typically occur"
    )
    category_distribution: Dict[str, Decimal] = Field(
        ...,
        description="Distribution of transfer categories and their proportions"
    )

class AccountUsagePattern(BaseSchemaValidator):
    """
    Schema for account usage pattern data.
    
    Describes how an account is typically used based on transaction history.
    """
    account_id: int = Field(
        ...,
        description="ID of the account"
    )
    primary_use: str = Field(
        ...,
        description="Primary purpose of the account"
    )
    average_transaction_size: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average size of transactions in this account"
    )
    common_merchants: List[str] = Field(
        ...,
        max_length=100,
        description="Most common merchants for this account"
    )
    peak_usage_days: List[int] = Field(
        ..., 
        max_length=31,
        description="Days of the month with highest transaction volume (1-31)"
    )
    category_preferences: Dict[str, Decimal] = Field(
        ...,
        description="Categories and their usage proportions"
    )
    utilization_rate: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Credit utilization rate (for credit accounts)"
    )

class BalanceDistribution(BaseSchemaValidator):
    """
    Schema for balance distribution data.
    
    Describes the distribution of funds across accounts.
    """
    account_id: int = Field(
        ...,
        description="ID of the account"
    )
    average_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average account balance"
    )
    balance_volatility: Decimal = Field(
        ...,
        decimal_places=2,
        description="Standard deviation of balance over time"
    )
    min_balance_30d: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum balance in last 30 days"
    )
    max_balance_30d: Decimal = Field(
        ...,
        decimal_places=2,
        description="Maximum balance in last 30 days"
    )
    typical_balance_range: Tuple[Decimal, Decimal] = Field(
        ...,
        description="Typical range of account balance (min, max)"
    )
    percentage_of_total: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=4,
        description="Percentage of total funds across all accounts"
    )

class AccountRiskAssessment(BaseSchemaValidator):
    """
    Schema for account risk assessment data.
    
    Provides risk metrics for an account based on transaction history.
    """
    account_id: int = Field(
        ...,
        description="ID of the account"
    )
    overdraft_risk: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Risk of overdraft (0-1 scale)"
    )
    credit_utilization_risk: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Risk from high credit utilization (0-1 scale)"
    )
    payment_failure_risk: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Risk of payment failure (0-1 scale)"
    )
    volatility_score: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Score representing balance volatility (0-1 scale)"
    )
    overall_risk_score: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Overall risk score (0-1 scale)"
    )

class CustomForecastParameters(BaseSchemaValidator):
    """
    Schema for custom forecast parameters.
    
    Defines parameters for generating a custom cashflow forecast.
    All datetime fields are stored in UTC timezone.
    """
    start_date: datetime = Field(
        ...,
        description="Start date for the forecast in UTC timezone"
    )
    end_date: datetime = Field(
        ...,
        description="End date for the forecast in UTC timezone"
    )
    include_pending: bool = Field(
        True,
        description="Whether to include pending transactions"
    )
    account_ids: Optional[List[int]] = Field(
        None,
        description="Specific accounts to include in forecast"
    )
    categories: Optional[List[str]] = Field(
        None,
        description="Specific categories to include in forecast"
    )
    confidence_threshold: Decimal = Field(
        default=Decimal('0.8'), 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Minimum confidence level for including predicted transactions"
    )
    include_recurring: bool = Field(
        True,
        description="Whether to include recurring transactions"
    )
    include_historical_patterns: bool = Field(
        True,
        description="Whether to include patterns from historical data"
    )

class CustomForecastResult(BaseSchemaValidator):
    """
    Schema for custom forecast results.
    
    Contains daily forecast results for a custom forecast period.
    All datetime fields are stored in UTC timezone.
    """
    date: datetime = Field(
        ...,
        description="Date of this forecast point in UTC timezone"
    )
    projected_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected balance on this date"
    )
    projected_income: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected income for this date"
    )
    projected_expenses: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected expenses for this date"
    )
    confidence_score: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Confidence score for this forecast point (0-1 scale)"
    )
    contributing_factors: Dict[str, Decimal] = Field(
        ...,
        description="Factors contributing to this forecast and their weights"
    )
    risk_factors: Dict[str, Decimal] = Field(
        ...,
        description="Risk factors for this forecast and their weights"
    )

class CustomForecastResponse(BaseSchemaValidator):
    """
    Schema for custom forecast response.
    
    Contains the complete custom forecast results with metadata.
    All datetime fields are stored in UTC timezone.
    """
    parameters: CustomForecastParameters = Field(
        ...,
        description="Parameters used for this forecast"
    )
    results: List[CustomForecastResult] = Field(
        ...,
        description="Daily forecast results"
    )
    overall_confidence: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Overall confidence score for the forecast"
    )
    summary_statistics: Dict[str, Decimal] = Field(
        ...,
        description="Summary statistics for the forecast period"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this forecast was generated in UTC timezone"
    )

class HistoricalTrendMetrics(BaseSchemaValidator):
    """
    Schema for historical trend metrics.
    
    Contains metrics describing historical trends in account balances.
    """
    average_daily_change: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average daily change in balance"
    )
    volatility: Decimal = Field(
        ...,
        decimal_places=2,
        description="Standard deviation of daily changes"
    )
    trend_direction: str = Field(
        ..., 
        pattern="^(increasing|decreasing|stable)$",
        description="Overall direction of the trend"
    )
    trend_strength: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Strength of the trend (0-1 scale)"
    )
    seasonal_factors: Dict[str, Decimal] = Field(
        ...,
        description="Seasonal factors affecting the trend"
    )
    confidence_score: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Confidence in the trend analysis (0-1 scale)"
    )

class HistoricalPeriodAnalysis(BaseSchemaValidator):
    """
    Schema for analyzing specific historical periods.
    
    Provides detailed analysis of a specific date range in account history.
    All datetime fields are stored in UTC timezone.
    """
    period_start: datetime = Field(
        ...,
        description="Start date of this analysis period in UTC timezone"
    )
    period_end: datetime = Field(
        ...,
        description="End date of this analysis period in UTC timezone"
    )
    average_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average balance during this period"
    )
    peak_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Highest balance during this period"
    )
    lowest_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Lowest balance during this period"
    )
    total_inflow: Decimal = Field(
        ...,
        decimal_places=2,
        description="Total money coming in during this period"
    )
    total_outflow: Decimal = Field(
        ...,
        decimal_places=2,
        description="Total money going out during this period"
    )
    net_change: Decimal = Field(
        ...,
        decimal_places=2,
        description="Net change in balance during this period"
    )
    significant_events: List[Dict[str, str]] = Field(
        ...,
        description="Significant financial events during this period"
    )

class SeasonalityAnalysis(BaseSchemaValidator):
    """
    Schema for seasonal patterns.
    
    Describes seasonal patterns in financial activity.
    """
    monthly_patterns: Dict[int, Decimal] = Field(
        ...,
        description="Patterns by month (1-12 for Jan-Dec)"
    )
    day_of_week_patterns: Dict[int, Decimal] = Field(
        ...,
        description="Patterns by day of week (0-6 for Sun-Sat)"
    )
    day_of_month_patterns: Dict[int, Decimal] = Field(
        ...,
        description="Patterns by day of month (1-31)"
    )
    holiday_impacts: Dict[str, Decimal] = Field(
        ...,
        description="Impact of holidays on financial patterns"
    )
    seasonal_strength: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Overall strength of seasonality (0-1 scale)"
    )

class HistoricalTrendsResponse(BaseSchemaValidator):
    """
    Schema for historical trends analysis response.
    
    Contains complete analysis of historical financial trends.
    All datetime fields are stored in UTC timezone.
    """
    metrics: HistoricalTrendMetrics = Field(
        ...,
        description="Overall metrics for historical trends"
    )
    period_analysis: List[HistoricalPeriodAnalysis] = Field(
        ...,
        description="Analysis of specific historical periods"
    )
    seasonality: SeasonalityAnalysis = Field(
        ...,
        description="Analysis of seasonal patterns"
    )
    timestamp: datetime = Field(
        ...,
        description="When this analysis was generated in UTC timezone"
    )

class AccountForecastRequest(BaseSchemaValidator):
    """
    Schema for account-specific forecast request.
    
    Contains parameters for generating an account-specific forecast.
    All datetime fields are stored in UTC timezone.
    """
    account_id: int = Field(
        ...,
        description="ID of the account to forecast"
    )
    start_date: datetime = Field(
        ...,
        description="Start date for the forecast in UTC timezone"
    )
    end_date: datetime = Field(
        ...,
        description="End date for the forecast in UTC timezone"
    )
    include_pending: bool = Field(
        True,
        description="Whether to include pending transactions"
    )
    include_recurring: bool = Field(
        True,
        description="Whether to include recurring transactions"
    )
    include_transfers: bool = Field(
        True,
        description="Whether to include inter-account transfers"
    )
    confidence_threshold: Decimal = Field(
        default=Decimal('0.8'), 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Minimum confidence level for including predicted transactions"
    )

class AccountForecastMetrics(BaseSchemaValidator):
    """
    Schema for account-specific forecast metrics.
    
    Contains summary metrics for an account forecast.
    All datetime fields are stored in UTC timezone.
    """
    average_daily_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average daily balance during forecast period"
    )
    minimum_projected_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Minimum projected balance during forecast period"
    )
    maximum_projected_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Maximum projected balance during forecast period"
    )
    average_inflow: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average daily money coming in"
    )
    average_outflow: Decimal = Field(
        ...,
        decimal_places=2,
        description="Average daily money going out"
    )
    projected_low_balance_dates: List[datetime] = Field(
        ...,
        description="Dates with projected low balances in UTC timezone"
    )
    credit_utilization: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Projected credit utilization (for credit accounts)"
    )
    balance_volatility: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected volatility in account balance"
    )
    forecast_confidence: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Overall confidence in the forecast (0-1 scale)"
    )

class AccountForecastResult(BaseSchemaValidator):
    """
    Schema for account-specific forecast result.
    
    Contains daily forecast results for a specific account.
    All datetime fields are stored in UTC timezone.
    """
    date: datetime = Field(
        ...,
        description="Date of this forecast point in UTC timezone"
    )
    projected_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected balance on this date"
    )
    projected_inflow: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected money coming in on this date"
    )
    projected_outflow: Decimal = Field(
        ...,
        decimal_places=2,
        description="Projected money going out on this date"
    )
    confidence_score: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Confidence score for this forecast point (0-1 scale)"
    )
    contributing_transactions: List[Dict[str, Union[Decimal, str]]] = Field(
        ...,
        description="Transactions contributing to this forecast point"
    )
    warning_flags: List[str] = Field(
        default_factory=list,
        description="Warning indicators for this forecast point"
    )

class AccountForecastResponse(BaseSchemaValidator):
    """
    Schema for account-specific forecast response.
    
    Contains the complete account forecast with metadata.
    All datetime fields are stored in UTC timezone.
    """
    account_id: int = Field(
        ...,
        description="ID of the account"
    )
    forecast_period: Tuple[datetime, datetime] = Field(
        ...,
        description="Start and end dates of the forecast in UTC timezone"
    )
    metrics: AccountForecastMetrics = Field(
        ...,
        description="Summary metrics for the forecast"
    )
    daily_forecasts: List[AccountForecastResult] = Field(
        ...,
        description="Daily forecast results"
    )
    overall_confidence: Decimal = Field(
        ..., 
        ge=0, 
        le=1,
        decimal_places=2,
        description="Overall confidence score for the forecast"
    )
    timestamp: datetime = Field(
        ...,
        description="When this forecast was generated in UTC timezone"
    )

class CrossAccountAnalysis(BaseSchemaValidator):
    """
    Schema for comprehensive cross-account analysis.
    
    Provides a holistic view of relationships between accounts.
    All datetime fields are stored in UTC timezone.
    """
    correlations: Dict[str, Dict[str, AccountCorrelation]] = Field(
        ...,
        description="Correlation data between account pairs"
    )
    transfer_patterns: List[TransferPattern] = Field(
        ...,
        description="Patterns of transfers between accounts"
    )
    usage_patterns: Dict[int, AccountUsagePattern] = Field(
        ...,
        description="Usage patterns for each account"
    )
    balance_distribution: Dict[int, BalanceDistribution] = Field(
        ...,
        description="Balance distribution across accounts"
    )
    risk_assessment: Dict[int, AccountRiskAssessment] = Field(
        ...,
        description="Risk assessment for each account"
    )
    timestamp: datetime = Field(
        ...,
        description="When this analysis was generated in UTC timezone"
    )
