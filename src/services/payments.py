"""
Payment service implementation.

This module provides a service for payment operations, including creating, updating,
and retrieving payments with their payment sources, following the repository pattern
according to ADR-014 compliance.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment
from src.repositories.accounts import AccountRepository
from src.repositories.income import IncomeRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payments import PaymentRepository
from src.schemas.payments import PaymentCreate, PaymentUpdate
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import ensure_utc
from src.utils.decimal_precision import DecimalPrecision


class PaymentService(BaseService):
    """
    Service for payment operations.

    This service implements the ADR-014 Repository Pattern Compliance by using repositories
    for all data access operations and inheriting from BaseService for standardized
    repository initialization.
    """

    # No custom initialization needed - using BaseService's __init__

    async def validate_account_availability(
        self, sources: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that accounts exist and have sufficient funds/credit.

        Args:
            sources: List of payment source dictionaries with account_id and amount keys

        Returns:
            Tuple containing validity flag and optional error message
        """
        # Get account repository
        account_repo = await self._get_repository(AccountRepository)

        for source in sources:
            # Get account from repository
            account = await account_repo.get(source["account_id"])
            if not account:
                return False, f"Account {source['account_id']} not found"

            # Validate account has sufficient funds/credit
            source_amount = Decimal(str(source["amount"]))
            # Round for internal calculation to ensure consistency
            source_amount = DecimalPrecision.round_for_calculation(source_amount)

            if account.account_type == "credit":
                available_credit = DecimalPrecision.round_for_calculation(
                    account.available_credit
                )
                if available_credit < source_amount:
                    return False, f"Insufficient credit in account {account.name}"
            else:
                available_balance = DecimalPrecision.round_for_calculation(
                    account.available_balance
                )
                if available_balance < source_amount:
                    return False, f"Insufficient funds in account {account.name}"

        return True, None

    async def validate_references(
        self, liability_id: Optional[int], income_id: Optional[int]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that optional liability and income references exist.

        Args:
            liability_id: Optional liability ID to validate
            income_id: Optional income ID to validate

        Returns:
            Tuple containing validity flag and optional error message
        """
        if liability_id:
            # Get liability repository and check existence
            liability_repo = await self._get_repository(LiabilityRepository)
            liability = await liability_repo.get(liability_id)
            if not liability:
                return False, f"Liability {liability_id} not found"

        if income_id:
            # Get income repository and check existence
            income_repo = await self._get_repository(IncomeRepository)
            income = await income_repo.get(income_id)
            if not income:
                return False, f"Income {income_id} not found"

        return True, None

    async def get_payments(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        """
        Get paginated list of payments with sources loaded.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Payment objects with sources loaded
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Use paginated query with sources included
        return await payment_repo.get_multi(
            skip=skip, 
            limit=limit, 
            order_by=[Payment.payment_date.desc()],
            options=[{"include_sources": True}]
        )

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        """
        Get a payment by ID with sources loaded.

        Args:
            payment_id: Payment ID to retrieve

        Returns:
            Payment object with sources loaded or None if not found
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Use specialized get_with_sources method
        return await payment_repo.get_with_sources(payment_id)

    async def create_payment(self, payment_create: PaymentCreate) -> Payment:
        """
        Create a new payment with its sources.

        Args:
            payment_create: Payment creation data with sources

        Returns:
            Created Payment object with sources loaded

        Raises:
            ValueError: If validation fails for accounts or references
        """
        # Validate account availability
        valid, error = await self.validate_account_availability(
            [source.model_dump() for source in payment_create.sources]
        )
        if not valid:
            raise ValueError(error)

        # Validate references
        valid, error = await self.validate_references(
            payment_create.liability_id, payment_create.income_id
        )
        if not valid:
            raise ValueError(error)

        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Prepare payment data
        payment_data = payment_create.model_dump()
        
        # Round amount for internal storage
        payment_data["amount"] = DecimalPrecision.round_for_calculation(payment_data["amount"])
        
        # Round source amounts
        for source in payment_data["sources"]:
            source["amount"] = DecimalPrecision.round_for_calculation(Decimal(str(source["amount"])))

        # Create payment with sources in one operation through repository
        return await payment_repo.create(payment_data)

    async def update_payment(
        self, payment_id: int, payment_update: PaymentUpdate
    ) -> Optional[Payment]:
        """
        Update an existing payment and optionally its sources.

        Args:
            payment_id: ID of payment to update
            payment_update: Payment update data with optional sources

        Returns:
            Updated Payment object with sources loaded or None if not found

        Raises:
            ValueError: If validation fails for accounts
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Get existing payment
        db_payment = await payment_repo.get_with_sources(payment_id)
        if not db_payment:
            return None

        # Prepare update data
        update_data = payment_update.model_dump(exclude_unset=True)
        
        # If sources are being updated, validate account availability
        if "sources" in update_data:
            # Validate account availability
            valid, error = await self.validate_account_availability(
                [source for source in update_data["sources"]]
            )
            if not valid:
                raise ValueError(error)
            
            # Round source amounts for consistency
            for source in update_data["sources"]:
                source["amount"] = DecimalPrecision.round_for_calculation(Decimal(str(source["amount"])))

        # Perform update through repository
        await payment_repo.update(payment_id, update_data)
        
        # Return payment with sources loaded
        return await payment_repo.get_with_sources(payment_id)

    async def delete_payment(self, payment_id: int) -> bool:
        """
        Delete a payment and its sources.

        Args:
            payment_id: ID of payment to delete

        Returns:
            True if payment was deleted, False if not found
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Get existing payment
        db_payment = await payment_repo.get(payment_id)
        if not db_payment:
            return False
        
        # Delete through repository
        await payment_repo.remove(payment_id)
        return True

    async def get_payments_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Payment]:
        """
        Get payments within a specific date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of Payment objects with sources loaded
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Convert dates to datetime for repository method
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Ensure UTC timezone awareness
        start_datetime = ensure_utc(start_datetime)
        end_datetime = ensure_utc(end_datetime)
        
        # Use repository's specialized method
        return await payment_repo.get_payments_in_date_range(
            start_datetime, 
            end_datetime,
            include_sources=True
        )

    async def get_payments_for_liability(self, liability_id: int) -> List[Payment]:
        """
        Get payments for a specific liability.

        Args:
            liability_id: Liability ID

        Returns:
            List of Payment objects with sources loaded
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Use repository's specialized method
        return await payment_repo.get_payments_for_bill(
            liability_id,
            include_sources=True
        )

    async def get_payments_for_account(self, account_id: int) -> List[Payment]:
        """
        Get payments that use a specific account as a source.

        Args:
            account_id: Account ID

        Returns:
            List of Payment objects with sources loaded
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Use repository's specialized method
        return await payment_repo.get_payments_for_account(
            account_id,
            include_sources=True
        )
        
    async def get_total_amount_in_range(
        self, 
        start_date: date, 
        end_date: date,
        category: Optional[str] = None
    ) -> Decimal:
        """
        Get total payment amount in a date range, optionally filtered by category.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            category: Optional category filter
            
        Returns:
            Total payment amount as Decimal
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Convert dates to datetime for repository method
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Ensure UTC timezone awareness
        start_datetime = ensure_utc(start_datetime)
        end_datetime = ensure_utc(end_datetime)
        
        # Use repository's specialized method
        return await payment_repo.get_total_amount_in_range(
            start_datetime,
            end_datetime,
            category
        )
        
    async def get_recent_payments(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[Payment]:
        """
        Get recent payments from the last specified number of days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of payments to return
            
        Returns:
            List of recent Payment objects with sources loaded
        """
        # Get payment repository
        payment_repo = await self._get_repository(PaymentRepository)
        
        # Use repository's specialized method
        return await payment_repo.get_recent_payments(
            days=days,
            limit=limit,
            include_sources=True
        )
