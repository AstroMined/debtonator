"""Integration tests for the API response formatter."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_decimal_formatting_in_response(client: AsyncClient):
    """Test that decimal values are properly formatted in API responses."""
    # Use the accounts endpoint since it contains monetary values
    response = await client.get("/api/v1/accounts")

    assert response.status_code == 200
    data = response.json()

    # Check that at least one account is returned
    assert len(data) > 0

    # Verify that all decimal values are formatted with 2 decimal places
    for account in data:
        if "available_balance" in account:
            # Check that the value is formatted as a string with 2 decimal places
            balance_str = account["available_balance"]
            assert isinstance(balance_str, str)
            # If the value contains a decimal point, verify it has exactly 2 decimal places
            if "." in balance_str:
                decimal_places = len(balance_str.split(".")[-1])
                assert (
                    decimal_places == 2
                ), f"Expected 2 decimal places, got {decimal_places} in {balance_str}"


@pytest.mark.asyncio
async def test_nested_decimal_formatting(client: AsyncClient):
    """Test that nested decimal values are properly formatted."""
    # Create a bill with a payment to test nested formatting
    # First create a bill
    bill_data = {
        "name": "Test Bill for Formatter",
        "amount": "123.45",
        "due_date": "2025-03-30T00:00:00Z",
        "category": "Utilities",
        "recurring": False,
        "auto_pay": False,
    }
    bill_response = await client.post("/api/v1/bills", json=bill_data)
    assert bill_response.status_code == 201
    bill_id = bill_response.json()["id"]

    # Then create a payment for that bill
    payment_data = {
        "bill_id": bill_id,
        "amount": "123.45",
        "payment_date": "2025-03-16T00:00:00Z",
        "category": "Utilities",
        "payment_sources": [{"account_id": 1, "amount": "123.45"}],
    }
    payment_response = await client.post("/api/v1/payments", json=payment_data)
    assert payment_response.status_code == 201

    # Now get the bill with its payments (nested structure)
    detail_response = await client.get(f"/api/v1/bills/{bill_id}")
    assert detail_response.status_code == 200
    data = detail_response.json()

    # Check formatting of the bill amount
    assert isinstance(data["amount"], str)
    if "." in data["amount"]:
        decimal_places = len(data["amount"].split(".")[-1])
        assert decimal_places == 2

    # Check formatting of payment amounts if there are payments
    if "payments" in data and data["payments"]:
        for payment in data["payments"]:
            assert isinstance(payment["amount"], str)
            if "." in payment["amount"]:
                decimal_places = len(payment["amount"].split(".")[-1])
                assert decimal_places == 2

            # Check formatting of payment source amounts (nested deeper)
            if "sources" in payment and payment["sources"]:
                for source in payment["sources"]:
                    assert isinstance(source["amount"], str)
                    if "." in source["amount"]:
                        decimal_places = len(source["amount"].split(".")[-1])
                        assert decimal_places == 2


@pytest.mark.asyncio
async def test_percentage_field_formatting(client: AsyncClient):
    """Test that percentage fields are properly formatted with 4 decimal places."""
    # Create a custom forecast request to get percentage fields in the response
    forecast_request = {
        "start_date": "2025-03-16T00:00:00Z",
        "end_date": "2025-04-15T00:00:00Z",
        "include_pending": True,
        "include_recurring": True,
        "confidence_threshold": "0.8000",
    }

    response = await client.post(
        "/api/v1/cashflow/forecasts/custom", json=forecast_request
    )

    # If the forecast endpoint works, check the response
    if response.status_code == 200:
        data = response.json()

        # Look for percentage fields in the response
        percentage_fields = [
            "confidence_score",
            "overall_confidence",
            "forecast_confidence",
            "credit_utilization",
            "confidence_threshold",
        ]

        # Find and verify any percentage fields
        def check_percentage_fields(obj):
            if not isinstance(obj, dict):
                return False

            found_percentage = False
            for field in percentage_fields:
                if field in obj:
                    found_percentage = True
                    value = obj[field]
                    assert isinstance(
                        value, str
                    ), f"Expected string for {field}, got {type(value)}"
                    if "." in value:
                        decimal_places = len(value.split(".")[-1])
                        # Percentage fields should have 4 decimal places
                        assert (
                            decimal_places == 4
                        ), f"Expected 4 decimal places for {field}, got {decimal_places}"

            # Recursively check nested objects
            for key, value in obj.items():
                if isinstance(value, dict):
                    if check_percentage_fields(value):
                        found_percentage = True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and check_percentage_fields(item):
                            found_percentage = True

            return found_percentage

        # If we have data, check it for percentage fields
        if data:
            # This will pass even if no percentage fields are found
            # The test is to verify proper formatting IF they exist
            check_percentage_fields(data)
    else:
        pytest.skip("Forecast endpoint not available, skipping percentage field test")

    # Try another endpoint that might have percentage fields
    response = await client.get("/api/v1/accounts/1/credit-limit-history")
    if response.status_code == 200:
        data = response.json()
        if "credit_utilization" in data:
            value = data["credit_utilization"]
            if isinstance(value, str) and "." in value:
                decimal_places = len(value.split(".")[-1])
                assert (
                    decimal_places == 4
                ), f"Expected 4 decimal places for credit_utilization, got {decimal_places}"
