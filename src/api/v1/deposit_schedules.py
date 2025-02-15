from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.deposit_schedules import (
    DepositSchedule,
    DepositScheduleCreate,
    DepositScheduleUpdate,
)
from src.services.deposit_schedules import DepositScheduleService

router = APIRouter(prefix="/deposit-schedules", tags=["deposit_schedules"])

@router.post("/", response_model=DepositSchedule)
async def create_deposit_schedule(
    schedule: DepositScheduleCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new deposit schedule"""
    service = DepositScheduleService(session)
    success, error, created_schedule = await service.create_deposit_schedule(schedule)
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    return created_schedule

@router.get("/{schedule_id}", response_model=DepositSchedule)
async def get_deposit_schedule(
    schedule_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a deposit schedule by ID"""
    service = DepositScheduleService(session)
    schedule = await service.get_deposit_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Deposit schedule not found")
    
    return schedule

@router.put("/{schedule_id}", response_model=DepositSchedule)
async def update_deposit_schedule(
    schedule_id: int,
    schedule_update: DepositScheduleUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a deposit schedule"""
    service = DepositScheduleService(session)
    success, error, updated_schedule = await service.update_deposit_schedule(
        schedule_id, schedule_update
    )
    
    if not success:
        raise HTTPException(
            status_code=404 if error == "Deposit schedule not found" else 400,
            detail=error
        )
    
    return updated_schedule

@router.delete("/{schedule_id}")
async def delete_deposit_schedule(
    schedule_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Delete a deposit schedule"""
    service = DepositScheduleService(session)
    success, error = await service.delete_deposit_schedule(schedule_id)
    
    if not success:
        raise HTTPException(
            status_code=404 if error == "Deposit schedule not found" else 400,
            detail=error
        )
    
    return {"message": "Deposit schedule deleted successfully"}

@router.get("/", response_model=List[DepositSchedule])
async def list_deposit_schedules(
    income_id: Optional[int] = None,
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    session: AsyncSession = Depends(get_db),
):
    """List deposit schedules with optional filters"""
    service = DepositScheduleService(session)
    schedules = await service.list_deposit_schedules(
        income_id=income_id,
        account_id=account_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
    )
    return schedules

@router.get("/pending/{account_id}", response_model=List[DepositSchedule])
async def get_pending_deposits(
    account_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get pending deposits for an account"""
    service = DepositScheduleService(session)
    schedules = await service.get_pending_deposits(account_id)
    return schedules
