from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...models.liabilities import Liability
from ...schemas.bill_splits import (BillSplitCreate, BillSplitResponse,
                                    BillSplitSuggestionResponse,
                                    BillSplitUpdate, BulkOperationResult,
                                    BulkSplitOperation, HistoricalAnalysis)
from ...services.bill_splits import BillSplitService

router = APIRouter(tags=["bill-splits"])


@router.post(
    "/bulk",
    response_model=BulkOperationResult,
    description="Process a bulk operation for bill splits",
)
async def process_bulk_operation(
    operation: BulkSplitOperation, db: AsyncSession = Depends(get_db)
):
    """Process a bulk operation for bill splits (create/update)"""
    service = BillSplitService(db)
    try:
        result = await service.process_bulk_operation(operation)
        if result.success:
            await db.commit()
        else:
            await db.rollback()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bulk/validate",
    response_model=BulkOperationResult,
    description="Validate a bulk operation without executing it",
)
async def validate_bulk_operation(
    operation: BulkSplitOperation, db: AsyncSession = Depends(get_db)
):
    """Validate a bulk operation without executing it"""
    service = BillSplitService(db)
    try:
        result = await service.validate_bulk_operation(operation)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/analysis/{bill_id}",
    response_model=HistoricalAnalysis,
    description="Get comprehensive historical analysis of bill splits",
)
async def get_historical_analysis(bill_id: int, db: AsyncSession = Depends(get_db)):
    """Get comprehensive historical analysis of bill splits patterns"""
    service = BillSplitService(db)
    try:
        analysis = await service.analyze_historical_patterns(bill_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Suggestions endpoint
@router.get("/suggestions/{bill_id}", response_model=BillSplitSuggestionResponse)
async def get_split_suggestions(bill_id: int, db: AsyncSession = Depends(get_db)):
    """Get split suggestions for a bill based on historical patterns and available funds"""
    service = BillSplitService(db)
    try:
        suggestions = await service.suggest_splits(bill_id)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# More specific routes first
@router.post("/", response_model=BillSplitResponse, status_code=201)
async def create_bill_split(split: BillSplitCreate, db: AsyncSession = Depends(get_db)):
    """Create a new bill split"""
    service = BillSplitService(db)
    try:
        # Verify liability exists
        liability_result = await db.execute(
            select(Liability).where(Liability.id == split.bill_id)
        )
        if not liability_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail=f"Liability with id {split.bill_id} not found"
            )

        db_split = await service.create_bill_split(split)
        await db.commit()
        return db_split
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/account/{account_id}", response_model=List[BillSplitResponse])
async def get_account_splits(account_id: int, db: AsyncSession = Depends(get_db)):
    """Get all splits for a specific account"""
    service = BillSplitService(db)
    splits = await service.get_account_splits(account_id)
    return splits


@router.delete("/bill/{bill_id}")
async def delete_bill_splits(bill_id: int, db: AsyncSession = Depends(get_db)):
    """Delete all splits for a specific bill"""
    service = BillSplitService(db)
    try:
        # Verify liability exists
        liability_result = await db.execute(
            select(Liability).where(Liability.id == bill_id)
        )
        if not liability_result.scalar_one_or_none():
            return {"message": "No splits found"}

        await service.delete_bill_splits(bill_id)
        await db.commit()
        return {"message": "Bill splits deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Generic routes last
@router.get("/{bill_id}", response_model=List[BillSplitResponse])
async def get_bill_splits(bill_id: int, db: AsyncSession = Depends(get_db)):
    """Get all splits for a specific bill"""
    service = BillSplitService(db)
    splits = await service.get_bill_splits(bill_id)
    return splits


@router.put("/{split_id}", response_model=BillSplitResponse)
async def update_bill_split(
    split_id: int, split: BillSplitUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing bill split"""
    service = BillSplitService(db)
    try:
        db_split = await service.update_bill_split(split_id, split)
        if not db_split:
            raise HTTPException(status_code=404, detail="Bill split not found")
        await db.commit()
        return db_split
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{split_id}")
async def delete_bill_split(split_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a bill split"""
    service = BillSplitService(db)
    try:
        success = await service.delete_bill_split(split_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bill split not found")
        await db.commit()
        return {"message": "Bill split deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
