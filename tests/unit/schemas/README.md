# Unit Tests for Pydantic Schemas

This directory contains unit tests for Pydantic schemas used throughout the Debtonator application. These tests validate schema behavior, validation rules, and serialization/deserialization functionality.

## Focus Areas

Schema unit tests should focus on:

1. **Schema Validation**: Testing that invalid data is rejected
2. **Default Values**: Testing that default values are correctly applied
3. **Type Conversion**: Testing that fields are properly converted to the expected types
4. **Custom Validators**: Testing custom field and model validators
5. **Serialization**: Testing `model_dump()` and `model_dump_json()` functionality

## Example Test Case

```python
def test_account_schema_validation():
    """Test validation rules for account schemas."""
    # Test invalid name (too short)
    with pytest.raises(ValidationError) as excinfo:
        AccountCreate(
            name="A",  # Too short (minimum 3 characters)
            available_balance=Decimal("1000.00"),
            current_balance=Decimal("1000.00"),
            account_type="checking"
        )
    
    errors = excinfo.value.errors()
    assert any(
        error["type"] == "string_too_short" and
        error["loc"][0] == "name"
        for error in errors
    )
```

## Pydantic v2 Features

Debtonator uses Pydantic v2 with several advanced features that should be tested:

1. **Field Annotations**: Testing Annotated types with Field constraints
2. **Model Config**: Testing model_config options
3. **Model Validators**: Testing mode="after" validators
4. **Discriminated Unions**: Testing polymorphic schema behavior

```python
def test_discriminator_recognition():
    """Test discriminator field recognition in polymorphic schemas."""
    data = {
        "id": 1,
        "name": "Primary Checking",
        "account_type": "checking",  # Discriminator field
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "overdraft_limit": Decimal("200.00")
    }
    
    # Union should recognize this as a CheckingAccountResponse
    response = AccountResponse.model_validate(data)
    assert isinstance(response, CheckingAccountResponse)
    assert response.overdraft_limit == Decimal("200.00")
```

## Writing Schema Tests

1. **Focus on schema behavior**: Test validation, conversion, and serialization
2. **Don't test SQLAlchemy models**: Schema tests should focus only on Pydantic schemas
3. **Test error cases**: Verify validation errors are raised for invalid data
4. **Test complex validation**: Ensure cross-field validators work correctly
5. **Use descriptive test names**: Names should clearly indicate what's being tested

## Test Organization

Tests are organized to mirror the structure of the `src/schemas` directory:

```
schemas/
├── test_accounts.py
├── test_bills.py
└── account_types/
    └── banking/
        ├── test_checking.py
        ├── test_savings.py
        └── test_credit.py
```
