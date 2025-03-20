from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...schemas.payments import (
    PaymentCreate,
    PaymentDateRange,
    PaymentResponse,
    PaymentUpdate,
)
from ...services.payments import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate, db: AsyncSession = Depends(get_db)
) -> PaymentResponse:
    """Create a new payment with associated payment sources"""
    try:
        payment_service = PaymentService(db)
        return await payment_service.create_payment(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> List[PaymentResponse]:
    """Get a list of payments with pagination"""
    payment_service = PaymentService(db)
    return await payment_service.get_payments(skip=skip, limit=limit)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int, db: AsyncSession = Depends(get_db)
) -> PaymentResponse:
    """Get a specific payment by ID"""
    payment_service = PaymentService(db)
    payment = await payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int, payment_update: PaymentUpdate, db: AsyncSession = Depends(get_db)
) -> PaymentResponse:
    """Update an existing payment"""
    try:
        payment_service = PaymentService(db)
        payment = await payment_service.update_payment(payment_id, payment_update)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{payment_id}")
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Delete a payment and its associated sources"""
    payment_service = PaymentService(db)
    if not await payment_service.delete_payment(payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}


@router.get("/date-range/", response_model=List[PaymentResponse])
async def get_payments_by_date_range(
    date_range: PaymentDateRange, db: AsyncSession = Depends(get_db)
) -> List[PaymentResponse]:
    """Get payments within a specific date range"""
    payment_service = PaymentService(db)
    return await payment_service.get_payments_by_date_range(
        date_range.start_date, date_range.end_date
    )


@router.get("/liability/{liability_id}", response_model=List[PaymentResponse])
async def get_payments_for_liability(
    liability_id: int, db: AsyncSession = Depends(get_db)
) -> List[PaymentResponse]:
    """Get all payments associated with a specific liability"""
    payment_service = PaymentService(db)
    return await payment_service.get_payments_for_liability(liability_id)


@router.get("/account/{account_id}", response_model=List[PaymentResponse])
async def get_payments_for_account(
    account_id: int, db: AsyncSession = Depends(get_db)
) -> List[PaymentResponse]:
    """Get all payments that have sources from a specific account"""
    payment_service = PaymentService(db)
    return await payment_service.get_payments_for_account(account_id)
