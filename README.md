# Debtonator v0.3.11

A modern bill and cashflow management system that helps track bills, income, and maintain sufficient account balances for timely bill payments.

## Features

- **Dynamic Account Management**
  - Multiple account types (credit, checking, savings)
  - Balance tracking and credit limit monitoring
  - Statement balance history with minimum payments and due dates
  - Account-specific transaction history

- **Bill Management**
  - Track bills with due dates and payment status
  - Split payment support across multiple accounts
  - Auto-pay status tracking
  - Payment history and tracking

- **Income Tracking**
  - Record income sources and amounts
  - Track deposit status
  - Running total of undeposited income
  - Target account selection for deposits

- **Cashflow Analysis**
  - 90-day rolling forecast
  - Available credit/balance tracking
  - Minimum required funds calculation
  - Required additional income analysis

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Pydantic (Data validation)
- SQLite (Development)
- MySQL/MariaDB (Production)

### Frontend
- React with TypeScript
- Material-UI components
- Redux Toolkit for state management
- Formik & Yup for form handling

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL/MariaDB (for production)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/debtonator.git
cd debtonator
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head
```

3. Set up the frontend:
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env if needed
```

### Running the Application

1. Start the backend server:
```bash
# From the root directory
uvicorn src.main:app --reload
```

2. Start the frontend development server:
```bash
# From the frontend directory
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

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

### Test Coverage (94% Overall)
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

- Service Layer (High Coverage Services)
  - Payments Service (100% coverage)
    * CRUD operations
    * Error handling
    * Relationship loading
    * Transaction management
  - Income Service (86% coverage)
    * CRUD operations
    * Account balance updates
    * Deposit status handling
    * Error scenarios
  - Bill Splits Service (100% coverage)
    * Split validation
    * Balance tracking
    * Error handling
  - Liabilities Service (100% coverage)
    * CRUD operations
    * Relationship management
    * Error scenarios
  - Bulk Import Service (91% coverage)
    * Data validation
    * Import processing
    * Error handling

### Running Tests
```bash
# Run all tests
pytest -q --tb=no --disable-warnings

# Run specific test file
pytest tests/models/test_accounts.py -v

# Run specific test
pytest tests/models/test_accounts.py::TestAccount::test_create_checking_account -v
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
