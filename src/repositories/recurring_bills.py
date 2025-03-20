"""
Recurring bills repository implementation.

This module provides a repository for RecurringBill model CRUD operations and specialized
recurring bill-related queries.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal

from sqlalchemy import select, and_, or_, desc, extract, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.recurring_bills import RecurringBill
from src.models.liabilities import Liability
from src.repositories.base import BaseRepository


class RecurringBillRepository(BaseRepository[RecurringBill, int]):
    """
    Repository for RecurringBill model operations.
    
    This repository handles CRUD operations for recurring bills and provides specialized
    queries for recurring bill-related functionality.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, RecurringBill)
    
    async def get_by_name(self, name: str) -> Optional[RecurringBill]:
        """
        Get recurring bill by name.
        
        Args:
            name (str): Recurring bill name to search for
            
        Returns:
            Optional[RecurringBill]: Recurring bill with matching name or None
        """
        result = await self.session.execute(
            select(RecurringBill).where(RecurringBill.bill_name == name)
        )
        return result.scalars().first()
    
    async def get_active_bills(self) -> List[RecurringBill]:
        """
        Get all active recurring bills.
        
        Returns:
            List[RecurringBill]: List of active recurring bills
        """
        result = await self.session.execute(
            select(RecurringBill)
            .where(RecurringBill.active == True)
            .order_by(RecurringBill.day_of_month, RecurringBill.bill_name)
        )
        return result.scalars().all()
    
    async def get_by_day_of_month(self, day: int) -> List[RecurringBill]:
        """
        Get recurring bills due on a specific day of the month.
        
        Args:
            day (int): Day of the month (1-31)
            
        Returns:
            List[RecurringBill]: List of recurring bills due on the specified day
        """
        result = await self.session.execute(
            select(RecurringBill)
            .where(and_(
                RecurringBill.day_of_month == day,
                RecurringBill.active == True
            ))
            .order_by(RecurringBill.bill_name)
        )
        return result.scalars().all()
    
    async def get_with_liabilities(self, bill_id: int) -> Optional[RecurringBill]:
        """
        Get recurring bill with its generated liabilities.
        
        Args:
            bill_id (int): Recurring bill ID
            
        Returns:
            Optional[RecurringBill]: Recurring bill with loaded liabilities or None
        """
        result = await self.session.execute(
            select(RecurringBill)
            .options(selectinload(RecurringBill.liabilities))
            .where(RecurringBill.id == bill_id)
        )
        return result.scalars().first()
    
    async def get_with_account(self, bill_id: int) -> Optional[RecurringBill]:
        """
        Get recurring bill with its associated account.
        
        Args:
            bill_id (int): Recurring bill ID
            
        Returns:
            Optional[RecurringBill]: Recurring bill with loaded account or None
        """
        result = await self.session.execute(
            select(RecurringBill)
            .options(joinedload(RecurringBill.account))
            .where(RecurringBill.id == bill_id)
        )
        return result.scalars().first()
    
    async def get_with_category(self, bill_id: int) -> Optional[RecurringBill]:
        """
        Get recurring bill with its associated category.
        
        Args:
            bill_id (int): Recurring bill ID
            
        Returns:
            Optional[RecurringBill]: Recurring bill with loaded category or None
        """
        result = await self.session.execute(
            select(RecurringBill)
            .options(joinedload(RecurringBill.category))
            .where(RecurringBill.id == bill_id)
        )
        return result.scalars().first()
    
    async def get_with_relationships(
        self, 
        bill_id: int,
        include_account: bool = False,
        include_category: bool = False,
        include_liabilities: bool = False
    ) -> Optional[RecurringBill]:
        """
        Get recurring bill with specified relationships loaded.
        
        Args:
            bill_id (int): Recurring bill ID
            include_account (bool): Load account relationship
            include_category (bool): Load category relationship
            include_liabilities (bool): Load generated liabilities
            
        Returns:
            Optional[RecurringBill]: Recurring bill with loaded relationships or None
        """
        query = select(RecurringBill).where(RecurringBill.id == bill_id)
        
        if include_account:
            query = query.options(joinedload(RecurringBill.account))
        
        if include_category:
            query = query.options(joinedload(RecurringBill.category))
            
        if include_liabilities:
            query = query.options(selectinload(RecurringBill.liabilities))
        
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_account_id(self, account_id: int) -> List[RecurringBill]:
        """
        Get recurring bills associated with an account.
        
        Args:
            account_id (int): Account ID
            
        Returns:
            List[RecurringBill]: List of recurring bills for the account
        """
        result = await self.session.execute(
            select(RecurringBill)
            .where(RecurringBill.account_id == account_id)
            .order_by(RecurringBill.day_of_month, RecurringBill.bill_name)
        )
        return result.scalars().all()
    
    async def get_by_category_id(self, category_id: int) -> List[RecurringBill]:
        """
        Get recurring bills associated with a category.
        
        Args:
            category_id (int): Category ID
            
        Returns:
            List[RecurringBill]: List of recurring bills for the category
        """
        result = await self.session.execute(
            select(RecurringBill)
            .where(RecurringBill.category_id == category_id)
            .order_by(RecurringBill.day_of_month, RecurringBill.bill_name)
        )
        return result.scalars().all()
    
    async def find_bills_with_auto_pay(self) -> List[RecurringBill]:
        """
        Find recurring bills with auto-pay enabled.
        
        Returns:
            List[RecurringBill]: List of recurring bills with auto-pay
        """
        result = await self.session.execute(
            select(RecurringBill)
            .where(and_(
                RecurringBill.auto_pay == True,
                RecurringBill.active == True
            ))
            .order_by(RecurringBill.day_of_month, RecurringBill.bill_name)
        )
        return result.scalars().all()
    
    async def toggle_active(self, bill_id: int) -> Optional[RecurringBill]:
        """
        Toggle active status of a recurring bill.
        
        Args:
            bill_id (int): Recurring bill ID
            
        Returns:
            Optional[RecurringBill]: Updated recurring bill or None if not found
        """
        bill = await self.get(bill_id)
        if not bill:
            return None
        
        bill.active = not bill.active
        await self.session.flush()
        await self.session.refresh(bill)
        return bill
    
    async def toggle_auto_pay(self, bill_id: int) -> Optional[RecurringBill]:
        """
        Toggle auto-pay status of a recurring bill.
        
        Args:
            bill_id (int): Recurring bill ID
            
        Returns:
            Optional[RecurringBill]: Updated recurring bill or None if not found
        """
        bill = await self.get(bill_id)
        if not bill:
            return None
        
        bill.auto_pay = not bill.auto_pay
        await self.session.flush()
        await self.session.refresh(bill)
        return bill
    
    async def update_day_of_month(
        self, 
        bill_id: int, 
        day_of_month: int
    ) -> Optional[RecurringBill]:
        """
        Update the day of month for a recurring bill.
        
        Args:
            bill_id (int): Recurring bill ID
            day_of_month (int): New day of month (1-31)
            
        Returns:
            Optional[RecurringBill]: Updated recurring bill or None if not found
        """
        # Validate day of month
        if day_of_month < 1 or day_of_month > 31:
            raise ValueError("Day of month must be between 1 and 31")
        
        return await self.update(bill_id, {"day_of_month": day_of_month})
    
    async def get_monthly_total(self) -> Decimal:
        """
        Get total amount of all active recurring bills.
        
        Returns:
            Decimal: Total monthly amount
        """
        result = await self.session.execute(
            select(func.sum(RecurringBill.amount))
            .where(RecurringBill.active == True)
        )
        total = result.scalar_one_or_none()
        return total or Decimal("0")
    
    async def check_liability_exists(
        self, 
        recurring_bill_id: int, 
        due_date: datetime
    ) -> bool:
        """
        Check if a liability already exists for this recurring bill and due date.
        
        Args:
            recurring_bill_id (int): Recurring bill ID
            due_date (datetime): Due date to check
            
        Returns:
            bool: True if liability exists, False otherwise
        """
        # Check if any liability exists for this recurring bill with the same due date
        # We need to check date part only, ignoring time
        result = await self.session.execute(
            select(func.count())
            .select_from(Liability)
            .where(and_(
                Liability.recurring_bill_id == recurring_bill_id,
                func.date(Liability.due_date) == due_date.date()
            ))
        )
        count = result.scalar_one()
        return count > 0
    
    async def get_upcoming_bills(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[RecurringBill, date]]:
        """
        Get upcoming recurring bills within a date range.
        
        Args:
            start_date (date): Start date (inclusive)
            end_date (date): End date (inclusive)
            
        Returns:
            List[Tuple[RecurringBill, date]]: List of (recurring bill, due date) tuples
        """
        # Get all active recurring bills
        result = await self.session.execute(
            select(RecurringBill)
            .where(RecurringBill.active == True)
            .order_by(RecurringBill.day_of_month, RecurringBill.bill_name)
        )
        bills = result.scalars().all()
        
        # Calculate due dates within the range
        upcoming_bills = []
        for bill in bills:
            # Get all possible due dates within the range
            current_date = start_date
            while current_date <= end_date:
                # If the day of month is valid for this month
                if bill.day_of_month <= 28 or bill.day_of_month <= current_date.replace(day=28).day:
                    # Create a date with the bill's day of month
                    try:
                        due_date = current_date.replace(day=bill.day_of_month)
                        # If the due date is within our range
                        if start_date <= due_date <= end_date:
                            upcoming_bills.append((bill, due_date))
                    except ValueError:
                        # Handle invalid day for month (e.g., February 30)
                        pass
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # Sort by due date, then bill name
        upcoming_bills.sort(key=lambda x: (x[1], x[0].bill_name))
        return upcoming_bills
