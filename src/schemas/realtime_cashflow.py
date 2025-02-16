from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from zoneinfo import ZoneInfo

class AccountBalance(BaseModel):
    account_id: int
    name: str
    type: str
    current_balance: Decimal
    available_credit: Optional[Decimal] = None
    total_limit: Optional[Decimal] = None

class RealtimeCashflow(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    account_balances: List[AccountBalance]
    total_available_funds: Decimal
    total_available_credit: Decimal
    total_liabilities_due: Decimal
    net_position: Decimal
    next_bill_due: Optional[datetime] = None
    days_until_next_bill: Optional[int] = None
    minimum_balance_required: Decimal
    projected_deficit: Optional[Decimal] = None

    @field_validator("timestamp", "next_bill_due", mode="before")
    @classmethod
    def validate_timezone(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value

class RealtimeCashflowResponse(BaseModel):
    data: RealtimeCashflow
    last_updated: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))

    @field_validator("last_updated", mode="before")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if not isinstance(value, datetime):
            raise ValueError("Must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be in UTC timezone")
        return value
