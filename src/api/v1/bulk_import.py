from fastapi import APIRouter, Depends, File, UploadFile, Query
from typing import Optional

from src.services.bulk_import import (
    BulkImportService,
    BulkImportResponse,
    BulkImportPreview
)
from src.services.liabilities import LiabilityService
from src.services.income import IncomeService
from src.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/bulk-import", tags=["bulk-import"])

async def get_bulk_import_service(db: AsyncSession = Depends(get_db)) -> BulkImportService:
    """Dependency to get BulkImportService instance."""
    liability_service = LiabilityService(db)
    income_service = IncomeService(db)
    return BulkImportService(liability_service, income_service)

@router.post("/liabilities", response_model=BulkImportResponse)
async def bulk_import_liabilities(
    file: UploadFile = File(...),
    preview: bool = Query(True, description="Preview mode validates data without importing"),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportResponse:
    """
    Bulk import liabilities from CSV or JSON file.
    
    - If preview=True, validates data and returns preview without importing
    - If preview=False, validates and imports data
    
    File format requirements:
    - CSV or JSON file
    - Required fields: month, day_of_month, bill_name, amount, account_id
    - Optional fields: auto_pay, splits (JSON array for bill splits)
    
    Note: This endpoint replaces the deprecated /bills endpoint.
    """
    return await service.import_liabilities(file, preview)

@router.post("/income", response_model=BulkImportResponse)
async def bulk_import_income(
    file: UploadFile = File(...),
    preview: bool = Query(True, description="Preview mode validates data without importing"),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportResponse:
    """
    Bulk import income records from CSV or JSON file.
    
    - If preview=True, validates data and returns preview without importing
    - If preview=False, validates and imports data
    
    File format requirements:
    - CSV or JSON file
    - Required fields: date, source, amount
    - Optional fields: deposited, account_id
    """
    return await service.import_income(file, preview)

@router.post("/liabilities/preview", response_model=BulkImportPreview)
async def preview_liabilities_import(
    file: UploadFile = File(...),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportPreview:
    """
    Preview liabilities import data with validation results.
    Returns validated records and any validation errors found.
    
    Note: This endpoint replaces the deprecated /bills/preview endpoint.
    """
    return await service.preview_liabilities_import(file)
# Keep old endpoints for backward compatibility
@router.post("/bills", response_model=BulkImportResponse, deprecated=True)
async def bulk_import_bills(
    file: UploadFile = File(...),
    preview: bool = Query(True, description="Preview mode validates data without importing"),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportResponse:
    """
    DEPRECATED: Use /liabilities endpoint instead.
    Bulk import bills from CSV or JSON file.
    """
    return await service.import_liabilities(file, preview)

@router.post("/bills/preview", response_model=BulkImportPreview, deprecated=True)
async def preview_bills_import(
    file: UploadFile = File(...),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportPreview:
    """
    DEPRECATED: Use /liabilities/preview endpoint instead.
    Preview bills import data with validation results.
    """
    return await service.preview_liabilities_import(file)
