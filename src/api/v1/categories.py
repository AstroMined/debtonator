from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...schemas.categories import Category, CategoryCreate, CategoryUpdate, CategoryWithBills
from ...services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=Category)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
) -> Category:
    """Create a new category"""
    try:
        category_service = CategoryService(db)
        return await category_service.create_category(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Category])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Category]:
    """List all categories with pagination"""
    category_service = CategoryService(db)
    return await category_service.get_categories(skip=skip, limit=limit)

@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
) -> Category:
    """Get a specific category by ID"""
    category_service = CategoryService(db)
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/{category_id}/bills", response_model=CategoryWithBills)
async def get_category_with_bills(
    category_id: int,
    db: AsyncSession = Depends(get_db)
) -> CategoryWithBills:
    """Get a category with its associated bills"""
    category_service = CategoryService(db)
    category = await category_service.get_category_with_bills(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
) -> Category:
    """Update a category"""
    try:
        category_service = CategoryService(db)
        category = await category_service.update_category(category_id, category_update)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a category"""
    try:
        category_service = CategoryService(db)
        success = await category_service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
