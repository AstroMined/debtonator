from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import Field

from src.schemas.base_schema import BaseSchemaValidator, MoneyDecimal


# Local enum instead of importing from models
class TransactionType(str, Enum):
    """Type of transaction (credit/debit)"""

    CREDIT = "credit"
    DEBIT = "debit"


class TransactionHistoryBase(BaseSchemaValidator):
    """
    Base schema for transaction history data.

    Contains common fields and validation shared by all transaction history schemas.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    amount: MoneyDecimal = Field(
        ..., ge=0, description="Transaction amount (in decimal format)"
    )
    transaction_type: TransactionType = Field(
        ..., description="Type of transaction (credit/debit)"
    )
    description: Optional[str] = Field(
        None, description="Transaction description", max_length=200
    )
    transaction_date: datetime = Field(
        ..., description="Date of the transaction (UTC timezone required)"
    )


class TransactionHistoryCreate(TransactionHistoryBase):
    """
    Schema for creating a new transaction history entry.

    Inherits all fields and validation from TransactionHistoryBase.
    """

    account_id: int = Field(
        ..., description="ID of the account associated with this transaction"
    )


class TransactionHistoryUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing transaction history entry.

    All fields are optional to allow partial updates.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="ID of the transaction history to update")
    amount: Optional[MoneyDecimal] = Field(
        default=None, ge=0, description="Transaction amount (in decimal format)"
    )
    transaction_type: Optional[TransactionType] = Field(
        None, description="Type of transaction (credit/debit)"
    )
    description: Optional[str] = Field(
        None, description="Transaction description", max_length=200
    )
    transaction_date: Optional[datetime] = Field(
        None, description="Date of the transaction (UTC timezone required)"
    )


class TransactionHistoryInDB(TransactionHistoryBase):
    """
    Schema for transaction history data as stored in the database.

    Extends the base schema with database-specific fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="Unique transaction identifier")
    account_id: int = Field(
        ..., description="ID of the account associated with this transaction"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated (UTC timezone)"
    )


class TransactionHistoryList(BaseSchemaValidator):
    """
    Schema for a paginated list of transaction history entries.

    Contains a list of transaction history items and total count for pagination.
    """

    items: List[TransactionHistoryInDB] = Field(
        ..., description="List of transaction history items"
    )
    total: int = Field(..., description="Total number of items available")
