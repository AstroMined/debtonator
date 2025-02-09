from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.bills import BillResponse, BillCreate, BillUpdate, BillDateRange
from src.services.bills import BillService

router = APIRouter()

@router.get("/", response_model=List[BillResponse])
async def list_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List all bills with pagination support.
    """
    bill_service = BillService(db)
    return await bill_service.get_bills(skip=skip, limit=limit)

@router.post("/", response_model=BillResponse)
async def create_bill(
    bill: BillCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bill.
    """
    bill_service = BillService(db)
    return await bill_service.create_bill(bill)

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific bill by ID.
    """
    bill_service = BillService(db)
    bill = await bill_service.get_bill(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a bill's details.
    """
    bill_service = BillService(db)
    bill = await bill_service.update_bill(bill_id, bill_update)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.delete("/{bill_id}")
async def delete_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a bill.
    """
    bill_service = BillService(db)
    success = await bill_service.delete_bill(bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}

@router.get("/unpaid/", response_model=List[BillResponse])
async def list_unpaid_bills(
    db: AsyncSession = Depends(get_db)
):
    """
    List all unpaid bills.
    """
    bill_service = BillService(db)
    return await bill_service.get_unpaid_bills()

@router.get("/by-date-range/", response_model=List[BillResponse])
async def get_bills_by_date_range(
    date_range: BillDateRange,
    db: AsyncSession = Depends(get_db)
):
    """
    Get bills within a specific date range.
    """
    bill_service = BillService(db)
    return await bill_service.get_bills_by_date_range(
        start_date=date_range.start_date,
        end_date=date_range.end_date
    )

@router.patch("/{bill_id}/mark-paid", response_model=BillResponse)
async def mark_bill_paid(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a bill as paid.
    """
    bill_service = BillService(db)
    bill = await bill_service.mark_bill_paid(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill
