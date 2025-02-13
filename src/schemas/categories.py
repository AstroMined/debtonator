from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field, validator

if TYPE_CHECKING:
    from ..models.liabilities import Liability

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    @validator('parent_id')
    def validate_parent_id(cls, v, values):
        if v is not None and v == values.get('id'):
            raise ValueError("Category cannot be its own parent")
        return v

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    
    @validator('parent_id')
    def validate_parent_id(cls, v, values):
        if v is not None and v == values.get('id'):
            raise ValueError("Category cannot be its own parent")
        return v

class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    full_path: str = Field(description="Full hierarchical path of the category")

class CategoryWithChildren(Category):
    children: List["CategoryWithChildren"] = []

class CategoryWithParent(Category):
    parent: Optional[CategoryWithChildren] = None

class CategoryWithBills(CategoryWithChildren):
    bills: List["Liability"] = []

# Needed for forward references
CategoryWithChildren.model_rebuild()
