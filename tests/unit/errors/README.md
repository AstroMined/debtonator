# Unit Tests for Error Classes

This directory contains unit tests for the error classes used throughout the Debtonator application. These tests verify error construction, inheritance hierarchy, and error-specific functionality.

## Purpose

Error class tests serve several important purposes:

1. **Verify Error Hierarchy**: Ensure that error inheritance works correctly
2. **Test Error Construction**: Validate that errors are constructed with proper parameters
3. **Verify Error Messages**: Ensure error messages are formatted correctly
4. **Test Error-specific Methods**: Validate any specialized methods on error classes
5. **Document Error Usage**: Demonstrate how to use errors effectively

## Directory Structure

Tests are organized to mirror the structure of the `src/errors` directory:

```tree
errors/
├── test_accounts_errors.py         # Tests for account-related errors
├── test_errors_init_errors.py      # Tests for base error classes
├── test_feature_flag_errors.py     # Tests for feature flag errors
├── test_http_exceptions_errors.py  # Tests for HTTP exception classes
└── account_types/                  # Tests for account type-specific errors
    └── banking/
        ├── test_checking_errors.py
        ├── test_savings_errors.py
        └── test_credit_errors.py
```

## Testing Focus Areas

### Error Hierarchy

Test that errors inherit correctly from parent classes:

```python
def test_account_error_hierarchy():
    """Test that AccountError inheritance hierarchy is correct."""
    # Test AccountError is a subclass of the base DebtonatorError
    assert issubclass(AccountError, DebtonatorError)
    
    # Test specific error is a subclass of AccountError
    assert issubclass(AccountNotFoundError, AccountError)
    
    # Test error instance relationships
    error = AccountNotFoundError(account_id=1)
    assert isinstance(error, AccountNotFoundError)
    assert isinstance(error, AccountError)
    assert isinstance(error, DebtonatorError)
    assert isinstance(error, Exception)
```

### Error Construction

Test that errors can be constructed with expected parameters:

```python
def test_account_not_found_error_construction():
    """Test constructing AccountNotFoundError with parameters."""
    account_id = 42
    error = AccountNotFoundError(account_id=account_id)
    
    assert error.account_id == account_id
    assert str(account_id) in str(error)  # ID should be in the error message
```

### Error Messages

Test that error messages are formatted correctly:

```python
def test_account_validation_error_message_format():
    """Test that error messages are formatted correctly."""
    field_name = "balance"
    message = "must be positive"
    error = AccountValidationError(field=field_name, message=message)
    
    error_str = str(error)
    assert field_name in error_str
    assert message in error_str
```

### Error-specific Methods

Test any specialized methods on error classes:

```python
def test_feature_flag_error_as_response():
    """Test converting FeatureFlagError to an API response."""
    error = FeatureFlagDisabledError(
        flag_name="banking_accounts", 
        message="Banking accounts are not enabled"
    )
    
    response = error.as_response()
    assert response["status_code"] == 403
    assert response["detail"] == "Feature 'banking_accounts' is disabled"
    assert response["error_type"] == "feature_flag_disabled"
```

## Best Practices

1. **Test All Error Classes**: Ensure every error class has dedicated tests
2. **Test Error Parameters**: Verify all constructor parameters work correctly
3. **Test Error Messages**: Ensure error messages contain relevant information
4. **Test Inheritance**: Verify subclassing works correctly with `isinstance` checks
5. **Document Behavior**: Use tests to demonstrate how errors should be used
