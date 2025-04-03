# Account Type Repository Module Pattern

This directory implements the Repository Module Pattern for account types, designed to scale to hundreds of account types without creating unwieldy monolithic repositories.

## Pattern Overview

1. **Base Repository**: `src/repositories/accounts.py` contains common operations for all account types
2. **Specialized Modules**: Each account type has its own module with specialized operations
3. **Dynamic Loading**: The `RepositoryFactory` dynamically loads and binds specialized functions
4. **No Code Duplication**: Common operations live in the base repository only
5. **Registry Integration**: Account types can register their repository modules in the registry

## Directory Structure

```
src/repositories/
├── accounts.py                  # Base AccountRepository (common operations)
├── factory.py                   # RepositoryFactory for dynamic loading
├── account_types/
│   ├── __init__.py              # Exports & consolidates functionality
│   ├── banking/
│   │   ├── __init__.py          # Exports banking-specific operations
│   │   ├── checking.py          # CheckingAccount-specific operations
│   │   ├── credit.py            # CreditAccount-specific operations
│   │   ├── savings.py           # SavingsAccount-specific operations
│   │   └── ...
│   ├── investment/
│   │   ├── __init__.py
│   │   ├── brokerage.py
│   │   ├── retirement.py
│   │   └── ...
│   └── loan/
│       ├── __init__.py
│       ├── mortgage.py
│       ├── personal.py
│       └── ...
```

## Usage Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService

# Create session and feature flag service
session = AsyncSession(...)
feature_flag_service = FeatureFlagService(...)

# Create repository for a specific account type
# All type-specific functions are automatically bound
checking_repo = RepositoryFactory.create_account_repository(
    session=session,
    account_type="checking",
    feature_flag_service=feature_flag_service
)

# Use base operations
all_accounts = await checking_repo.get_all()
account_by_id = await checking_repo.get(42)

# Use specialized operations (automatically bound from checking.py)
accounts_with_overdraft = await checking_repo.get_checking_accounts_with_overdraft()
interest_bearing = await checking_repo.get_interest_bearing_checking_accounts()

# Example with credit accounts
credit_repo = RepositoryFactory.create_account_repository(
    session=session, 
    account_type="credit"
)

# Mix of base and specialized operations
active_credit = await credit_repo.get_active_accounts()
accounts_near_limit = await credit_repo.get_credit_accounts_near_limit(threshold_percentage=0.8)
utilization_metrics = await credit_repo.get_credit_utilization_by_account()
```

## Adding New Account Types

1. Create a new module in the appropriate subdirectory
2. Implement specialized functions that take a session as their first parameter
3. Update the appropriate `__init__.py` files
4. (Optional) Register the module path in `AccountTypeRegistry`

## Benefits

- **Scalability**: Easily supports hundreds of account types
- **Maintainability**: Each account type has isolated code
- **DRY Design**: Common operations defined only once
- **Extensibility**: New account types can add specialized operations
- **Feature Flag Integration**: Integrates with the feature flag system
