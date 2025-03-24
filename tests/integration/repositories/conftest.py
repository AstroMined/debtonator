from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Account, StatementHistory
from src.models.balance_history import BalanceHistory
from src.models.categories import Category
from src.models.liabilities import Liability, LiabilityStatus
from src.models.payment_schedules import PaymentSchedule
from src.models.payments import Payment, PaymentSource
from src.models.recurring_bills import RecurringBill
from src.repositories.accounts import AccountRepository
from src.repositories.balance_history import BalanceHistoryRepository
from src.repositories.categories import CategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payment_schedules import PaymentScheduleRepository
from src.repositories.payments import PaymentRepository
from src.repositories.recurring_bills import RecurringBillRepository
from src.repositories.statement_history import StatementHistoryRepository
from tests.helpers.datetime_utils import utc_now
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.balance_history import create_balance_history_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema
from tests.helpers.schema_factories.payment_schedules import (
    create_payment_schedule_schema,
)
from tests.helpers.schema_factories.payment_sources import create_payment_source_schema
from tests.helpers.schema_factories.payments import create_payment_schema
from tests.helpers.schema_factories.recurring_bills import create_recurring_bill_schema
from tests.helpers.schema_factories.statement_history import (
    create_statement_history_schema,
)


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
