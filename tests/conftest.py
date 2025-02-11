import asyncio
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool

from src.database.base import Base
from src.database.database import get_db
from src.main import app

# Test database URL - using SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create engine with NullPool to ensure clean connection handling
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,  # Use NullPool for better async handling
    echo=False  # Disable SQL logging for cleaner test output
)

# Use async_sessionmaker for better async session management
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.fixture(scope="function")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def setup_db() -> AsyncGenerator[AsyncSession, None]:
    """Set up a fresh test database for each test."""
    # Create all tables
    async with engine.begin() as conn:
        # Drop all tables first
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        # Enable foreign key support and other SQLite settings
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA synchronous=NORMAL"))
        await conn.commit()

    # Create a session for the test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        # Clean up - drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for each test with proper transaction handling."""
    session = await anext(setup_db)
    try:
        async with session.begin():
            yield session
    finally:
        await session.close()

@pytest.fixture
async def client(setup_db) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with proper database session handling."""
    async def _get_test_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=True
    ) as test_client:
        try:
            yield test_client
        finally:
            app.dependency_overrides.clear()

@pytest.fixture
def sync_client(setup_db) -> Generator[TestClient, None, None]:
    """Provide a synchronous test client for non-async tests."""
    def _get_test_db():
        session = TestingSessionLocal()
        try:
            session.execute(text("PRAGMA foreign_keys=ON"))
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        try:
            yield test_client
        finally:
            app.dependency_overrides.clear()
