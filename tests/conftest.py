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

@pytest.fixture(scope="function")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def setup_db() -> AsyncGenerator:
    print("\nSetting up test database...")
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created")
        
        # List all tables in Base.metadata
        print(f"Tables in Base.metadata: {Base.metadata.tables.keys()}")
        
        # List actually created tables
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.scalars().all()
        print(f"Actually created tables in database: {tables}")
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Database tables dropped")

@pytest.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        # Enable foreign key constraints
        await session.execute(text("PRAGMA foreign_keys=ON"))
        await session.commit()
        yield session

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        print("\nCreating test database session...")
        async with TestingSessionLocal() as session:
            await session.execute(text("PRAGMA foreign_keys=ON"))
            await session.commit()
            print("Test database session created")
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    class DebugTransport(httpx.ASGITransport):
        async def handle_async_request(self, request):
            print(f"\nRequest Method: {request.method}")
            print(f"Request URL: {request.url}")
            print(f"Request Headers: {request.headers}")
            print(f"Request Body: {request.content.decode() if request.content else None}")
            response = await super().handle_async_request(request)
            content = await response.aread()
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {content.decode() if content else None}")
            return response

    async with AsyncClient(
        transport=DebugTransport(app=app), 
        base_url="http://testserver",
        follow_redirects=True
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
