from datetime import datetime, timezone, time
from typing import Optional
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..database.base import Base

def naive_utc_from_date(
    year: int,
    month: int,
    day: int,
    time_of_day: Optional[time] = None
) -> datetime:
    """
    Creates a naive UTC datetime from date components.
    
    Args:
        year: Full year (e.g., 2025)
        month: Month number (1-12)
        day: Day of month (1-31)
        time_of_day: Optional time component. If None, midnight (00:00:00) is used
        
    Returns:
        datetime: Naive datetime that semantically represents UTC
        
    Example:
        >>> # Create date for bill due on 15th
        >>> due_date = naive_utc_from_date(2025, 3, 15)
        >>> # Create date for payment scheduled at 2pm
        >>> schedule_date = naive_utc_from_date(2025, 3, 15, time(14, 0))
    """
    if time_of_day is None:
        time_of_day = time(0, 0)  # Midnight
        
    # Create timezone-aware UTC datetime
    aware = datetime.combine(
        datetime(year, month, day).date(),
        time_of_day,
        tzinfo=timezone.utc
    )
    
    # Convert to naive
    return aware.replace(tzinfo=None)

def naive_utc_now() -> datetime:
    """
    Returns a naive datetime representing the current UTC time.
    This function ensures that we drop any tzinfo before storing in the DB.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

class BaseDBModel(Base):
    """
    Base model class that provides common fields and functionality for all models.
    
    **Key Points**:
    - All datetime columns here are "naive" in the database, but semantically represent UTC.
    - Timezone enforcement is handled at the Pydantic layer (validation/conversion).
    - This approach provides:
      - Consistent UTC storage (though naive in DB)
      - Clear separation of storage vs. validation/logic
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),            # Naive in the DB, but logically UTC
        default=naive_utc_now, # Store the current UTC time, minus tzinfo
        nullable=False,
        doc="Naive UTC timestamp of when the record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),            # Naive in the DB, but logically UTC
        default=naive_utc_now, # Store the current UTC time, minus tzinfo
        onupdate=naive_utc_now,
        nullable=False,
        doc="Naive UTC timestamp of when the record was last updated"
    )
