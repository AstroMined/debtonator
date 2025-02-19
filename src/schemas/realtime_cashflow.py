from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from zoneinfo import ZoneInfo

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

class AccountBalance(BaseModel):
    account_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    type: AccountType
    current_balance: Decimal = Field(..., decimal_places=2)
    available_credit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_limit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)

    @field_validator("available_credit", "total_limit")
    @classmethod
    def validate_credit_fields(cls, v: Optional[Decimal], values: dict) -> Optional[Decimal]:
        if values.get("type") == AccountType.CREDIT:
            if v is None:
                raise ValueError(f"Field is required for credit accounts")
        return v

class RealtimeCashflow(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    account_balances: List[AccountBalance] = Field(..., min_items=1)
    total_available_funds: Decimal = Field(..., decimal_places=2)
    total_available_credit: Decimal = Field(..., ge=0, decimal_places=2)
    total_liabilities_due: Decimal = Field(..., ge=0, decimal_places=2)
    net_position: Decimal = Field(..., decimal_places=2)
    next_bill_due: Optional[datetime] = None
    days_until_next_bill: Optional[int] = Field(None, ge=0)
    minimum_balance_required: Decimal = Field(..., decimal_places=2)
    projected_deficit: Optional[Decimal] = Field(None, decimal_places=2)

    @field_validator("account_balances")
    @classmethod
    def validate_account_balances(cls, v: List[AccountBalance]) -> List[AccountBalance]:
        # Ensure no duplicate account IDs
        account_ids = [balance.account_id for balance in v]
        if len(set(account_ids)) != len(account_ids):
            raise ValueError("Duplicate account IDs found in account_balances")
        return v

    @field_validator("net_position")
    @classmethod
    def validate_net_position(cls, v: Decimal, values: dict) -> Decimal:
        # Verify net position calculation
        if "total_available_funds" in values and "total_liabilities_due" in values:
            expected_net = values["total_available_funds"] - values["total_liabilities_due"]
            if abs(v - expected_net) > Decimal("0.01"):  # Allow for small rounding differences
                raise ValueError("net_position must equal total_available_funds - total_liabilities_due")
        return v

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

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-01T00:00:00Z",
                "account_balances": [
                    {
                        "account_id": 1,
                        "name": "Main Checking",
                        "type": "checking",
                        "current_balance": "1000.00"
                    },
                    {
                        "account_id": 2,
                        "name": "Credit Card",
                        "type": "credit",
                        "current_balance": "-500.00",
                        "available_credit": "4500.00",
                        "total_limit": "5000.00"
                    }
                ],
                "total_available_funds": "1000.00",
                "total_available_credit": "4500.00",
                "total_liabilities_due": "500.00",
                "net_position": "500.00",
                "minimum_balance_required": "200.00"
            }
        }

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

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "account_balances": [
                        {
                            "account_id": 1,
                            "name": "Main Checking",
                            "type": "checking",
                            "current_balance": "1000.00"
                        }
                    ],
                    "total_available_funds": "1000.00",
                    "total_available_credit": "0.00",
                    "total_liabilities_due": "0.00",
                    "net_position": "1000.00",
                    "minimum_balance_required": "200.00"
                },
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
