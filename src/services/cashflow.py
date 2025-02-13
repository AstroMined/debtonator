from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Union
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.models.income import Income

class CashflowService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_forecast(
        self,
        account_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Union[date, Decimal]]]:
        """Get cashflow forecast for the specified date range."""
        return await calculate_forecast(self.db, account_id, start_date, end_date)
    
    async def get_required_funds(
        self,
        account_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """Get required funds for bills in the specified date range."""
        return await calculate_required_funds(self.db, account_id, start_date, end_date)
    
    def get_daily_deficit(self, min_amount: Decimal, days: int) -> Decimal:
        """Calculate daily deficit needed to cover minimum required amount."""
        return calculate_daily_deficit(min_amount, days)
    
    def get_yearly_deficit(self, daily_deficit: Decimal) -> Decimal:
        """Calculate yearly deficit based on daily deficit."""
        return calculate_yearly_deficit(daily_deficit)
    
    def get_required_income(
        self,
        yearly_deficit: Decimal,
        tax_rate: Decimal = Decimal("0.80")
    ) -> Decimal:
        """Calculate required gross income to cover yearly deficit."""
        return calculate_required_income(yearly_deficit, tax_rate)

async def calculate_forecast(
    db: AsyncSession,
    account_id: int,
    start_date: date,
    end_date: date
) -> List[Dict[str, Union[date, Decimal]]]:
    """Calculate daily cashflow forecast for the specified date range."""
    # Get account with relationships
    account = await db.get(Account, account_id)
    if not account:
        raise ValueError(f"Account with id {account_id} not found")
    
    # Get all unpaid liabilities in date range with relationships
    result = await db.execute(
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
    
    # Get all income in date range with relationships
    result = await db.execute(
        select(Income)
        .where(
            Income.account_id == account_id,
            Income.date >= start_date,
            Income.date <= end_date,
            Income.deposited == False
        )
    )
    income_entries = result.scalars().all()
    
    # Create daily forecast
    forecast = []
    current_balance = account.available_balance
    current_date = start_date
    
    while current_date <= end_date:
        # Add liabilities due on this date
        liabilities_due = sum(
            liability.amount for liability in liabilities
            if liability.due_date == current_date
        )
        current_balance -= liabilities_due
        
        # Add income on this date
        income_received = sum(
            income.amount for income in income_entries
            if income.date == current_date
        )
        current_balance += income_received
        
        forecast.append({
            "date": current_date,
            "balance": current_balance
        })
        
        current_date += timedelta(days=1)
    
    return forecast

async def calculate_required_funds(
    db: AsyncSession,
    account_id: int,
    start_date: date,
    end_date: date
) -> Decimal:
    """Calculate total required funds for bills in the specified date range."""
    result = await db.execute(
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

def calculate_daily_deficit(min_amount: Decimal, days: int) -> Decimal:
    """Calculate daily deficit needed to cover minimum required amount."""
    if min_amount >= 0:
        return Decimal("0.00")
    # Round to 2 decimal places with ROUND_HALF_UP
    return Decimal(str(round(float(abs(min_amount)) / days, 2)))

def calculate_yearly_deficit(daily_deficit: Decimal) -> Decimal:
    """Calculate yearly deficit based on daily deficit."""
    return daily_deficit * 365

def calculate_required_income(
    yearly_deficit: Decimal,
    tax_rate: Decimal = Decimal("0.80")
) -> Decimal:
    """
    Calculate required gross income to cover yearly deficit.
    Default tax_rate of 0.80 assumes 20% tax rate.
    """
    return yearly_deficit / tax_rate
