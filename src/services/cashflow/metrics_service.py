from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import select

from src.models.accounts import Account
from src.models.cashflow import CashflowForecast
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.schemas.cashflow import CustomForecastResult
from src.utils.decimal_precision import DecimalPrecision

from .base import BaseService
from .transaction_service import TransactionService
from .types import DateType


class MetricsService(BaseService):
    """Service for calculating cashflow metrics and analysis."""

    def __init__(self, db):
        super().__init__(db)
        self._transaction_service = TransactionService(db)

    async def get_metrics_for_date(
        self, target_date: DateType
    ) -> Optional[CustomForecastResult]:
        """Get cashflow metrics for a specific date.

        Args:
            target_date: Date to get metrics for

        Returns:
            CustomForecastResult with metrics or None if no data available
        """
        # Get all accounts
        accounts_query = select(Account)
        accounts = (await self.db.execute(accounts_query)).scalars().all()

        if not accounts:
            return None

        # Get day's transactions
        day_transactions = []
        total_balance = Decimal("0")
        total_inflow = Decimal("0")
        total_outflow = Decimal("0")

        for account in accounts:
            transactions = await self._transaction_service.get_day_transactions(
                account,
                target_date,
                include_pending=True,
                include_recurring=True,
                include_transfers=True,
            )
            day_transactions.extend(transactions)

            # Update totals
            total_balance += account.available_balance
            for trans in transactions:
                if trans["amount"] > 0:
                    total_inflow += trans["amount"]
                else:
                    total_outflow += abs(trans["amount"])

        # Calculate confidence score
        confidence_score = self._calculate_day_confidence(
            accounts[0],  # Use first account for base calculation
            total_balance,
            day_transactions,
            [],  # No warning flags for this calculation
        )

        return CustomForecastResult(
            date=target_date,
            projected_balance=total_balance,
            projected_income=total_inflow,
            projected_expenses=total_outflow,
            confidence_score=confidence_score,
            contributing_factors={
                "total_accounts": len(accounts),
                "total_transactions": len(day_transactions),
            },
            risk_factors={},
        )

    async def calculate_required_funds(
        self, account_id: int, start_date: DateType, end_date: DateType
    ) -> Decimal:
        """Calculate total required funds for bills in the specified date range.

        Args:
            account_id: Account ID to calculate for
            start_date: Start date of range
            end_date: End date of range

        Returns:
            Total required funds as Decimal
        """
        result = await self.db.execute(
            select(Liability)
            .outerjoin(Payment)
            .where(
                Liability.primary_account_id == account_id,
                Liability.due_date >= start_date,
                Liability.due_date <= end_date,
                Payment.id == None,  # No associated payments
            )
        )
        liabilities = result.scalars().all()
        # Use 4 decimal precision for internal calculations
        total = sum(liability.amount for liability in liabilities)
        return DecimalPrecision.round_for_calculation(total)

    def calculate_daily_deficit(self, min_amount: Decimal, days: int) -> Decimal:
        """Calculate daily deficit needed to cover minimum required amount.

        Args:
            min_amount: Minimum amount needed
            days: Number of days to spread deficit over

        Returns:
            Daily deficit amount (stored with 4 decimal places internally)
        """
        if min_amount >= 0:
            return Decimal("0.0000")

        # Use 4 decimal precision for internal calculations, will be rounded to 2 at API boundaries
        min_amount = DecimalPrecision.round_for_calculation(min_amount)
        result = abs(min_amount) / Decimal(days)
        return DecimalPrecision.round_for_calculation(result)

    def calculate_yearly_deficit(self, daily_deficit: Decimal) -> Decimal:
        """Calculate yearly deficit based on daily deficit.

        Args:
            daily_deficit: Daily deficit amount

        Returns:
            Yearly deficit amount (stored with 4 decimal places internally)
        """
        daily_deficit = DecimalPrecision.round_for_calculation(daily_deficit)
        result = daily_deficit * Decimal(365)
        return DecimalPrecision.round_for_calculation(result)

    def calculate_required_income(
        self, yearly_deficit: Decimal, tax_rate: Decimal = Decimal("0.80")
    ) -> Decimal:
        """Calculate required gross income to cover yearly deficit.

        Args:
            yearly_deficit: Yearly deficit amount
            tax_rate: Tax rate as decimal (default 0.80 assumes 20% tax rate)

        Returns:
            Required gross income (stored with 4 decimal places internally)
        """
        yearly_deficit = DecimalPrecision.round_for_calculation(yearly_deficit)
        tax_rate = DecimalPrecision.round_for_calculation(tax_rate)
        result = yearly_deficit / tax_rate
        return DecimalPrecision.round_for_calculation(result)

    def update_cashflow_deficits(self, forecast: CashflowForecast) -> None:
        """Calculate daily and yearly deficits for a cashflow forecast model.

        This method replaces the model's calculate_deficits method to move
        business logic to the service layer in compliance with ADR-012.

        Args:
            forecast: The CashflowForecast model to update
        """
        min_amount = min(
            forecast.min_14_day,
            forecast.min_30_day,
            forecast.min_60_day,
            forecast.min_90_day,
        )
        forecast.daily_deficit = self.calculate_daily_deficit(min_amount, 14)
        forecast.yearly_deficit = self.calculate_yearly_deficit(forecast.daily_deficit)

    def update_cashflow_required_income(
        self, forecast: CashflowForecast, tax_rate: Decimal = Decimal("0.8")
    ) -> None:
        """Calculate required income for a cashflow forecast model.

        This method replaces the model's calculate_required_income method to move
        business logic to the service layer in compliance with ADR-012.

        Args:
            forecast: The CashflowForecast model to update
            tax_rate: Tax rate as decimal (default 0.80 assumes 20% tax rate)
        """
        forecast.required_income = self.calculate_required_income(
            forecast.yearly_deficit, tax_rate
        )

    def update_cashflow_hourly_rates(self, forecast: CashflowForecast) -> None:
        """Calculate hourly rates for a cashflow forecast model.

        This method replaces the model's calculate_hourly_rates method to move
        business logic to the service layer in compliance with ADR-012.

        Args:
            forecast: The CashflowForecast model to update
        """
        # Use 4 decimal precision for all internal calculations
        required_income = DecimalPrecision.round_for_calculation(
            forecast.required_income
        )
        weekly_required = DecimalPrecision.round_for_calculation(
            required_income / Decimal(52)
        )

        forecast.hourly_rate_40 = DecimalPrecision.round_for_calculation(
            weekly_required / Decimal(40)
        )
        forecast.hourly_rate_30 = DecimalPrecision.round_for_calculation(
            weekly_required / Decimal(30)
        )
        forecast.hourly_rate_20 = DecimalPrecision.round_for_calculation(
            weekly_required / Decimal(20)
        )

    def update_cashflow_all_calculations(
        self, forecast: CashflowForecast, tax_rate: Decimal = Decimal("0.8")
    ) -> None:
        """Perform all calculations on a cashflow forecast model.

        This is a convenience method that performs all calculations in the correct order.

        Args:
            forecast: The CashflowForecast model to update
            tax_rate: Tax rate as decimal (default 0.80 assumes 20% tax rate)
        """
        self.update_cashflow_deficits(forecast)
        self.update_cashflow_required_income(forecast, tax_rate)
        self.update_cashflow_hourly_rates(forecast)

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
            Confidence score as Decimal (stored with 4 decimal places internally)
        """
        # Use 4 decimal precision for internal calculations
        base_confidence = DecimalPrecision.round_for_calculation(
            Decimal("0.9")
        )  # Start with 90% confidence

        # Reduce confidence based on warning flags with proper precision
        confidence_deductions = {
            "low_balance": DecimalPrecision.round_for_calculation(Decimal("0.2")),
            "high_credit_utilization": DecimalPrecision.round_for_calculation(
                Decimal("0.15")
            ),
            "large_outflow": DecimalPrecision.round_for_calculation(Decimal("0.1")),
        }

        for flag in warning_flags:
            if flag in confidence_deductions:
                base_confidence = DecimalPrecision.round_for_calculation(
                    base_confidence - confidence_deductions[flag]
                )

        # Adjust for transaction volume
        if len(transactions) > 5:  # High transaction volume increases uncertainty
            base_confidence = DecimalPrecision.round_for_calculation(
                base_confidence - DecimalPrecision.round_for_calculation(Decimal("0.1"))
            )

        # Ensure confidence stays within valid range with proper precision
        max_confidence = DecimalPrecision.round_for_calculation(Decimal("1.0"))
        min_confidence = DecimalPrecision.round_for_calculation(Decimal("0.1"))

        if base_confidence > max_confidence:
            return max_confidence
        elif base_confidence < min_confidence:
            return min_confidence
        else:
            return base_confidence
