import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.constants import (
    DEFAULT_CATEGORY_DESCRIPTION,
    DEFAULT_CATEGORY_ID,
    DEFAULT_CATEGORY_NAME,
)
from src.models.categories import Category

from .base import Base
from .database import engine


async def init_db(db_engine: AsyncEngine) -> None:
    """Initialize the database with all models and default data"""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create default category if it doesn't exist
    async with AsyncSession(db_engine) as session:
        # Check if default category exists
        result = await session.execute(
            select(Category).where(Category.id == DEFAULT_CATEGORY_ID)
        )
        default_category = result.scalars().first()

        if not default_category:
            # Create default category
            default_category = Category(
                id=DEFAULT_CATEGORY_ID,
                name=DEFAULT_CATEGORY_NAME,
                description=DEFAULT_CATEGORY_DESCRIPTION,
                system=True,
            )
            session.add(default_category)
            await session.commit()


def init_database() -> None:
    """Run database initialization"""
    asyncio.run(init_db(engine))


if __name__ == "__main__":
    init_database()
