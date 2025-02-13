import pytest
from decimal import Decimal
from datetime import date

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit

@pytest.fixture(scope="function")
async def checking_account(db_session):
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.flush()
    return account

@pytest.fixture(scope="function")
async def credit_account(db_session):
    account = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.flush()
    return account

@pytest.fixture(scope="function")
async def liability(db_session, checking_account):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("300.00"),
        due_date=date.today(),
        category_id=1,  # Assuming category 1 exists
        primary_account_id=checking_account.id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(liability)
    await db_session.flush()
    return liability

async def test_get_split_suggestions_historical(client, db_session, checking_account, credit_account, liability):
    """Test getting split suggestions based on historical patterns"""
    # Create two similar liabilities to meet min_frequency requirement
    for i in range(2):
        similar_liability = Liability(
            name=liability.name,  # Same name to trigger pattern matching
            amount=Decimal("300.00"),
            due_date=date.today(),
            category_id=liability.category_id,
            primary_account_id=checking_account.id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=date.today(),
            updated_at=date.today()
        )
        db_session.add(similar_liability)
        await db_session.flush()

        # Add historical splits
        historical_split1 = BillSplit(
            liability_id=similar_liability.id,
            account_id=checking_account.id,
            amount=Decimal("200.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
        historical_split2 = BillSplit(
            liability_id=similar_liability.id,
            account_id=credit_account.id,
            amount=Decimal("100.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
        db_session.add(historical_split1)
        db_session.add(historical_split2)
        await db_session.flush()

    # Get suggestions
    response = await client.get(f"/api/v1/bill-splits/suggestions/{liability.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["liability_id"] == liability.id
    assert data["total_amount"] == str(liability.amount)
    assert data["historical_pattern"] is True
    assert len(data["suggestions"]) == 2
    
    # Verify suggestions match historical pattern proportions
    suggestions = {s["account_id"]: s for s in data["suggestions"]}
    assert str(suggestions[checking_account.id]["amount"]) == "200.00"
    assert str(suggestions[credit_account.id]["amount"]) == "100.00"
    assert suggestions[checking_account.id]["confidence_score"] == 0.8
    assert suggestions[credit_account.id]["confidence_score"] == 0.8

async def test_get_split_suggestions_available_funds(client, db_session, checking_account, liability):
    """Test getting split suggestions based on available funds"""
    response = await client.get(f"/api/v1/bill-splits/suggestions/{liability.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["liability_id"] == liability.id
    assert data["total_amount"] == str(liability.amount)
    assert data["historical_pattern"] is False
    assert len(data["suggestions"]) == 1
    
    suggestion = data["suggestions"][0]
    assert suggestion["account_id"] == checking_account.id
    assert str(suggestion["amount"]) == str(liability.amount)
    assert suggestion["confidence_score"] == 0.6
    assert "sufficient funds" in suggestion["reason"]

async def test_get_split_suggestions_multiple_accounts(
    client, db_session, checking_account, credit_account, liability
):
    """Test getting split suggestions across multiple accounts"""
    # Update liability amount to require multiple accounts
    liability.amount = Decimal("1200.00")  # More than any single account's available funds
    await db_session.flush()
    
    response = await client.get(f"/api/v1/bill-splits/suggestions/{liability.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["liability_id"] == liability.id
    assert data["total_amount"] == str(liability.amount)
    assert data["historical_pattern"] is False
    assert len(data["suggestions"]) == 2
    
    # Verify total suggested amount matches liability amount
    total_suggested = sum(Decimal(s["amount"]) for s in data["suggestions"])
    assert total_suggested == liability.amount
    
    # Verify suggestions respect available funds
    for suggestion in data["suggestions"]:
        if suggestion["account_id"] == checking_account.id:
            assert Decimal(suggestion["amount"]) <= checking_account.available_balance
        elif suggestion["account_id"] == credit_account.id:
            available_credit = credit_account.total_limit + credit_account.available_balance
            assert Decimal(suggestion["amount"]) <= available_credit

async def test_get_split_suggestions_nonexistent_liability(client):
    """Test getting split suggestions for a nonexistent liability"""
    response = await client.get("/api/v1/bill-splits/suggestions/99999")
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()
