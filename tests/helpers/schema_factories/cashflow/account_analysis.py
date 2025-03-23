"""
Account analysis schema factory functions.

This module provides factory functions for creating valid account analysis
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from src.schemas.cashflow.account_analysis import (AccountCorrelation,
                                                   AccountRiskAssessment,
                                                   AccountUsagePattern,
                                                   BalanceDistribution,
                                                   CrossAccountAnalysis,
                                                   TransferPattern)
from tests.helpers.schema_factories.base import (MEDIUM_AMOUNT, SMALL_AMOUNT,
                                                 factory_function, utc_now)


@factory_function(AccountCorrelation)
def create_account_correlation_schema(
    correlation_score: Decimal = Decimal("0.75"),
    transfer_frequency: int = 3,
    common_categories: Optional[List[str]] = None,
    relationship_type: str = "complementary",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountCorrelation schema instance.

    Args:
        correlation_score: Correlation coefficient between accounts (-1 to 1)
        transfer_frequency: Number of transfers between accounts per month
        common_categories: Categories commonly used across both accounts
        relationship_type: Type of relationship between accounts
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountCorrelation schema
    """
    if common_categories is None:
        common_categories = ["Bills", "Groceries", "Utilities"]

    data = {
        "correlation_score": correlation_score,
        "transfer_frequency": transfer_frequency,
        "common_categories": common_categories,
        "relationship_type": relationship_type,
        **kwargs,
    }

    return data


@factory_function(TransferPattern)
def create_transfer_pattern_schema(
    source_account_id: int,
    target_account_id: int,
    average_amount: Optional[Decimal] = None,
    frequency: int = 2,
    typical_day_of_month: Optional[int] = None,
    category_distribution: Optional[Dict[str, Decimal]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TransferPattern schema instance.

    Args:
        source_account_id: ID of the source account for transfers
        target_account_id: ID of the target account for transfers
        average_amount: Average amount transferred (defaults to 500.00)
        frequency: Number of transfers per month (defaults to 2)
        typical_day_of_month: Day of month when transfers typically occur
        category_distribution: Distribution of transfer categories and proportions
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TransferPattern schema
    """
    if average_amount is None:
        average_amount = MEDIUM_AMOUNT * Decimal("5")  # 500.00

    if category_distribution is None:
        category_distribution = {
            "Bills": Decimal("0.5"),
            "Savings": Decimal("0.3"),
            "Discretionary": Decimal("0.2"),
        }

    data = {
        "source_account_id": source_account_id,
        "target_account_id": target_account_id,
        "average_amount": average_amount,
        "frequency": frequency,
        "category_distribution": category_distribution,
        **kwargs,
    }

    if typical_day_of_month is not None:
        data["typical_day_of_month"] = typical_day_of_month

    return data


@factory_function(AccountUsagePattern)
def create_account_usage_pattern_schema(
    account_id: int,
    primary_use: str = "Daily Expenses",
    average_transaction_size: Optional[Decimal] = None,
    common_merchants: Optional[List[str]] = None,
    peak_usage_days: Optional[List[int]] = None,
    category_preferences: Optional[Dict[str, Decimal]] = None,
    utilization_rate: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountUsagePattern schema instance.

    Args:
        account_id: ID of the account
        primary_use: Primary purpose of the account
        average_transaction_size: Average size of transactions
        common_merchants: Most common merchants for this account
        peak_usage_days: Days of the month with highest transaction volume
        category_preferences: Categories and their usage proportions
        utilization_rate: Credit utilization rate (for credit accounts)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountUsagePattern schema
    """
    if average_transaction_size is None:
        average_transaction_size = MEDIUM_AMOUNT  # 100.00

    if common_merchants is None:
        common_merchants = ["Grocery Store", "Gas Station", "Retail Store"]

    if peak_usage_days is None:
        peak_usage_days = [1, 15, 28]

    if category_preferences is None:
        category_preferences = {
            "Groceries": Decimal("0.3"),
            "Transportation": Decimal("0.2"),
            "Dining": Decimal("0.15"),
            "Shopping": Decimal("0.25"),
            "Utilities": Decimal("0.1"),
        }

    data = {
        "account_id": account_id,
        "primary_use": primary_use,
        "average_transaction_size": average_transaction_size,
        "common_merchants": common_merchants,
        "peak_usage_days": peak_usage_days,
        "category_preferences": category_preferences,
        **kwargs,
    }

    if utilization_rate is not None:
        data["utilization_rate"] = utilization_rate

    return data


@factory_function(BalanceDistribution)
def create_balance_distribution_schema(
    account_id: int,
    average_balance: Optional[Decimal] = None,
    balance_volatility: Optional[Decimal] = None,
    min_balance_30d: Optional[Decimal] = None,
    max_balance_30d: Optional[Decimal] = None,
    typical_balance_range: Optional[Tuple[Decimal, Decimal]] = None,
    percentage_of_total: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BalanceDistribution schema instance.

    Args:
        account_id: ID of the account
        average_balance: Average account balance (defaults to 1500.00)
        balance_volatility: Standard deviation of balance (defaults to 300.00)
        min_balance_30d: Minimum balance in last 30 days (defaults to 1000.00)
        max_balance_30d: Maximum balance in last 30 days (defaults to 2000.00)
        typical_balance_range: Typical range of account balance (min, max)
        percentage_of_total: Percentage of total funds (defaults to 0.35)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BalanceDistribution schema
    """
    if average_balance is None:
        average_balance = MEDIUM_AMOUNT * Decimal("15")  # 1500.00

    if balance_volatility is None:
        balance_volatility = MEDIUM_AMOUNT * Decimal("3")  # 300.00

    if min_balance_30d is None:
        min_balance_30d = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if max_balance_30d is None:
        max_balance_30d = MEDIUM_AMOUNT * Decimal("20")  # 2000.00

    if typical_balance_range is None:
        typical_balance_range = (
            MEDIUM_AMOUNT * Decimal("8"),
            MEDIUM_AMOUNT * Decimal("22"),
        )  # (800.00, 2200.00)

    if percentage_of_total is None:
        percentage_of_total = Decimal("0.35")

    data = {
        "account_id": account_id,
        "average_balance": average_balance,
        "balance_volatility": balance_volatility,
        "min_balance_30d": min_balance_30d,
        "max_balance_30d": max_balance_30d,
        "typical_balance_range": typical_balance_range,
        "percentage_of_total": percentage_of_total,
        **kwargs,
    }

    return data


@factory_function(AccountRiskAssessment)
def create_account_risk_assessment_schema(
    account_id: int,
    overdraft_risk: Optional[Decimal] = None,
    credit_utilization_risk: Optional[Decimal] = None,
    payment_failure_risk: Optional[Decimal] = None,
    volatility_score: Optional[Decimal] = None,
    overall_risk_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountRiskAssessment schema instance.

    Args:
        account_id: ID of the account
        overdraft_risk: Risk of overdraft (0-1 scale)
        credit_utilization_risk: Risk from high credit utilization (0-1 scale)
        payment_failure_risk: Risk of payment failure (0-1 scale)
        volatility_score: Score representing balance volatility (0-1 scale)
        overall_risk_score: Overall risk score (0-1 scale)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountRiskAssessment schema
    """
    if overdraft_risk is None:
        overdraft_risk = Decimal("0.25")

    if payment_failure_risk is None:
        payment_failure_risk = Decimal("0.15")

    if volatility_score is None:
        volatility_score = Decimal("0.30")

    if overall_risk_score is None:
        overall_risk_score = Decimal("0.23")

    data = {
        "account_id": account_id,
        "overdraft_risk": overdraft_risk,
        "payment_failure_risk": payment_failure_risk,
        "volatility_score": volatility_score,
        "overall_risk_score": overall_risk_score,
        **kwargs,
    }

    if credit_utilization_risk is not None:
        data["credit_utilization_risk"] = credit_utilization_risk

    return data


@factory_function(CrossAccountAnalysis)
def create_cross_account_analysis_schema(
    correlations: Optional[Dict[str, Dict[str, Any]]] = None,
    transfer_patterns: Optional[List[Dict[str, Any]]] = None,
    usage_patterns: Optional[Dict[int, Dict[str, Any]]] = None,
    balance_distribution: Optional[Dict[int, Dict[str, Any]]] = None,
    risk_assessment: Optional[Dict[int, Dict[str, Any]]] = None,
    timestamp: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CrossAccountAnalysis schema instance.

    Args:
        correlations: Correlation data between account pairs
        transfer_patterns: Patterns of transfers between accounts
        usage_patterns: Usage patterns for each account
        balance_distribution: Balance distribution across accounts
        risk_assessment: Risk assessment for each account
        timestamp: When analysis was generated (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CrossAccountAnalysis schema
    """
    # These would typically be populated with actual account IDs
    # For testing, we'll use placeholder values
    account1_id = 1
    account2_id = 2

    if correlations is None:
        # Create a dictionary with account pairs as keys
        correlations = {
            f"{account1_id}-{account2_id}": {
                # Use the factory function for AccountCorrelation
                create_account_correlation_schema().model_dump()
            }
        }

    if transfer_patterns is None:
        # Create a list of transfer patterns
        transfer_patterns = [
            create_transfer_pattern_schema(
                source_account_id=account1_id, target_account_id=account2_id
            ).model_dump(),
            create_transfer_pattern_schema(
                source_account_id=account2_id, target_account_id=account1_id
            ).model_dump(),
        ]

    if usage_patterns is None:
        # Create a dictionary with account IDs as keys
        usage_patterns = {
            account1_id: create_account_usage_pattern_schema(
                account_id=account1_id
            ).model_dump(),
            account2_id: create_account_usage_pattern_schema(
                account_id=account2_id
            ).model_dump(),
        }

    if balance_distribution is None:
        # Create a dictionary with account IDs as keys
        balance_distribution = {
            account1_id: create_balance_distribution_schema(
                account_id=account1_id
            ).model_dump(),
            account2_id: create_balance_distribution_schema(
                account_id=account2_id
            ).model_dump(),
        }

    if risk_assessment is None:
        # Create a dictionary with account IDs as keys
        risk_assessment = {
            account1_id: create_account_risk_assessment_schema(
                account_id=account1_id
            ).model_dump(),
            account2_id: create_account_risk_assessment_schema(
                account_id=account2_id
            ).model_dump(),
        }

    if timestamp is None:
        timestamp = utc_now()

    data = {
        "correlations": correlations,
        "transfer_patterns": transfer_patterns,
        "usage_patterns": usage_patterns,
        "balance_distribution": balance_distribution,
        "risk_assessment": risk_assessment,
        "timestamp": timestamp,
        **kwargs,
    }

    return data
