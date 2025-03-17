from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Union, Tuple

from pydantic import Field

from src.schemas import BaseSchemaValidator

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
    confidence_threshold: Decimal = BaseSchemaValidator.percentage_field(
        "Minimum confidence level for including predicted transactions",
        default=Decimal('0.8')
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
    projected_balance: Decimal = BaseSchemaValidator.money_field(
        "Projected balance on this date",
        default=...
    )
    projected_income: Decimal = BaseSchemaValidator.money_field(
        "Projected income for this date",
        default=...
    )
    projected_expenses: Decimal = BaseSchemaValidator.money_field(
        "Projected expenses for this date",
        default=...
    )
    confidence_score: Decimal = BaseSchemaValidator.percentage_field(
        "Confidence score for this forecast point (0-1 scale)",
        default=...
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
    overall_confidence: Decimal = BaseSchemaValidator.percentage_field(
        "Overall confidence score for the forecast",
        default=...
    )
    summary_statistics: Dict[str, Decimal] = Field(
        ...,
        description="Summary statistics for the forecast period"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this forecast was generated in UTC timezone"
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
    confidence_threshold: Decimal = BaseSchemaValidator.percentage_field(
        "Minimum confidence level for including predicted transactions",
        default=Decimal('0.8')
    )

class AccountForecastMetrics(BaseSchemaValidator):
    """
    Schema for account-specific forecast metrics.
    
    Contains summary metrics for an account forecast.
    All datetime fields are stored in UTC timezone.
    """
    average_daily_balance: Decimal = BaseSchemaValidator.money_field(
        "Average daily balance during forecast period",
        default=...
    )
    minimum_projected_balance: Decimal = BaseSchemaValidator.money_field(
        "Minimum projected balance during forecast period",
        default=...
    )
    maximum_projected_balance: Decimal = BaseSchemaValidator.money_field(
        "Maximum projected balance during forecast period",
        default=...
    )
    average_inflow: Decimal = BaseSchemaValidator.money_field(
        "Average daily money coming in",
        default=...
    )
    average_outflow: Decimal = BaseSchemaValidator.money_field(
        "Average daily money going out",
        default=...
    )
    projected_low_balance_dates: List[datetime] = Field(
        ...,
        description="Dates with projected low balances in UTC timezone"
    )
    credit_utilization: Optional[Decimal] = BaseSchemaValidator.percentage_field(
        "Projected credit utilization (for credit accounts)",
        default=None
    )
    balance_volatility: Decimal = BaseSchemaValidator.money_field(
        "Projected volatility in account balance",
        default=...
    )
    forecast_confidence: Decimal = BaseSchemaValidator.percentage_field(
        "Overall confidence in the forecast (0-1 scale)",
        default=...
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
    projected_balance: Decimal = BaseSchemaValidator.money_field(
        "Projected balance on this date",
        default=...
    )
    projected_inflow: Decimal = BaseSchemaValidator.money_field(
        "Projected money coming in on this date",
        default=...
    )
    projected_outflow: Decimal = BaseSchemaValidator.money_field(
        "Projected money going out on this date",
        default=...
    )
    confidence_score: Decimal = BaseSchemaValidator.percentage_field(
        "Confidence score for this forecast point (0-1 scale)",
        default=...
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
    overall_confidence: Decimal = BaseSchemaValidator.percentage_field(
        "Overall confidence score for the forecast",
        default=...
    )
    timestamp: datetime = Field(
        ...,
        description="When this forecast was generated in UTC timezone"
    )
