# Debtonator v0.3.80

A modern bill and cashflow management system that helps track bills, income, and maintain sufficient account balances for timely bill payments.

## Features

- **Dynamic Account Management**
  - Multiple account types (credit, checking, savings)
  - Balance tracking and credit limit monitoring
  - Statement balance history with minimum payments and due dates
  - Comprehensive transaction history with credit/debit tracking
  - Account-specific transaction history
  - Balance history tracking
    * Historical balance changes
    * Balance trend analysis
    * Reconciliation support
    * Volatility calculation
    * Trend direction detection
  - Balance reconciliation with history tracking
  - Real-time available credit calculation with pending transaction support

- **Bill Management**
  - Track bills with due dates and payment status
  - Recurring bill templates with automatic generation
  - Split payment support across multiple accounts
  - Split analysis system
    * Optimization metrics calculation
      - Credit utilization tracking per account
      - Balance impact analysis
      - Risk scoring system
      - Optimization scoring
    * Impact analysis features
      - Short-term (30-day) projections
      - Long-term (90-day) projections
      - Risk factor identification
      - Smart recommendations
    * Optimization suggestions
      - Credit utilization balancing
      - Mixed account type strategies
      - Priority-based suggestions
    * Comprehensive test coverage
      - Metrics calculation scenarios
      - Impact analysis verification
      - Suggestion generation testing
  - Bulk operations system
    * Transaction-based bulk processing
    * Validation-only mode for dry runs
    * Comprehensive error tracking
    * Rollback support for failed operations
    * Success/failure tracking per split
  - Impact analysis system
    * Account impact calculations
    * Credit utilization projections
    * Cashflow impact analysis
    * Risk scoring with weighted factors
    * Recommendation generation
    * Comprehensive validation
  - Historical analysis system
    * Pattern identification with confidence scoring
    * Category and seasonal pattern grouping
    * Account usage frequency tracking
    * Pattern-based metrics and insights
    * Historical trend analysis
    * Weighted confidence scoring
  - Payment scheduling system
    * Schedule future payments
    * Automatic and manual processing
    * Date range filtering
    * Liability-based schedule filtering
    * Auto-processing for due payments
    * Schedule status tracking
    * Comprehensive validation
  - Comprehensive auto-pay functionality
    * Preferred payment date configuration (1-31)
    * Payment method selection
    * Minimum balance requirements
    * Auto-pay status tracking
    * Manual processing capability
    * Robust validation and error handling
    * Decimal precision handling
    * Standardized serialization
  - Payment history and tracking
  - Hierarchical category management
    * Parent-child category relationships
    * Full path property for hierarchy
    * Circular reference prevention
    * Category validation
  - Category-based organization
    * Bill categorization
    * Category inheritance
    * Category-based reporting

- **Income Management**
  - Record income sources and amounts
  - Track deposit status
  - Running total of undeposited income
  - Target account selection for deposits
  - Deposit scheduling system
    * Schedule deposits to specific accounts
    * Recurring deposit configuration
    * Amount validation against income
    * Pending deposit tracking
    * Account-specific filtering
    * Comprehensive validation
  - Income categorization system
    * Category management with CRUD operations
    * Category assignment to income records
    * Category-based income tracking
    * Duplicate category prevention
    * Comprehensive validation
  - Income Analysis System
    * Comprehensive income trends analysis
    * Source-specific trend analysis
    * Period-based income analysis
    * Pattern detection with confidence scoring
    * Weekly, monthly, and irregular pattern detection
    * Next occurrence prediction for reliable patterns
    * Seasonality analysis with peak/trough detection
    * Source statistics with reliability scoring
    * RESTful API endpoints for analysis
    * Comprehensive test coverage
    * Decimal precision handling
  - Recurring income system
    * Income templates for recurring patterns
    * Monthly income generation
    * Auto-deposit configuration
    * Template management with CRUD operations
    * Duplicate prevention
    * Comprehensive validation
    * SQLite-compatible date handling

- **Cashflow Analysis**
  - Bill payment pattern analysis system
    * Pattern detection with confidence scoring
      - Regular payment pattern detection
      - Irregular payment identification
      - Seasonal pattern recognition
      - Monthly pattern analysis
    * Comprehensive metrics tracking
      - Frequency metrics (average days between, std dev, min/max)
      - Amount statistics (average, std dev, min/max, total)
      - Pattern-specific confidence scoring
    * Features include
      - Bill-specific pattern analysis
      - Category-based pattern detection
      - Date range filtering
      - Minimum sample size configuration
      - Pattern type classification
      - Detailed analysis notes
      - Due date proximity warnings
  - Real-time cashflow tracking
    * Account balance aggregation across all accounts
    * Real-time available funds calculation
    * Available credit tracking
    * Next bill due date tracking
    * Days until next bill calculation
    * Minimum balance requirements
    * Projected deficit calculation
    * Comprehensive test coverage
    * RESTful API endpoint
  - Custom forecast system
    * Configurable forecast parameters
    * Account and category filtering
    * Confidence scoring
    * Risk factor assessment
    * Contributing factor tracking
    * Summary statistics
    * Comprehensive test coverage
  - Account-specific forecasts system
    * Daily balance projections
    * Recurring bill handling with monthly patterns
    * Credit utilization tracking for credit accounts
    * Warning flags for low balances and high utilization
    * Confidence scoring system
    * Transaction-level detail tracking
    * Balance volatility calculation
    * Comprehensive test coverage
  - Historical trends analysis
    * Pattern detection with confidence scoring
    * Holiday impact analysis with ±7 day range
    * Significant event detection with type-based thresholds
    * Seasonality analysis with multiple pattern types
    * Monthly, daily, and weekly pattern tracking
    * Transaction type-based averages
    * Comprehensive test coverage
  - Cross-account analysis system
    * Account correlation analysis
      - Transfer frequency tracking
      - Common category identification
      - Relationship type detection (complementary/supplementary/independent)
      - Correlation scoring
    * Transfer pattern analysis
      - Average transfer amounts
      - Transfer frequency tracking
      - Category distribution analysis
      - Typical transfer timing detection
    * Usage pattern analysis
      - Primary use detection
      - Average transaction size calculation
      - Common merchant tracking
      - Peak usage day identification
      - Category preference analysis
      - Credit utilization tracking
    * Balance distribution analysis
      - Average balance tracking
      - Balance volatility calculation
      - 30-day min/max tracking
      - Typical balance range analysis
      - Total funds percentage calculation
    * Risk assessment system
      - Overdraft risk calculation
      - Credit utilization risk tracking
      - Payment failure risk assessment
      - Volatility scoring
      - Overall risk scoring
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
- Node.js 18+
- SQLite (development)
- MySQL/MariaDB (production)

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
    └── models/        # Model-specific tests (99% coverage)
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
- **Payment Schedules Service**: Manages scheduled payments and processing
- **Bill Splits Service**: Handles split payment logic and validation
- **Recurring Bills Service**: Manages recurring bill templates and generation
- **Cashflow Service**: Manages cashflow calculations and forecasting
- **Income Service**: Handles income tracking and deposit management
- **Liabilities Service**: Manages bill/liability operations
- **Payments Service**: Processes payments and payment sources
- **Transaction Service**: Manages account transaction history

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
- Function-scoped fixtures with model defaults
- Proper async/await handling for SQLAlchemy
- HTTPX AsyncClient for API testing
- Automatic relationship loading
- Standardized timestamp handling

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

- API Layer (Improving Coverage)
  - Payment Scheduling API (100% coverage)
    * Complete CRUD operations
    * Schedule processing endpoints
    * Date range filtering
    * Error handling
    * Validation
  - Recurring Bills API (100% coverage)
    * Complete CRUD operations
    * Bill generation endpoints
    * Edge case handling
    * Response validation
    * Account validation
  - Balance Reconciliation API (100% coverage)
    * CRUD operations
    * Error handling
    * Validation
  - Other APIs (28-44% coverage)
    * Basic CRUD operations
    * Initial error handling
    * Planned for expansion

- Service Layer (High Coverage Services)
  - Payment Schedules Service (100% coverage)
    * CRUD operations
    * Schedule processing
    * Auto-processing
    * Error handling
    * Validation
  - Payments Service (100% coverage)
    * CRUD operations
    * Error handling
    * Relationship loading
    * Transaction management
  - Income Service (100% coverage)
    * CRUD operations
    * Account balance updates
    * Deposit status handling
    * Category management
    * Deposit scheduling
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
  - Transaction Service (100% coverage)
    * Credit/debit transaction handling
    * Balance impact tracking
    * Transaction history management
    * Error scenarios
  - Balance Reconciliation Service (100% coverage)
    * Balance adjustment tracking
    * Reconciliation history
    * Account balance updates
    * Error handling
  - Recurring Bills Service (100% coverage)
    * CRUD operations with 100% coverage
    * Bill generation functionality
    * Active/inactive bill filtering
    * Edge case handling
    * Duplicate prevention
    * Comprehensive test fixtures
  - Auto-pay Service (100% coverage)
    * Settings management
    * Payment processing
    * Status tracking
    * Candidate identification
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
