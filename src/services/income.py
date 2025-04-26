from decimal import Decimal
from typing import Any, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.repositories.accounts import AccountRepository
from src.repositories.income import IncomeRepository
from src.repositories.income_categories import IncomeCategoryRepository
from src.schemas.income import IncomeCreate, IncomeFilters, IncomeUpdate
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.decimal_precision import DecimalPrecision


class IncomeService(BaseService):
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

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize IncomeService with required dependencies.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)

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
        amount = Decimal("0.00")
        if not income.deposited:
            # Use round_for_calculation for internal computation
            amount = DecimalPrecision.round_for_calculation(income.amount)

        # Return display-ready amount
        return DecimalPrecision.round_for_display(amount)

    async def _update_undeposited_amount(self, income: Income) -> None:
        """
        Update the undeposited_amount field of an income record.

        This private method handles the update of the calculated field,
        maintaining the business logic in the service layer.

        Args:
            income: The income record to update
        """
        income.undeposited_amount = await self._calculate_undeposited_amount(income)

    async def validate_income_create(
        self, income_data: IncomeCreate
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an income creation request.

        Business rules validated:
        - Account must exist
        - Category must exist (if provided)

        Args:
            income_data: The income data to validate

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if failed
        """
        # Get repositories
        account_repo = await self._get_repository(AccountRepository)
        
        # Verify account exists
        account = await account_repo.get(income_data.account_id)
        if not account:
            return False, f"Account with ID {income_data.account_id} not found"

        # Verify category exists if provided
        if income_data.category_id:
            category_repo = await self._get_repository(IncomeCategoryRepository)
            category = await category_repo.get(income_data.category_id)
            if not category:
                return False, f"Category with ID {income_data.category_id} not found"

        return True, None

    async def validate_income_update(
        self, income_id: int, income_data: IncomeUpdate
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an income update request.

        Business rules validated:
        - Income record must exist
        - Account must exist (if changing)
        - Category must exist (if changing)

        Args:
            income_id: The ID of the income to update
            income_data: The updated income data

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if failed
        """
        # Get repositories
        income_repo = await self._get_repository(IncomeRepository)
        
        # Verify income exists
        income = await income_repo.get_with_relationships(income_id)
        if not income:
            return False, f"Income with ID {income_id} not found"

        # Verify new account exists if changing
        update_data = income_data.dict(exclude_unset=True)
        if "account_id" in update_data:
            account_repo = await self._get_repository(AccountRepository)
            account = await account_repo.get(update_data["account_id"])
            if not account:
                return False, f"Account with ID {update_data['account_id']} not found"

        # Verify new category exists if changing
        if "category_id" in update_data and update_data["category_id"] is not None:
            category_repo = await self._get_repository(IncomeCategoryRepository)
            category = await category_repo.get(update_data["category_id"])
            if not category:
                return False, f"Category with ID {update_data['category_id']} not found"

        return True, None

    async def create(self, income_data: IncomeCreate) -> Income:
        """
        Create a new income entry.

        Handles the creation of a new income record, including:
        - Setting up relationships
        - Calculating initial undeposited amount
        - Updating account balance if auto-deposited

        Args:
            income_data: The income data to create

        Returns:
            Income: The created income record with relationships loaded

        Raises:
            HTTPException: If validation fails
        """
        # Validate first
        valid, error_message = await self.validate_income_create(income_data)
        if not valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Get repository
        income_repo = await self._get_repository(IncomeRepository)

        # Create new income record
        income = Income(
            date=income_data.date,
            source=income_data.source,
            # Use DecimalPrecision to ensure proper rounding for monetary values
            amount=DecimalPrecision.round_for_display(income_data.amount),
            deposited=income_data.deposited,
            account_id=income_data.account_id,
            category_id=income_data.category_id,
        )

        # Calculate initial undeposited amount
        await self._update_undeposited_amount(income)
        
        # Use repository to create the income record
        income = await income_repo.create(income)
        
        # Return the income record with relationships loaded
        return await income_repo.get_with_relationships(income.id)

    async def get(self, income_id: int) -> Optional[Income]:
        """
        Get an income entry by ID with relationships loaded.

        Args:
            income_id: The ID of the income record to get

        Returns:
            Optional[Income]: The income record or None if not found
        """
        income_repo = await self._get_repository(IncomeRepository)
        return await income_repo.get_with_relationships(income_id)

    async def update(
        self, income_id: int, income_data: IncomeUpdate
    ) -> Optional[Income]:
        """
        Update an income entry.

        Handles the update of an income record, including:
        - Recalculating undeposited amount if deposit status changes
        - Updating account balance if deposit status changes
        - Maintaining relationship integrity

        Args:
            income_id: The ID of the income to update
            income_data: The updated income data

        Returns:
            Optional[Income]: The updated income record or None if not found

        Raises:
            HTTPException: If validation fails
        """
        # Validate first
        valid, error_message = await self.validate_income_update(income_id, income_data)
        if not valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Get repositories
        income_repo = await self._get_repository(IncomeRepository)
        account_repo = await self._get_repository(AccountRepository)

        # Get the income record with relationships
        income = await income_repo.get_with_relationships(income_id)
        if not income:
            return None

        # Store original values
        original_amount = income.amount
        original_deposited = income.deposited

        # Update fields
        update_data = income_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(income, field, value)

        # Recalculate undeposited amount if needed
        if "deposited" in update_data or "amount" in update_data:
            await self._update_undeposited_amount(income)

        # If amount changed or deposit status changed, update account balance
        if income.deposited and (
            "amount" in update_data
            or ("deposited" in update_data and not original_deposited)
        ):
            # Get the account with relationships
            account = await account_repo.get_with_relationships(income.account_id)

            # If this is a new deposit
            if not original_deposited:
                # Use 4 decimal places for internal calculation
                amount = DecimalPrecision.round_for_calculation(income.amount)
                current_balance = DecimalPrecision.round_for_calculation(
                    account.available_balance
                )
                new_balance = DecimalPrecision.round_for_calculation(
                    current_balance + amount
                )

                # Round to 2 decimal places for storage
                account.available_balance = DecimalPrecision.round_for_display(
                    new_balance
                )
            # If this is an amount update on an existing deposit
            elif "amount" in update_data:
                # Remove old amount and add new amount with proper precision
                old_amount = DecimalPrecision.round_for_calculation(original_amount)
                new_amount = DecimalPrecision.round_for_calculation(income.amount)
                current_balance = DecimalPrecision.round_for_calculation(
                    account.available_balance
                )

                # Calculate new balance with 4 decimal precision
                new_balance = DecimalPrecision.round_for_calculation(
                    current_balance - old_amount + new_amount
                )

                # Round to 2 decimal places for storage
                account.available_balance = DecimalPrecision.round_for_display(
                    new_balance
                )
                
            # Update the account in the database
            await account_repo.update(account.id, {"available_balance": account.available_balance})

        # Update the income record in the database
        income = await income_repo.update(income_id, update_data)
        
        # Return the updated income record with relationships loaded
        return await income_repo.get_with_relationships(income_id)

    async def delete(self, income_id: int) -> bool:
        """
        Delete an income entry.

        Args:
            income_id: The ID of the income record to delete

        Returns:
            bool: True if deleted, False if not found
        """
        income_repo = await self._get_repository(IncomeRepository)
        
        # Verify income exists
        income = await income_repo.get(income_id)
        if not income:
            return False
            
        # Delete the income record
        return await income_repo.delete(income_id)

    async def list(
        self, filters: IncomeFilters, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Income], int]:
        """
        List income entries with filtering.

        Args:
            filters: Filter parameters for income records
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple[List[Income], int]: Tuple of (income_records, total_count)
        """
        income_repo = await self._get_repository(IncomeRepository)
        
        # Use repository's filter method to get income records
        return await income_repo.get_income_with_filters(
            skip=skip,
            limit=limit,
            start_date=filters.start_date,
            end_date=filters.end_date,
            source=filters.source,
            deposited=filters.deposited,
            min_amount=filters.min_amount,
            max_amount=filters.max_amount,
            account_id=getattr(filters, "account_id", None)
        )

    async def get_undeposited(self) -> List[Income]:
        """
        Get all undeposited income entries.

        Returns:
            List[Income]: List of undeposited income records
        """
        income_repo = await self._get_repository(IncomeRepository)
        return await income_repo.get_undeposited_income()

    async def validate_deposit_status_change(
        self, income_id: int, deposit: bool
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a deposit status change.

        Business rules validated:
        - Income record must exist
        - If marking as deposited, account must exist

        Args:
            income_id: The ID of the income record
            deposit: Whether to mark as deposited

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if failed
        """
        # Get repositories
        income_repo = await self._get_repository(IncomeRepository)
        
        # Verify income exists
        income = await income_repo.get_with_relationships(income_id)
        if not income:
            return False, f"Income with ID {income_id} not found"

        # If already in the requested state, no need to change
        if income.deposited == deposit:
            return True, None

        # If marking as deposited, verify account exists
        if deposit:
            account_repo = await self._get_repository(AccountRepository)
            account = await account_repo.get(income.account_id)
            if not account:
                return False, f"Account with ID {income.account_id} not found"

        return True, None

    async def update_account_balance_from_income(
        self, income_id: int
    ) -> Optional[Income]:
        """
        Update account balance when income is deposited.

        This method encapsulates the business logic for updating an account's
        balance when an income is marked as deposited. It ensures atomicity
        and proper state management.

        Args:
            income_id: ID of the income entry to process

        Returns:
            Optional[Income]: The updated income object or None if not found
        """
        # Get repositories
        income_repo = await self._get_repository(IncomeRepository)
        account_repo = await self._get_repository(AccountRepository)
        
        # Get the income entry with relationships
        income = await income_repo.get_with_relationships(income_id)
        if not income:
            return None

        # Skip if already deposited
        if income.deposited:
            return income

        # Get the target account with relationships
        account = await account_repo.get_with_relationships(income.account_id)

        # Update account balance with proper decimal precision
        income_amount = DecimalPrecision.round_for_calculation(income.amount)
        account_balance = DecimalPrecision.round_for_calculation(
            account.available_balance
        )
        new_balance = DecimalPrecision.round_for_calculation(
            account_balance + income_amount
        )

        # Round to 2 decimal places for storage
        new_balance_display = DecimalPrecision.round_for_display(new_balance)
        
        # Update the account balance
        await account_repo.update(account.id, {"available_balance": new_balance_display})

        # Mark income as deposited using repository method
        income = await income_repo.mark_as_deposited(income_id)
        
        # Return the updated income record with relationships loaded
        return await income_repo.get_with_relationships(income_id)

    async def mark_as_deposited(self, income_id: int) -> Optional[Income]:
        """
        Mark an income entry as deposited and update account balance.

        Args:
            income_id: The ID of the income record to mark as deposited

        Returns:
            Optional[Income]: The updated income record or None if not found

        Raises:
            HTTPException: If validation fails
        """
        # Validate first
        valid, error_message = await self.validate_deposit_status_change(
            income_id, True
        )
        if not valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Update the account balance using the dedicated method
        return await self.update_account_balance_from_income(income_id)

    async def get_total_undeposited(self) -> Decimal:
        """
        Get total amount of undeposited income.

        Returns:
            Decimal: Total undeposited amount
        """
        income_repo = await self._get_repository(IncomeRepository)
        total = await income_repo.get_total_undeposited()
        # Ensure proper decimal precision for the total
        return DecimalPrecision.round_for_display(total)

    async def get_total_undeposited_by_account(self, account_id: int) -> Decimal:
        """
        Get total undeposited income for a specific account.

        This method calculates the total undeposited amount for a specific account.

        Args:
            account_id: ID of the account to calculate total for

        Returns:
            Decimal: Total undeposited amount for the account
        """
        income_repo = await self._get_repository(IncomeRepository)
        total = await income_repo.get_total_undeposited_by_account(account_id)
        # Ensure proper decimal precision for the total
        return DecimalPrecision.round_for_display(total)

    async def get_income_by_account(self, account_id: int) -> List[Income]:
        """
        Get all income entries for a specific account.

        Args:
            account_id: ID of the account to get income for

        Returns:
            List[Income]: List of income entries for the account
        """
        income_repo = await self._get_repository(IncomeRepository)
        return await income_repo.get_income_by_account(account_id)


# Convenience functions that use the service


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

    This is a convenience function that uses the IncomeService.
    For repeated operations, prefer using the IncomeService directly.

    Args:
        db: The database session
        account_id: ID of the account to get income for

    Returns:
        List[Income]: List of income entries for the account
    """
    service = IncomeService(db)
    return await service.get_income_by_account(account_id)


async def get_total_undeposited_income(db: AsyncSession, account_id: int) -> Decimal:
    """
    Get total undeposited income for a specific account.

    This is a convenience function that uses the IncomeService.
    For repeated operations, prefer using the IncomeService directly.

    Args:
        db: The database session
        account_id: ID of the account to calculate total for

    Returns:
        Decimal: Total undeposited amount for the account
    """
    service = IncomeService(db)
    return await service.get_total_undeposited_by_account(account_id)


async def update_account_balance_from_income(db: AsyncSession, income_id: int) -> None:
    """
    Update account balance when income is deposited.

    This is a convenience function that uses the IncomeService.
    For repeated operations, prefer using the IncomeService directly.

    Args:
        db: The database session
        income_id: ID of the income entry to process
    """
    service = IncomeService(db)
    await service.update_account_balance_from_income(income_id)
