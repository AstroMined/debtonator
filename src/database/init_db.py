import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.database.base import Base
from src.database.database import engine

# Import all models through __init__.py to ensure proper registration
from src.repositories.categories import CategoryRepository
from src.services.system_initialization import ensure_system_categories


async def init_db(db_engine: AsyncEngine) -> None:
    """Initialize the database with all models and system data"""
    # Create schema
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize system data through repository layer
    async with AsyncSession(db_engine) as session:
        # Use repository for all data access
        category_repo = CategoryRepository(session)
        await ensure_system_categories(category_repo)


def init_database() -> None:
    """Run database initialization"""
    asyncio.run(init_db(engine))


if __name__ == "__main__":
    init_database()
