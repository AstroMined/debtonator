from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.database import get_db
from src.main import app
from src.registry.account_registry_init import register_account_types


# Ensure account type registry is initialized for testing
@pytest_asyncio.fixture(scope="function", autouse=True)
def initialize_account_registry():
    """Initialize the account type registry before any tests run."""
    register_account_types()
    return None  # Return value not used


# List of fixture modules to load
pytest_plugins = [
    # Environment fixtures
    "tests.fixtures.fixture_environment",
    # Consolidated feature flag fixtures
    "tests.fixtures.fixture_feature_flags",
    # Other service fixtures
    "tests.fixtures.services.fixture_service_factory",
    # Add repository fixtures
    "tests.fixtures.repositories.fixture_factory_repositories",
    "tests.fixtures.repositories.fixture_test_type_factory",
    "tests.fixtures.repositories.fixture_account_repositories",
    "tests.fixtures.repositories.fixture_balance_history_repositories",
    "tests.fixtures.repositories.fixture_balance_reconciliation_repositories",
    "tests.fixtures.repositories.fixture_bill_splits_repositories",
    "tests.fixtures.repositories.fixture_cashflow_repositories",
    "tests.fixtures.repositories.fixture_categories_repositories",
    "tests.fixtures.repositories.fixture_credit_limit_history_repositories",
    "tests.fixtures.repositories.fixture_deposit_schedules_repositories",
    "tests.fixtures.repositories.fixture_income_repositories",
    "tests.fixtures.repositories.fixture_income_categories_repositories",
    "tests.fixtures.repositories.fixture_liabilities_repositories",
    "tests.fixtures.repositories.fixture_payment_schedules_repositories",
    "tests.fixtures.repositories.fixture_payment_sources_repositories",
    "tests.fixtures.repositories.fixture_payments_repositories",
    "tests.fixtures.repositories.fixture_polymorphic_test_repositories",
    "tests.fixtures.repositories.fixture_recurring_bills_repositories",
    "tests.fixtures.repositories.fixture_recurring_income_repositories",
    "tests.fixtures.repositories.fixture_statement_history_repositories",
    "tests.fixtures.repositories.fixture_transaction_history_repositories",
    "tests.fixtures.repositories.fixture_basic_test_repositories",
    # Add account type repository fixtures
    "tests.fixtures.repositories.account_types.banking.fixture_checking_repositories",
    "tests.fixtures.repositories.account_types.banking.fixture_savings_repositories",
    "tests.fixtures.repositories.account_types.banking.fixture_credit_repositories",
    "tests.fixtures.repositories.account_types.banking.fixture_bnpl_repositories",
    "tests.fixtures.repositories.account_types.banking.fixture_payment_app_repositories",
    "tests.fixtures.repositories.account_types.banking.fixture_ewa_repositories",
    # Add service fixtures
    "tests.fixtures.services.fixture_accounts_services",
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
    "tests.fixtures.models.fixture_basic_test_models",
    # Account type model fixtures
    "tests.fixtures.models.account_types.banking.fixture_checking_models",
    "tests.fixtures.models.account_types.banking.fixture_credit_models",
    "tests.fixtures.models.account_types.banking.fixture_savings_models",
    "tests.fixtures.models.account_types.banking.fixture_payment_app_models",
    "tests.fixtures.models.account_types.banking.fixture_bnpl_models",
    "tests.fixtures.models.account_types.banking.fixture_ewa_models",
]


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


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Yield the SQLAlchemy engine"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
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
