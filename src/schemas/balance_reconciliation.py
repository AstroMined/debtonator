from datetime import datetime
from decimal import Decimal
from pydantic import Field, ConfigDict

from src.schemas import BaseSchemaValidator

class BalanceReconciliationBase(BaseSchemaValidator):
    """
    Base schema for balance reconciliation.
    
    Contains the core fields required for all balance reconciliation operations.
    """
    account_id: int = Field(..., description="ID of the account being reconciled")
    previous_balance: Decimal = Field(
        ..., 
        description="Balance before reconciliation",
        decimal_places=2
    )
    new_balance: Decimal = Field(
        ..., 
        description="Balance after reconciliation",
        decimal_places=2
    )
    reason: str | None = Field(
        None, 
        description="Reason for the reconciliation",
        max_length=500
    )

class BalanceReconciliationCreate(BalanceReconciliationBase):
    """
    Schema for creating a balance reconciliation.
    
    Extends the base schema without adding additional fields.
    """
    pass

class BalanceReconciliationUpdate(BaseSchemaValidator):
    """
    Schema for updating a balance reconciliation.
    
    Only allows updating the reason field.
    """
    reason: str | None = Field(
        None, 
        description="Updated reason for the reconciliation",
        max_length=500
    )

class BalanceReconciliation(BalanceReconciliationBase):
    """
    Schema for a complete balance reconciliation record.
    
    Includes all fields from the base schema plus system-generated fields.
    """
    id: int = Field(..., description="Unique identifier for the reconciliation record")
    adjustment_amount: Decimal = Field(
        ..., 
        description="Amount of adjustment (new_balance - previous_balance)",
        decimal_places=2
    )
    reconciliation_date: datetime = Field(
        ..., 
        description="Date and time of the reconciliation in UTC timezone"
    )
    created_at: datetime = Field(
        ..., 
        description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ..., 
        description="Date and time when the record was last updated in UTC timezone"
    )
