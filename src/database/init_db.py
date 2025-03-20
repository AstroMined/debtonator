import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from .base import Base
from .database import engine


async def init_db(db_engine: AsyncEngine) -> None:
    """Initialize the database with all models"""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_database() -> None:
    """Run database initialization"""
    asyncio.run(init_db(engine))


if __name__ == "__main__":
    init_database()
