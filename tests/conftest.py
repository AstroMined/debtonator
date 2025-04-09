import inspect
import re
import warnings
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.database import get_db
from src.main import app
from src.registry.account_registry_init import register_account_types


# Ensure account type registry is initialized for testing
@pytest.fixture(scope="session", autouse=True)
def initialize_account_registry():
    """Initialize the account type registry before any tests run."""
    register_account_types()
    return None  # Return value not used


# List of fixture modules to load
pytest_plugins = [
    # Add repository fixtures
    "tests.fixtures.repositories.fixture_repositories",
    "tests.fixtures.repositories.fixture_basic_test_repositories",
    # Add service fixtures
    "tests.fixtures.services.fixture_services",
    # Add model fixtures
    "tests.fixtures.models.fixture_accounts_models",
    "tests.fixtures.models.fixture_categories_models",
    "tests.fixtures.models.fixture_liabilities_models",
    "tests.fixtures.models.fixture_payments_models",
    "tests.fixtures.models.fixture_balance_models",
    "tests.fixtures.models.fixture_cashflow_models",
    "tests.fixtures.models.fixture_income_models",
    "tests.fixtures.models.fixture_income_categories_models",
    "tests.fixtures.models.fixture_statements_models",
    "tests.fixtures.models.fixture_transactions_models",
    "tests.fixtures.models.fixture_recurring_models",
    "tests.fixtures.models.fixture_schedules_models",
    "tests.fixtures.models.fixture_feature_flags_models",
    "tests.fixtures.models.fixture_basic_test_models",
    # Account type model fixtures
    "tests.fixtures.models.account_types.banking.fixture_checking_models",
    "tests.fixtures.models.account_types.banking.fixture_credit_models",
    "tests.fixtures.models.account_types.banking.fixture_savings_models",
    "tests.fixtures.models.account_types.banking.fixture_payment_app_models",
    "tests.fixtures.models.account_types.banking.fixture_bnpl_models",
    "tests.fixtures.models.account_types.banking.fixture_ewa_models",
]

# ADR-011 Datetime validation hooks


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    """Warn about naive datetime usage in tests that run successfully."""
    if not hasattr(item, "function"):
        return

    try:
        source = inspect.getsource(item.function)
    except (OSError, IOError):
        return

    naive_patterns = [
        r"datetime\.now\(\)",
        r"datetime\.utcnow\(\)",
        r"datetime\([^)]*\)\s*(?!.*tzinfo=)",
    ]

    for pattern in naive_patterns:
        if re.search(pattern, source):
            warnings.warn(
                f"\n⚠️ ADR-011 Warning: {item.name} contains naive datetime usage.\n"
                f"Use tests/helpers/datetime_utils.py functions instead.\n",
                category=UserWarning,
            )
            break


# Test database URL - use in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for tests with improved configuration
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0,  # Add timeout for better async handling
    },
    pool_pre_ping=True,  # Add connection health checks
    echo=False,  # True = Enable SQL logging for debugging
)

# Create async session factory
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="function")
async def db_engine():
    """Yield the SQLAlchemy engine"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new session and transaction for each test."""
    connection = await db_engine.connect()

    # Start an outer transaction that we'll roll back
    await connection.begin()

    # Begin a nested transaction that the service can commit
    session = TestingSessionLocal(bind=connection)
    await session.begin_nested()

    try:
        yield session
    finally:
        await session.close()
        await connection.rollback()
        await connection.close()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a new AsyncClient that uses the test database."""

    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
