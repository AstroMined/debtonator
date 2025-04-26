from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.liabilities import Liability, LiabilityStatus
from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payments import PaymentRepository
from src.schemas.liabilities import AutoPayUpdate, LiabilityCreate, LiabilityUpdate
from src.services.base import BaseService
from src.utils.datetime_utils import days_from_now, ensure_utc, utc_now
from src.utils.decimal_precision import DecimalPrecision


class LiabilityService(BaseService):
    """
    Service class for handling Liability-related business logic.

    This service is responsible for:
    - Managing liabilities (bills)
    - Handling auto-pay configuration
    - Validating liability operations
    - Managing liability relationships

    All business logic and validations are centralized here, keeping the
    Liability model as a pure data structure (ADR-012) and following
    ADR-014 repository pattern principles.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[Any] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the service with a database session and optional dependencies.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service
            config_provider: Optional configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def validate_liability_create(
        self, liability_data: LiabilityCreate
    ) -> Tuple[bool, Optional[str]]:
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
        # Get repositories
        category_repo = await self._get_repository(CategoryRepository)
        account_repo = await self._get_repository(AccountRepository)

        # Verify category exists
        category = await category_repo.get(liability_data.category_id)
        if not category:
            return False, f"Category with ID {liability_data.category_id} not found"

        # Verify account exists
        account = await account_repo.get(liability_data.primary_account_id)
        if not account:
            return (
                False,
                f"Account with ID {liability_data.primary_account_id} not found",
            )

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
        # Get repositories
        liability_repo = await self._get_repository(LiabilityRepository)
        category_repo = await self._get_repository(CategoryRepository)
        account_repo = await self._get_repository(AccountRepository)

        # Verify liability exists
        liability = await liability_repo.get(liability_id)
        if not liability:
            return False, f"Liability with ID {liability_id} not found"

        # Extract update data
        update_data = liability_data.model_dump(exclude_unset=True)

        # Verify new category exists if changing
        if "category_id" in update_data:
            category = await category_repo.get(update_data["category_id"])
            if not category:
                return False, f"Category with ID {update_data['category_id']} not found"

        # Verify new primary account exists if changing
        if "primary_account_id" in update_data:
            account = await account_repo.get(update_data["primary_account_id"])
            if not account:
                return (
                    False,
                    f"Account with ID {update_data['primary_account_id']} not found",
                )

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
        # Get repository
        liability_repo = await self._get_repository(LiabilityRepository)

        # Verify liability exists
        liability = await liability_repo.get(liability_id)
        if not liability:
            return False, f"Liability with ID {liability_id} not found"

        # Validate settings if provided
        if auto_pay_data.settings:
            # Add any specific validation for auto-pay settings here
            pass

        return True, None

    async def get_liabilities(self, skip: int = 0, limit: int = 100) -> List[Liability]:
        """
        Get a list of liabilities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Liability]: List of liabilities
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Use the repository's list method with pagination params
        return await liability_repo.list(
            skip=skip, limit=limit, order_by=Liability.due_date.desc()
        )

    async def get_liability(self, liability_id: int) -> Optional[Liability]:
        """
        Get a liability by ID with payments loaded.

        Args:
            liability_id: ID of the liability

        Returns:
            Optional[Liability]: The liability if found, None otherwise
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Use repository method that loads relationships
        return await liability_repo.get_with_relationships(
            liability_id, include_payments=True
        )

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
        # Ensure we have datetime objects in UTC for consistency
        start_datetime = ensure_utc(datetime.combine(start_date, datetime.min.time()))
        end_datetime = ensure_utc(datetime.combine(end_date, datetime.max.time()))

        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_bills_due_in_range(
            start_datetime, end_datetime, include_paid=True
        )

    async def get_unpaid_liabilities(self) -> List[Liability]:
        """
        Get all unpaid liabilities.

        Returns:
            List[Liability]: List of unpaid liabilities
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Find bills with PENDING status
        return await liability_repo.find_bills_by_status(LiabilityStatus.PENDING)

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
            raise HTTPException(status_code=400, detail=error_message)

        # Get repository
        liability_repo = await self._get_repository(LiabilityRepository)

        # Create liability data with proper decimal precision
        liability_data = liability_create.model_dump()
        liability_data["amount"] = DecimalPrecision.round_for_display(
            liability_data["amount"]
        )

        # Ensure due_date is UTC-aware if it's a datetime
        if isinstance(liability_data["due_date"], datetime):
            liability_data["due_date"] = ensure_utc(liability_data["due_date"])

        # Create liability using repository
        db_liability = await liability_repo.create(liability_data)

        # Get fresh copy with relationships
        return await liability_repo.get_with_relationships(
            db_liability.id, include_payments=True
        )

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
        valid, error_message = await self.validate_liability_update(
            liability_id, liability_update
        )
        if not valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Get repository
        liability_repo = await self._get_repository(LiabilityRepository)

        # Get update data
        update_data = liability_update.model_dump(exclude_unset=True)

        # Special handling for decimal values
        if "amount" in update_data:
            update_data["amount"] = DecimalPrecision.round_for_display(
                update_data["amount"]
            )

        # Ensure due_date is UTC-aware if it's a datetime
        if "due_date" in update_data and isinstance(update_data["due_date"], datetime):
            update_data["due_date"] = ensure_utc(update_data["due_date"])

        # Update using repository
        updated_liability = await liability_repo.update(liability_id, update_data)
        if not updated_liability:
            return None

        # Get fresh copy with relationships
        return await liability_repo.get_with_relationships(
            liability_id, include_payments=True
        )

    async def delete_liability(self, liability_id: int) -> bool:
        """
        Delete a liability.

        Args:
            liability_id: ID of the liability to delete

        Returns:
            bool: True if deleted, False if not found
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Check if liability exists
        liability = await liability_repo.get(liability_id)
        if not liability:
            return False

        # Delete using repository
        deleted = await liability_repo.delete(liability_id)
        return deleted

    async def is_paid(self, liability_id: int) -> bool:
        """
        Check if a liability has any associated payments.

        Args:
            liability_id: ID of the liability to check

        Returns:
            bool: True if paid, False otherwise
        """
        payment_repo = await self._get_repository(PaymentRepository)

        # Get payments for this liability
        payments = await payment_repo.get_by_liability(liability_id)
        return len(payments) > 0

    async def update_auto_pay(
        self, liability_id: int, auto_pay_update: AutoPayUpdate
    ) -> Optional[Liability]:
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
        valid, error_message = await self.validate_auto_pay_update(
            liability_id, auto_pay_update
        )
        if not valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Get repository
        liability_repo = await self._get_repository(LiabilityRepository)

        # Get liability
        liability = await liability_repo.get(liability_id)
        if not liability:
            return None

        # Prepare update data
        update_data = {
            "auto_pay_enabled": auto_pay_update.enabled,
            "auto_pay": auto_pay_update.enabled,  # Sync auto_pay with enabled state
        }

        # Update settings if provided
        if auto_pay_update.settings:
            # Convert settings to dict and handle Decimal serialization
            settings_dict = auto_pay_update.settings.model_dump(exclude_none=True)
            if "minimum_balance_required" in settings_dict:
                # Format the minimum balance with 2 decimal places
                min_balance = settings_dict["minimum_balance_required"]
                settings_dict["minimum_balance_required"] = str(
                    DecimalPrecision.round_for_display(min_balance)
                )
            update_data["auto_pay_settings"] = settings_dict
        elif not auto_pay_update.enabled:
            # Clear settings when disabling auto-pay
            update_data["auto_pay_settings"] = None

        # Update using repository
        updated_liability = await liability_repo.update(liability_id, update_data)

        # Get fresh copy
        return updated_liability

    async def get_auto_pay_candidates(self, days_ahead: int = 7) -> List[Liability]:
        """
        Get liabilities that are candidates for auto-pay processing.

        Args:
            days_ahead: Number of days ahead to look for candidates

        Returns:
            List[Liability]: List of auto-pay candidates
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Get current date and end date
        now = utc_now()
        end_date = days_from_now(days_ahead)

        # Get upcoming bills
        bills = await liability_repo.get_bills_due_in_range(
            now, end_date, include_paid=False
        )

        # Filter for auto-pay enabled
        return [bill for bill in bills if bill.auto_pay_enabled and bill.auto_pay]

    async def process_auto_pay(self, liability_id: int) -> bool:
        """
        Process auto-pay for a specific liability.

        Args:
            liability_id: ID of the liability to process

        Returns:
            bool: True if processed successfully, False otherwise
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Get liability with relationships
        liability = await liability_repo.get_with_relationships(
            liability_id, include_primary_account=True
        )

        if not liability or not liability.auto_pay_enabled:
            return False

        try:
            # Update last attempt timestamp
            update_data = {"last_auto_pay_attempt": utc_now()}

            await liability_repo.update(liability_id, update_data)

            # TODO: Implement actual payment processing logic here
            # This would involve:
            # 1. Checking account balances
            # 2. Creating payment record
            # 3. Processing payment through payment service
            # 4. Updating liability status

            return True
        except Exception:
            return False

    async def disable_auto_pay(self, liability_id: int) -> Optional[Liability]:
        """
        Disable auto-pay for a liability.

        Args:
            liability_id: ID of the liability to update

        Returns:
            Optional[Liability]: The updated liability if found, None otherwise
        """
        liability_repo = await self._get_repository(LiabilityRepository)

        # Update auto-pay settings
        update_data = {
            "auto_pay": False,
            "auto_pay_enabled": False,
            "auto_pay_settings": None,
        }

        return await liability_repo.update(liability_id, update_data)

    async def get_auto_pay_status(self, liability_id: int) -> Optional[Dict]:
        """
        Get auto-pay status and settings for a liability.

        Args:
            liability_id: ID of the liability to check

        Returns:
            Optional[Dict]: Auto-pay status info if found, None otherwise
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        liability = await liability_repo.get(liability_id)

        if not liability:
            return None

        return {
            "auto_pay": liability.auto_pay,
            "enabled": liability.auto_pay_enabled,
            "settings": liability.auto_pay_settings,
            "last_attempt": liability.last_auto_pay_attempt,
        }

    async def get_bills_due_in_range(
        self, start_date: datetime, end_date: datetime, include_paid: bool = False
    ) -> List[Liability]:
        """
        Get bills due within a specified date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            include_paid: Whether to include paid bills

        Returns:
            List[Liability]: Bills due in the date range
        """
        # Ensure UTC timezone
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)

        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_bills_due_in_range(
            start_date, end_date, include_paid
        )

    async def get_bills_by_category(
        self, category_id: int, include_paid: bool = False, limit: int = 100
    ) -> List[Liability]:
        """
        Get bills filtered by category.

        Args:
            category_id: Category ID
            include_paid: Whether to include paid bills
            limit: Maximum number of bills to return

        Returns:
            List[Liability]: Bills in the category
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_bills_by_category(
            category_id, include_paid, limit
        )

    async def get_recurring_bills(self, active_only: bool = True) -> List[Liability]:
        """
        Get recurring bills.

        Args:
            active_only: Whether to include only active bills

        Returns:
            List[Liability]: Recurring bills
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_recurring_bills(active_only)

    async def get_bills_for_account(
        self, account_id: int, include_paid: bool = False, include_splits: bool = True
    ) -> List[Liability]:
        """
        Get bills associated with a specific account.

        Args:
            account_id: Account ID
            include_paid: Whether to include paid bills
            include_splits: Whether to include bills via splits

        Returns:
            List[Liability]: Bills associated with the account
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_bills_for_account(
            account_id, include_paid, include_splits
        )

    async def get_upcoming_payments(
        self, days: int = 30, include_paid: bool = False
    ) -> List[Liability]:
        """
        Get upcoming bills due within specified number of days.

        Args:
            days: Number of days to look ahead
            include_paid: Whether to include paid bills

        Returns:
            List[Liability]: Upcoming bills
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_upcoming_payments(days, include_paid)

    async def get_overdue_bills(self) -> List[Liability]:
        """
        Get overdue bills (due date in past and not paid).

        Returns:
            List[Liability]: Overdue bills
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.get_overdue_bills()

    async def mark_as_paid(
        self, liability_id: int, payment_date: Optional[datetime] = None
    ) -> Optional[Liability]:
        """
        Mark a liability as paid.

        Args:
            liability_id: Liability ID
            payment_date: Date of payment (defaults to now)

        Returns:
            Optional[Liability]: Updated liability or None if not found
        """
        liability_repo = await self._get_repository(LiabilityRepository)
        return await liability_repo.mark_as_paid(liability_id, payment_date)
