from fastapi import APIRouter, Depends, File, UploadFile, Query
from typing import Optional

from src.services.bulk_import import (
    BulkImportService,
    BulkImportResponse,
    BulkImportPreview
)
from src.services.bills import BillService
from src.services.income import IncomeService
from src.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/bulk-import", tags=["bulk-import"])

async def get_bulk_import_service(db: AsyncSession = Depends(get_db)) -> BulkImportService:
    """Dependency to get BulkImportService instance."""
    bill_service = BillService(db)
    income_service = IncomeService(db)
    return BulkImportService(bill_service, income_service)

@router.post("/bills", response_model=BulkImportResponse)
async def bulk_import_bills(
    file: UploadFile = File(...),
    preview: bool = Query(True, description="Preview mode validates data without importing"),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportResponse:
    """
    Bulk import bills from CSV or JSON file.
    
    - If preview=True, validates data and returns preview without importing
    - If preview=False, validates and imports data
    
    File format requirements:
    - CSV or JSON file
    - Required fields: month, day_of_month, bill_name, amount, account_id
    - Optional fields: auto_pay, splits (JSON array for bill splits)
    """
    return await service.import_bills(file, preview)

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

@router.post("/bills/preview", response_model=BulkImportPreview)
async def preview_bills_import(
    file: UploadFile = File(...),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportPreview:
    """
    Preview bills import data with validation results.
    Returns validated records and any validation errors found.
    """
    return await service.preview_bills_import(file)

@router.post("/income/preview", response_model=BulkImportPreview)
async def preview_income_import(
    file: UploadFile = File(...),
    service: BulkImportService = Depends(get_bulk_import_service)
) -> BulkImportPreview:
    """
    Preview income import data with validation results.
    Returns validated records and any validation errors found.
    """
    return await service.preview_income_import(file)
