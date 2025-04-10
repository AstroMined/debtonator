# Unit Tests for Schema Factories

This directory contains unit tests for the schema factory functions in `tests/helpers/schema_factories/`. These tests validate that the schema factories produce valid schema instances with correct default values and customization options while following Debtonator's test patterns and financial validation requirements.

## Purpose

Schema factory tests serve to:

1. **Verify Factory Behavior**: Ensure factories create valid schema instances with expected values
2. **Test Customization Options**: Verify that custom parameters override defaults correctly
3. **Document Factory Usage**: Demonstrate how to use schema factories effectively
4. **Test Edge Cases**: Verify behavior with boundary values and special cases
5. **Ensure Determinism**: Verify that factories produce consistent results when needed
6. **Support Testing Strategy**: Validate that factories properly implement the "Real Objects Testing Philosophy" from ADR-014

## Directory Structure

The schema factory tests directory structure mirrors the structure of the `tests/helpers/schema_factories` directory:

```
unit/helpers/schema_factories/
├── __init__.py
├── test_basic_test_schema_factories.py
├── test_account_schema_factories.py
├── test_bill_schema_factories.py
├── test_income_schema_factories.py
├── test_cashflow_schema_factories.py
└── test_complex_schema_factories.py
```

## Naming Convention

All test files follow a consistent naming convention:

- Files must start with the prefix `test_`
- The remainder should match the name of the file in `tests/helpers/schema_factories` being tested
- Example: `tests/helpers/schema_factories/basic_test_schema_factories.py` → `test_basic_test_schema_factories.py`

## Key Testing Principles

### 1. Test All Factory Functions

Every schema factory function should have corresponding tests covering both default and customized behavior:

```python
def test_create_checking_account_schema():
    """Test create_checking_account_schema factory function."""
    # Test default values
    schema = create_checking_account_schema()
    assert isinstance(schema, CheckingAccountCreate)
    assert schema.name is not None
    assert schema.account_type == "checking"
    assert schema.available_balance is not None
    assert schema.current_balance is not None
    assert schema.overdraft_limit is not None
    
    # Test customized values
    custom_schema = create_checking_account_schema(
        name="Custom Checking",
        available_balance=Decimal("5000.00"),
        current_balance=Decimal("4800.00"),
        overdraft_limit=Decimal("1000.00")
    )
    assert custom_schema.name == "Custom Checking"
    assert custom_schema.available_balance == Decimal("5000.00")
    assert custom_schema.current_balance == Decimal("4800.00")
    assert custom_schema.overdraft_limit == Decimal("1000.00")
```

### 2. Test Default Value Ranges

Test that default values are within appropriate ranges and follow business rules:

```python
def test_credit_account_schema_defaults():
    """Test default values in credit account schema factory."""
    schemas = [create_credit_account_schema() for _ in range(20)]
    
    # Credit limit should be reasonable
    for schema in schemas:
        assert schema.credit_limit >= Decimal("500.00")
        assert schema.credit_limit <= Decimal("10000.00")
    
    # Current balance should not exceed credit limit
    for schema in schemas:
        assert schema.current_balance <= schema.credit_limit
    
    # Available credit should be calculated correctly
    for schema in schemas:
        assert schema.available_credit == (schema.credit_limit - schema.current_balance)
        
    # Names should follow expected pattern
    for schema in schemas:
        assert schema.name.startswith("Credit Card") or schema.name.startswith("Rewards Card")
```

### 3. Test Parameter Customization

Test that all parameters can be individually customized:

```python
def test_bill_schema_factory_customization():
    """Test parameter customization in bill schema factory."""
    # Test each parameter individually
    name_schema = create_bill_schema(name="Custom Bill Name")
    assert name_schema.name == "Custom Bill Name"
    
    amount_schema = create_bill_schema(amount=Decimal("123.45"))
    assert amount_schema.amount == Decimal("123.45")
    
    due_day_schema = create_bill_schema(due_day=15)
    assert due_day_schema.due_day == 15
    
    category_schema = create_bill_schema(category_name="Custom Category")
    assert category_schema.category.name == "Custom Category"
    
    # Test multiple parameters together
    full_schema = create_bill_schema(
        name="Multiple Params",
        amount=Decimal("500.00"),
        due_day=20,
        category_name="Multiple Test"
    )
    assert full_schema.name == "Multiple Params"
    assert full_schema.amount == Decimal("500.00")
    assert full_schema.due_day == 20
    assert full_schema.category.name == "Multiple Test"
```

### 4. Test Integration with Debtonator's Financial Requirements

Test that schema factories create financial data that complies with Debtonator's money precision requirements:

```python
def test_decimal_precision_in_schema_factories():
    """Test decimal precision for monetary values in schema factories."""
    # Create account with precise decimal values
    account_schema = create_checking_account_schema(
        available_balance=Decimal("1000.1234"),  # 4 decimal places
        current_balance=Decimal("1000.1234")     # 4 decimal places
    )
    
    # Verify precision is maintained
    assert account_schema.available_balance == Decimal("1000.1234")
    assert account_schema.current_balance == Decimal("1000.1234")
    
    # Test bill with precise amount
    bill_schema = create_bill_schema(amount=Decimal("123.4567"))
    assert bill_schema.amount == Decimal("123.4567")
    
    # Test bill splits with precise amounts
    bill_with_splits = create_bill_with_splits_schema(
        amount=Decimal("100.0000"),
        split_amounts=[Decimal("33.3333"), Decimal("33.3333"), Decimal("33.3334")]
    )
    
    # Sum should equal total (with appropriate precision)
    split_sum = sum(split.amount for split in bill_with_splits.splits)
    assert split_sum == bill_with_splits.amount
```

### 5. Test Schema Factory Lists

Test factories that generate lists of schemas:

```python
def test_create_account_schema_list():
    """Test factory for creating lists of account schemas."""
    # Test with default params
    schemas = create_account_schema_list(count=5)
    
    assert len(schemas) == 5
    assert all(isinstance(schema, AccountCreate) for schema in schemas)
    
    # Verify account types are distributed
    account_types = [schema.account_type for schema in schemas]
    unique_types = set(account_types)
    assert len(unique_types) > 1  # Should have multiple account types
    
    # Test with specific account type
    checking_schemas = create_account_schema_list(
        count=3,
        account_type="checking"
    )
    
    assert len(checking_schemas) == 3
    assert all(schema.account_type == "checking" for schema in checking_schemas)
    assert all(isinstance(schema, CheckingAccountCreate) for schema in checking_schemas)
    
    # Test with naming pattern
    custom_schemas = create_account_schema_list(
        count=3,
        name_prefix="Test Account"
    )
    
    assert len(custom_schemas) == 3
    assert all(schema.name.startswith("Test Account") for schema in custom_schemas)
```

### 6. Test Nested Schema Factories

Test factories that generate nested schemas, which are common in Debtonator (e.g., bills with splits):

```python
def test_create_bill_with_splits_schema():
    """Test factory for bill with nested split schemas."""
    # Create bill with multiple splits
    schema = create_bill_with_splits_schema(
        name="Shared Rent",
        amount=Decimal("1500.00"),
        split_count=3  # Create 3 splits
    )
    
    assert schema.name == "Shared Rent"
    assert schema.amount == Decimal("1500.00")
    assert len(schema.splits) == 3
    
    # Verify splits have appropriate values
    split_amounts = [split.amount for split in schema.splits]
    assert sum(split_amounts) == schema.amount  # Splits should equal total
    
    # Test with explicit split amounts
    custom_schema = create_bill_with_splits_schema(
        name="Custom Splits",
        amount=Decimal("1000.00"),
        split_amounts=[Decimal("400.00"), Decimal("350.00"), Decimal("250.00")]
    )
    
    assert custom_schema.name == "Custom Splits"
    assert custom_schema.amount == Decimal("1000.00")
    assert len(custom_schema.splits) == 3
    
    # Verify custom split amounts
    amounts = [split.amount for split in custom_schema.splits]
    assert Decimal("400.00") in amounts
    assert Decimal("350.00") in amounts
    assert Decimal("250.00") in amounts
```

### 7. Test Complex Schema Structures

Test factories that create complex nested schema structures like cashflow forecasts:

```python
def test_create_cashflow_forecast_schema():
    """Test factory for complex cashflow forecast schema."""
    # Create forecast with default values
    schema = create_cashflow_forecast_schema()
    
    assert schema.account_id is not None
    assert schema.starting_balance is not None
    assert schema.ending_balance is not None
    assert schema.total_income is not None
    assert schema.total_expenses is not None
    
    # Verify nested structures exist
    assert schema.daily_positions is not None
    assert len(schema.daily_positions) > 0
    assert schema.upcoming_bills is not None
    assert schema.upcoming_income is not None
    
    # Test with custom values
    custom_schema = create_cashflow_forecast_schema(
        account_id=42,
        days=14,  # 14-day forecast
        starting_balance=Decimal("2000.00"),
        bill_count=3,
        income_count=1
    )
    
    assert custom_schema.account_id == 42
    assert custom_schema.starting_balance == Decimal("2000.00")
    assert len(custom_schema.daily_positions) == 14  # 14 days
    assert len(custom_schema.upcoming_bills) == 3
    assert len(custom_schema.upcoming_income) == 1
    
    # Verify forecast math is correct
    assert custom_schema.total_expenses == sum(
        bill.amount for bill in custom_schema.upcoming_bills
    )
    assert custom_schema.total_income == sum(
        income.amount for income in custom_schema.upcoming_income
    )
    assert custom_schema.ending_balance == (
        custom_schema.starting_balance +
        custom_schema.total_income -
        custom_schema.total_expenses
    )
```

### 8. Test Random vs. Deterministic Behavior

Test that factories are appropriately random or deterministic as needed:

```python
def test_income_trends_schema_factory_determinism():
    """Test deterministic vs. random income trends schema generation."""
    # With random=False, should get consistent results
    schema1 = create_income_trends_schema(random=False, seed=42)
    schema2 = create_income_trends_schema(random=False, seed=42)
    
    # Compare dictionaries for exact equality
    dict1 = schema1.model_dump()
    dict2 = schema2.model_dump()
    assert dict1 == dict2
    
    # With random=True or different seeds, should get different results
    schema3 = create_income_trends_schema(random=True)
    schema4 = create_income_trends_schema(random=True)
    
    # Compare dictionaries - should be different
    dict3 = schema3.model_dump()
    dict4 = schema4.model_dump()
    assert dict3 != dict4
    
    # Specific test for seasonality - a common source of non-determinism
    schema5 = create_income_trends_schema(
        include_seasonality=True,  # Ensure seasonality is included
        random=False,  # Deterministic generation
        seed=123  # Fixed seed
    )
    schema6 = create_income_trends_schema(
        include_seasonality=True,
        random=False,
        seed=123
    )
    
    # Seasonality dictionaries should match exactly
    assert (
        schema5.seasonality.day_of_month == 
        schema6.seasonality.day_of_month
    )
    assert (
        schema5.seasonality.month_of_year == 
        schema6.seasonality.month_of_year
    )
```

### 9. Test Schema Factory Validation

Test that schema factories produce schemas that comply with validation rules:

```python
def test_schema_factory_validation():
    """Test that schema factories create valid schemas."""
    # Generate multiple schemas to ensure all pass validation
    for _ in range(10):
        # Account schemas
        checking_schema = create_checking_account_schema()
        savings_schema = create_savings_account_schema()
        credit_schema = create_credit_account_schema()
        
        # Bill schemas
        bill_schema = create_bill_schema()
        bill_with_splits = create_bill_with_splits_schema()
        
        # Complex schemas
        cashflow_schema = create_cashflow_forecast_schema()
        income_trends = create_income_trends_schema()
        
        # All should validate without errors
        # (would raise ValidationError if invalid)
```

### 10. Test Integration with Models

Test that schemas produced by factories can be used with SQLAlchemy models:

```python
async def test_schema_factory_model_integration(db_session):
    """Test schemas from factories work with models."""
    # Create schema from factory
    schema = create_checking_account_schema(
        name="Integration Test",
        available_balance=Decimal("1500.00"),
        current_balance=Decimal("1500.00")
    )
    
    # Convert to dict for model creation
    data = schema.model_dump()
    
    # Create model instance
    from src.models.account_types.banking.checking import CheckingAccount
    
    account = CheckingAccount(**data)
    db_session.add(account)
    await db_session.flush()
    
    # Verify model was created correctly
    assert account.id is not None
    assert account.name == "Integration Test"
    assert account.available_balance == Decimal("1500.00")
    assert account.current_balance == Decimal("1500.00")
    assert account.account_type == "checking"
```

## Testing Schema Factory Edge Cases

### 1. Testing with Extreme Values

```python
def test_schema_factory_extreme_values():
    """Test schema factories with extreme values."""
    # Very large decimal
    large_schema = create_checking_account_schema(
        available_balance=Decimal("9999999.9999"),
        current_balance=Decimal("9999999.9999")
    )
    assert large_schema.available_balance == Decimal("9999999.9999")
    
    # Very small decimal
    small_schema = create_checking_account_schema(
        available_balance=Decimal("0.0001"),
        current_balance=Decimal("0.0001")
    )
    assert small_schema.available_balance == Decimal("0.0001")
    
    # Zero values
    zero_schema = create_checking_account_schema(
        available_balance=Decimal("0.0000"),
        current_balance=Decimal("0.0000")
    )
    assert zero_schema.available_balance == Decimal("0.0000")
    
    # Maximum length strings
    long_name_schema = create_checking_account_schema(
        name="A" * 50  # 50 character name (maximum allowed)
    )
    assert len(long_name_schema.name) == 50
    
    # Test with empty string (should use default or raise error)
    try:
        empty_name_schema = create_checking_account_schema(name="")
        # If it doesn't raise error, should use default
        assert empty_name_schema.name != ""
    except ValueError:
        # Or should raise ValueError
        pass
```

### 2. Testing Conditional Logic

```python
def test_schema_factory_conditional_logic():
    """Test conditional logic in schema factories."""
    # Test with include_details=True
    detailed_schema = create_test_schema_with_options(include_details=True)
    assert hasattr(detailed_schema, "details")
    assert detailed_schema.details is not None
    
    # Test with include_details=False
    simple_schema = create_test_schema_with_options(include_details=False)
    assert not hasattr(simple_schema, "details") or simple_schema.details is None
    
    # Test BNPL account with different statuses
    active_bnpl = create_bnpl_account_schema(status="ACTIVE")
    assert active_bnpl.status == "ACTIVE"
    assert active_bnpl.is_active is True
    
    paid_bnpl = create_bnpl_account_schema(status="PAID_OFF")
    assert paid_bnpl.status == "PAID_OFF"
    assert paid_bnpl.is_active is False
```

### 3. Testing with Missing Optional Values

```python
def test_schema_factory_missing_optionals():
    """Test schema factories with missing optional values."""
    # Create schema with only required fields
    schema = create_minimal_test_schema()
    
    # Required fields should be present
    assert schema.name is not None
    
    # Optional fields should use defaults
    assert hasattr(schema, "description")  # Should exist
    assert schema.created_at is not None  # Should have default value
    
    # Test explicit None for optional field
    none_schema = create_test_schema_with_options(description=None)
    assert none_schema.description is None
```

## Schema Factory Implementation Patterns

The following patterns should be tested to ensure they're implemented correctly:

### 1. Default Value Generation

```python
def test_default_value_patterns():
    """Test default value generation patterns in factories."""
    # Timestamp defaults
    schema = create_test_item_schema()
    assert schema.timestamp is not None
    
    # Sequential ID defaults
    schemas = [create_test_item_schema() for _ in range(5)]
    ids = [schema.id for schema in schemas if hasattr(schema, 'id')]
    assert len(set(ids)) == len(ids)  # All IDs should be unique
    
    # Random string defaults
    schemas = [create_test_item_schema() for _ in range(5)]
    names = [schema.name for schema in schemas]
    assert len(set(names)) > 1  # Should have some variation
```

### 2. Nested Object Creation

```python
def test_nested_object_creation_patterns():
    """Test nested object creation patterns in factories."""
    # Parent-child relationships
    schema = create_parent_with_children_schema(children_count=3)
    assert len(schema.children) == 3
    
    # Test parent reference in children
    for child in schema.children:
        assert child.parent_name == schema.name
        
    # Dictionary of nested objects
    schema = create_schema_with_dict()
    assert isinstance(schema.items, dict)
    assert len(schema.items) > 0
```

### 3. Related Factory Integration

```python
def test_related_factory_integration():
    """Test integration between related factories."""
    # Bill factory should use account factory internally
    bill_schema = create_bill_schema(with_account=True)
    assert hasattr(bill_schema, "account")
    assert bill_schema.account is not None
    assert bill_schema.account.id is not None
    
    # Income factory should use account factory
    income_schema = create_income_schema(with_account=True)
    assert hasattr(income_schema, "target_account")
    assert income_schema.target_account is not None
```

## Testing Financial Validation Rules

Test that schema factories create schemas that comply with Debtonator's financial validation rules:

```python
def test_financial_validation_rules():
    """Test financial validation rules in schema factories."""
    # 1. Credit account validation (available credit = credit limit - current balance)
    credit_schema = create_credit_account_schema(
        credit_limit=Decimal("2000.00"),
        current_balance=Decimal("500.00")
    )
    assert credit_schema.available_credit == Decimal("1500.00")
    
    # 2. Bill split validation (splits sum to bill amount)
    bill_schema = create_bill_with_splits_schema(
        amount=Decimal("1000.00"),
        split_count=4
    )
    split_total = sum(split.amount for split in bill_schema.splits)
    assert split_total == Decimal("1000.00")
    
    # 3. BNPL account validation (remaining payments * payment amount = current balance)
    bnpl_schema = create_bnpl_account_schema(
        current_balance=Decimal("1200.00"),
        payment_amount=Decimal("200.00"),
        payments_remaining=6
    )
    assert bnpl_schema.current_balance == (
        bnpl_schema.payment_amount * bnpl_schema.payments_remaining
    )
```

## Best Practices

1. **Test Every Factory Function**: Ensure all factory functions have dedicated tests
2. **Test All Parameters**: Verify that each parameter can be customized
3. **Test Default Values**: Ensure defaults are appropriate and follow business rules
4. **Test Randomization**: Verify random behavior when appropriate (e.g., ID generation)
5. **Test Deterministic Behavior**: Ensure consistent output with same inputs when needed
6. **Test Edge Cases**: Verify behavior with boundary values and special cases
7. **Test Model Integration**: Verify schemas work with corresponding models
8. **Test Validation Flow**: Ensure generated schemas pass validation
9. **Use Clear Assertions**: Make assertions that clearly identify what's being tested
10. **Document Factory Usage**: Use tests to document how factories should be used
11. **Test Financial Validation**: Verify compliance with Debtonator's financial rules
12. **Test Nested Objects**: Verify factories correctly handle nested schema structures
13. **Test Schema Lists**: Verify factories can create lists of related schemas
14. **Test DateTime Compliance**: Verify factories follow ADR-011 for datetime fields
15. **Test Realism**: Ensure financial test data is realistic and useful

## Common Anti-Patterns to Avoid

1. **Inconsistent Testing**: Don't test some factory functions but not others
2. **Missing Parameter Tests**: Don't forget to test customization of all parameters
3. **Weak Assertions**: Avoid assertions that don't verify specific behavior
4. **Testing Implementation Details**: Focus on behavior, not implementation
5. **Overcomplicated Setup**: Keep test setup as simple as possible
6. **Missing Edge Case Tests**: Don't forget to test boundary conditions
7. **Ignoring Factory Documentation**: Document factory behavior through tests
8. **Testing Factory Internals**: Test factory outputs, not internal details
9. **Unrealistic Financial Data**: Ensure monetary values are realistic
10. **Improper Decimal Handling**: Always use Decimal for financial values
11. **Timezone Violations**: Always follow ADR-011 for datetime handling
12. **Missing Validation Tests**: Ensure schemas pass validation
13. **Non-deterministic Tests**: Ensure tests are deterministic when needed
14. **Missing Integration Tests**: Test integration with models
15. **Isolated Factory Testing**: Test factories in relation to one another

## Example Test File Structure

```python
import pytest
from decimal import Decimal
import json
from typing import List, Dict, Optional
from pydantic import ValidationError

from tests.helpers.schemas.account_types.banking.checking import CheckingAccountCreate
from tests.helpers.schemas.account_types.banking.savings import SavingsAccountCreate
from tests.helpers.schemas.account_types.banking.credit import CreditAccountCreate
from tests.helpers.schema_factories.account_schema_factories import (
    create_checking_account_schema,
    create_savings_account_schema,
    create_credit_account_schema,
    create_account_schema_list,
)
from src.utils.datetime_utils import utc_now

# Basic creation tests
def test_create_checking_account_schema():
    """Test basic schema creation for checking accounts."""
    # Test implementation...

# Parameter customization tests
def test_checking_account_schema_customization():
    """Test parameter customization for checking accounts."""
    # Test implementation...

# Default value tests
def test_checking_account_schema_defaults():
    """Test default values for checking account schemas."""
    # Test implementation...

# Schema list tests
def test_create_account_schema_list():
    """Test creating lists of account schemas."""
    # Test implementation...

# Financial validation tests
def test_financial_validation_rules():
    """Test financial validation rules in account schemas."""
    # Test implementation...

# Edge case tests
def test_account_schema_edge_cases():
    """Test edge cases for account schemas."""
    # Test implementation...
```

## Schema Factory Function Template

When creating new schema factory functions, follow this template:

```python
def create_some_schema(
    # Required parameters first
    required_field: str,
    # Optional parameters next with defaults
    optional_field: Optional[str] = None,
    count: int = 1,
    include_details: bool = True,
    random: bool = True,
    seed: Optional[int] = None,
) -> SomeSchema:
    """Create a SomeSchema instance with customizable fields.
    
    Args:
        required_field: Description of required field
        optional_field: Description of optional field, defaults to None
        count: Number of child items to create, defaults to 1
        include_details: Whether to include detailed information, defaults to True
        random: Whether to use random values or deterministic ones, defaults to True
        seed: Random seed for deterministic generation, defaults to None
        
    Returns:
        SomeSchema: A fully populated schema instance
    """
    # Implementation
    # ...
```

## Integration with Model Tests

Schema factories can be used in model tests to simplify setup:

```python
async def test_model_with_factory(db_session):
    """Test model using schema factory to generate test data."""
    # Create schema using factory
    schema = create_checking_account_schema(
        name="Integration Test",
        available_balance=Decimal("1000.00")
    )
    
    # Convert to dict for model creation
    data = schema.model_dump()
    
    # Create model
    from src.models.account_types.banking.checking import CheckingAccount
    account = CheckingAccount(**data)
    db_session.add(account)
    await db_session.flush()
    
    # Test model behavior
    assert account.name == "Integration Test"
    assert account.available_balance == Decimal("1000.00")
```

## Special Considerations for Financial Data

When testing schema factories that create financial data, special care is needed:

```python
def test_financial_schema_factory_precision():
    """Test precision handling in financial schema factories."""
    # Create schema with precise decimal values
    schema = create_financial_schema(
        principal=Decimal("1000.1234"),
        interest_rate=Decimal("0.0525"),
        payment=Decimal("123.45")
    )
    
    # Verify precision maintained based on field type
    assert schema.principal == Decimal("1000.1234")  # 4 decimal places (storage)
    assert schema.interest_rate == Decimal("0.0525")  # 4 decimal places (percentage)
    assert schema.payment == Decimal("123.45")  # 2 decimal places (money)
    
    # Test calculation with precision rules
    monthly_interest = schema.calculate_monthly_interest()
    
    # Verify calculation follows precision rules
    # 1000.1234 * (0.0525 / 12) = 4.3774...
    assert monthly_interest == Decimal("4.38")  # Rounded to 2 decimal places for display
```
