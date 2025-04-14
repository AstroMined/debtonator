# Account Type Schema Tests

This directory contains tests for the polymorphic account type schema system implemented as part of ADR-016 and ADR-019.

## Structure

The test files follow the same structure as the source code:

```
tests/unit/schemas/account_types/
├── __init__.py
├── test_account_type_unions.py  # Tests for discriminated union validation
├── banking/
│   ├── __init__.py
│   ├── test_checking_schemas.py
│   ├── test_credit_schemas.py 
│   ├── test_savings_schemas.py
│   ├── test_payment_app_schemas.py
│   ├── test_bnpl_schemas.py
│   └── test_ewa_schemas.py
└── README.md
```

## Testing Approach

Each account type has its own dedicated test file that tests:

1. Creating accounts with minimum required fields
2. Creating accounts with all fields populated
3. Validation of type-specific fields
4. Validation that the account_type field must match the schema's type
5. Response schema validation

Additionally, `test_account_type_unions.py` tests the discriminated union functionality:

1. Proper routing of validation based on account_type 
2. Validation that type-specific fields are rejected on incorrect account types
3. Testing field validation at the union level rather than the base schema level

This architecture-aligned testing approach tests validation at the correct level:
- Base schema only validates universal fields
- Type-specific schemas validate their own fields
- Discriminated unions route validation based on account_type

This modular approach allows for easy addition of new account types in the future without creating monolithic test files or adding specific type validations to the base schema.

## Running Tests

Run the tests for a specific account type:

```bash
pytest tests/unit/schemas/account_types/banking/test_checking_schemas.py -v
```

Run all account type schema tests:

```bash
pytest tests/unit/schemas/account_types/ -v
```
