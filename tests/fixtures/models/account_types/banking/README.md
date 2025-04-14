# Banking Account Types Model Fixtures

This directory contains fixture functions for creating test instances of banking account type models used throughout the Debtonator application. These fixtures follow the polymorphic model patterns defined in the system architecture.

## Related Documentation

- [Parent Models Fixtures README](../../README.md)
- [Repository Banking Account Types Fixtures](../../../../repositories/account_types/banking/README.md)
- [ADR-016: Account Type Polymorphic Models](/code/debtonator/docs/adr/backend/ADR-016-account-type-polymorphic-models.md)
- [ADR-019: Polymorphic Schema Design](/code/debtonator/docs/adr/backend/ADR-019-polymorphic-schema-design.md)

## Architecture

Banking account types extend the base Account model using SQLAlchemy's polymorphic inheritance. Each subclass implements specialized fields and behavior specific to that account type, following the design outlined in ADR-016.

```tree
Account (Base Class)
├── BankingAccount (Abstract)
│   ├── CheckingAccount
│   ├── SavingsAccount
│   └── CreditAccount
├── InvestmentAccount (Abstract)
├── LoanAccount (Abstract)
└── ...
```

## Implementation Patterns

### Polymorphic Model Instantiation

All fixtures in this directory follow the correct polymorphic instantiation pattern:

```python
# ✅ Correct: Using concrete subclass constructor 
checking = CheckingAccount(
    name="Primary Checking",
    available_balance=Decimal("1000.00"),
    current_balance=Decimal("1000.00")
)

# ❌ Incorrect: Setting discriminator on base class
account = Account(
    name="Primary Checking",
    account_type="checking",  # Will cause SQLAlchemy polymorphic warnings
    available_balance=Decimal("1000.00"),
    current_balance=Decimal("1000.00")
)
```

### Type-Specific Fields

Each account type fixture includes the specialized fields specific to that account type:

- **CheckingAccount**: overdraft_limit, daily_withdrawal_limit
- **SavingsAccount**: interest_rate, minimum_balance, withdrawal_limit
- **CreditAccount**: credit_limit, available_credit, last_statement_balance, autopay_status
- **BNPLAccount**: purchase_amount, remaining_balance, merchant_name, installment_count
- **EWAAccount**: advance_limit, remaining_advance_limit, employer_name, pay_period_end
- **PaymentAppAccount**: linked_account_id, transfer_limit, verification_status

### UTC Datetime Compliance

All fixtures follow the ADR-011 datetime standard by using the `naive_utc_now()` function for database fields:

```python
from src.utils.datetime_utils import naive_utc_now

account = CheckingAccount(
    # ... other fields
    created_at=naive_utc_now(),
    updated_at=naive_utc_now()
)
```

## Available Fixtures

### fixture_checking_models.py

- **test_checking_account**: Basic checking account
- **test_checking_with_overdraft**: Checking with overdraft protection
- **test_checking_with_limits**: Checking with withdrawal limits configured
- **test_checking_with_negative_balance**: Account with negative balance for testing

### fixture_savings_models.py

- **test_savings_account**: Basic savings account
- **test_savings_with_interest**: Savings with interest rate configured
- **test_savings_with_min_balance**: Savings with minimum balance requirement
- **test_savings_with_withdrawal_limit**: Savings with withdrawal limits

### fixture_credit_models.py

- **test_credit_account**: Basic credit account
- **test_credit_with_balance**: Credit account with existing balance
- **test_credit_with_due_date**: Credit account with statement date and due date
- **test_credit_with_rewards**: Credit account with rewards program

### fixture_bnpl_models.py

- **test_bnpl_account**: Buy-now-pay-later account with installments
- **test_bnpl_paid_account**: BNPL account that's fully paid off
- **test_bnpl_past_due**: BNPL account that's past due

### fixture_ewa_models.py

- **test_ewa_account**: Early wage access account
- **test_ewa_with_employer**: EWA with employer information
- **test_ewa_with_advances**: EWA with existing advances

### fixture_payment_app_models.py

- **test_payment_app_account**: Payment app account
- **test_payment_app_verified**: Payment app with verified status
- **test_payment_app_with_linked_account**: Payment app linked to another account

## Testing Strategy

These fixtures are designed to support testing that verifies:

1. **Polymorphic Integrity**: Proper inheritance and polymorphic identity
2. **Type-Specific Validation**: Specialized validation for each account type
3. **Relationship Loading**: Proper loading of type-specific relationships
4. **Field Defaults**: Correct default values for type-specific fields
5. **Edge Cases**: Boundary conditions specific to each account type

## Known Considerations

1. All model fixtures should use the proper SQLAlchemy subclass that matches the polymorphic type
2. When specifying balances, use Decimal with string values (`Decimal("100.00")`) for precision
3. For timezone-sensitive fields, use the appropriate utility functions
4. Fixtures should avoid persistent IDs to prevent test interdependencies
5. To test type-specific validation, use the Repository Layer rather than direct model manipulation
