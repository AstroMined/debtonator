"""
Integration tests for banking API endpoints.

These tests verify that the banking API endpoints work correctly with the
service layer, repository layer, and feature flag system.
"""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.base import api_router
from src.main import app
from src.repositories.accounts import AccountRepository
from src.services.accounts import AccountService
from tests.fixtures.models.account_types.banking import (
    fixture_bnpl_account,
    fixture_checking_account,
)


@pytest.fixture
def test_app():
    """Create a test app instance with overridden dependencies."""
    # Create a new app instance for testing
    app.include_router(api_router)

    # Return the test client
    return TestClient(app)


@pytest.fixture
async def mock_account_service(monkeypatch, db_session: AsyncSession):
    """Create a mock account service for testing."""
    # Create a real repository for the service to use
    repo = AccountRepository(db_session)

    # Create a service instance
    service = AccountService(
        account_repo=repo,
        statement_repo=None,  # Not needed for these tests
        credit_limit_repo=None,  # Not needed for these tests
        transaction_repo=None,  # Not needed for these tests
    )

    # Override the dependency
    async def override_get_account_service():
        return service

    monkeypatch.setattr(
        "src.api.dependencies.services.get_account_service",
        override_get_account_service,
    )

    # Return the service for test manipulation
    return service


@pytest.mark.asyncio
async def test_get_banking_overview(
    test_app, mock_account_service, db_session: AsyncSession
):
    """Test the GET /banking/overview endpoint."""
    # Create test checking account
    checking = fixture_checking_account(current_balance=Decimal("1000.00"))
    db_session.add(checking)

    # Create test BNPL account
    bnpl = fixture_bnpl_account(current_balance=Decimal("-500.00"))
    db_session.add(bnpl)

    # Commit the changes
    await db_session.commit()

    # Make the request
    user_id = 1  # User ID used in fixtures
    response = test_app.get(f"/api/v1/banking/overview?user_id={user_id}")

    # Verify the response
    assert response.status_code == 200
    data = response.json()

    # Check for expected keys
    assert "total_cash" in data
    assert "checking_balance" in data
    assert "bnpl_balance" in data
    assert "total_debt" in data

    # Check the values
    assert data["checking_balance"] == 1000.0
    assert data["bnpl_balance"] == 500.0  # Absolute value of negative balance
    assert data["total_cash"] == 1000.0
    assert data["total_debt"] == 500.0


@pytest.mark.asyncio
async def test_get_upcoming_payments(
    test_app, mock_account_service, db_session: AsyncSession
):
    """Test the GET /banking/upcoming-payments endpoint."""
    # Create test BNPL account with a payment due
    bnpl = fixture_bnpl_account(current_balance=Decimal("-500.00"))

    # Add to database
    db_session.add(bnpl)
    await db_session.commit()

    # Mock the get_upcoming_payments method to return test data
    async def mock_get_upcoming_payments(user_id, days):
        # Return mock payment data
        return [
            {
                "account_id": bnpl.id,
                "account_name": bnpl.name,
                "account_type": "bnpl",
                "due_date": "2025-04-20T00:00:00.000Z",
                "amount": 100.0,
                "payment_type": "installment",
                "status": "due",
                "details": {
                    "installment_number": 1,
                    "total_installments": 5,
                },
            }
        ]

    # Apply the mock
    mock_account_service.get_upcoming_payments = mock_get_upcoming_payments

    # Make the request
    user_id = 1  # User ID used in fixtures
    response = test_app.get(f"/api/v1/banking/upcoming-payments?user_id={user_id}")

    # Verify the response
    assert response.status_code == 200
    data = response.json()

    # Check the data
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["account_type"] == "bnpl"
    assert data[0]["amount"] == 100.0
    assert "due_date" in data[0]
    assert data[0]["payment_type"] == "installment"


@pytest.mark.asyncio
async def test_create_banking_account(
    test_app, mock_account_service, db_session: AsyncSession
):
    """Test the POST /banking/accounts endpoint."""
    # Create account data
    account_data = {
        "account_type": "checking",
        "name": "Test Checking Account",
        "account_number": "123456789",
        "institution": "Test Bank",
        "current_balance": 1000.0,
        "available_balance": 1000.0,
        "routing_number": "987654321",
        "has_overdraft_protection": True,
        "overdraft_limit": 500.0,
    }

    # Make the request
    response = test_app.post("/api/v1/banking/accounts", json=account_data)

    # Verify the response
    assert response.status_code == 201
    data = response.json()

    # Check key fields
    assert data["account_type"] == "checking"
    assert data["name"] == "Test Checking Account"
    assert data["current_balance"] == 1000.0
    assert data["available_balance"] == 1000.0
    assert data["routing_number"] == "987654321"
    assert data["has_overdraft_protection"] is True
    assert data["overdraft_limit"] == 500.0


@pytest.mark.asyncio
async def test_update_bnpl_account_status(
    test_app, mock_account_service, db_session: AsyncSession
):
    """Test the POST /banking/accounts/bnpl/{account_id}/update-status endpoint."""
    # Create test BNPL account
    bnpl = fixture_bnpl_account(
        current_balance=Decimal("-500.00"), installment_count=5, installments_paid=1
    )

    # Add to database
    db_session.add(bnpl)
    await db_session.commit()

    # Create status update data
    status_update = {
        "account_type": "bnpl",
        "installments_paid": 2,
    }

    # Make the request
    response = test_app.post(
        f"/api/v1/banking/accounts/bnpl/{bnpl.id}/update-status", json=status_update
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()

    # Check key fields
    assert data["account_type"] == "bnpl"
    assert data["installments_paid"] == 2


@pytest.mark.asyncio
async def test_get_banking_account_types(test_app):
    """Test the GET /banking/accounts/types endpoint."""
    # Make the request
    response = test_app.get("/api/v1/banking/accounts/types")

    # Verify the response
    assert response.status_code == 200
    data = response.json()

    # Check the data structure
    assert isinstance(data, list)

    # Check that we have the expected account types
    account_types = [item["account_type"] for item in data]
    assert "checking" in account_types
    assert "savings" in account_types
    assert "credit" in account_types

    # Check for extended fields
    for item in data:
        assert "supports_multi_currency" in item
        assert "supports_international" in item


@pytest.mark.asyncio
async def test_invalid_bnpl_account_status_update(
    test_app, mock_account_service, db_session: AsyncSession
):
    """Test the POST /banking/accounts/bnpl/{account_id}/update-status endpoint with invalid data."""
    # Create test checking account (not BNPL)
    checking = fixture_checking_account(current_balance=Decimal("1000.00"))

    # Add to database
    db_session.add(checking)
    await db_session.commit()

    # Create status update data
    status_update = {
        "account_type": "bnpl",
        "installments_paid": 2,
    }

    # Make the request to update a checking account as if it were BNPL
    response = test_app.post(
        f"/api/v1/banking/accounts/bnpl/{checking.id}/update-status", json=status_update
    )

    # Verify the response shows an error
    assert response.status_code == 400
    data = response.json()
    assert "Account" in data["detail"]
    assert "not a BNPL account" in data["detail"]
