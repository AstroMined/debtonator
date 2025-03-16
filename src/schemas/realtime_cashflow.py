from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import Field, field_validator, ConfigDict, model_validator

from src.schemas import BaseSchemaValidator

class AccountType(str, Enum):
    """
    Enumeration of account types in the system.
    
    Used to categorize different types of financial accounts.
    """
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

class AccountBalance(BaseSchemaValidator):
    """
    Schema for an account balance snapshot.
    
    Contains current financial state information for a single account.
    """
    account_id: int = Field(
        ..., 
        gt=0,
        description="Unique identifier for the account"
    )
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Name of the account"
    )
    type: AccountType = Field(
        ...,
        description="Type of the account (checking, savings, credit)"
    )
    current_balance: Decimal = Field(
        ..., 
        decimal_places=2,
        description="Current balance of the account"
    )
    available_credit: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Available credit (for credit accounts only)"
    )
    total_limit: Optional[Decimal] = Field(
        None, 
        gt=0, 
        decimal_places=2,
        description="Total credit limit (for credit accounts only)"
    )
    
    @model_validator(mode='after')
    def validate_credit_account_fields(self) -> 'AccountBalance':
        """
        Validate that credit-specific fields are present for credit accounts.
        
        This validator runs after all fields have been populated and checks
        that credit accounts have both available_credit and total_limit set.
        
        Returns:
            The validated model instance
            
        Raises:
            ValueError: If required credit fields are missing
        """
        if self.type == AccountType.CREDIT:
            if self.available_credit is None:
                raise ValueError("Field is required for credit accounts")
            if self.total_limit is None:
                raise ValueError("Field is required for credit accounts")
        return self

class RealtimeCashflow(BaseSchemaValidator):
    """
    Schema for real-time cashflow analysis.
    
    Contains comprehensive financial snapshot including account balances,
    funds availability, and liabilities.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this cashflow snapshot was created (UTC timezone)"
    )
    account_balances: List[AccountBalance] = Field(
        ..., 
        min_items=1,
        description="List of account balances included in this analysis"
    )
    total_available_funds: Decimal = Field(
        ..., 
        decimal_places=2,
        description="Total funds available across all accounts"
    )
    total_available_credit: Decimal = Field(
        ..., 
        ge=0, 
        decimal_places=2,
        description="Total available credit across all credit accounts"
    )
    total_liabilities_due: Decimal = Field(
        ..., 
        ge=0, 
        decimal_places=2,
        description="Total amount due across all liabilities"
    )
    net_position: Decimal = Field(
        ..., 
        decimal_places=2,
        description="Net financial position (total_available_funds - total_liabilities_due)"
    )
    next_bill_due: Optional[datetime] = Field(
        None,
        description="Date when the next bill is due (UTC timezone)"
    )
    days_until_next_bill: Optional[int] = Field(
        None, 
        ge=0,
        description="Number of days until the next bill is due"
    )
    minimum_balance_required: Decimal = Field(
        ..., 
        decimal_places=2,
        description="Minimum balance required to cover upcoming expenses"
    )
    projected_deficit: Optional[Decimal] = Field(
        None, 
        decimal_places=2,
        description="Projected deficit amount if current trends continue"
    )

    @field_validator("account_balances")
    @classmethod
    def validate_account_balances(cls, v: List[AccountBalance]) -> List[AccountBalance]:
        """
        Validate that there are no duplicate account IDs in the list.
        
        Args:
            v: The list of account balances to validate
            
        Returns:
            The original list if validation passes
            
        Raises:
            ValueError: If duplicate account IDs are found
        """
        account_ids = [balance.account_id for balance in v]
        if len(set(account_ids)) != len(account_ids):
            raise ValueError("Duplicate account IDs found in account_balances")
        return v

    @model_validator(mode='after')
    def validate_net_position_calculation(self) -> 'RealtimeCashflow':
        """
        Validate that net position equals total_available_funds minus total_liabilities_due.
        
        This validator runs after all fields have been populated and checks
        that the net_position calculation is correct.
        
        Returns:
            The validated model instance
            
        Raises:
            ValueError: If net position calculation is incorrect
        """
        expected_net = self.total_available_funds - self.total_liabilities_due
        if abs(self.net_position - expected_net) > Decimal("0.01"):  # Allow for small rounding differences
            raise ValueError("net_position must equal total_available_funds - total_liabilities_due")
        return self
    
    # No custom timezone validators needed - BaseSchemaValidator handles UTC validation
    
    model_config = ConfigDict(
        json_schema_extra={
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
    )

class RealtimeCashflowResponse(BaseSchemaValidator):
    """
    Schema for API response containing real-time cashflow data.
    
    Wraps the cashflow data with response metadata.
    All datetime fields are validated to ensure they have UTC timezone.
    """
    data: RealtimeCashflow = Field(
        ...,
        description="Real-time cashflow analysis data"
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this response was generated (UTC timezone)"
    )
    
    # No custom timezone validators needed - BaseSchemaValidator handles UTC validation
    
    model_config = ConfigDict(
        json_schema_extra={
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
    )
