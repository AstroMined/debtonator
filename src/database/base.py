from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

# Define naming convention for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create a base metadata instance with proper dialect options
metadata = MetaData(
    naming_convention=NAMING_CONVENTION
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name"""
        return cls.__name__.lower()

    # Use the configured metadata
    metadata = metadata

# Import all models at the bottom to avoid circular imports
from ..models import (
    accounts,
    bill_splits,
    recurring_bills,
    income,
    cashflow,
    liabilities,
    payments,
    categories
)

__all__ = [
    "Base",
    "accounts",
    "bill_splits",
    "recurring_bills",
    "income",
    "cashflow",
    "liabilities",
    "payments",
    "categories"
]
