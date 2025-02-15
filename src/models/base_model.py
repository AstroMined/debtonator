from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from zoneinfo import ZoneInfo

from ..database.base import Base

class BaseDBModel(Base):
    """Base model class that provides common fields and functionality for all models"""
    
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC")),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC")),
        onupdate=lambda: datetime.now(ZoneInfo("UTC")),
        nullable=False
    )
