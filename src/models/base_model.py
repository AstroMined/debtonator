from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from zoneinfo import ZoneInfo

from ..database.base import Base

class BaseDBModel(Base):
    """
    Base model class that provides common fields and functionality for all models.
    
    All datetime fields are stored in UTC format. Timezone awareness is enforced through
    Pydantic schemas rather than SQLAlchemy models. This approach provides:
    - Consistent UTC storage in the database
    - Schema-level validation of UTC datetimes
    - Clear separation of storage and validation concerns
    """
    
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        default=lambda: datetime.now(ZoneInfo("UTC")),
        nullable=False,
        doc="UTC timestamp of when the record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        default=lambda: datetime.now(ZoneInfo("UTC")),
        onupdate=lambda: datetime.now(ZoneInfo("UTC")),
        nullable=False,
        doc="UTC timestamp of when the record was last updated"
    )
