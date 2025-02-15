from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Union
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.models.income import Income
from src.models.categories import Category
from src.schemas.cashflow import CustomForecastParameters, CustomForecastResponse, CustomForecastResult

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
    
    async def get_custom_forecast(
        self,
        params: CustomForecastParameters
    ) -> CustomForecastResponse:
        """Get a custom forecast based on provided parameters."""
        return await calculate_custom_forecast(self.db, params)

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

async def calculate_custom_forecast(
    db: AsyncSession,
    params: "CustomForecastParameters"  # type: ignore
) -> "CustomForecastResponse":  # type: ignore
    """Calculate a custom forecast based on provided parameters."""
    results = []
    total_confidence = Decimal("0.0")
    summary_stats: Dict[str, Decimal] = {
        "total_projected_income": Decimal("0.0"),
        "total_projected_expenses": Decimal("0.0"),
        "average_confidence": Decimal("0.0"),
        "min_balance": Decimal("999999999.99"),
        "max_balance": Decimal("-999999999.99")
    }

    # Get accounts to analyze
    accounts_query = select(Account)
    if params.account_ids:
        accounts_query = accounts_query.where(Account.id.in_(params.account_ids))
    accounts = (await db.execute(accounts_query)).scalars().all()
    
    if not accounts:
        raise ValueError("No valid accounts found for analysis")

    # Initialize starting balances
    current_balances = {
        acc.id: acc.available_balance for acc in accounts
    }

    # Get liabilities query
    liabilities_query = (
        select(Liability)
        .outerjoin(Payment)
        .where(
            Liability.due_date >= params.start_date,
            Liability.due_date <= params.end_date,
            Payment.id == None  # No associated payments
        )
    )
    if params.account_ids:
        liabilities_query = liabilities_query.where(
            Liability.primary_account_id.in_(params.account_ids)
        )
    if params.categories:
        liabilities_query = liabilities_query.where(
            Liability.category_id.in_(
                select(Category.id).where(Category.name.in_(params.categories))
            )
        )
    
    # Get income query
    income_query = (
        select(Income)
        .where(
            Income.date >= params.start_date,
            Income.date <= params.end_date,
            Income.deposited == False
        )
    )
    if params.account_ids:
        income_query = income_query.where(
            Income.account_id.in_(params.account_ids)
        )
    
    # Fetch data
    liabilities = (await db.execute(liabilities_query)).scalars().all()
    income_entries = (await db.execute(income_query)).scalars().all()
    
    current_date = params.start_date
    days_processed = 0
    
    while current_date <= params.end_date:
        # Calculate daily projections
        daily_expenses = Decimal("0.0")
        daily_income = Decimal("0.0")
        contributing_factors: Dict[str, Decimal] = {}
        risk_factors: Dict[str, Decimal] = {}
        
        # Process liabilities
        daily_liabilities = [
            l for l in liabilities if l.due_date == current_date
        ]
        for liability in daily_liabilities:
            daily_expenses += liability.amount
            # Get category name from the database
            category_query = select(Category).where(Category.id == liability.category_id)
            category = (await db.execute(category_query)).scalar_one()
            contributing_factors[f"liability_{category.name}"] = liability.amount
            
            # Risk assessment for liability
            if liability.amount > current_balances[liability.primary_account_id]:
                risk_factors["insufficient_funds"] = Decimal("0.3")
        
        # Process income
        daily_income_entries = [
            i for i in income_entries if i.date == current_date
        ]
        for income in daily_income_entries:
            daily_income += income.amount
            contributing_factors[f"income_{income.source}"] = income.amount
        
        # Update balances
        for acc_id in current_balances:
            # Simplified balance update - in reality would need more complex logic
            # for handling split payments and income distribution
            current_balances[acc_id] += (daily_income / len(current_balances))
            current_balances[acc_id] -= (daily_expenses / len(current_balances))
        
        # Calculate confidence score
        base_confidence = Decimal("1.0")
        if risk_factors:
            base_confidence -= sum(risk_factors.values())
        
        confidence_score = max(min(base_confidence, Decimal("1.0")), Decimal("0.0"))
        
        # Create forecast result
        total_balance = sum(current_balances.values())
        result = {
            "date": current_date,
            "projected_balance": total_balance,
            "projected_income": daily_income,
            "projected_expenses": daily_expenses,
            "confidence_score": confidence_score,
            "contributing_factors": contributing_factors,
            "risk_factors": risk_factors
        }
        
        results.append(result)
        
        # Update summary statistics
        summary_stats["total_projected_income"] += daily_income
        summary_stats["total_projected_expenses"] += daily_expenses
        summary_stats["min_balance"] = min(summary_stats["min_balance"], total_balance)
        summary_stats["max_balance"] = max(summary_stats["max_balance"], total_balance)
        total_confidence += confidence_score
        days_processed += 1
        
        current_date += timedelta(days=1)
    
    # Calculate average confidence
    summary_stats["average_confidence"] = (
        total_confidence / days_processed if days_processed > 0 else Decimal("0.0")
    )
    
    return CustomForecastResponse(
        parameters=params,
        results=[
            CustomForecastResult(
                date=r["date"],
                projected_balance=r["projected_balance"],
                projected_income=r["projected_income"],
                projected_expenses=r["projected_expenses"],
                confidence_score=r["confidence_score"],
                contributing_factors=r["contributing_factors"],
                risk_factors=r["risk_factors"]
            ) for r in results
        ],
        overall_confidence=summary_stats["average_confidence"],
        summary_statistics=summary_stats,
        timestamp=date.today()
    )
