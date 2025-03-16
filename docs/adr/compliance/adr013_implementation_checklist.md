# ADR-013 Implementation Checklist

This checklist details all tasks required to fully implement ADR-013 (Decimal Precision Handling) across the Debtonator application. The checklist is organized by implementation area and includes specific files and changes needed.

## 1. Core Module Implementation

- [ ] Create `src/core` directory if it doesn't exist
- [ ] Create `src/core/decimal_precision.py` with the following components:
  - [ ] `DecimalPrecision` class with constants for display and calculation precision
  - [ ] `round_for_display()` method for 2 decimal place rounding
  - [ ] `round_for_calculation()` method for 4 decimal place rounding
  - [ ] `validate_input_precision()` method for input validation
  - [ ] `distribute_with_largest_remainder()` for equal distribution
  - [ ] `distribute_by_percentage()` for percentage-based distribution

## 2. Database Schema Updates

- [ ] Create an Alembic migration to update all 37 database decimal fields:
  - [ ] Change all 37 `Numeric(10, 2)` columns to `Numeric(12, 4)` (see detailed list below)
  - [ ] Add a data migration component to scale existing data appropriately

### Database Fields to Update (37 fields):

```
src/models/accounts.py:
- Account.available_balance: Numeric(10, 2) → Numeric(12, 4)
- Account.available_credit: Numeric(10, 2) → Numeric(12, 4)
- Account.total_limit: Numeric(10, 2) → Numeric(12, 4)
- Account.last_statement_balance: Numeric(10, 2) → Numeric(12, 4)

src/models/liabilities.py:
- Liability.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/bill_splits.py:
- BillSplit.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/payments.py:
- Payment.amount: Numeric(10, 2) → Numeric(12, 4)
- PaymentSource.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/income.py:
- Income.amount: Numeric(10, 2) → Numeric(12, 4)
- Income.undeposited_amount: Numeric(10, 2) → Numeric(12, 4)

src/models/balance_history.py:
- BalanceHistory.balance: Numeric(10, 2) → Numeric(12, 4)
- BalanceHistory.available_credit: Numeric(10, 2) → Numeric(12, 4)

src/models/transaction_history.py:
- TransactionHistory.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/credit_limit_history.py:
- CreditLimitHistory.credit_limit: Numeric(10, 2) → Numeric(12, 4)

src/models/recurring_bills.py:
- RecurringBill.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/recurring_income.py:
- RecurringIncome.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/statement_history.py:
- StatementHistory.statement_balance: Numeric(10, 2) → Numeric(12, 4)
- StatementHistory.minimum_payment: Numeric(10, 2) → Numeric(12, 4)

src/models/balance_reconciliation.py:
- BalanceReconciliation.previous_balance: Numeric(10, 2) → Numeric(12, 4)
- BalanceReconciliation.new_balance: Numeric(10, 2) → Numeric(12, 4)
- BalanceReconciliation.adjustment_amount: Numeric(10, 2) → Numeric(12, 4)

src/models/deposit_schedules.py:
- DepositSchedule.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/payment_schedules.py:
- PaymentSchedule.amount: Numeric(10, 2) → Numeric(12, 4)

src/models/cashflow.py:
- CashflowForecast.total_bills: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.total_income: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.balance: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.forecast: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.min_14_day: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.min_30_day: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.min_60_day: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.min_90_day: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.daily_deficit: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.yearly_deficit: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.required_income: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.hourly_rate_40: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.hourly_rate_30: Numeric(10, 2) → Numeric(12, 4)
- CashflowForecast.hourly_rate_20: Numeric(10, 2) → Numeric(12, 4)
```

## 3. SQLAlchemy Model Updates

- [ ] Update model definitions to match new database column precision:
  - [ ] `src/models/accounts.py` - Update field definitions
  - [ ] `src/models/liabilities.py` - Update field definitions
  - [ ] `src/models/bill_splits.py` - Update field definitions
  - [ ] `src/models/payments.py` - Update field definitions
  - [ ] `src/models/income.py` - Update field definitions
  - [ ] `src/models/balance_history.py` - Update field definitions
  - [ ] `src/models/transaction_history.py` - Update field definitions
  - [ ] `src/models/credit_limit_history.py` - Update field definitions
  - [ ] `src/models/recurring_bills.py` - Update field definitions
  - [ ] `src/models/recurring_income.py` - Update field definitions
  - [ ] `src/models/statement_history.py` - Update field definitions
  - [ ] `src/models/balance_reconciliation.py` - Update field definitions
  - [ ] `src/models/deposit_schedules.py` - Update field definitions
  - [ ] `src/models/payment_schedules.py` - Update field definitions
  - [ ] `src/models/cashflow.py` - Update field definitions

## 4. Pydantic Schema Updates

- [ ] Ensure all Pydantic schema files (150 fields across 21 schema files) maintain 2 decimal place validation at API boundaries:
  - [ ] Verify validation in `src/schemas/accounts.py`
  - [ ] Verify validation in `src/schemas/bill_splits.py`
  - [ ] Verify validation in `src/schemas/liabilities.py`
  - [ ] Verify validation in `src/schemas/payments.py`
  - [ ] Verify validation in `src/schemas/realtime_cashflow.py`
  - [ ] Verify validation in `src/schemas/credit_limits.py`
  - [ ] Verify validation in `src/schemas/balance_history.py`
  - [ ] Verify validation in `src/schemas/balance_reconciliation.py`
  - [ ] Verify validation in `src/schemas/deposit_schedules.py`
  - [ ] Verify validation in `src/schemas/impact_analysis.py`
  - [ ] Verify validation in `src/schemas/income_trends.py`
  - [ ] Verify validation in `src/schemas/income.py`
  - [ ] Verify validation in `src/schemas/payment_patterns.py`
  - [ ] Verify validation in `src/schemas/payment_schedules.py`
  - [ ] Verify validation in `src/schemas/recommendations.py`
  - [ ] Verify validation in `src/schemas/recurring_bills.py`
  - [ ] Verify validation in `src/schemas/transactions.py`
  - [ ] Verify validation in `src/schemas/cashflow/account_analysis.py`
  - [ ] Verify validation in `src/schemas/cashflow/base.py`
  - [ ] Verify validation in `src/schemas/cashflow/forecasting.py`
  - [ ] Verify validation in `src/schemas/cashflow/historical.py`
  - [ ] Verify validation in `src/schemas/cashflow/metrics.py`

- [ ] Update the one special case:
  - [ ] Ensure `BalanceDistribution.percentage_of_total` maintains 4 decimal places (in `src/schemas/cashflow/account_analysis.py`)

## 5. Update `BaseSchemaValidator` Class

- [ ] Update base schema validator to reference the new DecimalPrecision core module:
  - [ ] Modify the `validate_decimal_precision` method in appropriate base schema file
  - [ ] Use the `DecimalPrecision.validate_input_precision` method
  - [ ] Ensure this validation is consistently applied across all schema files

## 6. Service Layer Updates

Update service classes that handle decimal calculations to use the new `DecimalPrecision` core module:

### Critical Services to Update:

- [ ] `src/services/bill_splits.py`:
  - [ ] Update split calculation logic to use `distribute_with_largest_remainder()`
  - [ ] Ensure internal calculations use 4 decimal places
  - [ ] Round to 2 decimal places at API boundaries

- [ ] `src/services/payments.py`:
  - [ ] Update payment distribution logic
  - [ ] Use 4 decimal places for internal calculations
  - [ ] Round to 2 decimal places when returning results

- [ ] `src/services/balance_history.py`:
  - [ ] Use 4 decimal places for running balance calculations
  - [ ] Round appropriately at API boundaries

- [ ] `src/services/cashflow.py`:
  - [ ] Update forecast calculations to use 4 decimal precision internally
  - [ ] Round to 2 decimal places at API boundaries

- [ ] `src/services/impact_analysis.py`:
  - [ ] Use 4 decimal places for all percentage and distribution calculations
  - [ ] Round to 2 decimal places at API boundaries

### Additional Services That Work with Decimal Values:

- [ ] `src/services/accounts.py`:
  - [ ] Update balance calculation methods
  - [ ] Ensure proper rounding when returning values

- [ ] `src/services/liabilities.py`:
  - [ ] Update amount handling
  - [ ] Ensure proper precision in calculations

- [ ] `src/services/recurring_bills.py`:
  - [ ] Update amount calculations
  - [ ] Apply proper rounding

- [ ] `src/services/income.py`:
  - [ ] Update amount calculations
  - [ ] Apply proper rounding

## 7. API Response Update

- [ ] Update API response handling in `src/api/base.py` or other relevant files:
  - [ ] Ensure all monetary values are rounded to 2 decimal places before returning to clients
  - [ ] Special handling for the one 4-decimal field (percentage_of_total)
  - [ ] Consider creating a response formatter method using the DecimalPrecision core module

- [ ] Address any API endpoints that directly return decimal values:
  - [ ] Review `src/api/v1/` endpoints
  - [ ] Apply consistent rounding to all returned decimal values

## 8. Test Updates

Update test cases to account for new precision rules:

### Model Tests:
- [ ] `tests/unit/models/test_bill_splits.py` - Update assertions for 4 decimal precision
- [ ] `tests/unit/models/test_payments.py` - Update assertions for payment distribution
- [ ] `tests/unit/models/test_accounts.py` - Update balance calculation tests
- [ ] Add tests for other models with decimal fields

### Schema Tests:
- [ ] `tests/unit/schemas/test_bill_splits.py` - Update validation tests
- [ ] `tests/unit/schemas/test_payments.py` - Update validation tests
- [ ] `tests/unit/schemas/test_accounts.py` - Update validation tests
- [ ] Add tests for decimal precision validation across all schema files
- [ ] Ensure input validation still enforces 2 decimal places at boundaries
- [ ] Update tests to verify 4 decimal places are allowed in internal calculations

### Service Tests:
- [ ] `tests/unit/services/test_bill_splits.py` - Update service-level tests
- [ ] `tests/unit/services/test_payments.py` - Update service-level tests
- [ ] `tests/unit/services/test_accounts.py` - Update service-level tests
- [ ] Add tests for services that handle calculations with decimal values

### Core Module Tests:
- [ ] Create `tests/unit/core/test_decimal_precision.py`:
  - [ ] Test `round_for_display()`
  - [ ] Test `round_for_calculation()`
  - [ ] Test `validate_input_precision()`
  - [ ] Test `distribute_with_largest_remainder()`
  - [ ] Test `distribute_by_percentage()`

### Integration Tests:
- [ ] `tests/integration/services/test_bill_splits.py`:
  - [ ] Test equal distribution with largest remainder method
  - [ ] Verify exact total is preserved after splitting
- [ ] `tests/integration/services/test_payments.py`:
  - [ ] Test payment distribution across multiple sources
- [ ] `tests/integration/services/test_balance_history.py`:
  - [ ] Test running balance calculations maintain accuracy
- [ ] `tests/integration/api/test_bill_splits.py`:
  - [ ] Test API responses have 2 decimal places
  - [ ] Test bill splitting preserves totals

### Special Test Cases:
- [ ] Test the "$100 split three ways" case to ensure $33.33 + $33.33 + $33.34 = $100.00
- [ ] Test percentage-based distributions to verify totals match
- [ ] Test running calculations that could accumulate rounding errors
- [ ] Test edge cases (e.g., very small values, very large values)

## 9. Documentation Updates

- [ ] Update ADR-013 with implementation details:
  - [ ] Add core module approach to Technical Details section
  - [ ] Update any examples to reflect final implementation

- [ ] Update technical documentation for decimal precision handling:
  - [ ] Create developer guide for working with monetary values
  - [ ] Update API documentation to reflect precision expectations

## 10. Developer Guidelines

- [ ] Create developer guidelines document `docs/guides/working_with_money.md`:
  - [ ] When to use 4 vs 2 decimal places
  - [ ] How to use the `DecimalPrecision` core module
  - [ ] Common patterns for financial calculations
  - [ ] Testing best practices for financial calculations
  - [ ] Handling edge cases
  - [ ] How to use the distribution utilities

## 11. Quality Assurance

- [ ] Conduct full test suite run with new changes
- [ ] Verify all tests pass with new decimal precision handling
- [ ] Manually test critical financial operations with various inputs
- [ ] Verify rounding behavior in edge cases
- [ ] Check database migration works correctly
- [ ] Verify API responses maintain correct precision
