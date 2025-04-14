# Account Type Error Tests

This directory contains tests for account type-specific error classes. These tests verify the specialized error handling for different account types.

## Structure

The test files follow the same structure as the source code:

```tree
tests/unit/errors/account_types/
├── __init__.py
├── test_account_types_init_errors.py  # Tests for base account type errors
└── banking/
    ├── test_banking_init_errors.py    # Tests for banking base errors
    ├── test_checking_errors.py
    ├── test_credit_errors.py
    ├── test_savings_errors.py
    ├── test_bnpl_errors.py
    ├── test_ewa_errors.py
    └── test_payment_app_errors.py
```

## Testing Approach

Tests in this directory focus on:

1. **Type-Specific Error Inheritance**: Verifying that account type errors properly inherit from base errors
2. **Type-Specific Error Construction**: Testing specialized constructor parameters
3. **Type-Specific Error Messages**: Ensuring error messages contain type-specific information
4. **Error Handler Integration**: Testing integration with error handlers where applicable

## Example Tests

### Error Hierarchy Testing

```python
def test_checking_error_hierarchy():
    """Test that CheckingAccountError inherits correctly."""
    # Inheritance chain:
    # CheckingAccountError -> BankingAccountError -> AccountTypeError -> AccountError -> DebtonatorError
    assert issubclass(CheckingAccountError, BankingAccountError)
    assert issubclass(BankingAccountError, AccountTypeError)
    assert issubclass(AccountTypeError, AccountError)
    assert issubclass(AccountError, DebtonatorError)
    
    # Test instance relationships
    error = CheckingOverdraftError(account_id=1, attempted_amount=Decimal("150.00"))
    assert isinstance(error, CheckingOverdraftError)
    assert isinstance(error, CheckingAccountError)
    assert isinstance(error, BankingAccountError)
    assert isinstance(error, AccountTypeError)
    assert isinstance(error, AccountError)
    assert isinstance(error, DebtonatorError)
```

### Type-Specific Error Testing

```python
def test_credit_limit_error():
    """Test CreditLimitExceededError construction and properties."""
    account_id = 42
    attempted_amount = Decimal("2000.00")
    available_credit = Decimal("1000.00")
    
    error = CreditLimitExceededError(
        account_id=account_id, 
        attempted_amount=attempted_amount,
        available_credit=available_credit
    )
    
    assert error.account_id == account_id
    assert error.attempted_amount == attempted_amount
    assert error.available_credit == available_credit
    
    # Test error message contains relevant information
    error_msg = str(error)
    assert str(account_id) in error_msg
    assert str(attempted_amount) in error_msg
    assert str(available_credit) in error_msg
```

## Best Practices

1. **Follow Naming Conventions**: Error class tests should follow the established naming convention
2. **Test All Error Types**: Each error class should have dedicated tests
3. **Verify Complete Inheritance**: Test the full inheritance chain
4. **Test All Parameters**: Ensure all constructor parameters work correctly
5. **Test Error Messages**: Verify that error messages include the right content
