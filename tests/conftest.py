import asyncio
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.base import Base
from src.database.database import get_db
from src.main import app

# Test database URL - using SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        # Enable foreign key constraints
        await session.execute(text("PRAGMA foreign_keys=ON"))
        await session.commit()
        yield session

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        async with TestingSessionLocal() as session:
            await session.execute(text("PRAGMA foreign_keys=ON"))
            await session.commit()
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    class DebugTransport(httpx.ASGITransport):
        async def handle_async_request(self, request):
            print(f"\nRequest URL: {request.url}")
            return await super().handle_async_request(request)

    async with AsyncClient(
        transport=DebugTransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sync_client() -> Generator[TestClient, None, None]:
    def _get_test_db():
        session = TestingSessionLocal()
        try:
            session.execute(text("PRAGMA foreign_keys=ON"))
            session.commit()
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
