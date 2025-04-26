import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.database.base import Base
from src.database.database import engine

# Import all models through __init__.py to ensure proper registration
from src.services.system_initialization import SystemInitializationService


async def init_db(db_engine: AsyncEngine) -> None:
    """Initialize the database with all models and system data"""
    # Create schema
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize system data through service layer
    async with AsyncSession(db_engine) as session:
        # Use SystemInitializationService to initialize all required system data
        system_init_service = SystemInitializationService(session)
        await system_init_service.initialize_system()


def init_database() -> None:
    """Run database initialization"""
    asyncio.run(init_db(engine))


if __name__ == "__main__":
    init_database()
