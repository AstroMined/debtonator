from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.response_formatter import with_formatted_response
from src.database.database import get_db
from src.models.accounts import Account
from src.schemas.account_types import AccountCreateUnion, AccountResponseUnion
from src.schemas.accounts import (
    AccountResponse,
    AccountStatementHistoryResponse,
    AccountUpdate,
    AvailableCreditResponse,
)
from src.schemas.balance_reconciliation import (
    BalanceReconciliation,
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from src.schemas.credit_limit_history import (
    AccountCreditLimitHistoryResponse,
    CreditLimitHistoryUpdate,
)
from src.services.accounts import AccountService
from src.services.balance_reconciliation import BalanceReconciliationService

router = APIRouter(tags=["accounts"])


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    from src.repositories.accounts import AccountRepository
    from src.repositories.credit_limit_history import CreditLimitHistoryRepository
    from src.repositories.statement_history import StatementHistoryRepository
    from src.repositories.transaction_history import TransactionHistoryRepository

    # Initialize all required repositories
    account_repo = AccountRepository(db)
    statement_repo = StatementHistoryRepository(db)
    credit_limit_repo = CreditLimitHistoryRepository(db)
    transaction_repo = TransactionHistoryRepository(db)

    # Return properly initialized service
    return AccountService(
        account_repo=account_repo,
        statement_repo=statement_repo,
        credit_limit_repo=credit_limit_repo,
        transaction_repo=transaction_repo,
    )


def get_reconciliation_service(
    db: AsyncSession = Depends(get_db),
) -> BalanceReconciliationService:
    return BalanceReconciliationService(db)


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(db: AsyncSession = Depends(get_db)):
    """Get all accounts"""
    result = await db.execute(select(Account))
    accounts = result.scalars().all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponseUnion)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific account by ID"""
    result = await db.execute(select(Account).filter(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/", response_model=AccountResponseUnion, status_code=201)
async def create_account(
    account: AccountCreateUnion,
    account_service: AccountService = Depends(get_account_service),
):
    """Create a new account of the appropriate type"""
    try:
        return await account_service.create_account(account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{account_id}", response_model=AccountResponseUnion)
async def update_account(
    account_id: int,
    account: AccountUpdate,
    account_service: AccountService = Depends(get_account_service),
):
    """Update an existing account"""
    try:
        updated_account = await account_service.update_account(account_id, account)
        if not updated_account:
            raise HTTPException(status_code=404, detail="Account not found")
        return updated_account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{account_id}")
async def delete_account(
    account_id: int, account_service: AccountService = Depends(get_account_service)
):
    """Delete an account"""
    try:
        deleted = await account_service.delete_account(account_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"message": "Account deleted successfully"}
    except ValueError as e:
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
    account_service: AccountService = Depends(get_account_service),
):
    """Update an account's statement balance and record in history"""
    result = await account_service.update_statement_balance(
        account_id=account_id,
        statement_balance=statement_data.statement_balance,
        statement_date=statement_data.statement_date,
        minimum_payment=statement_data.minimum_payment,
        due_date=statement_data.due_date,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    return result


@router.post("/{account_id}/credit-limit", response_model=AccountResponse)
async def update_credit_limit(
    account_id: int,
    credit_limit_data: CreditLimitHistoryUpdate,
    account_service: AccountService = Depends(get_account_service),
):
    """Update an account's credit limit and record in history"""
    try:
        result = await account_service.update_credit_limit(
            account_id=account_id, credit_limit_data=credit_limit_data
        )
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{account_id}/credit-limit-history",
    response_model=AccountCreditLimitHistoryResponse,
)
async def get_credit_limit_history(
    account_id: int, account_service: AccountService = Depends(get_account_service)
):
    """Get credit limit history for an account"""
    try:
        result = await account_service.get_credit_limit_history(account_id)
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Balance Reconciliation Endpoints


@router.post("/{account_id}/reconcile", response_model=BalanceReconciliation)
async def create_balance_reconciliation(
    account_id: int,
    reconciliation_data: BalanceReconciliationCreate,
    reconciliation_service: BalanceReconciliationService = Depends(
        get_reconciliation_service
    ),
):
    """Create a new balance reconciliation record"""
    if reconciliation_data.account_id != account_id:
        raise HTTPException(
            status_code=400,
            detail="Account ID in path must match account ID in request body",
        )
    try:
        return await reconciliation_service.create_reconciliation(reconciliation_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{account_id}/reconciliations", response_model=List[BalanceReconciliation])
async def get_account_reconciliations(
    account_id: int,
    limit: int = 100,
    offset: int = 0,
    reconciliation_service: BalanceReconciliationService = Depends(
        get_reconciliation_service
    ),
):
    """Get reconciliation history for an account"""
    return await reconciliation_service.get_account_reconciliations(
        account_id, limit, offset
    )


@router.get(
    "/{account_id}/reconciliations/{reconciliation_id}",
    response_model=BalanceReconciliation,
)
async def get_reconciliation(
    account_id: int,
    reconciliation_id: int,
    reconciliation_service: BalanceReconciliationService = Depends(
        get_reconciliation_service
    ),
):
    """Get a specific reconciliation record"""
    reconciliation = await reconciliation_service.get_reconciliation(reconciliation_id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation record not found")
    if reconciliation.account_id != account_id:
        raise HTTPException(
            status_code=404, detail="Reconciliation record not found for this account"
        )
    return reconciliation


@router.patch(
    "/{account_id}/reconciliations/{reconciliation_id}",
    response_model=BalanceReconciliation,
)
async def update_reconciliation(
    account_id: int,
    reconciliation_id: int,
    update_data: BalanceReconciliationUpdate,
    reconciliation_service: BalanceReconciliationService = Depends(
        get_reconciliation_service
    ),
):
    """Update a reconciliation record"""
    reconciliation = await reconciliation_service.get_reconciliation(reconciliation_id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation record not found")
    if reconciliation.account_id != account_id:
        raise HTTPException(
            status_code=404, detail="Reconciliation record not found for this account"
        )

    updated = await reconciliation_service.update_reconciliation(
        reconciliation_id, update_data
    )
    if not updated:
        raise HTTPException(
            status_code=404, detail="Failed to update reconciliation record"
        )
    return updated


@router.delete("/{account_id}/reconciliations/{reconciliation_id}")
async def delete_reconciliation(
    account_id: int,
    reconciliation_id: int,
    reconciliation_service: BalanceReconciliationService = Depends(
        get_reconciliation_service
    ),
):
    """Delete a reconciliation record"""
    reconciliation = await reconciliation_service.get_reconciliation(reconciliation_id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation record not found")
    if reconciliation.account_id != account_id:
        raise HTTPException(
            status_code=404, detail="Reconciliation record not found for this account"
        )

    if await reconciliation_service.delete_reconciliation(reconciliation_id):
        return {"message": "Reconciliation record deleted successfully"}
    raise HTTPException(
        status_code=400, detail="Failed to delete reconciliation record"
    )


@router.get("/{account_id}/available-credit", response_model=AvailableCreditResponse)
@with_formatted_response  # Example of using decorator for decimal precision handling
async def get_available_credit(
    account_id: int, account_service: AccountService = Depends(get_account_service)
):
    """Get real-time available credit calculation for a credit account"""
    try:
        result = await account_service.calculate_available_credit(account_id)
        if not result:
            raise HTTPException(status_code=404, detail="Account not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{account_id}/statement-history", response_model=AccountStatementHistoryResponse
)
async def get_statement_history(
    account_id: int, account_service: AccountService = Depends(get_account_service)
):
    """Get statement balance history for an account"""
    result = await account_service.get_statement_history(account_id)
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    return result
