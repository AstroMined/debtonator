from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.payment_schedules import (PaymentSchedule,
                                           PaymentScheduleCreate)
from src.services.payment_schedules import PaymentScheduleService

router = APIRouter(prefix="/payment-schedules", tags=["payment_schedules"])


@router.post("/", response_model=PaymentSchedule)
async def create_payment_schedule(
    schedule: PaymentScheduleCreate, session: AsyncSession = Depends(get_db)
) -> PaymentSchedule:
    """Create a new payment schedule"""
    try:
        service = PaymentScheduleService(session)
        return await service.create_schedule(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{schedule_id}", response_model=PaymentSchedule)
async def get_payment_schedule(
    schedule_id: int, session: AsyncSession = Depends(get_db)
) -> PaymentSchedule:
    """Get a payment schedule by ID"""
    service = PaymentScheduleService(session)
    schedule = await service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Payment schedule not found")
    return schedule


@router.get("/by-date-range/", response_model=List[PaymentSchedule])
async def get_schedules_by_date_range(
    start_date: date,
    end_date: date,
    include_processed: bool = False,
    session: AsyncSession = Depends(get_db),
) -> List[PaymentSchedule]:
    """Get payment schedules within a date range"""
    service = PaymentScheduleService(session)
    return await service.get_schedules_by_date_range(
        start_date=start_date, end_date=end_date, include_processed=include_processed
    )


@router.get("/by-liability/{liability_id}", response_model=List[PaymentSchedule])
async def get_schedules_by_liability(
    liability_id: int,
    include_processed: bool = False,
    session: AsyncSession = Depends(get_db),
) -> List[PaymentSchedule]:
    """Get payment schedules for a specific liability"""
    service = PaymentScheduleService(session)
    return await service.get_schedules_by_liability(
        liability_id=liability_id, include_processed=include_processed
    )


@router.post("/{schedule_id}/process", response_model=PaymentSchedule)
async def process_schedule(
    schedule_id: int, session: AsyncSession = Depends(get_db)
) -> PaymentSchedule:
    """Process a payment schedule"""
    try:
        service = PaymentScheduleService(session)
        return await service.process_schedule(schedule_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int, session: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a payment schedule"""
    try:
        service = PaymentScheduleService(session)
        success = await service.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Payment schedule not found")
        return {"message": "Payment schedule deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/process-due", response_model=List[PaymentSchedule])
async def process_due_schedules(
    session: AsyncSession = Depends(get_db),
) -> List[PaymentSchedule]:
    """Process all auto-process schedules that are due today"""
    service = PaymentScheduleService(session)
    return await service.process_due_schedules()
