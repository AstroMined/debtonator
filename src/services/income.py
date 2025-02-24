from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.income import Income
from src.models.accounts import Account
from src.schemas.income import IncomeCreate, IncomeUpdate, IncomeFilters

class IncomeService:
    """
    Service class for handling Income-related business logic.
    
    This service is responsible for:
    - Managing income records
    - Calculating undeposited amounts
    - Handling deposit status changes
    - Updating account balances
    - Managing income relationships
    
    All business logic and validations are centralized here, keeping the
    Income model as a pure data structure (ADR-012).
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _calculate_undeposited_amount(self, income: Income) -> Decimal:
        """
        Calculate the undeposited amount for an income record.
        
        This private method encapsulates the business logic for determining
        undeposited amounts, which was previously in the Income model.
        
        Args:
            income: The income record to calculate for
            
        Returns:
            Decimal: The undeposited amount (full amount if not deposited, 0 if deposited)
        """
        return income.amount if not income.deposited else Decimal("0.00")

    async def _update_undeposited_amount(self, income: Income) -> None:
        """
        Update the undeposited_amount field of an income record.
        
        This private method handles the update of the calculated field,
        maintaining the business logic in the service layer.
        
        Args:
            income: The income record to update
        """
        income.undeposited_amount = await self._calculate_undeposited_amount(income)
    
    async def create(self, income_data: IncomeCreate) -> Income:
        """
        Create a new income entry.
        
        Handles the creation of a new income record, including:
        - Setting up relationships
        - Calculating initial undeposited amount
        - Updating account balance if auto-deposited
        """
        # Verify account exists
        stmt = (
            select(Account)
            .options(joinedload(Account.income))
            .where(Account.id == income_data.account_id)
        )
        result = await self.db.execute(stmt)
        account = result.unique().scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create new income record
        income = Income(
            date=income_data.date,
            source=income_data.source,
            amount=income_data.amount,
            deposited=income_data.deposited,
            account_id=income_data.account_id,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC"))
        )
        
        # Calculate initial undeposited amount
        await self._update_undeposited_amount(income)
        self.db.add(income)
        await self.db.commit()

        # Fetch fresh copy with relationships
        stmt = (
            select(Income)
            .options(joinedload(Income.account))
            .filter(Income.id == income.id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()
    
    async def get(self, income_id: int) -> Optional[Income]:
        """Get an income entry by ID."""
        stmt = (
            select(Income)
            .options(joinedload(Income.account))
            .where(Income.id == income_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    async def update(self, income_id: int, income_data: IncomeUpdate) -> Optional[Income]:
        """
        Update an income entry.
        
        Handles the update of an income record, including:
        - Recalculating undeposited amount if deposit status changes
        - Updating account balance if deposit status changes
        - Maintaining relationship integrity
        """
        stmt = (
            select(Income)
            .options(joinedload(Income.account))
            .where(Income.id == income_id)
        )
        result = await self.db.execute(stmt)
        income = result.unique().scalar_one_or_none()
        if not income:
            return None

        # Store original values
        original_amount = income.amount
        original_deposited = income.deposited

        # Update fields
        update_data = income_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(income, field, value)
        
        income.updated_at = datetime.now(ZoneInfo("UTC"))
        
        # Recalculate undeposited amount if needed
        if 'deposited' in update_data or 'amount' in update_data:
            await self._update_undeposited_amount(income)

        # If amount changed or deposit status changed, update account balance
        if income.deposited and (
            'amount' in update_data or 
            ('deposited' in update_data and not original_deposited)
        ):
            # Get the account
            stmt = (
                select(Account)
                .options(joinedload(Account.income))
                .where(Account.id == income.account_id)
            )
            result = await self.db.execute(stmt)
            account = result.unique().scalar_one()

            # If this is a new deposit
            if not original_deposited:
                account.available_balance += income.amount
            # If this is an amount update on an existing deposit
            elif 'amount' in update_data:
                # Remove old amount and add new amount
                account.available_balance -= original_amount
                account.available_balance += income.amount

        await self.db.commit()

        # Fetch fresh copy with relationships
        stmt = (
            select(Income)
            .options(joinedload(Income.account))
            .filter(Income.id == income_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()
    
    async def delete(self, income_id: int) -> bool:
        """Delete an income entry."""
        income = await self.get(income_id)
        if not income:
            return False
        
        await self.db.delete(income)
        await self.db.commit()
        return True
    
    async def list(
        self,
        filters: IncomeFilters,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Income], int]:
        """List income entries with filtering."""
        query = select(Income).options(joinedload(Income.account))
        conditions = []
        
        if filters.start_date:
            conditions.append(Income.date >= filters.start_date)
        if filters.end_date:
            conditions.append(Income.date <= filters.end_date)
        if filters.source:
            conditions.append(Income.source.ilike(f"%{filters.source}%"))
        if filters.deposited is not None:
            conditions.append(Income.deposited == filters.deposited)
        if filters.min_amount:
            conditions.append(Income.amount >= filters.min_amount)
        if filters.max_amount:
            conditions.append(Income.amount <= filters.max_amount)
        if hasattr(filters, 'account_id') and filters.account_id:
            conditions.append(Income.account_id == filters.account_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count (without joins to avoid cartesian product)
        count_query = select(func.count(Income.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()
        
        # Get paginated results (with joins)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def get_undeposited(self) -> List[Income]:
        """Get all undeposited income entries."""
        stmt = (
            select(Income)
            .options(joinedload(Income.account))
            .where(Income.deposited == False)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()
    
    async def mark_as_deposited(self, income_id: int) -> Optional[Income]:
        """Mark an income entry as deposited and update account balance."""
        income = await self.get(income_id)
        if not income:
            return None
        
        await update_account_balance_from_income(self.db, income_id)
        
        # Fetch fresh copy with relationships
        stmt = (
            select(Income)
            .options(joinedload(Income.account))
            .filter(Income.id == income_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()
    
    async def get_total_undeposited(self) -> Decimal:
        """Get total amount of undeposited income."""
        result = await self.db.execute(
            select(func.sum(Income.amount)).where(Income.deposited == False)
        )
        total = result.scalar_one() or Decimal("0.00")
        return total

async def calculate_undeposited_amount(db: AsyncSession, income_id: int) -> Decimal:
    """
    Calculate the undeposited amount for a given income entry.
    
    This is a convenience function that creates a temporary IncomeService
    to perform the calculation. For repeated operations, prefer using
    the IncomeService directly.
    
    Args:
        db: The database session
        income_id: ID of the income entry
        
    Returns:
        Decimal: The undeposited amount
        
    Raises:
        HTTPException: If the income entry is not found
    """
    service = IncomeService(db)
    income = await service.get(income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return await service._calculate_undeposited_amount(income)

async def get_income_by_account(db: AsyncSession, account_id: int) -> List[Income]:
    """
    Get all income entries for a specific account.
    
    This is a convenience function that uses the same query pattern
    as the IncomeService.list method but filtered by account.
    
    Args:
        db: The database session
        account_id: ID of the account to get income for
        
    Returns:
        List[Income]: List of income entries for the account
    """
    stmt = (
        select(Income)
        .options(joinedload(Income.account))
        .where(Income.account_id == account_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalars().all()

async def get_total_undeposited_income(db: AsyncSession, account_id: int) -> Decimal:
    """
    Get total undeposited income for a specific account.
    
    This is a convenience function that calculates the total undeposited
    amount for a specific account. For repeated operations, prefer using
    the IncomeService.
    
    Args:
        db: The database session
        account_id: ID of the account to calculate total for
        
    Returns:
        Decimal: Total undeposited amount for the account
    """
    result = await db.execute(
        select(func.sum(Income.amount))
        .where(and_(
            Income.account_id == account_id,
            Income.deposited == False
        ))
    )
    total = result.scalar_one() or Decimal("0.00")
    return total

async def update_account_balance_from_income(db: AsyncSession, income_id: int) -> None:
    """
    Update account balance when income is deposited.
    
    This function encapsulates the business logic for updating an account's
    balance when an income is marked as deposited. It ensures atomicity
    and proper state management.
    
    Note: This is a convenience function. For repeated operations,
    prefer using the IncomeService.mark_as_deposited method.
    
    Args:
        db: The database session
        income_id: ID of the income entry to process
    """
    # Get the income entry
    stmt = (
        select(Income)
        .options(joinedload(Income.account))
        .where(Income.id == income_id)
    )
    result = await db.execute(stmt)
    income = result.unique().scalar_one()
    
    # Skip if already deposited
    if income.deposited:
        return
    
    # Get the target account
    stmt = (
        select(Account)
        .options(joinedload(Account.income))
        .where(Account.id == income.account_id)
    )
    result = await db.execute(stmt)
    account = result.unique().scalar_one()
    
    # Update account balance
    account.available_balance += income.amount
    
    # Mark income as deposited
    income.deposited = True
    
    await db.commit()
