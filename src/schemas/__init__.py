from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
from typing import Any

class BaseSchemaValidator(BaseModel):
    """Base schema validator that enforces UTC timezone for all datetime fields.
    
    All schema classes should inherit from this base class to ensure consistent
    datetime handling across the application.
    
    Example:
        class PaymentCreate(BaseSchemaValidator):
            payment_date: datetime
            # The base validator will automatically enforce UTC timezone
    """
    
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

    class Config:
        """Pydantic config for consistent datetime handling."""
        json_encoders = {
            # Ensure datetimes are serialized to ISO format with Z suffix
            datetime: lambda dt: dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        }
