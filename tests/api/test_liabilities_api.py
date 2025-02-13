import pytest
from datetime import date
from decimal import Decimal
from httpx import AsyncClient

from src.schemas.liabilities import AutoPaySettings, AutoPayUpdate

async def test_update_auto_pay_settings(client: AsyncClient, base_bill):
    """Test updating auto-pay settings"""
    settings = AutoPaySettings(
        preferred_pay_date=15,
        days_before_due=5,
        payment_method="bank_transfer",
        minimum_balance_required=Decimal("100.00"),
        retry_on_failure=True,
        notification_email="test@example.com"
    )
    
    update = AutoPayUpdate(enabled=True, settings=settings)
    response = await client.put(
        f"/api/v1/liabilities/{base_bill.id}/auto-pay",
        json=update.model_dump()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["auto_pay"] is True
    assert data["auto_pay_enabled"] is True
    assert data["auto_pay_settings"]["payment_method"] == "bank_transfer"
    assert data["auto_pay_settings"]["preferred_pay_date"] == 15

async def test_get_auto_pay_status(client: AsyncClient, base_bill):
    """Test getting auto-pay status"""
    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await client.put(
        f"/api/v1/liabilities/{base_bill.id}/auto-pay",
        json=update.model_dump()
    )
    
    # Get status
    response = await client.get(f"/api/v1/liabilities/{base_bill.id}/auto-pay")
    
    assert response.status_code == 200
    data = response.json()
    assert data["auto_pay"] is True
    assert data["enabled"] is True
    assert data["settings"]["payment_method"] == "bank_transfer"
    assert data["last_attempt"] is None

async def test_process_auto_pay(client: AsyncClient, base_bill):
    """Test processing auto-pay"""
    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await client.put(
        f"/api/v1/liabilities/{base_bill.id}/auto-pay",
        json=update.model_dump()
    )
    
    # Process auto-pay
    response = await client.post(f"/api/v1/liabilities/{base_bill.id}/auto-pay/process")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Auto-pay processed successfully"

async def test_disable_auto_pay(client: AsyncClient, base_bill):
    """Test disabling auto-pay"""
    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await client.put(
        f"/api/v1/liabilities/{base_bill.id}/auto-pay",
        json=update.model_dump()
    )
    
    # Then disable it
    response = await client.delete(f"/api/v1/liabilities/{base_bill.id}/auto-pay")
    
    assert response.status_code == 200
    data = response.json()
    assert data["auto_pay_enabled"] is False

async def test_get_auto_pay_candidates(client: AsyncClient, base_bill):
    """Test getting auto-pay candidates"""
    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await client.put(
        f"/api/v1/liabilities/{base_bill.id}/auto-pay",
        json=update.model_dump()
    )
    
    # Get candidates
    response = await client.get("/api/v1/liabilities/auto-pay/candidates")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == base_bill.id

async def test_auto_pay_nonexistent_liability(client: AsyncClient):
    """Test auto-pay operations with non-existent liability"""
    liability_id = 999999
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    
    # Test update
    response = await client.put(
        f"/api/v1/liabilities/{liability_id}/auto-pay",
        json=update.model_dump()
    )
    assert response.status_code == 404
    
    # Test get status
    response = await client.get(f"/api/v1/liabilities/{liability_id}/auto-pay")
    assert response.status_code == 404
    
    # Test process
    response = await client.post(f"/api/v1/liabilities/{liability_id}/auto-pay/process")
    assert response.status_code == 400
    
    # Test disable
    response = await client.delete(f"/api/v1/liabilities/{liability_id}/auto-pay")
    assert response.status_code == 404

async def test_invalid_auto_pay_settings(client: AsyncClient, base_bill):
    """Test updating auto-pay with invalid settings"""
    # Test invalid preferred pay date
    settings = AutoPaySettings(
        preferred_pay_date=32,  # Invalid day
        payment_method="bank_transfer"
    )
    update = AutoPayUpdate(enabled=True, settings=settings)
    response = await client.put(
        f"/api/v1/liabilities/{base_bill.id}/auto-pay",
        json=update.model_dump()
    )
    assert response.status_code == 422
