import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.payments import PaymentService
from src.schemas.payments import PaymentCreate, PaymentSourceCreate, PaymentUpdate
from src.models.payments import Payment
from src.models.accounts import Account
from src.models.liabilities import Liability

@pytest.fixture
async def payment_service(db_session: AsyncSession):
    return PaymentService(db_session)

@pytest.mark.asyncio
async def test_get_payments(payment_service: PaymentService, base_payment: Payment, db_session: AsyncSession):
    """Test retrieving all payments with pagination"""
    # Get all payments
    payments = await payment_service.get_payments()
    assert len(payments) == 1
    assert payments[0].id == base_payment.id
    
    # Test pagination
    payments = await payment_service.get_payments(skip=1)
    assert len(payments) == 0
    
    # Test limit
    payments = await payment_service.get_payments(limit=1)
    assert len(payments) == 1

@pytest.mark.asyncio
async def test_get_payment(payment_service: PaymentService, base_payment: Payment, db_session: AsyncSession):
    """Test retrieving a single payment"""
    # Get the payment
    payment = await payment_service.get_payment(base_payment.id)
    
    # Verify payment data
    assert payment is not None
    assert payment.id == base_payment.id
    assert payment.amount == Decimal("100.00")
    assert payment.category == "Utilities"
    assert len(payment.sources) == 1
    assert payment.sources[0].amount == Decimal("100.00")

@pytest.mark.asyncio
async def test_create_payment(payment_service: PaymentService, base_account, db_session: AsyncSession):
    """Test creating a new payment with sources"""
    # Create payment data
    payment_create = PaymentCreate(
        amount=Decimal("150.00"),
        payment_date=date(2025, 2, 20),
        category="Test Category",
        description="Test payment",
        liability_id=None,
        income_id=None,
        sources=[
            PaymentSourceCreate(
                account_id=base_account.id,
                amount=Decimal("150.00")
            )
        ]
    )
    
    # Create the payment
    payment = await payment_service.create_payment(payment_create)
    
    # Verify payment was created
    assert payment is not None
    assert payment.amount == Decimal("150.00")
    assert payment.category == "Test Category"
    assert payment.description == "Test payment"
    assert len(payment.sources) == 1
    assert payment.sources[0].amount == Decimal("150.00")
    assert payment.sources[0].account_id == base_account.id

@pytest.mark.asyncio
async def test_create_payment_invalid_sources(payment_service: PaymentService, base_account, db_session: AsyncSession):
    """Test creating a payment with invalid source amounts"""
    # Create payment data with mismatched source amount
    payment_create = PaymentCreate(
        amount=Decimal("150.00"),
        payment_date=date(2025, 2, 20),
        category="Test Category",
        liability_id=None,
        income_id=None,
        sources=[
            PaymentSourceCreate(
                account_id=base_account.id,
                amount=Decimal("100.00")  # Less than total payment amount
            )
        ]
    )
    
    # Attempt to create payment should raise ValueError
    with pytest.raises(ValueError, match="Sum of payment sources .* must equal payment amount"):
        await payment_service.create_payment(payment_create)

@pytest.mark.asyncio
async def test_create_payment_invalid_account(payment_service: PaymentService, db_session: AsyncSession):
    """Test creating a payment with non-existent account"""
    # Create payment data with invalid account ID
    payment_create = PaymentCreate(
        amount=Decimal("150.00"),
        payment_date=date(2025, 2, 20),
        category="Test Category",
        liability_id=None,
        income_id=None,
        sources=[
            PaymentSourceCreate(
                account_id=99999,  # Non-existent account ID
                amount=Decimal("150.00")
            )
        ]
    )
    
    # Attempt to create payment should raise ValueError
    with pytest.raises(ValueError, match="Account .* not found"):
        await payment_service.create_payment(payment_create)

@pytest.mark.asyncio
async def test_update_payment_not_found(
    payment_service: PaymentService,
    db_session: AsyncSession
):
    """Test updating a non-existent payment"""
    payment_update = PaymentUpdate(
        amount=Decimal("200.00"),
        category="Updated Category"
    )
    
    # Update non-existent payment
    updated_payment = await payment_service.update_payment(99999, payment_update)
    assert updated_payment is None

@pytest.mark.asyncio
async def test_update_payment_invalid_sources(
    payment_service: PaymentService,
    base_payment: Payment,
    base_account: Account,
    db_session: AsyncSession
):
    """Test updating a payment with invalid source amounts"""
    payment_update = PaymentUpdate(
        amount=Decimal("200.00"),
        sources=[
            PaymentSourceCreate(
                account_id=base_account.id,
                amount=Decimal("150.00")  # Less than total payment amount
            )
        ]
    )
    
    # Attempt to update payment should raise ValueError
    with pytest.raises(ValueError, match="Sum of payment sources .* must equal payment amount"):
        await payment_service.update_payment(base_payment.id, payment_update)

@pytest.mark.asyncio
async def test_update_payment_partial(
    payment_service: PaymentService,
    base_payment: Payment,
    db_session: AsyncSession
):
    """Test partial update of a payment without changing sources"""
    payment_update = PaymentUpdate(
        category="Updated Category"
    )
    
    # Update only the category
    updated_payment = await payment_service.update_payment(base_payment.id, payment_update)
    
    # Verify only category was updated
    assert updated_payment is not None
    assert updated_payment.category == "Updated Category"
    assert updated_payment.amount == base_payment.amount
    assert len(updated_payment.sources) == len(base_payment.sources)

@pytest.mark.asyncio
async def test_update_payment(payment_service: PaymentService, base_payment: Payment, base_account, db_session: AsyncSession):
    """Test updating an existing payment"""
    # Create update data
    payment_update = PaymentUpdate(
        amount=Decimal("200.00"),
        category="Updated Category",
        sources=[
            PaymentSourceCreate(
                account_id=base_account.id,
                amount=Decimal("200.00")
            )
        ]
    )
    
    # Update the payment
    updated_payment = await payment_service.update_payment(base_payment.id, payment_update)
    
    # Verify payment was updated
    assert updated_payment is not None
    assert updated_payment.amount == Decimal("200.00")
    assert updated_payment.category == "Updated Category"
    assert len(updated_payment.sources) == 1
    assert updated_payment.sources[0].amount == Decimal("200.00")

@pytest.mark.asyncio
async def test_delete_payment_not_found(
    payment_service: PaymentService,
    db_session: AsyncSession
):
    """Test deleting a non-existent payment"""
    result = await payment_service.delete_payment(99999)
    assert result is False

@pytest.mark.asyncio
async def test_delete_payment_with_sources(
    payment_service: PaymentService,
    base_payment: Payment,
    db_session: AsyncSession
):
    """Test deleting a payment with associated sources"""
    # Verify payment has sources before deletion
    payment = await payment_service.get_payment(base_payment.id)
    assert len(payment.sources) > 0
    
    # Delete the payment
    result = await payment_service.delete_payment(base_payment.id)
    assert result is True
    
    # Verify payment and its sources were deleted
    deleted_payment = await payment_service.get_payment(base_payment.id)
    assert deleted_payment is None

@pytest.mark.asyncio
async def test_delete_payment(payment_service: PaymentService, base_payment: Payment, db_session: AsyncSession):
    """Test deleting a payment"""
    # Delete the payment
    result = await payment_service.delete_payment(base_payment.id)
    assert result is True
    
    # Verify payment was deleted
    deleted_payment = await payment_service.get_payment(base_payment.id)
    assert deleted_payment is None

@pytest.mark.asyncio
async def test_get_payments_by_date_range(
    payment_service: PaymentService,
    base_payment: Payment,
    db_session: AsyncSession
):
    """Test retrieving payments within a date range"""
    # Get payments for a date range that includes our test payment
    payments = await payment_service.get_payments_by_date_range(
        date(2025, 2, 1),
        date(2025, 2, 28)
    )
    
    # Verify payment is in results
    assert len(payments) == 1
    assert payments[0].id == base_payment.id
    
    # Get payments for a date range that doesn't include our test payment
    payments = await payment_service.get_payments_by_date_range(
        date(2025, 3, 1),
        date(2025, 3, 31)
    )
    
    # Verify no payments found
    assert len(payments) == 0

@pytest.mark.asyncio
async def test_get_payments_for_liability(
    payment_service: PaymentService,
    base_payment: Payment,
    base_bill: Liability,
    db_session: AsyncSession
):
    """Test retrieving payments for a specific liability"""
    # Get payments for the liability
    payments = await payment_service.get_payments_for_liability(base_bill.id)
    
    # Verify payment is in results
    assert len(payments) == 1
    assert payments[0].id == base_payment.id
    assert payments[0].liability_id == base_bill.id
    
    # Get payments for non-existent liability
    payments = await payment_service.get_payments_for_liability(99999)
    assert len(payments) == 0

@pytest.mark.asyncio
async def test_get_payments_for_account(
    payment_service: PaymentService,
    base_payment: Payment,
    base_account: Account,
    db_session: AsyncSession
):
    """Test retrieving payments for a specific account"""
    # Get payments for the account
    payments = await payment_service.get_payments_for_account(base_account.id)
    
    # Verify payment is in results
    assert len(payments) == 1
    assert payments[0].id == base_payment.id
    assert any(source.account_id == base_account.id for source in payments[0].sources)
    
    # Get payments for non-existent account
    payments = await payment_service.get_payments_for_account(99999)
    assert len(payments) == 0
