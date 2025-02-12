# Debtonator v1.3.0

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
    └── models/        # Model-specific tests
        ├── test_accounts.py     # Account model tests
        ├── test_liabilities.py  # Liability model tests
        └── test_payments.py     # Payment model tests
```

## Testing

The project includes a comprehensive test suite focusing on data integrity and model relationships:

### Test Infrastructure
- SQLite in-memory database for testing
- Transaction-based test isolation
- Function-scoped fixtures for clean test state
- Proper async/await handling for SQLAlchemy
- Automatic relationship loading

### Test Coverage
- Account Model Tests (5 tests)
  - Account type validation
  - Balance operations
  - Credit limit calculations
  - Default value handling

- Liability Model Tests (7 tests)
  - Basic and recurring liabilities
  - Account relationships
  - Payment status tracking
  - Optional field handling

- Payment Model Tests (6 tests)
  - Basic payment creation
  - Split payment handling
  - Source management
  - Relationship validation

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
