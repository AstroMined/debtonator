from decimal import Decimal

from pydantic import Field

from src.schemas import BaseSchemaValidator

class MinimumRequired(BaseSchemaValidator):
    """
    Schema for minimum required funds.
    
    Contains minimum funds required for different time periods.
    """
    min_14_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 14 days",
        ...
    )
    min_30_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 30 days",
        ...
    )
    min_60_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 60 days",
        ...
    )
    min_90_day: Decimal = BaseSchemaValidator.money_field(
        "Minimum funds required for next 90 days",
        ...
    )

class DeficitCalculation(BaseSchemaValidator):
    """
    Schema for deficit calculations.
    
    Contains various deficit metrics for financial planning.
    """
    daily_deficit: Decimal = BaseSchemaValidator.money_field(
        "Average daily deficit amount",
        ...
    )
    yearly_deficit: Decimal = BaseSchemaValidator.money_field(
        "Projected yearly deficit",
        ...
    )
    required_income: Decimal = BaseSchemaValidator.money_field(
        "Income required to cover bills with tax consideration",
        ...
    )

class HourlyRates(BaseSchemaValidator):
    """
    Schema for hourly rate calculations.
    
    Contains hourly rates needed at different weekly work hours.
    """
    hourly_rate_40: Decimal = BaseSchemaValidator.money_field(
        "Hourly rate needed at 40 hours per week",
        ...
    )
    hourly_rate_30: Decimal = BaseSchemaValidator.money_field(
        "Hourly rate needed at 30 hours per week",
        ...
    )
    hourly_rate_20: Decimal = BaseSchemaValidator.money_field(
        "Hourly rate needed at 20 hours per week",
        ...
    )
