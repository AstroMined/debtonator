from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account as AccountModel
from src.models.statement_history import StatementHistory
from src.schemas.accounts import (
    AccountCreate,
    AccountUpdate,
    AccountInDB,
    StatementBalanceHistory,
    AccountStatementHistoryResponse
)
from src.schemas.credit_limits import (
    CreditLimitHistoryCreate,
    CreditLimitUpdate,
    AccountCreditLimitHistoryResponse
)
from src.models.credit_limit_history import CreditLimitHistory

class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_account(self, account_data: AccountCreate) -> AccountInDB:
        """Create a new account"""
        db_account = AccountModel(**account_data.model_dump())
        self.session.add(db_account)
        await self.session.commit()
        await self.session.refresh(db_account)
        return AccountInDB.model_validate(db_account)

    async def get_account(self, account_id: int) -> Optional[AccountInDB]:
        """Get an account by ID"""
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        return AccountInDB.model_validate(db_account) if db_account else None

    async def update_account(
        self, account_id: int, account_data: AccountUpdate
    ) -> Optional[AccountInDB]:
        """Update an account"""
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        if not db_account:
            return None

        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_account, field, value)

        await self.session.commit()
        await self.session.refresh(db_account)
        return AccountInDB.model_validate(db_account)

    async def delete_account(self, account_id: int) -> bool:
        """Delete an account"""
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        if not db_account:
            return False

        await self.session.delete(db_account)
        await self.session.commit()
        return True

    async def list_accounts(self) -> List[AccountInDB]:
        """List all accounts"""
        result = await self.session.execute(select(AccountModel))
        accounts = result.scalars().all()
        return [AccountInDB.model_validate(account) for account in accounts]

    async def update_statement_balance(
        self,
        account_id: int,
        statement_balance: Decimal,
        statement_date: date,
        minimum_payment: Optional[Decimal] = None,
        due_date: Optional[date] = None
    ) -> Optional[AccountInDB]:
        """Update an account's statement balance and related information"""
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        if not db_account:
            return None

        # Update current statement info
        db_account.last_statement_balance = statement_balance
        db_account.last_statement_date = statement_date
        
        # Create statement history entry
        statement_history = StatementHistory(
            account_id=account_id,
            statement_date=statement_date,
            statement_balance=statement_balance,
            minimum_payment=minimum_payment,
            due_date=due_date
        )
        self.session.add(statement_history)
        
        await self.session.commit()
        await self.session.refresh(db_account)
        return AccountInDB.model_validate(db_account)

    async def update_credit_limit(
        self,
        account_id: int,
        credit_limit_data: CreditLimitUpdate
    ) -> Optional[AccountInDB]:
        """Update an account's credit limit and record in history"""
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        if not db_account:
            return None

        if db_account.type != "credit":
            raise ValueError("Credit limit can only be set for credit accounts")

        # Update account's total limit
        db_account.total_limit = credit_limit_data.credit_limit
        db_account.update_available_credit()

        # Create credit limit history entry
        history_entry = CreditLimitHistory(
            account_id=account_id,
            credit_limit=credit_limit_data.credit_limit,
            effective_date=credit_limit_data.effective_date,
            reason=credit_limit_data.reason
        )
        self.session.add(history_entry)

        await self.session.commit()
        await self.session.refresh(db_account)
        return AccountInDB.model_validate(db_account)

    async def get_credit_limit_history(
        self,
        account_id: int
    ) -> Optional[AccountCreditLimitHistoryResponse]:
        """Get credit limit history for an account"""
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        if not db_account:
            return None

        if db_account.type != "credit":
            raise ValueError("Credit limit history only available for credit accounts")

        # Get credit limit history ordered by effective date descending
        history_result = await self.session.execute(
            select(CreditLimitHistory)
            .where(CreditLimitHistory.account_id == account_id)
            .order_by(desc(CreditLimitHistory.effective_date))
        )
        history_records = history_result.scalars().all()

        return AccountCreditLimitHistoryResponse(
            account_id=db_account.id,
            account_name=db_account.name,
            current_credit_limit=db_account.total_limit or Decimal(0),
            credit_limit_history=history_records
        )

    async def get_statement_history(
        self, account_id: int
    ) -> Optional[AccountStatementHistoryResponse]:
        """Get statement balance history for an account"""
        # Get account
        result = await self.session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        db_account = result.scalar_one_or_none()
        if not db_account:
            return None

        # Get statement history ordered by date descending
        history_result = await self.session.execute(
            select(StatementHistory)
            .where(StatementHistory.account_id == account_id)
            .order_by(desc(StatementHistory.statement_date))
        )
        history_records = history_result.scalars().all()

        statement_history = [
            StatementBalanceHistory(
                statement_date=record.statement_date,
                statement_balance=record.statement_balance,
                minimum_payment=record.minimum_payment,
                due_date=record.due_date
            )
            for record in history_records
        ]

        return AccountStatementHistoryResponse(
            account_id=db_account.id,
            account_name=db_account.name,
            statement_history=statement_history
        )
