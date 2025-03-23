"""
Base schema validator with UTC timezone enforcement and decimal precision handling.

This module provides the foundation for all schema classes in the application,
ensuring consistent datetime handling and decimal precision validation across
all API boundaries.

Exports specialized decimal types and schema classes for use across the application.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)

from src.core.decimal_precision import DecimalPrecision

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
        - Implements dictionary validation for decimal precision

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

    @classmethod
    def model_validate(cls, obj, *, strict=False, from_attributes=True, context=None):
        """Override model_validate to add timezone info to naive datetimes.

        This method intercepts the validation process to convert any naive datetime
        objects to UTC-aware datetimes before field validation occurs. This is
        especially useful when converting SQLAlchemy models (which use naive
        datetimes) to Pydantic models.

        Args:
            obj: The object to validate
            strict: Whether to enforce strict validation
            from_attributes: Whether to extract data from object attributes
            context: Optional validation context

        Returns:
            The validated model
        """
        if from_attributes and hasattr(obj, "__dict__"):
            # Create a copy of the object's dict to avoid modifying the original
            obj_dict = dict(obj.__dict__)

            # Add UTC timezone to datetime fields
            for field_name, field_value in obj_dict.items():
                if isinstance(field_value, datetime) and field_value.tzinfo is None:
                    obj_dict[field_name] = field_value.replace(tzinfo=timezone.utc)

            # Use the modified dict for validation
            return super().model_validate(obj_dict, strict=strict, context=context)

        # Fall back to standard validation for non-object inputs
        return super().model_validate(
            obj, strict=strict, from_attributes=from_attributes, context=context
        )

    @field_validator("*", mode="before")
    @classmethod
    def validate_datetime_fields(cls, value: Any) -> Any:
        """Validates that all datetime fields have UTC timezone.

        Args:
            value: The field value to validate

        Returns:
            The original value if validation passes

        Raises:
            ValueError: If a datetime field is naive (no timezone) or not in UTC
        """
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise ValueError(
                    f"Datetime must be UTC. "
                    f"Got naive datetime: {value}. "
                    "Please provide datetime with UTC timezone (e.g., with Z suffix in ISO format)."
                )
            if value.utcoffset().total_seconds() != 0:
                raise ValueError(
                    f"Datetime must be UTC. "
                    f"Got datetime with non-UTC offset: {value} (offset: {value.utcoffset()}). "
                    "Please provide datetime with UTC timezone (offset zero)."
                )
        return value

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

            # Check dictionary field types based on the field annotation
            annotation = field_info.annotation

            # Handle MoneyDict fields
            if annotation in (MoneyDict, IntMoneyDict):
                for key, value in field_value.items():
                    if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
                        raise ValueError(
                            f"Dictionary value for key '{key}' should have no more than 2 decimal places"
                        )

            # Handle PercentageDict fields
            elif annotation in (PercentageDict, IntPercentageDict):
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

            # Handle CorrelationDict fields
            elif annotation == CorrelationDict:
                for key, value in field_value.items():
                    if isinstance(value, Decimal):
                        # Check decimal places
                        if value.as_tuple().exponent < -4:
                            raise ValueError(
                                f"Dictionary value for key '{key}' should have no more than 4 decimal places"
                            )
                        # Check range
                        if value < -1 or value > 1:
                            raise ValueError(
                                f"Correlation value for key '{key}' must be between -1 and 1"
                            )

            # Handle RatioDict fields
            elif annotation == RatioDict:
                for key, value in field_value.items():
                    if isinstance(value, Decimal) and value.as_tuple().exponent < -4:
                        raise ValueError(
                            f"Dictionary value for key '{key}' should have no more than 4 decimal places"
                        )

        return self

    @model_validator(mode="after")
    def ensure_datetime_fields_are_utc(self) -> "BaseSchemaValidator":
        """Ensures all datetime fields have UTC timezone after model initialization.

        This validator runs after the model is created and ensures that
        any datetime fields (including those set by default_factory)
        are properly timezone-aware with UTC timezone.

        This addresses a gap where values created by default_factory
        could bypass the regular field validation and remain naive.

        Important: Naive datetimes are assumed to be in the local timezone
        and are converted to their UTC equivalent, not just labeled with UTC.

        Args:
            self: The model instance

        Returns:
            The model instance with timezone-aware datetime fields
        """
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, datetime) and field_value.tzinfo is None:
                # Get the local timezone
                local_tz = datetime.now().astimezone().tzinfo

                # For naive datetimes (e.g., from default_factory=datetime.now),
                # first make it timezone-aware as local time
                aware_local_dt = field_value.replace(tzinfo=local_tz)

                # Then convert to UTC - this adjusts the actual time value
                utc_dt = aware_local_dt.astimezone(timezone.utc)

                # Update the field with the properly converted UTC datetime
                setattr(self, field_name, utc_dt)
        return self
        
    @model_validator(mode="after")
    def validate_required_fields_not_none(self) -> "BaseSchemaValidator":
        """
        Validates that required fields are not set to None in update schemas.
        
        This validator only applies to schemas that are likely to be used for updates
        (those with 'Update' in their name) to prevent setting required fields to None.
        """
        # Only apply this validation to Update schemas
        if not self.__class__.__name__.endswith('Update'):
            return self
            
        for field_name, field_value in self.__dict__.items():
            # Skip fields that weren't explicitly set
            if field_name not in self.__pydantic_fields_set__:
                continue
                
            # Check if field is None
            if field_value is None:
                # Get the model class this schema is associated with
                model_class = getattr(self.__class__, '__model__', None)
                
                # If we can't determine the model class, use a heuristic approach
                if model_class is None:
                    # Try to infer model class name from schema name (e.g., AccountUpdate -> Account)
                    model_name = self.__class__.__name__.replace('Update', '')
                    # Import the model dynamically (this is a fallback and may not always work)
                    try:
                        import importlib
                        models_module = importlib.import_module('src.models')
                        model_class = getattr(models_module, model_name, None)
                    except (ImportError, AttributeError):
                        model_class = None
                
                # If we have a model class, check if the field is non-nullable
                if model_class and hasattr(model_class, '__table__'):
                    column = getattr(model_class.__table__.columns, field_name, None)
                    if column and not column.nullable:
                        raise ValueError(f"Field '{field_name}' cannot be set to None (database column is non-nullable)")
                
        return self
