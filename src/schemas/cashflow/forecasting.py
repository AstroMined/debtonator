from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

from pydantic import Field

from src.schemas import (
    BaseSchemaValidator,
    MoneyDecimal,
    MoneyDict,
    PercentageDecimal,
    PercentageDict,
)


class CustomForecastParameters(BaseSchemaValidator):
    """
    Schema for custom forecast parameters.

    Defines parameters for generating a custom cashflow forecast.
    All datetime fields are stored in UTC timezone.
    """

    start_date: datetime = Field(
        ..., description="Start date for the forecast in UTC timezone"
    )
    end_date: datetime = Field(
        ..., description="End date for the forecast in UTC timezone"
    )
    include_pending: bool = Field(
        True, description="Whether to include pending transactions"
    )
    account_ids: Optional[List[int]] = Field(
        None, description="Specific accounts to include in forecast"
    )
    categories: Optional[List[str]] = Field(
        None, description="Specific categories to include in forecast"
    )
    confidence_threshold: PercentageDecimal = Field(
        default=Decimal("0.8"),
        description="Minimum confidence level for including predicted transactions",
    )
    include_recurring: bool = Field(
        True, description="Whether to include recurring transactions"
    )
    include_historical_patterns: bool = Field(
        True, description="Whether to include patterns from historical data"
    )


class CustomForecastResult(BaseSchemaValidator):
    """
    Schema for custom forecast results.

    Contains daily forecast results for a custom forecast period.
    All datetime fields are stored in UTC timezone.
    """

    date: datetime = Field(
        ..., description="Date of this forecast point in UTC timezone"
    )
    projected_balance: MoneyDecimal = Field(
        ..., description="Projected balance on this date"
    )
    projected_income: MoneyDecimal = Field(
        ..., description="Projected income for this date"
    )
    projected_expenses: MoneyDecimal = Field(
        ..., description="Projected expenses for this date"
    )
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence score for this forecast point (0-1 scale)"
    )
    contributing_factors: PercentageDict = Field(
        ..., description="Factors contributing to this forecast and their weights"
    )
    risk_factors: PercentageDict = Field(
        ..., description="Risk factors for this forecast and their weights"
    )


class CustomForecastResponse(BaseSchemaValidator):
    """
    Schema for custom forecast response.

    Contains the complete custom forecast results with metadata.
    All datetime fields are stored in UTC timezone.
    """

    parameters: CustomForecastParameters = Field(
        ..., description="Parameters used for this forecast"
    )
    results: List[CustomForecastResult] = Field(
        ..., description="Daily forecast results"
    )
    overall_confidence: PercentageDecimal = Field(
        ..., description="Overall confidence score for the forecast"
    )
    summary_statistics: MoneyDict = Field(
        ..., description="Summary statistics for the forecast period"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this forecast was generated in UTC timezone",
    )


class AccountForecastRequest(BaseSchemaValidator):
    """
    Schema for account-specific forecast request.

    Contains parameters for generating an account-specific forecast.
    All datetime fields are stored in UTC timezone.
    """

    account_id: int = Field(..., description="ID of the account to forecast")
    start_date: datetime = Field(
        ..., description="Start date for the forecast in UTC timezone"
    )
    end_date: datetime = Field(
        ..., description="End date for the forecast in UTC timezone"
    )
    include_pending: bool = Field(
        True, description="Whether to include pending transactions"
    )
    include_recurring: bool = Field(
        True, description="Whether to include recurring transactions"
    )
    include_transfers: bool = Field(
        True, description="Whether to include inter-account transfers"
    )
    confidence_threshold: PercentageDecimal = Field(
        default=Decimal("0.8"),
        description="Minimum confidence level for including predicted transactions",
    )


class AccountForecastMetrics(BaseSchemaValidator):
    """
    Schema for account-specific forecast metrics.

    Contains summary metrics for an account forecast.
    All datetime fields are stored in UTC timezone.
    """

    average_daily_balance: MoneyDecimal = Field(
        ..., description="Average daily balance during forecast period"
    )
    minimum_projected_balance: MoneyDecimal = Field(
        ..., description="Minimum projected balance during forecast period"
    )
    maximum_projected_balance: MoneyDecimal = Field(
        ..., description="Maximum projected balance during forecast period"
    )
    average_inflow: MoneyDecimal = Field(
        ..., description="Average daily money coming in"
    )
    average_outflow: MoneyDecimal = Field(
        ..., description="Average daily money going out"
    )
    projected_low_balance_dates: List[datetime] = Field(
        ..., description="Dates with projected low balances in UTC timezone"
    )
    credit_utilization: Optional[PercentageDecimal] = Field(
        default=None, description="Projected credit utilization (for credit accounts)"
    )
    balance_volatility: MoneyDecimal = Field(
        ..., description="Projected volatility in account balance"
    )
    forecast_confidence: PercentageDecimal = Field(
        ..., description="Overall confidence in the forecast (0-1 scale)"
    )


class AccountForecastResult(BaseSchemaValidator):
    """
    Schema for account-specific forecast result.

    Contains daily forecast results for a specific account.
    All datetime fields are stored in UTC timezone.
    """

    date: datetime = Field(
        ..., description="Date of this forecast point in UTC timezone"
    )
    projected_balance: MoneyDecimal = Field(
        ..., description="Projected balance on this date"
    )
    projected_inflow: MoneyDecimal = Field(
        ..., description="Projected money coming in on this date"
    )
    projected_outflow: MoneyDecimal = Field(
        ..., description="Projected money going out on this date"
    )
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence score for this forecast point (0-1 scale)"
    )
    contributing_transactions: List[Dict[str, Union[MoneyDecimal, str]]] = Field(
        ..., description="Transactions contributing to this forecast point"
    )
    warning_flags: List[str] = Field(
        default_factory=list, description="Warning indicators for this forecast point"
    )


class AccountForecastResponse(BaseSchemaValidator):
    """
    Schema for account-specific forecast response.

    Contains the complete account forecast with metadata.
    All datetime fields are stored in UTC timezone.
    """

    account_id: int = Field(..., description="ID of the account")
    forecast_period: Tuple[datetime, datetime] = Field(
        ..., description="Start and end dates of the forecast in UTC timezone"
    )
    metrics: AccountForecastMetrics = Field(
        ..., description="Summary metrics for the forecast"
    )
    daily_forecasts: List[AccountForecastResult] = Field(
        ..., description="Daily forecast results"
    )
    overall_confidence: PercentageDecimal = Field(
        ..., description="Overall confidence score for the forecast"
    )
    timestamp: datetime = Field(
        ..., description="When this forecast was generated in UTC timezone"
    )
