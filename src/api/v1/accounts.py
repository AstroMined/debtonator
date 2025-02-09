from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...models.accounts import Account
from ...schemas.accounts import AccountCreate, AccountUpdate, AccountResponse

router = APIRouter(tags=["accounts"])

@router.get("", response_model=List[AccountResponse])
async def get_accounts(
    db: AsyncSession = Depends(get_db)
):
    """Get all accounts"""
    result = await db.execute(select(Account))
    accounts = result.scalars().all()
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific account by ID"""
    result = await db.execute(select(Account).filter(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new account"""
    db_account = Account(**account.model_dump())
    db_account.update_available_credit()
    db.add(db_account)
    try:
        await db.commit()
        await db.refresh(db_account)
        return db_account
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account: AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing account"""
    result = await db.execute(select(Account).filter(Account.id == account_id))
    db_account = result.scalar_one_or_none()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = account.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_account, key, value)
    
    db_account.update_available_credit()
    try:
        await db.commit()
        await db.refresh(db_account)
        return db_account
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an account"""
    result = await db.execute(select(Account).filter(Account.id == account_id))
    db_account = result.scalar_one_or_none()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        await db.delete(db_account)
        await db.commit()
        return {"message": "Account deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
