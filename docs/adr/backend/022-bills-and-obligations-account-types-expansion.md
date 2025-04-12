# ADR-022: Bills and Obligations Account Types Expansion

## Status

Proposed

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

### Type-Specific Models

We will implement the following SQLAlchemy models for bills and obligations account types:

#### Base Obligation Account

To avoid duplication of common obligation attributes, we'll create a base obligation class:

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

## Performance Impact

- **Single Obligation Retrieval**: < 10ms (direct ID lookup with polymorphic loading)
- **Obligation Account List**: < 50ms for typical users (10-20 obligations)
- **Upcoming Bills Calculation**: < 100ms (requires filtering and date comparison)
- **Payment History Retrieval**: < 30ms (simple foreign key lookup)

### Optimization Strategies

To maintain performance with the obligation account structure:

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

## Integration with Existing Features

### Cashflow Analysis Integration

The obligation account types will integrate with Debtonator's cashflow analysis features:

1. **Forecasting Integration**:
   - Upcoming obligations will be included in cashflow forecasts
   - Different payment frequencies will be normalized to proper time periods
   - Obligations with variable amounts will use historical averages

2. **Payment Planning**:
   - Payment due dates will inform liquidity requirements
   - Autopay settings will be considered for account balance planning
   - Payment history will improve forecasting accuracy

3. **Budget Integration**:
   - Obligations will be categorized for budget allocation
   - Monthly equivalent amounts will be calculated for consistent budgeting
   - Seasonal variations will be identified and highlighted

## References

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-020: Loan Account Types Expansion](/code/debtonator/docs/adr/backend/020-loan-account-types-expansion.md)
- [ADR-021: Investment Account Types Expansion](/code/debtonator/docs/adr/backend/021-investment-account-types-expansion.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)
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

### Pydantic Schema Implementation

Following the pattern established in previous ADRs, we'll create Pydantic schemas for each obligation account type:

#### Base Obligation Schema

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

#### Payment History Schema

```python
class ObligationPaymentBase(BaseModel):
    """Base schema for obligation payments"""
    payment_date: datetime
    amount: MoneyDecimal
    payment_method: Optional[str] = None
    confirmation_number: Optional[str] = None
    notes: Optional[str] = None

class ObligationPaymentCreate(ObligationPaymentBase):
    """Create schema for obligation payments"""
    pass

class ObligationPaymentResponse(ObligationPaymentBase):
    """Response schema for obligation payments"""
    id: int
    obligation_id: int
```

#### Type-Specific Schemas

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

Similar schemas will be created for other obligation types with appropriate fields and validations.

### Discriminated Union for API

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

### Bill Management Service

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
        
    def get_payment_history(
        self, obligation_id: int, limit: int = 10
    ) -> List[ObligationPayment]:
        """Get payment history for an obligation account"""
        return self.payment_repository.get_by_obligation(obligation_id, limit)
    
    def get_bills_by_category(self, user_id: int) -> Dict:
        """Get bills organized by category"""
        # Get all obligation accounts
        obligation_accounts = self.account_repository.get_by_user_and_types(
            user_id,
            ["utility", "subscription", "insurance", "tax", "support_payment"]
        )
        
        # Filter out closed accounts
        active_accounts = [a for a in obligation_accounts if not a.is_closed]
        
        # Organize by type
        bills_by_type = {
            "utilities": [],
            "subscriptions": [],
            "insurance": [],
            "taxes": [],
            "support_payments": [],
        }
        
        for account in active_accounts:
            if account.account_type == "utility":
                bills_by_type["utilities"].append(self._account_to_dict(account))
            elif account.account_type == "subscription":
                bills_by_type["subscriptions"].append(self._account_to_dict(account))
            elif account.account_type == "insurance":
                bills_by_type["insurance"].append(self._account_to_dict(account))
            elif account.account_type == "tax":
                bills_by_type["taxes"].append(self._account_to_dict(account))
            elif account.account_type == "support_payment":
                bills_by_type["support_payments"].append(self._account_to_dict(account))
        
        # Calculate totals by type and frequency
        monthly_totals = {
            "utilities": sum(self._to_monthly_amount(b["payment_amount"], b["payment_frequency"]) for b in bills_by_type["utilities"]),
            "subscriptions": sum(self._to_monthly_amount(b["payment_amount"], b["payment_frequency"]) for b in bills_by_type["subscriptions"]),
            "insurance": sum(self._to_monthly_amount(b["payment_amount"], b["payment_frequency"]) for b in bills_by_type["insurance"]),
            "taxes": sum(self._to_monthly_amount(b["payment_amount"], b["payment_frequency"]) for b in bills_by_type["taxes"]),
            "support_payments": sum(self._to_monthly_amount(b["payment_amount"], b["payment_frequency"]) for b in bills_by_type["support_payments"]),
        }
        
        total_monthly = sum(monthly_totals.values())
        
        return {
            "bills_by_type": bills_by_type,
            "monthly_totals": monthly_totals,
            "total_monthly": total_monthly,
            "total_annual": total_monthly * 12
        }
    
    def get_bills_by_due_date(self, user_id: int) -> Dict:
        """Get bills organized by due date (week, month, quarter, year)"""
        now = datetime_utils.utc_now()
        
        # Define date ranges
        week_end = datetime_utils.add_days(now, 7)
        month_end = datetime_utils.add_days(now, 30)
        quarter_end = datetime_utils.add_days(now, 90)
        year_end = datetime_utils.add_days(now, 365)
        
        # Get all obligation accounts
        obligation_accounts = self.account_repository.get_by_user_and_types(
            user_id,
            ["utility", "subscription", "insurance", "tax", "support_payment"]
        )
        
        # Filter out closed accounts
        active_accounts = [a for a in obligation_accounts if not a.is_closed]
        
        # Organize by due date
        due_this_week = []
        due_this_month = []
        due_this_quarter = []
        due_this_year = []
        other = []
        
        for account in active_accounts:
            account_dict = self._account_to_dict(account)
            
            if account.next_due_date <= week_end:
                due_this_week.append(account_dict)
            elif account.next_due_date <= month_end:
                due_this_month.append(account_dict)
            elif account.next_due_date <= quarter_end:
                due_this_quarter.append(account_dict)
            elif account.next_due_date <= year_end:
                due_this_year.append(account_dict)
            else:
                other.append(account_dict)
        
        # Sort each list by due date
        due_this_week = sorted(due_this_week, key=lambda x: x["next_due_date"])
        due_this_month = sorted(due_this_month, key=lambda x: x["next_due_date"])
        due_this_quarter = sorted(due_this_quarter, key=lambda x: x["next_due_date"])
        due_this_year = sorted(due_this_year, key=lambda x: x["next_due_date"])
        
        # Calculate totals by time period
        week_total = sum(b["payment_amount"] for b in due_this_week)
        month_total = week_total + sum(b["payment_amount"] for b in due_this_month)
        quarter_total = month_total + sum(b["payment_amount"] for b in due_this_quarter)
        year_total = quarter_total + sum(b["payment_amount"] for b in due_this_year)
        
        return {
            "due_this_week": {
                "bills": due_this_week,
                "total": week_total
            },
            "due_this_month": {
                "bills": due_this_month,
                "total": month_total
            },
            "due_this_quarter": {
                "bills": due_this_quarter,
                "total": quarter_total
            },
            "due_this_year": {
                "bills": due_this_year,
                "total": year_total
            },
            "other": other
        }
    
    def _account_to_dict(self, account: ObligationAccount) -> Dict:
        """Convert an obligation account to a dictionary"""
        base_dict = {
            "id": account.id,
            "name": account.name,
            "account_type": account.account_type,
            "payment_amount": account.payment_amount,
            "payment_frequency": account.payment_frequency,
            "next_due_date": account.next_due_date,
            "autopay_enabled": account.autopay_enabled,
            "payment_method": account.payment_method,
            "payment_account_id": account.payment_account_id,
            "is_closed": account.is_closed
        }
        
        # Add type-specific fields
        if account.account_type == "utility":
            base_dict.update({
                "service_type": account.service_type,
                "service_address": account.service_address,
                "billing_cycle_day": account.billing_cycle_day
            })
        elif account.account_type == "subscription":
            base_dict.update({
                "service_type": account.service_type,
                "auto_renew": account.auto_renew,
                "trial_end_date": account.trial_end_date
            })
        elif account.account_type == "insurance":
            base_dict.update({
                "policy_type": account.policy_type,
                "provider": account.provider,
                "policy_number": account.policy_number,
                "policy_start_date": account.policy_start_date,
                "policy_end_date": account.policy_end_date
            })
        elif account.account_type == "tax":
            base_dict.update({
                "tax_type": account.tax_type,
                "authority": account.authority,
                "tax_year": account.tax_year,
                "is_payment_plan": account.is_payment_plan
            })
        elif account.account_type == "support_payment":
            base_dict.update({
                "obligation_type": account.obligation_type,
                "recipient": account.recipient,
                "start_date": account.start_date,
                "end_date": account.end_date,
                "arrears_balance": account.arrears_balance
            })
        
        return base_dict
    
    def _calculate_next_due_date(
        self, current_due_date: datetime, payment_frequency: str
    ) -> datetime:
        """Calculate the next due date based on payment frequency"""
        if payment_frequency == "weekly":
            return datetime_utils.add_days(current_due_date, 7)
        elif payment_frequency == "biweekly":
            return datetime_utils.add_days(current_due_date, 14)
        elif payment_frequency == "monthly":
            return datetime_utils.add_months(current_due_date, 1)
        elif payment_frequency == "quarterly":
            return datetime_utils.add_months(current_due_date, 3)
        elif payment_frequency == "semiannual":
            return datetime_utils.add_months(current_due_date, 6)
        elif payment_frequency == "annual":
            return datetime_utils.add_months(current_due_date, 12)
        else:
            # Default to monthly if frequency not recognized
            return datetime_utils.add_months(current_due_date, 1)
    
    def _to_monthly_amount(self, amount: Decimal, frequency: str) -> Decimal:
        """Convert an amount to a monthly equivalent based on frequency"""
        if frequency == "weekly":
            return amount * Decimal("4.33")  # Average weeks per month
        elif frequency == "biweekly":
            return amount * Decimal("2.17")  # Average bi-weeks per month
        elif frequency == "monthly":
            return amount
        elif frequency == "quarterly":
            return amount / Decimal("3")
        elif frequency == "semiannual":
            return amount / Decimal("6")
        elif frequency == "annual":
            return amount / Decimal("12")
        else:
            # Default to monthly if frequency not recognized
            return amount
    
    def _update_support_payment_arrears(
        self, account: SupportPaymentAccount, payment_amount: Decimal
    ) -> None:
        """Update arrears balance for support payment accounts"""
        # Only update if there are arrears or payment differs from obligation
        if account.arrears_balance > 0 or payment_amount != account.payment_amount:
            difference = payment_amount - account.payment_amount
            
            # If paid less than required, increase arrears
            if difference < 0:
                account.arrears_balance -= difference  # Subtract negative = add to arrears
            
            # If paid more than required, decrease arrears
            elif difference > 0 and account.arrears_balance > 0:
                # Can't reduce arrears below zero
                account.arrears_balance = max(Decimal("0"), account.arrears_balance - difference)
            
            # Update the account
            self.account_repository.update(
                account.id,
                {"arrears_balance": account.arrears_balance}
            )
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

#### Utility Account

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

#### Subscription Account

```python
class SubscriptionAccount(ObligationAccount):
    """Recurring subscription services"""
    __tablename__ = "subscription_accounts"
    
    id = Column(Integer, ForeignKey("obligation_accounts.id"), primary_key=True)
    renewal_frequency = Column(String, nullable=False)  # monthly, annual, etc.
    service_type = Column(String, nullable=True)  # streaming, software, membership, etc.
    auto_renew = Column(Boolean, default=True, nullable=False)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    cancellation_url = Column(String, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "subscription",
    }
```

#### Insurance Account

```python
class InsuranceAccount(ObligationAccount):
    """Insurance policies with recurring premiums"""
    __tablename__ = "insurance_accounts"
    
    id = Column(Integer, ForeignKey("obligation_accounts.id"), primary_key=True)
    policy_type = Column(String, nullable=False)  # auto, health, home, life, etc.
    provider = Column(String, nullable=False)
    policy_number = Column(String, nullable=True)
    policy_start_date = Column(DateTime(timezone=True), nullable=False)
    policy_end_date = Column(DateTime(timezone=True), nullable=False)
    coverage_details = Column(String, nullable=True)
    beneficiary = Column(String, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "insurance",
    }
```

#### Tax Account

```python
class TaxAccount(ObligationAccount):
    """Tax obligations like property tax, estimated income tax, etc."""
    __tablename__ = "tax_accounts"
    
    id = Column(Integer, ForeignKey("obligation_accounts.id"), primary_key=True)
    tax_type = Column(String, nullable=False)  # property, income, etc.
    authority = Column(String, nullable=False)  # IRS, state name, county, etc.
    tax_year = Column(Integer, nullable=True)
    tax_id = Column(String, nullable=True)  # Parcel number, EIN, etc.
    interest_rate = Column(Numeric(6, 4), nullable=True)  # For payment plans
    penalty_rate = Column(Numeric(6, 4), nullable=True)
    is_payment_plan = Column(Boolean, default=False, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "tax",
    }
```

#### Support Payment Account

```python
class SupportPaymentAccount(ObligationAccount):
    """Legal support obligations like child support, alimony, etc."""
    __tablename__ = "support_payment_accounts"
    
    id = Column(Integer, ForeignKey("obligation_accounts.id"), primary_key=True)
    obligation_type = Column(String, nullable=False)  # child_support, alimony, etc.
    recipient = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    case_number = Column(String, nullable=True)
    arrears_balance = Column(Numeric(12, 4), nullable=False, default=0)
    interest_on_arrears = Column(Numeric(6, 4), nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "support_payment",
    }
```

### Obligation Payment History Model

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

### Repository Layer Enhancements

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

### API Layer Implementation

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

### Account Type Registry Updates

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

account_type_registry.register(
    account_type_id="subscription",
    model_class=SubscriptionAccount,
    schema_class=SubscriptionAccountCreate,
    name="Subscription",
    description="Recurring subscription service like streaming, software, etc.",
    category="Bills"
)

account_type_registry.register(
    account_type_id="insurance",
    model_class=InsuranceAccount,
    schema_class=InsuranceAccountCreate,
    name="Insurance",
    description="Insurance policy with recurring premium payments",
    category="Bills"
)

account_type_registry.register(
    account_type_id="tax",
    model_class=TaxAccount,
    schema_class=TaxAccountCreate,
    name="Tax",
    description="Tax obligation like property tax, estimated income tax, etc.",
    category="Bills"
)

account_type_registry.register(
    account_type_id="support_payment",
    model_class=SupportPaymentAccount,
    schema_class=SupportPaymentAccountCreate,
    name="Support Payment",
    description="Legal support obligation like child support or alimony",
    category="Bills"
)
```

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

## Performance Impact

- **Single Obligation Retrieval**: < 10ms (direct ID lookup with polymorphic loading)
- **Obligation Account List**: < 50ms for typical users (10-20 obligations)
- **Upcoming Bills Calculation**: < 100ms (requires filtering and date comparison)
- **Payment History Retrieval**: < 30ms (simple foreign key lookup)

### Optimization Strategies

To maintain performance with the obligation account structure:

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

## Integration with Existing Features

### Cashflow Analysis Integration

The obligation account types will integrate with Debtonator's cashflow analysis features:

1. **Forecasting Integration**:
   - Upcoming obligations will be included in cashflow forecasts
   - Different payment frequencies will be normalized to proper time periods
   - Obligations with variable amounts will use historical averages

2. **Payment Planning**:
   - Payment due dates will inform liquidity requirements
   - Autopay settings will be considered for account balance planning
   - Payment history will improve forecasting accuracy

3. **Budget Integration**:
   - Obligations will be categorized for budget allocation
   - Monthly equivalent amounts will be calculated for consistent budgeting
   - Seasonal variations will be identified and highlighted

## References

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-020: Loan Account Types Expansion](/code/debtonator/docs/adr/backend/020-loan-account-types-expansion.md)
- [ADR-021: Investment Account Types Expansion](/code/debtonator/docs/adr/backend/021-investment-account-types-expansion.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)