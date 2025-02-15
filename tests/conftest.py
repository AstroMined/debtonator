import asyncio
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.database import get_db
from src.main import app
from src.models.accounts import Account
from src.models.income import Income
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.models.categories import Category

# Test database URL - use in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

from sqlalchemy import event

# Create async engine for tests with improved configuration
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0,  # Add timeout for better async handling
    },
    pool_pre_ping=True,  # Add connection health checks
    echo=False  # True = Enable SQL logging for debugging
)

# Configure SQLite connection to handle timezone-aware datetimes
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA timezone='UTC'")
    cursor.close()

# Create async session factory
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False  # Disable autoflush for more predictable behavior
)

@pytest.fixture(scope="function")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

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

@pytest.fixture(scope="function")
async def base_account(db_session: AsyncSession) -> Account:
    """Create a basic checking account for testing with unique name"""
    unique_id = str(uuid.uuid4())[:8]
    account = Account(
        name=f"Primary Test Checking {unique_id}",  # Make name unique
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)  # Ensure we have latest data
    return account

@pytest.fixture(scope="function")
async def base_category(db_session: AsyncSession) -> Category:
    """Create a basic category for testing"""
    category = Category(
        name="Utilities",
        description="Utility bills and services",
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category

@pytest.fixture(scope="function")
async def base_bill(db_session: AsyncSession, base_account: Account, base_category: Category) -> Liability:
    """Create a basic bill for testing"""
    # Set due_date to 15 days from now for auto-pay testing
    from datetime import timedelta
    future_date = (datetime.now(ZoneInfo("UTC")) + timedelta(days=15)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    bill = Liability(
        name=f"Test Bill {str(uuid.uuid4())[:8]}",  # Make name unique
        amount=Decimal("100.00"),
        due_date=future_date,
        category_id=base_category.id,
        recurring=False,
        primary_account_id=base_account.id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)  # Ensure we have latest data
    return bill

@pytest.fixture(scope="function")
async def base_payment(
    db_session: AsyncSession,
    base_bill: Liability,
    base_account: Account
) -> Payment:
    """Create a basic payment with one payment source for testing"""
    payment = Payment(
        liability_id=base_bill.id,
        amount=Decimal("100.00"),
        payment_date=datetime(2025, 2, 15, tzinfo=ZoneInfo("UTC")),
        category="Utilities",
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(payment)
    await db_session.flush()
    await db_session.refresh(payment)  # Ensure we have latest data

    # Create payment source
    payment_source = PaymentSource(
        payment_id=payment.id,
        account_id=base_account.id,
        amount=Decimal("100.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(payment_source)
    await db_session.flush()
    await db_session.refresh(payment_source)  # Ensure we have latest data
    
    return payment

@pytest.fixture(scope="function")
async def base_credit_account(db_session: AsyncSession) -> Account:
    """Create a basic credit account for testing with unique name"""
    unique_id = str(uuid.uuid4())[:8]
    account = Account(
        name=f"Test Credit Card {unique_id}",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account

@pytest.fixture(scope="function")
async def base_income(db_session: AsyncSession, base_account: Account) -> Income:
    """Create a basic income entry for testing"""
    income = Income(
        date=datetime(2025, 2, 15, tzinfo=ZoneInfo("UTC")),
        source=f"Test Income {str(uuid.uuid4())[:8]}",  # Make source unique
        amount=Decimal("1000.00"),
        deposited=False,
        account_id=base_account.id,
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(income)
    await db_session.flush()
    await db_session.refresh(income)  # Ensure we have latest data
    return income
