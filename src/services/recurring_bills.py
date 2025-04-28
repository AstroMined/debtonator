from datetime import date, datetime
from typing import Any, List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.liabilities import Liability
from src.models.recurring_bills import RecurringBill
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.recurring_bills import RecurringBillRepository
from src.schemas.recurring_bills import RecurringBillCreate, RecurringBillUpdate
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import naive_utc_from_date
from src.utils.decimal_precision import DecimalPrecision


class RecurringBillService(BaseService):
    """
    Service for managing recurring bills and generating liabilities.

    This service handles operations related to recurring bills, including creation,
    update, deletion, and generation of liabilities based on recurring bill templates.

    Attributes:
        _session: SQLAlchemy async session
        _feature_flag_service: Optional feature flag service
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the recurring bill service.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def get_recurring_bills(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[RecurringBill]:
        """
        Get all recurring bills with optional filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            active_only: If True, return only active recurring bills

        Returns:
            List of recurring bill objects with loaded relationships
        """
        # Get repository
        repo = await self._get_repository(RecurringBillRepository)

        if active_only:
            # Use repository's specialized method for active bills
            bills = await repo.get_active_bills()
            # Apply skip and limit
            return bills[skip : skip + limit]
        else:
            # Use get_multi for all bills with filters
            return await repo.get_multi(skip=skip, limit=limit, filters=None)

    async def get_recurring_bill(
        self, recurring_bill_id: int
    ) -> Optional[RecurringBill]:
        """
        Get a specific recurring bill by ID with relationships loaded.

        Args:
            recurring_bill_id: ID of the recurring bill to retrieve

        Returns:
            Recurring bill with loaded relationships or None if not found
        """
        # Get repository
        repo = await self._get_repository(RecurringBillRepository)

        # Use specialized method to get bill with relationships
        return await repo.get_with_relationships(
            recurring_bill_id, include_account=True, include_liabilities=True
        )

    async def create_recurring_bill(
        self, recurring_bill_create: RecurringBillCreate
    ) -> RecurringBill:
        """
        Create a new recurring bill.

        Args:
            recurring_bill_create: Schema with recurring bill data

        Returns:
            Created recurring bill instance

        Raises:
            HTTPException: If the account doesn't exist
        """
        # Get repositories
        account_repo = await self._get_repository(AccountRepository)
        recurring_bill_repo = await self._get_repository(RecurringBillRepository)

        # Verify account exists
        account = await account_repo.get(recurring_bill_create.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Prepare data with proper decimal precision
        bill_data = recurring_bill_create.model_dump()
        bill_data["amount"] = DecimalPrecision.round_for_display(
            recurring_bill_create.amount
        )

        # Use repository to create the bill
        db_recurring_bill = await recurring_bill_repo.create(bill_data)

        return db_recurring_bill

    async def update_recurring_bill(
        self, recurring_bill_id: int, recurring_bill_update: RecurringBillUpdate
    ) -> Optional[RecurringBill]:
        """
        Update an existing recurring bill.

        Args:
            recurring_bill_id: ID of the recurring bill to update
            recurring_bill_update: Schema with fields to update

        Returns:
            Updated recurring bill or None if not found
        """
        # Get repository
        repo = await self._get_repository(RecurringBillRepository)

        # Verify bill exists
        db_recurring_bill = await self.get_recurring_bill(recurring_bill_id)
        if not db_recurring_bill:
            return None

        # Prepare update data with proper decimal precision
        update_data = recurring_bill_update.model_dump(exclude_unset=True)

        # Apply proper decimal precision for amount if present
        if "amount" in update_data:
            update_data["amount"] = DecimalPrecision.round_for_display(
                update_data["amount"]
            )

        # Use repository to update
        return await repo.update(recurring_bill_id, update_data)

    async def delete_recurring_bill(self, recurring_bill_id: int) -> bool:
        """
        Delete a recurring bill and its generated liabilities.

        Args:
            recurring_bill_id: ID of the recurring bill to delete

        Returns:
            True if deleted successfully, False if not found
        """
        # Get repository
        repo = await self._get_repository(RecurringBillRepository)

        # Verify bill exists
        db_recurring_bill = await self.get_recurring_bill(recurring_bill_id)
        if not db_recurring_bill:
            return False

        # Use repository to delete
        return await repo.delete(recurring_bill_id)

    def create_liability_from_recurring(
        self, recurring_bill: RecurringBill, month: str, year: int
    ) -> Liability:
        """
        Create a new Liability instance from a recurring bill template.

        This method replaces the RecurringBill.create_liability method that
        was moved to the service layer as part of ADR-012 implementation.

        Args:
            recurring_bill: The recurring bill template
            month: Month number as string (1-12)
            year: Full year (e.g., 2025)

        Returns:
            Liability: New liability instance with proper UTC due date
        """
        # Create due date using proper ADR-011 datetime compliance
        due_date = naive_utc_from_date(year, int(month), recurring_bill.day_of_month)

        # Create liability with appropriate fields
        liability = Liability(
            name=recurring_bill.bill_name,
            # Ensure proper decimal precision for monetary values
            amount=DecimalPrecision.round_for_display(recurring_bill.amount),
            due_date=due_date,
            primary_account_id=recurring_bill.account_id,
            category_id=recurring_bill.category_id,
            auto_pay=recurring_bill.auto_pay,
            recurring=True,
            recurring_bill_id=recurring_bill.id,
            category=recurring_bill.category,  # Set the relationship directly
        )
        return liability

    async def generate_bills(
        self, recurring_bill_id: int, month: int, year: int
    ) -> List[Liability]:
        """
        Generate liabilities for a recurring bill pattern.

        Args:
            recurring_bill_id: ID of the recurring bill template
            month: Month (1-12) to generate bills for
            year: Year to generate bills for

        Returns:
            List of generated liability instances (empty if already exists)
        """
        # Get repositories
        recurring_bill_repo = await self._get_repository(RecurringBillRepository)
        liability_repo = await self._get_repository(LiabilityRepository)

        # Get recurring bill with relationships
        db_recurring_bill = await recurring_bill_repo.get_with_relationships(
            recurring_bill_id, include_category=True
        )

        if not db_recurring_bill or not db_recurring_bill.active:
            return []

        # Check if bills already exist for this month/year using repository method
        # Create the due date for checking
        check_date = date(year, month, db_recurring_bill.day_of_month)
        # Convert to datetime for consistent comparison
        check_datetime = datetime.combine(check_date, datetime.min.time())

        # Use repository to check if liability already exists
        already_exists = await recurring_bill_repo.check_liability_exists(
            recurring_bill_id, check_datetime
        )

        if already_exists:
            return []  # Bills already exist for this period

        # Create new liability using service method instead of model method
        liability = self.create_liability_from_recurring(
            db_recurring_bill, str(month), year
        )

        # Use repository to create liability
        created_liability = await liability_repo.create(liability.__dict__)

        return [created_liability]

    async def generate_bills_for_month(
        self, month: int, year: int, active_only: bool = True
    ) -> List[Liability]:
        """
        Generate liabilities for all recurring bills for a specific month.

        Args:
            month: Month (1-12) to generate bills for
            year: Year to generate bills for
            active_only: If True, only process active recurring bills

        Returns:
            List of all generated liability instances
        """
        # Get all applicable recurring bills
        recurring_bills = await self.get_recurring_bills(
            active_only=active_only,
            limit=1000,  # Increased limit to ensure we get all bills
        )

        generated_bills = []

        # Generate bills for each recurring bill
        for recurring_bill in recurring_bills:
            bills = await self.generate_bills(recurring_bill.id, month, year)
            generated_bills.extend(bills)

        return generated_bills
