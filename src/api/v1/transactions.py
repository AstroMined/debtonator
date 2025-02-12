from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.transactions import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TransactionList
)
from src.services.transactions import TransactionService

router = APIRouter(prefix="/accounts/{account_id}/transactions", tags=["transactions"])

@router.post("", response_model=Transaction)
async def create_transaction(
    account_id: int,
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db)
) -> Transaction:
    """Create a new transaction for an account"""
    try:
        service = TransactionService(db)
        transaction = await service.create_transaction(account_id, transaction_data)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=TransactionList)
async def list_transactions(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
) -> TransactionList:
    """List transactions for an account with optional date filtering"""
    service = TransactionService(db)
    transactions, total = await service.get_account_transactions(
        account_id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    return TransactionList(items=transactions, total=total)

@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    account_id: int,
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
) -> Transaction:
    """Get a specific transaction"""
    service = TransactionService(db)
    transaction = await service.get_transaction(transaction_id)
    if not transaction or transaction.account_id != account_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(
    account_id: int,
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db)
) -> Transaction:
    """Update a transaction"""
    service = TransactionService(db)
    transaction = await service.update_transaction(transaction_id, transaction_data)
    if not transaction or transaction.account_id != account_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    account_id: int,
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a transaction"""
    service = TransactionService(db)
    # First verify the transaction exists and belongs to the account
    transaction = await service.get_transaction(transaction_id)
    if not transaction or transaction.account_id != account_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    success = await service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete transaction")
