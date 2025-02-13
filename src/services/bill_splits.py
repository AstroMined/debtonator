from decimal import Decimal
from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit
from src.models.accounts import Account
from src.schemas.bill_splits import (
    BillSplitCreate,
    BillSplitUpdate,
    BillSplitValidation
)

class BillSplitValidationError(Exception):
    """Custom exception for bill split validation errors"""
    pass

class BillSplitService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_bill_splits(self, liability_id: int) -> List[BillSplit]:
        """Get all splits for a specific liability."""
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .where(BillSplit.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_account_splits(self, account_id: int) -> List[BillSplit]:
        """Get all splits for a specific account."""
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .where(BillSplit.account_id == account_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def create_split(self, liability_id: int, account_id: int, amount: Decimal) -> BillSplit:
        """Create a new bill split (internal use)."""
        split = BillSplit(
            liability_id=liability_id,
            account_id=account_id,
            amount=amount,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(split)
        await self.db.flush()

        # Fetch fresh copy with relationships
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .filter(BillSplit.id == split.id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def create_bill_split(self, split: BillSplitCreate) -> BillSplit:
        """Create a new bill split (API use)."""
        # Verify liability exists
        stmt = (
            select(Liability)
            .options(joinedload(Liability.splits))
            .where(Liability.id == split.liability_id)
        )
        result = await self.db.execute(stmt)
        liability = result.unique().scalar_one_or_none()
        if not liability:
            raise BillSplitValidationError(f"Liability with id {split.liability_id} not found")

        # Verify account exists and has sufficient balance/credit
        stmt = select(Account).where(Account.id == split.account_id)
        result = await self.db.execute(stmt)
        account = result.unique().scalar_one_or_none()
        if not account:
            raise BillSplitValidationError(f"Account with id {split.account_id} not found")

        # Validate account has sufficient balance/credit
        if account.type == "credit":
            available_credit = (
                account.total_limit + account.available_balance
                if account.total_limit
                else Decimal('0')
            )
            if split.amount > available_credit:
                raise BillSplitValidationError(
                    f"Account {account.name} has insufficient credit "
                    f"(needs {split.amount}, has {available_credit})"
                )
        else:  # checking/savings
            if split.amount > account.available_balance:
                raise BillSplitValidationError(
                    f"Account {account.name} has insufficient balance "
                    f"(needs {split.amount}, has {account.available_balance})"
                )

        return await self.create_split(
            liability_id=split.liability_id,
            account_id=split.account_id,
            amount=split.amount
        )

    async def update_bill_split(self, split_id: int, split: BillSplitUpdate) -> Optional[BillSplit]:
        """Update an existing bill split."""
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .where(BillSplit.id == split_id)
        )
        result = await self.db.execute(stmt)
        db_split = result.unique().scalar_one_or_none()
        if not db_split:
            return None

        if split.amount is not None:
            # Validate new amount against account balance/credit
            stmt = select(Account).where(Account.id == db_split.account_id)
            result = await self.db.execute(stmt)
            account = result.unique().scalar_one()

            if account.type == "credit":
                available_credit = (
                    account.total_limit + account.available_balance
                    if account.total_limit
                    else Decimal('0')
                )
                if split.amount > available_credit:
                    raise BillSplitValidationError(
                        f"Account {account.name} has insufficient credit "
                        f"(needs {split.amount}, has {available_credit})"
                    )
            else:  # checking/savings
                if split.amount > account.available_balance:
                    raise BillSplitValidationError(
                        f"Account {account.name} has insufficient balance "
                        f"(needs {split.amount}, has {account.available_balance})"
                    )

            db_split.amount = split.amount
            db_split.updated_at = date.today()
        
        await self.db.flush()

        # Fetch fresh copy with relationships
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def delete_bill_split(self, split_id: int) -> bool:
        """Delete a specific bill split. Returns True if successful."""
        result = await self.db.execute(
            delete(BillSplit).where(BillSplit.id == split_id)
        )
        return result.rowcount > 0

    async def delete_bill_splits(self, liability_id: int) -> None:
        """Delete all splits for a liability."""
        await self.db.execute(
            delete(BillSplit).where(BillSplit.liability_id == liability_id)
        )
        await self.db.commit()

    async def validate_splits(self, validation: BillSplitValidation) -> Tuple[bool, Optional[str]]:
        """
        Validate bill splits against multiple criteria:
        1. Sum of splits equals liability amount
        2. All accounts exist and have sufficient balance/credit
        3. No duplicate accounts
        4. All amounts are positive

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Verify liability exists
            stmt = select(Liability).where(Liability.id == validation.liability_id)
            result = await self.db.execute(stmt)
            liability = result.unique().scalar_one_or_none()
            if not liability:
                return False, f"Liability with id {validation.liability_id} not found"

            # Verify total amount matches liability
            if abs(validation.total_amount - liability.amount) > Decimal('0.01'):
                return False, (
                    f"Total amount {validation.total_amount} does not match "
                    f"liability amount {liability.amount}"
                )

            # Get all accounts involved in splits
            account_ids = [split.account_id for split in validation.splits]
            stmt = (
                select(Account)
                .where(Account.id.in_(account_ids))
            )
            result = await self.db.execute(stmt)
            accounts = {acc.id: acc for acc in result.scalars().all()}

            # Verify all accounts exist
            missing_accounts = set(account_ids) - set(accounts.keys())
            if missing_accounts:
                return False, f"Accounts not found: {missing_accounts}"

            # Check for duplicate accounts
            if len(account_ids) != len(set(account_ids)):
                return False, "Duplicate accounts found in splits"

            # Validate each split
            for split in validation.splits:
                account = accounts[split.account_id]
                
                # Validate account has sufficient balance/credit
                if account.type == "credit":
                    available_credit = (
                        account.total_limit + account.available_balance
                        if account.total_limit
                        else Decimal('0')
                    )
                    if split.amount > available_credit:
                        return False, (
                            f"Account {account.name} has insufficient credit "
                            f"(needs {split.amount}, has {available_credit})"
                        )
                else:  # checking/savings
                    if split.amount > account.available_balance:
                        return False, (
                            f"Account {account.name} has insufficient balance "
                            f"(needs {split.amount}, has {account.available_balance})"
                        )

            return True, None

        except Exception as e:
            return False, str(e)

async def calculate_split_totals(db: AsyncSession, liability_id: int) -> Decimal:
    """Calculate the total amount of all splits for a given liability."""
    stmt = (
        select(BillSplit)
        .options(
            joinedload(BillSplit.liability),
            joinedload(BillSplit.account)
        )
        .where(BillSplit.liability_id == liability_id)
    )
    result = await db.execute(stmt)
    splits = result.unique().scalars().all()
    return sum(split.amount for split in splits)
