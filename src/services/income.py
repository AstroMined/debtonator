from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.income import Income
from ..schemas.income import IncomeCreate, IncomeUpdate, IncomeFilters

class IncomeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, income_data: IncomeCreate) -> Income:
        """Create a new income record"""
        income = Income(**income_data.model_dump())
        income.calculate_undeposited()
        self.session.add(income)
        await self.session.commit()
        await self.session.refresh(income)
        return income

    async def get(self, income_id: int) -> Optional[Income]:
        """Get an income record by ID"""
        result = await self.session.get(Income, income_id)
        return result

    async def update(self, income_id: int, income_data: IncomeUpdate) -> Optional[Income]:
        """Update an income record"""
        income = await self.get(income_id)
        if not income:
            return None

        update_data = income_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(income, field, value)

        income.calculate_undeposited()
        await self.session.commit()
        await self.session.refresh(income)
        return income

    async def delete(self, income_id: int) -> bool:
        """Delete an income record"""
        income = await self.get(income_id)
        if not income:
            return False

        await self.session.delete(income)
        await self.session.commit()
        return True

    async def list(
        self,
        filters: Optional[IncomeFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Income], int]:
        """List income records with optional filtering"""
        query = select(Income)

        if filters:
            conditions = []
            if filters.start_date:
                conditions.append(Income.date >= filters.start_date)
            if filters.end_date:
                conditions.append(Income.date <= filters.end_date)
            if filters.source:
                conditions.append(Income.source.ilike(f"%{filters.source}%"))
            if filters.deposited is not None:
                conditions.append(Income.deposited == filters.deposited)
            if filters.min_amount:
                conditions.append(Income.amount >= filters.min_amount)
            if filters.max_amount:
                conditions.append(Income.amount <= filters.max_amount)

            if conditions:
                query = query.where(and_(*conditions))

        # Get total count
        count_query = select(Income)
        if filters and conditions:
            count_query = count_query.where(and_(*conditions))
        total = len((await self.session.execute(count_query)).scalars().all())

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        return items, total

    async def get_undeposited(self) -> List[Income]:
        """Get all undeposited income records"""
        query = select(Income).where(Income.deposited == False)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def mark_as_deposited(self, income_id: int) -> Optional[Income]:
        """Mark an income record as deposited"""
        income = await self.get(income_id)
        if not income:
            return None

        income.deposited = True
        income.calculate_undeposited()
        await self.session.commit()
        await self.session.refresh(income)
        return income

    async def get_total_undeposited(self) -> Decimal:
        """Get total amount of undeposited income"""
        query = select(Income).where(Income.deposited == False)
        result = await self.session.execute(query)
        undeposited_records = result.scalars().all()
        return sum(income.amount for income in undeposited_records)
