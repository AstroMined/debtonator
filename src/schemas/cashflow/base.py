from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import Field

from src.schemas import BaseSchemaValidator

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
    total_bills: Decimal = BaseSchemaValidator.money_field(
        "Total amount of bills in forecast period",
        default=...,
        ge=0
    )

    total_income: Decimal = BaseSchemaValidator.money_field(
        "Total amount of income in forecast period",
        default=...,
        ge=0
    )
    balance: Decimal = BaseSchemaValidator.money_field(
        "Current balance across all accounts",
        default=...
    )
    
    forecast: Decimal = BaseSchemaValidator.money_field(
        "Projected balance at end of forecast period",
        default=...
    )
    
    min_14_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 14 days",
        default=...
    )
    
    min_30_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 30 days",
        default=...
    )
    
    min_60_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 60 days",
        default=...
    )
    
    min_90_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 90 days",
        default=...
    )
    
    daily_deficit: Decimal = BaseSchemaValidator.money_field(
        "Average daily deficit amount",
        default=...
    )
    yearly_deficit: Decimal = BaseSchemaValidator.money_field(
        "Projected yearly deficit", 
        default=...
    )
    
    required_income: Decimal = BaseSchemaValidator.money_field(
        "Income required to cover bills with tax consideration",
        default=...
    )
    
    hourly_rate_40: Decimal = BaseSchemaValidator.money_field(
        "Hourly rate needed at 40 hours per week",
        default=...
    )
    
    hourly_rate_30: Decimal = BaseSchemaValidator.money_field(
        "Hourly rate needed at 30 hours per week",
        default=...
    )
    
    hourly_rate_20: Decimal = BaseSchemaValidator.money_field(
        "Hourly rate needed at 20 hours per week",
        default=...
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
    total_bills: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Total amount of bills in forecast period",
        default=None, 
        ge=0
    )
    
    total_income: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Total amount of income in forecast period",
        default=None, 
        ge=0
    )
    
    balance: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Current balance across all accounts",
        default=None
    )
    
    forecast: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Projected balance at end of forecast period",
        default=None
    )
    
    min_14_day: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Minimum funds required for next 14 days",
        default=None
    )
    
    min_30_day: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Minimum funds required for next 30 days",
        default=None
    )
    
    min_60_day: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Minimum funds required for next 60 days",
        default=None
    )
    
    min_90_day: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Minimum funds required for next 90 days",
        default=None
    )
    
    daily_deficit: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Average daily deficit amount",
        default=None
    )
    
    yearly_deficit: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Projected yearly deficit",
        default=None
    )
    
    required_income: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Income required to cover bills with tax consideration",
        default=None
    )
    
    hourly_rate_40: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Hourly rate needed at 40 hours per week",
        default=None
    )
    
    hourly_rate_30: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Hourly rate needed at 30 hours per week",
        default=None
    )
    
    hourly_rate_20: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Hourly rate needed at 20 hours per week",
        default=None
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
    min_balance: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Minimum balance threshold for filtering",
        default=None
    )
    
    max_balance: Optional[Decimal] = BaseSchemaValidator.money_field(
        "Maximum balance threshold for filtering",
        default=None
    )
