# Payment Source fixtures
@pytest_asyncio.fixture
async def test_payment_source(
    payment_source_repository: PaymentSourceRepository,
    test_payment: Payment,
    test_checking_account: Account,
) -> PaymentSource:
    """
    Create a test payment source.

    Note: This fixture creates a separate payment source, not directly
    associated with the test_payment fixture which already has its own source.
    """
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    source_schema = create_payment_source_schema(
        account_id=test_checking_account.id,
        amount=Decimal("75.00"),
        payment_id=test_payment.id,
    )

    # Convert validated schema to dict for repository
    validated_data = source_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_source_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_payment_with_multiple_sources(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_second_account: Account,
) -> Payment:
    """Create a test payment with multiple payment sources."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("150.00"),
        payment_date=utc_now(),
        category="Bill Payment",
        description="Test payment with multiple sources",
        sources=[
            create_payment_source_schema(
                account_id=test_checking_account.id, amount=Decimal("100.00")
            ),
            create_payment_source_schema(
                account_id=test_second_account.id, amount=Decimal("50.00")
            ),
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_repository.create(validated_data)from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import all models
from src.models import Account, StatementHistory
from src.models.balance_history import BalanceHistory
from src.models.balance_reconciliation import BalanceReconciliation
from src.models.bill_splits import BillSplit
from src.models.cashflow import CashflowForecast
from src.models.categories import Category
from src.models.credit_limit_history import CreditLimitHistory
from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.models.liabilities import Liability, LiabilityStatus
from src.models.payment_schedules import PaymentSchedule
from src.models.payments import Payment, PaymentSource
from src.models.recurring_bills import RecurringBill
from src.models.recurring_income import RecurringIncome
from src.models.transaction_history import TransactionHistory, TransactionType

# Import all repositories
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
from tests.helpers.datetime_utils import utc_now

# Import all schema factories
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.balance_history import create_balance_history_schema
from tests.helpers.schema_factories.balance_reconciliation import create_balance_reconciliation_schema
from tests.helpers.schema_factories.bill_splits import create_bill_split_schema
from tests.helpers.schema_factories.cashflow.base import create_cashflow_schema, create_cashflow_update_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.credit_limit_history import create_credit_limit_history_schema
from tests.helpers.schema_factories.deposit_schedules import create_deposit_schedule_schema
from tests.helpers.schema_factories.income import create_income_schema
from tests.helpers.schema_factories.income_categories import create_income_category_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema
from tests.helpers.schema_factories.payment_schedules import create_payment_schedule_schema
from tests.helpers.schema_factories.payment_sources import create_payment_source_schema
from tests.helpers.schema_factories.payments import create_payment_schema
from tests.helpers.schema_factories.recurring_bills import create_recurring_bill_schema
from tests.helpers.schema_factories.recurring_income import create_recurring_income_schema
from tests.helpers.schema_factories.statement_history import create_statement_history_schema
from tests.helpers.schema_factories.transaction_history import create_transaction_history_schema


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


# Test account fixtures
@pytest_asyncio.fixture
async def test_savings_account(account_repository: AccountRepository) -> Account:
    """Fixture to create a second test account for recurring income."""
    # Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Savings Account",
        account_type="savings",
        available_balance=Decimal("500.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # Create account through repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_second_account(account_repository: AccountRepository) -> Account:
    """Create a second test account for use in split payment tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Second Checking Account",
        account_type="checking",
        available_balance=Decimal("2000.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_accounts(
    account_repository: AccountRepository,
) -> List[Account]:
    """Create multiple test accounts of different types."""
    # 1. ARRANGE: No setup needed for this fixture

    # Create accounts of different types
    account_types = [
        ("Checking A", "checking", Decimal("1200.00")),
        ("Savings B", "savings", Decimal("5000.00")),
        ("Credit Card C", "credit", Decimal("-700.00")),
        (
            "Investment D",
            "savings",
            Decimal("10000.00"),
        ),  # Changed from "investment" to "savings"
    ]

    accounts = []
    for name, acc_type, balance in account_types:
        # 2. SCHEMA: Create and validate through Pydantic schema
        account_schema = create_account_schema(
            name=name,
            account_type=acc_type,
            available_balance=balance,
            total_limit=Decimal("3000.00") if acc_type == "credit" else None,
            available_credit=Decimal("2300.00") if acc_type == "credit" else None,
        )

        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        account = await account_repository.create(validated_data)
        accounts.append(account)

    return accounts


# Category fixtures
@pytest_asyncio.fixture
async def test_category(category_repository: CategoryRepository) -> Category:
    """Create a test category for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    category_schema = create_category_schema(
        name="Test Bill Category",
        description="Test category for bill tests",
    )

    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await category_repository.create(validated_data)


# Balance history fixtures
@pytest_asyncio.fixture
async def test_balance_history(
    balance_history_repository: BalanceHistoryRepository,
    test_checking_account: Account,
) -> BalanceHistory:
    """Create a test balance history record for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    timestamp = utc_now()
    balance_schema = create_balance_history_schema(
        account_id=test_checking_account.id,
        balance=Decimal("1000.00"),
        is_reconciled=False,
        notes="Initial balance",
        timestamp=timestamp,
    )

    # Convert validated schema to dict for repository
    validated_data = balance_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await balance_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_balances(
    balance_history_repository: BalanceHistoryRepository,
    test_checking_account: Account,
) -> List[BalanceHistory]:
    """Create multiple balance history records for use in tests."""
    # 1. ARRANGE: Setup balance configurations
    now = utc_now()
    balance_configs = [
        (now - timedelta(days=20), Decimal("1000.00"), False, "Initial balance"),
        (now - timedelta(days=10), Decimal("1500.00"), True, "After paycheck deposit"),
        (now, Decimal("2000.00"), False, "Current balance"),
    ]

    balances = []
    for timestamp, amount, reconciled, note in balance_configs:
        # 2. SCHEMA: Create and validate through Pydantic schema
        balance_schema = create_balance_history_schema(
            account_id=test_checking_account.id,
            balance=amount,
            is_reconciled=reconciled,
            notes=note,
            timestamp=timestamp,
        )

        # Convert validated schema to dict for repository
        validated_data = balance_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        balance = await balance_history_repository.create(validated_data)
        balances.append(balance)

    return balances


# Liability fixtures
@pytest_asyncio.fixture
async def test_liability(
    liability_repository: LiabilityRepository,
    test_checking_account: Account,
    test_category: Category,
) -> Liability:
    """Create a test liability for use in tests."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    due_date = utc_now() + timedelta(days=30)
    liability_schema = create_liability_schema(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=due_date,
        category_id=test_category.id,
        primary_account_id=test_checking_account.id,
        status=LiabilityStatus.PENDING,
    )

    # Convert validated schema to dict for repository
    validated_data = liability_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await liability_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_liabilities(
    liability_repository: LiabilityRepository,
    test_checking_account: Account,
    test_category: Category,
) -> List[Liability]:
    """Create multiple test liabilities with different due dates."""
    # 1. ARRANGE: Setup dates for different liabilities
    now = utc_now()
    due_dates = [
        now + timedelta(days=5),  # Soon due
        now + timedelta(days=15),  # Medium term
        now + timedelta(days=30),  # Long term
        now - timedelta(days=5),  # Overdue
    ]

    liabilities = []
    for i, due_date in enumerate(due_dates):
        # 2. SCHEMA: Create and validate through Pydantic schema
        liability_schema = create_liability_schema(
            name=f"Test Bill {i+1}",
            amount=Decimal(f"{(i+1) * 50}.00"),
            due_date=due_date,
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            paid=(i == 2),  # Make one of them paid
            recurring=(i % 2 == 0),  # Make some recurring
        )

        # Convert validated schema to dict for repository
        validated_data = liability_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        liability = await liability_repository.create(validated_data)
        liabilities.append(liability)

    return liabilities


# Payment fixtures
@pytest_asyncio.fixture
async def test_payment(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_liability: Liability,
) -> Payment:
    """Create a test payment for use in tests."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("50.00"),
        payment_date=utc_now(),
        category="Utilities",
        description="Test payment for utilities",
        liability_id=test_liability.id,
        sources=[
            {
                "account_id": test_checking_account.id,
                "amount": Decimal("50.00"),
            }
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_payments(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_second_account: Account,
    test_liability: Liability,
) -> List[Payment]:
    """Create multiple test payments with different dates and categories."""
    # 1. ARRANGE: Setup payment dates and categories
    now = utc_now()
    payment_data = [
        # Recent utility payment
        {
            "amount": Decimal("75.00"),
            "payment_date": now - timedelta(days=5),
            "category": "Utilities",
            "liability_id": test_liability.id,
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("75.00")}
            ],
        },
        # Older rent payment
        {
            "amount": Decimal("800.00"),
            "payment_date": now - timedelta(days=25),
            "category": "Rent",
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("800.00")}
            ],
        },
        # Split payment for insurance
        {
            "amount": Decimal("120.00"),
            "payment_date": now - timedelta(days=10),
            "category": "Insurance",
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("60.00")},
                {"account_id": test_second_account.id, "amount": Decimal("60.00")},
            ],
        },
        # Future payment (scheduled)
        {
            "amount": Decimal("45.00"),
            "payment_date": now + timedelta(days=5),
            "category": "Subscription",
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("45.00")}
            ],
        },
    ]

    payments = []
    for data in payment_data:
        # 2. SCHEMA: Create and validate through Pydantic schema
        payment_schema = create_payment_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = payment_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        payment = await payment_repository.create(validated_data)
        payments.append(payment)

    return payments


# Balance Reconciliation fixtures
@pytest_asyncio.fixture
async def test_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
) -> BalanceReconciliation:
    """Create a test balance reconciliation entry for use in tests."""
    # Create and validate through Pydantic schema
    reconciliation_schema = create_balance_reconciliation_schema(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1025.50"),
        reason="Initial reconciliation after transaction verification",
    )

    # Convert validated schema to dict for repository
    validated_data = reconciliation_schema.model_dump()

    # Create reconciliation entry through repository
    return await balance_reconciliation_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_reconciliations(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
) -> List[BalanceReconciliation]:
    """Create multiple balance reconciliation entries for testing."""
    now = utc_now()

    # Create multiple reconciliation entries with different dates
    entries = []

    for i, days_ago in enumerate([90, 60, 30, 15, 5]):
        schema = create_balance_reconciliation_schema(
            account_id=test_checking_account.id,
            previous_balance=Decimal(f"{1000 + (i * 50)}.00"),
            new_balance=Decimal(f"{1000 + ((i + 1) * 50)}.00"),
            reason=f"Reconciliation #{i + 1}",
            reconciliation_date=now - timedelta(days=days_ago),
        )

        entry = await balance_reconciliation_repository.create(schema.model_dump())
        entries.append(entry)

    return entries


# Bill Split fixtures
@pytest_asyncio.fixture
async def test_bill_splits(
    bill_split_repository: BillSplitRepository,
    test_liability: Liability,
    test_checking_account: Account,
) -> List[BillSplit]:
    """Create test bill splits using schema validation."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    split_schemas = [
        create_bill_split_schema(
            liability_id=test_liability.id,
            account_id=test_checking_account.id,
            amount=Decimal("100.00"),
        ),
        create_bill_split_schema(
            liability_id=test_liability.id,
            account_id=test_checking_account.id,
            amount=Decimal("100.00"),
        ),
        create_bill_split_schema(
            liability_id=test_liability.id,
            account_id=test_checking_account.id,
            amount=Decimal("100.00"),
        ),
    ]

    # Convert validated schemas to dicts for repository
    splits_data = [schema.model_dump() for schema in split_schemas]

    # 3. ACT: Pass validated data to repository
    splits = []
    for split_data in splits_data:
        split = await bill_split_repository.create(split_data)
        splits.append(split)

    return splits


# Cashflow Forecast fixtures
@pytest_asyncio.fixture
async def test_cashflow_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
) -> CashflowForecast:
    """Fixture to create a test cashflow forecast."""
    # Create and validate through Pydantic schema
    forecast_schema = create_cashflow_schema(
        forecast_date=datetime.now(timezone.utc),
        total_bills=Decimal("1000.00"),
        total_income=Decimal("1500.00"),
        balance=Decimal("2000.00"),
        forecast=Decimal("2500.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("25.00"),
        yearly_deficit=Decimal("9125.00"),
        required_income=Decimal("12000.00"),
        hourly_rate_40=Decimal("20.00"),
        hourly_rate_30=Decimal("26.67"),
        hourly_rate_20=Decimal("40.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = forecast_schema.model_dump()

    # Create forecast through repository
    return await cashflow_forecast_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_forecasts(
    cashflow_forecast_repository: CashflowForecastRepository,
) -> List[CashflowForecast]:
    """Fixture to create multiple cashflow forecasts for testing."""
    now = datetime.now(timezone.utc)

    # Create multiple forecasts with various dates
    forecast_data = [
        {
            "forecast_date": now - timedelta(days=10),
            "total_bills": Decimal("900.00"),
            "total_income": Decimal("1300.00"),
            "balance": Decimal("1800.00"),
            "forecast": Decimal("2200.00"),
            "min_14_day": Decimal("450.00"),
            "min_30_day": Decimal("900.00"),
            "min_60_day": Decimal("1800.00"),
            "min_90_day": Decimal("2700.00"),
            "daily_deficit": Decimal("20.00"),
            "yearly_deficit": Decimal("7300.00"),
            "required_income": Decimal("10000.00"),
            "hourly_rate_40": Decimal("17.00"),
            "hourly_rate_30": Decimal("22.67"),
            "hourly_rate_20": Decimal("34.00"),
        },
        {
            "forecast_date": now - timedelta(days=7),
            "total_bills": Decimal("950.00"),
            "total_income": Decimal("1400.00"),
            "balance": Decimal("1900.00"),
            "forecast": Decimal("2350.00"),
            "min_14_day": Decimal("475.00"),
            "min_30_day": Decimal("950.00"),
            "min_60_day": Decimal("1900.00"),
            "min_90_day": Decimal("2850.00"),
            "daily_deficit": Decimal("22.00"),
            "yearly_deficit": Decimal("8030.00"),
            "required_income": Decimal("11000.00"),
            "hourly_rate_40": Decimal("18.50"),
            "hourly_rate_30": Decimal("24.67"),
            "hourly_rate_20": Decimal("37.00"),
        },
        {
            "forecast_date": now - timedelta(days=3),
            "total_bills": Decimal("1000.00"),
            "total_income": Decimal("1500.00"),
            "balance": Decimal("2000.00"),
            "forecast": Decimal("2500.00"),
            "min_14_day": Decimal("500.00"),
            "min_30_day": Decimal("1000.00"),
            "min_60_day": Decimal("2000.00"),
            "min_90_day": Decimal("3000.00"),
            "daily_deficit": Decimal("25.00"),
            "yearly_deficit": Decimal("9125.00"),
            "required_income": Decimal("12000.00"),
            "hourly_rate_40": Decimal("20.00"),
            "hourly_rate_30": Decimal("26.67"),
            "hourly_rate_20": Decimal("40.00"),
        },
        {
            "forecast_date": now,
            "total_bills": Decimal("1050.00"),
            "total_income": Decimal("1550.00"),
            "balance": Decimal("2100.00"),
            "forecast": Decimal("2600.00"),
            "min_14_day": Decimal("525.00"),
            "min_30_day": Decimal("1050.00"),
            "min_60_day": Decimal("2100.00"),
            "min_90_day": Decimal("3150.00"),
            "daily_deficit": Decimal("27.00"),
            "yearly_deficit": Decimal("9855.00"),
            "required_income": Decimal("13000.00"),
            "hourly_rate_40": Decimal("21.50"),
            "hourly_rate_30": Decimal("28.67"),
            "hourly_rate_20": Decimal("43.00"),
        },
    ]

    # Create the forecasts using the repository
    created_forecasts = []
    for data in forecast_data:
        # Create and validate through Pydantic schema
        forecast_schema = create_cashflow_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = forecast_schema.model_dump()

        # Create forecast through repository
        forecast = await cashflow_forecast_repository.create(validated_data)
        created_forecasts.append(forecast)

    return created_forecasts


# Income fixtures
@pytest_asyncio.fixture
async def test_income(
    income_repository: IncomeRepository,
    test_checking_account: Account,
) -> Income:
    """Fixture to create a test income entry."""
    # Create and validate through Pydantic schema
    income_schema = create_income_schema(
        source="Monthly Salary",
        amount=Decimal("3000.00"),
        account_id=test_checking_account.id,
        date=datetime.now(timezone.utc),
        deposited=False,
    )

    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()

    # Create income through repository
    return await income_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_additional_income(
    income_repository: IncomeRepository,
    test_second_account: Account,
) -> Income:
    """Fixture to create a second test income entry."""
    # Create and validate through Pydantic schema
    income_schema = create_income_schema(
        source="Freelance Payment",
        amount=Decimal("1500.00"),
        account_id=test_second_account.id,
        date=datetime.now(timezone.utc),
        deposited=False,
    )

    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()

    # Create income through repository
    return await income_repository.create(validated_data)


# Deposit Schedule fixtures
@pytest_asyncio.fixture
async def test_deposit_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_income: Income,
    test_checking_account: Account,
) -> DepositSchedule:
    """Fixture to create a test deposit schedule."""
    # Create and validate through Pydantic schema
    schedule_schema = create_deposit_schedule_schema(
        income_id=test_income.id,
        account_id=test_checking_account.id,
        schedule_date=datetime.now(timezone.utc) + timedelta(days=7),
        amount=Decimal("3000.00"),
        recurring=False,
        status="pending",
    )

    # Convert validated schema to dict for repository
    validated_data = schedule_schema.model_dump()

    # Create deposit schedule through repository
    return await deposit_schedule_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_income: Income,
    test_additional_income: Income,
    test_checking_account: Account,
    test_second_account: Account,
) -> List[DepositSchedule]:
    """Fixture to create multiple deposit schedules for testing."""
    now = datetime.now(timezone.utc)

    # Create multiple deposit schedules with various attributes
    schedule_data = [
        {
            "income_id": test_income.id,
            "account_id": test_checking_account.id,
            "schedule_date": now + timedelta(days=3),
            "amount": Decimal("3000.00"),
            "recurring": False,
            "status": "pending",
        },
        {
            "income_id": test_additional_income.id,
            "account_id": test_second_account.id,
            "schedule_date": now + timedelta(days=14),
            "amount": Decimal("1500.00"),
            "recurring": True,
            "recurrence_pattern": {"frequency": "monthly", "day": 15},
            "status": "pending",
        },
        {
            "income_id": test_income.id,
            "account_id": test_checking_account.id,
            "schedule_date": now - timedelta(days=5),  # Past date
            "amount": Decimal("1000.00"),
            "recurring": False,
            "status": "pending",  # Overdue
        },
        {
            "income_id": test_additional_income.id,
            "account_id": test_second_account.id,
            "schedule_date": now - timedelta(days=10),  # Past date
            "amount": Decimal("500.00"),
            "recurring": False,
            "status": "processed",  # Already processed
        },
    ]

    # Create the deposit schedules using the repository
    created_schedules = []
    for data in schedule_data:
        # Create and validate through Pydantic schema
        schedule_schema = create_deposit_schedule_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = schedule_schema.model_dump()

        # Create deposit schedule through repository
        schedule = await deposit_schedule_repository.create(validated_data)
        created_schedules.append(schedule)

    return created_schedules


# Credit Limit History fixtures
@pytest_asyncio.fixture
async def test_credit_limit_history(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_account: Account,
) -> CreditLimitHistory:
    """Create a test credit limit history entry for use in tests."""
    # Create and validate through Pydantic schema
    credit_limit_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        old_limit=Decimal("2000.00"),
        new_limit=Decimal("3000.00"),
        reason="Credit limit increase",
    )

    # Convert validated schema to dict for repository
    validated_data = credit_limit_schema.model_dump()

    # Create credit limit history entry through repository
    return await credit_limit_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_credit_limit_changes(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_account: Account,
) -> List[CreditLimitHistory]:
    """Create multiple credit limit history entries for testing."""
    now = datetime.now(timezone.utc)

    # Create base entry (already created in test_credit_limit_history)
    base_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("5000.00"),
        effective_date=now - timedelta(days=90),
        reason="Initial credit limit",
    )
    await credit_limit_history_repository.create(base_schema.model_dump())

    # Create increase entry
    increase_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("7500.00"),
        effective_date=now - timedelta(days=60),
        reason="Credit increase due to good payment history",
    )
    increase = await credit_limit_history_repository.create(
        increase_schema.model_dump()
    )

    # Create decrease entry
    decrease_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("6500.00"),
        effective_date=now - timedelta(days=30),
        reason="Credit adjustment due to risk assessment",
    )
    decrease = await credit_limit_history_repository.create(
        decrease_schema.model_dump()
    )

    # Create recent increase entry
    latest_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("8000.00"),
        effective_date=now - timedelta(days=5),
        reason="Credit increase request approved",
    )
    latest = await credit_limit_history_repository.create(latest_schema.model_dump())

    return [increase, decrease, latest]


# Income Category fixtures
@pytest_asyncio.fixture
async def test_income_category(
    income_category_repository: IncomeCategoryRepository,
) -> IncomeCategory:
    """Create a test income category for use in tests."""
    # Create and validate through Pydantic schema
    category_schema = create_income_category_schema(
        name="Test Income Category",
        description="Test category for income",
    )

    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()

    # Create category through repository
    return await income_category_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_categories(
    income_category_repository: IncomeCategoryRepository,
) -> List[IncomeCategory]:
    """Fixture to create multiple income categories for testing."""
    # Create multiple income categories with various attributes
    category_data = [
        {
            "name": "Salary",
            "description": "Regular employment income",
        },
        {
            "name": "Freelance",
            "description": "Income from freelance work",
        },
        {
            "name": "Investments",
            "description": "Income from investments",
        },
        {
            "name": "Rental Income",
            "description": "Income from rental properties",
        },
    ]

    # Create the categories using the repository
    created_categories = []
    for data in category_data:
        # Create and validate through Pydantic schema
        category_schema = create_income_category_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = category_schema.model_dump()

        # Create category through repository
        category = await income_category_repository.create(validated_data)
        created_categories.append(category)

    return created_categories


@pytest_asyncio.fixture
async def test_income_entries(
    income_repository: IncomeRepository,
    test_multiple_categories: List[IncomeCategory],
) -> List[Income]:
    """Fixture to create test income entries associated with categories."""
    # Get category IDs for reference
    salary_category_id = test_multiple_categories[0].id
    freelance_category_id = test_multiple_categories[1].id
    investments_category_id = test_multiple_categories[2].id

    # Create income data with various attributes
    income_data = [
        {
            "source": "Monthly Salary",
            "amount": Decimal("3000.00"),
            "account_id": 1,  # Using a default account ID
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Bonus",
            "amount": Decimal("1000.00"),
            "account_id": 1,
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Website Project",
            "amount": Decimal("800.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": False,
        },
        {
            "source": "Logo Design",
            "amount": Decimal("350.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": True,
        },
        {
            "source": "Stock Dividends",
            "amount": Decimal("420.00"),
            "account_id": 1,
            "category_id": investments_category_id,
            "deposited": False,
        },
    ]

    # Create the income entries using the repository
    created_incomes = []
    for data in income_data:
        # Create and validate through Pydantic schema
        income_schema = create_income_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = income_schema.model_dump()

        # Create income through repository
        income = await income_repository.create(validated_data)
        created_incomes.append(income)

    return created_incomes


# Transaction History fixtures
@pytest_asyncio.fixture
async def test_transaction_history(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
) -> TransactionHistory:
    """Create a test transaction for use in tests."""
    # Create and validate through Pydantic schema
    transaction_schema = create_transaction_history_schema(
        account_id=test_checking_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        description="Initial deposit",
    )

    # Convert validated schema to dict for repository
    validated_data = transaction_schema.model_dump()

    # Create transaction through repository
    return await transaction_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_transactions(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_credit_account: Account,
) -> List[TransactionHistory]:
    """Create multiple test transactions for use in tests."""
    now = utc_now()
    
    # Transaction configs for different scenarios
    transaction_configs = [
        # Recent debit transaction on checking account
        {
            "account_id": test_checking_account.id,
            "amount": Decimal("45.67"),
            "description": "Grocery store purchase",
            "transaction_date": now - timedelta(days=2),
            "transaction_type": TransactionType.DEBIT,
            "balance_after": Decimal("954.33"),
            "category": "Groceries",
        },
        # Credit transaction on checking account
        {
            "account_id": test_checking_account.id,
            "amount": Decimal("1200.00"),
            "description": "Salary deposit",
            "transaction_date": now - timedelta(days=7),
            "transaction_type": TransactionType.CREDIT,
            "balance_after": Decimal("2154.33"),
            "category": "Income",
        },
        # Old debit transaction on checking account
        {
            "account_id": test_checking_account.id,
            "amount": Decimal("85.23"),
            "description": "Utilities payment",
            "transaction_date": now - timedelta(days=14),
            "transaction_type": TransactionType.DEBIT,
            "balance_after": Decimal("869.10"),
            "category": "Utilities",
        },
        # Credit card payment transaction
        {
            "account_id": test_credit_account.id,
            "amount": Decimal("250.00"),
            "description": "Online purchase",
            "transaction_date": now - timedelta(days=3),
            "transaction_type": TransactionType.DEBIT,
            "balance_after": Decimal("-750.00"),
            "category": "Shopping",
        },
    ]
    
    transactions = []
    for config in transaction_configs:
        # Create and validate through Pydantic schema
        transaction_schema = create_transaction_history_schema(**config)

        # Convert validated schema to dict for repository
        validated_data = transaction_schema.model_dump()

        # Create transaction through repository
        transaction = await transaction_history_repository.create(validated_data)
        transactions.append(transaction)
    
    return transactions


# Recurring Income fixtures
@pytest_asyncio.fixture
async def test_recurring_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_checking_account: Account,
    test_income_category: IncomeCategory,
) -> RecurringIncome:
    """Create a test recurring income entry for use in tests."""
    # Create and validate through Pydantic schema
    income_schema = create_recurring_income_schema(
        source="Monthly Salary",
        amount=Decimal("3000.00"),
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        day_of_month=15,
        active=True,
    )

    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()

    # Create recurring income through repository
    return await recurring_income_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_recurring_incomes(
    recurring_income_repository: RecurringIncomeRepository,
    test_checking_account: Account,
    test_second_account: Account,
    test_income_category: IncomeCategory,
) -> List[RecurringIncome]:
    """Create multiple recurring income entries for testing."""
    # Different recurring income configurations
    income_configs = [
        {
            "source": "Primary Job Salary",
            "amount": Decimal("4000.00"),
            "account_id": test_checking_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 1,
            "active": True,
        },
        {
            "source": "Part-time Job",
            "amount": Decimal("1200.00"),
            "account_id": test_second_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 15,
            "active": True,
        },
        {
            "source": "Rental Income",
            "amount": Decimal("800.00"),
            "account_id": test_checking_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 5,
            "active": True,
        },
        {
            "source": "Previous Freelance Contract",
            "amount": Decimal("1500.00"),
            "account_id": test_second_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 20,
            "active": False,  # Inactive income
        },
    ]
    
    incomes = []
    for config in income_configs:
        # Create and validate through Pydantic schema
        income_schema = create_recurring_income_schema(**config)

        # Convert validated schema to dict for repository
        validated_data = income_schema.model_dump()

        # Create recurring income through repository
        income = await recurring_income_repository.create(validated_data)
        incomes.append(income)
    
    return incomes


# Statement history fixtures
@pytest_asyncio.fixture
async def test_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
) -> StatementHistory:
    """Create a test statement history entry for a credit account."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    statement_schema = create_statement_history_schema(
        account_id=test_credit_account.id,
        statement_date=utc_now() - timedelta(days=15),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=utc_now() + timedelta(days=15),
    )

    # Convert validated schema to dict for repository
    validated_data = statement_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await statement_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_statements(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
) -> List[StatementHistory]:
    """Create multiple statement history records for use in tests."""
    # 1. ARRANGE: Setup statement configurations
    now = utc_now()
    statement_configs = [
        (
            now - timedelta(days=60),
            Decimal("400.00"),
            Decimal("20.00"),
            now - timedelta(days=39),
        ),
        (
            now - timedelta(days=30),
            Decimal("600.00"),
            Decimal("30.00"),
            now - timedelta(days=9),
        ),
        (now, Decimal("800.00"), Decimal("40.00"), now + timedelta(days=21)),
    ]

    statements = []
    for stmt_date, balance, min_payment, due_date in statement_configs:
        # 2. SCHEMA: Create and validate through Pydantic schema
        statement_schema = create_statement_history_schema(
            account_id=test_credit_account.id,
            statement_date=stmt_date,
            statement_balance=balance,
            minimum_payment=min_payment,
            due_date=due_date,
        )

        # Convert validated schema to dict for repository
        validated_data = statement_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        statement = await statement_history_repository.create(validated_data)
        statements.append(statement)

    return statements


@pytest_asyncio.fixture
async def test_multiple_accounts_with_statements(
    account_repository: AccountRepository,
    statement_history_repository: StatementHistoryRepository,
) -> Tuple[List[Account], List[StatementHistory]]:
    """Create multiple accounts with statements for testing."""
    # 1. ARRANGE: Setup account configurations
    accounts = []
    statements = []
    now = utc_now()

    # Create two credit accounts
    for i in range(2):
        # 2. SCHEMA: Create and validate account through Pydantic schema
        account_schema = create_account_schema(
            name=f"Credit Account {i+1}",
            account_type="credit",
            available_balance=Decimal(f"-{(i+5)*100}.00"),
            total_limit=Decimal(f"{(i+1)*1000}.00"),
            available_credit=Decimal(f"{(i+1)*1000 - (i+5)*100}.00"),
        )

        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        account = await account_repository.create(validated_data)
        accounts.append(account)

        # Create statements for each account
        for j in range(3):
            days_offset = (3 - j) * 30  # 90, 60, 30 days ago
            # Create statement schema
            statement_schema = create_statement_history_schema(
                account_id=account.id,
                statement_date=now - timedelta(days=days_offset),
                statement_balance=Decimal(f"{(i+j+1)*200}.00"),
                minimum_payment=Decimal(f"{(i+j+1)*10}.00"),
                due_date=now
                - timedelta(days=days_offset - 21),  # Due 21 days after statement
            )

            # Convert validated schema to dict for repository
            validated_data = statement_schema.model_dump()

            # Pass validated data to repository
            statement = await statement_history_repository.create(validated_data)
            statements.append(statement)

    return accounts, statements


# Recurring Bill fixtures
@pytest_asyncio.fixture
async def test_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_checking_account: Account,
    test_category: Category,
) -> RecurringBill:
    """Create a test recurring bill for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    bill_schema = create_recurring_bill_schema(
        bill_name="Test Recurring Bill",
        amount=Decimal("50.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_category.id,
        auto_pay=True,
    )

    # Convert validated schema to dict for repository
    validated_data = bill_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await recurring_bill_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_recurring_bills(
    recurring_bill_repository: RecurringBillRepository,
    test_checking_account: Account,
    test_category: Category,
) -> List[RecurringBill]:
    """Create multiple recurring bills for testing."""
    # 1. ARRANGE: Setup bill configurations
    bills_config = [
        ("Active Bill 1", 1, True, True),
        ("Active Bill 2", 15, True, True),
        ("Inactive Bill", 20, False, True),
        ("Day 10 Bill 1", 10, True, False),
        ("Day 10 Bill 2", 10, True, False),
        ("Day 15 Bill", 15, True, False),
    ]

    bills = []
    for name, day, active, auto_pay in bills_config:
        # 2. SCHEMA: Create and validate through Pydantic schema
        bill_schema = create_recurring_bill_schema(
            bill_name=name,
            amount=Decimal("100.00"),
            day_of_month=day,
            account_id=test_checking_account.id,
            category_id=test_category.id,
            auto_pay=auto_pay,
        )

        # Convert validated schema to dict for repository
        validated_data = bill_schema.model_dump()

        # Add active status which isn't in the create schema
        if not active:
            # 3. ACT: Create bill and then update to set active=False
            bill = await recurring_bill_repository.create(validated_data)
            await recurring_bill_repository.update(bill.id, {"active": False})
            # Fetch again to get updated version
            bill = await recurring_bill_repository.get(bill.id)
        else:
            # 3. ACT: Create bill (active by default)
            bill = await recurring_bill_repository.create(validated_data)

        bills.append(bill)

    return bills


# Payment Schedule fixtures
@pytest_asyncio.fixture
async def test_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_liability: Liability,
    test_checking_account: Account,
) -> PaymentSchedule:
    """Fixture to create a test payment schedule."""
    # Create and validate through Pydantic schema
    schedule_schema = create_payment_schedule_schema(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=Decimal("200.00"),
        scheduled_date=utc_now() + timedelta(days=7),
        description="Test payment schedule",
    )

    # Convert validated schema to dict for repository
    validated_data = schedule_schema.model_dump()

    # Create payment schedule through repository
    return await payment_schedule_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_liability: Liability,
    test_checking_account: Account,
    test_second_account: Account,
) -> List[PaymentSchedule]:
    """Fixture to create multiple payment schedules for testing."""
    now = utc_now()

    # Create multiple payment schedules with various attributes
    schedule_data = [
        {
            "liability_id": test_liability.id,
            "account_id": test_checking_account.id,
            "amount": Decimal("100.00"),
            "scheduled_date": now + timedelta(days=3),
            "description": "Upcoming payment",
            "auto_process": True,
        },
        {
            "liability_id": test_liability.id,
            "account_id": test_checking_account.id,
            "amount": Decimal("150.00"),
            "scheduled_date": now + timedelta(days=14),
            "description": "Future payment",
            "auto_process": False,
        },
        {
            "liability_id": test_liability.id,
            "account_id": test_second_account.id,
            "amount": Decimal("50.00"),
            "scheduled_date": now + timedelta(days=30),
            "description": "End of month payment",
            "auto_process": True,
        },
        {
            "liability_id": test_liability.id,
            "account_id": test_checking_account.id,
            "amount": Decimal("75.00"),
            "scheduled_date": now - timedelta(days=5),  # Past date
            "description": "Overdue payment",
            "auto_process": False,
        },
    ]

    # Create the payment schedules using the repository
    created_schedules = []
    for data in schedule_data:
        # Create and validate through Pydantic schema
        schedule_schema = create_payment_schedule_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = schedule_schema.model_dump()

        # Create payment schedule through repository
        schedule = await payment_schedule_repository.create(validated_data)
        created_schedules.append(schedule)

    return created_schedules

# Credit Limit History fixtures
@pytest_asyncio.fixture
async def test_credit_limit_changes(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_account: Account,
) -> List[CreditLimitHistory]:
    """Create multiple credit limit history entries for testing."""
    now = datetime.now(timezone.utc)

    # Create base entry (already created in test_credit_limit_history)
    base_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("5000.00"),
        effective_date=now - timedelta(days=90),
        reason="Initial credit limit",
    )
    await credit_limit_history_repository.create(base_schema.model_dump())

    # Create increase entry
    increase_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("7500.00"),
        effective_date=now - timedelta(days=60),
        reason="Credit increase due to good payment history",
    )
    increase = await credit_limit_history_repository.create(
        increase_schema.model_dump()
    )

    # Create decrease entry
    decrease_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("6500.00"),
        effective_date=now - timedelta(days=30),
        reason="Credit adjustment due to risk assessment",
    )
    decrease = await credit_limit_history_repository.create(
        decrease_schema.model_dump()
    )

    # Create recent increase entry
    latest_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("8000.00"),
        effective_date=now - timedelta(days=5),
        reason="Credit increase request approved",
    )
    latest = await credit_limit_history_repository.create(latest_schema.model_dump())

    return [increase, decrease, latest]


# Income Category fixtures
@pytest_asyncio.fixture
async def test_multiple_categories(
    income_category_repository: IncomeCategoryRepository,
) -> List[IncomeCategory]:
    """Fixture to create multiple income categories for testing."""
    # Create multiple income categories with various attributes
    category_data = [
        {
            "name": "Salary",
            "description": "Regular employment income",
        },
        {
            "name": "Freelance",
            "description": "Income from freelance work",
        },
        {
            "name": "Investments",
            "description": "Income from investments",
        },
        {
            "name": "Rental Income",
            "description": "Income from rental properties",
        },
    ]

    # Create the categories using the repository
    created_categories = []
    for data in category_data:
        # Create and validate through Pydantic schema
        category_schema = create_income_category_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = category_schema.model_dump()

        # Create category through repository
        category = await income_category_repository.create(validated_data)
        created_categories.append(category)

    return created_categories


@pytest_asyncio.fixture
async def test_income_entries(
    income_repository: IncomeRepository,
    test_multiple_categories: List[IncomeCategory],
) -> List[Income]:
    """Fixture to create test income entries associated with categories."""
    # Get category IDs for reference
    salary_category_id = test_multiple_categories[0].id
    freelance_category_id = test_multiple_categories[1].id
    investments_category_id = test_multiple_categories[2].id

    # Create income data with various attributes
    income_data = [
        {
            "source": "Monthly Salary",
            "amount": Decimal("3000.00"),
            "account_id": 1,  # Using a default account ID
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Bonus",
            "amount": Decimal("1000.00"),
            "account_id": 1,
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Website Project",
            "amount": Decimal("800.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": False,
        },
        {
            "source": "Logo Design",
            "amount": Decimal("350.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": True,
        },
        {
            "source": "Stock Dividends",
            "amount": Decimal("420.00"),
            "account_id": 1,
            "category_id": investments_category_id,
            "deposited": False,
        },
    ]

    # Create the income entries using the repository
    created_incomes = []
    for data in income_data:
        # Create and validate through Pydantic schema
        income_schema = create_income_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = income_schema.model_dump()

        # Create income through repository
        income = await income_repository.create(validated_data)
        created_incomes.append(income)

    return created_incomes


# Payment Source fixtures
@pytest_asyncio.fixture
async def test_payment_source(
    payment_source_repository: PaymentSourceRepository,
    test_payment: Payment,
    test_checking_account: Account,
) -> PaymentSource:
    """
    Create a test payment source.

    Note: This fixture creates a separate payment source, not directly
    associated with the test_payment fixture which already has its own source.
    """
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    source_schema = create_payment_source_schema(
        account_id=test_checking_account.id,
        amount=Decimal("75.00"),
        payment_id=test_payment.id,
    )

    # Convert validated schema to dict for repository
    validated_data = source_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_source_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_payment_with_multiple_sources(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_second_account: Account,
) -> Payment:
    """Create a test payment with multiple payment sources."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("150.00"),
        payment_date=utc_now(),
        category="Bill Payment",
        description="Test payment with multiple sources",
        sources=[
            create_payment_source_schema(
                account_id=test_checking_account.id, amount=Decimal("100.00")
            ),
            create_payment_source_schema(
                account_id=test_second_account.id, amount=Decimal("50.00")
            ),
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_repository.create(validated_data)


# Statement History fixtures
@pytest_asyncio.fixture
async def test_multiple_statements(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
) -> List[StatementHistory]:
    """Create multiple statement history records for use in tests."""
    # 1. ARRANGE: Setup statement configurations
    now = utc_now()
    statement_configs = [
        (
            now - timedelta(days=60),
            Decimal("400.00"),
            Decimal("20.00"),
            now - timedelta(days=39),
        ),
        (
            now - timedelta(days=30),
            Decimal("600.00"),
            Decimal("30.00"),
            now - timedelta(days=9),
        ),
        (now, Decimal("800.00"), Decimal("40.00"), now + timedelta(days=21)),
    ]

    statements = []
    for stmt_date, balance, min_payment, due_date in statement_configs:
        # 2. SCHEMA: Create and validate through Pydantic schema
        statement_schema = create_statement_history_schema(
            account_id=test_credit_account.id,
            statement_date=stmt_date,
            statement_balance=balance,
            minimum_payment=min_payment,
            due_date=due_date,
        )

        # Convert validated schema to dict for repository
        validated_data = statement_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        statement = await statement_history_repository.create(validated_data)
        statements.append(statement)

    return statements


@pytest_asyncio.fixture
async def test_multiple_accounts_with_statements(
    account_repository: AccountRepository,
    statement_history_repository: StatementHistoryRepository,
) -> Tuple[List[Account], List[StatementHistory]]:
    """Create multiple accounts with statements for testing."""
    # 1. ARRANGE: Setup account configurations
    accounts = []
    statements = []
    now = utc_now()

    # Create two credit accounts
    for i in range(2):
        # 2. SCHEMA: Create and validate account through Pydantic schema
        account_schema = create_account_schema(
            name=f"Credit Account {i+1}",
            account_type="credit",
            available_balance=Decimal(f"-{(i+5)*100}.00"),
            total_limit=Decimal(f"{(i+1)*1000}.00"),
            available_credit=Decimal(f"{(i+1)*1000 - (i+5)*100}.00"),
        )

        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        account = await account_repository.create(validated_data)
        accounts.append(account)

        # Create statements for each account
        for j in range(3):
            days_offset = (3 - j) * 30  # 90, 60, 30 days ago
            # Create statement schema
            statement_schema = create_statement_history_schema(
                account_id=account.id,
                statement_date=now - timedelta(days=days_offset),
                statement_balance=Decimal(f"{(i+j+1)*200}.00"),
                minimum_payment=Decimal(f"{(i+j+1)*10}.00"),
                due_date=now
                - timedelta(days=days_offset - 21),  # Due 21 days after statement
            )

            # Convert validated schema to dict for repository
            validated_data = statement_schema.model_dump()

            # Pass validated data to repository
            statement = await statement_history_repository.create(validated_data)
            statements.append(statement)

    return accounts, statements