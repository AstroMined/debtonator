# Debtonator v0.3.5

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
│   │   ├── bill_splits.py  # Split payment handling
│   │   ├── cashflow.py     # Cashflow calculations
│   │   ├── income.py       # Income management
│   │   ├── liabilities.py  # Liability operations
│   │   └── payments.py     # Payment processing
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

## Service Layer Design

The service layer implements consistent patterns for efficient data access and relationship handling:

### Key Features
- Automatic relationship loading using SQLAlchemy's joinedload()
- Proper transaction management
- Fresh data fetching after modifications
- N+1 query prevention
- Consistent error handling

### Service Components
- **Bill Splits Service**: Handles split payment logic and validation
- **Cashflow Service**: Manages cashflow calculations and forecasting
- **Income Service**: Handles income tracking and deposit management
- **Liabilities Service**: Manages bill/liability operations
- **Payments Service**: Processes payments and payment sources

### Design Patterns
```python
# Example service method pattern
async def get_entity(self, entity_id: int) -> Optional[Entity]:
    stmt = (
        select(Entity)
        .options(
            joinedload(Entity.relationship1),
            joinedload(Entity.relationship2)
        )
        .filter(Entity.id == entity_id)
    )
    result = await self.db.execute(stmt)
    return result.unique().scalar_one_or_none()

# Example create pattern
async def create_entity(self, data: EntityCreate) -> Entity:
    db_entity = Entity(**data.model_dump())
    self.db.add(db_entity)
    await self.db.commit()
    
    # Fetch fresh copy with relationships
    stmt = (
        select(Entity)
        .options(
            joinedload(Entity.relationship1),
            joinedload(Entity.relationship2)
        )
        .filter(Entity.id == db_entity.id)
    )
    result = await self.db.execute(stmt)
    return result.unique().scalar_one()
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
  - Relationship loading patterns
  - Transaction management
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
