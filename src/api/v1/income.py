from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_session
from ...schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeResponse,
    IncomeList,
    IncomeFilters
)
from ...services.income import IncomeService

router = APIRouter(prefix="/income", tags=["income"])

@router.post("/", response_model=IncomeResponse, status_code=201)
async def create_income(
    income_data: IncomeCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new income record"""
    service = IncomeService(session)
    income = await service.create(income_data)
    return income

@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(
    income_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get an income record by ID"""
    service = IncomeService(session)
    income = await service.get(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income

@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: int,
    income_data: IncomeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an income record"""
    service = IncomeService(session)
    income = await service.update(income_id, income_data)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income

@router.delete("/{income_id}", status_code=204)
async def delete_income(
    income_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete an income record"""
    service = IncomeService(session)
    success = await service.delete(income_id)
    if not success:
        raise HTTPException(status_code=404, detail="Income record not found")

@router.get("/", response_model=IncomeList)
async def list_income(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    source: Optional[str] = None,
    deposited: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List income records with optional filtering"""
    filters = IncomeFilters(
        start_date=start_date,
        end_date=end_date,
        source=source,
        deposited=deposited,
        min_amount=min_amount,
        max_amount=max_amount
    )
    service = IncomeService(session)
    items, total = await service.list(filters, skip, limit)
    return IncomeList(items=items, total=total)

@router.get("/undeposited/", response_model=list[IncomeResponse])
async def get_undeposited_income(
    session: AsyncSession = Depends(get_session)
):
    """Get all undeposited income records"""
    service = IncomeService(session)
    return await service.get_undeposited()

@router.put("/{income_id}/deposit", response_model=IncomeResponse)
async def mark_income_as_deposited(
    income_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Mark an income record as deposited"""
    service = IncomeService(session)
    income = await service.mark_as_deposited(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income

@router.get("/undeposited/total/")
async def get_total_undeposited(
    session: AsyncSession = Depends(get_session)
):
    """Get total amount of undeposited income"""
    service = IncomeService(session)
    total = await service.get_total_undeposited()
    return {"total": total}
