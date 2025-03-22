from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field, field_validator, ValidationInfo

from src.schemas import BaseSchemaValidator, MoneyDecimal


class BalanceReconciliationBase(BaseSchemaValidator):
    """
    Base schema for balance reconciliation.

    Contains the core fields required for all balance reconciliation operations.
    """

    account_id: int = Field(..., description="ID of the account being reconciled")
    previous_balance: MoneyDecimal = Field(
        ..., description="Balance before reconciliation"
    )
    new_balance: MoneyDecimal = Field(..., description="Balance after reconciliation")
    reason: str | None = Field(
        None, description="Reason for the reconciliation", max_length=500
    )


class BalanceReconciliationCreate(BalanceReconciliationBase):
    """
    Schema for creating a balance reconciliation.

    Note: adjustment_amount is required by the database model but is typically
    calculated by the service layer in production code. It is included here
    to support repository testing patterns that bypass the service layer.
    """

    adjustment_amount: MoneyDecimal = Field(
        ..., 
        description="Amount of adjustment (new_balance - previous_balance)"
    )
    
    @field_validator('adjustment_amount')
    @classmethod
    def validate_adjustment_amount(cls, v: Decimal, info: ValidationInfo) -> Decimal:
        """Validate that adjustment_amount equals new_balance - previous_balance."""
        values = info.data
        new_balance = values.get('new_balance')
        previous_balance = values.get('previous_balance')
        
        if new_balance is not None and previous_balance is not None:
            expected = new_balance - previous_balance
            if v != expected:
                raise ValueError(
                    f"adjustment_amount must equal new_balance - previous_balance "
                    f"(got {v}, expected {expected})"
                )
        
        return v


class BalanceReconciliationUpdate(BaseSchemaValidator):
    """
    Schema for updating a balance reconciliation.

    Allows updating new_balance, adjustment_amount, and reason fields.
    """

    new_balance: MoneyDecimal | None = Field(
        None, description="Updated balance after reconciliation"
    )
    adjustment_amount: MoneyDecimal | None = Field(
        None, description="Updated adjustment amount (new_balance - previous_balance)"
    )
    reason: str | None = Field(
        None, description="Updated reason for the reconciliation", max_length=500
    )


class BalanceReconciliation(BalanceReconciliationBase):
    """
    Schema for a complete balance reconciliation record.

    Includes all fields from the base schema plus system-generated fields.
    """

    id: int = Field(..., description="Unique identifier for the reconciliation record")
    adjustment_amount: MoneyDecimal = Field(
        ..., description="Amount of adjustment (new_balance - previous_balance)"
    )
    reconciliation_date: datetime = Field(
        ..., description="Date and time of the reconciliation in UTC timezone"
    )
    created_at: datetime = Field(
        ..., description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time when the record was last updated in UTC timezone",
    )
