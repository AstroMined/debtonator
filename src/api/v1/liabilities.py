from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.liabilities import (
    LiabilityResponse,
    LiabilityCreate,
    LiabilityUpdate,
    LiabilityDateRange
)
from src.schemas.payments import PaymentCreate, PaymentResponse
from src.services.liabilities import LiabilityService
from src.services.payments import PaymentService

router = APIRouter()

@router.get("/", response_model=List[LiabilityResponse])
async def list_liabilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List all liabilities with pagination support.
    """
    try:
        liability_service = LiabilityService(db)
        liabilities = await liability_service.get_liabilities(skip=skip, limit=limit)
        return liabilities
    except Exception as e:
        import traceback
        error_detail = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/", response_model=LiabilityResponse, status_code=201)
async def create_liability(
    liability: LiabilityCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new liability.
    """
    liability_service = LiabilityService(db)
    try:
        return await liability_service.create_liability(liability)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{liability_id}", response_model=LiabilityResponse)
async def get_liability(
    liability_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific liability by ID.
    """
    liability_service = LiabilityService(db)
    liability = await liability_service.get_liability(liability_id)
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")
    return liability

@router.put("/{liability_id}", response_model=LiabilityResponse)
async def update_liability(
    liability_id: int,
    liability_update: LiabilityUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a liability's details.
    """
    liability_service = LiabilityService(db)
    try:
        liability = await liability_service.update_liability(liability_id, liability_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")
    return liability

@router.delete("/{liability_id}")
async def delete_liability(
    liability_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a liability.
    """
    liability_service = LiabilityService(db)
    success = await liability_service.delete_liability(liability_id)
    if not success:
        raise HTTPException(status_code=404, detail="Liability not found")
    return {"message": "Liability deleted successfully"}

@router.get("/unpaid/", response_model=List[LiabilityResponse])
async def list_unpaid_liabilities(
    db: AsyncSession = Depends(get_db)
):
    """
    List all unpaid liabilities.
    """
    liability_service = LiabilityService(db)
    return await liability_service.get_unpaid_liabilities()

@router.get("/by-date-range/", response_model=List[LiabilityResponse])
async def get_liabilities_by_date_range(
    date_range: LiabilityDateRange,
    db: AsyncSession = Depends(get_db)
):
    """
    Get liabilities within a specific date range.
    """
    liability_service = LiabilityService(db)
    return await liability_service.get_liabilities_by_date_range(
        start_date=date_range.start_date,
        end_date=date_range.end_date
    )

@router.post("/{liability_id}/payments/", response_model=PaymentResponse)
async def create_payment_for_liability(
    liability_id: int,
    payment: PaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a payment for a specific liability.
    """
    # First verify liability exists
    liability_service = LiabilityService(db)
    liability = await liability_service.get_liability(liability_id)
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")

    # Create payment
    payment_service = PaymentService(db)
    try:
        # Ensure payment is associated with this liability
        payment.bill_id = liability_id
        return await payment_service.create_payment(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{liability_id}/payments/", response_model=List[PaymentResponse])
async def get_payments_for_liability(
    liability_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all payments for a specific liability.
    """
    # First verify liability exists
    liability_service = LiabilityService(db)
    liability = await liability_service.get_liability(liability_id)
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")

    # Get payments
    payment_service = PaymentService(db)
    return await payment_service.get_payments_for_liability(liability_id)
