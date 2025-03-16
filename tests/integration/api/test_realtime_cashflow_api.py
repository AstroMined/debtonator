from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from src.models.accounts import Account
from src.models.liabilities import Liability

@pytest.fixture(scope="function")
async def test_accounts(db_session):
    """Create test accounts for API testing."""
    accounts = [
        Account(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("2500.00"),
            created_at=datetime.now().date(),
            updated_at=datetime.now().date()
        ),
        Account(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-1000.00"),
            available_credit=Decimal("4000.00"),
            total_limit=Decimal("5000.00"),
            created_at=datetime.now().date(),
            updated_at=datetime.now().date()
        )
    ]
    
    for account in accounts:
        db_session.add(account)
    await db_session.commit()
    return accounts

@pytest.fixture(scope="function")
async def test_bills(db_session, test_accounts, base_category):
    """Create test bills for API testing."""
    today = datetime.now().date()
    bills = [
        Liability(
            name="Test Bill 1",
            amount=Decimal("500.00"),
            due_date=today + timedelta(days=5),
            description="Test bill 1",
            recurring=False,
            category_id=base_category.id,
            primary_account_id=test_accounts[0].id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Liability(
            name="Test Bill 2",
            amount=Decimal("300.00"),
            due_date=today + timedelta(days=10),
            description="Test bill 2",
            recurring=False,
            category_id=base_category.id,
            primary_account_id=test_accounts[0].id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    for bill in bills:
        db_session.add(bill)
    await db_session.commit()
    return bills

async def test_get_realtime_cashflow(client, test_accounts, test_bills):
    """Test GET /api/v1/realtime-cashflow endpoint."""
    response = await client.get("/api/v1/realtime-cashflow/")
    assert response.status_code == 200
    
    data = response.json()["data"]
    
    # Verify account balances
    assert len(data["account_balances"]) == 2
    checking = next(a for a in data["account_balances"] if a["type"] == "checking")
    credit = next(a for a in data["account_balances"] if a["type"] == "credit")
    
    assert checking["current_balance"] == "2500.00"
    assert credit["available_credit"] == "4000.00"
    
    # Verify totals
    assert data["total_available_funds"] == "2500.00"  # Only checking balance
    assert data["total_available_credit"] == "4000.00"
    assert data["total_liabilities_due"] == "800.00"  # Sum of both bills
    assert data["net_position"] == "1700.00"  # 2500 - 800
    
    # Verify upcoming bill info
    assert data["days_until_next_bill"] == 5  # First bill is due in 5 days
    assert data["minimum_balance_required"] == "800.00"  # Both bills within 14 days
    assert data["projected_deficit"] is None  # We have enough funds
