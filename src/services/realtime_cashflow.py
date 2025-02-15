from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.schemas.realtime_cashflow import AccountBalance, RealtimeCashflow


class RealtimeCashflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_account_balances(self) -> List[AccountBalance]:
        """Fetch current balances for all accounts."""
        query = select(Account)
        result = await self.db.execute(query)
        accounts = result.scalars().all()

        return [
            AccountBalance(
                account_id=account.id,
                name=account.name,
                type=account.type,
                current_balance=account.available_balance,
                available_credit=account.available_credit,
                total_limit=account.total_limit
            )
            for account in accounts
        ]

    async def get_upcoming_bill(self) -> Tuple[Optional[datetime], Optional[int]]:
        """Get the next upcoming bill and days until due."""
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date >= datetime.now().date()
        ).order_by(Liability.due_date)
        
        result = await self.db.execute(query)
        bills = result.scalars().all()

        if not bills:
            return None, None

        # Get the earliest bill
        next_bill = min(bills, key=lambda x: x.due_date)
        days_until = (next_bill.due_date - datetime.now().date()).days
        return next_bill.due_date, days_until

    async def calculate_minimum_balance(self) -> Decimal:
        """Calculate minimum balance required for upcoming bills."""
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date <= (datetime.now() + timedelta(days=14)).date()
        )
        result = await self.db.execute(query)
        upcoming_bills = result.scalars().all()

        return sum((bill.amount for bill in upcoming_bills), Decimal(0))

    async def get_realtime_cashflow(self) -> RealtimeCashflow:
        """Get real-time cashflow data across all accounts."""
        account_balances = await self.get_account_balances()
        
        total_funds = sum(
            (acc.current_balance for acc in account_balances 
             if acc.type != "credit"),
            Decimal(0)
        )
        
        total_credit = sum(
            (acc.available_credit for acc in account_balances 
             if acc.type == "credit" and acc.available_credit is not None),
            Decimal(0)
        )

        # Get upcoming bills
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date >= datetime.now().date()
        )
        result = await self.db.execute(query)
        upcoming_bills = result.scalars().all()
        total_liabilities = sum((bill.amount for bill in upcoming_bills), Decimal(0))

        next_bill_date, days_until_bill = await self.get_upcoming_bill()
        min_balance = await self.calculate_minimum_balance()

        # Calculate projected deficit
        projected_deficit = None
        if total_funds < min_balance:
            projected_deficit = min_balance - total_funds

        return RealtimeCashflow(
            account_balances=account_balances,
            total_available_funds=total_funds,
            total_available_credit=total_credit,
            total_liabilities_due=total_liabilities,
            net_position=total_funds - total_liabilities,
            next_bill_due=next_bill_date,
            days_until_next_bill=days_until_bill,
            minimum_balance_required=min_balance,
            projected_deficit=projected_deficit
        )
