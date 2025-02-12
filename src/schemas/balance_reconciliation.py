from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class BalanceReconciliationBase(BaseModel):
    """Base schema for balance reconciliation"""
    account_id: int = Field(..., description="ID of the account being reconciled")
    previous_balance: Decimal = Field(..., description="Balance before reconciliation")
    new_balance: Decimal = Field(..., description="Balance after reconciliation")
    reason: str | None = Field(None, description="Reason for the reconciliation")

class BalanceReconciliationCreate(BalanceReconciliationBase):
    """Schema for creating a balance reconciliation"""
    pass

class BalanceReconciliationUpdate(BaseModel):
    """Schema for updating a balance reconciliation"""
    reason: str | None = Field(None, description="Updated reason for the reconciliation")

class BalanceReconciliation(BalanceReconciliationBase):
    """Schema for a complete balance reconciliation record"""
    id: int
    adjustment_amount: Decimal = Field(..., description="Amount of adjustment (new_balance - previous_balance)")
    reconciliation_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config"""
        from_attributes = True
