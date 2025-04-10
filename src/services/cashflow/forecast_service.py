from datetime import date, timedelta
from decimal import Decimal
from statistics import mean, stdev
from typing import Dict, List, Optional

from sqlalchemy import select

from src.models.accounts import Account
from src.schemas.cashflow import (
    AccountForecastMetrics,
    AccountForecastRequest,
    AccountForecastResponse,
    AccountForecastResult,
    CustomForecastParameters,
    CustomForecastResponse,
    CustomForecastResult,
)

from .base import BaseService
from .transaction_service import TransactionService
from .types import DateType


class ForecastService(BaseService):
    """Service for generating cashflow forecasts."""

    def __init__(self, db):
        super().__init__(db)
        self._transaction_service = TransactionService(db)

    async def get_account_forecast(
        self, params: AccountForecastRequest
    ) -> AccountForecastResponse:
        """Generate account-specific forecast with detailed metrics.

        Args:
            params: Parameters for the forecast

        Returns:
            AccountForecastResponse with forecast details
        """
        # Verify account exists and get its details
        account = await self.db.get(Account, params.account_id)
        if not account:
            raise ValueError(f"Account with id {params.account_id} not found")

        # Initialize metrics
        metrics = await self._calculate_account_metrics(
            account,
            params.start_date,
            params.end_date,
            params.include_pending,
            params.include_recurring,
        )

        # Generate daily forecasts
        daily_forecasts = await self._generate_account_daily_forecasts(
            account,
            params.start_date,
            params.end_date,
            params.include_pending,
            params.include_recurring,
            params.include_transfers,
        )

        # Calculate overall confidence
        overall_confidence = await self._calculate_forecast_confidence(
            account, daily_forecasts, metrics
        )

        return AccountForecastResponse(
            account_id=account.id,
            forecast_period=(params.start_date, params.end_date),
            metrics=metrics,
            daily_forecasts=daily_forecasts,
            overall_confidence=overall_confidence,
            timestamp=date.today(),
        )

    async def get_custom_forecast(
        self, params: CustomForecastParameters
    ) -> CustomForecastResponse:
        """Calculate a custom forecast based on provided parameters.

        Args:
            params: Parameters for the custom forecast

        Returns:
            CustomForecastResponse with forecast details
        """
        results = []
        total_confidence = Decimal("0.0")
        summary_stats: Dict[str, Decimal] = {
            "total_projected_income": Decimal("0.0"),
            "total_projected_expenses": Decimal("0.0"),
            "average_confidence": Decimal("0.0"),
            "min_balance": Decimal("999999999.99"),
            "max_balance": Decimal("-999999999.99"),
        }

        # Get accounts to analyze
        accounts_query = select(Account)
        if params.account_ids:
            accounts_query = accounts_query.where(Account.id.in_(params.account_ids))
        accounts = (await self.db.execute(accounts_query)).scalars().all()

        if not accounts:
            raise ValueError("No valid accounts found for analysis")

        # Initialize starting balances
        current_balances = {acc.id: acc.available_balance for acc in accounts}

        # Process each day in the forecast period
        current_date = params.start_date
        days_processed = 0

        while current_date <= params.end_date:
            daily_result = await self._calculate_daily_forecast(
                current_date, accounts, current_balances, params
            )

            if daily_result:
                results.append(daily_result)
                summary_stats["total_projected_income"] += daily_result.projected_income
                summary_stats[
                    "total_projected_expenses"
                ] += daily_result.projected_expenses
                summary_stats["min_balance"] = min(
                    summary_stats["min_balance"], daily_result.projected_balance
                )
                summary_stats["max_balance"] = max(
                    summary_stats["max_balance"], daily_result.projected_balance
                )
                total_confidence += daily_result.confidence_score
                days_processed += 1

            current_date += timedelta(days=1)

        # Calculate average confidence
        summary_stats["average_confidence"] = (
            total_confidence / days_processed if days_processed > 0 else Decimal("0.0")
        )

        return CustomForecastResponse(
            parameters=params,
            results=results,
            overall_confidence=summary_stats["average_confidence"],
            summary_statistics=summary_stats,
            timestamp=date.today(),
        )

    async def _calculate_account_metrics(
        self,
        account: Account,
        start_date: DateType,
        end_date: DateType,
        include_pending: bool,
        include_recurring: bool,
    ) -> AccountForecastMetrics:
        """Calculate account-specific forecast metrics.

        Args:
            account: Account to calculate metrics for
            start_date: Start date for metrics
            end_date: End date for metrics
            include_pending: Whether to include pending transactions
            include_recurring: Whether to include recurring transactions

        Returns:
            AccountForecastMetrics with calculated metrics
        """
        # Get historical transactions for volatility calculation
        historical_start = (
            start_date - timedelta(days=90)
            if isinstance(start_date, date)
            else start_date.date() - timedelta(days=90)
        )
        transactions = await self._transaction_service.get_historical_transactions(
            [account.id], historical_start, start_date
        )

        # Calculate projected transactions
        projected_transactions = (
            await self._transaction_service.get_projected_transactions(
                account, start_date, end_date, include_pending, include_recurring
            )
        )

        # Calculate metrics
        daily_balances = []
        inflows = []
        outflows = []
        current_balance = account.available_balance

        for trans in projected_transactions:
            current_balance += trans["amount"]
            daily_balances.append(current_balance)
            if trans["amount"] > 0:
                inflows.append(trans["amount"])
            else:
                outflows.append(abs(trans["amount"]))

        # Identify low balance dates
        low_balance_dates = [
            trans["date"]
            for trans in projected_transactions
            if (current_balance + trans["amount"])
            < self._warning_thresholds.LOW_BALANCE
        ]

        # Calculate credit utilization for credit accounts
        credit_utilization = None
        if account.account_type == "credit" and account.total_limit:
            if daily_balances:
                credit_utilization = abs(min(daily_balances)) / account.total_limit
            else:
                credit_utilization = (
                    abs(account.available_balance) / account.total_limit
                )

        # Calculate balance volatility
        balance_volatility = (
            Decimal(str(stdev(daily_balances)))
            if len(daily_balances) > 1
            else Decimal("0")
        )

        return AccountForecastMetrics(
            average_daily_balance=(
                Decimal(str(mean(daily_balances))) if daily_balances else Decimal("0")
            ),
            minimum_projected_balance=(
                min(daily_balances) if daily_balances else account.available_balance
            ),
            maximum_projected_balance=(
                max(daily_balances) if daily_balances else account.available_balance
            ),
            average_inflow=Decimal(str(mean(inflows))) if inflows else Decimal("0"),
            average_outflow=Decimal(str(mean(outflows))) if outflows else Decimal("0"),
            projected_low_balance_dates=low_balance_dates,
            credit_utilization=credit_utilization,
            balance_volatility=balance_volatility,
            forecast_confidence=Decimal(
                "0.9"
            ),  # Will be adjusted in _calculate_forecast_confidence
        )

    async def _generate_account_daily_forecasts(
        self,
        account: Account,
        start_date: DateType,
        end_date: DateType,
        include_pending: bool,
        include_recurring: bool,
        include_transfers: bool,
    ) -> List[AccountForecastResult]:
        """Generate daily forecast results for an account.

        Args:
            account: Account to generate forecasts for
            start_date: Start date for forecasts
            end_date: End date for forecasts
            include_pending: Whether to include pending transactions
            include_recurring: Whether to include recurring transactions
            include_transfers: Whether to include transfers

        Returns:
            List of AccountForecastResult for each day
        """
        daily_forecasts = []
        current_balance = account.available_balance
        current_date = start_date

        while current_date <= end_date:
            # Get day's transactions
            day_transactions = await self._transaction_service.get_day_transactions(
                account,
                current_date,
                include_pending,
                include_recurring,
                include_transfers,
            )

            # Calculate day's inflow/outflow
            day_inflow = sum(t["amount"] for t in day_transactions if t["amount"] > 0)
            day_outflow = sum(
                abs(t["amount"]) for t in day_transactions if t["amount"] < 0
            )

            # Update balance
            current_balance += day_inflow - day_outflow

            # Generate warning flags
            warning_flags = []
            if current_balance < self._warning_thresholds.LOW_BALANCE:
                warning_flags.append("low_balance")
            if account.account_type == "credit" and account.total_limit:
                utilization = abs(current_balance) / account.total_limit
                if utilization > self._warning_thresholds.HIGH_CREDIT_UTILIZATION:
                    warning_flags.append("high_credit_utilization")
            if day_outflow > self._warning_thresholds.LARGE_OUTFLOW:
                warning_flags.append("large_outflow")

            # Calculate confidence score for the day
            confidence_score = self._calculate_day_confidence(
                account, current_balance, day_transactions, warning_flags
            )

            daily_forecasts.append(
                AccountForecastResult(
                    date=current_date,
                    projected_balance=current_balance,
                    projected_inflow=day_inflow,
                    projected_outflow=day_outflow,
                    confidence_score=confidence_score,
                    contributing_transactions=[
                        {"amount": t["amount"], "description": t["description"]}
                        for t in day_transactions
                    ],
                    warning_flags=warning_flags,
                )
            )

            current_date += timedelta(days=1)

        return daily_forecasts

    async def _calculate_forecast_confidence(
        self,
        account: Account,
        daily_forecasts: List[AccountForecastResult],
        metrics: AccountForecastMetrics,
    ) -> Decimal:
        """Calculate overall confidence score for the forecast.

        Args:
            account: Account being forecasted
            daily_forecasts: List of daily forecast results
            metrics: Account forecast metrics

        Returns:
            Overall confidence score as Decimal
        """
        if not daily_forecasts:
            return Decimal("0.0")

        # Average of daily confidence scores
        avg_confidence = mean(f.confidence_score for f in daily_forecasts)

        # Adjust for account type specific factors
        if account.account_type == "credit":
            # Lower confidence if projected to exceed credit limit
            if metrics.credit_utilization and metrics.credit_utilization > Decimal(
                "0.9"
            ):
                avg_confidence *= Decimal("0.8")
        else:  # checking/savings
            # Lower confidence if multiple low balance warnings
            low_balance_days = len(
                [f for f in daily_forecasts if "low_balance" in f.warning_flags]
            )
            if low_balance_days > len(daily_forecasts) // 4:  # More than 25% of days
                avg_confidence *= Decimal("0.85")

        # Adjust for volatility
        if metrics.balance_volatility > metrics.average_daily_balance * Decimal("0.2"):
            avg_confidence *= Decimal("0.9")

        return max(min(Decimal(str(avg_confidence)), Decimal("1.0")), Decimal("0.1"))

    def _calculate_day_confidence(
        self,
        account: Account,
        balance: Decimal,
        transactions: List[Dict],
        warning_flags: List[str],
    ) -> Decimal:
        """Calculate confidence score for a day's forecast.

        Args:
            account: Account being analyzed
            balance: Current balance
            transactions: List of transactions
            warning_flags: List of warning flags

        Returns:
            Confidence score as Decimal
        """
        base_confidence = Decimal("0.9")  # Start with 90% confidence

        # Reduce confidence based on warning flags
        confidence_deductions = {
            "low_balance": Decimal("0.2"),
            "high_credit_utilization": Decimal("0.15"),
            "large_outflow": Decimal("0.1"),
        }

        for flag in warning_flags:
            if flag in confidence_deductions:
                base_confidence -= confidence_deductions[flag]

        # Adjust for transaction volume
        if len(transactions) > 5:  # High transaction volume increases uncertainty
            base_confidence -= Decimal("0.1")

        # Ensure confidence stays within valid range
        return max(min(base_confidence, Decimal("1.0")), Decimal("0.1"))

    async def _calculate_daily_forecast(
        self,
        current_date: DateType,
        accounts: List[Account],
        current_balances: Dict[int, Decimal],
        params: CustomForecastParameters,
    ) -> Optional[CustomForecastResult]:
        """Calculate forecast for a specific day.

        Args:
            current_date: Date to calculate forecast for
            accounts: List of accounts to include
            current_balances: Current balance for each account
            params: Forecast parameters

        Returns:
            CustomForecastResult for the day or None if no data
        """
        daily_expenses = Decimal("0.0")
        daily_income = Decimal("0.0")
        contributing_factors: Dict[str, Decimal] = {}
        risk_factors: Dict[str, Decimal] = {}

        for account in accounts:
            transactions = await self._transaction_service.get_day_transactions(
                account,
                current_date,
                include_pending=True,
                include_recurring=True,
                include_transfers=True,
            )

            # Update totals
            for trans in transactions:
                if trans["amount"] > 0:
                    daily_income += trans["amount"]
                    contributing_factors[f"income_{trans['type']}"] = trans["amount"]
                else:
                    amount = abs(trans["amount"])
                    daily_expenses += amount
                    contributing_factors[f"expense_{trans['type']}"] = amount

                    # Risk assessment
                    if amount > current_balances[account.id]:
                        risk_factors["insufficient_funds"] = Decimal("0.3")

            # Update balances
            current_balances[account.id] += daily_income - daily_expenses

        # Calculate confidence score
        base_confidence = Decimal("1.0")
        if risk_factors:
            base_confidence -= sum(risk_factors.values())
        confidence_score = max(min(base_confidence, Decimal("1.0")), Decimal("0.0"))

        return CustomForecastResult(
            date=current_date,
            projected_balance=sum(current_balances.values()),
            projected_income=daily_income,
            projected_expenses=daily_expenses,
            confidence_score=confidence_score,
            contributing_factors=contributing_factors,
            risk_factors=risk_factors,
        )
