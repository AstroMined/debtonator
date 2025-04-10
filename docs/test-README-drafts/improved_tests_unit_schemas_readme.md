# Unit Tests for Pydantic Schemas

This directory contains unit tests for Pydantic schemas used throughout the Debtonator application. These tests validate schema behavior, validation rules, conversion logic, and serialization/deserialization functionality with particular focus on financial data validation.

## Directory Structure

The schema tests directory structure mirrors the structure of the `src/schemas` directory:

```
unit/schemas/
├── __init__.py
├── test_accounts.py
├── test_balance.py
├── test_bills.py
├── test_cashflow.py
├── test_income.py
├── test_payments.py
├── test_categories.py
├── ...
└── account_types/
    ├── __init__.py
    ├── banking/
    │   ├── __init__.py
    │   ├── test_checking.py
    │   ├── test_savings.py
    │   ├── test_credit.py
    │   ├── test_bnpl.py
    │   └── ...
    ├── bill/
    ├── investment/
    └── loan/
```

## Naming Convention

All test files follow a consistent naming convention:

- Files must start with the prefix `test_`
- The remainder should match the name of the file in `src/schemas` being tested
- Example: `src/schemas/accounts.py` → `test_accounts.py`

## Schema Testing Focus Areas

Debtonator schema unit tests should focus on:

### 1. Schema Instantiation

Test that schemas can be created with valid attributes:

```python
def test_checking_account_schema_creation():
    """Test that a checking account schema can be created with valid attributes."""
    data = {
        "name": "Primary Checking",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "overdraft_limit": Decimal("200.00"),
        "account_type": "checking"
    }
    schema = CheckingAccountCreate(**data)
    
    assert schema.name == "Primary Checking"
    assert schema.available_balance == Decimal("1000.00")
    assert schema.current_balance == Decimal("1000.00")
    assert schema.overdraft_limit == Decimal("200.00")
    assert schema.account_type == "checking"
```

### 2. Decimal Precision for Financial Fields

Test that monetary values have the correct precision:

```python
def test_monetary_decimal_precision():
    """Test that monetary values have correct decimal precision."""
    data = {
        "name": "Precision Test",
        "available_balance": Decimal("1000.1234"),  # 4 decimal places
        "current_balance": Decimal("1000.1234"),    # 4 decimal places
        "account_type": "checking"
    }
    
    schema = AccountCreate(**data)
    
    # Financial calculations should maintain 4 decimal places
    assert schema.available_balance == Decimal("1000.1234")
    
    # Test dumping to dict
    data_dict = schema.model_dump()
    assert data_dict["available_balance"] == Decimal("1000.1234")
    
    # Test JSON serialization (should convert to string with 2 decimal places)
    json_data = schema.model_dump_json()
    parsed = json.loads(json_data)
    assert parsed["available_balance"] == "1000.1234"
```

### 3. Schema Validation

Test that schemas properly validate incoming data:

```python
def test_account_schema_validation():
    """Test validation rules for account schemas."""
    # Test name length validation
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
    
    # Test negative balance validation
    with pytest.raises(ValidationError) as excinfo:
        AccountCreate(
            name="Test Account",
            available_balance=Decimal("-1000.00"),  # Negative balance
            current_balance=Decimal("1000.00"),
            account_type="checking"
        )
    
    errors = excinfo.value.errors()
    assert any(
        "cannot be negative" in error["msg"].lower()
        for error in errors
    )
```

### 4. Bill Split Schema Validation

Test the core bill splitting validation rules:

```python
def test_bill_split_schema_validation():
    """Test validation of bill split schemas."""
    # Create a bill schema
    bill_data = {
        "name": "Rent",
        "amount": Decimal("1500.00"),
        "due_day": 1,
        "primary_account_id": 1,
        "splits": [
            {"account_id": 2, "amount": Decimal("500.00")},
            {"account_id": 3, "amount": Decimal("300.00")}
        ]
    }
    
    # Primary account split should be calculated automatically
    bill_schema = BillCreate(**bill_data)
    assert len(bill_schema.splits) == 3  # 2 explicit + 1 automatic
    
    # Find primary account split
    primary_split = next(
        (split for split in bill_schema.splits if split.account_id == 1),
        None
    )
    assert primary_split is not None
    assert primary_split.amount == Decimal("700.00")  # 1500 - 500 - 300
    
    # Test total split validation - splits exceed bill amount
    invalid_data = {
        "name": "Rent",
        "amount": Decimal("1500.00"),
        "due_day": 1,
        "primary_account_id": 1,
        "splits": [
            {"account_id": 2, "amount": Decimal("1000.00")},
            {"account_id": 3, "amount": Decimal("700.00")}
        ]
    }
    
    with pytest.raises(ValidationError) as excinfo:
        BillCreate(**invalid_data)
    
    errors = excinfo.value.errors()
    assert any(
        "exceed bill amount" in error["msg"].lower()
        for error in errors
    )
```

### 5. Field Type Conversion

Test that schemas properly convert field types:

```python
def test_account_schema_decimal_conversion():
    """Test conversion of string amounts to Decimal."""
    data = {
        "name": "Test Account",
        "available_balance": "1000.00",  # String, not Decimal
        "current_balance": "1000.00",    # String, not Decimal
        "account_type": "checking"
    }
    
    schema = AccountCreate(**data)
    
    assert isinstance(schema.available_balance, Decimal)
    assert isinstance(schema.current_balance, Decimal)
    assert schema.available_balance == Decimal("1000.00")
    assert schema.current_balance == Decimal("1000.00")
```

### 6. Default Values

Test that default values are properly set:

```python
def test_account_schema_default_values():
    """Test that default values are set correctly."""
    data = {
        "name": "Minimal Test Account",
        "account_type": "checking"
        # available_balance and current_balance not provided
    }
    
    schema = AccountCreate(**data)
    
    assert schema.available_balance == Decimal("0.00")
    assert schema.current_balance == Decimal("0.00")
    assert schema.status == "ACTIVE"  # Default status
```

### 7. Custom Validators

Test custom validator functions for fields:

```python
def test_credit_account_schema_validators():
    """Test custom validators for credit accounts."""
    # Credit limit less than current balance
    data = {
        "name": "Credit Card",
        "account_type": "credit",
        "credit_limit": Decimal("1000.00"),
        "current_balance": Decimal("1500.00")  # Exceeds credit limit
    }
    
    with pytest.raises(ValidationError) as excinfo:
        CreditAccountCreate(**data)
    
    errors = excinfo.value.errors()
    assert any(
        "current balance cannot exceed credit limit" in error["msg"].lower()
        for error in errors
    )
    
    # Test BNPL payment schedule validator
    data = {
        "name": "BNPL Account",
        "account_type": "bnpl",
        "credit_limit": Decimal("1000.00"),
        "current_balance": Decimal("500.00"),
        "payment_schedule": "INVALID_SCHEDULE"  # Invalid value
    }
    
    with pytest.raises(ValidationError) as excinfo:
        BNPLAccountCreate(**data)
    
    errors = excinfo.value.errors()
    assert any(
        "payment schedule" in error["msg"].lower()
        for error in errors
    )
```

### 8. Model Methods

Test schema methods that transform or validate data:

```python
def test_account_schema_methods():
    """Test methods on account schemas."""
    data = {
        "name": "Test Account",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "account_type": "checking"
    }
    
    schema = AccountCreate(**data)
    
    # Test to_dict method
    result = schema.model_dump()
    assert result["name"] == "Test Account"
    assert result["available_balance"] == Decimal("1000.00")
    assert result["current_balance"] == Decimal("1000.00")
    assert result["account_type"] == "checking"
    
    # Test JSON serialization
    json_str = schema.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["name"] == "Test Account"
    assert parsed["available_balance"] == "1000.00"  # Should be string in JSON
```

### 9. Nested Schemas

Test schemas with nested objects, common in bill splits:

```python
def test_nested_bill_schema_validation():
    """Test validation of nested bill schemas with splits."""
    data = {
        "name": "Rent and Utilities",
        "amount": Decimal("1200.00"),
        "due_day": 1,
        "primary_account_id": 1,
        "category": {
            "name": "Housing",
            "category_type": "EXPENSE"
        },
        "splits": [
            {
                "account_id": 2,
                "amount": Decimal("400.00"),
                "description": "Your portion"
            },
            {
                "account_id": 3,
                "amount": Decimal("300.00"),
                "description": "Roommate portion"
            }
        ]
    }
    
    schema = BillCreateWithCategory(**data)
    
    # Verify nested category
    assert schema.category.name == "Housing"
    assert schema.category.category_type == "EXPENSE"
    
    # Verify nested splits
    assert len(schema.splits) == 3  # 2 explicit + 1 calculated for primary
    
    # Find primary account split (should be calculated)
    primary_split = next(
        (split for split in schema.splits if split.account_id == 1),
        None
    )
    assert primary_split is not None
    assert primary_split.amount == Decimal("500.00")  # 1200 - 400 - 300
    
    # Verify other splits
    other_splits = [split for split in schema.splits if split.account_id != 1]
    assert len(other_splits) == 2
    assert other_splits[0].amount == Decimal("400.00")
    assert other_splits[0].description == "Your portion"
    assert other_splits[1].amount == Decimal("300.00")
    assert other_splits[1].description == "Roommate portion"
```

### 10. Schema Inheritance

Test schema inheritance and polymorphic behavior:

```python
def test_account_schema_inheritance():
    """Test schema inheritance for account types."""
    # Test base account schema
    base_data = {
        "name": "Base Account",
        "account_type": "base",  # Generic type
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
    }
    
    base_schema = AccountCreate(**base_data)
    assert base_schema.name == "Base Account"
    assert base_schema.account_type == "base"
    
    # Test checking account schema (inherits from AccountCreate)
    checking_data = {
        "name": "Checking Account",
        "account_type": "checking",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "overdraft_limit": Decimal("100.00")  # Checking-specific field
    }
    
    checking_schema = CheckingAccountCreate(**checking_data)
    assert checking_schema.name == "Checking Account"
    assert checking_schema.account_type == "checking"
    assert checking_schema.overdraft_limit == Decimal("100.00")
    
    # Test credit account schema (inherits from AccountCreate)
    credit_data = {
        "name": "Credit Card",
        "account_type": "credit",
        "current_balance": Decimal("500.00"),
        "credit_limit": Decimal("2000.00")  # Credit-specific field
    }
    
    credit_schema = CreditAccountCreate(**credit_data)
    assert credit_schema.name == "Credit Card"
    assert credit_schema.account_type == "credit"
    assert credit_schema.credit_limit == Decimal("2000.00")
    assert credit_schema.available_credit == Decimal("1500.00")  # Calculated field
```

### 11. Discriminated Union Pattern

Test schemas using Pydantic's discriminated union pattern, which is crucial for Debtonator's polymorphic account types:

```python
def test_account_response_discriminated_union():
    """Test discriminated union pattern for account responses."""
    # Create a checking account response
    checking_data = {
        "id": 1,
        "name": "Primary Checking",
        "account_type": "checking",  # Discriminator field
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "overdraft_limit": Decimal("200.00")  # Type-specific field
    }
    
    # This should be recognized as a CheckingAccountResponse
    response = AccountResponse.model_validate(checking_data)
    
    assert isinstance(response, CheckingAccountResponse)
    assert response.account_type == "checking"
    assert response.overdraft_limit == Decimal("200.00")
    
    # Create a credit account response
    credit_data = {
        "id": 2,
        "name": "Rewards Credit Card",
        "account_type": "credit",  # Different discriminator value
        "current_balance": Decimal("500.00"),
        "credit_limit": Decimal("2000.00"),  # Type-specific field
        "available_credit": Decimal("1500.00")  # Type-specific field
    }
    
    # This should be recognized as a CreditAccountResponse
    response = AccountResponse.model_validate(credit_data)
    
    assert isinstance(response, CreditAccountResponse)
    assert response.account_type == "credit"
    assert response.credit_limit == Decimal("2000.00")
    assert response.available_credit == Decimal("1500.00")
    
    # Test invalid discriminator
    invalid_data = {
        "id": 3,
        "name": "Invalid Account",
        "account_type": "invalid_type",  # Invalid discriminator
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00")
    }
    
    with pytest.raises(ValidationError) as excinfo:
        AccountResponse.model_validate(invalid_data)
    
    errors = excinfo.value.errors()
    assert any(
        "account_type" in str(error["loc"]) and
        "invalid enumeration member" in error["msg"].lower()
        for error in errors
    )
```

### 12. UTC Datetime Validation

Test schemas with datetime fields (per ADR-011):

```python
def test_schema_datetime_validation():
    """Test validation of UTC datetime fields."""
    from src.utils.datetime_utils import utc_now, days_ago
    
    # Valid UTC datetime
    valid_date = utc_now()
    data = {
        "name": "Test Transaction",
        "amount": Decimal("100.00"),
        "transaction_date": valid_date
    }
    
    schema = TransactionCreate(**data)
    assert schema.transaction_date == valid_date
    
    # Invalid: Naive datetime (no timezone)
    import datetime
    naive_date = datetime.datetime.now()  # No timezone
    invalid_data = {
        "name": "Test Transaction",
        "amount": Decimal("100.00"),
        "transaction_date": naive_date
    }
    
    with pytest.raises(ValidationError) as excinfo:
        TransactionCreate(**invalid_data)
    
    errors = excinfo.value.errors()
    assert any(
        "timezone" in error["msg"].lower()
        for error in errors
    )
    
    # Invalid: Non-UTC timezone
    non_utc_date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))
    invalid_data = {
        "name": "Test Transaction",
        "amount": Decimal("100.00"),
        "transaction_date": non_utc_date
    }
    
    with pytest.raises(ValidationError) as excinfo:
        TransactionCreate(**invalid_data)
    
    errors = excinfo.value.errors()
    assert any(
        "utc" in error["msg"].lower()
        for error in errors
    )
```

### 13. Cashflow Analysis Schemas

Test complex schemas for cashflow analysis features:

```python
def test_cashflow_forecast_schema():
    """Test cashflow forecast schema with complex structure."""
    # Create forecast data with daily cash positions
    data = {
        "account_id": 1,
        "starting_balance": Decimal("1000.00"),
        "ending_balance": Decimal("1500.00"),
        "total_income": Decimal("2000.00"),
        "total_expenses": Decimal("1500.00"),
        "lowest_balance": Decimal("800.00"),
        "lowest_balance_date": date(2023, 5, 15),
        "daily_positions": {
            "2023-05-01": Decimal("1000.00"),
            "2023-05-02": Decimal("950.00"),
            "2023-05-03": Decimal("900.00"),
            "2023-05-04": Decimal("850.00"),
            "2023-05-05": Decimal("800.00"),  # Lowest point
            "2023-05-15": Decimal("2000.00"),  # After income received
            "2023-05-30": Decimal("1500.00"),  # End of forecast
        },
        "upcoming_bills": [
            {
                "id": 1,
                "name": "Rent",
                "amount": Decimal("1000.00"),
                "due_day": 5
            },
            {
                "id": 2,
                "name": "Utilities",
                "amount": Decimal("200.00"),
                "due_day": 10
            }
        ],
        "upcoming_income": [
            {
                "id": 1,
                "name": "Salary",
                "amount": Decimal("2000.00"),
                "deposit_date": date(2023, 5, 15)
            }
        ]
    }
    
    schema = CashflowForecastResponse(**data)
    
    # Verify complex structure
    assert schema.account_id == 1
    assert schema.starting_balance == Decimal("1000.00")
    assert schema.ending_balance == Decimal("1500.00")
    assert schema.lowest_balance == Decimal("800.00")
    assert schema.lowest_balance_date == date(2023, 5, 15)
    
    # Verify daily positions dictionary
    assert len(schema.daily_positions) == 7
    assert schema.daily_positions["2023-05-01"] == Decimal("1000.00")
    assert schema.daily_positions["2023-05-05"] == Decimal("800.00")
    assert schema.daily_positions["2023-05-30"] == Decimal("1500.00")
    
    # Verify nested objects
    assert len(schema.upcoming_bills) == 2
    assert schema.upcoming_bills[0].name == "Rent"
    assert schema.upcoming_bills[0].amount == Decimal("1000.00")
    
    assert len(schema.upcoming_income) == 1
    assert schema.upcoming_income[0].name == "Salary"
    assert schema.upcoming_income[0].amount == Decimal("2000.00")
```

## Testing Pydantic v2 Features

Debtonator uses Pydantic v2 with several advanced features that need testing:

### Field Annotations

Test schemas with field annotations:

```python
def test_schema_field_annotations():
    """Test validation with field annotations."""
    from pydantic import Field
    from typing_extensions import Annotated
    
    # In Pydantic v2, we use Annotated types with Field
    class AccountSchema(BaseModel):
        name: Annotated[str, Field(min_length=3, max_length=50)]
        balance: Annotated[Decimal, Field(ge=0)]
    
    # Valid data
    valid_data = {
        "name": "Test Account",
        "balance": Decimal("100.00")
    }
    schema = AccountSchema(**valid_data)
    assert schema.name == "Test Account"
    assert schema.balance == Decimal("100.00")
    
    # Invalid name (too short)
    with pytest.raises(ValidationError):
        AccountSchema(name="Te", balance=Decimal("100.00"))
    
    # Invalid balance (negative)
    with pytest.raises(ValidationError):
        AccountSchema(name="Test Account", balance=Decimal("-50.00"))
```

### Model Config

Test schema configuration options:

```python
def test_schema_model_config():
    """Test model_config options."""
    # In Pydantic v2, we use model_config dict
    class AccountWithConfig(BaseModel):
        name: str
        balance: Decimal
        created_at: datetime
        
        model_config = {
            "json_encoders": {
                Decimal: lambda v: str(v),
                datetime: lambda v: v.isoformat()
            },
            "str_strip_whitespace": True
        }
    
    # Test whitespace stripping
    schema = AccountWithConfig(
        name="  Test Account  ",  # Extra whitespace
        balance=Decimal("100.00"),
        created_at=utc_now()
    )
    assert schema.name == "Test Account"  # Whitespace stripped
    
    # Test json encoding
    json_data = schema.model_dump_json()
    parsed = json.loads(json_data)
    assert isinstance(parsed["balance"], str)  # Decimal converted to string
    assert parsed["created_at"].endswith("Z")  # ISO format with Z for UTC
```

### Model Validators

Test model-level validators:

```python
def test_model_validators():
    """Test model validators in Pydantic v2."""
    # In Pydantic v2, we use @field_validator and @model_validator
    class PaymentWithValidator(BaseModel):
        bill_amount: Decimal
        payment_amount: Decimal
        
        @field_validator("payment_amount")
        def validate_payment_amount(cls, v, info):
            if v <= 0:
                raise ValueError("Payment amount must be positive")
            return v
        
        @model_validator(mode="after")
        def validate_payment_covers_bill(self):
            if self.payment_amount < self.bill_amount:
                raise ValueError("Payment amount must cover bill amount")
            return self
    
    # Valid data
    valid_data = {
        "bill_amount": Decimal("100.00"),
        "payment_amount": Decimal("100.00")
    }
    schema = PaymentWithValidator(**valid_data)
    
    # Invalid: payment_amount less than bill_amount
    with pytest.raises(ValidationError) as excinfo:
        PaymentWithValidator(
            bill_amount=Decimal("100.00"),
            payment_amount=Decimal("50.00")
        )
    
    errors = excinfo.value.errors()
    assert "Payment amount must cover bill amount" in str(errors)
```

## Working with Discriminated Unions in Pydantic v2

Pydantic v2 provides a discriminated union pattern essential for Debtonator's polymorphic account types:

### Common Issues to Test:

1. **Discriminator Field Recognition**:

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

2. **Literal Type with Validator Conflicts**:

```python
def test_literal_with_validators():
    """Test literal type fields with validators in discriminated unions."""
    # This test verifies that validators don't conflict with discriminator fields
    
    # A common issue in Pydantic v2 is validators affecting discriminator fields
    # The test attempts to validate a model with a discriminator field that has validators
    
    data = {
        "id": 1,
        "name": "Checking Account",
        "account_type": "checking",  # Discriminator field with validator
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00")
    }
    
    # Should validate without error
    response = AccountResponse.model_validate(data)
    assert response.account_type == "checking"
    
    # In the model definition, we should avoid validators on discriminator fields:
    # 
    # class AccountBase(BaseModel):
    #     account_type: str
    #     
    #     @field_validator("account_type")
    #     def validate_account_type(cls, v):
    #         # This would cause issues with discriminated unions
    #         return v
    # 
    # class CheckingAccount(AccountBase):
    #     account_type: Literal["checking"] = "checking"  # Discriminator field
```

3. **Inheritance Order Testing**:

```python
def test_discriminator_inheritance_order():
    """Test inheritance order effect on discriminator fields."""
    # The order of inheritance is crucial for discriminated unions
    # Derived class must come first for Literal to take precedence
    
    data = {
        "id": 1,
        "name": "Credit Card",
        "account_type": "credit",
        "current_balance": Decimal("500.00"),
        "credit_limit": Decimal("2000.00"),
        "available_credit": Decimal("1500.00")
    }
    
    # This should be recognized as a CreditAccountResponse
    response = AccountResponse.model_validate(data)
    assert isinstance(response, CreditAccountResponse)
    
    # The class definition should follow this pattern:
    # 
    # class CreditAccountResponse(CreditAccountBase, AccountResponse):
    #     account_type: Literal["credit"] = "credit"
    # 
    # NOT this:
    # 
    # class CreditAccountResponse(AccountResponse, CreditAccountBase):
    #     account_type: Literal["credit"] = "credit"
```

4. **Type-Specific Field Validation**:

```python
def test_discriminated_type_specific_validation():
    """Test type-specific field validation in discriminated unions."""
    # Missing required field for specific type
    data = {
        "id": 1,
        "name": "BNPL Account",
        "account_type": "bnpl",  # Type requires payment_schedule
        "current_balance": Decimal("500.00"),
        "credit_limit": Decimal("1000.00")
        # Missing payment_schedule field
    }
    
    with pytest.raises(ValidationError) as excinfo:
        AccountResponse.model_validate(data)
    
    errors = excinfo.value.errors()
    assert any(
        "payment_schedule" in str(error["loc"])
        for error in errors
    )
```

## Complex Validation Scenarios

Debtonator has complex validation needs for financial functionality:

### Nested Bill Split Validation

```python
def test_complex_bill_split_validation():
    """Test complex bill split validation with multiple accounts."""
    # Create a complex bill with multiple splits
    data = {
        "name": "Shared Expenses",
        "amount": Decimal("1000.00"),
        "due_day": 1,
        "primary_account_id": 1,
        "splits": [
            {"account_id": 2, "amount": Decimal("250.00")},
            {"account_id": 3, "amount": Decimal("250.00")},
            {"account_id": 4, "amount": Decimal("250.00")}
        ]
    }
    
    bill = BillCreate(**data)
    
    # Verify primary account split is created with correct amount
    primary_split = next(
        (split for split in bill.splits if split.account_id == 1),
        None
    )
    assert primary_split is not None
    assert primary_split.amount == Decimal("250.00")  # 1000 - 3*250
    
    # Test validation of split uniqueness (no duplicate account_id allowed)
    invalid_data = {
        "name": "Shared Expenses",
        "amount": Decimal("1000.00"),
        "due_day": 1,
        "primary_account_id": 1,
        "splits": [
            {"account_id": 2, "amount": Decimal("250.00")},
            {"account_id": 2, "amount": Decimal("250.00")}  # Duplicate account_id
        ]
    }
    
    with pytest.raises(ValidationError) as excinfo:
        BillCreate(**invalid_data)
    
    errors = excinfo.value.errors()
    assert any(
        "duplicate" in error["msg"].lower()
        for error in errors
    )
```

### Income Trends Analysis Schema

```python
def test_income_trends_schema():
    """Test complex income trends analysis schema."""
    data = {
        "account_id": 1,
        "total_income": Decimal("12000.00"),
        "average_monthly": Decimal("1000.00"),
        "trend_percentage": Decimal("0.05"),  # 5% growth
        "monthly_breakdown": {
            "2023-01": Decimal("950.00"),
            "2023-02": Decimal("960.00"),
            "2023-03": Decimal("970.00"),
            "2023-04": Decimal("980.00"),
            "2023-05": Decimal("990.00"),
            "2023-06": Decimal("1000.00"),
            "2023-07": Decimal("1010.00"),
            "2023-08": Decimal("1020.00"),
            "2023-09": Decimal("1030.00"),
            "2023-10": Decimal("1040.00"),
            "2023-11": Decimal("1050.00"),
            "2023-12": Decimal("1060.00")
        },
        "seasonality": {
            "day_of_month": {
                "1": Decimal("0.3"),
                "15": Decimal("0.7")
            },
            "month_of_year": {
                "1": Decimal("0.07"),  # January
                "2": Decimal("0.07"),  # February
                "3": Decimal("0.08"),  # March
                "4": Decimal("0.08"),  # April
                "5": Decimal("0.08"),  # May
                "6": Decimal("0.08"),  # June
                "7": Decimal("0.09"),  # July
                "8": Decimal("0.09"),  # August
                "9": Decimal("0.09"),  # September
                "10": Decimal("0.09"), # October
                "11": Decimal("0.09"), # November
                "12": Decimal("0.09")  # December
            }
        }
    }
    
    schema = IncomeTrendsResponse(**data)
    
    # Verify complex nested structure
    assert schema.account_id == 1
    assert schema.total_income == Decimal("12000.00")
    assert schema.average_monthly == Decimal("1000.00")
    
    # Verify monthly breakdown dictionary
    assert len(schema.monthly_breakdown) == 12
    assert schema.monthly_breakdown["2023-01"] == Decimal("950.00")
    assert schema.monthly_breakdown["2023-12"] == Decimal("1060.00")
    
    # Verify nested dictionaries in seasonality
    assert len(schema.seasonality.day_of_month) == 2
    assert schema.seasonality.day_of_month["1"] == Decimal("0.3")
    assert schema.seasonality.day_of_month["15"] == Decimal("0.7")
    
    assert len(schema.seasonality.month_of_year) == 12
    assert schema.seasonality.month_of_year["1"] == Decimal("0.07")
    assert schema.seasonality.month_of_year["12"] == Decimal("0.09")
    
    # Test validation: probability distribution should sum to approximately 1.0
    day_sum = sum(schema.seasonality.day_of_month.values())
    month_sum = sum(schema.seasonality.month_of_year.values())
    
    assert Decimal("0.99") <= day_sum <= Decimal("1.01")
    assert Decimal("0.99") <= month_sum <= Decimal("1.01")
```

## Best Practices

1. **Test all validation rules**: Test both successful validation and error cases
2. **Test type conversion**: Verify that fields are properly converted to the expected types
3. **Test custom validators**: Verify that custom field and model validators work correctly
4. **Test default values**: Ensure default values are correctly applied
5. **Test complex validation logic**: Test validators that involve multiple fields
6. **Test inheritance**: Verify that schema inheritance works correctly
7. **Test serialization/deserialization**: Verify model_dump() and model_dump_json() behavior
8. **Test Pydantic v2 features**: Test new features introduced in Pydantic v2
9. **Test edge cases**: Verify behavior with boundary values and edge cases
10. **Test UTC datetime validation**: Ensure compliance with ADR-011
11. **Test financial precision**: Verify decimal precision for monetary fields
12. **Test discriminated unions**: Verify proper handling of polymorphic account types
13. **Test schema factory integration**: Verify schema factories produce valid schemas

## Common Anti-Patterns to Avoid

1. **Testing SQLAlchemy models**: Schema tests should focus on Pydantic schemas, not SQLAlchemy models
2. **Using mocks**: Don't use unittest.mock or similar mocking libraries (per ADR-014)
3. **Testing implementation details**: Test schema behavior, not implementation details
4. **Overcomplicated fixtures**: Keep test fixtures simple and focused
5. **Hardcoded validation messages**: Use message snippets for validation to allow for message changes
6. **Missing error cases**: Test both successful validation and validation failures
7. **Using naive datetimes**: Always use timezone-aware UTC datetimes (per ADR-011)
8. **Circular imports**: Avoid circular imports in test modules
9. **Validator conflicts with discriminator fields**: Avoid validators on discriminator fields
10. **Too much business logic in schemas**: Verify complex validation is in service layer, not schemas

## Decimal Precision in Tests

When testing financial calculations, follow Debtonator's precision rules:

1. **Storage Precision**: 4 decimal places for database (Numeric(12, 4))
2. **Display Precision**: 2 decimal places for UI/API boundaries
3. **Use MoneyDecimal type**: For monetary values (custom decimal handling)
4. **Use PercentageDecimal type**: For percentage values (custom decimal handling)

Example:

```python
def test_decimal_precision_rules():
    """Test decimal precision handling for financial schemas."""
    # Create schema with precise values
    data = {
        "principal": Decimal("1000.5678"),  # 4 decimal places (storage)
        "interest_rate": Decimal("0.0525"),  # 4 decimal places (percentage)
        "payment": Decimal("150.57")         # 2 decimal places (money)
    }
    
    schema = LoanCalculationRequest(**data)
    
    # Test internal precision
    assert schema.principal == Decimal("1000.5678")
    assert schema.interest_rate == Decimal("0.0525")
    
    # Test calculation with proper precision
    monthly_interest = schema.principal * (schema.interest_rate / Decimal("12"))
    
    # Should maintain 4 decimal places for internal calculation
    assert monthly_interest == Decimal("4.3774")  # 1000.5678 * (0.0525 / 12)
    
    # Test serialization (should follow display rules)
    data_dict = schema.model_dump()
    assert data_dict["principal"] == Decimal("1000.5678")
    
    # Test JSON serialization (converts to string with appropriate precision)
    json_str = schema.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["principal"] == "1000.5678"
    assert parsed["interest_rate"] == "0.0525"
    assert parsed["payment"] == "150.57"
```

## Example Test File Structure

```python
import pytest
from decimal import Decimal
import json
from datetime import datetime, date, timezone
from pydantic import ValidationError, Field
from typing_extensions import Annotated

from src.schemas.accounts import AccountCreate, AccountResponse
from src.schemas.account_types.banking.checking import CheckingAccountCreate, CheckingAccountResponse
from src.schemas.account_types.banking.credit import CreditAccountCreate, CreditAccountResponse
from src.schemas.bills import BillCreate, BillSplitCreate
from src.utils.datetime_utils import utc_now, days_ago, days_from_now

# Schema creation tests
def test_account_create_schema():
    """Test creating account schema with valid data."""
    # Test implementation...

# Validation error tests
def test_account_create_validation_errors():
    """Test validation errors for account creation schema."""
    # Test implementation...

# Type conversion tests
def test_account_create_type_conversion():
    """Test type conversion in account creation schema."""
    # Test implementation...

# Default value tests
def test_account_create_default_values():
    """Test default values in account creation schema."""
    # Test implementation...

# Custom validator tests
def test_account_create_custom_validators():
    """Test custom validators in account creation schema."""
    # Test implementation...

# Nested schema tests
def test_account_nested_schemas():
    """Test nested schemas in account responses."""
    # Test implementation...

# Discriminated union tests
def test_account_response_discriminated_union():
    """Test discriminated union pattern in account responses."""
    # Test implementation...

# UTC datetime tests
def test_account_datetime_validation():
    """Test UTC datetime validation in account schemas."""
    # Test implementation...

# Bill split tests
def test_bill_split_validation():
    """Test bill split validation rules."""
    # Test implementation...

# Financial precision tests
def test_financial_precision():
    """Test decimal precision for financial fields."""
    # Test implementation...
```