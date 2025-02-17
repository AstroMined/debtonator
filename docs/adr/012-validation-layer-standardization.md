# ADR-012: Validation Layer Standardization

## Status
Proposed

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

## Performance Impact
- Improved performance by reducing duplicate validation
- Better query efficiency with simpler models
- Reduced memory usage without redundant checks
- More efficient service layer operations

## Cost Considerations
- Development effort for refactoring
- Testing effort for validation coverage
- Documentation updates
- Training for new patterns

## Compliance & Security
- Improved validation consistency
- Better error handling
- Clearer security boundaries
- Enhanced data integrity

## Dependencies
- Pydantic V2
- SQLAlchemy 2.0+
- FastAPI

## Timeline
- Phase 1: 1 week
- Phase 2: 1 week
- Phase 3: 2 weeks
- Phase 4: 1 week

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
