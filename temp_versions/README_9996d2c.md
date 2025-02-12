# Debtonator v1.4.0

[Previous content up to Project Structure remains unchanged...]

## Project Structure

```
debtonator/
├── alembic/              # Database migrations
├── docs/                 # Project documentation
│   ├── adr/             # Architecture Decision Records
│   └── ...              # Other documentation
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Redux store and slices
│   │   │   └── slices/  # Feature-specific slices
│   │   └── types/       # TypeScript types
│   └── ...
├── src/                 # Backend application
│   ├── api/            # API endpoints
│   ├── models/         # Database models
│   │   ├── liabilities.py  # Bill tracking (liabilities)
│   │   ├── payments.py     # Payment and source tracking
│   │   └── ...            # Other models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── utils/          # Utilities
└── tests/              # Test suites
    ├── conftest.py    # Test configuration and fixtures
    └── models/        # Model-specific tests (97% coverage)
        ├── test_accounts.py     # Account model tests
        ├── test_cashflow.py     # Cashflow calculations
        ├── test_income.py       # Income tracking
        ├── test_liabilities.py  # Liability model tests
        ├── test_payments.py     # Payment model tests
        └── test_recurring_bills.py  # Recurring bill templates
```

## Testing

The project includes a comprehensive test suite focusing on data integrity and model relationships:

### Test Infrastructure
- SQLite in-memory database for testing
- Transaction-based test isolation
- Function-scoped fixtures for clean test state
- Proper async/await handling for SQLAlchemy
- Automatic relationship loading

### Test Coverage (97% Overall)
- Account Model Tests (5 tests, 98% coverage)
  - Account type validation
  - Balance operations
  - Credit limit calculations
  - Default value handling

- Cashflow Model Tests (5 tests, 97% coverage)
  - Deficit calculations
  - Required income projections
  - Hourly rate calculations
  - Forecast validations

- Income Model Tests (5 tests, 100% coverage)
  - Income tracking
  - Deposit status
  - Undeposited calculations
  - Account relationships

- Liability Model Tests (7 tests, 96% coverage)
  - Basic and recurring liabilities
  - Account relationships
  - Payment status tracking
  - Optional field handling

- Payment Model Tests (6 tests, 94% coverage)
  - Basic payment creation
  - Split payment handling
  - Source management
  - Relationship validation

- RecurringBill Model Tests (4 tests, 100% coverage)
  - Template creation
  - Liability generation
  - Account relationships
  - Category assignment

### Running Tests
```bash
# Run all tests
pytest -q --tb=no --disable-warnings

# Run specific test file
pytest tests/models/test_accounts.py -v

# Run specific test
pytest tests/models/test_accounts.py::TestAccount::test_create_checking_account -v
```

[Rest of the content remains unchanged...]
