# Error Handling Guide: Debtonator

This guide provides detailed information and examples for implementing error handling in the Debtonator system, with special focus on account type-specific errors.

## Error Hierarchy Design

Debtonator uses a hierarchical error structure that mirrors the domain model:

```dir
AccountError
├── AccountNotFoundError
├── AccountTypeError
├── AccountValidationError
├── AccountOperationError
└── (Account Type-Specific Errors)
    ├── CheckingAccountError
    │   ├── CheckingOverdraftError
    │   ├── CheckingInsufficientFundsError
    │   ├── CheckingInvalidRoutingNumberError
    │   └── CheckingInternationalBankingError
    ├── SavingsAccountError
    │   ├── SavingsWithdrawalLimitError
    │   ├── SavingsMinimumBalanceError
    │   ├── SavingsInterestRateError
    │   └── SavingsCompoundFrequencyError
    ├── CreditAccountError
    │   ├── CreditCreditLimitExceededError
    │   ├── CreditPaymentDueError
    │   ├── CreditAPRError
    │   └── CreditStatementError
    └── ...
```

## Naming Conventions

When creating error classes, follow these naming conventions:

1. **Base errors**: Use general descriptive names ending with `Error` suffix
   - Example: `AccountError`, `RepositoryError`

2. **Account type base errors**: Include the account type name followed by `AccountError`
   - Example: `CheckingAccountError`, `SavingsAccountError`

3. **Specific error types**: Start with the account type name followed by the specific error condition and `Error` suffix
   - Example: `CheckingOverdraftError`, `SavingsWithdrawalLimitError`

4. **Avoid name conflicts**: Use fully qualified names to prevent import conflicts
   - Example: `BNPLProviderError` instead of generic `ProviderError`

## Directory Structure

Organize error classes in a structure that mirrors the domain model:

```dir
src/errors/
├── __init__.py                     # Exports all error classes
├── accounts.py                     # Base account errors
├── http_exceptions.py              # HTTP-specific exceptions
├── feature_flags.py                # Feature flag related errors
├── utils.py                        # Error conversion utilities
└── account_types/                  # Type-specific errors
    ├── __init__.py                 # Exports all account type errors
    └── banking/                    # Banking category errors
        ├── __init__.py             # Exports all banking error classes
        ├── checking.py             # Checking-specific errors
        ├── savings.py              # Savings-specific errors
        ├── credit.py               # Credit-specific errors
        ├── payment_app.py          # Payment app-specific errors
        ├── bnpl.py                 # BNPL-specific errors
        └── ewa.py                  # EWA-specific errors
```

## Implementation Examples

### Base Error Class

```python
# src/errors/accounts.py
from typing import Optional, Dict, Any

class AccountError(Exception):
    """Base class for all account-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result
```

### Account Type-Specific Base Error

```python
# src/errors/account_types/banking/checking.py
from typing import Optional, Dict, Any
from src.errors.accounts import AccountError

class CheckingAccountError(AccountError):
    """Base class for checking account errors."""
    
    def __init__(
        self, 
        message: str, 
        account_id: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        super().__init__(message, combined_details)
```

### Specific Error Class

```python
# src/errors/account_types/banking/checking.py
class CheckingOverdraftError(CheckingAccountError):
    """Error raised when overdraft limit is exceeded."""
    
    def __init__(
        self, 
        message: str, 
        account_id: Optional[int] = None,
        current_balance: Optional[float] = None,
        overdraft_limit: Optional[float] = None,
        transaction_amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if current_balance is not None:
            combined_details["current_balance"] = current_balance
        if overdraft_limit is not None:
            combined_details["overdraft_limit"] = overdraft_limit
        if transaction_amount is not None:
            combined_details["transaction_amount"] = transaction_amount
        super().__init__(message, account_id, combined_details)
```

### Package Export Setup

```python
# src/errors/account_types/banking/__init__.py
from src.errors.account_types.banking.checking import CheckingAccountError, CheckingOverdraftError, CheckingInsufficientFundsError, CheckingInvalidRoutingNumberError, CheckingInternationalBankingError
from src.errors.account_types.banking.savings import SavingsAccountError, SavingsWithdrawalLimitError, SavingsMinimumBalanceError, SavingsInterestRateError, SavingsCompoundFrequencyError
from src.errors.account_types.banking.credit import CreditAccountError, CreditCreditLimitExceededError, CreditPaymentDueError, CreditAPRError, CreditAutopayError, CreditStatementError
# ...more imports...
```

```python
# src/errors/__init__.py
from src.errors.accounts import AccountError, AccountNotFoundError, AccountTypeError, AccountValidationError, AccountOperationError
from src.errors.account_types import (
    # Checking account errors
    CheckingAccountError, CheckingOverdraftError, CheckingInsufficientFundsError,
    # other error imports...
)
```

## Error Usage Examples

### Raising Errors

```python
# In service layer
def withdraw(self, account_id: int, amount: Decimal) -> None:
    account = self.repository.get(account_id)
    if account is None:
        raise AccountNotFoundError(account_id)
        
    if not isinstance(account, CheckingAccount):
        raise AccountTypeError(
            f"Operation not supported for account type: {account.account_type}",
            account.account_type
        )
    
    if account.current_balance + account.overdraft_limit < amount:
        raise CheckingOverdraftError(
            f"Withdrawal of {amount} exceeds available balance including overdraft limit",
            account_id=account_id,
            current_balance=account.current_balance,
            overdraft_limit=account.overdraft_limit,
            transaction_amount=amount
        )
    
    # Proceed with withdrawal...
```

### Catching and Translating Errors

```python
# In API layer
@router.post("/accounts/{account_id}/withdraw", response_model=WithdrawalResponse)
async def withdraw(
    account_id: int, 
    withdrawal_data: WithdrawalRequest,
    service: AccountService = Depends(get_account_service)
):
    try:
        result = await service.withdraw(account_id, withdrawal_data.amount)
        return WithdrawalResponse(success=True, new_balance=result.new_balance)
    except AccountNotFoundError as e:
        raise AccountNotFoundHTTPException(account_id=account_id)
    except CheckingOverdraftError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "overdraft_limit_exceeded",
                "message": str(e),
                "current_balance": e.details.get("current_balance"),
                "overdraft_limit": e.details.get("overdraft_limit"),
                "transaction_amount": e.details.get("transaction_amount")
            }
        )
    except AccountTypeError as e:
        raise AccountTypeHTTPException(account_type=e.details.get("account_type"))
    except Exception as e:
        logger.error(f"Unexpected error in withdraw: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_server_error", "message": "An unexpected error occurred"}
        )
```

## Error Translation Utilities

Create utility functions to standardize error translation between layers:

```python
# src/errors/utils.py
from fastapi import HTTPException, status
from src.errors.accounts import AccountError, AccountNotFoundError, AccountTypeError
from src.errors.http_exceptions import (
    AccountHTTPException, AccountNotFoundHTTPException, AccountTypeHTTPException
)

def account_error_to_http_exception(error: AccountError) -> HTTPException:
    """Convert an AccountError to the appropriate HTTPException."""
    if isinstance(error, AccountNotFoundError):
        return AccountNotFoundHTTPException(account_id=error.details.get("account_id"))
    elif isinstance(error, AccountTypeError):
        return AccountTypeHTTPException(account_type=error.details.get("account_type"))
    # Add more specialized conversions
    
    # Default to a general account error
    return AccountHTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": error.__class__.__name__,
            "message": str(error),
            **error.details
        }
    )
```

## Testing Errors

Create comprehensive tests for your error classes:

```python
# tests/unit/errors/test_account_errors.py
import pytest
from decimal import Decimal
from src.errors.accounts import AccountError, AccountNotFoundError
from src.errors.account_types.banking.checking import CheckingOverdraftError

def test_account_error_base():
    """Test base AccountError class."""
    error = AccountError("Test error message", {"test_key": "test_value"})
    assert str(error) == "Test error message"
    assert error.message == "Test error message"
    assert error.details == {"test_key": "test_value"}
    
    # Test to_dict method
    error_dict = error.to_dict()
    assert error_dict["error"] == "AccountError"
    assert error_dict["message"] == "Test error message"
    assert error_dict["details"] == {"test_key": "test_value"}

def test_account_not_found_error():
    """Test AccountNotFoundError class."""
    error = AccountNotFoundError(42)
    assert "Account with ID 42 not found" in str(error)
    assert error.details["account_id"] == 42

def test_checking_overdraft_error():
    """Test CheckingOverdraftError with all parameters."""
    error = CheckingOverdraftError(
        "Withdrawal exceeds available funds",
        account_id=42,
        current_balance=Decimal("100.00"),
        overdraft_limit=Decimal("200.00"),
        transaction_amount=Decimal("350.00")
    )
    
    assert "Withdrawal exceeds available funds" in str(error)
    assert error.details["account_id"] == 42
    assert error.details["current_balance"] == Decimal("100.00")
    assert error.details["overdraft_limit"] == Decimal("200.00")
    assert error.details["transaction_amount"] == Decimal("350.00")
```

## Best Practices

1. **Be Specific**: Use the most specific error class appropriate for the situation

   ```python
   # Instead of:
   raise AccountError("Insufficient funds")
   
   # Use:
   raise CheckingInsufficientFundsError(
     "Insufficient funds for withdrawal",
     account_id=account_id,
     available_balance=available,
     requested_amount=amount
   )
   ```

2. **Include Context**: Always include relevant contextual information

   ```python
   # Instead of:
   raise AccountValidationError("Invalid account data")
   
   # Use:
   raise AccountValidationError(
     "Invalid account data",
     field_errors={"name": "Name cannot be empty", "balance": "Initial balance must be positive"}
   )
   ```

3. **Consistent Constructors**: Use consistent parameter patterns across similar error classes

   ```python
   # All "not found" errors should have similar constructor patterns:
   class AccountNotFoundError(AccountError):
     def __init__(self, account_id: int, message: Optional[str] = None):
       message = message or f"Account with ID {account_id} not found"
       super().__init__(message, {"account_id": account_id})
   
   class TransactionNotFoundError(TransactionError):
     def __init__(self, transaction_id: int, message: Optional[str] = None):
       message = message or f"Transaction with ID {transaction_id} not found"
       super().__init__(message, {"transaction_id": transaction_id})
   ```

4. **Clean Error Messages**: Make error messages user-friendly and actionable

   ```python
   # Instead of:
   raise MinimumBalanceError("balance < minimum")
   
   # Use:
   raise SavingsMinimumBalanceError(
     f"Account balance ${current} is below minimum required balance ${minimum}",
     account_id=account_id,
     current_balance=current,
     minimum_balance=minimum
   )
   ```

5. **Layer Responsibility**: Handle errors at the appropriate layer
   - **Service Layer**: Business logic validation errors
   - **Repository Layer**: Data access errors
   - **API Layer**: Request validation and error translation to HTTP responses

6. **Error Translation**: Use consistent error translation between layers

   ```python
   # API endpoint error handling
   try:
     result = await service.some_operation()
     return SuccessResponse(result=result)
   except AccountError as e:
     # Translate domain errors to HTTP exceptions
     raise account_error_to_http_exception(e)
   ```

7. **Error Hierarchies**: Keep error hierarchies shallow and focused
   - Aim for 2-3 levels of inheritance maximum
   - Group errors by domain concept, not by technical detail
   - Create specialized errors only when they need different parameters or handling

8. **Testing**: Create comprehensive tests for error scenarios
   - Test error instantiation with various parameter combinations
   - Test error message formatting
   - Test error translation between layers
   - Test error handling in API endpoints

## Dealing with Third-Party Errors

Wrap third-party errors in your application's error hierarchy:

```python
from sqlalchemy.exc import IntegrityError, OperationalError
from src.errors.database import DatabaseError, DatabaseIntegrityError, DatabaseConnectionError

async def create_account(self, account_data):
    try:
        account = Account(**account_data)
        self.session.add(account)
        await self.session.commit()
        return account
    except IntegrityError as e:
        await self.session.rollback()
        if "foreign key constraint" in str(e).lower():
            raise DatabaseIntegrityError("Foreign key constraint violation", original_error=e)
        elif "unique constraint" in str(e).lower():
            raise DatabaseIntegrityError("Unique constraint violation", original_error=e)
        else:
            raise DatabaseIntegrityError("Database integrity error", original_error=e)
    except OperationalError as e:
        await self.session.rollback()
        raise DatabaseConnectionError("Database connection error", original_error=e)
```

## Error Logging

Implement consistent error logging across the application:

```python
import logging
from src.errors.accounts import AccountError

logger = logging.getLogger(__name__)

def process_transaction(transaction_data):
    try:
        # Transaction processing logic
        pass
    except AccountNotFoundError as e:
        # Expected error, log at info level
        logger.info(f"Account not found during transaction processing: {e}", 
                   extra={"account_id": e.details.get("account_id")})
        raise
    except AccountError as e:
        # Business logic error, log at warning level
        logger.warning(f"Account error during transaction processing: {e}",
                      extra={"details": e.details})
        raise
    except Exception as e:
        # Unexpected error, log at error level
        logger.error(f"Unexpected error during transaction processing: {e}", 
                    exc_info=True)
        raise
```

## Feature Flag Integration

Consider feature flag-related errors:

```python
# src/errors/feature_flags.py
from typing import Optional, Dict, Any
from src.errors.accounts import AccountError

class FeatureFlagAccountError(AccountError):
    """Error raised when an operation is blocked by a feature flag."""
    
    def __init__(
        self, 
        message: str, 
        feature_flag: str,
        account_id: Optional[int] = None,
        account_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        combined_details["feature_flag"] = feature_flag
        if account_id:
            combined_details["account_id"] = account_id
        if account_type:
            combined_details["account_type"] = account_type
        super().__init__(message, combined_details)
```

```python
# Usage in service layer
def create_bnpl_account(self, account_data):
    if not self.feature_flag_service.is_enabled("BNPL_ACCOUNTS_ENABLED"):
        raise FeatureFlagAccountError(
            "BNPL accounts are not currently enabled",
            feature_flag="BNPL_ACCOUNTS_ENABLED",
            account_type="bnpl"
        )
    
    # Continue with account creation...
```

## Conclusion

A well-designed error handling system provides several benefits:

1. **Improved Debugging**: Specific error types with detailed context make debugging easier
2. **Better User Experience**: Clear error messages help users understand issues
3. **Code Clarity**: Error types document expected failure modes
4. **Maintainability**: Hierarchical error structure scales with the domain model
5. **Consistency**: Standardized error handling across the application

By following the patterns in this guide, you'll create a robust error handling system that scales with your application's complexity.
