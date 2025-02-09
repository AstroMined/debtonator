from decimal import Decimal
from datetime import date
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.accounts import Account

class IncomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_income(
        self,
        date: date,
        source: str,
        amount: Decimal,
        account_id: int,
        deposited: bool = False
    ) -> Income:
        """Create a new income entry."""
        income = Income(
            date=date,
            source=source,
            amount=amount,
            deposited=deposited,
            account_id=account_id,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(income)
        await self.db.commit()
        return income
    
    async def get_undeposited_amount(self, income_id: int) -> Decimal:
        """Get the undeposited amount for an income entry."""
        return await calculate_undeposited_amount(self.db, income_id)
    
    async def deposit_income(self, income_id: int) -> None:
        """Deposit income into the associated account."""
        await update_account_balance_from_income(self.db, income_id)
    
    async def get_income_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Income]:
        """Get all income entries within a date range."""
        result = await self.db.execute(
            select(Income).where(
                Income.date >= start_date,
                Income.date <= end_date
            )
        )
        return result.scalars().all()

async def calculate_undeposited_amount(db: AsyncSession, income_id: int) -> Decimal:
    """Calculate the undeposited amount for a given income entry."""
    result = await db.execute(
        select(Income).where(Income.id == income_id)
    )
    income = result.scalar_one()
    return income.amount if not income.deposited else Decimal("0.00")

async def update_account_balance_from_income(db: AsyncSession, income_id: int) -> None:
    """
    Update account balance when income is deposited.
    Only updates if the income hasn't been deposited yet.
    """
    # Get the income entry
    result = await db.execute(
        select(Income).where(Income.id == income_id)
    )
    income = result.scalar_one()
    
    # Skip if already deposited
    if income.deposited:
        return
    
    # Get the target account
    result = await db.execute(
        select(Account).where(Account.id == income.account_id)
    )
    account = result.scalar_one()
    
    # Update account balance
    account.available_balance += income.amount
    
    # Mark income as deposited
    income.deposited = True
    
    await db.commit()
