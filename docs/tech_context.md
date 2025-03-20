# Technical Context: Debtonator

## Technology Stack

### Backend
- **Framework**: FastAPI
  - High performance, modern Python web framework
  - Native async support
  - Automatic OpenAPI documentation
  - Built-in data validation with Pydantic

- **Repository Pattern**:
  - Separates data access logic from business logic
  - Provides a consistent interface for database operations
  - Encapsulates SQLAlchemy-specific implementation details
  - Enables easier testing through dependency injection
  - Reduces code duplication across services
  - Improves maintainability through smaller, focused components

- **Repository Components**:
  - BaseRepository<ModelType, PKType>: Generic base class with CRUD operations
  - Model-specific repositories: Extend BaseRepository with specialized queries
  - RepositoryFactory: Manages and caches repository instances
  - Dependency injection: Provides repositories to services via FastAPI dependencies

- **Repository Features**:
  - Type-safe operations with generics
  - Pagination support for querying large datasets
  - Filtering capabilities for complex queries
  - Relationship loading with eager loading patterns
  - Transaction support for multi-operation consistency
  - Bulk operations for improved performance

- **Database**:
  - Development: SQLite
    - Simple setup
    - File-based storage
    - Perfect for development and testing
  - Production: MySQL/MariaDB
    - Robust and reliable
    - Strong community support
    - Excellent performance for this use case

- **Data Validation**: Pydantic
  - Pydantic V2 style validation throughout
  - Type checking and automatic validation
  - Centralized UTC timezone handling via BaseSchemaValidator
  - Consistent field constraints with descriptive messages
  - Schema-based validation with proper inheritance
  - Comprehensive cross-field validation where needed

### Frontend
- **Framework**: React with TypeScript
  - Component-based architecture
  - Virtual DOM for performance
  - Large ecosystem of libraries
  - Strong community support
  - Type safety with TypeScript

- **UI Components**: Material-UI
  - Comprehensive component library
  - Customizable theming
  - Responsive design support
  - Form components
  - Data grid for tables

- **Form Management**: Formik & Yup
  - Form state management
  - Validation with Yup schemas
  - Error handling
  - Field-level validation
  - Form submission handling

## Technical Standards

### Datetime Handling
- All datetime fields use timezone-aware datetime objects
- UTC is used as the standard timezone for stored data
- SQLAlchemy models use `DateTime(timezone=True)`
- Pydantic schemas inherit from BaseSchemaValidator which enforces UTC timezone
- Automatic conversion from naive to UTC-aware datetime in model_validate
- Validation of timezone correctness with clear error messages
- Timezone conversion is handled in the UI layer
- All tests use timezone-aware datetime objects
- Field descriptions explicitly mention UTC timezone requirement

### Validation Architecture
- Three-layer validation approach:
  1. **Schema Layer**: Basic structural validation with Pydantic
     - Type checking
     - Field constraints (min/max values, string formats)
     - Required vs. optional fields
     - Decimal precision for monetary values
     - Cross-field validation for related fields
  2. **Service Layer**: Business logic validation
     - Complex validation rules
     - Data integrity checks
     - State-dependent validation
     - Data relationship validation
  3. **Database Layer**: Data integrity constraints
     - Foreign key constraints
     - Unique constraints
     - Check constraints
     - Default values

### Schema Standards
- All schema classes inherit from BaseSchemaValidator
- UTC timezone handling for all datetime fields
- Proper field descriptions with explicit purposes
- Decimal precision validation for monetary values (decimal_places=2)
- Modern union type syntax (Type | None) rather than Optional[Type]
- Comprehensive docstrings explaining class purpose
- Cross-field validation where appropriate
- Strong validation error messages
- Consistent naming patterns across related schemas

## Data Models

### Bulk Import
```python
class BulkImportResponse(BaseSchemaValidator):
    success: bool
    processed: int
    succeeded: int
    failed: int
    errors: List[ImportError] | None

class ImportError(BaseSchemaValidator):
    row: int
    field: str
    message: str

class BulkImportPreview(BaseSchemaValidator):
    records: List[Union[Bill, Income]]
    validation_errors: List[ImportError]
    total_records: int
```

### Bills (Liabilities)
```python
class Bill(BaseSchemaValidator):
    id: int
    name: str
    amount: Decimal = Field(..., decimal_places=2)
    due_date: datetime  # UTC timezone
    description: str | None
    category: str
    recurring: bool
    recurrence_pattern: Dict | None
    created_at: datetime  # UTC timezone
    updated_at: datetime  # UTC timezone

class BillCreate(BaseSchemaValidator):
    name: str
    amount: Decimal = Field(..., decimal_places=2)
    due_date: datetime  # UTC timezone
    description: str | None = None
    category: str
    recurring: bool = False
    recurrence_pattern: Dict | None = None
```

### Payments (Transactions)
```python
class Payment(BaseSchemaValidator):
    id: int
    bill_id: int | None  # Optional for non-bill expenses
    amount: Decimal = Field(..., decimal_places=2)
    payment_date: datetime  # UTC timezone
    description: str | None
    category: str
    created_at: datetime  # UTC timezone
    updated_at: datetime  # UTC timezone

class PaymentCreate(BaseSchemaValidator):
    bill_id: int | None
    amount: Decimal = Field(..., decimal_places=2)
    payment_date: datetime  # UTC timezone
    description: str | None = None
    category: str
```

### Payment Sources (Entries)
```python
class PaymentSource(BaseSchemaValidator):
    id: int
    payment_id: int
    account_id: int
    amount: Decimal = Field(..., decimal_places=2)
    created_at: datetime  # UTC timezone
    updated_at: datetime  # UTC timezone

class PaymentSourceCreate(BaseSchemaValidator):
    payment_id: int
    account_id: int
    amount: Decimal = Field(..., decimal_places=2)
```

### Accounts
```python
class Account(BaseSchemaValidator):
    id: int
    name: str
    type: str  # credit, checking, savings
    available_balance: Decimal = Field(..., decimal_places=2)
    available_credit: Decimal | None = Field(None, decimal_places=2)
    total_limit: Decimal | None = Field(None, decimal_places=2)
    last_statement_balance: Decimal | None = Field(None, decimal_places=2)
    last_statement_date: datetime | None  # UTC timezone
    created_at: datetime  # UTC timezone
    updated_at: datetime  # UTC timezone
```

### Income
```python
class Income(BaseSchemaValidator):
    id: int
    date: datetime  # UTC timezone
    source: str
    amount: Decimal = Field(..., decimal_places=2)
    deposited: bool
    undeposited_amount: Decimal = Field(..., decimal_places=2)
```

### Cashflow
```python
class CashflowForecast(BaseSchemaValidator):
    date: datetime  # UTC timezone
    total_bills: Decimal = Field(..., decimal_places=2)
    total_income: Decimal = Field(..., decimal_places=2)
    balance: Decimal = Field(..., decimal_places=2)
    forecast: Decimal = Field(..., decimal_places=2)
    min_14_day: Decimal = Field(..., decimal_places=2)
    min_30_day: Decimal = Field(..., decimal_places=2)
    min_60_day: Decimal = Field(..., decimal_places=2)
    min_90_day: Decimal = Field(..., decimal_places=2)
```

## Formula Translations

### Payment Calculations
```python
def validate_payment_sources(payment: Payment) -> bool:
    total_source_amount = sum(source.amount for source in payment.sources)
    return total_source_amount == payment.amount

def get_account_payments(account_id: int, payments: List[Payment]) -> Decimal:
    total = Decimal(0)
    for payment in payments:
        for source in payment.sources:
            if source.account_id == account_id:
                total += source.amount
    return total

def get_bill_payments(bill_id: int) -> List[Payment]:
    return Payment.objects.filter(bill_id=bill_id).order_by('payment_date')
```

### Account Calculations
```python
def calculate_available_credit(account: Account) -> Decimal:
    if account.type == "credit" and account.total_limit:
        return account.total_limit - abs(account.available_balance)
    return Decimal(0)

def update_account_balance(account: Account, amount: Decimal, is_credit: bool = False) -> Decimal:
    if is_credit:
        account.available_balance -= amount
    else:
        account.available_balance += amount
    return account.available_balance
```

### Income Calculations
```python
def calculate_undeposited_amount(income: Income) -> Decimal:
    return income.amount if not income.deposited else Decimal(0)
```

### Cashflow Calculations
```python
def calculate_daily_deficit(min_amount: Decimal, days: int) -> Decimal:
    return min_amount / days if min_amount < 0 else Decimal(0)

def calculate_yearly_deficit(daily_deficit: Decimal) -> Decimal:
    return daily_deficit * 365

def calculate_required_income(yearly_deficit: Decimal) -> Decimal:
    # Consider 80% after tax
    return abs(yearly_deficit) / Decimal('0.8')

def calculate_hourly_rate(required_income: Decimal, hours_per_week: int) -> Decimal:
    return required_income / 52 / hours_per_week
```

## Technical Constraints

### Data Migration
- Preserve all historical data since 2017
- Maintain data integrity during migration
- Verify calculation accuracy
- Handle date format conversions
- Convert bill splits to payment sources
- Link existing bills to new payment records

### Performance Requirements
- Fast cashflow calculations
- Quick forecast updates
- Responsive UI updates
- Efficient database queries
- Optimized payment tracking

### Security Requirements
- Secure user authentication
- Financial data encryption
- Secure API endpoints
- Input validation
- Account data protection

## Development Setup
1. Python virtual environment with UV
   - Centralized configuration in pyproject.toml
   - Dependency management with UV
   - Project metadata and build settings
   - Test configuration (pytest)
2. Node.js for frontend development
3. Local database instance
4. Development tools:
   - VS Code
   - Git for version control
   - Docker for containerization
   - Testing frameworks
   - ESLint and Prettier

## Deployment Considerations
1. Database migration strategy
   - Schema versioning
   - Data migration scripts
   - Rollback procedures
   - Payment data migration

2. API versioning
   - URL versioning
   - Backward compatibility
   - Documentation
   - OpenAPI/Swagger docs

3. Frontend deployment
   - Static file hosting
   - CDN integration
   - Build optimization
   - TypeScript compilation

4. Monitoring and logging
   - Application metrics
   - Error tracking
   - Performance monitoring
   - User analytics
   - Payment tracking logs

5. Backup strategy
   - Database backups
   - Data retention
   - Disaster recovery
   - Account data protection
