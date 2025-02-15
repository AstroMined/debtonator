from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union
from sqlalchemy import select

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.schemas.cashflow import CustomForecastResult

from .base import BaseService
from .transaction_service import TransactionService
from .types import DateType

class MetricsService(BaseService):
    """Service for calculating cashflow metrics and analysis."""

    def __init__(self, db):
        super().__init__(db)
        self._transaction_service = TransactionService(db)

    async def get_metrics_for_date(
        self,
        target_date: DateType
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
                include_transfers=True
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
            []  # No warning flags for this calculation
        )

        return CustomForecastResult(
            date=target_date,
            projected_balance=total_balance,
            projected_income=total_inflow,
            projected_expenses=total_outflow,
            confidence_score=confidence_score,
            contributing_factors={
                "total_accounts": len(accounts),
                "total_transactions": len(day_transactions)
            },
            risk_factors={}
        )

    async def calculate_required_funds(
        self,
        account_id: int,
        start_date: DateType,
        end_date: DateType
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
                Payment.id == None  # No associated payments
            )
        )
        liabilities = result.scalars().all()
        return sum(liability.amount for liability in liabilities)

    def calculate_daily_deficit(
        self,
        min_amount: Decimal,
        days: int
    ) -> Decimal:
        """Calculate daily deficit needed to cover minimum required amount.
        
        Args:
            min_amount: Minimum amount needed
            days: Number of days to spread deficit over
            
        Returns:
            Daily deficit amount
        """
        if min_amount >= 0:
            return Decimal("0.00")
        # Round to 2 decimal places with ROUND_HALF_UP
        return Decimal(str(round(float(abs(min_amount)) / days, 2)))

    def calculate_yearly_deficit(
        self,
        daily_deficit: Decimal
    ) -> Decimal:
        """Calculate yearly deficit based on daily deficit.
        
        Args:
            daily_deficit: Daily deficit amount
            
        Returns:
            Yearly deficit amount
        """
        return daily_deficit * 365

    def calculate_required_income(
        self,
        yearly_deficit: Decimal,
        tax_rate: Decimal = Decimal("0.80")
    ) -> Decimal:
        """Calculate required gross income to cover yearly deficit.
        
        Args:
            yearly_deficit: Yearly deficit amount
            tax_rate: Tax rate as decimal (default 0.80 assumes 20% tax rate)
            
        Returns:
            Required gross income
        """
        return yearly_deficit / tax_rate

    def _calculate_day_confidence(
        self,
        account: Account,
        balance: Decimal,
        transactions: List[Dict],
        warning_flags: List[str]
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
            "large_outflow": Decimal("0.1")
        }
        
        for flag in warning_flags:
            if flag in confidence_deductions:
                base_confidence -= confidence_deductions[flag]

        # Adjust for transaction volume
        if len(transactions) > 5:  # High transaction volume increases uncertainty
            base_confidence -= Decimal("0.1")

        # Ensure confidence stays within valid range
        return max(min(base_confidence, Decimal("1.0")), Decimal("0.1"))
