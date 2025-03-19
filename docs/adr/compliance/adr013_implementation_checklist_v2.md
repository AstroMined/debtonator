# ADR-013 Implementation Checklist (Pydantic V2 Approach)

## Implementation Strategy Update (3/18/2025)

**Critical Update**: Due to `ConstrainedDecimal` being completely removed in Pydantic V2, we are pivoting to a new implementation approach using Pydantic V2's recommended pattern with Annotated types. This document replaces the previous implementation checklist with a Pydantic V2-compatible approach.

The new approach maintains the same goals as the original ADR-013:
1. Two-tier precision model (2 decimal places for UI/API, 4 decimal places for calculations)
2. Proper validation at API boundaries
3. Distribution utilities for handling common financial scenarios

However, instead of using custom field methods and validation logic, we'll now use Python's Annotated types combined with Pydantic's Field constraints, which is the recommended approach in Pydantic V2.

## Implementation Progress (Updated 3/19/2025)

**Major Update**: All schema files have now been updated to use the Pydantic V2-compatible Annotated types approach. This completes a major milestone in our implementation of decimal precision handling with Pydantic V2 compatibility.

We have started implementing the Pydantic V2 compatible approach, with progress shown below:

| Area | Total Items | Completed | Remaining | Progress | Notes |
|------|-------------|-----------|-----------|----------|-------|
| Core Module | 10 | 10 | 0 | 100% | No changes needed |
| Database Schema | 37 | 37 | 0 | 100% | No changes needed |
| SQLAlchemy Models | 15 | 15 | 0 | 100% | No changes needed |
| Pydantic Schemas | 22 | 22 | 0 | 100% | All 22 schema files updated |
| BaseSchemaValidator | 5 | 5 | 0 | 100% | Implemented with Annotated types |
| Service Layer | 9 | 9 | 0 | 100% | May need minor updates |
| API Response | 2 | 2 | 0 | 100% | No changes needed |
| Core Tests | 10 | 10 | 0 | 100% | No changes needed |
| Model Tests | 3 | 3 | 0 | 100% | No changes needed |
| Schema Tests | 6 | 6 | 0 | 100% | Updated all test files to match new validation patterns |
| Service Tests | 3 | 0 | 3 | 0% | Need implementation |
| Integration Tests | 5 | 3 | 2 | 60% | Minor updates needed |
| Special Test Cases | 4 | 4 | 0 | 100% | No changes needed |
| Documentation | 2 | 1 | 1 | 50% | Need to update ADR-013 documentation |
| Developer Guidelines | 6 | 6 | 0 | 100% | Need minor updates |
| Dictionary Validation | 5 | 5 | 0 | 100% | Implemented in BaseSchemaValidator |
| Quality Assurance | 7 | 0 | 7 | 0% | Need implementation |
| **TOTAL** | **151** | **138** | **13** | **91%** | Progress improved from 91% |

## Remaining Priority Tasks

1. **Update All Schema Files** ✓
   - Completed all 22 schema files (100%)
   - All utility method calls replaced with direct type annotations
   - Dictionary field validation implemented
   - All files now using Pydantic V2-compatible Annotated types approach

2. **Update Schema Tests** ✓
   - Updated all schema test files to reflect new validation behavior
   - Added tests for dictionary validation
   - Updated error message expectations to match Pydantic V2 patterns

3. **Update Documentation**
   - Update ADR-013 with the new implementation approach
   - Update developer guidelines with new patterns

4. **Update Service Tests**
   - Complete remaining service tests

## Phase 1: Core Type Definitions

### Update `src/schemas/__init__.py` with Annotated Types

- [x] Replace utility methods with Annotated type definitions:
  ```python
  from typing import Annotated, Dict
  from decimal import Decimal
  from pydantic import Field

  # 2 decimal places for monetary values
  MoneyDecimal = Annotated[
      Decimal,
      Field(multiple_of=Decimal("0.01"))
  ]

  # 4 decimal places for percentage values (0-1 range)
  PercentageDecimal = Annotated[
      Decimal,
      Field(ge=0, le=1, multiple_of=Decimal("0.0001"))
  ]

  # 4 decimal places for correlation values (-1 to 1 range)
  CorrelationDecimal = Annotated[
      Decimal,
      Field(ge=-1, le=1, multiple_of=Decimal("0.0001"))
  ]

  # 4 decimal places for general ratio values (no min/max)
  RatioDecimal = Annotated[
      Decimal,
      Field(multiple_of=Decimal("0.0001"))
  ]
  ```

- [x] Add dictionary type definitions:
  ```python
  # Dictionary type aliases
  MoneyDict = Dict[str, MoneyDecimal]
  PercentageDict = Dict[str, PercentageDecimal]
  IntMoneyDict = Dict[int, MoneyDecimal]
  IntPercentageDict = Dict[int, PercentageDecimal]
  ```

- [x] Remove the now-obsolete utility methods from BaseSchemaValidator:
  - [x] Remove `money_field()` method
  - [x] Remove `percentage_field()` method
  - [x] Update `validate_decimal_precision()` validator or replace with appropriate validator for dictionary fields

- [x] Add comprehensive documentation for the types:
  - [x] Add docstrings for each type
  - [x] Include usage examples
  - [x] Explain validation behavior

## Phase 2: Dictionary Validation Strategy

- [x] Implement dictionary validation strategy:
  - [x] Create custom dictionary classes with validation:
    ```python
    class ValidatedMoneyDict(Dict[str, Decimal]):
        """Dictionary for monetary values that enforces 2 decimal places."""
        # Implementation details
    ```
  - [x] Add validator for dictionaries to BaseSchemaValidator:
    ```python
    @model_validator(mode='after')
    def validate_decimal_dictionaries(self) -> 'BaseSchemaValidator':
        """Validate that all dictionary fields with decimal values for proper precision."""
        # Implementation details
    ```

## Phase 3: Schema Updates ✓

All Pydantic schema files have been updated to use the new Annotated types:

- [x] Update critical schema files first:
  - [x] Update `src/schemas/accounts.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/bill_splits.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/liabilities.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/payments.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/balance_history.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/balance_reconciliation.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/credit_limits.py` - Replace utility methods with direct type annotations

- [x] Update cashflow schema files:
  - [x] Update `src/schemas/cashflow/account_analysis.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/cashflow/base.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/cashflow/forecasting.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/cashflow/historical.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/cashflow/metrics.py` - Replace utility methods with direct type annotations

- [x] Update remaining schema files:
  - [x] Update `src/schemas/balance_history.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/balance_reconciliation.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/credit_limits.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/deposit_schedules.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/impact_analysis.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/income_categories.py` - No decimal fields to update
  - [x] Update `src/schemas/income_trends.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/income.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/payment_patterns.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/payment_schedules.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/realtime_cashflow.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/recommendations.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/recurring_bills.py` - Replace utility methods with direct type annotations
  - [x] Update `src/schemas/transactions.py` - Replace utility methods with direct type annotations

- [x] Update special case for percentage fields:
  - [x] Ensure `BalanceDistribution.percentage_of_total` uses `PercentageDecimal` type

## Phase 4: Test Updates ✓

Updated all schema tests to account for the new validation behavior:

- [x] Updated schema test files:
  - [x] Updated `tests/unit/schemas/test_accounts_schemas.py` - Update validation tests for new error messages
  - [x] Updated `tests/unit/schemas/test_bill_splits_schemas.py` - Update validation tests for new error messages
  - [x] Updated `tests/unit/schemas/test_payments_schemas.py` - Update validation tests for new error messages
  - [x] Updated `tests/unit/schemas/test_deposit_schedules_schemas.py` - Update validation tests for new error messages
  - [x] Updated `tests/unit/schemas/test_credit_limits_schemas.py` - Update validation tests for new error messages
  - [x] Updated `tests/unit/schemas/test_balance_history_schemas.py` - Update validation tests for new error messages
  - [x] Updated cashflow schema test files (previously completed)

- [x] Added dictionary validation tests:
  - [x] Tested `MoneyDict` validation behavior
  - [x] Tested `PercentageDict` validation behavior
  - [x] Tested validation of nested dictionaries
  - [x] Tested validation of dictionaries with invalid values

- [x] Updated error message expectations:
  - [x] Updated expected error messages to match Pydantic V2's format
  - [x] Updated assertions in all tests

## Phase 5: Service Tests

- [ ] `tests/unit/services/test_bill_splits.py` - Implement service-level tests:
  - [ ] Test equal distribution with largest remainder method
  - [ ] Test special cases like "$100 split three ways"
  - [ ] Test precision handling in distribution

- [ ] `tests/unit/services/test_payments.py` - Implement service-level tests:
  - [ ] Test payment distribution across multiple sources
  - [ ] Test validation of payment source totals

- [ ] `tests/unit/services/test_accounts.py` - Implement service-level tests:
  - [ ] Test balance calculation with 4 decimal precision
  - [ ] Test rounding behavior at API boundaries

## Phase 6: Documentation Updates

- [ ] Update ADR-013 with the new implementation approach:
  - [ ] Add section on Pydantic V2 compatibility
  - [ ] Update examples to use Annotated types
  - [ ] Explain why this approach was chosen

- [x] Update `docs/guides/working_with_money.md`:
  - [x] Update examples to use the new types
  - [x] Add section on dictionary validation
  - [x] Provide examples of common patterns with the new approach

## Phase 7: Integration Tests

- [ ] Complete remaining integration tests:
  - [ ] `tests/integration/services/test_bill_splits.py` - Test equal distribution
  - [ ] `tests/integration/services/test_payments.py` - Test payment distribution

## Phase 8: Quality Assurance

- [ ] Conduct full test suite run with new implementation
- [ ] Verify all tests pass
- [ ] Manually test critical financial operations
- [ ] Verify rounding behavior in edge cases
- [ ] Verify API responses maintain correct precision
- [ ] Verify validation for different precision levels
- [ ] Check for any potential regressions

## Benefits of the New Approach

1. **Pydantic V2 Compatibility**: Uses Pydantic's recommended pattern with Annotated types
2. **Type Safety**: Provides distinct types that carry their validation rules with them
3. **Cleaner Schema Code**: Field constraints are declared alongside the field definition
4. **Simpler Mental Model**: Direct type annotations are easier to understand than utility methods
5. **Better IDE Integration**: Improved type hints for better IDE support
6. **Future-Proof**: Aligned with Pydantic's design direction

## Pre-implementation Checklist

Before beginning implementation, verify:

- [ ] All team members understand the new approach
- [ ] Test environment is set up to quickly verify changes
- [ ] Plan for handling any data migration edge cases
- [ ] Backup of the current implementation
- [ ] Clear rollback strategy if issues are encountered
