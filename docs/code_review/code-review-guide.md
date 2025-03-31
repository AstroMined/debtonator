# Debtonator Code Review Guide

## Overview

This guide provides detailed explanations and examples for the requirements in the [Code Review Checklist](./code-review-checklist.md). While the checklist serves as a quick verification tool, this guide offers deeper context, code examples, and rationale for each requirement.

## Repository Layer (ADR-014)

The repository layer is responsible for all database access operations. It encapsulates data access patterns and provides a clean API for services.

### Structure and Responsibilities

Repositories should focus exclusively on data access with no business logic or validation. This maintains a clear separation of concerns:

```python
# Good Example - Repository focused on data access
class LiabilityRepository(BaseRepository[Liability, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Liability)
        
    async def get_bills_due_in_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Liability]:
        """Get bills due within a date range (inclusive of both dates)."""
        # Use datetime_utils to ensure proper range handling per ADR-011
        range_start = start_of_day(ensure_utc(start_date))
        range_end = end_of_day(ensure_utc(end_date))
        
        # Pure data access logic, no business validation
        query = select(Liability).where(
            and_(
                Liability.due_date >= range_start,
                Liability.due_date <= range_end
            )
        ).order_by(Liability.due_date)
        
        result = await self.session.execute(query)
        return result.scalars().all()
```

```python
# Bad Example - Repository with business logic
class LiabilityRepository(BaseRepository[Liability, int]):
    # ...
    
    async def create_bill(self, bill_data: dict) -> Liability:
        # Business validation belongs in service layer, not repository
        if bill_data["amount"] <= 0:
            raise ValueError("Bill amount must be positive")
            
        # Business logic for categories belongs in service layer
        if "category_id" not in bill_data:
            bill_data["category_id"] = await self._get_default_category_id()
            
        # Data access is the repository's responsibility
        bill = Liability(**bill_data)
        self.session.add(bill)
        await self.session.flush()
        await self.session.refresh(bill)
        return bill
```

### Transaction Management

Repositories should handle transaction boundaries for multi-operation sequences:

```python
async def create_bill_with_splits(
    self, 
    bill_data: Dict[str, Any], 
    splits_data: List[Dict[str, Any]]
) -> Tuple[Liability, List[BillSplit]]:
    """
    Create a bill with multiple splits in a single transaction.
    
    All operations succeed or fail together.
    """
    # Start a transaction
    async with self.session.begin_nested():  # Creates a savepoint
        # Create the bill
        bill = await self.create(bill_data)
        
        # Create splits linked to the bill
        splits = []
        for split_data in splits_data:
            split_data["bill_id"] = bill.id
            split = await self.bill_split_repo.create(split_data)
            splits.append(split)
            
    # At this point, transaction is committed if all operations succeeded
    # or rolled back if any operation failed
    
    return bill, splits
```

### SQL Aggregation Patterns

SQL aggregation requires careful handling, especially with LEFT JOINs:

```python
async def get_category_with_bill_counts(self) -> List[Dict[str, Any]]:
    """
    Get categories with the count of bills in each.
    
    Uses proper SQL aggregation pattern with LEFT JOIN and func.count().
    """
    query = (
        select(
            Category,
            func.count(Liability.id).label("bill_count")  # Count non-NULL liability IDs
        )
        .outerjoin(Liability, Category.id == Liability.category_id)
        .group_by(Category.id)
        .order_by(Category.name)
    )
    
    result = await self.session.execute(query)
    
    categories_with_counts = []
    for category, bill_count in result:
        categories_with_counts.append({
            "id": category.id,
            "name": category.name,
            "bill_count": bill_count
        })
        
    return categories_with_counts
```

**Key Insight**: When using LEFT JOIN with aggregation:
- `func.count(*)` counts all rows, including those with NULL joined values
- `func.count(right_table.id)` only counts rows where the joined ID is not NULL
- This distinction is critical for accurate counts with OUTER JOINs

### Repository Testing Pattern

Repository tests should follow the Arrange-Schema-Act-Assert pattern to simulate the actual service-repository flow:

```python
@pytest.mark.asyncio
async def test_create_bill(session: AsyncSession):
    """Test creating a bill following the proper validation flow."""
    # 1. ARRANGE: Set up repository
    repo = LiabilityRepository(session)
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    bill_schema = LiabilityCreate(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=utc_datetime(2025, 4, 15),
        category_id=1,
        primary_account_id=1
    )
    
    # Convert validated schema to dict for repository
    validated_data = bill_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    bill = await repo.create(validated_data)
    
    # 4. ASSERT: Verify the operation results
    assert bill.id is not None
    assert bill.name == "Test Bill"
    assert bill.amount == Decimal("100.00")
    assert datetime_equals(bill.due_date, bill_schema.due_date)
    assert bill.category_id == 1
    assert bill.primary_account_id == 1
```

For detailed guidance, refer to the [Repository Test Pattern Guide](../guides/repository_test_pattern.md).

## Service Layer (ADR-012, ADR-014)

The service layer implements business logic, validation, and orchestrates operations across multiple repositories.

### Validation Flow

Services must validate input data through Pydantic schemas before passing it to repositories:

```python
class LiabilityService:
    def __init__(
        self, 
        liability_repo: LiabilityRepository,
        category_repo: CategoryRepository
    ):
        self.liability_repo = liability_repo
        self.category_repo = category_repo
        
    async def create_bill(self, bill_in: LiabilityCreate) -> Liability:
        """
        Create a new bill with proper validation.
        
        Performs business validation beyond schema validation.
        """
        # Schema validation happens when bill_in is created
        
        # Business rule validation
        valid, error_message = await self.validate_bill_creation(bill_in)
        if not valid:
            raise ValueError(error_message)
            
        # Convert validated schema to dict
        bill_data = bill_in.model_dump()
        
        # Pass validated data to repository
        return await self.liability_repo.create(bill_data)
        
    async def validate_bill_creation(
        self, 
        bill_in: LiabilityCreate
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate business rules for bill creation.
        
        Returns a tuple of (is_valid, error_message).
        """
        # Verify category exists
        category = await self.category_repo.get(bill_in.category_id)
        if not category:
            return False, f"Category with ID {bill_in.category_id} not found"
            
        # Verify account exists (assuming account check is needed)
        # ... other business rule validation
        
        return True, None
```

### Business Logic in Services

Business logic should be implemented in services, not models or repositories:

```python
class PaymentService:
    # ...
    
    async def make_payment(
        self, 
        payment_in: PaymentCreate, 
        user_id: int
    ) -> Payment:
        """
        Make a payment with proper business logic.
        
        This method handles complex business rules like:
        - Account balance updates
        - Payment status tracking
        - Notification generation
        """
        # Schema validation happens when payment_in is created
        
        # Business rule validation
        valid, error_message = await self.validate_payment(payment_in)
        if not valid:
            raise ValueError(error_message)
            
        # Convert validated schema to dict
        payment_data = payment_in.model_dump()
        
        # Add user information
        payment_data["created_by_user_id"] = user_id
        
        # Business logic: Mark payment as pending
        payment_data["status"] = "pending"
        
        # Create payment record
        payment = await self.payment_repo.create(payment_data)
        
        # Business logic: Update account balances
        await self.update_account_balances(payment)
        
        # Business logic: Track payment against bill
        await self.track_payment_for_bill(payment)
        
        # Business logic: Generate notifications
        await self.notification_service.generate_payment_notification(payment)
        
        return payment
```

## Schema Validation (ADR-012)

Schema validation provides the first line of defense against invalid data. Pydantic schemas are responsible for data structure validation.

### Schema Structure with Pydantic V2

Schemas should use Pydantic V2 features and extend `BaseSchemaValidator`:

```python
from typing import Optional, Annotated
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# Custom annotated types for validation
MoneyDecimal = Annotated[
    Decimal,
    Field(multiple_of=Decimal("0.01"), description="Monetary value with 2 decimal places")
]

class BaseSchemaValidator(BaseModel):
    """Base schema with common validation logic."""
    # Validation methods omitted for brevity
    
class PaymentCreate(BaseSchemaValidator):
    """Schema for creating a payment."""
    
    payment_date: datetime
    amount: MoneyDecimal = Field(gt=0, description="Payment amount (positive)")
    liability_id: int = Field(ge=1, description="ID of the bill to pay")
    account_id: int = Field(ge=1, description="ID of the account making the payment")
    description: Optional[str] = Field(None, max_length=200)
    
    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, v: datetime) -> datetime:
        """Ensure payment date is not in the distant past."""
        # Business validation: Payment date shouldn't be too far in the past
        if v < days_ago(365):
            raise ValueError("Payment date cannot be more than a year in the past")
        return v
```

### Dictionary Validation

Dictionary fields with decimal values require special validation:

```python
class AccountBalances(BaseSchemaValidator):
    """Schema for account balances data."""
    
    # Dictionary of account_id -> balance
    balances: Dict[int, MoneyDecimal] = Field(
        description="Account balances keyed by account ID"
    )
    
    # Dictionary of account_id -> percentage
    allocation_percentages: Dict[int, PercentageDecimal] = Field(
        description="Balance allocation percentages keyed by account ID"
    )
    
    @field_validator("allocation_percentages")
    @classmethod
    def validate_percentages_sum(cls, v: Dict[int, Decimal]) -> Dict[int, Decimal]:
        """Validate that allocation percentages sum to 1."""
        total = sum(v.values(), Decimal("0"))
        if not within_epsilon(total, Decimal("1.0"), Decimal("0.0001")):
            raise ValueError(
                f"Allocation percentages must sum to 1.0, got {total}"
            )
        return v
```

## Decimal Precision (ADR-013)

Decimal precision is critical for financial applications. Our approach uses a two-tier precision model:

1. 4 decimal places for storage and internal calculations
2. 2 decimal places for UI/API boundaries

### Annotated Types for Validation

Use specialized annotated types for different decimal purposes:

```python
from typing import Annotated
from decimal import Decimal
from pydantic import Field

# Money values with 2 decimal places (e.g., $100.00)
MoneyDecimal = Annotated[
    Decimal,
    Field(multiple_of=Decimal("0.01"), description="Monetary value with 2 decimal places")
]

# Percentage values with 4 decimal places (0-1 range, e.g., 0.1234 = 12.34%)
PercentageDecimal = Annotated[
    Decimal,
    Field(ge=0, le=1, multiple_of=Decimal("0.0001"), 
          description="Percentage value with 4 decimal places (0-1 range)")
]
```

### Distribution Strategies

When splitting bills or distributing amounts, use proper strategies to ensure exact sums:

```python
def distribute_with_largest_remainder(
    total: Decimal, 
    parts: int
) -> List[Decimal]:
    """
    Distribute a total amount into equal parts without losing cents.
    
    Args:
        total: Total amount to distribute
        parts: Number of parts to distribute into
            
    Returns:
        List of distributed amounts that sum exactly to the total
    """
    # Step 1: Calculate base amount (integer division)
    cents = int(total * 100)
    base_cents = cents // parts
    
    # Step 2: Calculate remainder
    remainder_cents = cents - (base_cents * parts)
    
    # Step 3: Distribute base amounts
    result = [Decimal(base_cents) / 100] * parts
    
    # Step 4: Distribute remainder one cent at a time
    for i in range(remainder_cents):
        result[i] += Decimal('0.01')
        
    return result
```

## Datetime Handling (ADR-011)

All datetime handling must comply with ADR-011, which requires consistent UTC-based datetime management.

### Utility Function Usage

Always use functions from `datetime_utils.py` instead of direct datetime functions:

```python
# INCORRECT ❌
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)
```

```python
# CORRECT ✅
from src.utils.datetime_utils import utc_now, days_ago

now = utc_now()
yesterday = days_ago(1)
```

### Date Range Handling

Date ranges should be inclusive of both start and end dates:

```python
async def get_transactions_in_range(
    self,
    account_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[Transaction]:
    """
    Get transactions within a date range.
    
    The range is INCLUSIVE of both start and end dates.
    """
    # Ensure proper date range boundaries per ADR-011
    range_start = start_of_day(ensure_utc(start_date))
    range_end = end_of_day(ensure_utc(end_date))
    
    query = select(Transaction).where(
        and_(
            Transaction.account_id == account_id,
            Transaction.transaction_date >= range_start,
            Transaction.transaction_date <= range_end  # Note <= for inclusivity
        )
    ).order_by(Transaction.transaction_date)
    
    result = await self.session.execute(query)
    return result.scalars().all()
```

### Cross-Database Compatibility

When comparing dates from database results, use compatibility functions:

```python
def compare_db_dates(dates_from_db: List[Any], test_date: date) -> bool:
    """
    Compare a test date against a list of dates from database.
    
    Handles different database engines' date representations.
    """
    for db_date in dates_from_db:
        # Normalize database date for comparison
        normalized_db_date = normalize_db_date(db_date)
        
        # Use date_equals for safe comparison
        if date_equals(normalized_db_date, test_date):
            return True
            
    return False
```

## Models and SQLAlchemy (ADR-012)

SQLAlchemy models should focus on data structure, not business logic. Validation belongs in the schema layer.

### Model Structure

```python
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database.base import Base

class Liability(Base):
    """
    Bill/liability model focused on data structure.
    
    No business logic or validation, just structure.
    """
    __tablename__ = "liabilities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 4), nullable=False)  # 4 decimal precision per ADR-013
    due_date = Column(DateTime(), nullable=False)    # No timezone parameter per ADR-011
    status = Column(String(20), nullable=False, default="unpaid")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    primary_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="bills")
    primary_account = relationship("Account", back_populates="primary_bills")
    payments = relationship("Payment", back_populates="bill")
    splits = relationship("BillSplit", back_populates="bill", cascade="all, delete-orphan")
    
    # Simple properties for derivable data are acceptable
    @property
    def is_overdue(self) -> bool:
        """Simple utility property to check if bill is overdue."""
        return self.due_date < datetime.now(timezone.utc) and self.status == "unpaid"
```

### Type Annotations with SQLAlchemy 2.0

Use newer SQLAlchemy 2.0 annotations for cleaner models:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class Account(Base):
    """
    Account model with SQLAlchemy 2.0 annotations.
    """
    __tablename__ = "accounts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    available_balance: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    available_credit: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    total_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    
    # Relationships
    statements: Mapped[List["StatementHistory"]] = relationship(back_populates="account")
    balances: Mapped[List["BalanceHistory"]] = relationship(back_populates="account")
```

## Testing Patterns

### Repository Testing

Repository tests should reflect the actual application flow:

```python
@pytest.mark.asyncio
async def test_get_bills_due_in_range(session: AsyncSession):
    """Test getting bills due in a date range."""
    # 1. ARRANGE: Set up fixtures
    repo = LiabilityRepository(session)
    
    # Create test bills with different due dates
    bill1 = create_liability_schema(
        name="Bill 1",
        due_date=utc_datetime(2025, 4, 15)
    )
    bill2 = create_liability_schema(
        name="Bill 2",
        due_date=utc_datetime(2025, 4, 25)
    )
    bill3 = create_liability_schema(
        name="Bill 3",
        due_date=utc_datetime(2025, 5, 5)
    )
    
    # Create bills through repository
    await repo.create(bill1.model_dump())
    await repo.create(bill2.model_dump())
    await repo.create(bill3.model_dump())
    
    # 2. ACT: Call repository method
    start_date = utc_datetime(2025, 4, 10)
    end_date = utc_datetime(2025, 4, 30)
    bills = await repo.get_bills_due_in_range(start_date, end_date)
    
    # 3. ASSERT: Verify results
    assert len(bills) == 2
    assert bills[0].name == "Bill 1"
    assert bills[1].name == "Bill 2"
    # Bill 3 should not be included (due in May)
```

### Schema Testing

Test both field constraints and validator methods:

```python
def test_payment_create_schema_validation():
    """Test payment schema validation."""
    # Test valid data
    valid_payment = PaymentCreate(
        payment_date=utc_now(),
        amount=Decimal("100.00"),
        liability_id=1,
        account_id=1,
        description="Test payment"
    )
    assert valid_payment.amount == Decimal("100.00")
    
    # Test invalid data - should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        PaymentCreate(
            payment_date=utc_now(),
            amount=Decimal("-100.00"),  # Negative amount
            liability_id=1,
            account_id=1
        )
    assert "amount" in str(exc_info.value)
    assert "greater than" in str(exc_info.value)
    
    # Test decimal precision validation
    with pytest.raises(ValueError) as exc_info:
        PaymentCreate(
            payment_date=utc_now(),
            amount=Decimal("100.001"),  # 3 decimal places
            liability_id=1,
            account_id=1
        )
    assert "multiple of" in str(exc_info.value)
```

## Testing Philosophy: Integration-First with Real Objects

Debtonator follows an integration-first testing approach that emphasizes using real objects rather than mocks:

1. **No Mocks Policy**: We strictly prohibit using unittest.mock, MagicMock, or any other mocking libraries.
2. **Real Database Testing**: We use a real test database that gets set up and torn down between each test.
3. **Cross-Layer Integration**: Tests should verify real interactions between layers using actual objects.
4. **Real Repositories**: Service tests use real repositories connected to the test database.
5. **Real Schemas**: All data validation uses real Pydantic schemas, not test dummies.

This approach provides several benefits:

- Tests catch real integration issues that mocks would miss
- Tests validate actual database operations and constraints
- Test maintenance is simpler without complex mock setups
- Tests provide higher confidence in production behavior

### Service Testing

Test business logic and validation in services using real repositories:

```python
@pytest.mark.asyncio
async def test_service_validation_logic(
    db_session: AsyncSession,  # Real test database session
    account_repo_fixture: AccountRepository,  # Real repository fixture
    category_repo_fixture: CategoryRepository  # Real repository fixture
):
    """Test service validation logic with real repositories."""
    # Create service with real repositories
    account_service = AccountService(
        account_repo=account_repo_fixture,
        category_repo=category_repo_fixture
    )
    
    # Test validation logic for non-existent account
    with pytest.raises(ValueError) as exc_info:
        await account_service.get_account_with_validation(999)  # Non-existent ID
        
    # Verify proper error message
    assert "not found" in str(exc_info.value)
    
    # Create an account to test positive case
    account_schema = create_account_schema(name="Test Account")
    await account_repo_fixture.create(account_schema.model_dump())
    
    # Now test with a valid account ID
    result = await account_service.get_account_with_validation(1)
    assert result is not None
    assert result.name == "Test Account"
```

## API Layer (ADR-010)

### Endpoint Design

API endpoints should follow consistent URL patterns:

```python
# Entity endpoints follow consistent pattern
@router.get("/{entity_id}", response_model=EntityResponse)
@router.post("/", response_model=EntityResponse, status_code=201)
@router.put("/{entity_id}", response_model=EntityResponse)
@router.delete("/{entity_id}", status_code=204)

# Collection endpoints use plural names
@router.get("/", response_model=List[EntityResponse])

# Nested resources use sub-paths
@router.get("/{entity_id}/related-items", response_model=List[RelatedItemResponse])

# Actions use verbs with POST
@router.post("/{entity_id}/actions/mark-as-completed", response_model=EntityResponse)
```

### Dependency Injection

Use FastAPI's dependency injection for services and repositories:

```python
# Repository dependencies
def get_account_repository(session: AsyncSession = Depends(get_db)) -> AccountRepository:
    return AccountRepository(session)

# Service dependencies that use repositories
def get_account_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    statement_repo: StatementHistoryRepository = Depends(get_statement_history_repository)
) -> AccountService:
    return AccountService(account_repo, statement_repo)

# API endpoints that use services
@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service)
):
    account = await account_service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
```

## Common Pitfalls to Avoid

### Repository Layer

1. **Validation in Repositories**:
   - **Incorrect**: Validating user input in repositories
   - **Correct**: Assume data is validated by services before reaching repositories

2. **Business Logic in Repositories**:
   - **Incorrect**: Implementing business rules in repositories
   - **Correct**: Focus on data access patterns only

3. **Direct Model Construction**:
   - **Incorrect**: Services creating model instances directly
   - **Correct**: Pass validated dictionaries to repositories which handle model creation

### Schema Layer

1. **Bypassing Validation**:
   - **Incorrect**: Creating/modifying dictionaries after validation
   - **Correct**: Use schema validation for all data

2. **Pydantic V1 Style**:
   - **Incorrect**: Using deprecated `@validator` decorators
   - **Correct**: Use `@field_validator` with `@classmethod`

3. **Missing Annotated Types**:
   - **Incorrect**: Using raw `Decimal` without constraints
   - **Correct**: Use specialized `MoneyDecimal` or `PercentageDecimal` types

### Datetime Handling

1. **Raw Datetime Functions**:
   - **Incorrect**: Using `datetime.now()` directly
   - **Correct**: Use `utc_now()` from datetime_utils

2. **Exclusive Date Ranges**:
   - **Incorrect**: Using `<` for end date comparisons
   - **Correct**: Use `<=` for inclusive date ranges

3. **Database Date Comparisons**:
   - **Incorrect**: Directly comparing dates from different database engines
   - **Correct**: Use `date_equals()` or `datetime_equals()` utilities

### Service Layer

1. **Raw SQL in Services**:
   - **Incorrect**: Writing SQL queries in services
   - **Correct**: Use repositories for all data access

2. **Skipping Validation**:
   - **Incorrect**: Passing unvalidated data to repositories
   - **Correct**: Always validate through Pydantic schemas first

3. **Mixing Concerns**:
   - **Incorrect**: Services handling both validation and HTTP response formatting
   - **Correct**: Services focus on business logic, let API layer handle HTTP concerns

## Conclusion

This guide provides detailed explanations and examples for the requirements in the Code Review Checklist. By following these patterns and practices, we can maintain high code quality, consistent architecture, and avoid common pitfalls.

For specific implementation details, consult:
- The relevant ADRs in `/docs/adr/`
- The code guides in `/docs/guides/`
- Example implementations in the codebase
