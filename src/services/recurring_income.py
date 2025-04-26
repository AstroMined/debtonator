"""
RecurringIncome service implementation with ADR-014 Repository Layer Compliance.

This module provides business logic for managing recurring income templates and
generating income entries, following ADR-012 for domain logic and ADR-014 for
repository pattern usage.
"""

from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.recurring_income import RecurringIncome
from src.repositories.accounts import AccountRepository
from src.repositories.income import IncomeRepository
from src.repositories.recurring_income import RecurringIncomeRepository
from src.schemas.recurring_income import (
    GenerateIncomeRequest,
    RecurringIncomeCreate,
    RecurringIncomeUpdate,
)
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import naive_utc_from_date, utc_now


class RecurringIncomeService(BaseService):
    """
    Service for managing recurring income templates and generating income entries.

    This service follows:
    - ADR-012 by handling all business logic related to recurring income
    - ADR-014 by using the repository pattern exclusively for data access
    - ADR-011 by using proper datetime handling utilities

    All repository access is standardized using the BaseService._get_repository method.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize RecurringIncomeService with required dependencies.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)

    def create_income_from_recurring(
        self, recurring_income: RecurringIncome, month: int, year: int
    ) -> Income:
        """
        Create a new Income instance from a recurring income template.

        This method replaces the RecurringIncome.create_income_entry method that
        was moved to the service layer as part of ADR-012 implementation.

        Args:
            recurring_income: The recurring income template
            month: Month number (1-12)
            year: Full year (e.g., 2025)

        Returns:
            Income: New income entry with proper UTC date
        """
        income_entry = Income(
            source=recurring_income.source,
            amount=recurring_income.amount,
            date=naive_utc_from_date(
                year, month, recurring_income.day_of_month
            ),  # Store as naive UTC
            account_id=recurring_income.account_id,
            category_id=recurring_income.category_id,
            deposited=recurring_income.auto_deposit,
            recurring=True,
            recurring_income_id=recurring_income.id,
            category=recurring_income.category,
        )
        return income_entry

    async def create(self, income_data: RecurringIncomeCreate) -> RecurringIncome:
        """
        Create a new recurring income template.

        Args:
            income_data: Data for creating the recurring income

        Returns:
            RecurringIncome: Created recurring income object

        Raises:
            HTTPException: If the account does not exist
        """
        # Verify account exists using AccountRepository
        account_repo = await self._get_repository(AccountRepository)
        account = await account_repo.get(income_data.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Use RecurringIncomeRepository to create the recurring income
        recurring_repo = await self._get_repository(RecurringIncomeRepository)

        # Get the current time using utility functions for ADR-011 compliance
        current_time = utc_now().replace(tzinfo=None)  # Naive UTC for DB

        # Prepare data for creation
        create_data = income_data.dict()
        create_data["created_at"] = current_time
        create_data["updated_at"] = current_time

        # Create recurring income
        return await recurring_repo.create(create_data)

    async def get(self, recurring_income_id: int) -> Optional[RecurringIncome]:
        """
        Get a recurring income template by ID with all relationships loaded.

        Args:
            recurring_income_id: ID of the recurring income to retrieve

        Returns:
            Optional[RecurringIncome]: Retrieved recurring income with all relationships or None
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)
        return await recurring_repo.get_with_relationships(recurring_income_id)

    async def update(
        self, recurring_income_id: int, income_data: RecurringIncomeUpdate
    ) -> Optional[RecurringIncome]:
        """
        Update a recurring income template.

        Args:
            recurring_income_id: ID of the recurring income to update
            income_data: Data for updating the recurring income

        Returns:
            Optional[RecurringIncome]: Updated recurring income or None if not found
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)

        # Check if recurring income exists
        existing = await recurring_repo.get(recurring_income_id)
        if not existing:
            return None

        # Prepare update data
        update_data = income_data.dict(exclude_unset=True)

        # Add updated timestamp
        current_time = utc_now().replace(tzinfo=None)  # Naive UTC for DB
        update_data["updated_at"] = current_time

        # Update recurring income
        return await recurring_repo.update(recurring_income_id, update_data)

    async def delete(self, recurring_income_id: int) -> bool:
        """
        Delete a recurring income template.

        Args:
            recurring_income_id: ID of the recurring income to delete

        Returns:
            bool: True if deleted successfully, False if not found
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)

        # Check if recurring income exists
        existing = await recurring_repo.get(recurring_income_id)
        if not existing:
            return False

        # Delete recurring income
        await recurring_repo.delete(recurring_income_id)
        return True

    async def list(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[RecurringIncome], int]:
        """
        List recurring income templates with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple[List[RecurringIncome], int]: List of recurring incomes and total count
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)

        # Get items with pagination
        items = await recurring_repo.get_multi(skip=skip, limit=limit)

        # Get total count
        total = await recurring_repo.count()

        return items, total

    async def generate_income(self, request: GenerateIncomeRequest) -> List[Income]:
        """
        Generate income entries for a specific month/year from recurring templates.

        Args:
            request: Request containing month and year for income generation

        Returns:
            List[Income]: List of generated income entries
        """
        # Get repositories
        recurring_repo = await self._get_repository(RecurringIncomeRepository)
        income_repo = await self._get_repository(IncomeRepository)

        # Get all active recurring income templates
        templates = await recurring_repo.get_active_income()

        generated_income = []
        for template in templates:
            # Check if income entry already exists for this month/year
            existing_entries = await income_repo.find_by_recurring_and_date(
                template.id, request.month, request.year
            )

            # If no existing entry, create a new one
            if not existing_entries:
                # Create new income entry from template using service method
                income_entry = self.create_income_from_recurring(
                    template, request.month, request.year
                )

                # Create income entry using repository
                created_entry = await income_repo.create(income_entry.__dict__)
                generated_income.append(created_entry)

        return generated_income

    async def toggle_active(self, recurring_id: int) -> Optional[RecurringIncome]:
        """
        Toggle the active status of a recurring income record.

        Args:
            recurring_id: ID of the recurring income to toggle

        Returns:
            Optional[RecurringIncome]: Updated recurring income or None if not found
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)
        return await recurring_repo.toggle_active(recurring_id)

    async def toggle_auto_deposit(self, recurring_id: int) -> Optional[RecurringIncome]:
        """
        Toggle the auto_deposit status of a recurring income record.

        Args:
            recurring_id: ID of the recurring income to toggle

        Returns:
            Optional[RecurringIncome]: Updated recurring income or None if not found
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)
        return await recurring_repo.toggle_auto_deposit(recurring_id)

    async def update_day_of_month(
        self, recurring_id: int, day: int
    ) -> Optional[RecurringIncome]:
        """
        Update the day_of_month for a recurring income record.

        Args:
            recurring_id: ID of the recurring income to update
            day: New day of the month (1-31)

        Returns:
            Optional[RecurringIncome]: Updated recurring income or None if not found

        Raises:
            ValueError: If day is not between 1 and 31
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)
        return await recurring_repo.update_day_of_month(recurring_id, day)

    async def get_upcoming_deposits(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get estimated upcoming deposits based on recurring income records.

        Args:
            days: Number of days to look ahead (default: 30)

        Returns:
            List[Dict[str, Any]]: List of projected income entries
        """
        recurring_repo = await self._get_repository(RecurringIncomeRepository)
        return await recurring_repo.get_upcoming_deposits(days)
