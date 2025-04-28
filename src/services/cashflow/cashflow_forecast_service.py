from datetime import date, datetime, timedelta
from decimal import Decimal
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.cashflow_types import DateType
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.schemas.cashflow import (
    AccountForecastMetrics,
    AccountForecastRequest,
    AccountForecastResponse,
    AccountForecastResult,
    CustomForecastParameters,
    CustomForecastResponse,
    CustomForecastResult,
)
from src.services.cashflow.cashflow_base import CashflowBaseService
from src.services.cashflow.cashflow_transaction_service import TransactionService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import ensure_utc, naive_utc_from_date, utc_now, naive_start_of_day, naive_end_of_day
from src.utils.decimal_precision import DecimalPrecision


class ForecastService(CashflowBaseService):
    """Service for generating cashflow forecasts."""

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """Initialize the forecast service.

        Args:
            session: SQLAlchemy async session for database operations
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)
        self._transaction_service = TransactionService(
            session, feature_flag_service, config_provider
        )
        
    async def get_required_funds(
        self,
        account_id: int,
        start_date: Union[date, datetime],
        end_date: Union[date, datetime]
    ) -> Decimal:
        """Calculate the total funds required to cover liabilities in the specified date range.
        
        Args:
            account_id: ID of the account
            start_date: Start date for the calculation
            end_date: End date for the calculation
            
        Returns:
            Decimal: Total amount required to cover all liabilities in the date range
        """
        # Ensure dates are naive UTC datetime objects for database query
        if isinstance(start_date, date):
            start_naive = naive_start_of_day(start_date)
        else:
            start_naive = start_date
            
        if isinstance(end_date, date):
            end_naive = naive_end_of_day(end_date)
        else:
            end_naive = end_date
        
        # Query liabilities for the account within the date range
        stmt = select(Liability).where(
            Liability.primary_account_id == account_id,
            Liability.due_date >= start_naive,
            Liability.due_date <= end_naive,
            Liability.paid == False  # Only include unpaid liabilities
        )
        
        result = await self._session.execute(stmt)
        liabilities = result.scalars().all()
        
        # Sum up all liability amounts
        total_required = sum(liability.amount for liability in liabilities)
        
        return total_required

    async def get_account_forecast(
        self, params: AccountForecastRequest
    ) -> AccountForecastResponse:
        """Generate account-specific forecast with detailed metrics.

        Args:
            params: Parameters for the forecast

        Returns:
            AccountForecastResponse with forecast details
        """
        # Verify account exists and get its details using repository
        transaction_repo = await self.transaction_repository
        account = await transaction_repo.get_account_by_id(params.account_id)
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

        # Calculate overall confidence with proper precision per ADR-013
        overall_confidence = await self._calculate_forecast_confidence(
            account, daily_forecasts, metrics
        )
        
        # Ensure proper rounding for overall_confidence
        rounded_confidence = DecimalPrecision.round_for_calculation(overall_confidence)

        return AccountForecastResponse(
            account_id=account.id,
            forecast_period=(params.start_date, params.end_date),
            metrics=metrics,
            daily_forecasts=daily_forecasts,
            overall_confidence=rounded_confidence,
            timestamp=utc_now()
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

        # Get accounts to analyze using repository
        metrics_repo = await self.metrics_repository
        accounts = await metrics_repo.get_accounts_for_forecast(params.account_ids)

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
                summary_stats["total_projected_expenses"] += daily_result.projected_expenses
                summary_stats["min_balance"] = min(
                    summary_stats["min_balance"], daily_result.projected_balance
                )
                summary_stats["max_balance"] = max(
                    summary_stats["max_balance"], daily_result.projected_balance
                )
                total_confidence += daily_result.confidence_score
                days_processed += 1

            current_date += timedelta(days=1)

        # Calculate average confidence with proper rounding per ADR-013
        if days_processed > 0:
            avg_confidence = total_confidence / days_processed
            # We use DecimalPrecision.round_for_display because summary_stats is a dictionary
            # that may contain MoneyDecimal values which require 2 decimal places
            summary_stats["average_confidence"] = DecimalPrecision.round_for_display(avg_confidence)
        else:
            summary_stats["average_confidence"] = Decimal("0.0")

        # Apply proper rounding to overall confidence per ADR-013
        # This is a PercentageDecimal which can have 4 decimal places
        overall_confidence = DecimalPrecision.round_for_calculation(avg_confidence if days_processed > 0 else Decimal("0.0"))

        # Round all monetary values in summary_stats to 2 decimal places
        for key in summary_stats.keys():
            if key != "average_confidence":  # We already handled this one
                summary_stats[key] = DecimalPrecision.round_for_display(summary_stats[key])
        
        # Create and return response with proper formatting
        return CustomForecastResponse(
            parameters=params,
            results=results,
            overall_confidence=overall_confidence,
            summary_statistics=summary_stats,
            timestamp=utc_now()
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
        historical_transactions = (
            await self._transaction_service.get_historical_transactions(
                [account.id], historical_start, start_date
            )
        )

        # Calculate projected transactions
        projected_transactions = (
            await self._transaction_service.get_projected_transactions(
                account, start_date, end_date, include_pending, include_recurring
            )
        )

        # Calculate historical metrics
        historical_daily_changes = []
        if historical_transactions:
            # Group transactions by date
            historical_daily_totals = {}
            for trans in historical_transactions:
                trans_date = (
                    trans["date"].date()
                    if hasattr(trans["date"], "date")
                    else trans["date"]
                )
                if trans_date not in historical_daily_totals:
                    historical_daily_totals[trans_date] = Decimal("0")
                historical_daily_totals[trans_date] += trans["amount"]

            # Calculate daily changes
            historical_daily_changes = list(historical_daily_totals.values())

        # Calculate historical volatility
        historical_volatility = (
            Decimal(str(stdev(historical_daily_changes)))
            if len(historical_daily_changes) > 1
            else Decimal("0")
        )

        # Calculate projected metrics
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

        # Calculate balance volatility - use historical data when available
        balance_volatility = historical_volatility
        if balance_volatility == Decimal("0") and len(daily_balances) > 1:
            # Fall back to projected volatility if no historical data
            balance_volatility = Decimal(str(stdev(daily_balances)))

        # Calculate forecast confidence based on historical data consistency
        forecast_confidence = Decimal("0.9")  # Base confidence

        # Adjust confidence based on historical data availability
        if not historical_transactions:
            forecast_confidence -= Decimal("0.2")  # Less confidence without history

        # Adjust confidence based on volatility
        if historical_volatility > Decimal("0") and len(daily_balances) > 0:
            avg_balance = (
                Decimal(str(mean(daily_balances)))
                if daily_balances
                else account.available_balance
            )
            volatility_ratio = balance_volatility / (abs(avg_balance) + Decimal("0.01"))
            if volatility_ratio > Decimal("0.2"):
                forecast_confidence -= Decimal(
                    "0.1"
                )  # Higher volatility = lower confidence

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
            average_inflow=Decimal(str(mean(inflows))).quantize(Decimal("0.01")) if inflows else Decimal("0"),
            average_outflow=Decimal(str(mean(outflows))).quantize(Decimal("0.01")) if outflows else Decimal("0"),
            projected_low_balance_dates=low_balance_dates,
            credit_utilization=credit_utilization,
            balance_volatility=balance_volatility.quantize(Decimal("0.01")) if balance_volatility else Decimal("0"),
            forecast_confidence=forecast_confidence,
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

        # Apply proper rounding according to ADR-013 for percentage values (4 decimal places)
        result = max(min(Decimal(str(avg_confidence)), Decimal("1.0")), Decimal("0.1"))
        return DecimalPrecision.round_for_calculation(result)

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

        # Account-specific confidence adjustments
        if account.account_type == "credit":
            # Credit accounts have different risk profiles
            if account.total_limit:
                # Calculate current utilization
                utilization = abs(balance) / account.total_limit

                # Higher utilization = lower confidence
                if utilization > Decimal("0.8"):
                    base_confidence -= Decimal("0.15")
                elif utilization > Decimal("0.5"):
                    base_confidence -= Decimal("0.05")

                # Approaching limit is a major confidence reducer
                if utilization > Decimal("0.95"):
                    base_confidence -= Decimal("0.25")

        elif account.account_type == "checking":
            # Checking accounts: low balance is a bigger risk
            if balance < Decimal("200"):
                base_confidence -= Decimal("0.2")
            elif balance < Decimal("500"):
                base_confidence -= Decimal("0.1")

            # Large transactions relative to balance reduce confidence
            if transactions:
                largest_transaction = max(abs(t["amount"]) for t in transactions)
                if largest_transaction > balance * Decimal("0.5"):
                    base_confidence -= Decimal("0.15")

        # Transaction volume adjustments
        if len(transactions) > 5:  # High transaction volume increases uncertainty
            base_confidence -= Decimal("0.1")
        elif len(transactions) > 10:  # Very high volume is even more uncertain
            base_confidence -= Decimal("0.2")

        # Balance-based adjustments
        if balance < Decimal("0"):
            # Negative balance is a significant confidence reducer
            base_confidence -= Decimal("0.2")

        # Ensure confidence stays within valid range and has proper precision
        bounded_confidence = max(min(base_confidence, Decimal("1.0")), Decimal("0.1"))
        # Apply proper rounding per ADR-013 for percentage values
        return DecimalPrecision.round_for_calculation(bounded_confidence)

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
            params: Forecast parameters for customization

        Returns:
            CustomForecastResult for the day or None if no data
        """
        daily_expenses = Decimal("0.0")
        daily_income = Decimal("0.0")
        contributing_factors: Dict[str, Decimal] = {}
        risk_factors: Dict[str, Decimal] = {}

        # Apply parameter-specific adjustment factors
        income_adjustment = Decimal("1.0")
        expense_adjustment = Decimal("1.0")

        # Adjust based on scenario parameter
        if params.scenario == "optimistic":
            income_adjustment = Decimal("1.1")  # 10% higher income
            expense_adjustment = Decimal("0.9")  # 10% lower expenses
        elif params.scenario == "pessimistic":
            income_adjustment = Decimal("0.9")  # 10% lower income
            expense_adjustment = Decimal("1.1")  # 10% higher expenses

        # Apply custom thresholds from parameters if provided
        warning_threshold = (
            params.warning_threshold
            if params.warning_threshold is not None
            else self._warning_thresholds.LOW_BALANCE
        )

        for account in accounts:
            # Apply account filters from parameters
            if (
                params.account_types
                and account.account_type not in params.account_types
            ):
                # Skip accounts not in specified types
                continue

            # Get transactions for the day with parameter settings
            transactions = await self._transaction_service.get_day_transactions(
                account,
                current_date,
                include_pending=params.include_pending,
                include_recurring=params.include_recurring,
                include_transfers=params.include_transfers,
            )

            # Apply category filtering if specified in parameters
            filtered_transactions = []
            for trans in transactions:
                # If categories are specified, only include transactions with matching categories
                if params.categories is not None:
                    # Only include transactions that have a category matching one of the specified categories
                    if "category" in trans and trans["category"] in params.categories:
                        filtered_transactions.append(trans)
                    # For expenses with no category, we'll include them in the "expense_bill" category
                    elif "type" in trans and trans["type"] == "bill" and "Utilities" in trans["description"]:
                        filtered_transactions.append(trans)
                else:
                    # No category filtering, include all transactions
                    filtered_transactions.append(trans)
                    
            # Update totals with parameter-specific adjustments
            for trans in filtered_transactions:
                if trans["amount"] > 0:
                    # Adjust income based on scenario
                    adjusted_amount = trans["amount"] * income_adjustment
                    # Apply proper 2-decimal rounding for MoneyDecimal values
                    rounded_amount = DecimalPrecision.round_for_display(adjusted_amount)
                    daily_income += rounded_amount
                    contributing_factors[f"income_{trans['type']}"] = rounded_amount
                else:
                    # Adjust expenses based on scenario
                    amount = abs(trans["amount"]) * expense_adjustment
                    # Apply proper 2-decimal rounding for MoneyDecimal values
                    rounded_amount = DecimalPrecision.round_for_display(amount)
                    daily_expenses += rounded_amount
                    contributing_factors[f"expense_{trans['type']}"] = rounded_amount

                    # Risk assessment using parameter-specific thresholds
                    if rounded_amount > current_balances[account.id]:
                        risk_factors["insufficient_funds"] = Decimal("0.3")

                    # Apply custom threshold for risk assessment
                    if current_balances[account.id] - rounded_amount < warning_threshold:
                        risk_factors["approaching_warning_threshold"] = Decimal("0.2")

            # Update balances
            net_change = daily_income - daily_expenses
            current_balances[account.id] += net_change

            # Apply seasonal factors if enabled in parameters
            if params.apply_seasonal_factors and hasattr(params, "seasonal_factors"):
                # Get month name from current date
                month_name = current_date.strftime("%B").lower()
                if month_name in params.seasonal_factors:
                    # Apply seasonal adjustment to balance
                    seasonal_factor = params.seasonal_factors[month_name]
                    current_balances[account.id] *= Decimal("1.0") + seasonal_factor

        # Calculate confidence score with parameter-specific adjustments
        base_confidence = Decimal("1.0")
        if risk_factors:
            base_confidence -= sum(risk_factors.values())

        # Adjust confidence based on scenario
        if params.scenario == "pessimistic":
            base_confidence *= Decimal(
                "0.9"
            )  # Lower confidence for pessimistic scenario
        elif params.scenario == "optimistic":
            base_confidence *= Decimal(
                "0.95"
            )  # Slightly lower for optimistic (still uncertain)

        # Apply confidence floor from parameters if provided
        min_confidence = (
            params.min_confidence
            if hasattr(params, "min_confidence")
            else Decimal("0.1")
        )
        # Ensure proper rounding for the percentage value per ADR-013
        bounded_confidence = max(min(base_confidence, Decimal("1.0")), min_confidence)
        confidence_score = DecimalPrecision.round_for_calculation(bounded_confidence)

        # Apply proper rounding to all values before returning
        projected_balance = DecimalPrecision.round_for_display(sum(current_balances.values()))
        
        return CustomForecastResult(
            date=current_date,
            projected_balance=projected_balance,
            projected_income=daily_income,  # Already rounded earlier
            projected_expenses=daily_expenses,  # Already rounded earlier
            confidence_score=confidence_score,
            contributing_factors=contributing_factors,
            risk_factors=risk_factors,
        )
