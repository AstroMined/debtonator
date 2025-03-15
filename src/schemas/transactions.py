from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic import Field

from src.schemas import BaseSchemaValidator

# Local enum instead of importing from models
class TransactionType(str, Enum):
    """Type of transaction (credit/debit)"""
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionBase(BaseSchemaValidator):
    """
    Base schema for transaction data.
    
    Contains common fields and validation shared by all transaction schemas.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    amount: Decimal = Field(
        ..., 
        description="Transaction amount (in decimal format)",
        ge=0,
        decimal_places=2
    )
    transaction_type: TransactionType = Field(
        ..., 
        description="Type of transaction (credit/debit)"
    )
    description: Optional[str] = Field(
        None, 
        description="Transaction description",
        max_length=200
    )
    transaction_date: datetime = Field(
        ..., 
        description="Date of the transaction (UTC timezone required)"
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation

class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.
    
    Inherits all fields and validation from TransactionBase.
    """
    pass

class TransactionUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing transaction.
    
    All fields are optional to allow partial updates.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    amount: Optional[Decimal] = Field(
        None, 
        description="Transaction amount (in decimal format)",
        ge=0,
        decimal_places=2
    )
    transaction_type: Optional[TransactionType] = Field(
        None, 
        description="Type of transaction (credit/debit)"
    )
    description: Optional[str] = Field(
        None, 
        description="Transaction description",
        max_length=200
    )
    transaction_date: Optional[datetime] = Field(
        None, 
        description="Date of the transaction (UTC timezone required)"
    )

class TransactionInDB(TransactionBase):
    """
    Schema for transaction data as stored in the database.
    
    Extends the base schema with database-specific fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    id: int = Field(..., description="Unique transaction identifier")
    account_id: int = Field(..., description="ID of the account associated with this transaction")
    created_at: datetime = Field(..., description="Timestamp when the record was created (UTC timezone)")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated (UTC timezone)")

class Transaction(TransactionInDB):
    """
    Schema for transaction data returned to the client.
    
    Inherits all fields and validation from TransactionInDB.
    Represents the complete transaction data model as returned by the API.
    """
    pass

class TransactionList(BaseSchemaValidator):
    """
    Schema for a paginated list of transactions.
    
    Contains a list of transaction items and total count for pagination.
    """
    items: List[Transaction] = Field(..., description="List of transaction items")
    total: int = Field(..., description="Total number of items available")
