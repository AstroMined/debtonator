"""
Statement history schema definitions for the API.

This module defines the schema classes for statement history data validation and serialization.
Includes schemas for creating, updating, and retrieving statement history records, as well as
specialized response formats for different statement-related operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import ConfigDict, Field

from src.schemas.accounts import AccountResponse

from . import BaseSchemaValidator, MoneyDecimal


class StatementHistoryBase(BaseSchemaValidator):
    """
    Base schema for statement history data.

    Contains the common attributes and validation logic for statement history data.
    """

    account_id: int = Field(..., gt=0, description="ID of the associated account")
    statement_date: datetime = Field(
        ..., description="Date of the statement (UTC timezone)"
    )
    statement_balance: MoneyDecimal = Field(
        ..., description="Balance on statement date"
    )
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    due_date: Optional[datetime] = Field(
        default=None, description="Payment due date (UTC timezone)"
    )


class StatementHistoryCreate(StatementHistoryBase):
    """
    Schema for creating a new statement history record.

    Extends the base statement history schema without adding additional fields.
    """

    pass


class StatementHistoryUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing statement history record.

    Contains all fields from StatementHistoryBase but makes them optional for partial updates.
    """

    account_id: Optional[int] = Field(
        default=None, gt=0, description="ID of the associated account"
    )
    statement_date: Optional[datetime] = Field(
        default=None, description="Date of the statement (UTC timezone)"
    )
    statement_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Balance on statement date"
    )
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    due_date: Optional[datetime] = Field(
        default=None, description="Payment due date (UTC timezone)"
    )


class StatementHistory(StatementHistoryBase):
    """
    Schema for statement history data as stored in the database.

    Extends the base statement history schema with database-specific fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0, description="Statement history ID (unique identifier)")


class StatementHistoryWithAccount(StatementHistory):
    """
    Schema for statement history with associated account details.

    Used for returning statement history with account information.
    """

    account: AccountResponse = Field(..., description="Associated account details")


class StatementHistoryResponse(StatementHistory):
    """
    Schema for statement history data in API responses.

    Extends the database statement history schema for API response formatting.
    """

    pass


class StatementHistoryTrend(BaseSchemaValidator):
    """
    Schema for statement history trend data.

    Provides a view of statement balances and minimum payments over time.
    """

    account_id: int = Field(..., gt=0, description="Account ID")
    statement_dates: List[datetime] = Field(
        ..., description="List of statement dates (UTC timezone)"
    )
    statement_balances: List[MoneyDecimal] = Field(
        ..., description="List of statement balances"
    )
    minimum_payments: List[Optional[MoneyDecimal]] = Field(
        ..., description="List of minimum payments (may contain None values)"
    )


class UpcomingStatementDue(BaseSchemaValidator):
    """
    Schema for upcoming statement due information.

    Used for returning information about statements with upcoming due dates.
    """

    statement_id: int = Field(..., gt=0, description="Statement history ID")
    account_id: int = Field(..., gt=0, description="Account ID")
    account_name: str = Field(..., description="Account name")
    due_date: datetime = Field(..., description="Payment due date (UTC timezone)")
    statement_balance: MoneyDecimal = Field(
        ..., description="Balance on statement date"
    )
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    days_until_due: int = Field(..., description="Number of days until payment is due")
