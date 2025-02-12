from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.database import get_db
from ...models.accounts import Account
from pydantic import BaseModel
from ...schemas.accounts import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountStatementHistoryResponse,
)
from ...schemas.credit_limits import (
    CreditLimitUpdate,
    AccountCreditLimitHistoryResponse,
)
from ...services.accounts import AccountService

router = APIRouter(tags=["accounts"])

def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(db)

@router.get("/", response_model=List[AccountResponse])
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

@router.post("/", response_model=AccountResponse, status_code=201)
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

@router.patch("/{account_id}", response_model=AccountResponse)
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

class StatementUpdate(BaseModel):
    """Schema for updating statement balance"""
    statement_date: date
    statement_balance: Decimal
    minimum_payment: Optional[Decimal] = None
    due_date: Optional[date] = None

@router.post("/{account_id}/statement", response_model=AccountResponse)
async def update_statement_balance(
    account_id: int,
    statement_data: StatementUpdate,
    account_service: AccountService = Depends(get_account_service)
):
    """Update an account's statement balance and record in history"""
    result = await account_service.update_statement_balance(
        account_id=account_id,
        statement_balance=statement_data.statement_balance,
        statement_date=statement_data.statement_date,
        minimum_payment=statement_data.minimum_payment,
        due_date=statement_data.due_date
    )
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    return result

@router.post("/{account_id}/credit-limit", response_model=AccountResponse)
async def update_credit_limit(
    account_id: int,
    credit_limit_data: CreditLimitUpdate,
    account_service: AccountService = Depends(get_account_service)
):
    """Update an account's credit limit and record in history"""
    try:
        result = await account_service.update_credit_limit(
            account_id=account_id,
            credit_limit_data=credit_limit_data
        )
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{account_id}/credit-limit-history", response_model=AccountCreditLimitHistoryResponse)
async def get_credit_limit_history(
    account_id: int,
    account_service: AccountService = Depends(get_account_service)
):
    """Get credit limit history for an account"""
    try:
        result = await account_service.get_credit_limit_history(account_id)
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{account_id}/statement-history", response_model=AccountStatementHistoryResponse)
async def get_statement_history(
    account_id: int,
    account_service: AccountService = Depends(get_account_service)
):
    """Get statement balance history for an account"""
    result = await account_service.get_statement_history(account_id)
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    return result
