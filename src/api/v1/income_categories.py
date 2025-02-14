from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...schemas.income_categories import (
    IncomeCategory,
    IncomeCategoryCreate,
    IncomeCategoryUpdate,
)
from ...services.income_categories import IncomeCategoryService

router = APIRouter(tags=["income categories"])

@router.post("", response_model=IncomeCategory, status_code=status.HTTP_201_CREATED)
async def create_income_category(
    category: IncomeCategoryCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new income category"""
    service = IncomeCategoryService(session)
    return await service.create_category(category)

@router.get("", response_model=List[IncomeCategory])
async def list_income_categories(
    session: AsyncSession = Depends(get_db),
):
    """List all income categories"""
    service = IncomeCategoryService(session)
    return await service.get_categories()

@router.get("/{category_id}", response_model=IncomeCategory)
async def get_income_category(
    category_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific income category"""
    service = IncomeCategoryService(session)
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income category not found",
        )
    return category

@router.put("/{category_id}", response_model=IncomeCategory)
async def update_income_category(
    category_id: int,
    category: IncomeCategoryUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update an income category"""
    service = IncomeCategoryService(session)
    updated_category = await service.update_category(category_id, category)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income category not found",
        )
    return updated_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income_category(
    category_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Delete an income category"""
    service = IncomeCategoryService(session)
    if not await service.delete_category(category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income category not found",
        )
