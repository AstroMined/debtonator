from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.income import IncomeCreate, IncomeFilters, IncomeResponse, IncomeUpdate
from src.services.income import IncomeService

router = APIRouter()


@router.post("/", response_model=IncomeResponse, status_code=201)
async def create_income(income_data: IncomeCreate, db: AsyncSession = Depends(get_db)):
    """Create a new income record"""
    service = IncomeService(db)
    income = await service.create(income_data)
    return income


@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(income_id: int, db: AsyncSession = Depends(get_db)):
    """Get an income record by ID"""
    service = IncomeService(db)
    income = await service.get(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income


@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: int, income_data: IncomeUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an income record"""
    service = IncomeService(db)
    income = await service.update(income_id, income_data)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income


@router.delete("/{income_id}", status_code=204)
async def delete_income(income_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an income record"""
    service = IncomeService(db)
    success = await service.delete(income_id)
    if not success:
        raise HTTPException(status_code=404, detail="Income record not found")


@router.get("/", response_model=list[IncomeResponse])
async def list_income(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    source: Optional[str] = None,
    deposited: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    account_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List income records with optional filtering"""
    filters = IncomeFilters(
        start_date=start_date,
        end_date=end_date,
        source=source,
        deposited=deposited,
        min_amount=min_amount,
        max_amount=max_amount,
        account_id=account_id,
    )
    service = IncomeService(db)
    items, total = await service.list(filters, skip, limit)
    return items


@router.get("/undeposited", response_model=list[IncomeResponse])
async def get_undeposited_income(db: AsyncSession = Depends(get_db)):
    """Get all undeposited income records"""
    service = IncomeService(db)
    return await service.get_undeposited()


@router.put("/{income_id}/deposit", response_model=IncomeResponse)
async def mark_income_as_deposited(income_id: int, db: AsyncSession = Depends(get_db)):
    """Mark an income record as deposited"""
    service = IncomeService(db)
    income = await service.mark_as_deposited(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income


@router.get("/undeposited/total")
async def get_total_undeposited(db: AsyncSession = Depends(get_db)):
    """Get total amount of undeposited income"""
    service = IncomeService(db)
    total = await service.get_total_undeposited()
    return {"total": total}
