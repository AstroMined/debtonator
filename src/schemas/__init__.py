from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Any

class BaseSchemaValidator(BaseModel):
    """Base schema validator that enforces UTC timezone for all datetime fields.
    
    All schema classes should inherit from this base class to ensure consistent
    datetime handling across the application.
    
    Features:
        - Automatically converts naive datetimes to UTC-aware during model_validate
        - Enforces UTC timezone for all datetime fields through validation
        - Provides consistent datetime serialization to ISO format with Z suffix
    
    Example:
        class PaymentCreate(BaseSchemaValidator):
            payment_date: datetime
            # The base validator will automatically enforce UTC timezone
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
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_decimal_precision(cls, value: Any) -> Any:
        """Validates that decimal values don't exceed 2 decimal places.
        
        TODO: This is a temporary solution that strictly validates decimal
        precision to 2 decimal places. A proper architectural decision is
        needed for how to handle decimal precision in financial calculations.
        
        Future considerations:
        - Allow more precision (4-6 decimal places) for internal calculations
        - Enforce 2 decimal places for external inputs/outputs
        - Implement proper rounding strategies for boundary operations
        - Document precision handling policies
        
        See upcoming ADR for "Decimal Precision Handling".
        
        Args:
            value: The field value to validate
            
        Returns:
            The original value if validation passes
            
        Raises:
            ValueError: If a Decimal field has more than 2 decimal places
        """
        if isinstance(value, Decimal):
            # Check if it has more than 2 decimal places
            if value.as_tuple().exponent < -2:  # exponent is negative, so < -2 means more decimal places
                raise ValueError("Decimal input should have no more than 2 decimal places")
        return value

    # model_config defined once at the top of the class
