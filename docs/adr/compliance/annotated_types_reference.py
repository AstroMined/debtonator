"""
Reference implementation for ADR-013 Decimal Precision Handling using Pydantic V2's Annotated types.

This file demonstrates the new approach for decimal precision validation using Python's
Annotated types with Pydantic Field constraints, which is the recommended pattern in
Pydantic V2 since ConstrainedDecimal has been removed.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)

# 2 decimal places for monetary values (e.g., $100.00)
MoneyDecimal = Annotated[
    Decimal,
    Field(
        multiple_of=Decimal("0.01"), description="Monetary value with 2 decimal places"
    ),
]

# 4 decimal places for percentage values (0-1 range, e.g., 0.1234 = 12.34%)
PercentageDecimal = Annotated[
    Decimal,
    Field(
        ge=0,
        le=1,
        multiple_of=Decimal("0.0001"),
        description="Percentage value with 4 decimal places (0-1 range)",
    ),
]

# 4 decimal places for correlation values (-1 to 1 range)
CorrelationDecimal = Annotated[
    Decimal,
    Field(
        ge=-1,
        le=1,
        multiple_of=Decimal("0.0001"),
        description="Correlation value with 4 decimal places (-1 to 1 range)",
    ),
]

# 4 decimal places for general ratio values (no min/max constraints)
RatioDecimal = Annotated[
    Decimal,
    Field(
        multiple_of=Decimal("0.0001"), description="Ratio value with 4 decimal places"
    ),
]

# Dictionary type aliases
MoneyDict = Dict[str, MoneyDecimal]
PercentageDict = Dict[str, PercentageDecimal]
CorrelationDict = Dict[str, CorrelationDecimal]
RatioDict = Dict[str, RatioDecimal]
IntMoneyDict = Dict[int, MoneyDecimal]
IntPercentageDict = Dict[int, PercentageDecimal]


# Custom dictionary class with validation for monetary values
class ValidatedMoneyDict(Dict[str, Decimal]):
    """Dictionary for monetary values that enforces 2 decimal places."""

    def __setitem__(self, key, value):
        """Validate values when they're set."""
        if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
            raise ValueError(f"Value for key '{key}' must have max 2 decimal places")
        super().__setitem__(key, value)

    @classmethod
    def __get_validators__(cls):
        """Return validators for Pydantic."""
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate the dictionary during model construction."""
        if not isinstance(v, dict):
            raise TypeError("Dictionary required")

        result = cls()
        for key, val in v.items():
            result[key] = val  # This triggers __setitem__ validation
        return result


class BaseSchemaValidator(BaseModel):
    """Base schema validator with UTC timezone enforcement and decimal precision handling.

    All schema classes should inherit from this base class to ensure consistent
    datetime and decimal handling across the application.

    Features:
        - Automatically converts naive datetimes to UTC-aware during model_validate
        - Enforces UTC timezone for all datetime fields through validation
        - Provides specialized decimal types with appropriate validation:
          * MoneyDecimal: 2 decimal places for monetary values
          * PercentageDecimal: 4 decimal places for percentage values (0-1 range)
          * CorrelationDecimal: 4 decimal places for correlation values (-1 to 1 range)
          * RatioDecimal: 4 decimal places for general ratio values (no min/max)
        - Provides dictionary types for collections of decimal values

    Example usage:
        ```python
        class PaymentCreate(BaseSchemaValidator):
            payment_date: datetime
            amount: MoneyDecimal
            confidence_score: PercentageDecimal = Field(default=0.95)
            account_distribution: IntMoneyDict
        ```
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            # Ensure datetimes are serialized to ISO format with Z suffix
            datetime: lambda dt: dt.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        },
        # Helpful error messages
        error_msg_templates={
            "decimal_places": "Value must have no more than {decimal_places} decimal places",
            "multiple_of": "Value must be a multiple of {multiple_of}",
        },
    )

    @model_validator(mode="after")
    def validate_decimal_dictionaries(self) -> "BaseSchemaValidator":
        """Validate all dictionary fields with decimal values for proper precision.

        This validator checks all dictionary fields to ensure decimal values have
        the appropriate precision based on the field's type annotation.
        """
        for field_name, field_value in self.__dict__.items():
            # Skip non-dictionary fields
            if not isinstance(field_value, dict):
                continue

            field_info = self.model_fields.get(field_name)
            if not field_info or not hasattr(field_info, "annotation"):
                continue

            # Check dictionary field types
            annotation = field_info.annotation

            # Handle MoneyDict fields
            if annotation == MoneyDict or annotation == IntMoneyDict:
                for key, value in field_value.items():
                    if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
                        raise ValueError(
                            f"Dictionary value for key '{key}' should have no more than 2 decimal places"
                        )

            # Handle PercentageDict fields
            elif annotation == PercentageDict or annotation == IntPercentageDict:
                for key, value in field_value.items():
                    if isinstance(value, Decimal):
                        # Check decimal places
                        if value.as_tuple().exponent < -4:
                            raise ValueError(
                                f"Dictionary value for key '{key}' should have no more than 4 decimal places"
                            )
                        # Check range
                        if value < 0 or value > 1:
                            raise ValueError(
                                f"Percentage value for key '{key}' must be between 0 and 1"
                            )

        return self

    # Keep all the existing datetime validation methods unchanged


# Example usage in schema classes:


class PaymentCreate(BaseSchemaValidator):
    """Example schema using the new Annotated decimal types."""

    payment_date: datetime
    amount: MoneyDecimal
    description: str | None = None

    # Optional field with default
    confidence_score: PercentageDecimal = Field(default=0.95)

    # Dictionary of account distributions
    account_distributions: IntMoneyDict = Field(default_factory=dict)


class BalanceDistribution(BaseSchemaValidator):
    """Example schema showing percentage fields."""

    account_id: int
    average_balance: MoneyDecimal
    percentage_of_total: PercentageDecimal
    trend_correlation: CorrelationDecimal = Field(default=0)


class AccountAnalysis(BaseSchemaValidator):
    """Example schema showing dictionary usage."""

    account_id: int

    # Dictionary of category distributions (percentage per category)
    category_distribution: PercentageDict

    # Dictionary of daily balances (date string -> balance)
    daily_balances: MoneyDict
