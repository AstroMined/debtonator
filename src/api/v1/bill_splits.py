from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...models.bills import Bill
from ...services.bill_splits import BillSplitService
from ...schemas.bill_splits import (
    BillSplitCreate,
    BillSplitUpdate,
    BillSplitResponse
)

router = APIRouter(tags=["bill-splits"])

# More specific routes first
@router.post("/", response_model=BillSplitResponse, status_code=201)
async def create_bill_split(
    split: BillSplitCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new bill split"""
    service = BillSplitService(db)
    try:
        # Verify bill exists
        bill_result = await db.execute(
            select(Bill).where(Bill.id == split.bill_id)
        )
        if not bill_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Bill with id {split.bill_id} not found")

        db_split = await service.create_bill_split(split)
        await db.commit()
        return db_split
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/account/{account_id}", response_model=List[BillSplitResponse])
async def get_account_splits(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all splits for a specific account"""
    service = BillSplitService(db)
    splits = await service.get_account_splits(account_id)
    return splits

@router.delete("/bill/{bill_id}")
async def delete_bill_splits(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete all splits for a specific bill"""
    service = BillSplitService(db)
    try:
        # Verify bill exists
        bill_result = await db.execute(
            select(Bill).where(Bill.id == bill_id)
        )
        if not bill_result.scalar_one_or_none():
            return {"message": "No splits found"}

        await service.delete_bill_splits(bill_id)
        await db.commit()
        return {"message": "Bill splits deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Generic routes last
@router.get("/{bill_id}", response_model=List[BillSplitResponse])
async def get_bill_splits(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all splits for a specific bill"""
    service = BillSplitService(db)
    splits = await service.get_bill_splits(bill_id)
    return splits

@router.put("/{split_id}", response_model=BillSplitResponse)
async def update_bill_split(
    split_id: int,
    split: BillSplitUpdate,
    db: AsyncSession = Depends(get_db)
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
async def delete_bill_split(
    split_id: int,
    db: AsyncSession = Depends(get_db)
):
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
