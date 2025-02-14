from sqlalchemy import Column, Integer, String, Text
from src.database.base import Base

class IncomeCategory(Base):
    __tablename__ = "income_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
