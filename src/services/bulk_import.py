import csv
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import List, Optional, Tuple, Union

from fastapi import UploadFile
from pydantic import BaseModel, ValidationError

from src.models.income import Income
from src.models.liabilities import Liability
from src.schemas.categories import CategoryCreate
from src.schemas.income import IncomeCreate
from src.schemas.liabilities import LiabilityCreate
from src.services.categories import CategoryService
from src.services.income import IncomeService
from src.services.liabilities import LiabilityService


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
    records: List[Union[LiabilityCreate, IncomeCreate]]
    validation_errors: List[ImportError]
    total_records: int


async def process_csv_content(content: bytes) -> List[dict]:
    """Process CSV content and return list of dictionaries."""
    reader = csv.DictReader(StringIO(content.decode("utf-8")))
    return [row for row in reader]


async def process_json_content(content: bytes) -> List[dict]:
    """Process JSON content and return list of dictionaries."""
    return json.loads(content.decode("utf-8"))


class BulkImportService:
    def __init__(
        self,
        liability_service: LiabilityService,
        income_service: IncomeService,
        category_service: CategoryService,
    ):
        self.liability_service = liability_service
        self.income_service = income_service
        self.category_service = category_service

    async def validate_liability_record(
        self, record: dict, row_num: int
    ) -> Tuple[Optional[LiabilityCreate], Optional[ImportError]]:
        """Validate a single liability record."""
        try:
            # Convert amount to Decimal
            try:
                amount = Decimal(str(record.get("amount", "0")))
            except (ValueError, InvalidOperation):
                return None, ImportError(
                    row=row_num, field="amount", message="Invalid amount format"
                )

            # Validate and convert date components
            try:
                month = int(record.get("month", "1"))
                day = int(record.get("day_of_month", "1"))
                if not (1 <= month <= 12 and 1 <= day <= 31):
                    raise ValueError("Invalid date")
                due_date = datetime.strptime(f"{month}/{day}/2025", "%m/%d/%Y").date()
            except ValueError:
                return None, ImportError(
                    row=row_num, field="date", message="Invalid date format or values"
                )

            # Get or create category based on account_name
            account_name = record.get("account_name", "Uncategorized")
            try:
                # First try to get existing category
                category = await self.category_service.get_category_by_name(
                    account_name
                )

                # If category doesn't exist, try to get Uncategorized
                if not category and account_name != "Uncategorized":
                    category = await self.category_service.get_category_by_name(
                        "Uncategorized"
                    )

                # If still no category, create a new one
                if not category:
                    try:
                        category = await self.category_service.create_category(
                            CategoryCreate(
                                name=account_name,
                                description=f"Auto-created category for {account_name}",
                            )
                        )
                    except Exception as e:
                        # If we failed to create the requested category, try using Uncategorized
                        if account_name != "Uncategorized":
                            try:
                                category = await self.category_service.create_category(
                                    CategoryCreate(
                                        name="Uncategorized",
                                        description="Default category for uncategorized items",
                                    )
                                )
                            except Exception:
                                return None, ImportError(
                                    row=row_num,
                                    field="account_name",
                                    message=f"Failed to create category: {str(e)}",
                                )
                        else:
                            return None, ImportError(
                                row=row_num,
                                field="account_name",
                                message=f"Failed to create category: {str(e)}",
                            )
            except Exception as e:
                return None, ImportError(
                    row=row_num,
                    field="account_name",
                    message=f"Failed to process category: {str(e)}",
                )

            if not category:
                return None, ImportError(
                    row=row_num,
                    field="account_name",
                    message="Failed to get or create category",
                )

            # Build liability data with required fields
            liability_data = {
                "name": record.get("bill_name"),
                "amount": amount,
                "due_date": due_date,
                "category_id": category.id,
                "recurring": True,  # All imported bills are recurring by default
                "recurrence_pattern": {"frequency": "monthly", "day": str(day)},
                "primary_account_id": int(
                    record.get("primary_account_id", "1")
                ),  # Default to account ID 1
            }

            liability = LiabilityCreate(**liability_data)
            return liability, None
        except ValidationError as e:
            error = ImportError(
                row=row_num,
                field=str(e.errors()[0]["loc"][0]),
                message=str(e.errors()[0]["msg"]),
            )
            return None, error
        except (ValueError, json.JSONDecodeError) as e:
            error = ImportError(row=row_num, field="unknown", message=str(e))
            return None, error

    async def validate_income_record(
        self, record: dict, row_num: int
    ) -> Tuple[Optional[IncomeCreate], Optional[ImportError]]:
        """Validate a single income record."""
        try:
            # Convert amount to Decimal
            try:
                if "amount" in record:
                    record["amount"] = Decimal(str(record["amount"]))
            except (ValueError, InvalidOperation):
                return None, ImportError(
                    row=row_num, field="amount", message="Invalid amount format"
                )

            # Convert date string to date object
            try:
                if "date" in record:
                    record["date"] = datetime.strptime(
                        record["date"], "%Y-%m-%d"
                    ).date()
            except ValueError:
                return None, ImportError(
                    row=row_num, field="date", message="Invalid date format"
                )

            income = IncomeCreate(**record)
            return income, None
        except ValidationError as e:
            error = ImportError(
                row=row_num,
                field=str(e.errors()[0]["loc"][0]),
                message=str(e.errors()[0]["msg"]),
            )
            return None, error
        except ValueError as e:
            error = ImportError(row=row_num, field="unknown", message=str(e))
            return None, error

    async def process_file(self, file: UploadFile) -> List[dict]:
        """Process uploaded file and return list of records."""
        content = await file.read()
        await file.seek(0)  # Reset file position for future reads
        if file.filename.endswith(".csv"):
            return await process_csv_content(content)
        elif file.filename.endswith(".json"):
            return await process_json_content(content)
        else:
            raise ValueError(
                "Unsupported file format. Please upload CSV or JSON files only."
            )

    async def preview_liabilities_import(self, file: UploadFile) -> BulkImportPreview:
        """Preview liabilities import data with validation."""
        records = await self.process_file(file)
        await file.seek(0)  # Reset file position for future reads
        validated_records = []
        validation_errors = []

        for i, record in enumerate(records, 1):
            # Validate required fields first
            required_fields = [
                "bill_name",
                "amount",
                "month",
                "day_of_month",
                "account_name",
            ]
            missing_fields = [
                field for field in required_fields if not record.get(field)
            ]

            if missing_fields:
                for field in missing_fields:
                    validation_errors.append(
                        ImportError(
                            row=i,
                            field=field,
                            message=f"Missing required field: {field}",
                        )
                    )
                continue

            # Proceed with full validation if all required fields are present
            liability, error = await self.validate_liability_record(record, i)
            if liability:
                validated_records.append(liability)
            if error:
                validation_errors.append(error)

        return BulkImportPreview(
            records=validated_records,
            validation_errors=validation_errors,
            total_records=len(records),
        )

    async def preview_income_import(self, file: UploadFile) -> BulkImportPreview:
        """Preview income import data with validation."""
        records = await self.process_file(file)
        await file.seek(0)  # Reset file position for future reads
        validated_records = []
        validation_errors = []

        for i, record in enumerate(records, 1):
            income, error = await self.validate_income_record(record, i)
            if income:
                validated_records.append(income)
            if error:
                validation_errors.append(error)

        return BulkImportPreview(
            records=validated_records,
            validation_errors=validation_errors,
            total_records=len(records),
        )

    async def import_liabilities(
        self, file: UploadFile, preview: bool = True
    ) -> Union[BulkImportResponse, BulkImportPreview]:
        """Import liabilities from file."""
        if preview:
            return await self.preview_liabilities_import(file)

        await file.seek(0)  # Reset file position
        preview_result = await self.preview_liabilities_import(file)

        # Return early if there are validation errors
        if preview_result.validation_errors:
            return BulkImportResponse(
                success=False,
                processed=preview_result.total_records,
                succeeded=0,
                failed=len(preview_result.validation_errors),
                errors=preview_result.validation_errors,
            )

        succeeded = 0
        failed = 0
        errors = []

        # Process each validated record
        for i, liability in enumerate(preview_result.records, 1):
            try:
                # Create the liability and verify it was created
                created_liability = await self.liability_service.create_liability(
                    liability
                )
                if created_liability:
                    succeeded += 1
                else:
                    failed += 1
                    errors.append(
                        ImportError(
                            row=i,
                            field="db_operation",
                            message="Failed to create liability record",
                        )
                    )
            except Exception as e:
                failed += 1
                errors.append(ImportError(row=i, field="db_operation", message=str(e)))

        return BulkImportResponse(
            success=failed == 0,
            processed=len(preview_result.records),
            succeeded=succeeded,
            failed=failed,
            errors=errors if errors else None,
        )

    async def import_income(
        self, file: UploadFile, preview: bool = True
    ) -> Union[BulkImportResponse, BulkImportPreview]:
        """Import income records from file."""
        if preview:
            return await self.preview_income_import(file)

        await file.seek(0)  # Reset file position
        preview_result = await self.preview_income_import(file)
        if preview_result.validation_errors:
            return BulkImportResponse(
                success=False,
                processed=preview_result.total_records,
                succeeded=0,
                failed=len(preview_result.validation_errors),
                errors=preview_result.validation_errors,
            )

        succeeded = 0
        failed = 0
        errors = []

        for i, income in enumerate(preview_result.records, 1):
            try:
                await self.income_service.create(income)
                succeeded += 1
            except Exception as e:
                failed += 1
                errors.append(ImportError(row=i, field="db_operation", message=str(e)))

        return BulkImportResponse(
            success=failed == 0,
            processed=len(preview_result.records),
            succeeded=succeeded,
            failed=failed,
            errors=errors if errors else None,
        )
