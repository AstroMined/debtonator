import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.accounts import AccountRepository
from src.repositories.balance_history import BalanceHistoryRepository
from src.repositories.balance_reconciliation import BalanceReconciliationRepository
from src.repositories.bill_splits import BillSplitRepository
from src.repositories.cashflow import CashflowForecastRepository
from src.repositories.categories import CategoryRepository
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.deposit_schedules import DepositScheduleRepository
from src.repositories.income import IncomeRepository
from src.repositories.income_categories import IncomeCategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payment_schedules import PaymentScheduleRepository
from src.repositories.payment_sources import PaymentSourceRepository
from src.repositories.payments import PaymentRepository
from src.repositories.recurring_bills import RecurringBillRepository
from src.repositories.recurring_income import RecurringIncomeRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.transaction_history import TransactionHistoryRepository


# Repository fixtures
@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def balance_history_repository(
    db_session: AsyncSession,
) -> BalanceHistoryRepository:
    """Fixture for BalanceHistoryRepository with test database session."""
    return BalanceHistoryRepository(db_session)


@pytest_asyncio.fixture
async def category_repository(db_session: AsyncSession) -> CategoryRepository:
    """Fixture for CategoryRepository with test database session."""
    return CategoryRepository(db_session)


@pytest_asyncio.fixture
async def liability_repository(db_session: AsyncSession) -> LiabilityRepository:
    """Fixture for LiabilityRepository with test database session."""
    return LiabilityRepository(db_session)


@pytest_asyncio.fixture
async def payment_repository(db_session: AsyncSession) -> PaymentRepository:
    """Fixture for PaymentRepository with test database session."""
    return PaymentRepository(db_session)


@pytest_asyncio.fixture
async def statement_history_repository(
    db_session: AsyncSession,
) -> StatementHistoryRepository:
    """Fixture for StatementHistoryRepository with test database session."""
    return StatementHistoryRepository(db_session)


@pytest_asyncio.fixture
async def recurring_bill_repository(
    db_session: AsyncSession,
) -> RecurringBillRepository:
    """Fixture for RecurringBillRepository with test database session."""
    return RecurringBillRepository(db_session)


@pytest_asyncio.fixture
async def payment_schedule_repository(
    db_session: AsyncSession,
) -> PaymentScheduleRepository:
    """Fixture for PaymentScheduleRepository with test database session."""
    return PaymentScheduleRepository(db_session)


@pytest_asyncio.fixture
async def balance_reconciliation_repository(
    db_session: AsyncSession,
) -> BalanceReconciliationRepository:
    """Fixture for BalanceReconciliationRepository with test database session."""
    return BalanceReconciliationRepository(db_session)


@pytest_asyncio.fixture
async def bill_split_repository(db_session: AsyncSession) -> BillSplitRepository:
    """Fixture for BillSplitRepository with test database session."""
    return BillSplitRepository(db_session)


@pytest_asyncio.fixture
async def cashflow_forecast_repository(
    db_session: AsyncSession,
) -> CashflowForecastRepository:
    """Fixture for CashflowForecastRepository with test database session."""
    return CashflowForecastRepository(db_session)


@pytest_asyncio.fixture
async def credit_limit_history_repository(
    db_session: AsyncSession,
) -> CreditLimitHistoryRepository:
    """Fixture for CreditLimitHistoryRepository with test database session."""
    return CreditLimitHistoryRepository(db_session)


@pytest_asyncio.fixture
async def deposit_schedule_repository(
    db_session: AsyncSession,
) -> DepositScheduleRepository:
    """Fixture for DepositScheduleRepository with test database session."""
    return DepositScheduleRepository(db_session)


@pytest_asyncio.fixture
async def income_repository(db_session: AsyncSession) -> IncomeRepository:
    """Fixture for IncomeRepository with test database session."""
    return IncomeRepository(db_session)


@pytest_asyncio.fixture
async def income_category_repository(
    db_session: AsyncSession,
) -> IncomeCategoryRepository:
    """Fixture for IncomeCategoryRepository with test database session."""
    return IncomeCategoryRepository(db_session)


@pytest_asyncio.fixture
async def payment_source_repository(
    db_session: AsyncSession,
) -> PaymentSourceRepository:
    """Fixture for PaymentSourceRepository with test database session."""
    return PaymentSourceRepository(db_session)


@pytest_asyncio.fixture
async def recurring_income_repository(
    db_session: AsyncSession,
) -> RecurringIncomeRepository:
    """Fixture for RecurringIncomeRepository with test database session."""
    return RecurringIncomeRepository(db_session)


@pytest_asyncio.fixture
async def transaction_history_repository(
    db_session: AsyncSession,
) -> TransactionHistoryRepository:
    """Fixture for TransactionHistoryRepository with test database session."""
    return TransactionHistoryRepository(db_session)
