from pydantic import BaseModel, Field
from typing import Optional

class IncomeCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class IncomeCategoryCreate(IncomeCategoryBase):
    pass

class IncomeCategoryUpdate(IncomeCategoryBase):
    pass

class IncomeCategory(IncomeCategoryBase):
    id: int

    class Config:
        from_attributes = True
