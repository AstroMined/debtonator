# ADR-022: Bills and Obligations Account Types Expansion

## Status

Proposed

## Executive Summary

Extends the polymorphic account architecture established in ADR-016 by implementing specialized obligation account types for recurring financial commitments including utilities, subscriptions, insurance, taxes, and legal support payments. This expansion provides comprehensive support for obligation-specific features including payment scheduling, due date calculation, payment history tracking, and specialized validation rules for each obligation type. The implementation enables improved cashflow forecasting, payment compliance tracking, and budget planning with specialized handling for varied payment frequencies and obligation-specific attributes, enhancing Debtonator's ability to provide users with a complete financial picture that includes all recurring financial obligations.

## Context

Building upon the polymorphic account model established in ADR-016 and subsequent implementations in ADR-019 (Banking), ADR-020 (Loans), and ADR-021 (Investments), we now need to address recurring financial obligations. These obligations, while not traditional accounts, are essential components of a user's financial picture and directly impact cashflow planning.

The current limitations in our system include:

1. Incomplete representation of recurring financial obligations beyond basic utility bills and subscriptions
2. Inability to track specialized recurring payments like insurance premiums, tax obligations, and legal support payments
3. Lack of specialized validation rules and business logic for different obligation types
4. Missing support for recurring payment scheduling, due date tracking, and payment history

These limitations prevent users from properly tracking and planning for all their financial obligations, leading to an incomplete financial picture and potentially missed payments.

## Decision

We will implement the following bills and obligations account types as part of the polymorphic inheritance structure defined in ADR-016:

1. **Utility Account**: For essential services like electricity, water, gas, internet, etc.
2. **Subscription Account**: For recurring digital and physical subscriptions
3. **Insurance Account**: For various insurance policies (auto, home, life, health, etc.)
4. **Tax Account**: For recurring tax obligations (property tax, estimated income tax, etc.)
5. **Support Payment Account**: For legal support obligations (child support, alimony)

Each account type will have specialized attributes and business logic to accurately represent its unique characteristics while supporting Debtonator's core financial planning features.

## Technical Details

### Architecture Overview

This ADR extends the polymorphic account model foundation established in ADR-016 by implementing specialized obligation account types. The architecture introduces:

- **Base ObligationAccount Class**: A shared parent model capturing common obligation attributes
- **Specialized Obligation Type Models**: Inheritance hierarchy for different obligation types
- **BillManagementService**: Centralized obligation management functionality
- **Obligation-Specific Repositories**: Specialized data access for obligations and payments

This design enables accurate representation of diverse financial obligations while sharing common functionality across all obligation types, following the same inheritance pattern established in previous ADRs for other account categories.

### Data Layer

#### Models

We will implement the following SQLAlchemy models for bills and obligations account types:

```python
class ObligationAccount(Account):
    """Base class for all obligation account types"""
    __tablename__ = "obligation_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    payment_amount = Column(Numeric(12, 4), nullable=False)
    payment_frequency = Column(String, nullable=False)  # monthly, quarterly, annual, etc.
    next_due_date = Column(DateTime(timezone=True), nullable=False)
    autopay_enabled = Column(Boolean, default=False, nullable=False)
    payment_method = Column(String, nullable=True)  # bank_account, credit_card, etc.
    payment_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    reminder_days = Column(Integer, default=7, nullable=False)  # Days before due date to send reminder
    
    # Relationships
    payment_account = relationship("Account", foreign_keys=[payment_account_id])
    payment_history = relationship("ObligationPayment", back_populates="obligation", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        "polymorphic_identity": "obligation",
    }
```

Each specialized obligation type will be implemented as a subclass:

```python
class UtilityAccount(ObligationAccount):
    """Utility service bills like electricity, water, gas, etc."""
    __tablename__ = "utility_accounts"
    
    id = Column(Integer, ForeignKey("obligation_accounts.id"), primary_key=True)
    service_type = Column(String, nullable=False)  # electricity, water, gas, internet, etc.
    service_address = Column(String, nullable=True)
    account_holder_name = Column(String, nullable=True)
    billing_cycle_day = Column(Integer, nullable=True)  # Day of month billing occurs
    average_bill_amount = Column(Numeric(12, 4), nullable=True)  # For variable bills
    
    __mapper_args__ = {
        "polymorphic_identity": "utility",
    }
```

Similar model classes will be created for SubscriptionAccount, InsuranceAccount, TaxAccount, and SupportPaymentAccount, each with type-specific fields.

To track payment history for obligations, we'll create a separate model:

```python
class ObligationPayment(Base):
    """Payment history for obligation accounts"""
    __tablename__ = "obligation_payments"
    
    id = Column(Integer, primary_key=True)
    obligation_id = Column(Integer, ForeignKey("obligation_accounts.id"), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(12, 4), nullable=False)
    payment_method = Column(String, nullable=True)
    confirmation_number = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    obligation = relationship("ObligationAccount", back_populates="payment_history")
```

#### Repositories

We'll implement an ObligationPaymentRepository and extend the AccountRepository with obligation-specific methods:

```python
class ObligationPaymentRepository(BaseRepository):
    """Repository for obligation payments"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.model_class = ObligationPayment
    
    def get_by_obligation(
        self, obligation_id: int, limit: int = 10
    ) -> List[ObligationPayment]:
        """Get payments for an obligation account"""
        return self.session.query(ObligationPayment).filter(
            ObligationPayment.obligation_id == obligation_id
        ).order_by(ObligationPayment.payment_date.desc()).limit(limit).all()
    
    def get_payments_in_date_range(
        self, 
        obligation_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[ObligationPayment]:
        """Get payments for an obligation account in a date range"""
        return self.session.query(ObligationPayment).filter(
            ObligationPayment.obligation_id == obligation_id,
            ObligationPayment.payment_date >= start_date,
            ObligationPayment.payment_date <= end_date
        ).order_by(ObligationPayment.payment_date).all()
```

Extension to AccountRepository:

```python
class AccountRepository(BaseRepository):
    # ... existing methods from previous ADRs ...
    
    def get_obligations_by_type(
        self, user_id: int, obligation_type: str
    ) -> List[ObligationAccount]:
        """Get all obligations of a specific type for a user"""
        model_class = self.account_type_registry.get_model_class(obligation_type)
        if not model_class or not issubclass(model_class, ObligationAccount):
            raise ValueError(f"Invalid obligation type: {obligation_type}")
        
        return self.session.query(model_class).filter(
            model_class.user_id == user_id
        ).all()
    
    def get_upcoming_obligations(
        self, user_id: int, days: int = 30
    ) -> List[ObligationAccount]:
        """Get obligations with due dates in the next X days"""
        now = datetime_utils.utc_now()
        end_date = datetime_utils.add_days(now, days)
        
        return self.session.query(ObligationAccount).filter(
            ObligationAccount.user_id == user_id,
            ObligationAccount.is_closed == False,
            ObligationAccount.next_due_date >= now,
            ObligationAccount.next_due_date <= end_date
        ).order_by(ObligationAccount.next_due_date).all()
    
    def get_overdue_obligations(self, user_id: int) -> List[ObligationAccount]:
        """Get obligations that are past due"""
        now = datetime_utils.utc_now()
        
        return self.session.query(ObligationAccount).filter(
            ObligationAccount.user_id == user_id,
            ObligationAccount.is_closed == False,
            ObligationAccount.next_due_date < now
        ).order_by(ObligationAccount.next_due_date).all()
```

### Business Logic Layer

#### Schemas

Following the pattern established in previous ADRs, we'll create Pydantic schemas for each obligation account type:

```python
class ObligationAccountBase(AccountBase):
    """Base schema for all obligation accounts"""
    payment_amount: MoneyDecimal
    payment_frequency: str
    next_due_date: datetime
    autopay_enabled: bool = False
    payment_method: Optional[str] = None
    payment_account_id: Optional[int] = None
    reminder_days: int = 7
    
    @field_validator("payment_frequency")
    @classmethod
    def validate_payment_frequency(cls, v):
        allowed_frequencies = ["weekly", "biweekly", "monthly", "quarterly", "semiannual", "annual"]
        if v.lower() not in allowed_frequencies:
            raise ValueError(f"Payment frequency must be one of: {', '.join(allowed_frequencies)}")
        return v.lower()
    
    @field_validator("reminder_days")
    @classmethod
    def validate_reminder_days(cls, v):
        if v < 0 or v > 90:
            raise ValueError("Reminder days must be between 0 and 90")
        return v

class ObligationAccountCreate(ObligationAccountBase, AccountCreate):
    """Base create schema for obligation accounts"""
    pass

class ObligationAccountResponse(ObligationAccountBase, AccountResponse):
    """Base response schema for obligation accounts"""
    pass
```

For each obligation type, we'll create corresponding Create and Response schemas. Here's an example for the Insurance account type:

```python
class InsuranceAccountCreate(ObligationAccountCreate):
    """Create schema for insurance accounts"""
    account_type: Literal["insurance"]
    policy_type: str
    provider: str
    policy_number: Optional[str] = None
    policy_start_date: datetime
    policy_end_date: datetime
    coverage_details: Optional[str] = None
    beneficiary: Optional[str] = None
    
    @field_validator("policy_type")
    @classmethod
    def validate_policy_type(cls, v):
        allowed_types = ["auto", "health", "home", "renters", "life", "disability", "umbrella", "pet", "other"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Policy type must be one of: {', '.join(allowed_types)}")
        return v.lower()
    
    @field_validator("policy_end_date")
    @classmethod
    def validate_policy_dates(cls, v, values):
        start_date = values.data.get("policy_start_date")
        if start_date and v < start_date:
            raise ValueError("Policy end date must be after the start date")
        return v

class InsuranceAccountResponse(ObligationAccountResponse):
    """Response schema for insurance accounts"""
    account_type: Literal["insurance"]
    policy_type: str
    provider: str
    policy_number: Optional[str] = None
    policy_start_date: datetime
    policy_end_date: datetime
    coverage_details: Optional[str] = None
    beneficiary: Optional[str] = None
    payment_history: Optional[List[ObligationPaymentResponse]] = None
```

For the API, we'll create discriminated unions:

```python
ObligationAccountCreateUnion = Annotated[
    Union[
        UtilityAccountCreate,
        SubscriptionAccountCreate,
        InsuranceAccountCreate,
        TaxAccountCreate,
        SupportPaymentAccountCreate,
    ],
    Field(discriminator="account_type")
]

ObligationAccountResponseUnion = Annotated[
    Union[
        UtilityAccountResponse,
        SubscriptionAccountResponse,
        InsuranceAccountResponse,
        TaxAccountResponse,
        SupportPaymentAccountResponse,
    ],
    Field(discriminator="account_type")
]
```

#### Services

To support obligation-specific operations and payments, we'll implement a BillManagementService:

```python
class BillManagementService:
    """Service for bill and obligation management"""
    
    def __init__(
        self,
        account_repository: AccountRepository,
        payment_repository: ObligationPaymentRepository
    ):
        self.account_repository = account_repository
        self.payment_repository = payment_repository
    
    def get_upcoming_bills(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get all upcoming bills for a user within the specified days"""
        now = datetime_utils.utc_now()
        end_date = datetime_utils.add_days(now, days)
        
        # Get all obligation accounts
        obligation_accounts = self.account_repository.get_by_user_and_types(
            user_id,
            ["utility", "subscription", "insurance", "tax", "support_payment"]
        )
        
        # Filter for accounts with due dates in the specified range
        upcoming_bills = []
        for account in obligation_accounts:
            if account.is_closed:
                continue
                
            if account.next_due_date >= now and account.next_due_date <= end_date:
                upcoming_bills.append({
                    "account_id": account.id,
                    "account_name": account.name,
                    "account_type": account.account_type,
                    "due_date": account.next_due_date,
                    "amount": account.payment_amount,
                    "payment_frequency": account.payment_frequency,
                    "autopay_enabled": account.autopay_enabled,
                    "days_until_due": (account.next_due_date - now).days,
                    "payment_account_id": account.payment_account_id,
                    "payment_method": account.payment_method
                })
        
        # Sort by due date
        return sorted(upcoming_bills, key=lambda x: x["due_date"])
    
    def record_payment(
        self, obligation_id: int, payment_data: Dict
    ) -> ObligationPayment:
        """Record a payment for an obligation account"""
        # Verify account exists
        account = self.account_repository.get(obligation_id)
        if not account or not isinstance(account, ObligationAccount):
            raise ValueError("Account is not a valid obligation account")
        
        # Create payment record
        payment_data["obligation_id"] = obligation_id
        payment = self.payment_repository.create(payment_data)
        
        # Calculate next due date based on payment frequency
        next_due_date = self._calculate_next_due_date(
            account.next_due_date, 
            account.payment_frequency
        )
        
        # Update account with new due date
        self.account_repository.update(
            obligation_id, 
            {"next_due_date": next_due_date}
        )
        
        # For SupportPaymentAccount, update arrears if applicable
        if isinstance(account, SupportPaymentAccount):
            self._update_support_payment_arrears(account, payment.amount)
        
        return payment
    
    # Additional methods for bill management, due date calculation, etc.
```

### API Layer

We will implement the following endpoints for obligation account management:

```python
@router.post("/accounts/obligations", response_model=ObligationAccountResponseUnion)
def create_obligation_account(
    account_data: ObligationAccountCreateUnion,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new obligation account."""
    data_dict = account_data.model_dump()
    data_dict["user_id"] = current_user.id
    
    # Set current_balance to payment_amount for obligations
    data_dict["current_balance"] = data_dict.get("payment_amount", 0)
    
    return account_service.create_account(data_dict)

@router.get("/accounts/obligations", response_model=List[ObligationAccountResponseUnion])
def get_obligation_accounts(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get all obligation accounts for the current user."""
    return account_service.get_obligation_accounts(current_user.id)

@router.get("/accounts/obligations/{account_id}/payments", response_model=List[ObligationPaymentResponse])
def get_obligation_payments(
    account_id: int,
    limit: int = Query(10, description="Maximum number of payments to return"),
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    bill_service: BillManagementService = Depends(get_bill_management_service)
):
    """Get payment history for an obligation account."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify account is an obligation account
    if not isinstance(account, ObligationAccount):
        raise HTTPException(status_code=400, detail="Account is not an obligation account")
    
    return bill_service.get_payment_history(account_id, limit)

@router.post("/accounts/obligations/{account_id}/payments", response_model=ObligationPaymentResponse)
def record_obligation_payment(
    account_id: int,
    payment_data: ObligationPaymentCreate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    bill_service: BillManagementService = Depends(get_bill_management_service)
):
    """Record a payment for an obligation account."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify account is an obligation account
    if not isinstance(account, ObligationAccount):
        raise HTTPException(status_code=400, detail="Account is not an obligation account")
    
    data_dict = payment_data.model_dump()
    return bill_service.record_payment(account_id, data_dict)
```

Additional endpoints will be implemented for bill management features:

```python
@router.get("/bills/upcoming", response_model=List[UpcomingBillResponse])
def get_upcoming_bills(
    days: int = Query(30, description="Number of days to look ahead"),
    current_user: User = Depends(get_current_user),
    bill_service: BillManagementService = Depends(get_bill_management_service)
):
    """Get upcoming bills for the current user."""
    return bill_service.get_upcoming_bills(current_user.id, days)

@router.get("/bills/by-category", response_model=BillsByCategoryResponse)
def get_bills_by_category(
    current_user: User = Depends(get_current_user),
    bill_service: BillManagementService = Depends(get_bill_management_service)
):
    """Get bills organized by category."""
    return bill_service.get_bills_by_category(current_user.id)

@router.get("/bills/by-due-date", response_model=BillsByDueDateResponse)
def get_bills_by_due_date(
    current_user: User = Depends(get_current_user),
    bill_service: BillManagementService = Depends(get_bill_management_service)
):
    """Get bills organized by due date."""
    return bill_service.get_bills_by_due_date(current_user.id)
```

### Frontend Considerations

The frontend implementation will need to:

- Create specialized forms for each obligation type with appropriate validation
- Implement obligation payment recording interfaces
- Develop visualizations for upcoming bills and payment history
- Create a bills dashboard with category-based and due date-based views
- Implement reminder notification displays

A dedicated frontend ADR will detail the specific UI/UX considerations for these obligation types.

### Config, Utils, and Cross-Cutting Concerns

#### Account Type Registry Updates

We'll update the AccountTypeRegistry to include the new obligation account types:

```python
# During application initialization
account_type_registry = AccountTypeRegistry()

# Register obligation account types
account_type_registry.register(
    account_type_id="utility",
    model_class=UtilityAccount,
    schema_class=UtilityAccountCreate,
    name="Utility",
    description="Recurring utility service like electricity, water, gas, etc.",
    category="Bills"
)

# Additional registration for other obligation types
```

#### Date Utility Functions

We'll enhance the existing datetime_utils module with functions specific to obligation management:

```python
def calculate_next_due_date(current_due_date: datetime, frequency: str) -> datetime:
    """Calculate the next due date based on payment frequency"""
    if frequency == "weekly":
        return add_days(current_due_date, 7)
    elif frequency == "biweekly":
        return add_days(current_due_date, 14)
    elif frequency == "monthly":
        return add_months(current_due_date, 1)
    # Additional frequencies handled similarly
```

### Dependencies and External Systems

This implementation has minimal external dependencies, primarily building on existing internal systems:

- Utilizes the Account polymorphic model foundation from ADR-016
- Extends the repository pattern established in ADR-014
- Leverages the datetime standardization from ADR-011
- Builds on decimal precision handling from ADR-013

### Implementation Impact

The complete implementation will require:

1. **Database Changes**:
   - New tables for the ObligationAccount base class and each subtype
   - New table for ObligationPayment history tracking
   - Migration scripts to create these tables with proper constraints

2. **Code Changes**:
   - New model classes for each obligation type
   - Schema implementations for all obligation types
   - Repository implementation for payment tracking
   - Service layer for obligation management
   - API endpoints for obligation operations
   - Registry updates for obligation type support

3. **Integration Points**:
   - Cashflow analysis service integration
   - Account selection dropdowns for payment account references
   - Budget category assignment integration
   - Payment recording integration with existing account systems

4. **Documentation**:
   - API documentation for obligation-specific endpoints
   - Schema documentation for new obligation types
   - Usage examples for bill management features

## Consequences

### Positive

1. **Comprehensive Bill Tracking**: Users can track all types of recurring financial obligations in one place, with dedicated fields for each obligation type's unique attributes.

2. **Payment History Tracking**: The system maintains a complete history of payments for each obligation, helping users verify compliance with payment schedules.

3. **Specialized Due Date Handling**: Different obligation types have customized due date calculation based on their specific payment frequencies.

4. **Support for Legal Obligations**: Special handling for legal support payments with arrears tracking ensures users stay compliant with legal requirements.

5. **Enhanced Financial Planning**: More detailed obligation tracking enables more accurate cashflow forecasting and budgeting.

### Negative

1. **Increased Schema Complexity**: The addition of a base ObligationAccount class and multiple subtypes increases the schema complexity.

2. **Maintenance Requirements**: Each obligation type requires ongoing maintenance to stay current with industry practices and regulations.

3. **UI Expansion Needed**: The frontend will need significant expansion to handle obligation-specific displays and payment recording.

### Neutral

1. **Migration Effort**: New tables need to be created for each obligation type as part of the database migration.

2. **Balance Semantics**: For obligation accounts, the current_balance field represents the amount due for the current period, which differs from asset or liability accounts.

## Quality Considerations

This implementation maintains and improves code quality through:

1. **Consistent Architecture Patterns**: Follows the established polymorphic account model pattern from ADR-016, ensuring architectural consistency across the system.

2. **Clear Separation of Concerns**:
   - Models focus on data structure and relationships
   - Schemas handle validation and API interaction
   - Repositories manage data access
   - Services encapsulate business logic

3. **Comprehensive Validation**: Includes thorough validation at multiple levels:
   - Field-level validation in Pydantic schemas
   - Cross-field validation for related fields
   - Business rule validation in service layer
   - Database-level constraints

4. **DRY Implementation**: Uses inheritance to avoid duplication:
   - Common obligation fields in base ObligationAccount class
   - Shared validation rules in base ObligationAccountBase schema
   - Centralized payment tracking functionality

5. **Maintainable Testing Approach**:
   - Clear test boundaries for each layer
   - Comprehensive validation test cases
   - Integration tests for obligation payment flows
   - Performance tests for date-based operations

6. **Tech Debt Prevention**:
   - Proper type annotations throughout the codebase
   - Comprehensive docstrings for all classes and methods
   - Clear error messages for validation failures
   - Consistent naming conventions across all components

## Performance and Resource Considerations

Performance impact has been carefully analyzed and optimized:

- **Single Obligation Retrieval**: < 10ms (direct ID lookup with polymorphic loading)
- **Obligation Account List**: < 50ms for typical users (10-20 obligations)
- **Upcoming Bills Calculation**: < 100ms (requires filtering and date comparison)
- **Payment History Retrieval**: < 30ms (simple foreign key lookup)

The following optimization strategies will be employed:

1. **Optimized Date Queries**:
   - Index on next_due_date for efficient upcoming bill queries
   - Use date range queries with appropriate bounds
   - Pre-filter closed accounts for improved performance

2. **Payment History Pagination**:
   - Default limit on payment history queries
   - Implement cursor-based pagination for large payment histories
   - Index on payment_date for efficient sorting

3. **Caching Aggregations**:
   - Cache bill category summaries with short TTL
   - Cache monthly equivalent calculations
   - Cache due date calculations with appropriate invalidation

4. **Batch Processing**:
   - Implement batch payment recording for multiple bills
   - Use transactions for payment recording and due date updates
   - Optimize arrears calculations with batch updates

## Development Considerations

1. **Implementation Effort**:
   - Estimated at 2-3 weeks of development time
   - Primary focus on backend implementation
   - Additional 1-2 weeks for frontend integration

2. **Required Skills**:
   - SQLAlchemy for polymorphic model implementation
   - Pydantic V2 for schema development
   - FastAPI for API endpoints
   - React/Redux for frontend integration

3. **Implementation Phases**:
   - Phase 1: Base ObligationAccount and core types (Utility, Subscription)
   - Phase 2: Specialized types (Insurance, Tax, Support Payment)
   - Phase 3: Payment tracking and history
   - Phase 4: Integration with cashflow and budgeting

4. **Testing Requirements**:
   - Unit tests for new models and schemas
   - Repository tests for data access patterns
   - Service tests for business logic
   - API integration tests for endpoints
   - Performance tests for date-based operations

5. **Documentation Requirements**:
   - API documentation with examples
   - Usage guides for obligation management
   - Database migration documentation
   - Service integration documentation

## Security and Compliance Considerations

1. **Data Privacy**:
   - Sensitive information in subscription and support payments requires proper handling
   - Personal identifiers in insurance policies need protection
   - Payment confirmation numbers should be encrypted at rest

2. **Access Control**:
   - User-based isolation for all obligation data
   - Proper authorization checks on all API endpoints
   - Verification of account ownership before operations

3. **Legal Requirements**:
   - Special handling for support payment arrears to comply with legal requirements
   - Proper tracking of tax obligations for audit purposes
   - Support for region-specific tax categories and rules

4. **Input Validation**:
   - Thorough validation of all obligation data at API boundaries
   - Prevention of cross-account access
   - Validation of payment amounts and dates

## Timeline

1. **Phase 1: Core Implementation (2 weeks)**
   - Base ObligationAccount model and schema
   - Utility and Subscription account types
   - Basic repository and service functionality
   - Core API endpoints

2. **Phase 2: Specialized Types (1 week)**
   - Insurance account implementation
   - Tax account implementation
   - Support payment account implementation

3. **Phase 3: Payment Tracking (1 week)**
   - Payment history model and schema
   - Payment recording and retrieval
   - Due date calculation functionality

4. **Phase 4: Integration (1-2 weeks)**
   - Cashflow analysis integration
   - Budget category integration
   - Frontend implementation
   - Documentation and testing

## Monitoring & Success Metrics

1. **Usage Metrics**:
   - Number of obligation accounts created by type
   - Frequency of payment recording
   - User engagement with upcoming bills view
   - Utilization of different obligation types

2. **Performance Metrics**:
   - API response times for obligation operations
   - Query performance for date-based operations
   - Cache hit rates for bill aggregations
   - Payment recording transaction times

3. **Business Metrics**:
   - Reduction in missed payments by users
   - Improvements in financial forecasting accuracy
   - User satisfaction with bill management features
   - Increased usage of payment tracking features

4. **Success Criteria**:
   - At least 80% of users create 5+ obligation accounts
   - Average user records 90% of payments on time
   - Query performance stays within target ranges
   - Positive user feedback on bill management features

## Team Impact

1. **Development Team**:
   - Backend developers will implement models, schemas, and services
   - Frontend developers will create obligation-specific UIs
   - QA team will develop comprehensive test cases

2. **Operations Team**:
   - Database migration coordination
   - Performance monitoring setup
   - Cache configuration and tuning

3. **User Experience Team**:
   - Design of obligation-specific form fields
   - Creation of obligation dashboards
   - Payment recording interface design

4. **Training Requirements**:
   - Documentation for customer support
   - User guides for obligation management
   - Video tutorials for payment recording

## Related Documents

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-020: Loan Account Types Expansion](/code/debtonator/docs/adr/backend/020-loan-account-types-expansion.md)
- [ADR-021: Investment Account Types Expansion](/code/debtonator/docs/adr/backend/021-investment-account-types-expansion.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)

## Notes

- The decision to use a separate ObligationPayment model rather than reusing a general Payment model was made to allow for obligation-specific payment attributes and validation.
- Consideration was given to combining all obligation types into a single table with a type discriminator, but the specialized fields for each type made separate tables more maintainable.
- Future enhancements could include integration with notification systems for payment reminders and overdue alerts.
- The current design accommodates potential future expansion to additional obligation types without schema changes.

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-04-20 | 1.0 | Debtonator Team | Initial version |
