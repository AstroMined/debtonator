from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Annotated

from pydantic import Field

from src.schemas import BaseSchemaValidator, MoneyDecimal

class CashflowBase(BaseSchemaValidator):
    """
    Base schema for cashflow data.
    
    Contains all the core fields required for cashflow forecasting.
    All datetime fields are stored in UTC timezone.
    """
    forecast_date: datetime = Field(
        default_factory=datetime.now,  # BaseSchemaValidator handles UTC validation
        description="Date and time of forecast in UTC timezone"
    )
    total_bills: MoneyDecimal = Field(
        ...,
        ge=Decimal('0'),
        description="Total amount of bills in forecast period"
    )

    total_income: MoneyDecimal = Field(
        ...,
        ge=Decimal('0'),
        description="Total amount of income in forecast period"
    )
    balance: MoneyDecimal = Field(
        ...,
        description="Current balance across all accounts"
    )
    
    forecast: MoneyDecimal = Field(
        ...,
        description="Projected balance at end of forecast period"
    )
    
    min_14_day: MoneyDecimal = Field(
        ...,
        description="Minimum funds required for next 14 days"
    )
    
    min_30_day: MoneyDecimal = Field(
        ...,
        description="Minimum funds required for next 30 days"
    )
    
    min_60_day: MoneyDecimal = Field(
        ...,
        description="Minimum funds required for next 60 days"
    )
    
    min_90_day: MoneyDecimal = Field(
        ...,
        description="Minimum funds required for next 90 days"
    )
    
    daily_deficit: MoneyDecimal = Field(
        ...,
        description="Average daily deficit amount"
    )
    yearly_deficit: MoneyDecimal = Field(
        ...,
        description="Projected yearly deficit"
    )
    
    required_income: MoneyDecimal = Field(
        ...,
        description="Income required to cover bills with tax consideration"
    )
    
    hourly_rate_40: MoneyDecimal = Field(
        ...,
        description="Hourly rate needed at 40 hours per week"
    )
    
    hourly_rate_30: MoneyDecimal = Field(
        ...,
        description="Hourly rate needed at 30 hours per week"
    )
    
    hourly_rate_20: MoneyDecimal = Field(
        ...,
        description="Hourly rate needed at 20 hours per week"
    )

class CashflowCreate(CashflowBase):
    """
    Schema for creating a new cashflow forecast.
    
    Extends the base schema without adding additional fields.
    """
    pass

class CashflowUpdate(BaseSchemaValidator):
    """
    Schema for updating a cashflow forecast.
    
    All fields are optional to allow partial updates.
    """
    forecast_date: Optional[datetime] = Field(
        None,
        description="Date and time of forecast in UTC timezone"
    )
    total_bills: Optional[MoneyDecimal] = Field(
        default=None,
        ge=Decimal('0'),
        description="Total amount of bills in forecast period"
    )
    
    total_income: Optional[MoneyDecimal] = Field(
        default=None,
        ge=Decimal('0'),
        description="Total amount of income in forecast period"
    )
    
    balance: Optional[MoneyDecimal] = Field(
        default=None,
        description="Current balance across all accounts"
    )
    
    forecast: Optional[MoneyDecimal] = Field(
        default=None,
        description="Projected balance at end of forecast period"
    )
    
    min_14_day: Optional[MoneyDecimal] = Field(
        default=None,
        description="Minimum funds required for next 14 days"
    )
    
    min_30_day: Optional[MoneyDecimal] = Field(
        default=None,
        description="Minimum funds required for next 30 days"
    )
    
    min_60_day: Optional[MoneyDecimal] = Field(
        default=None,
        description="Minimum funds required for next 60 days"
    )
    
    min_90_day: Optional[MoneyDecimal] = Field(
        default=None,
        description="Minimum funds required for next 90 days"
    )
    
    daily_deficit: Optional[MoneyDecimal] = Field(
        default=None,
        description="Average daily deficit amount"
    )
    
    yearly_deficit: Optional[MoneyDecimal] = Field(
        default=None,
        description="Projected yearly deficit"
    )
    
    required_income: Optional[MoneyDecimal] = Field(
        default=None,
        description="Income required to cover bills with tax consideration"
    )
    
    hourly_rate_40: Optional[MoneyDecimal] = Field(
        default=None,
        description="Hourly rate needed at 40 hours per week"
    )
    
    hourly_rate_30: Optional[MoneyDecimal] = Field(
        default=None,
        description="Hourly rate needed at 30 hours per week"
    )
    
    hourly_rate_20: Optional[MoneyDecimal] = Field(
        default=None,
        description="Hourly rate needed at 20 hours per week"
    )

class CashflowInDB(CashflowBase):
    """
    Schema for cashflow forecast in database.
    
    Includes system-generated fields like ID and timestamps.
    All datetime fields are stored in UTC timezone.
    """
    id: int = Field(..., description="Unique identifier for the cashflow record")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when the record was last updated in UTC timezone"
    )

class CashflowResponse(CashflowInDB):
    """
    Schema for cashflow forecast response.
    
    Extends the database schema for API responses.
    """
    pass

class CashflowList(BaseSchemaValidator):
    """
    Schema for list of cashflow forecasts.
    
    Used for paginated responses of multiple cashflow records.
    """
    items: List[CashflowResponse] = Field(
        ...,
        description="List of cashflow forecast records"
    )
    total: int = Field(
        ...,
        description="Total number of records available"
    )

class CashflowFilters(BaseSchemaValidator):
    """
    Schema for cashflow filtering parameters.
    
    Used to filter cashflow forecasts by date range and balance thresholds.
    All datetime fields are stored in UTC timezone.
    """
    start_date: Optional[datetime] = Field(
        None,
        description="Filter cashflows starting from this date in UTC timezone"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Filter cashflows until this date in UTC timezone"
    )
    min_balance: Optional[MoneyDecimal] = Field(
        default=None,
        description="Minimum balance threshold for filtering"
    )
    
    max_balance: Optional[MoneyDecimal] = Field(
        default=None,
        description="Maximum balance threshold for filtering"
    )
