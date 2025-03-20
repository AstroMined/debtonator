from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import UploadFile

from src.services.bulk_import import BulkImportPreview, BulkImportService
from src.services.categories import CategoryService
from src.services.income import IncomeService
from src.services.liabilities import LiabilityService

TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(scope="function")
def valid_liabilities_file(request):
    path = TEST_DATA_DIR / "valid_liabilities.csv"
    file_handle = open(path, "rb")
    request.addfinalizer(lambda: file_handle.close())
    return UploadFile(filename="valid_liabilities.csv", file=file_handle)


@pytest.fixture(scope="function")
def invalid_liabilities_file(request):
    path = TEST_DATA_DIR / "invalid_liabilities.csv"
    file_handle = open(path, "rb")
    request.addfinalizer(lambda: file_handle.close())
    return UploadFile(filename="invalid_liabilities.csv", file=file_handle)


@pytest.fixture(scope="function")
def valid_income_file(request):
    path = TEST_DATA_DIR / "valid_income.json"
    file_handle = open(path, "rb")
    request.addfinalizer(lambda: file_handle.close())
    return UploadFile(filename="valid_income.json", file=file_handle)


@pytest.fixture(scope="function")
def invalid_income_file(request):
    path = TEST_DATA_DIR / "invalid_income.json"
    file_handle = open(path, "rb")
    request.addfinalizer(lambda: file_handle.close())
    return UploadFile(filename="invalid_income.json", file=file_handle)


@pytest.fixture(scope="function")
def bulk_import_service(db_session):
    liability_service = LiabilityService(db_session)
    income_service = IncomeService(db_session)
    category_service = CategoryService(db_session)
    return BulkImportService(liability_service, income_service, category_service)


@pytest.mark.asyncio
async def test_process_csv_file(bulk_import_service, valid_liabilities_file, request):
    """Test processing a valid CSV file"""
    records = await bulk_import_service.process_file(valid_liabilities_file)
    assert len(records) == 2
    assert records[0]["bill_name"] == "Internet Bill"
    assert records[0]["amount"] == "89.99"
    assert records[1]["bill_name"] == "Phone Bill"
    assert records[1]["amount"] == "75.50"


@pytest.mark.asyncio
async def test_process_json_file(bulk_import_service, valid_income_file, request):
    """Test processing a valid JSON file"""
    records = await bulk_import_service.process_file(valid_income_file)
    assert len(records) == 2
    assert records[0]["source"] == "Salary"
    assert records[0]["amount"] == "5000.00"
    assert records[1]["source"] == "Freelance"
    assert records[1]["amount"] == "1000.00"


@pytest.mark.asyncio
async def test_process_unsupported_file(bulk_import_service, request):
    """Test processing an unsupported file type"""
    file_handle = open(__file__, "rb")
    request.addfinalizer(lambda: file_handle.close())
    file = UploadFile(filename="test.txt", file=file_handle)
    with pytest.raises(ValueError, match="Unsupported file format"):
        await bulk_import_service.process_file(file)


@pytest.mark.asyncio
async def test_preview_valid_liabilities_import(
    bulk_import_service, valid_liabilities_file, base_category, request
):
    """Test previewing valid liabilities import"""
    preview = await bulk_import_service.preview_liabilities_import(
        valid_liabilities_file
    )
    assert preview.total_records == 2
    assert len(preview.records) == 2
    assert len(preview.validation_errors) == 0

    # Verify first record
    liability = preview.records[0]
    assert liability.name == "Internet Bill"
    assert liability.amount == Decimal("89.99")
    assert liability.category_id is not None  # Category should be created
    assert liability.recurring is True
    assert liability.recurrence_pattern == {"frequency": "monthly", "day": "15"}


@pytest.mark.asyncio
async def test_preview_invalid_liabilities_import(
    bulk_import_service, invalid_liabilities_file, request
):
    """Test previewing invalid liabilities import"""
    preview = await bulk_import_service.preview_liabilities_import(
        invalid_liabilities_file
    )
    assert preview.total_records == 2
    assert len(preview.validation_errors) > 0

    # First record should have amount validation error
    error = preview.validation_errors[0]
    assert error.row == 1
    assert "amount" in error.field.lower()


@pytest.mark.asyncio
async def test_preview_valid_income_import(
    bulk_import_service, valid_income_file, base_account, request
):
    """Test previewing valid income import"""
    preview = await bulk_import_service.preview_income_import(valid_income_file)
    assert preview.total_records == 2
    assert len(preview.records) == 2
    assert len(preview.validation_errors) == 0

    # Verify first record
    income = preview.records[0]
    assert income.source == "Salary"
    assert income.amount == Decimal("5000.00")
    assert income.date == date(2025, 3, 15)
    assert income.deposited is False


@pytest.mark.asyncio
async def test_preview_invalid_income_import(
    bulk_import_service, invalid_income_file, request
):
    """Test previewing invalid income import"""
    preview = await bulk_import_service.preview_income_import(invalid_income_file)
    assert preview.total_records == 2
    assert len(preview.validation_errors) > 0

    # First record should have date validation error
    error = preview.validation_errors[0]
    assert error.row == 1
    assert "date" in error.field.lower() or "amount" in error.field.lower()


@pytest.mark.asyncio
async def test_import_valid_liabilities(
    bulk_import_service, valid_liabilities_file, base_account, base_category, request
):
    """Test importing valid liabilities"""
    result = await bulk_import_service.import_liabilities(
        valid_liabilities_file, preview=False
    )
    assert result.success is True
    assert result.processed == 2
    assert result.succeeded == 2
    assert result.failed == 0
    assert result.errors is None


@pytest.mark.asyncio
async def test_import_invalid_liabilities(
    bulk_import_service, invalid_liabilities_file, request
):
    """Test importing invalid liabilities"""
    result = await bulk_import_service.import_liabilities(
        invalid_liabilities_file, preview=False
    )
    assert result.success is False
    assert result.processed == 2
    assert result.succeeded == 0
    assert result.failed > 0
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_import_valid_income(
    bulk_import_service, valid_income_file, base_account, request
):
    """Test importing valid income"""
    result = await bulk_import_service.import_income(valid_income_file, preview=False)
    assert result.success is True
    assert result.processed == 2
    assert result.succeeded == 2
    assert result.failed == 0
    assert result.errors is None


@pytest.mark.asyncio
async def test_import_invalid_income(bulk_import_service, invalid_income_file, request):
    """Test importing invalid income"""
    result = await bulk_import_service.import_income(invalid_income_file, preview=False)
    assert result.success is False
    assert result.processed == 2
    assert result.succeeded == 0
    assert result.failed > 0
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_preview_mode_liabilities(
    bulk_import_service, valid_liabilities_file, base_category, request
):
    """Test liabilities import in preview mode"""
    result = await bulk_import_service.import_liabilities(
        valid_liabilities_file, preview=True
    )
    assert isinstance(result, BulkImportPreview)
    assert result.total_records == 2
    assert len(result.records) == 2
    assert len(result.validation_errors) == 0


@pytest.mark.asyncio
async def test_preview_mode_income(bulk_import_service, valid_income_file, request):
    """Test income import in preview mode"""
    result = await bulk_import_service.import_income(valid_income_file, preview=True)
    assert isinstance(result, BulkImportPreview)
    assert result.total_records == 2
    assert len(result.records) == 2
    assert len(result.validation_errors) == 0
