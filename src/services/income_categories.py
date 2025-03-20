from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.income_categories import IncomeCategory
from ..schemas.income_categories import IncomeCategoryCreate, IncomeCategoryUpdate
from ..utils.db import handle_db_error


class IncomeCategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(self, category: IncomeCategoryCreate) -> IncomeCategory:
        """Create a new income category"""
        try:
            db_category = IncomeCategory(**category.model_dump())
            self.session.add(db_category)
            await self.session.commit()
            await self.session.refresh(db_category)
            return db_category
        except IntegrityError as e:
            await self.session.rollback()
            handle_db_error(e)

    async def get_category(self, category_id: int) -> Optional[IncomeCategory]:
        """Get a category by ID"""
        result = await self.session.execute(
            select(IncomeCategory).where(IncomeCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_categories(self) -> List[IncomeCategory]:
        """Get all income categories"""
        result = await self.session.execute(select(IncomeCategory))
        return list(result.scalars().all())

    async def update_category(
        self, category_id: int, category: IncomeCategoryUpdate
    ) -> Optional[IncomeCategory]:
        """Update a category"""
        try:
            update_data = category.model_dump(exclude_unset=True)
            if not update_data:
                return await self.get_category(category_id)

            result = await self.session.execute(
                update(IncomeCategory)
                .where(IncomeCategory.id == category_id)
                .values(**update_data)
                .returning(IncomeCategory)
            )
            await self.session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as e:
            await self.session.rollback()
            handle_db_error(e)

    async def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        result = await self.session.execute(
            delete(IncomeCategory).where(IncomeCategory.id == category_id)
        )
        await self.session.commit()
        return result.rowcount > 0
