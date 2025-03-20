from datetime import date
from decimal import Decimal

import pytest
from httpx import AsyncClient

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability
from src.schemas.bill_splits import BillSplitCreate, BulkSplitOperation


@pytest.fixture(scope="function")
async def test_category(db_session):
    category = Category(
        name="Test Category",
        description="Test Description",
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(category)
    await db_session.flush()
    return category


@pytest.fixture(scope="function")
async def test_accounts(db_session):
    accounts = [
        Account(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-500"),
            total_limit=Decimal("1000"),
            created_at=date.today(),
            updated_at=date.today(),
        ),
        Account(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000"),
            created_at=date.today(),
            updated_at=date.today(),
        ),
    ]
    for account in accounts:
        db_session.add(account)
    await db_session.flush()
    return accounts


@pytest.fixture(scope="function")
async def test_liability(db_session, test_category, test_accounts):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("300"),
        due_date=date.today(),
        category_id=test_category.id,
        primary_account_id=test_accounts[0].id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        recurring=False,
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(liability)
    await db_session.flush()
    return liability


async def test_bulk_create_endpoint(client: AsyncClient, test_liability, test_accounts):
    """Test successful bulk creation of bill splits"""
    payload = {
        "operation_type": "create",
        "splits": [
            {
                "liability_id": test_liability.id,
                "account_id": test_accounts[0].id,
                "amount": str(Decimal("100")),
            },
            {
                "liability_id": test_liability.id,
                "account_id": test_accounts[1].id,
                "amount": str(Decimal("200")),
            },
        ],
        "validate_only": False,
    }

    response = await client.post("/api/v1/bill-splits/bulk", json=payload)
    assert response.status_code == 200

    result = response.json()
    assert result["success"] is True
    assert result["processed_count"] == 2
    assert result["success_count"] == 2
    assert result["failure_count"] == 0
    assert len(result["successful_splits"]) == 2
    assert len(result["errors"]) == 0


async def test_bulk_create_validation_failure(
    client: AsyncClient, test_liability, test_accounts
):
    """Test validation failure in bulk creation"""
    payload = {
        "operation_type": "create",
        "splits": [
            {
                "liability_id": test_liability.id,
                "account_id": test_accounts[0].id,
                "amount": str(Decimal("100")),
            },
            {
                "liability_id": test_liability.id,
                "account_id": test_accounts[1].id,
                "amount": str(Decimal("2000")),  # Exceeds available balance
            },
        ],
        "validate_only": False,
    }

    response = await client.post("/api/v1/bill-splits/bulk", json=payload)
    assert (
        response.status_code == 200
    )  # Still returns 200 as it's a valid request with validation errors

    result = response.json()
    assert result["success"] is False
    assert result["processed_count"] == 2
    assert result["success_count"] == 1
    assert result["failure_count"] == 1
    assert len(result["successful_splits"]) == 1
    assert len(result["errors"]) == 1
    assert "insufficient balance" in result["errors"][0]["error_message"].lower()


async def test_validate_bulk_operation_endpoint(
    client: AsyncClient, test_liability, test_accounts
):
    """Test validation-only endpoint"""
    payload = {
        "operation_type": "create",
        "splits": [
            {
                "liability_id": test_liability.id,
                "account_id": test_accounts[0].id,
                "amount": str(Decimal("100")),
            },
            {
                "liability_id": test_liability.id,
                "account_id": test_accounts[1].id,
                "amount": str(Decimal("2000")),  # Exceeds available balance
            },
        ],
        "validate_only": False,
    }

    response = await client.post("/api/v1/bill-splits/bulk/validate", json=payload)
    assert response.status_code == 200

    result = response.json()
    assert result["success"] is False
    assert result["processed_count"] == 2
    assert result["success_count"] == 1
    assert result["failure_count"] == 1
    assert len(result["errors"]) == 1
    assert "insufficient balance" in result["errors"][0]["error_message"].lower()


async def test_bulk_operation_invalid_liability(client: AsyncClient, test_accounts):
    """Test bulk operation with non-existent liability"""
    payload = {
        "operation_type": "create",
        "splits": [
            {
                "liability_id": 99999,  # Non-existent liability
                "account_id": test_accounts[0].id,
                "amount": str(Decimal("100")),
            }
        ],
        "validate_only": False,
    }

    response = await client.post("/api/v1/bill-splits/bulk", json=payload)
    assert response.status_code == 200

    result = response.json()
    assert result["success"] is False
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error_type"] == "validation"
