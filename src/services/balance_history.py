from datetime import datetime
from decimal import Decimal
from statistics import mean, stdev
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.balance_history import BalanceHistory
from src.schemas.balance_history import BalanceHistoryCreate, BalanceTrend
from src.utils.decimal_precision import DecimalPrecision


class BalanceHistoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_balance_change(
        self, balance_data: BalanceHistoryCreate, timestamp: Optional[datetime] = None
    ) -> BalanceHistory:
        """Record a new balance history entry"""
        # Verify account exists
        query = select(Account).where(Account.id == balance_data.account_id)
        result = await self.session.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise ValueError(f"Account {balance_data.account_id} not found")

        db_entry = BalanceHistory(
            **balance_data.model_dump(), timestamp=timestamp or datetime.utcnow()
        )
        self.session.add(db_entry)
        await self.session.commit()
        await self.session.refresh(db_entry)
        return db_entry

    async def get_balance_history(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[BalanceHistory]:
        """Get balance history for an account within a date range"""
        query = (
            select(BalanceHistory)
            .where(BalanceHistory.account_id == account_id)
            .order_by(BalanceHistory.timestamp)
        )

        if start_date:
            query = query.where(BalanceHistory.timestamp >= start_date)
        if end_date:
            query = query.where(BalanceHistory.timestamp <= end_date)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_balance_trend(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> BalanceTrend:
        """Calculate balance trends for an account within a date range"""
        history = await self.get_balance_history(account_id, start_date, end_date)

        if not history:
            raise ValueError(f"No balance history found for account {account_id}")

        balances = [float(entry.balance) for entry in history]

        # Calculate basic statistics with proper precision
        start_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(balances[0]))
        )
        end_balance = DecimalPrecision.round_for_calculation(Decimal(str(balances[-1])))
        net_change = DecimalPrecision.round_for_calculation(end_balance - start_balance)
        avg_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(mean(balances)))
        )
        min_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(min(balances)))
        )
        max_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(max(balances)))
        )

        # Calculate volatility (standard deviation) with proper precision
        volatility = DecimalPrecision.round_for_calculation(
            Decimal(str(stdev(balances))) if len(balances) > 1 else Decimal("0")
        )

        # Determine trend direction - use a slightly higher threshold for "stable" with 4 decimal places
        if abs(net_change) < Decimal("0.0001"):
            trend_direction = "stable"
        else:
            trend_direction = "increasing" if net_change > 0 else "decreasing"

        # The values will be automatically rounded to 2 decimal places for display
        # by the Pydantic schema when returned in API responses
        return BalanceTrend(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            start_balance=start_balance,
            end_balance=end_balance,
            net_change=net_change,
            average_balance=avg_balance,
            min_balance=min_balance,
            max_balance=max_balance,
            trend_direction=trend_direction,
            volatility=volatility,
        )

    async def mark_reconciled(
        self, balance_history_id: int, notes: Optional[str] = None
    ) -> BalanceHistory:
        """Mark a balance history entry as reconciled"""
        query = select(BalanceHistory).where(BalanceHistory.id == balance_history_id)
        result = await self.session.execute(query)
        entry = result.scalar_one_or_none()

        if not entry:
            raise ValueError(f"Balance history entry {balance_history_id} not found")

        entry.is_reconciled = True
        if notes:
            entry.notes = notes

        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def get_unreconciled_entries(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[BalanceHistory]:
        """Get unreconciled balance history entries for an account"""
        query = (
            select(BalanceHistory)
            .where(
                BalanceHistory.account_id == account_id,
                BalanceHistory.is_reconciled == False,
            )
            .order_by(BalanceHistory.timestamp)
        )

        if start_date:
            query = query.where(BalanceHistory.timestamp >= start_date)
        if end_date:
            query = query.where(BalanceHistory.timestamp <= end_date)

        result = await self.session.execute(query)
        return list(result.scalars().all())
