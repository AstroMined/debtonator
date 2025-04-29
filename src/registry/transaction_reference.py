"""
Transaction Reference Registry for standardized transaction categorization and field access.

This module provides the TransactionReferenceRegistry class which maintains standardized
field definitions and key generation for transaction objects across the application.
It eliminates hardcoded string matching and ensures consistent transaction handling.

Implemented as part of ADR-029 Transaction Categorization and Reference System.
"""

import threading
from typing import Any, ClassVar, Dict, List, Optional

from src.common.transaction_constants import (
    INCOME,
    EXPENSE,
    BILL,
    TRANSFER,
    RECURRING_BILL,
    RECURRING_INCOME,
    PAYMENT,
    SOURCE_FIELDS,
    CATEGORY_FIELDS,
    AMOUNT_FIELDS,
    DATE_FIELDS,
    ALL_TRANSACTION_TYPES,
)


class TransactionReferenceRegistry:  # pylint: disable=too-many-instance-attributes
    """
    Registry for transaction attribute definitions and field access.

    This class implements the singleton pattern to ensure a single registry instance
    exists across the application. It defines standard transaction types, field
    mappings, and methods to consistently access fields from different transaction
    structures.

    The registry eliminates hardcoded string matching and improves maintainability
    by centralizing transaction field definitions.

    Note: The uppercase naming convention for constants like INCOME, SOURCE_FIELDS
    is intentional and follows Python's standard for constants.
    """

    _instance: ClassVar[Optional["TransactionReferenceRegistry"]] = None
    _lock = threading.RLock()  # Reentrant lock for thread safety

    def __new__(cls) -> "TransactionReferenceRegistry":
        """
        Create a new TransactionReferenceRegistry instance or return the existing instance.

        Returns:
            TransactionReferenceRegistry: The singleton registry instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TransactionReferenceRegistry, cls).__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        """Initialize the registry with transaction types and field mappings."""
        with self.__class__._lock:
            # Use hasattr to check if already initialized
            if not hasattr(self, "_initialized"):
                # Set initialized flag first to avoid recursion
                object.__setattr__(self, "_initialized", False)

                # Transaction type constants  # pylint: disable=invalid-name
                self.INCOME = INCOME
                self.EXPENSE = EXPENSE
                self.BILL = BILL
                self.TRANSFER = TRANSFER
                self.RECURRING_BILL = RECURRING_BILL
                self.RECURRING_INCOME = RECURRING_INCOME
                self.PAYMENT = PAYMENT

                # Field mappings  # pylint: disable=invalid-name
                self.SOURCE_FIELDS = SOURCE_FIELDS
                self.CATEGORY_FIELDS = CATEGORY_FIELDS
                self.AMOUNT_FIELDS = AMOUNT_FIELDS
                self.DATE_FIELDS = DATE_FIELDS

                # Now we're fully initialized
                self._initialized = True

    def get_contribution_key(self, transaction_type: str, identifier: str) -> str:
        """
        Generate a consistent key for contribution factors.

        This method provides a standardized way to generate keys for transaction
        contributions in forecasts and analysis.

        Args:
            transaction_type: Type of transaction (income, expense, bill, etc.)
            identifier: Identifier for the transaction (source, category, etc.)

        Returns:
            Consistently formatted key string for the contribution
        """
        return f"{transaction_type}_{identifier}"

    def extract_source(self, transaction: Dict[str, Any]) -> str:
        """
        Extract the source identifier from a transaction.

        This method provides a consistent way to get the source from any transaction
        type by using the appropriate field based on the transaction's type.

        Args:
            transaction: Transaction dictionary with a "type" field

        Returns:
            Source identifier string or "unknown" if not found
        """
        if "type" not in transaction:
            return "unknown"

        field = self.SOURCE_FIELDS.get(transaction["type"], "description")
        return transaction.get(field, "unknown")

    def extract_category(self, transaction: Dict[str, Any]) -> Optional[str]:
        """
        Extract the category from a transaction.

        This method provides a consistent way to get the category from any transaction
        type by using the appropriate field based on the transaction's type.

        Args:
            transaction: Transaction dictionary with a "type" field

        Returns:
            Category string or None if the transaction has no category
        """
        if "type" not in transaction:
            return None

        field = self.CATEGORY_FIELDS.get(transaction["type"])
        if not field:
            return None

        return transaction.get(field)

    def extract_amount(self, transaction: Dict[str, Any]) -> Optional[float]:
        """
        Extract the amount from a transaction.

        This method provides a consistent way to get the amount from any transaction
        type by using the appropriate field based on the transaction's type.

        Args:
            transaction: Transaction dictionary with a "type" field

        Returns:
            Amount value or None if not found
        """
        if "type" not in transaction:
            return None

        field = self.AMOUNT_FIELDS.get(transaction["type"])
        if not field:
            return None

        return transaction.get(field)

    def extract_date(self, transaction: Dict[str, Any]) -> Optional[Any]:
        """
        Extract the date from a transaction.

        This method provides a consistent way to get the date from any transaction
        type by using the appropriate field based on the transaction's type.

        Args:
            transaction: Transaction dictionary with a "type" field

        Returns:
            Date value or None if not found
        """
        if "type" not in transaction:
            return None

        field = self.DATE_FIELDS.get(transaction["type"])
        if not field:
            return None

        return transaction.get(field)

    def get_transaction_fields(self) -> Dict[str, Dict[str, str]]:
        """
        Get all field mappings for all transaction types.

        Returns:
            Dict mapping transaction types to their field mappings
        """
        field_mappings = {}
        for transaction_type in ALL_TRANSACTION_TYPES:
            field_mappings[transaction_type] = {
                "source": self.SOURCE_FIELDS.get(transaction_type),
                "category": self.CATEGORY_FIELDS.get(transaction_type),
                "amount": self.AMOUNT_FIELDS.get(transaction_type),
                "date": self.DATE_FIELDS.get(transaction_type),
            }

        return field_mappings

    def is_valid_transaction_type(self, transaction_type: str) -> bool:
        """
        Check if a transaction type is valid and registered.

        Args:
            transaction_type: Transaction type to check

        Returns:
            True if the transaction type is valid, False otherwise
        """
        return transaction_type in ALL_TRANSACTION_TYPES

    def get_all_transaction_types(self) -> List[str]:
        """
        Get all registered transaction types.

        Returns:
            List of all transaction type strings
        """
        return ALL_TRANSACTION_TYPES


# Global instance for convenience - follows singleton pattern
transaction_reference_registry = TransactionReferenceRegistry()
