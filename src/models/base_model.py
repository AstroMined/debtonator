from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..database.base import Base

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
