from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.categories import (
    Category,
    CategoryCreate,
    CategoryTree,
    CategoryUpdate,
    CategoryWithBillsResponse,
)
from src.services.categories import CategoryError, CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=Category)
async def create_category(
    category: CategoryCreate, db: AsyncSession = Depends(get_db)
) -> Category:
    """Create a new category"""
    try:
        category_service = CategoryService(db)
        db_category = await category_service.create_category(category)

        # Set full_path using service method
        db_category.full_path = await category_service.get_full_path(db_category)

        return db_category
    except (ValueError, CategoryError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Category])
async def list_categories(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[Category]:
    """List all categories with pagination"""
    category_service = CategoryService(db)
    categories = await category_service.get_categories(skip=skip, limit=limit)

    # Set full_path for each category
    for category in categories:
        category.full_path = await category_service.get_full_path(category)

    return categories


@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: int, db: AsyncSession = Depends(get_db)
) -> Category:
    """Get a specific category by ID"""
    category_service = CategoryService(db)
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Set full_path using service method
    category.full_path = await category_service.get_full_path(category)

    return category


@router.get("/{category_id}/bills", response_model=CategoryWithBillsResponse)
async def get_category_with_bills(
    category_id: int, db: AsyncSession = Depends(get_db)
) -> CategoryWithBillsResponse:
    """Get a category with its associated bills"""
    category_service = CategoryService(db)
    
    # Use the new composition method instead of direct database mapping
    category_response = await category_service.compose_category_with_bills(category_id)
    
    if not category_response:
        raise HTTPException(status_code=404, detail="Category not found")

    return category_response


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> Category:
    """Update a category"""
    try:
        category_service = CategoryService(db)
        category = await category_service.update_category(category_id, category_update)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Set full_path using service method
        category.full_path = await category_service.get_full_path(category)

        return category
    except (ValueError, CategoryError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    """Delete a category"""
    try:
        category_service = CategoryService(db)
        success = await category_service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except (ValueError, CategoryError) as e:
        raise HTTPException(status_code=400, detail=str(e))
