from decimal import Decimal
from typing import List, Optional, Tuple, Union
import csv
import json
from datetime import datetime
from io import StringIO

from fastapi import UploadFile
from pydantic import BaseModel, ValidationError

from src.models.bills import Bill
from src.models.income import Income
from src.schemas.bills import BillCreate
from src.schemas.income import IncomeCreate
from src.services.bills import BillService
from src.services.income import IncomeService

class ImportError(BaseModel):
    row: int
    field: str
    message: str

class BulkImportResponse(BaseModel):
    success: bool
    processed: int
    succeeded: int
    failed: int
    errors: Optional[List[ImportError]] = None

class BulkImportPreview(BaseModel):
    records: List[Union[BillCreate, IncomeCreate]]
    validation_errors: List[ImportError]
    total_records: int

async def process_csv_content(content: str) -> List[dict]:
    """Process CSV content and return list of dictionaries."""
    reader = csv.DictReader(StringIO(content.decode('utf-8')))
    return [row for row in reader]

async def process_json_content(content: str) -> List[dict]:
    """Process JSON content and return list of dictionaries."""
    return json.loads(content.decode('utf-8'))

async def validate_bill_record(record: dict, row_num: int) -> Tuple[Optional[BillCreate], Optional[ImportError]]:
    """Validate a single bill record."""
    try:
        # Convert string amount to Decimal
        if 'amount' in record:
            record['amount'] = Decimal(str(record['amount']))
        
        # Parse splits if present
        if 'splits' in record and isinstance(record['splits'], str):
            record['splits'] = json.loads(record['splits'])

        bill = BillCreate(**record)
        return bill, None
    except ValidationError as e:
        error = ImportError(
            row=row_num,
            field=str(e.errors()[0]['loc'][0]),
            message=str(e.errors()[0]['msg'])
        )
        return None, error
    except (ValueError, json.JSONDecodeError) as e:
        error = ImportError(
            row=row_num,
            field='unknown',
            message=str(e)
        )
        return None, error

async def validate_income_record(record: dict, row_num: int) -> Tuple[Optional[IncomeCreate], Optional[ImportError]]:
    """Validate a single income record."""
    try:
        # Convert string amount to Decimal
        if 'amount' in record:
            record['amount'] = Decimal(str(record['amount']))
        
        income = IncomeCreate(**record)
        return income, None
    except ValidationError as e:
        error = ImportError(
            row=row_num,
            field=str(e.errors()[0]['loc'][0]),
            message=str(e.errors()[0]['msg'])
        )
        return None, error
    except ValueError as e:
        error = ImportError(
            row=row_num,
            field='unknown',
            message=str(e)
        )
        return None, error

class BulkImportService:
    def __init__(self, bill_service: BillService, income_service: IncomeService):
        self.bill_service = bill_service
        self.income_service = income_service

    async def process_file(self, file: UploadFile) -> List[dict]:
        """Process uploaded file and return list of records."""
        content = await file.read()
        if file.filename.endswith('.csv'):
            return await process_csv_content(content)
        elif file.filename.endswith('.json'):
            return await process_json_content(content)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or JSON files only.")

    async def preview_bills_import(self, file: UploadFile) -> BulkImportPreview:
        """Preview bills import data with validation."""
        records = await self.process_file(file)
        validated_records = []
        validation_errors = []

        for i, record in enumerate(records, 1):
            bill, error = await validate_bill_record(record, i)
            if bill:
                validated_records.append(bill)
            if error:
                validation_errors.append(error)

        return BulkImportPreview(
            records=validated_records,
            validation_errors=validation_errors,
            total_records=len(records)
        )

    async def preview_income_import(self, file: UploadFile) -> BulkImportPreview:
        """Preview income import data with validation."""
        records = await self.process_file(file)
        validated_records = []
        validation_errors = []

        for i, record in enumerate(records, 1):
            income, error = await validate_income_record(record, i)
            if income:
                validated_records.append(income)
            if error:
                validation_errors.append(error)

        return BulkImportPreview(
            records=validated_records,
            validation_errors=validation_errors,
            total_records=len(records)
        )

    async def import_bills(self, file: UploadFile, preview: bool = True) -> BulkImportResponse:
        """Import bills from file."""
        if preview:
            return await self.preview_bills_import(file)

        preview_result = await self.preview_bills_import(file)
        if preview_result.validation_errors:
            return BulkImportResponse(
                success=False,
                processed=preview_result.total_records,
                succeeded=0,
                failed=len(preview_result.validation_errors),
                errors=preview_result.validation_errors
            )

        succeeded = 0
        failed = 0
        errors = []

        for i, bill in enumerate(preview_result.records, 1):
            try:
                await self.bill_service.create_bill(bill)
                succeeded += 1
            except Exception as e:
                failed += 1
                errors.append(ImportError(
                    row=i,
                    field='db_operation',
                    message=str(e)
                ))

        return BulkImportResponse(
            success=failed == 0,
            processed=len(preview_result.records),
            succeeded=succeeded,
            failed=failed,
            errors=errors if errors else None
        )

    async def import_income(self, file: UploadFile, preview: bool = True) -> BulkImportResponse:
        """Import income records from file."""
        if preview:
            return await self.preview_income_import(file)

        preview_result = await self.preview_income_import(file)
        if preview_result.validation_errors:
            return BulkImportResponse(
                success=False,
                processed=preview_result.total_records,
                succeeded=0,
                failed=len(preview_result.validation_errors),
                errors=preview_result.validation_errors
            )

        succeeded = 0
        failed = 0
        errors = []

        for i, income in enumerate(preview_result.records, 1):
            try:
                await self.income_service.create_income(income)
                succeeded += 1
            except Exception as e:
                failed += 1
                errors.append(ImportError(
                    row=i,
                    field='db_operation',
                    message=str(e)
                ))

        return BulkImportResponse(
            success=failed == 0,
            processed=len(preview_result.records),
            succeeded=succeeded,
            failed=failed,
            errors=errors if errors else None
        )
