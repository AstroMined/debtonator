# ADR-025: Statement Type Expansion

## Status

Proposed

## Context

The Debtonator application currently uses a single `StatementHistory` model for all account types. This approach has led to several issues:

1. Test failures show that there's a mismatch between field names in the model and schema (`due_date` vs `payment_due_date`)
2. Different account types have different statement requirements and semantics
3. The current structure fails to properly validate minimum_payment values for different account types
4. Validation rules that apply to credit accounts don't apply to checking or savings accounts
5. The current implementation doesn't align with the polymorphic account type architecture established in ADR-016

The test failures in `/code/debtonator/tests/unit/schemas/test_statement_history_schemas.py` highlight these issues:

- `'StatementHistoryCreate' object has no attribute 'payment_due_date'` (related field is called `due_date` in the model)
- Validation tests failing because they make assumptions about payment due dates that only apply to credit accounts
- Lack of account-type-specific validation for statement balances and minimum payments

### Current Limitations

1. All statement histories share the same model and schema regardless of account type
2. Credit-specific fields (minimum_payment, due_date) are applied to all account types
3. Schema validation logic is inconsistent with underlying model field names
4. Type-specific validation is missing (e.g., minimum payments for credit accounts vs statements for checking accounts)
5. Account-type-specific statement data cannot be properly captured

### Technical Debt to Address

1. **Field Naming Inconsistency**: The schema uses `payment_due_date` while the model uses `due_date`
2. **Schema Validation Mismatch**: Validation logic assumes credit-card-like behavior for all statement types
3. **Missing Type-Specific Fields**: Different statement types need different fields (e.g., interest earned for savings)
4. **Inconsistent Test Expectations**: Tests expect all statements to validate like credit statements

## Decision

We will implement a polymorphic statement history structure that mirrors our account type hierarchy, following the design patterns established in ADR-016:

1. A base `StatementHistory` model containing common fields and behaviors
2. Type-specific statement models that inherit from the base with specialized fields
3. Corresponding Pydantic schemas that mirror the inheritance structure
4. Updated repository, service, and API layers to work with the polymorphic models
5. Integration with the feature flag system for controlled deployment of new statement types

### Statement Type Categorization

Our statement types will follow the account type hierarchy:

#### Tier 1: Major Categories
- Banking Statement Types (checking, savings, credit, payment apps)
- Investment Statement Types (brokerage, retirement)
- Loan Statement Types (personal loans, mortgages)
- Bill/Utility Statement Types (utility bill statements)

#### Tier 2: Account Types (Examples)
- Banking: CheckingStatement, SavingsStatement, CreditStatement, PaymentAppStatement
- Investment: BrokerageStatement, RetirementStatement
- Loan: LoanStatement, MortgageStatement
- Bills/Utilities: UtilityStatement, SubscriptionStatement

### Base Statement History Model

All statement types will share these core attributes in the base StatementHistory model:

```python
class StatementHistory(BaseDBModel):
    """Base statement history model for all account types."""
    
    __tablename__ = "statement_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    statement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date of the statement (UTC timezone)",
    )
    statement_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Balance on statement date"
    )
    statement_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type of statement - discriminator for polymorphic identity",
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="ISO 4217 currency code (e.g., USD, EUR, GBP)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Record creation timestamp (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        comment="Record last update timestamp (UTC)",
    )
    
    # Relationships
    account: Mapped["Account"] = relationship(
        "Account", back_populates="statement_history"
    )
    
    __mapper_args__ = {
        "polymorphic_on": statement_type,
        "polymorphic_identity": "statement"
    }
```

### Type-Specific Statement Models

Each statement type will have its own model that inherits from the base StatementHistory model, with specialized fields:

```python
class CreditStatement(StatementHistory):
    """Statement history for credit accounts."""
    
    __tablename__ = "credit_statements"
    
    id: Mapped[int] = mapped_column(ForeignKey("statement_history.id"), primary_key=True)
    minimum_payment: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Minimum payment due"
    )
    payment_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Payment due date (UTC timezone)"
    )
    interest_charged: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Interest charged this statement period"
    )
    fees_charged: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Fees charged this statement period"
    )
    payments_made: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Payments made during statement period"
    )
    is_paid: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether the statement is paid"
    )
    
    __mapper_args__ = {"polymorphic_identity": "credit"}

class CheckingStatement(StatementHistory):
    """Statement history for checking accounts."""
    
    __tablename__ = "checking_statements"
    
    id: Mapped[int] = mapped_column(ForeignKey("statement_history.id"), primary_key=True)
    deposits_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of deposits in statement period"
    )
    withdrawals_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of withdrawals in statement period"
    )
    deposits_total: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Total deposits in statement period"
    )
    withdrawals_total: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Total withdrawals in statement period"
    )
    fees_charged: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Fees charged this statement period"
    )
    
    __mapper_args__ = {"polymorphic_identity": "checking"}

class SavingsStatement(StatementHistory):
    """Statement history for savings accounts."""
    
    __tablename__ = "savings_statements"
    
    id: Mapped[int] = mapped_column(ForeignKey("statement_history.id"), primary_key=True)
    interest_earned: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Interest earned this statement period"
    )
    apy_for_period: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4), nullable=True, comment="APY for this statement period"
    )
    deposits_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of deposits in statement period"
    )
    withdrawals_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of withdrawals in statement period"
    )
    
    __mapper_args__ = {"polymorphic_identity": "savings"}
```

### Pydantic Schema Architecture

The Pydantic schema layer will mirror the model inheritance structure, using discriminated unions to handle polymorphic validation:

```python
class StatementHistoryBase(BaseSchemaValidator):
    """Base schema for all statement history types."""
    
    account_id: int = Field(..., gt=0, description="ID of the associated account")
    statement_date: datetime = Field(
        ..., description="Date of the statement (UTC timezone)"
    )
    statement_balance: MoneyDecimal = Field(
        ..., ge=0, description="Balance on statement date"
    )
    statement_type: str = Field(
        ..., description="Type of statement"
    )
    currency: str = Field(
        "USD", min_length=3, max_length=3, 
        description="ISO 4217 currency code (e.g., USD, EUR, GBP)"
    )

class StatementHistoryCreate(StatementHistoryBase):
    """Base schema for creating a new statement history record."""
    
    @validator("statement_type")
    def validate_statement_type(cls, v):
        allowed_types = ["credit", "checking", "savings", "loan", "brokerage", "utility"]
        if v not in allowed_types:
            raise ValueError(f"Invalid statement type. Must be one of: {', '.join(allowed_types)}")
        return v

class CreditStatementBase(StatementHistoryBase):
    """Base schema for credit account statements."""
    
    statement_type: Literal["credit"] = "credit"
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    payment_due_date: Optional[datetime] = Field(
        default=None, description="Payment due date (UTC timezone)"
    )
    interest_charged: Optional[MoneyDecimal] = Field(
        default=None, description="Interest charged this statement period", ge=0
    )
    fees_charged: Optional[MoneyDecimal] = Field(
        default=None, description="Fees charged this statement period", ge=0
    )
    payments_made: Optional[MoneyDecimal] = Field(
        default=None, description="Payments made during statement period", ge=0
    )
    is_paid: bool = Field(default=False, description="Whether the statement is paid")
    
    @model_validator(mode="after")
    def validate_credit_statement(self):
        """Validate credit statement specific rules."""
        # 1. Check minimum payment against statement balance
        if (self.minimum_payment is not None and self.statement_balance is not None
                and self.minimum_payment > self.statement_balance):
            raise ValueError("Minimum payment cannot exceed statement balance")
        
        # 2. Check payment due date against statement date
        if (self.payment_due_date is not None and self.statement_date is not None
                and ensure_utc(self.payment_due_date) < ensure_utc(self.statement_date)):
            raise ValueError("Payment due date cannot be before statement date")
        
        return self

class CreditStatementCreate(CreditStatementBase, StatementHistoryCreate):
    """Schema for creating a credit statement history record."""
    pass

class CheckingStatementBase(StatementHistoryBase):
    """Base schema for checking account statements."""
    
    statement_type: Literal["checking"] = "checking"
    deposits_count: Optional[int] = Field(
        default=None, description="Number of deposits in statement period", ge=0
    )
    withdrawals_count: Optional[int] = Field(
        default=None, description="Number of withdrawals in statement period", ge=0
    )
    deposits_total: Optional[MoneyDecimal] = Field(
        default=None, description="Total deposits in statement period", ge=0
    )
    withdrawals_total: Optional[MoneyDecimal] = Field(
        default=None, description="Total withdrawals in statement period", ge=0
    )
    fees_charged: Optional[MoneyDecimal] = Field(
        default=None, description="Fees charged this statement period", ge=0
    )

class CheckingStatementCreate(CheckingStatementBase, StatementHistoryCreate):
    """Schema for creating a checking statement history record."""
    pass

class SavingsStatementBase(StatementHistoryBase):
    """Base schema for savings account statements."""
    
    statement_type: Literal["savings"] = "savings"
    interest_earned: Optional[MoneyDecimal] = Field(
        default=None, description="Interest earned this statement period", ge=0
    )
    apy_for_period: Optional[PercentageDecimal] = Field(
        default=None, description="APY for this statement period", ge=0
    )
    deposits_count: Optional[int] = Field(
        default=None, description="Number of deposits in statement period", ge=0
    )
    withdrawals_count: Optional[int] = Field(
        default=None, description="Number of withdrawals in statement period", ge=0
    )

class SavingsStatementCreate(SavingsStatementBase, StatementHistoryCreate):
    """Schema for creating a savings statement history record."""
    pass
```

### Discriminated Union for API

To handle all statement types in a single API endpoint, we'll use Pydantic's discriminated unions:

```python
StatementHistoryCreateUnion = Annotated[
    Union[
        CreditStatementCreate,
        CheckingStatementCreate,
        SavingsStatementCreate,
        # Add other statement type create schemas as they're implemented
    ],
    Field(discriminator="statement_type")
]

StatementHistoryResponseUnion = Annotated[
    Union[
        CreditStatementResponse,
        CheckingStatementResponse,
        SavingsStatementResponse,
        # Add other statement type response schemas as they're implemented
    ],
    Field(discriminator="statement_type")
]
```

## Repository Module Pattern Integration

Following the project's Repository Module Pattern as documented in system_patterns.md, we'll implement specialized repository modules for each statement type:

### Directory Structure

```
src/
  repositories/
    statement_types/
      banking/
        credit_statement.py
        checking_statement.py
        savings_statement.py
      investment/
        brokerage_statement.py
        retirement_statement.py
      loan/
        loan_statement.py
        mortgage_statement.py
```

### Base Repository Implementation

```python
# src/repositories/statement_history.py
class StatementHistoryRepository(BaseRepository):
    """Repository for statement history entities with polymorphic operations."""
    
    def __init__(
        self, 
        session: AsyncSession,
        statement_type_registry: Optional[StatementTypeRegistry] = None,
        feature_flag_service: Optional[FeatureFlagService] = None
    ):
        super().__init__(session)
        self.model_class = StatementHistory
        self.statement_type_registry = statement_type_registry or get_statement_type_registry()
        self.feature_flag_service = feature_flag_service or get_feature_flag_service()
        
        # Dynamically bind type-specific methods
        self._bind_type_specific_methods()
    
    async def get_with_type(self, id: int) -> Optional[StatementHistory]:
        """Get statement by ID, ensuring type-specific data is loaded."""
        stmt = select(StatementHistory).options(
            with_polymorphic('*')
        ).where(StatementHistory.id == id)
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_account_id(self, account_id: int) -> List[StatementHistory]:
        """Get all statements for a specific account."""
        stmt = select(StatementHistory).options(
            with_polymorphic('*')
        ).where(StatementHistory.account_id == account_id)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create_typed_statement(
        self, statement_type: str, data: dict
    ) -> StatementHistory:
        """Create a new statement of the specified type."""
        if not self._is_statement_type_enabled(statement_type):
            raise FeatureFlagError(f"Statement type '{statement_type}' is not enabled")
            
        model_class = self.statement_type_registry.get_model_class(statement_type)
        if not model_class:
            raise ValueError(f"Unknown statement type: {statement_type}")
        
        statement = model_class(**data)
        self.session.add(statement)
        await self.session.commit()
        await self.session.refresh(statement)
        return statement
    
    def _bind_type_specific_methods(self):
        """Dynamically bind type-specific methods from modules."""
        for statement_type in self.statement_type_registry.get_all_types():
            type_id = statement_type["id"]
            
            # Skip if feature flag is disabled for this type
            if not self._is_statement_type_enabled(type_id):
                continue
                
            module_path = self.statement_type_registry.get_repository_module(type_id)
            if not module_path:
                continue
                
            try:
                module = importlib.import_module(module_path)
                
                # Find all functions in the module that take a session as first param
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith('_'):
                        continue
                        
                    sig = inspect.signature(func)
                    params = list(sig.parameters.values())
                    
                    # Check if function signature is compatible (takes session as first param)
                    if params and params[0].name == 'session':
                        # Bind the function to this repository instance
                        bound_method = functools.partial(func, self.session)
                        setattr(self, name, bound_method)
                        
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not load repository module for {type_id}: {e}")
    
    def _is_statement_type_enabled(self, statement_type: str) -> bool:
        """Check if a statement type is enabled via feature flags."""
        if not self.feature_flag_service:
            return True
            
        # Get feature flag name for statement type
        flag_name = f"STATEMENT_TYPE_{statement_type.upper()}_ENABLED"
        
        # Special case for core types
        if statement_type in ["credit", "checking", "savings"]:
            return self.feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED")
            
        return self.feature_flag_service.is_enabled(flag_name)
```

### Type-Specific Repository Module Example

```python
# src/repositories/statement_types/banking/credit_statement.py

async def get_upcoming_due_payments(session: AsyncSession, days: int = 30) -> List[CreditStatement]:
    """
    Get upcoming credit statements with due dates within the specified days.
    Only applies to credit statements with payment_due_date.
    
    This function is dynamically bound to the StatementHistoryRepository.
    """
    now = utc_now()
    end_date = add_days(now, days)
    
    stmt = select(CreditStatement).where(
        CreditStatement.payment_due_date.between(now, end_date),
        CreditStatement.is_paid == False
    )
    
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_unpaid_statements(session: AsyncSession, account_ids: List[int]) -> List[CreditStatement]:
    """
    Get all unpaid credit statements for the specified accounts.
    
    This function is dynamically bound to the StatementHistoryRepository.
    """
    stmt = select(CreditStatement).where(
        CreditStatement.account_id.in_(account_ids),
        CreditStatement.is_paid == False
    ).order_by(CreditStatement.payment_due_date.asc())
    
    result = await session.execute(stmt)
    return result.scalars().all()

async def mark_statement_paid(
    session: AsyncSession, statement_id: int, paid_amount: Decimal
) -> Optional[CreditStatement]:
    """
    Mark a credit statement as paid.
    
    This function is dynamically bound to the StatementHistoryRepository.
    """
    stmt = select(CreditStatement).where(CreditStatement.id == statement_id)
    result = await session.execute(stmt)
    statement = result.scalars().first()
    
    if not statement:
        return None
    
    statement.is_paid = True
    statement.payments_made = paid_amount
    statement.updated_at = utc_now()
    
    await session.commit()
    await session.refresh(statement)
    return statement
```

## Statement Type Registry

Following the pattern established in ADR-016, we'll implement a registry for statement types:

```python
class StatementTypeRegistry:
    """Registry for statement type models, schemas, and operations."""
    
    def __init__(self):
        self._registry = {}
    
    def register(
        self,
        statement_type_id: str,
        model_class: Type,
        schema_class: Type,
        repository_module: str,
        name: str,
        description: str,
        category: str
    ):
        """Register a new statement type with its classes and metadata."""
        self._registry[statement_type_id] = {
            "model_class": model_class,
            "schema_class": schema_class,
            "repository_module": repository_module,
            "name": name,
            "description": description,
            "category": category
        }
    
    def get_model_class(self, statement_type_id: str) -> Optional[Type]:
        """Get the model class for a given statement type."""
        return self._registry.get(statement_type_id, {}).get("model_class")
    
    def get_schema_class(self, statement_type_id: str) -> Optional[Type]:
        """Get the schema class for a given statement type."""
        return self._registry.get(statement_type_id, {}).get("schema_class")
    
    def get_repository_module(self, statement_type_id: str) -> Optional[str]:
        """Get the repository module path for a given statement type."""
        return self._registry.get(statement_type_id, {}).get("repository_module")
    
    def get_all_types(self) -> List[Dict[str, Any]]:
        """Get all registered statement types."""
        return [
            {
                "id": type_id,
                "name": info["name"],
                "description": info["description"],
                "category": info["category"]
            }
            for type_id, info in self._registry.items()
        ]
    
    def get_types_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get statement types filtered by category."""
        return [
            {
                "id": type_id,
                "name": info["name"],
                "description": info["description"],
                "category": info["category"]
            }
            for type_id, info in self._registry.items()
            if info["category"] == category
        ]
```

## Schema Factory Pattern Integration

To solve the "Missing Schema Factories" issue, we'll implement factories for statement schemas:

```python
# src/schemas/factories/statement_history_factory.py

class StatementSchemaFactory:
    """Factory for creating statement history schemas."""
    
    @staticmethod
    def create_credit_statement(**kwargs) -> CreditStatementCreate:
        """Create a credit statement schema with default values."""
        now = utc_now()
        
        defaults = {
            "account_id": 1,
            "statement_type": "credit",
            "statement_date": now,
            "statement_balance": Decimal("1000.00"),
            "minimum_payment": Decimal("25.00"),
            "payment_due_date": add_days(now, 21),
            "interest_charged": Decimal("12.50"),
            "fees_charged": Decimal("0.00"),
            "is_paid": False,
            "currency": "USD"
        }
        
        defaults.update(kwargs)
        return CreditStatementCreate(**defaults)
    
    @staticmethod
    def create_checking_statement(**kwargs) -> CheckingStatementCreate:
        """Create a checking statement schema with default values."""
        now = utc_now()
        
        defaults = {
            "account_id": 1,
            "statement_type": "checking",
            "statement_date": now,
            "statement_balance": Decimal("2500.00"),
            "deposits_count": 3,
            "withdrawals_count": 12,
            "deposits_total": Decimal("3200.00"),
            "withdrawals_total": Decimal("1800.00"),
            "fees_charged": Decimal("0.00"),
            "currency": "USD"
        }
        
        defaults.update(kwargs)
        return CheckingStatementCreate(**defaults)
    
    @staticmethod
    def create_savings_statement(**kwargs) -> SavingsStatementCreate:
        """Create a savings statement schema with default values."""
        now = utc_now()
        
        defaults = {
            "account_id": 1,
            "statement_type": "savings",
            "statement_date": now,
            "statement_balance": Decimal("5000.00"),
            "interest_earned": Decimal("4.17"),
            "apy_for_period": Decimal("0.01"),
            "deposits_count": 1,
            "withdrawals_count": 0,
            "currency": "USD"
        }
        
        defaults.update(kwargs)
        return SavingsStatementCreate(**defaults)
    
    @classmethod
    def create_statement_for_account_type(
        cls, account_type: str, **kwargs
    ) -> StatementHistoryCreate:
        """Create an appropriate statement schema based on account type."""
        account_to_statement_map = {
            "checking": cls.create_checking_statement,
            "savings": cls.create_savings_statement,
            "credit": cls.create_credit_statement,
            # Add more mappings as new types are implemented
        }
        
        factory_method = account_to_statement_map.get(account_type)
        if not factory_method:
            raise ValueError(f"No statement factory for account type: {account_type}")
        
        return factory_method(**kwargs)
```

## Feature Flag Integration

We'll integrate the statement type expansion with the feature flag system:

```python
# Feature flag naming convention for statement types
STATEMENT_TYPE_CREDIT_ENABLED = "STATEMENT_TYPE_CREDIT_ENABLED"
STATEMENT_TYPE_CHECKING_ENABLED = "STATEMENT_TYPE_CHECKING_ENABLED"
STATEMENT_TYPE_SAVINGS_ENABLED = "STATEMENT_TYPE_SAVINGS_ENABLED"
STATEMENT_TYPE_LOAN_ENABLED = "STATEMENT_TYPE_LOAN_ENABLED"
STATEMENT_TYPE_BROKERAGE_ENABLED = "STATEMENT_TYPE_BROKERAGE_ENABLED"

# Base statement types are controlled by existing account type flags
BANKING_STATEMENT_TYPES_ENABLED = "BANKING_ACCOUNT_TYPES_ENABLED"

# Feature flags for cross-cutting statement features
MULTI_CURRENCY_STATEMENTS_ENABLED = "MULTI_CURRENCY_SUPPORT_ENABLED"
STATEMENT_ANALYTICS_ENABLED = "STATEMENT_ANALYTICS_ENABLED"
STATEMENT_NOTIFICATION_ENABLED = "STATEMENT_NOTIFICATION_ENABLED"

# Register the feature flags with the registry
def register_statement_feature_flags(feature_flag_service: FeatureFlagService):
    """Register feature flags for statement types."""
    # Core banking statement types (enabled by default)
    feature_flag_service.register_flag(
        flag_name=BANKING_STATEMENT_TYPES_ENABLED,
        flag_type="boolean",
        default_value=True,
        description="Enable banking statement types (credit, checking, savings)"
    )
    
    # Other statement types (disabled by default)
    feature_flag_service.register_flag(
        flag_name=STATEMENT_TYPE_LOAN_ENABLED,
        flag_type="boolean",
        default_value=False,
        description="Enable loan statement type"
    )
    
    feature_flag_service.register_flag(
        flag_name=STATEMENT_TYPE_BROKERAGE_ENABLED,
        flag_type="boolean",
        default_value=False,
        description="Enable brokerage statement type"
    )
    
    # Cross-cutting features (linked to existing flags)
    feature_flag_service.register_flag(
        flag_name=MULTI_CURRENCY_STATEMENTS_ENABLED,
        flag_type="boolean",
        default_value=False,
        description="Enable multi-currency support for statements"
    )
    
    feature_flag_service.register_flag(
        flag_name=STATEMENT_ANALYTICS_ENABLED,
        flag_type="boolean",
        default_value=False,
        description="Enable advanced statement analytics features"
    )
```

### Feature Flag-Aware Service Layer

The service layer will check feature flags before operation:

```python
class StatementService:
    """Service for managing statement history with type-specific operations."""
    
    def __init__(
        self, 
        statement_repository: StatementHistoryRepository,
        account_repository: AccountRepository,
        feature_flag_service: FeatureFlagService,
        statement_type_registry: StatementTypeRegistry,
    ):
        self.statement_repository = statement_repository
        self.account_repository = account_repository
        self.feature_flag_service = feature_flag_service
        self.statement_type_registry = statement_type_registry
    
    async def create_statement(self, data: dict) -> StatementHistory:
        """Create a new statement with type-specific validation."""
        statement_type = data.get("statement_type")
        if not statement_type:
            raise ValueError("Statement type is required")
        
        # Check if statement type is enabled via feature flags
        if not self._is_statement_type_enabled(statement_type):
            raise FeatureFlagError(f"Statement type '{statement_type}' is not enabled")
        
        # Get the account to determine if statement type matches account type
        account_id = data.get("account_id")
        if not account_id:
            raise ValueError("Account ID is required")
        
        account = await self.account_repository.get(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")
        
        # Apply business rules based on account type and statement type
        self._validate_statement_type_for_account(account, statement_type)
        
        # Handle currency if multi-currency is enabled
        if self.feature_flag_service.is_enabled("MULTI_CURRENCY_SUPPORT_ENABLED"):
            # Use account currency if not specified
            if "currency" not in data:
                data["currency"] = account.currency
        else:
            # Default to USD if multi-currency not enabled
            data["currency"] = "USD"
        
        # Create the statement with the appropriate type
        return await self.statement_repository.create_typed_statement(
            statement_type, data
        )
    
    def _is_statement_type_enabled(self, statement_type: str) -> bool:
        """Check if a statement type is enabled via feature flags."""
        # Core banking statement types controlled by banking account types flag
        if statement_type in ["credit", "checking", "savings"]:
            return self.feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED")
        
        # Other statement types have dedicated flags
        flag_name = f"STATEMENT_TYPE_{statement_type.upper()}_ENABLED"
        return self.feature_flag_service.is_enabled(flag_name)
```

## Enhanced Statement Features

The new architecture enables several advanced statement features:

### Statement Analytics

With type-specific statement data, we can implement analytics tailored to each account type:

```python
class StatementAnalyticsService:
    """Service for analyzing statement histories."""
    
    def __init__(
        self,
        statement_repository: StatementHistoryRepository,
        feature_flag_service: FeatureFlagService,
    ):
        self.statement_repository = statement_repository
        self.feature_flag_service = feature_flag_service
    
    async def get_credit_utilization_trend(
        self, account_id: int, months: int = 6
    ) -> Dict[str, Any]:
        """
        Analyze credit utilization trend over time.
        Only applies to credit statements.
        """
        if not self.feature_flag_service.is_enabled("STATEMENT_ANALYTICS_ENABLED"):
            raise FeatureFlagError("Statement analytics feature is not enabled")
        
        # Get credit statements for the account
        statements = await self.statement_repository.get_by_account_id_and_type(
            account_id, "credit"
        )
        
        # Sort by date
        statements.sort(key=lambda s: s.statement_date)
        
        # Take the last {months} statements
        recent_statements = statements[-months:] if len(statements) > months else statements
        
        # Calculate utilization for each statement
        utilization_data = []
        for stmt in recent_statements:
            # Get the credit limit from account or credit limit history
            credit_limit = await self._get_credit_limit_for_date(
                account_id, stmt.statement_date
            )
            
            if credit_limit:
                utilization = (stmt.statement_balance / credit_limit) * 100
                utilization_data.append({
                    "date": stmt.statement_date,
                    "statement_balance": stmt.statement_balance,
                    "credit_limit": credit_limit,
                    "utilization_percentage": round(utilization, 2)
                })
        
        return {
            "account_id": account_id,
            "utilization_trend": utilization_data
        }
    
    async def get_checking_cashflow_analysis(
        self, account_id: int, months: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze checking account cashflow patterns.
        Only applies to checking statements.
        """
        if not self.feature_flag_service.is_enabled("STATEMENT_ANALYTICS_ENABLED"):
            raise FeatureFlagError("Statement analytics feature is not enabled")
        
        statements = await self.statement_repository.get_by_account_id_and_type(
            account_id, "checking"
        )
        
        # Sort by date
        statements.sort(key=lambda s: s.statement_date)
        
        # Take the last {months} statements
        recent_statements = statements[-months:] if len(statements) > months else statements
        
        cashflow_data = []
        for stmt in recent_statements:
            net_flow = (stmt.deposits_total or Decimal("0")) - (stmt.withdrawals_total or Decimal("0"))
            cashflow_data.append({
                "date": stmt.statement_date,
                "deposits": stmt.deposits_total or Decimal("0"),
                "withdrawals": stmt.withdrawals_total or Decimal("0"),
                "net_flow": net_flow,
                "fees": stmt.fees_charged or Decimal("0")
            })
        
        return {
            "account_id": account_id,
            "cashflow_analysis": cashflow_data
        }
```

### Statement Notifications

The type-specific statement structure enables targeted notifications:

```python
class StatementNotificationService:
    """Service for generating statement-related notifications."""
    
    def __init__(
        self,
        statement_repository: StatementHistoryRepository,
        feature_flag_service: FeatureFlagService,
    ):
        self.statement_repository = statement_repository
        self.feature_flag_service = feature_flag_service
    
    async def get_upcoming_payment_notifications(
        self, account_ids: List[int], days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate notifications for upcoming credit statement payments.
        Only applies to credit statements.
        """
        if not self.feature_flag_service.is_enabled("STATEMENT_NOTIFICATION_ENABLED"):
            raise FeatureFlagError("Statement notification feature is not enabled")
        
        # Get upcoming due payments
        upcoming_statements = await self.statement_repository.get_upcoming_due_payments(
            account_ids, days
        )
        
        notifications = []
        now = utc_now()
        
        for stmt in upcoming_statements:
            days_until_due = (stmt.payment_due_date - now).days
            
            notification = {
                "statement_id": stmt.id,
                "account_id": stmt.account_id,
                "account_name": await self._get_account_name(stmt.account_id),
                "due_date": stmt.payment_due_date,
                "statement_balance": stmt.statement_balance,
                "minimum_payment": stmt.minimum_payment,
                "days_until_due": days_until_due,
                "priority": "high" if days_until_due <= 3 else "medium"
            }
            
            notifications.append(notification)
        
        return notifications
```

## Error Handling Strategy

We'll implement a comprehensive error handling hierarchy for statements:

```python
class StatementError(ApplicationError):
    """Base class for statement-related errors."""
    error_code = "STATEMENT_ERROR"
    http_status = status.HTTP_400_BAD_REQUEST
    default_message = "An error occurred with the statement operation."

class StatementNotFoundError(StatementError):
    """Statement not found error."""
    error_code = "STATEMENT_NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND
    default_message = "The requested statement could not be found."

class StatementTypeError(StatementError):
    """Error related to statement types."""
    error_code = "STATEMENT_TYPE_ERROR"
    http_status = status.HTTP_400_BAD_REQUEST
    default_message = "Invalid statement type specified."

class StatementValidationError(StatementError):
    """Validation error for statement operations."""
    error_code = "STATEMENT_VALIDATION_ERROR"
    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = "The statement data failed validation."

class StatementTypeNotEnabledError(StatementError):
    """Error when a statement type is not enabled by feature flags."""
    error_code = "STATEMENT_TYPE_NOT_ENABLED"
    http_status = status.HTTP_403_FORBIDDEN
    default_message = "The requested statement type is not currently enabled."

# Type-specific errors
class CreditStatementError(StatementError):
    """Base class for credit statement errors."""
    error_code = "CREDIT_STATEMENT_ERROR"
    default_message = "An error occurred with the credit statement operation."

class PaymentDueDateError(CreditStatementError):
    """Payment due date validation error."""
    error_code = "PAYMENT_DUE_DATE_ERROR"
    default_message = "The payment due date is invalid."

class MinimumPaymentError(CreditStatementError):
    """Minimum payment validation error."""
    error_code = "MINIMUM_PAYMENT_ERROR"
    default_message = "The minimum payment amount is invalid."
```

### Error Translation Layer

To ensure consistent error handling across layers:

```python
class ErrorTranslator:
    """Translates internal errors to standardized API responses."""
    
    @staticmethod
    def translate_statement_error(error: Exception) -> ErrorResponse:
        """Translate statement errors to standardized API responses."""
        if isinstance(error, StatementError):
            # Already a structured error, just return it
            return ErrorResponse(
                code=error.error_code,
                message=str(error),
                details=getattr(error, "details", None)
            )
        
        # Translate validation errors
        if isinstance(error, ValidationError):
            return ErrorResponse(
                code="STATEMENT_VALIDATION_ERROR",
                message="The statement data failed validation.",
                details=str(error)
            )
        
        # Translate SQLAlchemy errors
        if isinstance(error, SQLAlchemyError):
            return ErrorResponse(
                code="DATABASE_ERROR",
                message="A database error occurred while processing the statement.",
                details=str(error)
            )
        
        # Fallback for unknown errors
        return ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred while processing the statement.",
            details=str(error) if settings.DEBUG else None
        )
```

## Cross-Component Impact Analysis

The statement type expansion affects several other components:

### Impact on Cashflow Analysis

Cashflow analysis must be updated to handle different statement types:

```python
class ForecastService:
    """Service for forecast analysis across accounts."""
    
    # ... existing code ...
    
    async def include_upcoming_statements(self, forecast: CashflowForecast) -> None:
        """Include upcoming statement payments in cashflow forecast."""
        forecast_repository = await self.forecast_repository
        statement_repository = await self._get_repository(StatementRepository)
        account_repository = await self._get_repository(AccountRepository)
        
        credit_accounts = await account_repository.get_by_type("credit")
        account_ids = [acc.id for acc in credit_accounts]
        
        # Get upcoming credit statement payments
        upcoming_statements = await statement_repository.get_upcoming_due_payments(
            account_ids, forecast.days
        )
        
        # Add each payment to the forecast
        for stmt in upcoming_statements:
            # Use minimum payment or statement balance based on user preferences
            payment_amount = stmt.minimum_payment
            if self.user_preferences.get("use_statement_balance", False):
                payment_amount = stmt.statement_balance
            
            forecast.add_outflow(
                amount=payment_amount,
                date=stmt.payment_due_date,
                category="Credit Payment",
                description=f"Payment for {stmt.account.name}",
                account_id=stmt.account_id,
                source_id=stmt.id,
                source_type="statement"
            )
```

### Impact on Payments

The payment system needs to connect to the correct statement type:

```python
class PaymentService:
    """Service for processing payments."""
    
    # ... existing code ...
    
    async def apply_payment_to_statement(
        self, payment_id: int, statement_id: int
    ) -> None:
        """Apply a payment to a statement."""
        payment = await self.payment_repository.get(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment with ID {payment_id} not found")
        
        statement = await self.statement_repository.get_with_type(statement_id)
        if not statement:
            raise StatementNotFoundError(f"Statement with ID {statement_id} not found")
        
        # Different logic based on statement type
        if statement.statement_type == "credit":
            # For credit statements, mark as paid if payment >= minimum_payment
            if payment.amount >= statement.minimum_payment:
                await self.statement_repository.mark_statement_paid(
                    statement_id, payment.amount
                )
            else:
                # Partial payment
                await self.statement_repository.update_typed_statement(
                    statement_id, "credit", {"payments_made": payment.amount}
                )
        elif statement.statement_type == "loan":
            # Loan payment logic
            pass
        # Other statement type handling...
```

### Impact on Recommendations

The recommendation system can use statement data for tailored advice:

```python
class RecommendationService:
    """Service for generating financial recommendations."""
    
    # ... existing code ...
    
    async def get_credit_recommendations(self, account_id: int) -> List[Recommendation]:
        """Generate credit-specific recommendations based on statement history."""
        statements = await self.statement_repository.get_by_account_id_and_type(
            account_id, "credit"
        )
        
        recommendations = []
        
        # Check for consistently high balances
        high_balance_count = sum(
            1 for s in statements 
            if s.statement_balance > Decimal("0.7") * await self._get_credit_limit(account_id)
        )
        
        if high_balance_count >= 3 and len(statements) >= 3:
            recommendations.append(
                Recommendation(
                    type="credit_utilization",
                    title="High Credit Utilization",
                    description="Your credit utilization has been consistently high. " 
                               "Consider reducing your balance to improve your credit score.",
                    impact_score=8,
                    actionable=True
                )
            )
        
        # Check for minimum payments only
        min_payment_count = sum(
            1 for s in statements
            if s.payments_made and s.payments_made <= s.minimum_payment * Decimal("1.1")
        )
        
        if min_payment_count >= 3 and len(statements) >= 3:
            recommendations.append(
                Recommendation(
                    type="minimum_payments",
                    title="Paying Only Minimums",
                    description="You've been making only minimum payments. "
                               "This will result in significant interest charges over time.",
                    impact_score=9,
                    actionable=True
                )
            )
        
        return recommendations
```

## Testing Strategy

### Testing Directory Structure

Following the project's "mirror structure" pattern:

```
tests/
  unit/
    schemas/
      statement_types/
        banking/
          test_credit_statement_schemas.py
          test_checking_statement_schemas.py
          test_savings_statement_schemas.py
    models/
      statement_types/
        banking/
          test_credit_statement_models.py
          test_checking_statement_models.py
          test_savings_statement_models.py
    repositories/
      statement_types/
        banking/
          test_credit_statement_repository.py
          test_checking_statement_repository.py
          test_savings_statement_repository.py
  integration/
    services/
      test_statement_service.py
      test_statement_analytics_service.py
      test_statement_notification_service.py
```

### Statement Schema Test Example

```python
class TestCreditStatementSchema:
    """Tests for credit statement schemas."""
    
    def test_credit_statement_create_valid(self):
        """Test creating a valid credit statement."""
        statement_date = utc_now()
        due_date = add_days(statement_date, 21)
        
        statement = CreditStatementCreate(
            account_id=1,
            statement_type="credit",
            statement_date=statement_date,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("25.00"),
            payment_due_date=due_date,
            interest_charged=Decimal("12.50"),
            fees_charged=Decimal("0.00"),
            is_paid=False
        )

        assert statement.account_id == 1
        assert statement.statement_type == "credit"
        assert statement.statement_date == statement_date
        assert statement.statement_balance == Decimal("1000.00")
        assert statement.minimum_payment == Decimal("25.00")
        assert statement.payment_due_date == due_date
        assert statement.interest_charged == Decimal("12.50")
        assert statement.fees_charged == Decimal("0.00")
        assert statement.is_paid is False
    
    def test_credit_statement_minimum_payment_validation(self):
        """Test validation of minimum payment in credit statements."""
        statement_date = utc_now()
        due_date = add_days(statement_date, 21)
        
        # Test minimum payment > statement balance
        with pytest.raises(ValidationError) as exc_info:
            CreditStatementCreate(
                account_id=1,
                statement_type="credit",
                statement_date=statement_date,
                statement_balance=Decimal("1000.00"),
                minimum_payment=Decimal("1100.00"),
                payment_due_date=due_date
            )
        assert "Minimum payment cannot exceed statement balance" in str(exc_info.value)
        
        # Valid minimum payment
        statement = CreditStatementCreate(
            account_id=1,
            statement_type="credit",
            statement_date=statement_date,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("25.00"),
            payment_due_date=due_date
        )
        assert statement.minimum_payment == Decimal("25.00")
    
    def test_credit_statement_due_date_validation(self):
        """Test validation of due date in credit statements."""
        statement_date = utc_now()
        past_date = days_ago(10)  # 10 days before now
        
        # Test due date before statement date
        with pytest.raises(ValidationError) as exc_info:
            CreditStatementCreate(
                account_id=1,
                statement_type="credit",
                statement_date=statement_date,
                statement_balance=Decimal("1000.00"),
                minimum_payment=Decimal("25.00"),
                payment_due_date=past_date
            )
        assert "Payment due date cannot be before statement date" in str(exc_info.value)
        
        # Valid due date
        future_date = add_days(statement_date, 21)
        statement = CreditStatementCreate(
            account_id=1,
            statement_type="credit",
            statement_date=statement_date,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("25.00"),
            payment_due_date=future_date
        )
        assert statement.payment_due_date == future_date
```

### Statement Repository Test Example

```python
class TestCreditStatementRepository:
    """Tests for credit statement repository."""
    
    @pytest_asyncio.fixture
    async def credit_account(self, db_session) -> CreditAccount:
        """Create a test credit account."""
        account = CreditAccount(
            name="Test Credit Card",
            account_type="credit",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("4000.00"),
            credit_limit=Decimal("5000.00"),
            statement_balance=Decimal("1000.00"),
            statement_due_date=add_days(utc_now(), 21),
            minimum_payment=Decimal("25.00")
        )
        db_session.add(account)
        await db_session.flush()
        return account
    
    @pytest_asyncio.fixture
    async def credit_statement(self, db_session, credit_account) -> CreditStatement:
        """Create a test credit statement."""
        statement = CreditStatement(
            account_id=credit_account.id,
            statement_type="credit",
            statement_date=utc_now(),
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("25.00"),
            payment_due_date=add_days(utc_now(), 21),
            interest_charged=Decimal("12.50"),
            fees_charged=Decimal("0.00"),
            is_paid=False
        )
        db_session.add(statement)
        await db_session.flush()
        return statement
    
    async def test_get_credit_statement_with_type(
        self, db_session, credit_statement, statement_type_registry
    ):
        """Test getting a credit statement with type-specific data."""
        repo = StatementHistoryRepository(db_session, statement_type_registry)
        
        # Get statement with type
        statement = await repo.get_with_type(credit_statement.id)
        
        # Verify it's a credit statement
        assert isinstance(statement, CreditStatement)
        assert statement.statement_type == "credit"
        assert statement.minimum_payment == credit_statement.minimum_payment
        assert statement.payment_due_date == credit_statement.payment_due_date
    
    async def test_get_upcoming_due_payments(
        self, db_session, credit_account, credit_statement, statement_type_registry
    ):
        """Test getting upcoming due payments for credit statements."""
        repo = StatementHistoryRepository(db_session, statement_type_registry)
        
        # Get upcoming due payments
        statements = await repo.get_upcoming_due_payments([credit_account.id], 30)
        
        # Verify we got the statement
        assert len(statements) == 1
        assert statements[0].id == credit_statement.id
        assert statements[0].account_id == credit_account.id
        assert statements[0].payment_due_date == credit_statement.payment_due_date
    
    async def test_mark_statement_paid(
        self, db_session, credit_statement, statement_type_registry
    ):
        """Test marking a credit statement as paid."""
        repo = StatementHistoryRepository(db_session, statement_type_registry)
        
        # Mark statement as paid
        paid_statement = await repo.mark_statement_paid(
            credit_statement.id, Decimal("1000.00")
        )
        
        # Verify it's marked as paid
        assert paid_statement.is_paid is True
        assert paid_statement.payments_made == Decimal("1000.00")
        
        # Verify it's updated in the database
        updated_statement = await repo.get_with_type(credit_statement.id)
        assert updated_statement.is_paid is True
        assert updated_statement.payments_made == Decimal("1000.00")
```

## International Statement Support

We'll extend the statement types to handle international formats:

```python
class InternationalStatementMixin:
    """Mixin for international statement fields."""
    
    currency: str = Field(
        "USD", min_length=3, max_length=3, 
        description="ISO 4217 currency code (e.g., USD, EUR, GBP)"
    )
    exchange_rate: Optional[PercentageDecimal] = Field(
        default=None,
        description="Exchange rate used for conversion if statement is in foreign currency"
    )
    local_amount: Optional[MoneyDecimal] = Field(
        default=None,
        description="Amount in local currency if different from statement currency"
    )
    
    @model_validator(mode="after")
    def validate_international_fields(self):
        """Validate international statement fields."""
        if self.currency != "USD":
            # If non-USD currency, should have exchange rate
            if (hasattr(self, 'exchange_rate') and 
                self.exchange_rate is not None and 
                hasattr(self, 'local_amount') and 
                self.local_amount is not None):
                # Has required fields
                pass
            else:
                # Missing required fields
                raise ValueError(
                    "Foreign currency statements must include exchange_rate and local_amount"
                )
        return self

class InternationalCreditStatementCreate(InternationalStatementMixin, CreditStatementCreate):
    """Credit statement schema with international support."""
    pass
```

## Validation Update Process

We'll establish a clear process for adding new statement types:

```python
# Validation update template for new statement types
def register_statement_type(
    registry: StatementTypeRegistry,
    type_id: str,
    model_class: Type,
    schema_class: Type,
    repository_module: str,
    name: str,
    description: str,
    category: str
):
    """Register a new statement type in the registry."""
    # 1. Register the statement type
    registry.register(
        statement_type_id=type_id,
        model_class=model_class,
        schema_class=schema_class,
        repository_module=repository_module,
        name=name,
        description=description,
        category=category
    )
    
    # 2. Create a feature flag for the statement type
    feature_flag_service = get_feature_flag_service()
    flag_name = f"STATEMENT_TYPE_{type_id.upper()}_ENABLED"
    feature_flag_service.register_flag(
        flag_name=flag_name,
        flag_type="boolean",
        default_value=False,
        description=f"Enable {name} statement type"
    )
    
    # 3. Create test fixtures for the statement type
    _create_test_fixtures(type_id, model_class, schema_class)
    
    # 4. Create schema factory for the statement type
    _create_schema_factory(type_id, schema_class)
    
    # 5. Log the registration
    logger.info(f"Registered statement type: {type_id} ({name}) in category {category}")
```

## Implementation Plan

We recommend implementing this design in the following phases:

### Phase 1: Core Architecture (This ADR-025)
- [x] Define the polymorphic model structure
- [x] Establish statement type definitions and relationships
- [x] Create base schema architecture
- [x] Define repository module pattern integration
- [x] Plan feature flag integration
- [x] Define schema factory pattern integration
- [x] Create international support architecture
- [x] Define error handling strategy
- [x] Analyze cross-component impact
- [x] Create testing strategy

### Phase 2: Banking Statement Types
- [ ] Implement credit, checking, and savings statement models
- [ ] Implement type-specific schema classes with validation
- [ ] Create repository modules for each statement type
- [ ] Implement statement type registry
- [ ] Set up feature flags for banking statement types
- [ ] Create schema factories for each statement type
- [ ] Implement service-layer business rules
- [ ] Update unit tests for all components
- [ ] Fix existing test failures

### Phase 3: Analytics and Notifications
- [ ] Implement statement analytics service
- [ ] Create notification service for statements
- [ ] Integrate with cashflow analysis
- [ ] Implement payment processing for statements
- [ ] Update recommendation system
- [ ] Create tests for all new features

### Phase 4: API Integration
- [ ] Update API endpoints for polymorphic statements
- [ ] Implement error translation layer
- [ ] Create OpenAPI documentation
- [ ] Implement API tests

### Phase 5: Additional Statement Types
- [ ] Implement loan statement types
- [ ] Implement investment statement types
- [ ] Create repository modules for new types
- [ ] Add feature flags for new types
- [ ] Create schema factories for new types
- [ ] Update tests for new types

## Risk Assessment and Mitigation

### Identified Risks

1. **Query Performance Degradation**
   - **Risk**: Polymorphic queries may be slower than single-table queries
   - **Impact**: High (affects overall application performance)
   - **Probability**: Medium
   - **Mitigation**: 
     - Implement selective loading strategy to only load type-specific data when needed
     - Add proper indexes on discriminator column and frequently queried fields
     - Use query optimization techniques like eager loading for specific scenarios
     - Implement query caching for frequently accessed statement data

2. **Data Consistency Issues**
   - **Risk**: Type-specific validation rules could lead to inconsistent data across statement types
   - **Impact**: High (affects data integrity)
   - **Probability**: Low
   - **Mitigation**:
     - Implement comprehensive service-layer validation
     - Ensure database constraints mirror business rules
     - Create automated tests that verify cross-statement consistency
     - Implement data audit and repair tools

3. **Maintenance Overhead**
   - **Risk**: Adding new statement types requires changes to multiple components
   - **Impact**: Medium (affects development velocity)
   - **Probability**: High
   - **Mitigation**:
     - Create clear documentation for adding new statement types
     - Implement helper utilities for registering new types
     - Use code generation for repetitive aspects
     - Create comprehensive test templates for new types

4. **Feature Flag Complexity**
   - **Risk**: Complex dependencies between feature flags could lead to unexpected behavior
   - **Impact**: Medium (affects feature rollout)
   - **Probability**: Medium
   - **Mitigation**:
     - Clearly document feature flag dependencies
     - Implement validation of feature flag combinations
     - Create automated tests for different feature flag states
     - Add monitoring for feature flag configuration

5. **Migration Disruption**
   - **Risk**: Schema changes could cause downtime or data issues
   - **Impact**: High (affects user experience)
   - **Probability**: Low
   - **Mitigation**:
     - Complete database refresh avoids migration complexities
     - Use feature flags to control rollout
     - Implement proper validation before and after database changes
     - Create comprehensive test suite for all data operations

## Performance Benchmarking Methodology

To validate the performance characteristics of the new architecture, we will implement the following benchmarking approach:

### Benchmark Test Cases

1. **Single Statement Retrieval**
   - **Test**: Retrieve a single statement by ID with type-specific data
   - **Variables**: Statement type (credit, checking, savings)
   - **Method**: `repository.get_with_type(id)`
   - **Target**: < 10ms
   - **Measurement**: Average of 100 executions excluding outliers

2. **Account Statement List**
   - **Test**: Retrieve all statements for an account
   - **Variables**: Number of statements (5, 15, 30), statement types (mixed)
   - **Method**: `repository.get_by_account_id(account_id)`
   - **Target**: < 30ms for 15 statements
   - **Measurement**: Linear scaling factor with statement count

3. **Statement Creation**
   - **Test**: Create a new statement with type-specific validation
   - **Variables**: Statement type (credit, checking, savings)
   - **Method**: `service.create_statement(data)`
   - **Target**: < 50ms
   - **Measurement**: Average of 50 executions including validation

4. **Type-Specific Queries**
   - **Test**: Execute type-specific repository methods
   - **Variables**: Method type, result set size
   - **Method**: Various type-specific methods
   - **Target**: < 20ms for standard queries
   - **Measurement**: Average of 50 executions per method

### Benchmarking Infrastructure

1. **Testing Environment**
   - Dedicated test database with controlled dataset
   - Isolated service instances for consistent measurement
   - Automated execution to eliminate manual timing variation

2. **Measurement Tools**
   - Custom benchmarking decorator for method timing
   - Statistical analysis for identifying performance patterns
   - Comparison against baseline single-table implementation

3. **Reporting**
   - Detailed performance reports broken down by operation type
   - Trend analysis across different dataset sizes
   - Identification of optimization opportunities

### Performance Optimization Strategy

1. **Index Optimization**
   - Add targeted indexes for common query patterns
   - Analyze query plans using EXPLAIN to identify inefficiencies
   - Implement compound indexes for multi-field query conditions

2. **Query Optimization**
   - Use query-specific loading strategies (with_polymorphic vs. direct subclass queries)
   - Implement result pagination for large datasets
   - Use strategic caching for frequently accessed data

3. **Database Optimization**
   - Configure proper connection pooling parameters
   - Optimize transaction boundaries for critical operations
   - Use database-specific features for improved performance

## Rollback Plan

In case of implementation issues, we will follow this rollback procedure:

### Rollback Triggers

1. **Performance Degradation**: If statement operations exceed 2x the target response times
2. **Data Integrity Issues**: If validation fails or data inconsistencies are detected
3. **API Compatibility Problems**: If existing API clients break or report errors
4. **Functionality Regression**: If key features no longer work correctly

### Rollback Procedure

1. **Stage 1: Feature Flag Deactivation**
   - Disable the feature flags for new statement types
   - Revert to using only the base statement type for all operations
   - Monitor error rates and performance metrics

2. **Stage 2: Schema Reversal**
   - Execute database reset to remove the polymorphic tables
   - Deploy previous version of statement models and schemas
   - Update repository layer to use the previous implementation

3. **Stage 3: Code Reversion**
   - Revert codebase to the pre-implementation state
   - Update all references to statement types
   - Deploy the reverted code to all environments

4. **Stage 4: Verification**
   - Run comprehensive test suite against the reverted system
   - Validate that all previous functionality works correctly
   - Ensure all performance metrics return to baseline

### Post-Rollback Analysis

After completing the rollback, we will conduct a thorough analysis:

1. Identify the specific causes of implementation failure
2. Document lessons learned and architectural insights
3. Create a revised implementation plan with identified issues addressed
4. Update risk assessment with newly discovered risks

## Monitoring Strategy

To measure the success of this implementation and detect issues early, we will implement the following monitoring approach:

### Key Performance Indicators (KPIs)

1. **Operation Timing**
   - Statement retrieval time by type
   - Statement creation time by type
   - Type-specific operation timing
   - Overall statement API response times

2. **Error Rates**
   - Validation errors by statement type
   - Repository exceptions
   - API error responses
   - Feature flag-related errors

3. **Data Quality**
   - Statement data consistency across types
   - Cross-reference validation
   - Field validation success rates
   - Type-specific constraint violations

4. **Usage Metrics**
   - Statement type distribution
   - API endpoint usage by statement type
   - Feature flag configuration states
   - Statement operation frequency

### Monitoring Implementation

1. **Application Instrumentation**
   - Add timing metrics to all statement operations
   - Implement detailed error logging with context
   - Create health check endpoints for statement functionality
   - Add tracing for cross-service statement operations

2. **Alerting Rules**
   - Set up alerts for slow statement operations (> 2x normal)
   - Configure error rate thresholds for automatic notification
   - Add data consistency check alerts
   - Implement feature flag configuration monitoring

3. **Dashboards**
   - Create statement performance dashboard
   - Implement type distribution visualization
   - Add error rate tracking and trending
   - Develop feature flag status overview

4. **Regular Auditing**
   - Weekly performance review for statement operations
   - Monthly data quality audit across statement types
   - Quarterly optimization analysis
   - Automated daily consistency checks

## Stakeholder Impact Analysis

### Backend Development Team

- **Impact**: High (architectural pattern to learn and implement)
- **Benefits**: Cleaner code organization, better separation of concerns, more maintainable codebase
- **Challenges**: Learning curve for polymorphic patterns, more complex repository layer
- **Support Needed**: Documentation, code examples, pair programming sessions

### QA/Testing Team

- **Impact**: Medium (new test patterns, more comprehensive test scenarios)
- **Benefits**: Structured test organization, clearer test boundaries, more focused test cases
- **Challenges**: Testing polymorphic behavior, feature flag interaction testing, performance validation
- **Support Needed**: Test fixtures, test case templates, documentation on statement validation

### Database Administrators

- **Impact**: Medium (new table structure, index optimization)
- **Benefits**: Better data organization, clearer field semantics, improved data integrity
- **Challenges**: More complex queries, index optimization, understanding polymorphic joins
- **Support Needed**: Database schema documentation, query patterns, index recommendations

### Operations Team

- **Impact**: Low (monitoring new components)
- **Benefits**: Better visibility into statement operations, clearer error context
- **Challenges**: Understanding performance characteristics, troubleshooting polymorphic issues
- **Support Needed**: Monitoring documentation, alert guidelines, troubleshooting playbooks

### API Consumers

- **Impact**: Low (implementation details hidden behind API)
- **Benefits**: More consistent validation, clearer error messages, type-specific features
- **Challenges**: Understanding statement type requirements, handling type-specific fields
- **Support Needed**: API documentation updates, examples for each statement type

## Implementation Checklist

### Phase 1: Core Architecture
- [ ] Create StatementHistory base model with polymorphic identity
- [ ] Create CreditStatement, CheckingStatement, and SavingsStatement models
- [ ] Update database schema for polymorphic statement storage
- [ ] Implement statement type registry
- [ ] Create base schema structure with proper field alignment
- [ ] Implement CreditStatementCreate and related schemas
- [ ] Create repository module pattern infrastructure
- [ ] Set up feature flag registration for statement types
- [ ] Implement statement schema factories

### Phase 2: Banking Statement Types
- [ ] Implement statement_types/banking/credit_statement.py repository module
- [ ] Implement statement_types/banking/checking_statement.py repository module
- [ ] Implement statement_types/banking/savings_statement.py repository module
- [ ] Create StatementHistoryRepository with dynamic module loading
- [ ] Implement StatementService with type-specific business rules
- [ ] Create test fixtures for each statement type
- [ ] Update API endpoint handlers for polymorphic types
- [ ] Fix existing statement test failures
- [ ] Create unit tests for all new components

## Expected Benefits

1. **Clean Separation of Concerns**: Each statement type has its own model and schema
2. **Type Safety**: The polymorphic design ensures type-specific operations are validated
3. **Extensibility**: New statement types can be added by creating new models
4. **Feature Control**: Statement types can be enabled/disabled via feature flags
5. **Improved Testing**: Each statement type can be tested independently
6. **Enhanced Analytics**: Type-specific statement data enables better financial insights
7. **International Support**: Multi-currency statements with proper exchange rate handling
8. **Notification System**: Statement-specific notification rules for better user experience
9. **Better Error Handling**: Structured error hierarchy with proper layer translation
10. **Component Integration**: Proper connections to cashflow, payments, and recommendations

## Alternatives Considered

1. **Extend the current approach**: Continue with a single-table design and use validation
   - Pros: Simpler structure, less migration effort
   - Cons: Increasingly complex validation logic, poor separation of concerns

2. **Separate tables for each statement type**: Create entirely separate models without inheritance
   - Pros: Full separation of concerns, simplified queries
   - Cons: Duplication of common fields and logic, harder to maintain

3. **EAV (Entity-Attribute-Value) pattern**: Store type-specific attributes in a separate table
   - Pros: High flexibility for new statement types
   - Cons: Complex queries, poor performance, difficult validation

4. **JSON fields for type-specific data**: Store common fields in base table, type-specific in JSON
   - Pros: Flexible schema without multiple tables
   - Cons: Poor validation, complex queries, difficult indexing

## References

- [ADR-016: Account Type Expansion](../../adr/backend/016-account-type-expansion.md)
- [ADR-011: DateTime Standardization](../../adr/backend/011-datetime-standardization.md)
- [ADR-012: Validation Architecture](../../adr/backend/012-validation-architecture.md)
- [SQLAlchemy Joined Table Inheritance](https://docs.sqlalchemy.org/en/14/orm/inheritance.html#joined-table-inheritance)
- [Pydantic Discriminated Unions](https://docs.pydantic.dev/latest/usage/types/#discriminated-unions-aka-tagged-unions)
