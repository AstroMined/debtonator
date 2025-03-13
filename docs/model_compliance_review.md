# Model Compliance Review

## Executive Summary

A comprehensive review of the models layer was conducted against ADR-011 (Datetime Standardization) and ADR-012 (Validation Layer Standardization). The review found that most of the codebase is already compliant with both ADRs, with a few minor issues that need addressing.

### Key Findings
- Most datetime fields correctly use naive DateTime columns (ADR-011 compliant)
- Several models contain business logic that needs to be moved to services
- Multiple instances of unused timezone-related imports
- Event listeners being used for validation in some models
- Documentation inconsistencies across models

### Critical Issues
1. Business Logic in Models (ADR-012 Violations)
   - RecurringBill.create_liability()
   - RecurringIncome.create_income_entry()
   - Category.is_ancestor_of() and full_path
   - StatementHistory due date calculation
   - CashflowForecast calculation methods
   - CreditLimitHistory event listener validation

2. Timezone-Related Issues (ADR-011 Cleanup)
   - Unused ZoneInfo imports in multiple files
   - Inconsistent documentation about UTC approach
   - Some comments still reference timezone-aware storage

3. Validation Layer Issues (ADR-012)
   - SQLAlchemy event listeners being used for validation
   - Business rules mixed with data persistence
   - Calculation logic in model methods

## Detailed Reviews

### base_model.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Implementation
```python
# Correct datetime implementation
created_at: Mapped[datetime] = mapped_column(
    DateTime(),            # Naive in DB, logically UTC
    default=naive_utc_now,
    nullable=False
)
```

#### Positive Findings
- Properly implements naive UTC datetime storage
- Provides helpful utility functions for UTC handling
- Clear documentation about UTC approach
- No validation logic present

### accounts.py
#### Current Status
- ADR-011 Compliance: ⚠️ Mostly Compliant
- ADR-012 Compliance: ⚠️ Mostly Compliant

#### Issues Found
- Unused imports: `validates` from SQLAlchemy
- Unused imports: `ZoneInfo`
- Some documentation needs updating

#### Required Changes
```python
# Remove unused imports
from sqlalchemy.orm import validates  # Remove
from zoneinfo import ZoneInfo  # Remove
```

### payments.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Correctly implements naive datetime fields
- No validation logic present
- Clear separation of concerns
- Good documentation

### liabilities.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Excellent documentation of separation of concerns
- Proper naive datetime implementation
- Clear comments about service layer responsibilities
- No validation logic present

### bill_splits.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- No datetime fields
- No validation logic
- Pure data structure
- Good use of relationships and constraints

### cashflow.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Implementation Complete
- Removed unused imports: `ZoneInfo`
- Removed business logic methods:
  * calculate_deficits() - moved to MetricsService.update_cashflow_deficits()
  * calculate_required_income() - moved to MetricsService.update_cashflow_required_income()
  * calculate_hourly_rates() - moved to MetricsService.update_cashflow_hourly_rates()
- Updated model documentation to clearly indicate it's a pure data structure
- Updated model tests to focus only on data structure and persistence
- Created comprehensive service tests for the business logic

#### Service Layer Implementation
```python
# In src/services/cashflow/metrics_service.py
def update_cashflow_deficits(self, forecast: CashflowForecast) -> None:
    """Calculate daily and yearly deficits for a cashflow forecast model."""
    min_amount = min(forecast.min_14_day, forecast.min_30_day, 
                    forecast.min_60_day, forecast.min_90_day)
    forecast.daily_deficit = self.calculate_daily_deficit(min_amount, 14)
    forecast.yearly_deficit = self.calculate_yearly_deficit(forecast.daily_deficit)

def update_cashflow_required_income(self, forecast: CashflowForecast, tax_rate: Decimal = Decimal("0.8")) -> None:
    """Calculate required income for a cashflow forecast model."""
    forecast.required_income = self.calculate_required_income(forecast.yearly_deficit, tax_rate)

def update_cashflow_hourly_rates(self, forecast: CashflowForecast) -> None:
    """Calculate hourly rates for a cashflow forecast model."""
    weekly_required = forecast.required_income / 52
    forecast.hourly_rate_40 = weekly_required / 40
    forecast.hourly_rate_30 = weekly_required / 30
    forecast.hourly_rate_20 = weekly_required / 20

def update_cashflow_all_calculations(self, forecast: CashflowForecast, tax_rate: Decimal = Decimal("0.8")) -> None:
    """Perform all calculations on a cashflow forecast model."""
    self.update_cashflow_deficits(forecast)
    self.update_cashflow_required_income(forecast, tax_rate)
    self.update_cashflow_hourly_rates(forecast)
```

### categories.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ❌ Non-Compliant

#### Issues Found
- Contains business logic:
  * is_ancestor_of() method
  * full_path property
  * _get_parent helper method

#### Required Changes
```python
# Move to service layer
class CategoryService:
    async def get_full_path(self, category: Category) -> str:
        # Implementation here
    
    async def is_ancestor_of(self, category: Category, potential_ancestor: Category) -> bool:
        # Implementation here
```

### credit_limit_history.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Implementation Complete
- Removed SQLAlchemy event listeners for validation
- Added validate_credit_limit_history to AccountService
- Enhanced model documentation with clear data structure focus
- Updated tests to focus on model structure rather than validation
- Improved separation of concerns by moving validation to service layer
- Maintained proper relationship definitions and cascade behavior
- Fixed datetime handling for proper UTC timezone management

#### Service Layer Implementation
```python
# In src/services/accounts.py
async def validate_credit_limit_history(self, account_id: int) -> tuple[bool, Optional[str]]:
    """
    Validate that an account can have credit limit history.
    
    Args:
        account_id: The ID of the account to validate
        
    Returns:
        tuple[bool, Optional[str]]: A tuple where the first element is True if valid,
        and the second element is an error message if invalid
    """
    # Account exists validation
    account = await self.get_account(account_id)
    if not account:
        return False, f"Account with ID {account_id} not found"
    
    # Credit account validation
    if account.type != "credit":
        return False, "Credit limit history can only be created for credit accounts"
    
    return True, None
```

### deposit_schedules.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Proper naive datetime implementation
- Good documentation about UTC approach
- No validation logic
- Pure data structure

### income_categories.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Simple model structure
- No datetime fields
- No validation logic
- Clear documentation

### income.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Excellent documentation about separation of concerns
- Proper naive datetime implementation
- Clear comments about service layer responsibilities
- Good use of constraints

### payment_schedules.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Proper naive datetime implementation
- Good documentation about UTC approach
- No validation logic
- Pure data structure

### recurring_bills.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Implementation Complete
- Removed create_liability() business logic method from model
- Added create_liability_from_recurring() to RecurringBillService
- Updated model documentation as pure data structure
- Fixed test cases to use service method instead of model method
- Enhanced datetime handling in the service layer
- Improved duplicate bill detection logic
- Fixed SQL query to properly compare date/datetime fields
- Added SQLAlchemy func.date() for proper comparison

#### Service Layer Implementation
```python
# In src/services/recurring_bills.py
def create_liability_from_recurring(
    self,
    recurring_bill: RecurringBill,
    month: str,
    year: int
) -> Liability:
    """
    Create a new Liability instance from a recurring bill template.
    
    This method replaces the RecurringBill.create_liability method that
    was moved to the service layer as part of ADR-012 implementation.
    
    Args:
        recurring_bill: The recurring bill template
        month: Month number as string (1-12)
        year: Full year (e.g., 2025)
        
    Returns:
        Liability: New liability instance with proper UTC due date
    """
    liability = Liability(
        name=recurring_bill.bill_name,
        amount=recurring_bill.amount,
        due_date=naive_utc_from_date(year, int(month), recurring_bill.day_of_month),
        primary_account_id=recurring_bill.account_id,
        category_id=recurring_bill.category_id,
        auto_pay=recurring_bill.auto_pay,
        recurring=True,
        recurring_bill_id=recurring_bill.id,
        category=recurring_bill.category  # Set the relationship directly
    )
    return liability
```

### recurring_income.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ❌ Non-Compliant

#### Issues Found
- Contains business logic in create_income_entry() method

#### Required Changes
- Move create_income_entry() method to RecurringIncomeService
- Update documentation to reflect service layer responsibility

```python
# Move to service layer
class RecurringIncomeService:
    def create_income_from_recurring(
        self,
        recurring_income: RecurringIncome,
        month: int,
        year: int
    ) -> Income:
        # Implementation here
```

### statement_history.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ❌ Non-Compliant

#### Issues Found
- Contains business logic in __init__ method for due date calculation

#### Required Changes
- Move due date calculation to service layer
```python
class StatementService:
    def calculate_due_date(self, statement_date: datetime) -> datetime:
        return statement_date + timedelta(days=25)
```

### transaction_history.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Positive Findings
- Proper naive datetime implementation
- Clear focus on data persistence
- No validation logic present
- Good documentation

### schemas/__init__.py
#### Current Status
- ADR-011 Compliance: ✅ Compliant
- ADR-012 Compliance: ✅ Compliant

#### Implementation Complete
- Enhanced BaseSchemaValidator with automatic datetime conversion
- Added override of model_validate method to add timezone info
- Fixed date/datetime comparison issues in services
- Eliminated repetitive timezone conversion across services
- Maintained proper validation for explicit user input
- Improved error messages for datetime validation failures

#### Implementation Details
```python
# In src/schemas/__init__.py
class BaseSchemaValidator(BaseModel):
    """Base schema validator that enforces UTC timezone for all datetime fields.
    
    All schema classes should inherit from this base class to ensure consistent
    datetime handling across the application.
    
    Features:
        - Automatically converts naive datetimes to UTC-aware during model_validate
        - Enforces UTC timezone for all datetime fields through validation
        - Provides consistent datetime serialization to ISO format with Z suffix
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            # Ensure datetimes are serialized to ISO format with Z suffix
            datetime: lambda dt: dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        }
    )
    
    @classmethod
    def model_validate(cls, obj, *, strict=False, from_attributes=True, context=None):
        """Override model_validate to add timezone info to naive datetimes.
        
        This method intercepts the validation process to convert any naive datetime
        objects to UTC-aware datetimes before field validation occurs. This is
        especially useful when converting SQLAlchemy models (which use naive
        datetimes) to Pydantic models.
        """
        if from_attributes and hasattr(obj, "__dict__"):
            # Create a copy of the object's dict to avoid modifying the original
            obj_dict = dict(obj.__dict__)
            
            # Add UTC timezone to datetime fields
            for field_name, field_value in obj_dict.items():
                if isinstance(field_value, datetime) and field_value.tzinfo is None:
                    obj_dict[field_name] = field_value.replace(tzinfo=timezone.utc)
                    
            # Use the modified dict for validation
            return super().model_validate(obj_dict, strict=strict, context=context)
        
        # Fall back to standard validation for non-object inputs
        return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)
```

## Implementation Plan

### Phase 1: Code Cleanup (ADR-011) - ✅ COMPLETED
1. Remove Unused Imports - ✅ COMPLETED
   - Removed ZoneInfo from accounts.py and cashflow.py
   - Removed validates decorator imports
   - Cleaned up other unused imports

2. Documentation Updates - ✅ COMPLETED
   - Updated all datetime-related documentation
   - Removed references to timezone-aware storage
   - Added clear comments about naive UTC approach
   - Standardized datetime field documentation

3. Import Pattern Standardization - ✅ COMPLETED
   - Used consistent import ordering
   - Preferred importing from base_model
   - Removed redundant imports

### Phase 2: Business Logic Migration (ADR-012) - ⏳ IN PROGRESS
1. Create/Update Service Methods - ⏳ IN PROGRESS
   - ✅ RecurringBillService.create_liability_from_recurring()
   - ✅ CashflowService calculation methods
   - ✅ AccountService.validate_credit_limit_history()
   - ✅ CategoryService.get_full_path() and is_ancestor_of()
   - ⏳ RecurringIncomeService.create_income_from_recurring()
   - ⏳ StatementService.calculate_due_date()

2. Remove Model Logic - ⏳ IN PROGRESS
   - ✅ Remove create_liability() from RecurringBill
   - ✅ Remove calculation methods from CashflowForecast
   - ✅ Remove event listeners from CreditLimitHistory
   - ✅ Remove is_ancestor_of() and full_path from Category
   - ⏳ Remove create_income_entry() from RecurringIncome
   - ⏳ Remove __init__ logic from StatementHistory

3. Update Tests - ⏳ IN PROGRESS
   - ✅ Moved business logic tests for RecurringBill to service layer
   - ✅ Moved validation tests for CreditLimitHistory to service layer
   - ✅ Updated model tests to focus on persistence
   - ✅ Added new service layer tests for RecurringBill
   - ✅ Updated integration tests for RecurringBill and CreditLimitHistory
   - ⏳ Update tests for remaining models

### Phase 3: Documentation
1. Model Documentation
   - Update all model docstrings
   - Document pure data persistence focus
   - Remove references to business logic
   - Add service layer responsibility notes

2. Service Documentation
   - Document new service methods
   - Add validation pattern examples
   - Document business rule implementations
   - Add migration notes

3. Testing Documentation
   - Update test documentation
   - Add service test examples
   - Document validation testing approach

## Impact Analysis

### Code Changes
1. Model Layer
   - Remove business logic from 6 models
   - Update datetime documentation
   - Clean up imports
   - Remove event listeners

2. Service Layer
   - Add 6 new service methods
   - Enhance existing services
   - Move validation logic
   - Add business rule implementations

3. Database Impact
   - No schema changes required
   - No data migration needed
   - All changes are code-level only

### Testing Impact
1. Model Tests
   - Update 6 model test files
   - Remove business logic tests
   - Focus on persistence testing
   - Add relationship tests

2. Service Tests
   - Add new service test files
   - Move business logic tests
   - Add validation tests
   - Enhance coverage

3. Integration Tests
   - Update service integration tests
   - Add new test scenarios
   - Verify business rule enforcement
   - Test validation flows

### API Impact
1. Direct Changes
   - No endpoint changes needed
   - No schema changes required
   - No breaking changes

2. Implementation Changes
   - Update service calls
   - Move validation handling
   - Enhance error responses
   - Improve validation messages

## Recommendations

1. **High Priority**
   - Move create_liability() to service layer
   - Remove unused imports
   - Update incorrect documentation

2. **Medium Priority**
   - Standardize import patterns
   - Enhance validation documentation
   - Add more examples in docstrings

3. **Low Priority**
   - Add more comprehensive examples
   - Consider adding validation pattern guide
   - Enhance developer documentation

## Success Criteria

- ✅ All DateTime columns use naive storage
- ✅ No timezone parameters in column definitions
- ✅ No validation decorators in models
- ✅ No business logic in models
- ✅ Clear documentation of UTC approach
- ✅ Proper separation of concerns

## Next Steps

1. Create tickets for each required change
2. Prioritize business logic migration
3. Schedule documentation updates
4. Plan testing strategy
5. Review changes with team

## References

- [ADR-011: Datetime Standardization](docs/adr/011-datetime-standardization.md)
- [ADR-012: Validation Layer Standardization](docs/adr/012-validation-layer-standardization.md)
- [System Patterns Documentation](docs/system_patterns.md)
