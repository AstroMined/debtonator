from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from pydantic import Field

from src.schemas import (BaseSchemaValidator, CorrelationDecimal, IntMoneyDict,
                         IntPercentageDict, MoneyDecimal, MoneyDict,
                         PercentageDecimal, PercentageDict)


class AccountCorrelation(BaseSchemaValidator):
    """
    Schema for account correlation data.

    Describes the relationship between two accounts based on transaction patterns.
    Implements ADR-013 with standardized precision validation.
    """

    correlation_score: CorrelationDecimal = Field(
        ..., description="Correlation coefficient between accounts (-1 to 1)"
    )
    transfer_frequency: int = Field(
        ..., ge=0, description="Number of transfers between accounts per month"
    )
    common_categories: List[str] = Field(
        ..., max_length=100, description="Categories commonly used across both accounts"
    )
    relationship_type: str = Field(
        ...,
        pattern="^(complementary|supplementary|independent)$",
        description="Type of relationship between accounts",
    )


class TransferPattern(BaseSchemaValidator):
    """
    Schema for transfer pattern data.

    Describes patterns of fund transfers between accounts.
    Implements ADR-013 with standardized money field validation.
    """

    source_account_id: int = Field(
        ..., description="ID of the source account for transfers"
    )
    target_account_id: int = Field(
        ..., description="ID of the target account for transfers"
    )
    average_amount: MoneyDecimal = Field(..., description="Average amount transferred")
    frequency: int = Field(..., ge=0, description="Number of transfers per month")
    typical_day_of_month: Optional[int] = Field(
        None, ge=1, le=31, description="Day of month when transfers typically occur"
    )
    category_distribution: PercentageDict = Field(
        ..., description="Distribution of transfer categories and their proportions"
    )


class AccountUsagePattern(BaseSchemaValidator):
    """
    Schema for account usage pattern data.

    Describes how an account is typically used based on transaction history.
    Implements ADR-013 with standardized money and percentage field validation.
    """

    account_id: int = Field(..., description="ID of the account")
    primary_use: str = Field(..., description="Primary purpose of the account")
    average_transaction_size: MoneyDecimal = Field(
        ..., description="Average size of transactions in this account"
    )
    common_merchants: List[str] = Field(
        ..., max_length=100, description="Most common merchants for this account"
    )
    peak_usage_days: List[int] = Field(
        ...,
        max_length=31,
        description="Days of the month with highest transaction volume (1-31)",
    )
    category_preferences: PercentageDict = Field(
        ..., description="Categories and their usage proportions"
    )
    utilization_rate: Optional[PercentageDecimal] = Field(
        default=None, description="Credit utilization rate (for credit accounts)"
    )


class BalanceDistribution(BaseSchemaValidator):
    """
    Schema for balance distribution data.

    Describes the distribution of funds across accounts.
    Implements ADR-013 with 2 decimal precision for monetary values
    and 4 decimal precision for percentage values.
    """

    account_id: int = Field(..., description="ID of the account")
    average_balance: MoneyDecimal = Field(..., description="Average account balance")
    balance_volatility: MoneyDecimal = Field(
        ..., description="Standard deviation of balance over time"
    )
    min_balance_30d: MoneyDecimal = Field(
        ..., description="Minimum balance in last 30 days"
    )
    max_balance_30d: MoneyDecimal = Field(
        ..., description="Maximum balance in last 30 days"
    )
    typical_balance_range: Tuple[MoneyDecimal, MoneyDecimal] = Field(
        ..., description="Typical range of account balance (min, max)"
    )
    percentage_of_total: PercentageDecimal = Field(
        ..., description="Percentage of total funds across all accounts"
    )


class AccountRiskAssessment(BaseSchemaValidator):
    """
    Schema for account risk assessment data.

    Provides risk metrics for an account based on transaction history.
    Implements ADR-013 with standardized validation for percentage fields.
    """

    account_id: int = Field(..., description="ID of the account")
    overdraft_risk: PercentageDecimal = Field(
        ..., description="Risk of overdraft (0-1 scale)"
    )
    credit_utilization_risk: Optional[PercentageDecimal] = Field(
        default=None, description="Risk from high credit utilization (0-1 scale)"
    )
    payment_failure_risk: PercentageDecimal = Field(
        ..., description="Risk of payment failure (0-1 scale)"
    )
    volatility_score: PercentageDecimal = Field(
        ..., description="Score representing balance volatility (0-1 scale)"
    )
    overall_risk_score: PercentageDecimal = Field(
        ..., description="Overall risk score (0-1 scale)"
    )


class CrossAccountAnalysis(BaseSchemaValidator):
    """
    Schema for comprehensive cross-account analysis.

    Provides a holistic view of relationships between accounts.
    All datetime fields are stored in UTC timezone.
    """

    correlations: Dict[str, Dict[str, AccountCorrelation]] = Field(
        ..., description="Correlation data between account pairs"
    )
    transfer_patterns: List[TransferPattern] = Field(
        ..., description="Patterns of transfers between accounts"
    )
    usage_patterns: Dict[int, AccountUsagePattern] = Field(
        ..., description="Usage patterns for each account"
    )
    balance_distribution: Dict[int, BalanceDistribution] = Field(
        ..., description="Balance distribution across accounts"
    )
    risk_assessment: Dict[int, AccountRiskAssessment] = Field(
        ..., description="Risk assessment for each account"
    )
    timestamp: datetime = Field(
        ..., description="When this analysis was generated in UTC timezone"
    )
