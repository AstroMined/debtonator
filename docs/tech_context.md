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

### Frontend
- **Framework**: React
  - Component-based architecture
  - Virtual DOM for performance
  - Large ecosystem of libraries
  - Strong community support

- **State Management**: TBD
  - Options:
    - Redux for complex state
    - React Context for simpler state
    - React Query for server state

- **UI Components**: TBD
  - Options:
    - Material-UI
    - Chakra UI
    - Tailwind CSS

## Data Models

### Bills
```python
class Bill(BaseModel):
    id: int
    month: str
    day_of_month: int
    due_date: date
    paid_date: Optional[date]
    bill_name: str
    amount: Decimal
    up_to_date: bool
    account: str
    auto_pay: bool
    paid: bool
    amex_amount: Optional[Decimal]
    unlimited_amount: Optional[Decimal]
    ufcu_amount: Optional[Decimal]
```

### Income
```python
class Income(BaseModel):
    id: int
    date: date
    source: str
    amount: Decimal
    deposited: bool
    undeposited_amount: Decimal
```

### Accounts
```python
class Account(BaseModel):
    id: int
    name: str
    type: str
    available_balance: Decimal
    available_credit: Optional[Decimal]
```

### Cashflow
```python
class CashflowForecast(BaseModel):
    date: date
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

### Bill Calculations
```python
def calculate_account_amount(bill: Bill) -> Decimal:
    if not bill.paid:
        if bill.account == "AMEX":
            return bill.amount
        elif bill.account == "UNLIMITED":
            return bill.amount
        elif bill.account == "UFCU":
            return bill.amount
    return Decimal(0)
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

### Performance Requirements
- Fast cashflow calculations
- Quick forecast updates
- Responsive UI updates
- Efficient database queries

### Security Requirements
- Secure user authentication
- Financial data encryption
- Secure API endpoints
- Input validation

## Development Setup
1. Python virtual environment with UV
2. Node.js for frontend development
3. Local database instance
4. Development tools:
   - VS Code
   - Git for version control
   - Docker for containerization
   - Testing frameworks

## Deployment Considerations
1. Database migration strategy
   - Schema versioning
   - Data migration scripts
   - Rollback procedures

2. API versioning
   - URL versioning
   - Backward compatibility
   - Documentation

3. Frontend deployment
   - Static file hosting
   - CDN integration
   - Build optimization

4. Monitoring and logging
   - Application metrics
   - Error tracking
   - Performance monitoring
   - User analytics

5. Backup strategy
   - Database backups
   - Data retention
   - Disaster recovery
