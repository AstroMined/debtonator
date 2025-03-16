from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel, field_validator, model_validator, ConfigDict, Field
from typing import Any

from src.core.decimal_precision import DecimalPrecision

class BaseSchemaValidator(BaseModel):
    """Base schema validator that enforces UTC timezone for all datetime fields
    and decimal precision for monetary values.
    
    All schema classes should inherit from this base class to ensure consistent
    datetime and decimal handling across the application.
    
    Features:
        - Automatically converts naive datetimes to UTC-aware during model_validate
        - Enforces UTC timezone for all datetime fields through validation
        - Provides consistent datetime serialization to ISO format with Z suffix
        - Enforces 2 decimal places for monetary values at API boundaries
        - Supports special case handling for percentage fields (4 decimal places)
        - Provides utility methods for creating standardized field definitions
    
    Example:
        class PaymentCreate(BaseSchemaValidator):
            payment_date: datetime
            amount: Decimal = BaseSchemaValidator.money_field("Payment amount")
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            # Ensure datetimes are serialized to ISO format with Z suffix
            datetime: lambda dt: dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        }
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
        return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)
    
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
    
    @classmethod
    def money_field(cls, description: str, **kwargs) -> Field:
        """
        Creates a standard monetary field with 2 decimal places.
        
        Implementing ADR-013, this method standardizes the creation of monetary
        fields with proper decimal precision validation.
        
        Args:
            description: Field description
            **kwargs: Additional Field parameters
            
        Returns:
            Field: Configured Field instance with decimal_places=2
        """
        return Field(
            decimal_places=2,
            description=description,
            **kwargs
        )
    
    @classmethod
    def percentage_field(cls, description: str, **kwargs) -> Field:
        """
        Creates a percentage field with 4 decimal places.
        
        This special case is for percentage fields that require higher precision,
        as specified in ADR-013.
        
        Args:
            description: Field description
            **kwargs: Additional Field parameters
            
        Returns:
            Field: Configured Field instance with decimal_places=4
        """
        return Field(
            decimal_places=4,
            ge=0,
            le=1,
            description=description,
            **kwargs
        )
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_decimal_precision(cls, value: Any) -> Any:
        """Validates that decimal values don't exceed the specified decimal places at API boundaries.
        
        Implements ADR-013 "Decimal Precision Handling" which establishes:
        - 2 decimal places (0.01) for user inputs and outputs at API boundaries
        - 4 decimal places (0.0001) for internal calculations to maintain precision
        - Special case for percentage fields with 4 decimal places
        
        This validator enforces the API boundary rule to ensure all incoming decimal
        values have appropriate decimal places for consistency and to meet user expectations.
        
        Field-specific precision is determined by checking the decimal_places parameter
        in the Field definition. Fields using BaseSchemaValidator.percentage_field()
        will have 4 decimal places, while all other monetary fields default to 2.
        
        Internal calculations are allowed to use higher precision (4 decimal places),
        but must be rounded appropriately when returned to the user.
        
        Args:
            value: The field value to validate
            
        Returns:
            The original value if validation passes
            
        Raises:
            ValueError: If a Decimal field has more than the allowed decimal places
        """
        if isinstance(value, Decimal):
            # Check if we're in a field validation (field name is available)
            field_name = getattr(cls.validate_decimal_precision, 'field_name', None)
            
            if field_name and field_name in cls.model_fields:
                field_info = cls.model_fields[field_name]
                # Check if this field has a custom decimal_places setting
                if hasattr(field_info, 'json_schema_extra') and field_info.json_schema_extra and 'decimal_places' in field_info.json_schema_extra:
                    decimal_places = field_info.json_schema_extra['decimal_places']
                    if decimal_places != 2:
                        # Special handling for non-standard precision (e.g., 4 decimal places for percentages)
                        if value.as_tuple().exponent < -decimal_places:
                            raise ValueError(f"Value must have at most {decimal_places} decimal places")
                        return value
            
            # Standard case: Use the DecimalPrecision utility to validate input precision (2 decimal places)
            if not DecimalPrecision.validate_input_precision(value):
                raise ValueError("Decimal input should have no more than 2 decimal places")
        
        return value

    @model_validator(mode="after")
    def ensure_datetime_fields_are_utc(self) -> 'BaseSchemaValidator':
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
