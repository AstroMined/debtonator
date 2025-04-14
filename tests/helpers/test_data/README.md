# Test Data Files

This directory contains sample data files used for testing file-based operations in Debtonator. These files serve as controlled test inputs for validating data import, validation, and processing functionality.

## Purpose

The test data files serve several important purposes:

1. **Testing Import Functionality**: Provide input files for testing data import functions
2. **Validation Testing**: Include both valid and invalid data to test validation logic
3. **Format Testing**: Demonstrate handling of different file formats (CSV, JSON, etc.)
4. **Boundary Testing**: Contain edge cases to test boundary conditions
5. **Consistent Test Data**: Ensure tests have consistent, version-controlled test inputs

## File Categories

### Valid Data Files

Files that contain properly formatted data that should pass validation:

- `valid_liabilities.csv`: Sample CSV file with valid bill/liability data
- `valid_income.json`: Sample JSON file with valid income data

### Invalid Data Files

Files that contain improperly formatted data to test validation error handling:

- `invalid_liabilities.csv`: CSV file with invalid bill/liability data
- `invalid_income.json`: JSON file with invalid income data

## Usage in Tests

These files are used in various test modules to validate file processing functionality:

```python
import os
from pathlib import Path

async def test_import_liability_csv():
    # Get path to test data file
    test_file_path = Path(__file__).parent.parent / "helpers" / "test_data" / "valid_liabilities.csv"
    
    # Test import function
    result = await import_service.import_liabilities_from_csv(test_file_path)
    
    # Verify import worked correctly
    assert len(result.imported) > 0
    assert len(result.errors) == 0
```

## File Format Specifications

### CSV Files

- Use comma (`,`) as delimiter
- Include header row
- Use UTF-8 encoding
- Follow RFC 4180 CSV format standards
- Date format: YYYY-MM-DD
- Decimal format: Period (`.`) as decimal separator

### JSON Files

- Valid JSON format according to RFC 8259
- UTF-8 encoding
- Array of objects structure for collections
- ISO 8601 date format (YYYY-MM-DDTHH:MM:SSZ)
- Properly nested objects for complex structures

## Adding New Test Files

When adding new test files:

1. Follow the naming convention: `{valid|invalid}_{entity_type}.{extension}`
2. Include both valid and invalid versions for comprehensive testing
3. Add small, focused files rather than large comprehensive ones
4. Include representative samples of all field types
5. Document any specific test cases included in the file
6. Ensure files use proper encoding (UTF-8)

## Related Documentation

- [Integration Tests for File Operations](../../integration/services/import/README.md)
- [Data Import Service](../../../../src/services/import/README.md)
