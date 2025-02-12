# Debtonator v1.5.0

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

### Test Coverage (57% Overall)
- Models Layer (94-100% coverage)
  - Account operations and validation
  - Balance and credit calculations
  - Relationship integrity
  - Default value handling

- Schema Layer (88-100% coverage)
  - Data validation
  - Field constraints
  - Optional field handling
  - Relationship mapping

- API Layer (28-44% coverage)
  - Basic CRUD operations
  - Initial error handling
  - Needs more coverage

- Service Layer (20-40% coverage)
  - Core business logic
  - Basic validations
  - Needs more coverage

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
