"""
Impact analysis schema factory functions.

This module provides factory functions for creating valid impact analysis
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.impact_analysis import (
    AccountImpact,
    CashflowImpact,
    RiskFactor,
    SplitImpactAnalysis,
    SplitImpactRequest,
)
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function
from src.utils.datetime_utils import utc_now


@factory_function(AccountImpact)
def create_account_impact_schema(
    account_id: int,
    current_balance: Optional[Decimal] = None,
    projected_balance: Optional[Decimal] = None,
    current_credit_utilization: Optional[Decimal] = None,
    projected_credit_utilization: Optional[Decimal] = None,
    risk_score: int = 35,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountImpact schema instance.

    Args:
        account_id: ID of the account being analyzed
        current_balance: Current balance in the account (defaults to 1000.00)
        projected_balance: Projected balance after the action (defaults to 900.00)
        current_credit_utilization: Current credit utilization percentage
        projected_credit_utilization: Projected credit utilization percentage
        risk_score: Risk score from 0-100 (defaults to 35)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountImpact schema
    """
    if current_balance is None:
        current_balance = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if projected_balance is None:
        projected_balance = MEDIUM_AMOUNT * Decimal("9")  # 900.00

    data = {
        "account_id": account_id,
        "current_balance": current_balance,
        "projected_balance": projected_balance,
        "risk_score": risk_score,
        **kwargs,
    }

    if current_credit_utilization is not None:
        data["current_credit_utilization"] = current_credit_utilization

    if projected_credit_utilization is not None:
        data["projected_credit_utilization"] = projected_credit_utilization

    return data


@factory_function(CashflowImpact)
def create_cashflow_impact_schema(
    date: Optional[datetime] = None,
    total_bills: Optional[Decimal] = None,
    available_funds: Optional[Decimal] = None,
    projected_deficit: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CashflowImpact schema instance.

    Args:
        date: Date for this cashflow snapshot (defaults to current UTC time)
        total_bills: Total bills due on this date (defaults to 500.00)
        available_funds: Available funds on this date (defaults to 1000.00)
        projected_deficit: Projected deficit amount if funds insufficient
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CashflowImpact schema
    """
    if date is None:
        date = utc_now()

    if total_bills is None:
        total_bills = MEDIUM_AMOUNT * Decimal("5")  # 500.00

    if available_funds is None:
        available_funds = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    data = {
        "date": date,
        "total_bills": total_bills,
        "available_funds": available_funds,
        **kwargs,
    }

    if projected_deficit is not None:
        data["projected_deficit"] = projected_deficit

    return data


@factory_function(RiskFactor)
def create_risk_factor_schema(
    name: str = "Insufficient Funds",
    severity: int = 65,
    description: str = "Risk of insufficient funds to cover upcoming bills",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RiskFactor schema instance.

    Args:
        name: Name of the risk factor
        severity: Severity rating from 0-100
        description: Detailed description of the risk factor
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RiskFactor schema
    """
    data = {
        "name": name,
        "severity": severity,
        "description": description,
        **kwargs,
    }

    return data


@factory_function(SplitImpactAnalysis)
def create_split_impact_analysis_schema(
    total_amount: Optional[Decimal] = None,
    account_impacts: Optional[List[Dict[str, Any]]] = None,
    cashflow_impacts: Optional[List[Dict[str, Any]]] = None,
    risk_factors: Optional[List[Dict[str, Any]]] = None,
    overall_risk_score: int = 45,
    recommendations: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SplitImpactAnalysis schema instance.

    Args:
        total_amount: Total amount of the liability (defaults to 1000.00)
        account_impacts: Impacts on individual accounts
        cashflow_impacts: Impacts on cashflow over time
        risk_factors: Identified risk factors
        overall_risk_score: Overall risk score from 0-100 (defaults to 45)
        recommendations: Recommendations based on the analysis
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SplitImpactAnalysis schema
    """
    if total_amount is None:
        total_amount = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if account_impacts is None:
        # Sample account impacts for two accounts
        account_impacts = [
            create_account_impact_schema(account_id=1).model_dump(),
            create_account_impact_schema(
                account_id=2,
                current_balance=MEDIUM_AMOUNT * Decimal("20"),  # 2000.00
                projected_balance=MEDIUM_AMOUNT * Decimal("17"),  # 1700.00
                risk_score=25,
            ).model_dump(),
        ]

    if cashflow_impacts is None:
        # Sample cashflow impacts for different dates
        now = utc_now()
        cashflow_impacts = [
            create_cashflow_impact_schema(date=now).model_dump(),
            create_cashflow_impact_schema(
                date=now + timedelta(days=30),
                total_bills=MEDIUM_AMOUNT * Decimal("7"),  # 700.00
                available_funds=MEDIUM_AMOUNT * Decimal("8"),  # 800.00
                projected_deficit=MEDIUM_AMOUNT,  # 100.00
            ).model_dump(),
        ]

    if risk_factors is None:
        # Sample risk factors
        risk_factors = [
            create_risk_factor_schema().model_dump(),
            create_risk_factor_schema(
                name="Credit Utilization",
                severity=40,
                description="Risk of high credit utilization affecting credit score",
            ).model_dump(),
        ]

    if recommendations is None:
        recommendations = [
            "Split bill payment across multiple pay periods",
            "Consider using savings account for partial payment",
            "Adjust budget for next month to accommodate this expense",
        ]

    data = {
        "total_amount": total_amount,
        "account_impacts": account_impacts,
        "cashflow_impacts": cashflow_impacts,
        "risk_factors": risk_factors,
        "overall_risk_score": overall_risk_score,
        "recommendations": recommendations,
        **kwargs,
    }

    return data


@factory_function(SplitImpactRequest)
def create_split_impact_request_schema(
    liability_id: int,
    splits: Optional[List[Dict[str, Any]]] = None,
    analysis_period_days: int = 90,
    start_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SplitImpactRequest schema instance.

    Args:
        liability_id: ID of the liability to analyze
        splits: Split configuration to analyze
        analysis_period_days: Number of days in analysis period (14-365)
        start_date: Start date for analysis (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SplitImpactRequest schema
    """
    if splits is None:
        # Sample split configuration for two accounts
        splits = [
            {"account_id": 1, "amount": MEDIUM_AMOUNT * Decimal("3")},  # 300.00
            {"account_id": 2, "amount": MEDIUM_AMOUNT * Decimal("7")},  # 700.00
        ]

    if start_date is None:
        start_date = utc_now()

    data = {
        "liability_id": liability_id,
        "splits": splits,
        "analysis_period_days": analysis_period_days,
        "start_date": start_date,
        **kwargs,
    }

    return data
