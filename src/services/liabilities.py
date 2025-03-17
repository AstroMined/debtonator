from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from src.core.decimal_precision import DecimalPrecision
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.liabilities import Liability
from src.models.payments import Payment
from src.models.accounts import Account
from src.models.categories import Category
from src.models.base_model import naive_utc_now
from src.schemas.liabilities import (
    LiabilityCreate, 
    LiabilityUpdate, 
    AutoPayUpdate,
    AutoPaySettings
)

class LiabilityService:
    """
    Service class for handling Liability-related business logic.
    
    This service is responsible for:
    - Managing liabilities (bills)
    - Handling auto-pay configuration
    - Validating liability operations
    - Managing liability relationships
    
    All business logic and validations are centralized here, keeping the
    Liability model as a pure data structure (ADR-012).
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_liability_create(self, liability_data: LiabilityCreate) -> Tuple[bool, Optional[str]]:
        """
        Validate a liability creation request.
        
        Business rules validated:
        - Category must exist
        - Primary account must exist
        - Due date must be valid
        
        Args:
            liability_data: The liability data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if failed
        """
        # Verify category exists
        category = await self._get_category(liability_data.category_id)
        if not category:
            return False, f"Category with ID {liability_data.category_id} not found"
        
        # Verify account exists
        account = await self._get_account(liability_data.primary_account_id)
        if not account:
            return False, f"Account with ID {liability_data.primary_account_id} not found"
        
        # Additional validations can be added here
        
        return True, None
    
    async def validate_liability_update(
        self, liability_id: int, liability_data: LiabilityUpdate
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a liability update request.
        
        Business rules validated:
        - Liability must exist
        - Category must exist (if changing)
        - Primary account must exist (if changing)
        
        Args:
            liability_id: The ID of the liability to update
            liability_data: The updated liability data
            
        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if failed
        """
        # Verify liability exists
        liability = await self.get_liability(liability_id)
        if not liability:
            return False, f"Liability with ID {liability_id} not found"
        
        # Extract update data
        update_data = liability_data.model_dump(exclude_unset=True)
        
        # Verify new category exists if changing
        if 'category_id' in update_data:
            category = await self._get_category(update_data['category_id'])
            if not category:
                return False, f"Category with ID {update_data['category_id']} not found"
        
        # Verify new primary account exists if changing
        if 'primary_account_id' in update_data:
            account = await self._get_account(update_data['primary_account_id'])
            if not account:
                return False, f"Account with ID {update_data['primary_account_id']} not found"
        
        return True, None
    
    async def validate_auto_pay_update(
        self, liability_id: int, auto_pay_data: AutoPayUpdate
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an auto-pay update request.
        
        Business rules validated:
        - Liability must exist
        - Settings must be valid if provided
        
        Args:
            liability_id: The ID of the liability to update
            auto_pay_data: The auto-pay update data
            
        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if failed
        """
        # Verify liability exists
        liability = await self.get_liability(liability_id)
        if not liability:
            return False, f"Liability with ID {liability_id} not found"
        
        # Validate settings if provided
        if auto_pay_data.settings:
            # Add any specific validation for auto-pay settings here
            pass
        
        return True, None
    
    async def _get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID."""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def _get_account(self, account_id: int) -> Optional[Account]:
        """Get an account by ID."""
        result = await self.db.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_liabilities(self, skip: int = 0, limit: int = 100) -> List[Liability]:
        """
        Get a list of liabilities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Liability]: List of liabilities
        """
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .offset(skip)
            .limit(limit)
            .order_by(Liability.due_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_liability(self, liability_id: int) -> Optional[Liability]:
        """
        Get a liability by ID.
        
        Args:
            liability_id: ID of the liability
            
        Returns:
            Optional[Liability]: The liability if found, None otherwise
        """
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_liabilities_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Liability]:
        """
        Get liabilities due within a date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            List[Liability]: List of liabilities due within the range
        """
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.due_date.between(start_date, end_date))
            .order_by(Liability.due_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_unpaid_liabilities(self) -> List[Liability]:
        """
        Get all unpaid liabilities.
        
        Returns:
            List[Liability]: List of unpaid liabilities
        """
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(~Liability.payments.any())  # No associated payments
            .order_by(Liability.due_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def create_liability(self, liability_create: LiabilityCreate) -> Liability:
        """
        Create a new liability.
        
        Args:
            liability_create: Liability creation data
            
        Returns:
            Liability: The created liability
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate first
        valid, error_message = await self.validate_liability_create(liability_create)
        if not valid:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=error_message)
        
        # Create liability
        db_liability = Liability(
            name=liability_create.name,
            # Ensure proper decimal precision for the amount
            amount=DecimalPrecision.round_for_display(liability_create.amount),
            due_date=liability_create.due_date,
            description=liability_create.description,
            category_id=liability_create.category_id,
            recurring=liability_create.recurring,
            recurrence_pattern=liability_create.recurrence_pattern,
            primary_account_id=liability_create.primary_account_id
        )
        
        self.db.add(db_liability)
        await self.db.commit()

        # Fetch fresh copy with relationships
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.id == db_liability.id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def update_liability(
        self, liability_id: int, liability_update: LiabilityUpdate
    ) -> Optional[Liability]:
        """
        Update an existing liability.
        
        Args:
            liability_id: ID of the liability to update
            liability_update: Liability update data
            
        Returns:
            Optional[Liability]: The updated liability if found, None otherwise
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate first
        valid, error_message = await self.validate_liability_update(liability_id, liability_update)
        if not valid:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=error_message)
        
        # Get liability
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        # Update fields
        update_data = liability_update.model_dump(exclude_unset=True)
        
        # Special handling for decimal values
        if 'amount' in update_data:
            update_data['amount'] = DecimalPrecision.round_for_display(update_data['amount'])
            
        for key, value in update_data.items():
            setattr(db_liability, key, value)

        await self.db.commit()

        # Fetch fresh copy with relationships
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def delete_liability(self, liability_id: int) -> bool:
        """
        Delete a liability.
        
        Args:
            liability_id: ID of the liability to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return False
        
        # The cascade will handle deleting associated payments and payment sources
        await self.db.delete(db_liability)
        await self.db.commit()
        return True

    async def is_paid(self, liability_id: int) -> bool:
        """
        Check if a liability has any associated payments.
        
        Args:
            liability_id: ID of the liability to check
            
        Returns:
            bool: True if paid, False otherwise
        """
        stmt = (
            select(Payment)
            .options(
                joinedload(Payment.sources),
                joinedload(Payment.liability)
            )
            .filter(Payment.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().first() is not None

    async def update_auto_pay(self, liability_id: int, auto_pay_update: AutoPayUpdate) -> Optional[Liability]:
        """
        Update auto-pay settings for a liability.
        
        Args:
            liability_id: ID of the liability to update
            auto_pay_update: Auto-pay update data
            
        Returns:
            Optional[Liability]: The updated liability if found, None otherwise
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate first
        valid, error_message = await self.validate_auto_pay_update(liability_id, auto_pay_update)
        if not valid:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=error_message)
        
        # Get liability
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        # Update auto-pay state and settings
        db_liability.auto_pay_enabled = auto_pay_update.enabled
        db_liability.auto_pay = auto_pay_update.enabled  # Sync auto_pay with enabled state
        
        # Update settings if provided
        if auto_pay_update.settings:
            # Convert settings to dict and handle Decimal serialization
            settings_dict = auto_pay_update.settings.model_dump(exclude_none=True)
            if 'minimum_balance_required' in settings_dict:
                # Format the minimum balance with 2 decimal places
            min_balance = settings_dict['minimum_balance_required']
            settings_dict['minimum_balance_required'] = str(DecimalPrecision.round_for_display(min_balance))
            db_liability.auto_pay_settings = settings_dict
        elif not auto_pay_update.enabled:
            # Clear settings when disabling auto-pay
            db_liability.auto_pay_settings = None

        await self.db.commit()
        await self.db.refresh(db_liability)  # Ensure we have latest data
        return db_liability

    async def get_auto_pay_candidates(self, days_ahead: int = 7) -> List[Liability]:
        """
        Get liabilities that are candidates for auto-pay processing.
        
        Args:
            days_ahead: Number of days ahead to look for candidates
            
        Returns:
            List[Liability]: List of auto-pay candidates
        """
        end_date = date.today() + timedelta(days=days_ahead)
        
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(
                and_(
                    Liability.auto_pay == True,
                    Liability.auto_pay_enabled == True,
                    Liability.paid == False,
                    Liability.due_date <= end_date
                )
            )
            .order_by(Liability.due_date.asc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def process_auto_pay(self, liability_id: int) -> bool:
        """
        Process auto-pay for a specific liability.
        
        Args:
            liability_id: ID of the liability to process
            
        Returns:
            bool: True if processed successfully, False otherwise
        """
        db_liability = await self.get_liability(liability_id)
        if not db_liability or not db_liability.auto_pay_enabled:
            return False

        try:
            # Update last attempt timestamp
            db_liability.last_auto_pay_attempt = naive_utc_now()
            
            # TODO: Implement actual payment processing logic here
            # This would involve:
            # 1. Checking account balances
            # 2. Creating payment record
            # 3. Processing payment through payment service
            # 4. Updating liability status
            
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False

    async def disable_auto_pay(self, liability_id: int) -> Optional[Liability]:
        """
        Disable auto-pay for a liability.
        
        Args:
            liability_id: ID of the liability to update
            
        Returns:
            Optional[Liability]: The updated liability if found, None otherwise
        """
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        db_liability.auto_pay = False
        db_liability.auto_pay_enabled = False
        db_liability.auto_pay_settings = None
        
        await self.db.commit()
        await self.db.refresh(db_liability)  # Ensure we have latest data
        return db_liability

    async def get_auto_pay_status(self, liability_id: int) -> Optional[Dict]:
        """
        Get auto-pay status and settings for a liability.
        
        Args:
            liability_id: ID of the liability to check
            
        Returns:
            Optional[Dict]: Auto-pay status info if found, None otherwise
        """
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        return {
            "auto_pay": db_liability.auto_pay,
            "enabled": db_liability.auto_pay_enabled,
            "settings": db_liability.auto_pay_settings,
            "last_attempt": db_liability.last_auto_pay_attempt
        }
