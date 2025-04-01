# ADR-019: Banking Account Types Expansion

## Status

Proposed

## Context

Following the foundational polymorphic account model established in ADR-016, we now need to implement specific account types to support modern financial platforms and services. The Banking category requires particular attention as it encompasses both traditional accounts and emerging financial products that blur traditional boundaries.

Current limitations in our account system include:

1. Limited support for modern financial products like Buy Now Pay Later (BNPL) and Earned Wage Access (EWA)
2. Inability to properly represent hybrid financial platforms like PayPal, Venmo, and Cash App
3. Inconsistent handling of account-specific attributes across different banking account types
4. Lack of specialized validation rules for different banking account types

These limitations prevent users from having a comprehensive view of their financial situation and limit Debtonator's ability to provide accurate financial insights and planning.

## Decision

We will implement the following banking account types as part of the polymorphic inheritance structure defined in ADR-016:

1. Traditional Banking Accounts:
   - Checking Account
   - Savings Account
   - Credit Account

2. Modern Financial Services:
   - Payment App Account (for PayPal, Venmo, Cash App, etc.)
   - Buy Now Pay Later (BNPL) Account
   - Earned Wage Access (EWA) Account

Each account type will have specialized attributes and business logic to accurately represent its unique characteristics while maintaining a consistent user experience.

## Technical Details

### International Banking Support

To accommodate international banking systems, our implementation will include:

1. **Flexible Account Identification**:
   - Support for IBAN (International Bank Account Number) used in Europe and many other countries
   - Support for SWIFT/BIC codes for international transfers
   - Support for sort codes used in the UK and Ireland
   - Support for branch codes used in various countries including Canada, India, and Japan

2. **Currency Handling**:
   - Store account currency as a separate field with ISO 4217 currency code (e.g., USD, EUR, GBP)
   - Support for display of amounts in the account's native currency
   - Integration with currency conversion for multi-currency reporting

3. **Regional Account Types**:
   - Support for region-specific banking features like Canadian TFSAs, UK ISAs, etc.
   - Account subtypes can be extended with regional variations

4. **Naming Conventions**:
   - Labels adaptable to regional terminology (e.g., "checking" in US vs. "current" in UK)
   - Flexible display options for account numbers based on regional formats

This international support requires minimal changes to the underlying polymorphic architecture, but enhances the model's ability to represent various banking systems accurately.

### Type-Specific Models

We will implement the following SQLAlchemy models for banking account types:

#### Checking Account

```python
class CheckingAccount(Account):
    __tablename__ = "checking_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    routing_number = Column(String, nullable=True)
    has_overdraft_protection = Column(Boolean, default=False, nullable=False)
    overdraft_limit = Column(Numeric(12, 4), nullable=True)
    monthly_fee = Column(Numeric(12, 4), nullable=True)
    interest_rate = Column(Numeric(6, 4), nullable=True)
    # International banking support
    iban = Column(String, nullable=True)  # International Bank Account Number
    swift_bic = Column(String, nullable=True)  # SWIFT/BIC code for international transfers
    sort_code = Column(String, nullable=True)  # Used in UK and other countries
    branch_code = Column(String, nullable=True)  # Used in various countries
    account_format = Column(String, default="local", nullable=False)  # local, iban, etc.
    
    __mapper_args__ = {
        "polymorphic_identity": "checking"
    }
```

#### Savings Account

```python
class SavingsAccount(Account):
    __tablename__ = "savings_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    interest_rate = Column(Numeric(6, 4), nullable=True)
    compound_frequency = Column(String, nullable=True)  # monthly, quarterly, etc.
    interest_earned_ytd = Column(Numeric(12, 4), nullable=True)
    withdrawal_limit = Column(Integer, nullable=True)
    minimum_balance = Column(Numeric(12, 4), nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "savings"
    }
```

#### Credit Account

```python
class CreditAccount(Account):
    __tablename__ = "credit_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    credit_limit = Column(Numeric(12, 4), nullable=False)
    statement_balance = Column(Numeric(12, 4), nullable=True)
    statement_due_date = Column(DateTime(timezone=True), nullable=True)
    minimum_payment = Column(Numeric(12, 4), nullable=True)
    apr = Column(Numeric(6, 4), nullable=True)
    annual_fee = Column(Numeric(12, 4), nullable=True)
    rewards_program = Column(String, nullable=True)
    autopay_status = Column(String, nullable=True)  # none, minimum, full_balance, fixed_amount
    last_statement_date = Column(DateTime(timezone=True), nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "credit"
    }
```

#### Payment App Account

```python
class PaymentAppAccount(Account):
    __tablename__ = "payment_app_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    platform = Column(String, nullable=False)  # PayPal, Venmo, Cash App, etc.
    has_debit_card = Column(Boolean, default=False, nullable=False)
    card_last_four = Column(String, nullable=True)
    linked_account_ids = Column(String, nullable=True)  # Comma-separated list of related account IDs
    supports_direct_deposit = Column(Boolean, default=False, nullable=False)
    supports_crypto = Column(Boolean, default=False, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "payment_app"
    }
```

#### BNPL Account

```python
class BNPLAccount(Account):
    __tablename__ = "bnpl_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    original_amount = Column(Numeric(12, 4), nullable=False)
    installment_count = Column(Integer, nullable=False)
    installments_paid = Column(Integer, nullable=False, default=0)
    installment_amount = Column(Numeric(12, 4), nullable=False)
    payment_frequency = Column(String, nullable=False)  # biweekly, monthly, etc.
    next_payment_date = Column(DateTime(timezone=True), nullable=True)
    promotion_info = Column(String, nullable=True)
    late_fee = Column(Numeric(12, 4), nullable=True)
    bnpl_provider = Column(String, nullable=False)  # Affirm, Klarna, Afterpay, etc.
    
    __mapper_args__ = {
        "polymorphic_identity": "bnpl"
    }
```

#### EWA Account

```python
class EWAAccount(Account):
    __tablename__ = "ewa_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    provider = Column(String, nullable=False)  # Payactiv, DailyPay, etc.
    max_advance_percentage = Column(Numeric(6, 4), nullable=True)  # Often limited to 50%
    per_transaction_fee = Column(Numeric(12, 4), nullable=True)
    pay_period_start = Column(DateTime(timezone=True), nullable=True)
    pay_period_end = Column(DateTime(timezone=True), nullable=True)
    next_payday = Column(DateTime(timezone=True), nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "ewa"
    }
```

### Pydantic Schema Implementation

For each account type, we will implement the following schema classes:

#### Base Schema

We're extending the base schemas from ADR-016:

```python
class AccountBase(BaseModel):
    account_number: Optional[str] = None
    name: str
    institution: Optional[str] = None
    url: Optional[str] = None
    logo_path: Optional[str] = None
    current_balance: MoneyDecimal
    
    class Config:
        extra = "forbid"

class AccountCreate(AccountBase):
    account_type: str
    
    @field_validator("account_type")
    @classmethod
    def validate_account_type(cls, v):
        allowed_types = account_type_registry.get_all_types()
        allowed_ids = [t["id"] for t in allowed_types]
        if v not in allowed_ids:
            raise ValueError(f"Invalid account type. Must be one of: {', '.join(allowed_ids)}")
        return v

class AccountResponse(AccountBase):
    id: int
    account_type: str
    available_balance: Optional[MoneyDecimal] = None
    created_at: datetime
    updated_at: datetime
    is_closed: bool = False
    
    class Config:
        orm_mode = True
```

#### Type-Specific Schemas

Examples of type-specific schemas (Create and Response) for each banking account type:

```python
# Checking Account
class CheckingAccountCreate(AccountCreate):
    account_type: Literal["checking"]
    routing_number: Optional[str] = None
    has_overdraft_protection: bool = False
    overdraft_limit: Optional[MoneyDecimal] = None
    monthly_fee: Optional[MoneyDecimal] = None
    interest_rate: Optional[PercentageDecimal] = None

    @field_validator("overdraft_limit")
    @classmethod
    def validate_overdraft_limit(cls, v, values):
        if values.data.get("has_overdraft_protection") and v is None:
            raise ValueError("Overdraft limit is required when overdraft protection is enabled")
        return v

class CheckingAccountResponse(AccountResponse):
    account_type: Literal["checking"]
    routing_number: Optional[str] = None
    has_overdraft_protection: bool = False
    overdraft_limit: Optional[MoneyDecimal] = None
    monthly_fee: Optional[MoneyDecimal] = None
    interest_rate: Optional[PercentageDecimal] = None

# Similar patterns for other account types...
```

### Discriminated Union for API

```python
BankingAccountCreateUnion = Annotated[
    Union[
        CheckingAccountCreate,
        SavingsAccountCreate,
        CreditAccountCreate,
        PaymentAppAccountCreate,
        BNPLAccountCreate,
        EWAAccountCreate,
    ],
    Field(discriminator="account_type")
]

BankingAccountResponseUnion = Annotated[
    Union[
        CheckingAccountResponse,
        SavingsAccountResponse,
        CreditAccountResponse,
        PaymentAppAccountResponse,
        BNPLAccountResponse,
        EWAAccountResponse,
    ],
    Field(discriminator="account_type")
]
```

### Repository Layer Enhancements

We will extend the AccountRepository with banking-specific methods:

```python
class AccountRepository(BaseRepository):
    # ... existing methods from ADR-016 ...
    
    def get_checking_accounts_by_user(self, user_id: int) -> List[CheckingAccount]:
        """Get all checking accounts for a specific user."""
        return self.session.query(CheckingAccount).filter(
            CheckingAccount.user_id == user_id,
            CheckingAccount.is_closed == False
        ).all()
    
    def get_credit_accounts_with_upcoming_payments(
        self, user_id: int, days: int = 14
    ) -> List[CreditAccount]:
        """Get credit accounts with payments due in the next X days."""
        now = datetime_utils.utc_now()
        cutoff = datetime_utils.add_days(now, days)
        
        return self.session.query(CreditAccount).filter(
            CreditAccount.user_id == user_id,
            CreditAccount.is_closed == False,
            CreditAccount.statement_due_date <= cutoff,
            CreditAccount.statement_due_date >= now
        ).order_by(CreditAccount.statement_due_date).all()
    
    def get_bnpl_accounts_with_upcoming_payments(
        self, user_id: int, days: int = 14
    ) -> List[BNPLAccount]:
        """Get BNPL accounts with payments due in the next X days."""
        now = datetime_utils.utc_now()
        cutoff = datetime_utils.add_days(now, days)
        
        return self.session.query(BNPLAccount).filter(
            BNPLAccount.user_id == user_id,
            BNPLAccount.is_closed == False,
            BNPLAccount.next_payment_date <= cutoff,
            BNPLAccount.next_payment_date >= now
        ).order_by(BNPLAccount.next_payment_date).all()
    
    def get_connected_payment_app_accounts(
        self, account_id: int
    ) -> List[Account]:
        """Get all accounts connected to a payment app account."""
        payment_app = self.session.query(PaymentAppAccount).get(account_id)
        if not payment_app or not payment_app.linked_account_ids:
            return []
        
        linked_ids = [int(id_str) for id_str in payment_app.linked_account_ids.split(",")]
        return self.session.query(Account).filter(
            Account.id.in_(linked_ids)
        ).all()
```

### Service Layer Enhancements

```python
class AccountService:
    # ... existing methods from ADR-016 ...
    
    def get_upcoming_payments(self, user_id: int, days: int = 14) -> List[Dict]:
        """Get all upcoming payments for a user across account types."""
        upcoming_payments = []
        
        # Get credit account payments
        credit_accounts = self.account_repository.get_credit_accounts_with_upcoming_payments(
            user_id, days
        )
        for account in credit_accounts:
            upcoming_payments.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": "credit",
                "due_date": account.statement_due_date,
                "amount": account.minimum_payment or 0,
                "full_amount": account.statement_balance or 0,
                "payment_type": "minimum_payment"
            })
        
        # Get BNPL account payments
        bnpl_accounts = self.account_repository.get_bnpl_accounts_with_upcoming_payments(
            user_id, days
        )
        for account in bnpl_accounts:
            upcoming_payments.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": "bnpl",
                "due_date": account.next_payment_date,
                "amount": account.installment_amount,
                "payment_type": "installment"
            })
        
        # Sort by due date
        return sorted(upcoming_payments, key=lambda x: x["due_date"])
    
    def get_banking_overview(self, user_id: int) -> Dict:
        """Get an overview of banking accounts for a user."""
        accounts = self.get_user_accounts(user_id)
        
        checking_balance = sum(
            a.current_balance for a in accounts 
            if a.account_type == "checking" and not a.is_closed
        )
        savings_balance = sum(
            a.current_balance for a in accounts 
            if a.account_type == "savings" and not a.is_closed
        )
        credit_used = sum(
            a.current_balance for a in accounts 
            if a.account_type == "credit" and not a.is_closed
        )
        
        credit_accounts = [a for a in accounts if a.account_type == "credit" and not a.is_closed]
        credit_limit = sum(a.credit_limit for a in credit_accounts) if credit_accounts else 0
        
        payment_app_balance = sum(
            a.current_balance for a in accounts 
            if a.account_type == "payment_app" and not a.is_closed
        )
        
        bnpl_balance = sum(
            a.current_balance for a in accounts 
            if a.account_type == "bnpl" and not a.is_closed
        )
        
        ewa_balance = sum(
            a.current_balance for a in accounts 
            if a.account_type == "ewa" and not a.is_closed
        )
        
        return {
            "total_cash": checking_balance + savings_balance + payment_app_balance,
            "checking_balance": checking_balance,
            "savings_balance": savings_balance,
            "payment_app_balance": payment_app_balance,
            "credit_used": credit_used,
            "credit_limit": credit_limit,
            "credit_available": credit_limit - credit_used if credit_limit else 0,
            "credit_utilization": (credit_used / credit_limit * 100) if credit_limit else 0,
            "bnpl_balance": bnpl_balance,
            "ewa_balance": ewa_balance,
            "total_debt": credit_used + bnpl_balance + ewa_balance
        }
    
    def update_bnpl_status(self, account_id: int) -> Optional[BNPLAccount]:
        """Update BNPL account status including incrementing paid installments 
        if payment date has passed."""
        bnpl_account = self.get_account(account_id)
        if not bnpl_account or bnpl_account.account_type != "bnpl":
            return None
        
        now = datetime_utils.utc_now()
        
        # If next payment date has passed, increment installments paid
        if (bnpl_account.next_payment_date and 
            bnpl_account.next_payment_date < now and 
            bnpl_account.installments_paid < bnpl_account.installment_count):
            
            # Calculate new next payment date based on frequency
            if bnpl_account.payment_frequency == "biweekly":
                next_payment_date = datetime_utils.add_days(bnpl_account.next_payment_date, 14)
            elif bnpl_account.payment_frequency == "monthly":
                next_payment_date = datetime_utils.add_months(bnpl_account.next_payment_date, 1)
            else:
                # Default to biweekly if frequency not recognized
                next_payment_date = datetime_utils.add_days(bnpl_account.next_payment_date, 14)
            
            update_data = {
                "installments_paid": bnpl_account.installments_paid + 1,
                "next_payment_date": next_payment_date
            }
            
            # If all installments are now paid, mark as closed
            if bnpl_account.installments_paid + 1 >= bnpl_account.installment_count:
                update_data["is_closed"] = True
                update_data["current_balance"] = 0
            else:
                # Update current balance
                remaining_installments = bnpl_account.installment_count - (bnpl_account.installments_paid + 1)
                update_data["current_balance"] = bnpl_account.installment_amount * remaining_installments
            
            return self.update_account(account_id, update_data)
        
        return bnpl_account
```

### Business Rules and Validation

Each account type will have specific business rules implemented at the service layer:

#### Checking Account
- If `has_overdraft_protection` is True, `overdraft_limit` must be provided
- `routing_number` should follow a valid format (9 digits for US)

#### Savings Account
- `interest_rate` must be a valid percentage (0-100%)
- `compound_frequency` must be one of: daily, monthly, quarterly, annually

#### Credit Account
- `credit_limit` must be greater than zero
- `statement_balance` cannot exceed `credit_limit`
- `minimum_payment` cannot exceed `statement_balance`
- `apr` must be a valid percentage

#### Payment App Account
- `platform` must be one of the supported platforms
- If `has_debit_card` is True, `card_last_four` should be provided
- `linked_account_ids` should contain valid account IDs

#### BNPL Account
- `installment_count` must be greater than zero
- `installments_paid` cannot exceed `installment_count`
- `payment_frequency` must be one of: weekly, biweekly, monthly
- `next_payment_date` must be in the future when creating account
- `current_balance` should equal (installment_count - installments_paid) * installment_amount

#### EWA Account
- `max_advance_percentage` must be between 0 and 100
- `next_payday` must be in the future when creating account
- `current_balance` represents the amount to be repaid on next payday

### API Layer Implementation

We will implement the following endpoints for banking account management:

```python
@router.get("/banking/overview", response_model=BankingOverviewResponse)
def get_banking_overview(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get an overview of banking accounts for the current user."""
    return account_service.get_banking_overview(current_user.id)

@router.get("/banking/upcoming-payments", response_model=List[UpcomingPaymentResponse])
def get_upcoming_payments(
    days: int = Query(14, description="Number of days to look ahead"),
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get upcoming payments for the current user."""
    return account_service.get_upcoming_payments(current_user.id, days)

@router.post("/accounts/banking", response_model=BankingAccountResponseUnion)
def create_banking_account(
    account_data: BankingAccountCreateUnion,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new banking account."""
    data_dict = account_data.model_dump()
    data_dict["user_id"] = current_user.id
    return account_service.create_account(data_dict)

@router.post("/accounts/bnpl/{account_id}/update-status", response_model=BNPLAccountResponse)
def update_bnpl_status(
    account_id: int,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Update BNPL account status."""
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.account_type != "bnpl":
        raise HTTPException(status_code=400, detail="Account is not a BNPL account")
    
    updated_account = account_service.update_bnpl_status(account_id)
    if not updated_account:
        raise HTTPException(status_code=500, detail="Failed to update BNPL account status")
    
    return updated_account
```

### Account Type Registry Updates

We'll update the AccountTypeRegistry to include the new account types:

```python
# During application initialization
account_type_registry = AccountTypeRegistry()

# Register traditional banking accounts
account_type_registry.register(
    account_type_id="checking",
    model_class=CheckingAccount,
    schema_class=CheckingAccountCreate,
    name="Checking Account",
    description="Standard transaction account for day-to-day banking",
    category="Banking"
)

account_type_registry.register(
    account_type_id="savings",
    model_class=SavingsAccount,
    schema_class=SavingsAccountCreate,
    name="Savings Account",
    description="Interest-bearing account for saving money",
    category="Banking"
)

account_type_registry.register(
    account_type_id="credit",
    model_class=CreditAccount,
    schema_class=CreditAccountCreate,
    name="Credit Card",
    description="Revolving credit account with a credit limit",
    category="Banking"
)

# Register modern financial services
account_type_registry.register(
    account_type_id="payment_app",
    model_class=PaymentAppAccount,
    schema_class=PaymentAppAccountCreate,
    name="Payment App",
    description="Digital wallet like PayPal, Venmo, or Cash App",
    category="Banking"
)

account_type_registry.register(
    account_type_id="bnpl",
    model_class=BNPLAccount,
    schema_class=BNPLAccountCreate,
    name="Buy Now, Pay Later",
    description="Short-term installment plan for purchases",
    category="Banking"
)

account_type_registry.register(
    account_type_id="ewa",
    model_class=EWAAccount,
    schema_class=EWAAccountCreate,
    name="Earned Wage Access",
    description="Early access to earned wages before payday",
    category="Banking"
)
```

## Consequences

### Positive

1. **Comprehensive Financial Picture**: Users can track all their banking accounts in one place, including modern financial services that weren't previously supported.

2. **Better Debt Tracking**: By properly modeling BNPL and EWA accounts, users get a more accurate view of their short-term debt obligations.

3. **Enhanced Financial Insights**: The service layer can now provide more meaningful analysis across different account types.

4. **Improved UX**: Type-specific fields and validation ensure that users provide only relevant information for each account type.

5. **Future-Proof Design**: The polymorphic architecture makes it easy to add new account types as financial services evolve.

### Negative

1. **Increased Complexity**: The polymorphic design introduces more tables and relationships to maintain.

2. **Query Performance**: Polymorphic queries may be more complex than single-table queries, potentially impacting performance for users with many accounts.

3. **Testing Overhead**: Each account type requires thorough testing of its specific fields and validation rules.

### Neutral

1. **UI Adaptation Required**: Frontend components need to adapt to the different fields for each account type.

2. **Database Migration**: New tables need to be created for each account type as part of the migration.

## Performance Impact

- **Single Account Retrieval**: < 10ms (direct ID lookup with polymorphic loading)
- **User Account List**: < 50ms for typical users (10-30 accounts)
- **Banking Overview Calculation**: < 100ms (requires aggregation across multiple account types)
- **Account Creation/Update**: < 100ms (multiple validation layers but minimal impact)

### Database Optimization Strategy

Given the potential performance impact of the polymorphic design, we will implement several optimization strategies:

1. **Selective Loading Strategy**:
   ```python
   # When only base fields are needed
   accounts = session.query(Account).filter(Account.user_id == user_id).all()
   
   # When full type details are needed
   accounts = session.query(Account).options(
       with_polymorphic('*')
   ).filter(Account.user_id == user_id).all()
   ```

2. **Comprehensive Indexing Strategy**:
   - Index on `account_type` in base Account table
   - Index on `user_id` for quick filtering
   - Index on `is_closed` to filter out closed accounts
   - For payment-related queries, index on date fields like `statement_due_date` and `next_payment_date`
   - Composite index on (user_id, account_type) for frequent queries

3. **Query Caching Strategy**:
   - Cache account lists with short TTL (5 minutes)
   - Cache aggregated metrics like banking overview
   - Invalidate caches on relevant account updates

4. **Denormalization for Performance**:
   - Add `next_action_date` and `next_action_amount` to the base Account model
   - Update these fields whenever a payment due date or amount changes
   - This allows efficient sorting/filtering across account types without joins

5. **Pagination Implementation**:
   - All list endpoints will implement cursor-based pagination
   - Default page size of 50 items
   - Include total count for UI pagination controls

6. **Database Connection Pooling**:
   - Configure appropriate connection pool size
   - Monitor connection usage under load
   - Set appropriate timeouts to prevent connection leaks

These optimizations will mitigate the performance impact of the polymorphic design, ensuring good performance even as user account counts grow.

## Cost Considerations

- **Development Effort**: Approximately 2-3 weeks for full implementation including:
  - Database model and migration development (3 days)
  - Schema and validation implementation (3 days)
  - Repository and service layer enhancements (5 days)
  - API implementation (2 days)
  - Testing and QA (5 days)

- **Maintenance Costs**: Low to moderate, as the polymorphic design minimizes code duplication but does require more database tables to maintain.

## Compliance & Security

- **Financial Data Protection**: All account data must be encrypted at rest.
- **Privacy Considerations**: The expanded account types capture more detailed financial information, requiring clear privacy policies.
- **No PCI DSS Scope**: The design explicitly avoids storing actual card numbers by only capturing the last four digits when needed.

## Dependencies

- **ADR-016** (Account Type Expansion - Foundation): This is a direct implementation of the polymorphic account model defined in ADR-016.
- **ADR-011** (DateTime Standardization): All date fields use UTC for storage and follow the standardization rules.
- **ADR-013** (Decimal Precision Handling): Monetary values use MoneyDecimal type with appropriate precision.
- **Bill Splitting Functionality**: The expanded account types must integrate with Debtonator's core bill splitting functionality.

## Timeline

- **Database Migration Development**: Week 1
- **Model and Schema Implementation**: Week 1-2
- **Repository and Service Layer Implementation**: Week 2
- **API Implementation**: Week 3
- **Testing and QA**: Week 3
- **Rollout**: End of Week 3

## Monitoring & Success Metrics

- **Account Type Adoption**: Track how many users create each type of account
- **Feature Utilization**: Monitor usage of type-specific features like upcoming payment tracking
- **Error Rates**: Monitor validation errors and failed operations by account type
- **Query Performance**: Track execution time for polymorphic queries
- **Data Quality**: Audit completeness and correctness of account data

## Team Impact

- **Backend Team**: Needs to implement and test all account type models, schemas, and business logic
- **Frontend Team**: Needs to create type-specific forms and displays for each account type
- **QA Team**: Needs to test each account type thoroughly, including edge cases
- **Documentation**: API documentation must be updated to include all new endpoints and schemas

## Related Documents

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [Account Type Expansion Planning](/code/debtonator/docs/adr/backend/016-account-type-expansion-planning.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)

## Notes

### Modeling Hybrid Financial Platforms

We decided to represent payment platforms like PayPal or Venmo primarily through the PaymentAppAccount type, which covers their wallet-like functionality. If a user also has a credit product from the same platform (e.g., PayPal Credit), that would be modeled as a separate CreditAccount with appropriate linking.

This approach maintains clear separation of concerns while still acknowledging the relationship between connected accounts from the same provider.

### Bill Splitting Integration

The expanded account types must integrate seamlessly with Debtonator's core bill splitting functionality. The implementation will ensure:

1. **Type-Appropriate Validation**: 
   - Only certain account types should be eligible for bill splits (e.g., checking accounts, credit accounts)
   - BNPL accounts should not be used for bill splits as they are already tied to specific purchases
   - EWA accounts should not be used for bill splits as they represent advances on income

2. **Split Payment Routing**:
   - Bill splits will continue to reference the base Account model
   - The repository layer will handle routing payments to the appropriate account subtypes
   - Validation will occur at the service layer to prevent invalid account type usage

3. **Balance Updates**:
   - When a bill split is created or modified, appropriate balance updates must occur for each account type
   - For asset accounts, the balance decreases
   - For liability accounts, the balance increases

4. **UI Considerations**:
   - The UI will clearly indicate which account types can be used for bill splits
   - Account selection dropdowns will filter out ineligible account types
   - Error messages will clearly explain why certain accounts cannot be used for splits

This integration ensures that the new account types enhance rather than disrupt the core bill splitting functionality.

### Balance Field Semantics and UI Representation

For consistency across account types, we define the `current_balance` field semantics:

- For asset accounts (Checking, Savings, Payment App): Positive balance represents available funds
- For liability accounts (Credit, BNPL, EWA): Positive balance represents amount owed
- For closed accounts: Balance should be zero

To avoid user confusion, the UI layer must clearly distinguish between these different balance semantics:

1. **Visual Differentiation**: Asset accounts will display balances in green, while liability accounts will display balances in red
2. **Explicit Labeling**: Instead of generically labeling everything as "Balance", asset accounts will show "Available: $X" while liability accounts will show "Owed: $X"
3. **Aggregation Logic**: When calculating totals, the service layer will handle the appropriate addition/subtraction based on account type
4. **Sign Conversion**: All displays of liability balances to users will include the appropriate negative sign to reinforce the debt semantics

This approach maintains internal consistency while providing clear visual and textual cues to users about the nature of each balance.

### Special BNPL Considerations

Buy Now Pay Later (BNPL) accounts require special handling for lifecycle management. Once all installments are paid, the account should automatically be marked as closed. The `update_bnpl_status` method handles this transition.

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-04-01 | 1.0 | Debtonator Team | Initial draft |
