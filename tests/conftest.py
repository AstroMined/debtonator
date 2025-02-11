import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.database import get_db
from src.main import app
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource

# Test database URL - use in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for tests
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create async session factory
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    """Yield the SQLAlchemy engine"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Get a TestingSessionLocal instance that rolls back all changes"""
    connection = await db_engine.connect()
    transaction = await connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

@pytest.fixture(scope="function")
async def client(db_session) -> Generator:
    """Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def base_account(db_session: AsyncSession) -> Account:
    """Create a basic checking account for testing"""
    account = Account(
        name="Primary Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture(scope="function")
async def base_bill(db_session: AsyncSession, base_account: Account) -> Liability:
    """Create a basic bill for testing"""
    bill = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=date(2025, 3, 1),
        category="Utilities",
        recurring=False,
        primary_account_id=base_account.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(bill)
    await db_session.commit()
    await db_session.refresh(bill)
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
        payment_date=date(2025, 2, 15),
        category="Utilities",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    # Create payment source
    payment_source = PaymentSource(
        payment_id=payment.id,
        account_id=base_account.id,
        amount=Decimal("100.00"),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(payment_source)
    await db_session.commit()
    
    return payment
