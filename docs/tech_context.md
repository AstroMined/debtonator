# Technical Context: Debtonator

## Technology Stack

### Backend
- **Framework**: FastAPI
  - High performance, modern Python web framework
  - Native async support
  - Automatic OpenAPI documentation
  - Built-in data validation with Pydantic

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
  - Type checking
  - Data validation
  - Settings management
  - Schema definition
  - Timezone-aware datetime handling

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
- Pydantic schemas use `datetime` with explicit timezone info
- Timezone conversion is handled in the UI layer
- All tests use timezone-aware datetime objects

## Data Models

### Bulk Import
```python
class BulkImportResponse(BaseModel):
    success: bool
    processed: int
    succeeded: int
    failed: int
    errors: Optional[List[ImportError]]

class ImportError(BaseModel):
    row: int
    field: str
    message: str

class BulkImportPreview(BaseModel):
    records: List[Union[Bill, Income]]
    validation_errors: List[ImportError]
    total_records: int
```

### Bills (Liabilities)
```python
class Bill(BaseModel):
    id: int
    name: str
    amount: Decimal
    due_date: datetime
    description: Optional[str]
    category: str
    recurring: bool
    recurrence_pattern: Optional[dict]
    created_at: datetime
    updated_at: datetime

class BillCreate(BaseModel):
    name: str
    amount: Decimal
    due_date: datetime
    description: Optional[str]
    category: str
    recurring: bool = False
    recurrence_pattern: Optional[dict] = None
```

### Payments (Transactions)
```python
class Payment(BaseModel):
    id: int
    bill_id: Optional[int]  # Optional for non-bill expenses
    amount: Decimal
    payment_date: datetime
    description: Optional[str]
    category: str
    created_at: datetime
    updated_at: datetime

class PaymentCreate(BaseModel):
    bill_id: Optional[int]
    amount: Decimal
    payment_date: datetime
    description: Optional[str]
    category: str
```

### Payment Sources (Entries)
```python
class PaymentSource(BaseModel):
    id: int
    payment_id: int
    account_id: int
    amount: Decimal
    created_at: datetime
    updated_at: datetime

class PaymentSourceCreate(BaseModel):
    payment_id: int
    account_id: int
    amount: Decimal
```

### Accounts
```python
class Account(BaseModel):
    id: int
    name: str
    type: str  # credit, checking, savings
    available_balance: Decimal
    available_credit: Optional[Decimal]
    total_limit: Optional[Decimal]
    last_statement_balance: Optional[Decimal]
    last_statement_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
```

### Income
```python
class Income(BaseModel):
    id: int
    date: datetime
    source: str
    amount: Decimal
    deposited: bool
    undeposited_amount: Decimal
```

### Cashflow
```python
class CashflowForecast(BaseModel):
    date: datetime
    total_bills: Decimal
    total_income: Decimal
    balance: Decimal
    forecast: Decimal
    min_14_day: Decimal
    min_30_day: Decimal
    min_60_day: Decimal
    min_90_day: Decimal
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
