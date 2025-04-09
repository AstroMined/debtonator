from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.deposit_schedules import DepositSchedule
from src.models.payment_schedules import PaymentSchedule
from src.utils.datetime_utils import days_from_now, naive_utc_now, utc_now


@pytest_asyncio.fixture
async def test_payment_schedule(
    db_session: AsyncSession,
    test_liability,
    test_checking_account,
) -> PaymentSchedule:
    """
    Create a test payment schedule.
    
    Args:
        db_session: Database session fixture
        test_liability: Test liability fixture
        test_checking_account: Test checking account fixture
        
    Returns:
        PaymentSchedule: Created payment schedule
    """
    # Create a naive datetime for DB storage
    scheduled_date = days_from_now(7).replace(tzinfo=None)

    # Create model instance directly
    schedule = PaymentSchedule(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=Decimal("200.00"),
        scheduled_date=scheduled_date,
        description="Test payment schedule",
        auto_process=False,  # Default value
    )

    # Add to session manually
    db_session.add(schedule)
    await db_session.flush()
    await db_session.refresh(schedule)

    return schedule


@pytest_asyncio.fixture
async def test_multiple_payment_schedules(
    db_session: AsyncSession,
    test_liability,
    test_checking_account,
    test_second_account,
) -> List[PaymentSchedule]:
    """
    Create multiple payment schedules for testing.
    
    Args:
        db_session: Database session fixture
        test_liability: Test liability fixture
        test_checking_account: Test checking account fixture
        test_second_account: Test second account fixture
        
    Returns:
        List[PaymentSchedule]: List of created payment schedules
    """
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

    # Create the payment schedules using direct model instantiation
    created_schedules = []
    for data in schedule_data:
        # Make datetime naive for DB storage
        naive_date = data["scheduled_date"].replace(tzinfo=None)

        # Create model instance directly
        schedule = PaymentSchedule(
            liability_id=data["liability_id"],
            account_id=data["account_id"],
            amount=data["amount"],
            scheduled_date=naive_date,
            description=data["description"],
            auto_process=data["auto_process"],
        )

        # Add to session manually
        db_session.add(schedule)
        created_schedules.append(schedule)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for schedule in created_schedules:
        await db_session.refresh(schedule)

    return created_schedules


@pytest_asyncio.fixture
async def test_deposit_schedule(
    db_session: AsyncSession,
    test_income,
    test_checking_account,
) -> DepositSchedule:
    """
    Create a test deposit schedule.
    
    Args:
        db_session: Database session fixture
        test_income: Test income fixture
        test_checking_account: Test checking account fixture
        
    Returns:
        DepositSchedule: Created deposit schedule
    """
    # Create a naive datetime for DB storage
    schedule_date = days_from_now(7).replace(tzinfo=None)

    # Create model instance directly
    schedule = DepositSchedule(
        income_id=test_income.id,
        account_id=test_checking_account.id,
        schedule_date=schedule_date,
        amount=Decimal("3000.00"),
        recurring=False,
        status="pending",
    )

    # Add to session manually
    db_session.add(schedule)
    await db_session.flush()
    await db_session.refresh(schedule)

    return schedule


@pytest_asyncio.fixture
async def test_multiple_deposit_schedules(
    db_session: AsyncSession,
    test_income,
    test_additional_income,
    test_checking_account,
    test_second_account,
) -> List[DepositSchedule]:
    """
    Create multiple deposit schedules for testing.
    
    Args:
        db_session: Database session fixture
        test_income: Test income fixture
        test_additional_income: Test additional income fixture
        test_checking_account: Test checking account fixture
        test_second_account: Test second account fixture
        
    Returns:
        List[DepositSchedule]: List of created deposit schedules
    """
    now = utc_now()

    # Create multiple deposit schedules with various attributes
    schedule_data = [
        {
            "income_id": test_income.id,
            "account_id": test_checking_account.id,
            "schedule_date": now + timedelta(days=3),
            "amount": Decimal("3000.00"),
            "recurring": False,
            "recurrence_pattern": None,
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
            "recurrence_pattern": None,
            "status": "pending",  # Overdue
        },
        {
            "income_id": test_additional_income.id,
            "account_id": test_second_account.id,
            "schedule_date": now - timedelta(days=10),  # Past date
            "amount": Decimal("500.00"),
            "recurring": False,
            "recurrence_pattern": None,
            "status": "processed",  # Already processed
        },
    ]

    # Create the deposit schedules using direct model instantiation
    created_schedules = []
    for data in schedule_data:
        # Make datetime naive for DB storage
        naive_date = data["schedule_date"].replace(tzinfo=None)

        # Create model instance directly
        schedule = DepositSchedule(
            income_id=data["income_id"],
            account_id=data["account_id"],
            schedule_date=naive_date,
            amount=data["amount"],
            recurring=data["recurring"],
            recurrence_pattern=data["recurrence_pattern"],
            status=data["status"],
        )

        # Add to session manually
        db_session.add(schedule)
        created_schedules.append(schedule)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for schedule in created_schedules:
        await db_session.refresh(schedule)

    return created_schedules
