# ADR-012: Validation Layer Standardization

## Status
Implemented

## Context
Our current validation architecture has logic split across multiple layers:
- SQLAlchemy models using @validates decorators
- Pydantic schemas for data validation
- Business logic in models that should be in services

This creates several issues:
- Unclear responsibility boundaries
- Potential for validation conflicts
- Business logic mixed with data persistence
- Harder to maintain and test

## Decision
Standardize our validation approach following a clear separation of concerns:

1. Pydantic Layer (Input/Output Validation):
   - All data structure validation
   - Type checking
   - Field constraints
   - Format validation
   - No business logic

2. SQLAlchemy Layer (Data Persistence):
   - Database constraints only (unique, foreign keys, etc.)
   - No @validates decorators
   - No business logic
   - Focus on relationships and persistence

3. Service Layer (Business Logic):
   - All business rules
   - Complex calculations (like available_credit)
   - State management
   - Data consistency
   - Transaction management

## Technical Details

### 1. Schema Updates
```python
class AccountBase(BaseModel):
    """Base schema for account data with enhanced validation"""
    name: str = Field(..., min_length=1, max_length=50)
    type: AccountType
    available_balance: Decimal = Field(default=0)
    total_limit: Optional[Decimal] = Field(None, ge=0)

    @field_validator("total_limit")
    @classmethod
    def validate_total_limit(cls, v: Optional[Decimal], values: Dict[str, Any]) -> Optional[Decimal]:
        if v is not None and values.get("type") != "credit":
            raise ValueError("Total limit can only be set for credit accounts")
        return v
```

### 2. Model Simplification
```python
class Account(BaseDBModel):
    """Account model focused on persistence"""
    __tablename__ = "accounts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    available_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    available_credit: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    total_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
```

### 3. Service Layer Enhancement
```python
class AccountService:
    """Account service with business logic"""
    async def update_available_credit(self, account: Account) -> None:
        """Calculate and update available credit"""
        if account.type == "credit" and account.total_limit is not None:
            account.available_credit = account.total_limit - abs(account.available_balance)
            await self.session.commit()
            await self.session.refresh(account)

    async def update_account(self, account_id: int, data: AccountUpdate) -> Optional[Account]:
        """Update account with business logic"""
        account = await self.get_account(account_id)
        if not account:
            return None

        # Update fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(account, field, value)

        # Apply business logic
        await self.update_available_credit(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account
```

## Consequences

### Positive
- Clear separation of concerns
- Improved testability
- Better maintainability
- Consistent validation patterns
- Simplified model layer
- More robust service layer

### Negative
- Initial refactoring effort required
- Need to update existing tests
- Temporary duplication during migration

### Migration Strategy

1. Phase 1: Schema Enhancement
   - Update all Pydantic schemas
   - Add comprehensive validation
   - Update schema tests
   - Document validation rules

2. Phase 2: Model Simplification
   - Remove @validates decorators
   - Remove business logic
   - Update model tests
   - Document model changes

3. Phase 3: Service Enhancement
   - Move business logic to services
   - Add service methods
   - Update service tests
   - Document service patterns

4. Phase 4: Documentation
   - Update technical docs
   - Add validation examples
   - Document patterns
   - Update ADRs

## Implementation Progress

### Status and Timeline
- Phase 1: Completed
- Phase 2: Completed
- Phase 3: In Progress (Income and Liability Services completed)
- Phase 4: In Progress

### Completed Model Simplifications
1. **Categories Model**
   - Moved full_path property, is_ancestor_of() method, and _get_parent() to service layer
   - Enhanced model documentation with clear data structure focus
   - Fixed SQLAlchemy query handling for eager-loaded relationships

2. **CashflowForecast Model**
   - Moved calculation methods to service layer:
     * calculate_deficits()
     * calculate_required_income()
     * calculate_hourly_rates()
   - Removed unused ZoneInfo import
   - Enhanced model documentation with pure data structure focus

3. **Account Model**
   - Removed update_available_credit method 
   - Removed @validates decorators
   - Added _update_available_credit to service
   - Simplified model to pure data structure

4. **CreditLimitHistory Model**
   - Removed SQLAlchemy event listeners for validation
   - Added validate_credit_limit_history to AccountService
   - Enhanced model documentation with pure data structure focus

5. **RecurringBill Model**
   - Moved create_liability() method to service layer
   - Added create_liability_from_recurring() to RecurringBillService
   - Enhanced model documentation with pure data structure focus

6. **StatementHistory Model**
   - Moved due date calculation from __init__ method to service layer
   - Created new StatementService with calculate_due_date method
   - Enhanced model documentation with pure data structure focus

7. **RecurringIncome Model**
   - Moved create_income_entry() method to service layer
   - Added create_income_from_recurring() to RecurringIncomeService
   - Enhanced model documentation with pure data structure focus

8. **Income Model**
   - Moved calculate_undeposited() to service layer
   - Added _calculate_undeposited_amount and _update_undeposited_amount to service
   - Enhanced model documentation with pure data structure focus

### Completed Service Enhancements

1. **Income Service**
   ```python
   async def validate_income_create(self, income_data: IncomeCreate) -> Tuple[bool, Optional[str]]:
       """
       Validate an income creation request.
       
       Business rules validated:
       - Account must exist
       - Category must exist (if provided)
       """
       # Verify account exists
       account = await self._get_account(income_data.account_id)
       if not account:
           return False, f"Account with ID {income_data.account_id} not found"
       
       # Verify category exists if provided
       if income_data.category_id:
           category = await self._get_category(income_data.category_id)
           if not category:
               return False, f"Category with ID {income_data.category_id} not found"
       
       return True, None
   ```

2. **Liability Service**
   ```python
   async def validate_liability_create(self, liability_data: LiabilityCreate) -> Tuple[bool, Optional[str]]:
       """
       Validate a liability creation request.
       
       Business rules validated:
       - Category must exist
       - Primary account must exist
       - Due date must be valid
       """
       # Verify category exists
       category = await self._get_category(liability_data.category_id)
       if not category:
           return False, f"Category with ID {liability_data.category_id} not found"
       
       # Verify account exists
       account = await self._get_account(liability_data.primary_account_id)
       if not account:
           return False, f"Account with ID {liability_data.primary_account_id} not found"
       
       return True, None
   ```

3. **Category Service**
   ```python
   async def get_full_path(self, category: Category) -> str:
       """
       Get the full hierarchical path of a category.
       
       This method replaces the model property with a service method,
       moving business logic to the service layer per ADR-012.
       """
       if not category.parent_id:
           return category.name
           
       parent = await self.get_category(category.parent_id)
       if not parent:
           return category.name
           
       parent_path = await self.get_full_path(parent)
       return f"{parent_path} > {category.name}"
   ```

4. **Account Service**
   ```python
   async def validate_credit_limit_history(self, account_id: int) -> tuple[bool, Optional[str]]:
       """
       Validate that an account can have credit limit history.
       """
       # Account exists validation
       account = await self.get_account(account_id)
       if not account:
           return False, f"Account with ID {account_id} not found"
       
       # Credit account validation
       if account.type != "credit":
           return False, "Credit limit history can only be created for credit accounts"
       
       return True, None
   ```

### Remaining Work
1. **Documentation Updates**
   - Update technical documentation with model simplification approach
   - Add validation pattern examples across different services
   - Document relationships between services and models
   - Update ADRs with implementation details

## Performance Impact
- Improved performance by reducing duplicate validation
- Better query efficiency with simpler models
- Reduced memory usage without redundant checks
- More efficient service layer operations

## Compliance & Security
- Improved validation consistency
- Better error handling
- Clearer security boundaries
- Enhanced data integrity

## Dependencies
- Pydantic V2
- SQLAlchemy 2.0+
- FastAPI

## Monitoring & Success Metrics
- Test coverage metrics
- Code complexity metrics
- Error rates
- Performance metrics

## Team Impact
- Training on new validation patterns
- Updated code review guidelines
- Documentation requirements

## Related Documents
- ADR-011: Datetime Standardization
- System Patterns Documentation
- Technical Context Documentation

## Notes
- Consider impact on existing integrations
- Plan for backward compatibility
- Document migration patterns

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-02-17 | 1.0 | Cline | Initial version |
| 2025-03-13 | 2.0 | Cline | Updated with implementation progress |
