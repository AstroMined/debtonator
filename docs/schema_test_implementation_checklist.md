# Schema Test Implementation Plan

## Overview
This document outlines our plan to achieve 100% test coverage for all schema files following the recent refactoring. Each schema file will have a corresponding test file with comprehensive test cases covering validation rules, constraints, and edge cases.

## Timezone Compliance Fix (CRITICAL)

To ensure all test files properly align with ADR-011 and use the exact same timezone mechanism as the production code, we need to make the following changes to all test files:

### Required Changes:
- Replace `from zoneinfo import ZoneInfo` with `from datetime import timezone` (keeping ZoneInfo only for non-UTC timezone tests)
- Replace all instances of `datetime.now(ZoneInfo("UTC"))` with `datetime.now(timezone.utc)`
- Replace all instances of other UTC datetime creations to use `timezone.utc` instead of `ZoneInfo("UTC")`
- Keep `ZoneInfo` usage only for creating non-UTC timezones in negative test cases
- When creating non-UTC timezones, use `timezone(timedelta(hours=X))` pattern, not `timezone(hours=X)`
- Important: Remember to import timedelta: `from datetime import datetime, timezone, timedelta`

### Issue Discovered and Fixed:
We found and fixed an issue with non-UTC timezone creation in the test files. The correct pattern is to use `timezone(timedelta(hours=X))` and not `timezone(hours=X)`, as the `timezone` constructor requires a `timedelta` object for its offset parameter.

### Rationale:
- ADR-011 explicitly states "All new Python datetimes are created with UTC explicitly set, such as `datetime.now(timezone.utc)`"
- The actual implementation in `BaseSchemaValidator` uses `timezone.utc` from the standard library
- We need to match the production code's UTC time approach for consistency and correctness
- This ensures our tests properly validate the schemas' behavior with the same timezone mechanism

### Files Requiring Timezone Fixes:
1. **Completed Files (Timezone Fixes Implemented):**
   - [x] tests/schemas/test_balance_reconciliation_schemas.py (FIXED)
   - [x] tests/schemas/test_bill_splits_schemas.py (FIXED)
   - [x] tests/schemas/test_categories_schemas.py (FIXED)
   - [x] tests/schemas/test_credit_limits_schemas.py (FIXED)

2. **Existing Test Files (Need Review & Timezone Updates):**
   - [ ] tests/schemas/test_accounts_schemas.py (UPDATE + TIMEZONE FIX)
   - [ ] tests/schemas/test_income_schemas.py (UPDATE + TIMEZONE FIX)
   - [ ] tests/schemas/test_liabilities_schemas.py (UPDATE + TIMEZONE FIX)
   - [ ] tests/schemas/test_payments_schemas.py (UPDATE + TIMEZONE FIX)
   - [ ] tests/schemas/test_transactions_schemas.py (UPDATE + TIMEZONE FIX)
   - [ ] tests/schemas/test_analysis_schemas.py (REVIEW + TIMEZONE FIX)

3. **New Test Files:**
   - [ ] All new test files should use `timezone.utc` from the start

## Test Organization Structure
- Each schema file will have a corresponding test file named `test_FILENAME_schemas.py`
- Test files will follow a consistent structure with standard test categories
- All tests will verify ADR-011 and ADR-012 compliance

## Files to Create or Update

### Phase 1: Core Schema Tests

#### 1. tests/schemas/test_balance_reconciliation_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test business rule validations
- [x] Test BaseSchemaValidator inheritance

#### 2. tests/schemas/test_bill_splits_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test business rule validations
- [x] Test BaseSchemaValidator inheritance

#### 3. tests/schemas/test_categories_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test parent/child relationship validations
- [x] Test UTC datetime validation
- [x] Test business rule validations
- [x] Test BaseSchemaValidator inheritance

#### 4. tests/schemas/test_credit_limits_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test business rule validations
- [x] Test BaseSchemaValidator inheritance

### Phase 2: Financial Operation Schema Tests

#### 5. tests/schemas/test_balance_history_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test business rule validations
- [x] Test BaseSchemaValidator inheritance

#### 6. tests/schemas/test_payment_schedules_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test recurring pattern validations
- [x] Test BaseSchemaValidator inheritance

#### 7. tests/schemas/test_deposit_schedules_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test recurring pattern validations
- [x] Test BaseSchemaValidator inheritance

#### 8. tests/schemas/test_recurring_bills_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test recurring pattern validations
- [x] Test BaseSchemaValidator inheritance

### Phase 3: Analysis Schema Tests

#### 9. tests/schemas/test_cashflow_base_schemas.py
- [ ] Import and validate core cashflow schema classes (CashflowBase, CashflowCreate, etc.)
- [ ] Test valid object creation
- [ ] Test field validations (required fields, constraints)
- [ ] Test decimal precision for monetary fields
- [ ] Test UTC datetime validation
- [ ] Test calculation validations
- [ ] Test BaseSchemaValidator inheritance

#### 10. tests/schemas/test_cashflow_metrics_schemas.py
- [ ] Import and validate metrics schema classes (MinimumRequired, DeficitCalculation, HourlyRates)
- [ ] Test valid object creation
- [ ] Test field validations (required fields, constraints)
- [ ] Test decimal precision for monetary fields
- [ ] Test calculation validations
- [ ] Test BaseSchemaValidator inheritance

#### 11. tests/schemas/test_cashflow_account_analysis_schemas.py
- [ ] Import and validate account analysis schema classes (AccountCorrelation, TransferPattern, etc.)
- [ ] Test valid object creation
- [ ] Test field validations (required fields, constraints)
- [ ] Test decimal precision for monetary fields
- [ ] Test UTC datetime validation
- [ ] Test relationship validations
- [ ] Test BaseSchemaValidator inheritance

#### 12. tests/schemas/test_cashflow_forecasting_schemas.py
- [ ] Import and validate forecasting schema classes (CustomForecastParameters, AccountForecastRequest, etc.)
- [ ] Test valid object creation
- [ ] Test field validations (required fields, constraints)
- [ ] Test decimal precision for monetary fields
- [ ] Test UTC datetime validation
- [ ] Test forecast parameter validations
- [ ] Test BaseSchemaValidator inheritance

#### 13. tests/schemas/test_cashflow_historical_schemas.py
- [ ] Import and validate historical analysis schema classes (HistoricalTrendMetrics, SeasonalityAnalysis, etc.)
- [ ] Test valid object creation
- [ ] Test field validations (required fields, constraints)
- [ ] Test decimal precision for monetary fields
- [ ] Test UTC datetime validation
- [ ] Test historical analysis validations
- [ ] Test BaseSchemaValidator inheritance

#### 14. tests/schemas/test_impact_analysis_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test analysis parameter validations
- [x] Test BaseSchemaValidator inheritance

#### 15. tests/schemas/test_income_trends_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test trend calculation validations
- [x] Test BaseSchemaValidator inheritance

#### 16. tests/schemas/test_payment_patterns_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test pattern analysis validations
- [x] Test BaseSchemaValidator inheritance

#### 17. tests/schemas/test_realtime_cashflow_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test realtime calculation validations
- [x] Test BaseSchemaValidator inheritance

#### 18. tests/schemas/test_recommendations_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test decimal precision for monetary fields
- [x] Test UTC datetime validation
- [x] Test recommendation algorithm validations
- [x] Test BaseSchemaValidator inheritance

#### 19. tests/schemas/test_income_categories_schemas.py
- [x] Import and validate all schema classes
- [x] Test valid object creation
- [x] Test field validations (required fields, constraints)
- [x] Test category relationship validations
- [x] Test UTC datetime validation (N/A - no datetime fields)
- [x] Test business rule validations (N/A - no custom validators)
- [x] Test BaseSchemaValidator inheritance

### Phase 4: Review and Update Existing Test Files

#### 20. tests/schemas/test_accounts_schemas.py (UPDATE)
- [ ] Review for completeness against current schema
- [ ] Add tests for any missing validation rules
- [ ] Ensure proper testing of BaseSchemaValidator functionality
- [ ] Verify ADR-011 and ADR-012 compliance tests
- [ ] Add tests for recent schema enhancements

#### 21. tests/schemas/test_income_schemas.py (UPDATE)
- [ ] Review for completeness against current schema
- [ ] Add tests for any missing validation rules
- [ ] Ensure proper testing of BaseSchemaValidator functionality
- [ ] Verify ADR-011 and ADR-012 compliance tests
- [ ] Add tests for recent schema enhancements

#### 22. tests/schemas/test_liabilities_schemas.py (UPDATE)
- [ ] Review for completeness against current schema
- [ ] Add tests for any missing validation rules
- [ ] Ensure proper testing of BaseSchemaValidator functionality
- [ ] Verify ADR-011 and ADR-012 compliance tests
- [ ] Add tests for recent schema enhancements

#### 23. tests/schemas/test_payments_schemas.py (UPDATE)
- [ ] Review for completeness against current schema
- [ ] Add tests for any missing validation rules
- [ ] Ensure proper testing of BaseSchemaValidator functionality
- [ ] Verify ADR-011 and ADR-012 compliance tests
- [ ] Add tests for recent schema enhancements

#### 24. tests/schemas/test_transactions_schemas.py (UPDATE)
- [ ] Review for completeness against current schema
- [ ] Add tests for any missing validation rules
- [ ] Ensure proper testing of BaseSchemaValidator functionality
- [ ] Verify ADR-011 and ADR-012 compliance tests
- [ ] Add tests for recent schema enhancements

#### 25. tests/schemas/test_analysis_schemas.py (REVIEW)
- [ ] Determine corresponding schema file(s)
- [ ] Review for completeness against current schema(s)
- [ ] Add tests for any missing validation rules
- [ ] Ensure proper testing of BaseSchemaValidator functionality
- [ ] Verify ADR-011 and ADR-012 compliance tests
- [ ] Add tests for recent schema enhancements

## Test Template

Each test file will follow this standard template:

```python
from datetime import datetime, timezone
from decimal import Decimal
import pytest
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests
from pydantic import ValidationError

from src.schemas.SCHEMA_FILE import (
    # Import all schema classes from the file
)

def test_schema_class_valid():
    """Test valid schema creation with all fields"""
    now = datetime.now(timezone.utc)  # Use timezone.utc per ADR-011
    # Create valid instance with required fields
    # Assert fields match expectations

def test_schema_class_optional_fields():
    """Test schema creation with optional fields"""
    # Create instance with optional fields
    # Assert optional fields match expectations

def test_schema_class_required_fields():
    """Test required field validation"""
    # Test missing required fields raise ValidationError
    # Check error messages

def test_schema_class_field_constraints():
    """Test field constraint validation"""
    # Test min/max values
    # Test string length constraints
    # Test enum constraints
    # Test custom constraints

def test_schema_class_decimal_precision():
    """Test decimal precision validation"""
    # Test decimal fields with too many decimal places
    # Test decimal fields with valid decimal places

def test_schema_class_datetime_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime rejection
    # Test non-UTC timezone rejection
    # Test valid UTC datetime acceptance

def test_schema_class_business_rules():
    """Test business rule validation"""
    # Test any cross-field validation rules
    # Test conditional validation rules

# Additional tests for custom validation logic...
```

## Fixtures and Helpers

We'll utilize existing fixtures in conftest.py and add new ones as needed:

- Use existing datetime fixtures for UTC and non-UTC testing
- Create schema-specific fixtures for common test data
- Add helper functions for repetitive validation testing

## Test Execution Strategy

For each phase:
1. Implement the test files in the specified order
2. Run tests with pytest to validate functionality
3. Verify test coverage for each schema file
4. Address any gaps or issues found during testing
5. Document any special cases or considerations

## Success Criteria

- All schema files have corresponding test files
- 100% validation coverage for all schema classes
- All tests pass consistently
- ADR-011 and ADR-012 compliance verified through tests
- Edge cases and business rules properly tested
