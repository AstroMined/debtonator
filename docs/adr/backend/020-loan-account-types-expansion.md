# ADR-020: Loan Account Types Expansion

## Status

Proposed

## Context

Following the foundation established in ADR-016 (Account Type Expansion) and building upon the banking account types from ADR-019, we need to implement loan-specific account types to provide users with a comprehensive view of their financial obligations. Loans represent a significant portion of many users' financial lives, and proper tracking is essential for accurate financial planning.

Current limitations in our account system include:

1. Incomplete representation of various loan types such as personal loans, auto loans, mortgages, and student loans
2. Inability to track loan-specific attributes like amortization schedules, interest calculations, and payoff forecasting
3. Lack of specialized validation rules for different loan account types
4. Missing support for features like early payoff calculations and payment allocation strategies

These limitations prevent users from effectively managing their loans within Debtonator and limit our ability to provide meaningful insights for debt reduction strategies.

## Decision

We will implement the following loan account types as part of the polymorphic inheritance structure defined in ADR-016:

1. **Personal Loan Account**: For unsecured personal loans from banks, credit unions, or online lenders
2. **Auto Loan Account**: For vehicle financing with specific vehicle information
3. **Mortgage Account**: For home loans with property information and escrow tracking
4. **Student Loan Account**: For education loans with specialized repayment and forgiveness options

Each account type will have specialized attributes and business logic to accurately represent its unique characteristics while supporting Debtonator's core debt management features.

## Technical Details

### Type-Specific Models

We will implement the following SQLAlchemy models for loan account types:

#### Base Loan Account

To avoid duplication of common loan attributes, we'll create a base loan class that other loan types will inherit from:

```python
class LoanAccount(Account):
    """Base class for all loan account types"""
    __tablename__ = "loan_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    original_loan_amount = Column(Numeric(12, 4), nullable=False)
    interest_rate = Column(Numeric(6, 4), nullable=False)
    term_months = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    payment_amount = Column(Numeric(12, 4), nullable=False)
    payment_due_day = Column(Integer, nullable=False)  # Day of month (1-31)
    remaining_term = Column(Integer, nullable=True)  # Calculated or explicitly set
    prepayment_penalty = Column(Boolean, default=False, nullable=False)
    loan_status = Column(String, default="active", nullable=False)  # active, paid_off, defaulted, etc.
    
    __mapper_args__ = {
        "polymorphic_identity": "loan",
    }
```

#### Personal Loan Account

```python
class PersonalLoanAccount(LoanAccount):
    """Personal unsecured loans"""
    __tablename__ = "personal_loan_accounts"
    
    id = Column(Integer, ForeignKey("loan_accounts.id"), primary_key=True)
    purpose = Column(String, nullable=True)  # Debt consolidation, home improvement, etc.
    is_secured = Column(Boolean, default=False, nullable=False)
    collateral_description = Column(String, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "personal_loan",
    }
```

#### Auto Loan Account

```python
class AutoLoanAccount(LoanAccount):
    """Auto loans for vehicle financing"""
    __tablename__ = "auto_loan_accounts"
    
    id = Column(Integer, ForeignKey("loan_accounts.id"), primary_key=True)
    vehicle_make = Column(String, nullable=False)
    vehicle_model = Column(String, nullable=False)
    vehicle_year = Column(Integer, nullable=False)
    vehicle_vin = Column(String, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "auto_loan",
    }
```

#### Mortgage Account

```python
class MortgageAccount(LoanAccount):
    """Home mortgage loans"""
    __tablename__ = "mortgage_accounts"
    
    id = Column(Integer, ForeignKey("loan_accounts.id"), primary_key=True)
    property_address = Column(String, nullable=False)
    property_type = Column(String, nullable=False)  # Single family, condo, etc.
    is_primary_residence = Column(Boolean, default=True, nullable=False)
    escrow_amount = Column(Numeric(12, 4), nullable=True)
    property_tax_annual = Column(Numeric(12, 4), nullable=True)
    insurance_annual = Column(Numeric(12, 4), nullable=True)
    mortgage_type = Column(String, nullable=False)  # Fixed, ARM, etc.
    interest_only_period = Column(Integer, nullable=True)  # Months of interest-only payments
    adjustment_period = Column(Integer, nullable=True)  # For ARMs, months between rate adjustments
    rate_cap = Column(Numeric(6, 4), nullable=True)  # For ARMs, maximum interest rate
    
    __mapper_args__ = {
        "polymorphic_identity": "mortgage",
    }
```

#### Student Loan Account

```python
class StudentLoanAccount(LoanAccount):
    """Education loans with specialized options"""
    __tablename__ = "student_loan_accounts"
    
    id = Column(Integer, ForeignKey("loan_accounts.id"), primary_key=True)
    loan_program = Column(String, nullable=False)  # Federal Direct, Private, etc.
    is_subsidized = Column(Boolean, default=False, nullable=False)
    deferment_status = Column(String, nullable=True)  # None, in-school, economic hardship, etc.
    repayment_plan = Column(String, nullable=True)  # Standard, income-based, etc.
    forgiveness_program = Column(String, nullable=True)  # PSLF, Teacher Forgiveness, etc.
    forgiveness_progress_months = Column(Integer, nullable=True)
    education_institution = Column(String, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "student_loan",
    }
```

### Pydantic Schema Implementation

Following the pattern established in ADR-016 and ADR-019, we will create Pydantic schemas for each loan account type:

#### Base Loan Schema

```python
class LoanAccountBase(AccountBase):
    """Base schema for all loan accounts"""
    original_loan_amount: MoneyDecimal
    interest_rate: PercentageDecimal
    term_months: int
    start_date: datetime
    payment_amount: MoneyDecimal
    payment_due_day: int
    prepayment_penalty: bool = False
    loan_status: str = "active"
    
    @field_validator("payment_due_day")
    @classmethod
    def validate_due_day(cls, v):
        if v < 1 or v > 31:
            raise ValueError("Payment due day must be between 1 and 31")
        return v
    
    @field_validator("interest_rate")
    @classmethod
    def validate_interest_rate(cls, v):
        if v < 0:
            raise ValueError("Interest rate cannot be negative")
        return v
    
    @field_validator("term_months")
    @classmethod
    def validate_term(cls, v):
        if v <= 0:
            raise ValueError("Loan term must be positive")
        return v

class LoanAccountCreate(LoanAccountBase, AccountCreate):
    """Base create schema for loan accounts"""
    pass

class LoanAccountResponse(LoanAccountBase, AccountResponse):
    """Base response schema for loan accounts"""
    remaining_term: Optional[int] = None
```

#### Type-Specific Schemas

For each loan type, we'll create corresponding Create and Response schemas. Here's an example for the Mortgage account type:

```python
class MortgageAccountCreate(LoanAccountCreate):
    """Create schema for mortgage accounts"""
    account_type: Literal["mortgage"]
    property_address: str
    property_type: str
    is_primary_residence: bool = True
    escrow_amount: Optional[MoneyDecimal] = None
    property_tax_annual: Optional[MoneyDecimal] = None
    insurance_annual: Optional[MoneyDecimal] = None
    mortgage_type: str
    interest_only_period: Optional[int] = None
    adjustment_period: Optional[int] = None
    rate_cap: Optional[PercentageDecimal] = None
    
    @field_validator("mortgage_type")
    @classmethod
    def validate_mortgage_type(cls, v):
        allowed_types = ["fixed", "arm", "balloon", "interest_only", "reverse"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Mortgage type must be one of: {', '.join(allowed_types)}")
        return v.lower()

class MortgageAccountResponse(LoanAccountResponse):
    """Response schema for mortgage accounts"""
    account_type: Literal["mortgage"]
    property_address: str
    property_type: str
    is_primary_residence: bool
    escrow_amount: Optional[MoneyDecimal] = None
    property_tax_annual: Optional[MoneyDecimal] = None
    insurance_annual: Optional[MoneyDecimal] = None
    mortgage_type: str
    interest_only_period: Optional[int] = None
    adjustment_period: Optional[int] = None
    rate_cap: Optional[PercentageDecimal] = None
```

Similar schemas will be created for other loan types with appropriate fields and validations.

### Discriminated Union for API

```python
LoanAccountCreateUnion = Annotated[
    Union[
        PersonalLoanAccountCreate,
        AutoLoanAccountCreate,
        MortgageAccountCreate,
        StudentLoanAccountCreate,
    ],
    Field(discriminator="account_type")
]

LoanAccountResponseUnion = Annotated[
    Union[
        PersonalLoanAccountResponse,
        AutoLoanAccountResponse,
        MortgageAccountResponse,
        StudentLoanAccountResponse,
    ],
    Field(discriminator="account_type")
]
```

### Loan Amortization Service

To support loan-specific calculations, we'll implement a LoanAmortizationService:

```python
class LoanAmortizationService:
    """Service for loan amortization calculations"""
    
    @staticmethod
    def calculate_payment(principal: Decimal, annual_rate: Decimal, term_months: int) -> Decimal:
        """Calculate monthly payment amount for a loan"""
        if annual_rate == 0:
            return principal / term_months
        
        monthly_rate = annual_rate / 12 / 100
        x = (1 + monthly_rate) ** term_months
        return principal * (monthly_rate * x) / (x - 1)
    
    @staticmethod
    def generate_amortization_schedule(
        principal: Decimal,
        annual_rate: Decimal,
        term_months: int,
        payment: Optional[Decimal] = None,
        extra_payment: Decimal = Decimal("0")
    ) -> List[Dict]:
        """Generate complete amortization schedule for a loan"""
        if payment is None:
            payment = LoanAmortizationService.calculate_payment(principal, annual_rate, term_months)
        
        total_payment = payment + extra_payment
        monthly_rate = annual_rate / 12 / 100
        
        schedule = []
        balance = principal
        month = 1
        
        while balance > 0 and month <= term_months + 120:  # Add buffer to prevent infinite loops
            interest_payment = balance * monthly_rate
            principal_payment = min(total_payment - interest_payment, balance)
            
            # Handle final payment
            if balance < total_payment:
                principal_payment = balance
                interest_payment = balance * monthly_rate
            
            balance = balance - principal_payment
            
            schedule.append({
                "month": month,
                "payment": principal_payment + interest_payment,
                "principal": principal_payment,
                "interest": interest_payment,
                "extra_payment": extra_payment if balance > 0 else Decimal("0"),
                "balance": balance
            })
            
            # If loan is paid off, stop
            if balance <= 0:
                break
                
            month += 1
        
        return schedule
    
    @staticmethod
    def calculate_payoff_date(
        current_balance: Decimal,
        annual_rate: Decimal,
        monthly_payment: Decimal,
        extra_payment: Decimal = Decimal("0")
    ) -> datetime:
        """Calculate payoff date given current balance and payment information"""
        if monthly_payment <= 0:
            raise ValueError("Monthly payment must be positive")
            
        total_payment = monthly_payment + extra_payment
        monthly_rate = annual_rate / 12 / 100
        
        # If payment doesn't cover interest, loan will never be paid off
        if total_payment <= current_balance * monthly_rate:
            raise ValueError("Payment too small to pay off loan")
        
        months_to_payoff = 0
        balance = current_balance
        
        while balance > 0 and months_to_payoff < 1200:  # 100 years max to prevent infinite loops
            interest_payment = balance * monthly_rate
            principal_payment = min(total_payment - interest_payment, balance)
            balance -= principal_payment
            months_to_payoff += 1
        
        # Calculate date by adding months to today
        return datetime_utils.add_months(datetime_utils.utc_now(), months_to_payoff)
    
    @staticmethod
    def calculate_loan_stats(loan_account: LoanAccount) -> Dict:
        """Calculate comprehensive loan statistics for a loan account"""
        # Convert to right types for calculations
        current_balance = loan_account.current_balance
        original_amount = loan_account.original_loan_amount
        interest_rate = loan_account.interest_rate
        payment = loan_account.payment_amount
        term_months = loan_account.term_months
        
        # Calculate standard stats
        monthly_rate = interest_rate / 12 / 100
        total_payments_made = term_months - (loan_account.remaining_term or 0)
        principal_paid = original_amount - current_balance
        
        # Generate amortization schedule for future payments
        schedule = LoanAmortizationService.generate_amortization_schedule(
            principal=current_balance,
            annual_rate=interest_rate,
            term_months=loan_account.remaining_term or term_months,
            payment=payment
        )
        
        # Calculate total interest over life of loan
        total_interest_paid = sum(payment.interest for payment in schedule)
        
        # Calculate payoff date
        payoff_date = LoanAmortizationService.calculate_payoff_date(
            current_balance=current_balance,
            annual_rate=interest_rate,
            monthly_payment=payment
        )
        
        return {
            "original_amount": original_amount,
            "current_balance": current_balance,
            "principal_paid": principal_paid,
            "interest_paid_to_date": None,  # Would require payment history
            "total_interest": total_interest_paid,
            "monthly_payment": payment,
            "total_payments_made": total_payments_made,
            "remaining_payments": len(schedule),
            "payoff_date": payoff_date,
            "percent_paid": (principal_paid / original_amount * 100) if original_amount > 0 else 0
        }
```

### Enhancements to AccountService

We'll extend the AccountService with loan-specific methods:

```python
class AccountService:
    # ... existing methods from ADR-016 and ADR-019 ...
    
    def get_loan_accounts(self, user_id: int) -> List[LoanAccount]:
        """Get all loan accounts for a user"""
        return self.account_repository.get_by_user_and_types(
            user_id, 
            ["personal_loan", "auto_loan", "mortgage", "student_loan"]
        )
    
    def calculate_loan_payoff_with_extra_payment(
        self, loan_id: int, extra_payment: Decimal
    ) -> Dict:
        """Calculate the impact of making extra payments on a loan"""
        loan = self.get_account(loan_id)
        if not loan or not isinstance(loan, LoanAccount):
            raise ValueError("Account is not a loan account")
            
        # Calculate standard payoff stats
        standard_schedule = LoanAmortizationService.generate_amortization_schedule(
            principal=loan.current_balance,
            annual_rate=loan.interest_rate,
            term_months=loan.remaining_term or loan.term_months,
            payment=loan.payment_amount
        )
        
        standard_payoff = {
            "total_payments": len(standard_schedule),
            "total_interest": sum(payment["interest"] for payment in standard_schedule),
            "payoff_date": datetime_utils.add_months(
                datetime_utils.utc_now(), 
                len(standard_schedule)
            )
        }
        
        # Calculate accelerated payoff stats
        accelerated_schedule = LoanAmortizationService.generate_amortization_schedule(
            principal=loan.current_balance,
            annual_rate=loan.interest_rate,
            term_months=loan.remaining_term or loan.term_months,
            payment=loan.payment_amount,
            extra_payment=extra_payment
        )
        
        accelerated_payoff = {
            "total_payments": len(accelerated_schedule),
            "total_interest": sum(payment["interest"] for payment in accelerated_schedule),
            "payoff_date": datetime_utils.add_months(
                datetime_utils.utc_now(), 
                len(accelerated_schedule)
            )
        }
        
        # Calculate savings
        months_saved = standard_payoff["total_payments"] - accelerated_payoff["total_payments"]
        interest_saved = standard_payoff["total_interest"] - accelerated_payoff["total_interest"]
        
        return {
            "standard_payoff": standard_payoff,
            "accelerated_payoff": accelerated_payoff,
            "months_saved": months_saved,
            "interest_saved": interest_saved,
            "extra_payment": extra_payment,
            "total_extra_payments": extra_payment * accelerated_payoff["total_payments"]
        }
    
    def get_debt_reduction_strategies(self, user_id: int) -> Dict:
        """Calculate debt reduction strategies (snowball and avalanche)"""
        loan_accounts = self.get_loan_accounts(user_id)
        credit_accounts = self.account_repository.get_by_user_and_type(user_id, "credit")
        
        # Combine all debt accounts for calculation
        debt_accounts = []
        
        for loan in loan_accounts:
            if loan.is_closed:
                continue
                
            debt_accounts.append({
                "id": loan.id,
                "name": loan.name,
                "type": loan.account_type,
                "balance": loan.current_balance,
                "interest_rate": loan.interest_rate,
                "minimum_payment": loan.payment_amount
            })
        
        for credit in credit_accounts:
            if credit.is_closed:
                continue
                
            debt_accounts.append({
                "id": credit.id,
                "name": credit.name,
                "type": "credit",
                "balance": credit.current_balance,
                "interest_rate": credit.apr or Decimal("0"),
                "minimum_payment": credit.minimum_payment or Decimal("0")
            })
        
        # Sort by balance for snowball method (smallest balance first)
        snowball_order = sorted(debt_accounts, key=lambda x: x["balance"])
        
        # Sort by interest rate for avalanche method (highest rate first)
        avalanche_order = sorted(debt_accounts, key=lambda x: x["interest_rate"], reverse=True)
        
        return {
            "total_debt": sum(account["balance"] for account in debt_accounts),
            "accounts_count": len(debt_accounts),
            "snowball_strategy": snowball_order,
            "avalanche_strategy": avalanche_order,
            "minimum_monthly_payment": sum(account["minimum_payment"] for account in debt_accounts)
        }
```

### API Layer Implementation

We will implement the following endpoints for loan account management:

```python
@router.post("/accounts/loans", response_model=LoanAccountResponseUnion)
def create_loan_account(
    account_data: LoanAccountCreateUnion,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new loan account."""
    data_dict = account_data.model_dump()
    data_dict["user_id"] = current_user.id
    return account_service.create_account(data_dict)

@router.get("/accounts/loans", response_model=List[LoanAccountResponseUnion])
def get_loan_accounts(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get all loan accounts for the current user."""
    return account_service.get_loan_accounts(current_user.id)

@router.get("/accounts/loans/{loan_id}/amortization", response_model=List[AmortizationScheduleItem])
def get_loan_amortization(
    loan_id: int,
    extra_payment: Decimal = Query(0, description="Optional extra payment per month"),
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get amortization schedule for a loan."""
    loan = account_service.get_account(loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    if not isinstance(loan, LoanAccount):
        raise HTTPException(status_code=400, detail="Account is not a loan account")
    
    schedule = LoanAmortizationService.generate_amortization_schedule(
        principal=loan.current_balance,
        annual_rate=loan.interest_rate,
        term_months=loan.remaining_term or loan.term_months,
        payment=loan.payment_amount,
        extra_payment=extra_payment
    )
    
    return schedule

@router.get("/accounts/loans/{loan_id}/extra-payment-impact", response_model=ExtraPaymentImpactResponse)
def calculate_extra_payment_impact(
    loan_id: int,
    extra_payment: Decimal = Query(..., description="Extra payment per month"),
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Calculate the impact of extra payments on a loan."""
    loan = account_service.get_account(loan_id)
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    if not isinstance(loan, LoanAccount):
        raise HTTPException(status_code=400, detail="Account is not a loan account")
    
    return account_service.calculate_loan_payoff_with_extra_payment(loan_id, extra_payment)

@router.get("/accounts/debt-reduction-strategies", response_model=DebtReductionStrategiesResponse)
def get_debt_reduction_strategies(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get debt reduction strategies (snowball and avalanche) for all debt accounts."""
    return account_service.get_debt_reduction_strategies(current_user.id)
```

### Account Type Registry Updates

We'll update the AccountTypeRegistry to include the new loan account types:

```python
# During application initialization
account_type_registry = AccountTypeRegistry()

# Register loan account types
account_type_registry.register(
    account_type_id="personal_loan",
    model_class=PersonalLoanAccount,
    schema_class=PersonalLoanAccountCreate,
    name="Personal Loan",
    description="Unsecured personal loan from a bank or lender",
    category="Loans"
)

account_type_registry.register(
    account_type_id="auto_loan",
    model_class=AutoLoanAccount,
    schema_class=AutoLoanAccountCreate,
    name="Auto Loan",
    description="Vehicle financing loan with vehicle as collateral",
    category="Loans"
)

account_type_registry.register(
    account_type_id="mortgage",
    model_class=MortgageAccount,
    schema_class=MortgageAccountCreate,
    name="Mortgage",
    description="Home loan with property as collateral",
    category="Loans"
)

account_type_registry.register(
    account_type_id="student_loan",
    model_class=StudentLoanAccount,
    schema_class=StudentLoanAccountCreate,
    name="Student Loan",
    description="Education loan with specialized repayment options",
    category="Loans"
)
```

## Consequences

### Positive

1. **Comprehensive Debt Management**: Users can track all types of loans in one place, with dedicated fields for each loan type's unique attributes.

2. **Advanced Debt Analysis**: The amortization service enables powerful features like payoff forecasting, acceleration strategies, and what-if scenarios.

3. **Debt Reduction Strategies**: Built-in support for debt snowball and avalanche methods helps users strategically reduce debt.

4. **Better Financial Planning**: More detailed loan tracking enables more accurate long-term financial forecasting.

5. **Support for Specialized Loan Types**: Student loan tracking with forgiveness options helps users manage complex education debt.

### Negative

1. **Increased Schema Complexity**: The inheritance hierarchy is deeper with the addition of a base LoanAccount class between Account and specific loan types.

2. **Calculation Overhead**: Amortization and loan payoff calculations may be computationally intensive for complex scenarios.

3. **Maintenance Requirements**: Each loan type requires ongoing maintenance to stay current with industry practices and regulations.

### Neutral

1. **Migration Effort**: New tables need to be created for each loan type as part of the migration.

2. **UI Expansion Needed**: Frontend components need significant expansion to handle loan-specific displays and tools.

## Performance Impact

- **Single Loan Retrieval**: < 10ms (direct ID lookup with polymorphic loading)
- **Loan Account List**: < 50ms for typical users (2-5 loans)
- **Amortization Calculation**: < 100ms for standard loans, may increase with very long terms
- **Debt Reduction Strategy Calculation**: < 50ms for typical users with 3-7 debt accounts

### Optimization Strategies

To maintain performance with the complex loan calculations:

1. **Caching Amortization Results**:
   - Cache amortization schedules with a TTL of 24 hours
   - Invalidate cache when loan details are updated
   - Use a combination of loan_id and extra_payment as cache key

2. **Pagination for Long Schedules**:
   - Implement pagination for amortization schedules
   - Default to first 12 months with option to load more
   - Provide summary statistics without loading full schedule

3. **Batch Processing for Debt Strategy**:
   - Calculate debt strategies in background task if many accounts
   - Cache results for quick retrieval
   - Update on schedule or when debt accounts change

4. **Lazy Loading for Details**:
   - Load basic loan information first
   - Fetch detailed amortization only when requested
   - Use expandable UI components to show/hide details on demand

## Integration with Existing Features

### Debt Management Integration

The loan account types will integrate with Debtonator's core debt management features:

1. **Debt Snowball/Avalanche Integration**:
   - Loan accounts will be included in debt reduction strategies
   - Payoff ordering will consider interest rates and balances
   - Progress tracking will update as payments are made

2. **Cashflow Analysis Integration**:
   - Loan payments will be incorporated into cashflow forecasts
   - Due dates based on payment_due_day will be used for forecasting
   - Payment amounts will be factored into required funds calculations

3. **Bill Splitting Support**:
   - Loan payments can be split across multiple accounts if needed
   - Special validation ensures loan-specific payments are properly handled
   - UI will clearly indicate loan payments vs. other bill types

4. **Financial Projection Integration**:
   - Loan payoff dates will be incorporated into long-term financial projections
   - Interest savings from payment strategies will be highlighted
   - Impact of loans on net worth will be calculated and displayed

### User Experience Enhancements

The loan account implementation will include several UX improvements:

1. **Loan Dashboard**:
   - Visual payoff progress indicators for each loan
   - Time-to-payoff countdowns
   - Interest paid vs. principal paid visualizations
   - Color coding based on loan status (on track, at risk, etc.)

2. **What-If Scenarios**:
   - Interactive sliders for extra payment amounts
   - Real-time updates to payoff date and interest saved
   - Comparison views for different payment strategies
   - Option to save scenarios for future reference

3. **Educational Content**:
   - Contextual explanations of loan terms and concepts
   - Tips for accelerating loan payoff
   - Pros and cons of different debt reduction strategies
   - Guidance for refinancing consideration

## Compliance Considerations

The loan account implementation must adhere to several compliance requirements:

1. **Interest Calculation Accuracy**:
   - Calculations must follow standard financial formulas
   - Results must be validated against known test cases
   - Documentation must explain calculation methodology

2. **Terminology Standardization**:
   - Financial terms must be used consistently
   - Clear definitions must be provided for specialized terms
   - Complex concepts should be explained in plain language

3. **Privacy Protections**:
   - Loan account details should be treated with highest security
   - PII in loan documents should not be stored unnecessarily
   - Export/delete functionality must include loan data

4. **Disclaimer Requirements**:
   - Clear disclaimers that calculations are estimates only
   - Statement that Debtonator is not providing financial advice
   - Recommendation to consult financial professionals for major decisions

## Implementation Timeline

The loan account types will be implemented in three phases:

### Phase 1: Core Infrastructure (Week 1-2)
- Database model implementation
- Pydantic schema creation
- Basic repository and service methods
- Initial API endpoints

### Phase 2: Calculation Engine (Week 3-4)
- Amortization schedule calculations
- Extra payment impact analysis
- Debt reduction strategy implementation
- Payoff date forecasting

### Phase 3: Integration & UI (Week 5-6)
- Integration with existing features
- User interface components
- Educational content
- Performance optimization

## Migration Considerations

As noted in ADR-016, we will implement this new structure with a fresh database initialization rather than migrating existing data. However, for production deployment, we will need:

1. **Data Migration Scripts**:
   - Convert existing generic loans to appropriate specific types
   - Calculate missing fields based on available data
   - Map relationships correctly (especially for bill splits)

2. **Backward Compatibility Layer**:
   - Temporary support for old endpoints during transition
   - Graceful error handling for requests using old formats
   - Documentation for API changes

3. **Feature Flag Control**:
   - Ability to enable/disable specific loan types
   - Gradual rollout of complex calculation features
   - A/B testing of different UI approaches

## Testing Strategy

Testing for loan account types will be comprehensive:

1. **Model Validation Tests**:
   - Verify inheritance hierarchy works correctly
   - Test polymorphic loading and saving
   - Ensure type-specific fields are properly validated

2. **Calculation Accuracy Tests**:
   - Test amortization calculations against known examples
   - Validate edge cases (zero interest, very short/long terms)
   - Test payment date logic across month boundaries

3. **Integration Tests**:
   - Verify loan accounts work with bill splitting
   - Test cashflow integration accuracy
   - Validate debt reduction strategy ordering

4. **Performance Tests**:
   - Benchmark amortization calculations
   - Test with large number of accounts
   - Verify caching strategies are effective

## Documentation Requirements

The loan account implementation will require the following documentation:

1. **Technical Documentation**:
   - Complete API specification for all endpoints
   - Database schema diagrams
   - Calculation methodologies with references

2. **User Documentation**:
   - Guides for setting up different loan types
   - Explanations of loan terms and concepts
   - Tutorials for using debt reduction features

3. **Developer Guides**:
   - Implementation examples for frontend integration
   - Test cases for loan calculations
   - Best practices for loan-related features

## References

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)

## Notes

### Student Loan Special Considerations

Student loans deserve special attention due to their unique characteristics:

1. **Repayment Plan Tracking**:
   The StudentLoanAccount includes fields for tracking specialized repayment plans like income-based repayment (IBR), Pay As You Earn (PAYE), and others. This is critical because the payment amount may change annually based on income recertification.

2. **Forgiveness Program Integration**:
   For borrowers pursuing forgiveness programs like Public Service Loan Forgiveness (PSLF), the system tracks qualifying payments and estimates forgiveness dates. This provides valuable long-term planning insights.

3. **Deferment and Forbearance Handling**:
   Student loans can enter various administrative statuses that affect payment requirements and interest accrual. The model captures these states and their implications for overall loan calculations.

4. **Subsidized vs. Unsubsidized Distinction**:
   The is_subsidized field allows the system to handle different interest rules, particularly for federal loans where interest may be covered by the government during certain periods.

### Mortgage Escrow Management

Mortgages with escrow accounts require special handling:

1. **Escrow Component Breakdown**:
   The mortgage model tracks both the loan payment and the escrow component separately, allowing for accurate representation of total monthly payment.

2. **Annual Escrow Analysis**:
   The system will support annual escrow recalculation based on property tax and insurance changes, with appropriate adjustment of monthly payment amounts.

3. **Escrow Shortage/Surplus Handling**:
   When escrow analysis results in shortages or surpluses, the system can track adjustment payments or refunds and their impact on monthly payment amounts.

## Updates

| Date | Revision | Author | Description |
|------|----------|--------|-------------|
| 2025-04-11 | 1.0 | Debtonator Team | Initial draft |