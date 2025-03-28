from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...schemas.liabilities import LiabilityResponse
from ...schemas.recurring_bills import (
    GenerateBillsRequest,
    RecurringBillCreate,
    RecurringBillResponse,
    RecurringBillUpdate,
)
from ...services.recurring_bills import RecurringBillService

router = APIRouter()


@router.get("", response_model=List[RecurringBillResponse])
async def get_recurring_bills(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get all recurring bills"""
    service = RecurringBillService(db)
    return await service.get_recurring_bills(
        skip=skip, limit=limit, active_only=active_only
    )


@router.get("/{recurring_bill_id}", response_model=RecurringBillResponse)
async def get_recurring_bill(
    recurring_bill_id: int, db: AsyncSession = Depends(get_db)
):
    """Get a specific recurring bill by ID"""
    service = RecurringBillService(db)
    recurring_bill = await service.get_recurring_bill(recurring_bill_id)
    if not recurring_bill:
        raise HTTPException(status_code=404, detail="Recurring bill not found")
    return recurring_bill


@router.post("", response_model=RecurringBillResponse)
async def create_recurring_bill(
    recurring_bill: RecurringBillCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new recurring bill"""
    service = RecurringBillService(db)
    return await service.create_recurring_bill(recurring_bill)


@router.put("/{recurring_bill_id}", response_model=RecurringBillResponse)
async def update_recurring_bill(
    recurring_bill_id: int,
    recurring_bill: RecurringBillUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a recurring bill"""
    service = RecurringBillService(db)
    updated_bill = await service.update_recurring_bill(
        recurring_bill_id, recurring_bill
    )
    if not updated_bill:
        raise HTTPException(status_code=404, detail="Recurring bill not found")
    return updated_bill


@router.delete("/{recurring_bill_id}")
async def delete_recurring_bill(
    recurring_bill_id: int, db: AsyncSession = Depends(get_db)
):
    """Delete a recurring bill and its generated liabilities"""
    service = RecurringBillService(db)
    success = await service.delete_recurring_bill(recurring_bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recurring bill not found")
    return {"message": "Recurring bill deleted"}


@router.post("/{recurring_bill_id}/generate", response_model=List[LiabilityResponse])
async def generate_bills(
    recurring_bill_id: int,
    request: GenerateBillsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate liabilities for a recurring bill pattern"""
    service = RecurringBillService(db)
    bills = await service.generate_bills(recurring_bill_id, request.month, request.year)
    if not bills:
        raise HTTPException(
            status_code=400,
            detail="Could not generate bills. Bills may already exist for this period.",
        )
    return bills


@router.post("/generate-month", response_model=List[LiabilityResponse])
async def generate_bills_for_month(
    request: GenerateBillsRequest,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Generate liabilities for all recurring bills for a specific month"""
    service = RecurringBillService(db)
    return await service.generate_bills_for_month(
        request.month, request.year, active_only=active_only
    )
