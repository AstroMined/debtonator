import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.recurring_income import RecurringIncome
from src.models.income import Income
from src.models.accounts import Account
from src.schemas.income import RecurringIncomeCreate, RecurringIncomeUpdate, GenerateIncomeRequest
from src.services.recurring_income import RecurringIncomeService

@pytest.fixture
async def test_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def test_recurring_income(db_session: AsyncSession, test_account: Account) -> RecurringIncome:
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_account.id,
        auto_deposit=False,
        active=True,
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)
    return recurring_income

async def test_create_recurring_income(db_session: AsyncSession, test_account: Account):
    """Test creating a recurring income template."""
    service = RecurringIncomeService(db_session)
    income_data = RecurringIncomeCreate(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_account.id,
        auto_deposit=False
    )
    
    result = await service.create(income_data)
    assert result.source == "Test Income"
    assert result.amount == Decimal("1000.00")
    assert result.day_of_month == 15
    assert result.account_id == test_account.id
    assert result.auto_deposit is False
    assert result.active is True

async def test_get_recurring_income(
    db_session: AsyncSession,
    test_recurring_income: RecurringIncome
):
    """Test retrieving a recurring income template."""
    service = RecurringIncomeService(db_session)
    result = await service.get(test_recurring_income.id)
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.source == test_recurring_income.source
    assert result.amount == test_recurring_income.amount

async def test_update_recurring_income(
    db_session: AsyncSession,
    test_recurring_income: RecurringIncome
):
    """Test updating a recurring income template."""
    service = RecurringIncomeService(db_session)
    update_data = RecurringIncomeUpdate(
        source="Updated Income",
        amount=Decimal("1500.00")
    )
    
    result = await service.update(test_recurring_income.id, update_data)
    assert result is not None
    assert result.source == "Updated Income"
    assert result.amount == Decimal("1500.00")
    assert result.day_of_month == test_recurring_income.day_of_month

async def test_delete_recurring_income(
    db_session: AsyncSession,
    test_recurring_income: RecurringIncome
):
    """Test deleting a recurring income template."""
    service = RecurringIncomeService(db_session)
    success = await service.delete(test_recurring_income.id)
    assert success is True
    
    # Verify it's deleted
    result = await service.get(test_recurring_income.id)
    assert result is None

async def test_list_recurring_income(
    db_session: AsyncSession,
    test_recurring_income: RecurringIncome
):
    """Test listing recurring income templates."""
    service = RecurringIncomeService(db_session)
    items, total = await service.list()
    assert total >= 1
    assert any(item.id == test_recurring_income.id for item in items)

async def test_generate_income(
    db_session: AsyncSession,
    test_recurring_income: RecurringIncome
):
    """Test generating income entries from recurring templates."""
    service = RecurringIncomeService(db_session)
    request = GenerateIncomeRequest(month=date.today().month, year=date.today().year)
    
    results = await service.generate_income(request)
    assert len(results) > 0
    
    generated = results[0]
    assert isinstance(generated, Income)
    assert generated.source == test_recurring_income.source
    assert generated.amount == test_recurring_income.amount
    assert generated.account_id == test_recurring_income.account_id
    assert generated.recurring is True
    assert generated.recurring_income_id == test_recurring_income.id
    
    # Test that duplicate entries are not created
    new_results = await service.generate_income(request)
    assert len(new_results) == 0
