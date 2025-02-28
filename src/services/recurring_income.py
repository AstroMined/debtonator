from datetime import date
from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy import select, and_, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.recurring_income import RecurringIncome
from src.models.income import Income
from src.models.accounts import Account
from src.schemas.income import RecurringIncomeCreate, RecurringIncomeUpdate, GenerateIncomeRequest

class RecurringIncomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, income_data: RecurringIncomeCreate) -> RecurringIncome:
        """Create a new recurring income template."""
        # Verify account exists
        stmt = (
            select(Account)
            .where(Account.id == income_data.account_id)
        )
        result = await self.db.execute(stmt)
        account = result.unique().scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        recurring_income = RecurringIncome(
            source=income_data.source,
            amount=income_data.amount,
            day_of_month=income_data.day_of_month,
            account_id=income_data.account_id,
            category_id=income_data.category_id,
            auto_deposit=income_data.auto_deposit,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(recurring_income)
        await self.db.commit()
        await self.db.refresh(recurring_income)
        return recurring_income
    
    async def get(self, recurring_income_id: int) -> Optional[RecurringIncome]:
        """Get a recurring income template by ID."""
        stmt = (
            select(RecurringIncome)
            .options(
                joinedload(RecurringIncome.account),
                joinedload(RecurringIncome.category),
                joinedload(RecurringIncome.income_entries)
            )
            .where(RecurringIncome.id == recurring_income_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    async def update(
        self, recurring_income_id: int, income_data: RecurringIncomeUpdate
    ) -> Optional[RecurringIncome]:
        """Update a recurring income template."""
        recurring_income = await self.get(recurring_income_id)
        if not recurring_income:
            return None
        
        update_data = income_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(recurring_income, field, value)
        
        recurring_income.updated_at = date.today()
        await self.db.commit()
        await self.db.refresh(recurring_income)
        return recurring_income
    
    async def delete(self, recurring_income_id: int) -> bool:
        """Delete a recurring income template."""
        recurring_income = await self.get(recurring_income_id)
        if not recurring_income:
            return False
        
        await self.db.delete(recurring_income)
        await self.db.commit()
        return True
    
    async def list(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RecurringIncome], int]:
        """List recurring income templates."""
        # Get total count
        count_query = select(func.count()).select_from(RecurringIncome)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()
        
        # Get paginated results with relationships
        query = (
            select(RecurringIncome)
            .options(
                joinedload(RecurringIncome.account),
                joinedload(RecurringIncome.category)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = result.unique().scalars().all()
        
        return items, total
    
    async def generate_income(self, request: GenerateIncomeRequest) -> List[Income]:
        """Generate income entries for a specific month/year from recurring templates."""
        # Get all active recurring income templates
        stmt = (
            select(RecurringIncome)
            .options(
                joinedload(RecurringIncome.account),
                joinedload(RecurringIncome.category)
            )
            .where(RecurringIncome.active == True)
        )
        result = await self.db.execute(stmt)
        templates = result.unique().scalars().all()
        
        generated_income = []
        for template in templates:
            # Check if income entry already exists for this month/year
            existing_stmt = (
                select(Income)
                .where(
                    and_(
                        Income.recurring_income_id == template.id,
                        func.strftime('%m', Income.date).cast(Integer) == request.month,
                        func.strftime('%Y', Income.date).cast(Integer) == request.year
                    )
                )
            )
            existing = await self.db.execute(existing_stmt)
            if existing.first() is None:
                # Create new income entry from template
                income_entry = template.create_income_entry(request.month, request.year)
                self.db.add(income_entry)
                generated_income.append(income_entry)
        
        if generated_income:
            await self.db.commit()
            # Refresh all generated entries to load relationships
            for entry in generated_income:
                await self.db.refresh(entry)
        
        return generated_income
