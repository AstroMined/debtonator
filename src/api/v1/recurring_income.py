from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.income import (
    GenerateIncomeRequest,
    IncomeResponse,
    RecurringIncomeCreate,
    RecurringIncomeResponse,
    RecurringIncomeUpdate,
)
from src.services.recurring_income import RecurringIncomeService

router = APIRouter(prefix="/recurring-income", tags=["recurring-income"])


@router.post("/", response_model=RecurringIncomeResponse)
async def create_recurring_income(
    income_data: RecurringIncomeCreate, db: AsyncSession = Depends(get_db)
) -> RecurringIncomeResponse:
    """Create a new recurring income template."""
    service = RecurringIncomeService(db)
    return await service.create(income_data)


@router.get("/{recurring_income_id}", response_model=RecurringIncomeResponse)
async def get_recurring_income(
    recurring_income_id: int, db: AsyncSession = Depends(get_db)
) -> RecurringIncomeResponse:
    """Get a recurring income template by ID."""
    service = RecurringIncomeService(db)
    recurring_income = await service.get(recurring_income_id)
    if not recurring_income:
        raise HTTPException(status_code=404, detail="Recurring income not found")
    return recurring_income


@router.put("/{recurring_income_id}", response_model=RecurringIncomeResponse)
async def update_recurring_income(
    recurring_income_id: int,
    income_data: RecurringIncomeUpdate,
    db: AsyncSession = Depends(get_db),
) -> RecurringIncomeResponse:
    """Update a recurring income template."""
    service = RecurringIncomeService(db)
    recurring_income = await service.update(recurring_income_id, income_data)
    if not recurring_income:
        raise HTTPException(status_code=404, detail="Recurring income not found")
    return recurring_income


@router.delete("/{recurring_income_id}")
async def delete_recurring_income(
    recurring_income_id: int, db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a recurring income template."""
    service = RecurringIncomeService(db)
    success = await service.delete(recurring_income_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recurring income not found")
    return {"status": "success", "message": "Recurring income deleted"}


@router.get("/", response_model=List[RecurringIncomeResponse])
async def list_recurring_income(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[RecurringIncomeResponse]:
    """List recurring income templates with pagination."""
    service = RecurringIncomeService(db)
    items, _ = await service.list(skip=skip, limit=limit)
    return items


@router.post("/generate", response_model=List[IncomeResponse])
async def generate_income(
    request: GenerateIncomeRequest, db: AsyncSession = Depends(get_db)
) -> List[IncomeResponse]:
    """Generate income entries from recurring templates for a specific month/year."""
    service = RecurringIncomeService(db)
    return await service.generate_income(request)
