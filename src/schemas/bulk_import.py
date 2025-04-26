"""
Bulk import schemas.

This module defines schemas used for bulk data import operations,
including error tracking, import responses, and import previews.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from src.schemas.income import IncomeCreate
from src.schemas.liabilities import LiabilityCreate


class ImportError(BaseModel):
    """
    Schema for import errors.
    
    Tracks the row, field, and error message for import validation failures.
    """
    row: int = Field(..., description="Row number where the error occurred")
    field: str = Field(..., description="Field name where the error occurred")
    message: str = Field(..., description="Error message")


class BulkImportResponse(BaseModel):
    """
    Schema for bulk import operation response.
    
    Contains detailed information about the results of a bulk import operation,
    including success/failure counts and validation errors.
    """
    success: bool = Field(..., description="Overall success status of the import")
    processed: int = Field(..., description="Total number of records processed")
    succeeded: int = Field(..., description="Number of records successfully imported")
    failed: int = Field(..., description="Number of records that failed to import")
    errors: Optional[List[ImportError]] = Field(
        None, description="List of validation errors if any"
    )


class BulkImportPreview(BaseModel):
    """
    Schema for bulk import preview.
    
    Contains validation information and records that passed validation
    before committing the import.
    """
    records: List[Union[LiabilityCreate, IncomeCreate]] = Field(
        ..., description="List of validated records ready for import"
    )
    validation_errors: List[ImportError] = Field(
        ..., description="List of validation errors"
    )
    total_records: int = Field(
        ..., description="Total number of records in the original file"
    )
