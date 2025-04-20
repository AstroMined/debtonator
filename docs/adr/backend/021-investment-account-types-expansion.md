# ADR-021: Investment Account Types Expansion

## Status

Accepted

## Executive Summary

Extends the polymorphic account architecture established in ADR-016 by implementing specialized investment account types (brokerage, retirement, HSA, cryptocurrency) with a shared base InvestmentAccount class. This expansion introduces a sophisticated investment holdings model to track portfolio composition, performance metrics, and account-specific attributes across diverse investment vehicles. The implementation provides comprehensive support for investment-specific features including contribution tracking, tax-advantaged account management, health expense management, and cryptocurrency tracking, with specialized portfolio visualization and analysis tools, enhancing Debtonator's ability to offer users a complete financial picture that includes their investment assets and strategies.

## Context

Following ADR-016 (Account Type Expansion) and building upon the implementation of banking account types (ADR-019) and loan account types (ADR-020), we need to address a critical gap in our financial account tracking capabilities: investment accounts. Investment accounts represent a significant portion of users' financial assets and are essential for comprehensive financial planning and net worth tracking.

The current limitations in our system include:

1. Inability to track investment accounts such as brokerage accounts, retirement accounts, and specialized tax-advantaged accounts
2. No support for investment-specific attributes like tax advantages, contribution limits, and portfolio composition
3. Missing representation of HSA (Health Savings Account) accounts which serve dual purposes as health expenditure and investment vehicles
4. Lack of cryptocurrency tracking despite increasing adoption among users

These limitations prevent Debtonator from providing a complete financial picture for users with investments and limit our ability to offer holistic financial insights and planning tools.

## Decision

We will implement the following investment account types as part of the polymorphic inheritance structure defined in ADR-016:

1. **Brokerage Account**: General investment accounts for stocks, bonds, ETFs, etc.
2. **Retirement Account**: Tax-advantaged retirement accounts (401(k), IRA, Roth IRA, etc.)
3. **HSA Account**: Health Savings Accounts with dual health spending and investment capabilities
4. **Crypto Account**: Cryptocurrency wallets and exchange accounts

Each account type will have specialized attributes and business logic to accurately represent its unique characteristics while supporting Debtonator's financial tracking and analysis features.

## Technical Details

### Type-Specific Models

We will implement the following SQLAlchemy models for investment account types:

#### Base Investment Account

Similar to our approach with loan accounts in ADR-020, we'll create a base investment account class to capture common investment attributes:

```python
class InvestmentAccount(Account):
    """Base class for all investment account types"""
    __tablename__ = "investment_accounts"
    
    id = Column(Integer, ForeignKey("accounts.id"), primary_key=True)
    cash_balance = Column(Numeric(12, 4), nullable=False, default=0)
    investment_balance = Column(Numeric(12, 4), nullable=False, default=0)
    tax_advantaged = Column(Boolean, default=False, nullable=False)
    last_updated = Column(DateTime(timezone=True), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "investment",
    }
    
    @hybrid_property
    def total_balance(self):
        """Total account balance including cash and investments"""
        return self.cash_balance + self.investment_balance
```

#### Brokerage Account

```python
class BrokerageAccount(InvestmentAccount):
    """Standard taxable brokerage accounts"""
    __tablename__ = "brokerage_accounts"
    
    id = Column(Integer, ForeignKey("investment_accounts.id"), primary_key=True)
    margin_enabled = Column(Boolean, default=False, nullable=False)
    margin_balance = Column(Numeric(12, 4), nullable=True)
    dividend_reinvestment = Column(Boolean, default=False, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "brokerage",
    }
```

#### Retirement Account

```python
class RetirementAccount(InvestmentAccount):
    """Tax-advantaged retirement accounts"""
    __tablename__ = "retirement_accounts"
    
    id = Column(Integer, ForeignKey("investment_accounts.id"), primary_key=True)
    retirement_type = Column(String, nullable=False)  # 401k, IRA, Roth IRA, etc.
    contribution_limit = Column(Numeric(12, 4), nullable=True)
    ytd_contributions = Column(Numeric(12, 4), nullable=False, default=0)
    employer_match_percent = Column(Numeric(6, 4), nullable=True)
    vested_percentage = Column(Numeric(6, 4), nullable=True, default=100)
    early_withdrawal_penalty = Column(Numeric(6, 4), nullable=True)
    required_minimum_distribution = Column(Boolean, default=False, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "retirement",
    }
```

#### HSA Account

```python
class HSAAccount(InvestmentAccount):
    """Health Savings Accounts"""
    __tablename__ = "hsa_accounts"
    
    id = Column(Integer, ForeignKey("investment_accounts.id"), primary_key=True)
    annual_contribution_limit = Column(Numeric(12, 4), nullable=True)
    ytd_contributions = Column(Numeric(12, 4), nullable=False, default=0)
    coverage_type = Column(String, nullable=False, default="individual")  # individual or family
    investment_threshold = Column(Numeric(12, 4), nullable=True)  # Min cash before investing
    linked_health_plan = Column(String, nullable=True)
    debit_card_last_four = Column(String, nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "hsa",
    }
```

#### Crypto Account

```python
class CryptoAccount(InvestmentAccount):
    """Cryptocurrency accounts"""
    __tablename__ = "crypto_accounts"
    
    id = Column(Integer, ForeignKey("investment_accounts.id"), primary_key=True)
    wallet_type = Column(String, nullable=False)  # exchange, hardware, software, etc.
    wallet_address = Column(String, nullable=True)  # Public address or identifier
    platform = Column(String, nullable=True)  # Exchange or service name
    supports_staking = Column(Boolean, default=False, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "crypto",
    }
```

### Investment Holdings Model

To represent the contents of investment accounts, we'll create a separate model for investment holdings:

```python
class InvestmentHolding(Base):
    """Holdings within investment accounts"""
    __tablename__ = "investment_holdings"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("investment_accounts.id"), nullable=False)
    ticker_symbol = Column(String, nullable=True)  # Stock/ETF symbol or crypto ticker
    asset_name = Column(String, nullable=False)  # Human-readable name
    asset_type = Column(String, nullable=False)  # stock, bond, etf, mutual_fund, crypto, etc.
    quantity = Column(Numeric(18, 8), nullable=False)  # Higher precision for crypto
    cost_basis = Column(Numeric(12, 4), nullable=True)
    current_price = Column(Numeric(18, 8), nullable=True)
    current_value = Column(Numeric(12, 4), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    account = relationship("InvestmentAccount", back_populates="holdings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('account_id', 'ticker_symbol', name='unique_holding_per_account'),
    )
```

We'll update the InvestmentAccount model to include a relationship:

```python
# Add to InvestmentAccount class
holdings = relationship("InvestmentHolding", back_populates="account", cascade="all, delete-orphan")
```

### Pydantic Schema Implementation

Following the pattern established in previous ADRs, we'll create Pydantic schemas for each investment account type:

#### Base Investment Schema

```python
class InvestmentAccountBase(AccountBase):
    """Base schema for all investment accounts"""
    cash_balance: MoneyDecimal = Decimal("0")
    investment_balance: MoneyDecimal = Decimal("0")
    tax_advantaged: bool = False
    
    @field_validator("cash_balance", "investment_balance")
    @classmethod
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v

class InvestmentAccountCreate(InvestmentAccountBase, AccountCreate):
    """Base create schema for investment accounts"""
    pass

class InvestmentAccountResponse(InvestmentAccountBase, AccountResponse):
    """Base response schema for investment accounts"""
    last_updated: datetime
    total_balance: MoneyDecimal
```

#### Investment Holding Schema

```python
class InvestmentHoldingBase(BaseModel):
    """Base schema for investment holdings"""
    ticker_symbol: Optional[str] = None
    asset_name: str
    asset_type: str
    quantity: Decimal
    cost_basis: Optional[MoneyDecimal] = None
    current_price: Optional[Decimal] = None
    current_value: Optional[MoneyDecimal] = None
    
    @field_validator("asset_type")
    @classmethod
    def validate_asset_type(cls, v):
        allowed_types = ["stock", "bond", "etf", "mutual_fund", "crypto", "other"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Asset type must be one of: {', '.join(allowed_types)}")
        return v.lower()
    
    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v

class InvestmentHoldingCreate(InvestmentHoldingBase):
    """Create schema for investment holdings"""
    pass

class InvestmentHoldingResponse(InvestmentHoldingBase):
    """Response schema for investment holdings"""
    id: int
    account_id: int
    last_updated: datetime
```

#### Type-Specific Schemas

For each investment account type, we'll create corresponding Create and Response schemas. Here's an example for the Retirement account type:

```python
class RetirementAccountCreate(InvestmentAccountCreate):
    """Create schema for retirement accounts"""
    account_type: Literal["retirement"]
    retirement_type: str
    contribution_limit: Optional[MoneyDecimal] = None
    ytd_contributions: MoneyDecimal = Decimal("0")
    employer_match_percent: Optional[PercentageDecimal] = None
    vested_percentage: PercentageDecimal = Decimal("100")
    early_withdrawal_penalty: Optional[PercentageDecimal] = None
    required_minimum_distribution: bool = False
    
    @field_validator("retirement_type")
    @classmethod
    def validate_retirement_type(cls, v):
        allowed_types = ["401k", "roth_401k", "ira", "roth_ira", "403b", "457", "sep_ira", "simple_ira", "other"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Retirement type must be one of: {', '.join(allowed_types)}")
        return v.lower()
    
    @field_validator("ytd_contributions")
    @classmethod
    def validate_contributions(cls, v, values):
        contribution_limit = values.data.get("contribution_limit")
        if contribution_limit is not None and v > contribution_limit:
            raise ValueError("Year-to-date contributions cannot exceed the contribution limit")
        return v

class RetirementAccountResponse(InvestmentAccountResponse):
    """Response schema for retirement accounts"""
    account_type: Literal["retirement"]
    retirement_type: str
    contribution_limit: Optional[MoneyDecimal] = None
    ytd_contributions: MoneyDecimal
    employer_match_percent: Optional[PercentageDecimal] = None
    vested_percentage: PercentageDecimal
    early_withdrawal_penalty: Optional[PercentageDecimal] = None
    required_minimum_distribution: bool
    holdings: Optional[List[InvestmentHoldingResponse]] = None
```

Similar schemas will be created for other investment account types with appropriate fields and validations.

### Discriminated Union for API

```python
InvestmentAccountCreateUnion = Annotated[
    Union[
        BrokerageAccountCreate,
        RetirementAccountCreate,
        HSAAccountCreate,
        CryptoAccountCreate,
    ],
    Field(discriminator="account_type")
]

InvestmentAccountResponseUnion = Annotated[
    Union[
        BrokerageAccountResponse,
        RetirementAccountResponse,
        HSAAccountResponse,
        CryptoAccountResponse,
    ],
    Field(discriminator="account_type")
]
```

### Investment Portfolio Service

To support investment-specific operations and analysis, we'll implement an InvestmentPortfolioService:

```python
class InvestmentPortfolioService:
    """Service for investment portfolio operations and analysis"""
    
    def __init__(
        self,
        account_repository: AccountRepository,
        holding_repository: InvestmentHoldingRepository
    ):
        self.account_repository = account_repository
        self.holding_repository = holding_repository
    
    def get_portfolio_summary(self, user_id: int) -> Dict:
        """Get summary of all investment accounts for a user"""
        investment_accounts = self.account_repository.get_by_user_and_types(
            user_id,
            ["brokerage", "retirement", "hsa", "crypto"]
        )
        
        # Calculate totals by account type
        brokerage_total = sum(
            a.total_balance for a in investment_accounts 
            if a.account_type == "brokerage" and not a.is_closed
        )
        retirement_total = sum(
            a.total_balance for a in investment_accounts 
            if a.account_type == "retirement" and not a.is_closed
        )
        hsa_total = sum(
            a.total_balance for a in investment_accounts 
            if a.account_type == "hsa" and not a.is_closed
        )
        crypto_total = sum(
            a.total_balance for a in investment_accounts 
            if a.account_type == "crypto" and not a.is_closed
        )
        
        # Calculate tax-advantaged vs. taxable
        tax_advantaged_total = sum(
            a.total_balance for a in investment_accounts 
            if a.tax_advantaged and not a.is_closed
        )
        taxable_total = sum(
            a.total_balance for a in investment_accounts 
            if not a.tax_advantaged and not a.is_closed
        )
        
        return {
            "total_investments": brokerage_total + retirement_total + hsa_total + crypto_total,
            "brokerage_total": brokerage_total,
            "retirement_total": retirement_total,
            "hsa_total": hsa_total,
            "crypto_total": crypto_total,
            "tax_advantaged_total": tax_advantaged_total,
            "taxable_total": taxable_total,
            "account_count": len(investment_accounts)
        }
    
    def get_asset_allocation(self, user_id: int) -> Dict:
        """Get asset allocation across all investment accounts"""
        investment_accounts = self.account_repository.get_by_user_and_types(
            user_id,
            ["brokerage", "retirement", "hsa", "crypto"]
        )
        
        # Collect all holdings from all accounts
        all_holdings = []
        for account in investment_accounts:
            if account.is_closed:
                continue
            
            account_holdings = self.holding_repository.get_by_account(account.id)
            all_holdings.extend(account_holdings)
        
        # Calculate allocation by asset type
        allocation_by_type = {}
        total_value = sum(holding.current_value or 0 for holding in all_holdings)
        
        for holding in all_holdings:
            asset_type = holding.asset_type
            value = holding.current_value or 0
            
            if asset_type not in allocation_by_type:
                allocation_by_type[asset_type] = 0
            
            allocation_by_type[asset_type] += value
        
        # Convert to percentages
        allocation_percentages = {}
        for asset_type, value in allocation_by_type.items():
            if total_value > 0:
                allocation_percentages[asset_type] = (value / total_value) * 100
            else:
                allocation_percentages[asset_type] = 0
        
        return {
            "total_value": total_value,
            "allocation_by_type": allocation_by_type,
            "allocation_percentages": allocation_percentages,
            "asset_count": len(all_holdings)
        }
    
    def calculate_retirement_projections(
        self, 
        account_id: int, 
        monthly_contribution: Decimal,
        years_to_retirement: int,
        expected_return_rate: Decimal
    ) -> Dict:
        """Calculate retirement account projections"""
        account = self.account_repository.get(account_id)
        if not account or not isinstance(account, RetirementAccount):
            raise ValueError("Account is not a retirement account")
        
        current_balance = account.total_balance
        annual_contribution = monthly_contribution * 12
        annual_return_rate = expected_return_rate / 100  # Convert percentage to decimal
        
        # Simple compound interest calculation (could be enhanced in production)
        projected_balance = current_balance
        yearly_projections = []
        
        for year in range(1, years_to_retirement + 1):
            # Add annual contribution
            projected_balance += annual_contribution
            
            # Apply annual return
            projected_balance *= (1 + annual_return_rate)
            
            yearly_projections.append({
                "year": year,
                "balance": projected_balance,
                "contributions_to_date": annual_contribution * year,
                "growth_to_date": projected_balance - current_balance - (annual_contribution * year)
            })
        
        return {
            "initial_balance": current_balance,
            "monthly_contribution": monthly_contribution,
            "annual_contribution": annual_contribution,
            "years_to_retirement": years_to_retirement,
            "expected_return_rate": expected_return_rate,
            "final_projected_balance": projected_balance,
            "total_contributions": annual_contribution * years_to_retirement,
            "total_growth": projected_balance - current_balance - (annual_contribution * years_to_retirement),
            "yearly_projections": yearly_projections
        }
    
    def check_contribution_limits(self, user_id: int) -> Dict:
        """Check contribution limits for tax-advantaged accounts"""
        retirement_accounts = self.account_repository.get_by_user_and_type(user_id, "retirement")
        hsa_accounts = self.account_repository.get_by_user_and_type(user_id, "hsa")
        
        contribution_status = []
        
        # Check retirement accounts
        for account in retirement_accounts:
            if account.is_closed or account.contribution_limit is None:
                continue
                
            remaining = account.contribution_limit - account.ytd_contributions
            percent_used = (account.ytd_contributions / account.contribution_limit * 100) if account.contribution_limit > 0 else 0
            
            contribution_status.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": "retirement",
                "retirement_type": account.retirement_type,
                "contribution_limit": account.contribution_limit,
                "ytd_contributions": account.ytd_contributions,
                "remaining": remaining,
                "percent_used": percent_used
            })
        
        # Check HSA accounts
        for account in hsa_accounts:
            if account.is_closed or account.annual_contribution_limit is None:
                continue
                
            remaining = account.annual_contribution_limit - account.ytd_contributions
            percent_used = (account.ytd_contributions / account.annual_contribution_limit * 100) if account.annual_contribution_limit > 0 else 0
            
            contribution_status.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": "hsa",
                "coverage_type": account.coverage_type,
                "contribution_limit": account.annual_contribution_limit,
                "ytd_contributions": account.ytd_contributions,
                "remaining": remaining,
                "percent_used": percent_used
            })
        
        return {
            "contribution_status": contribution_status,
            "current_year": datetime.now().year
        }
```

### Repository Layer Enhancements

We'll implement an InvestmentHoldingRepository and extend the AccountRepository with investment-specific methods:

```python
class InvestmentHoldingRepository(BaseRepository):
    """Repository for investment holdings"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.model_class = InvestmentHolding
    
    def get_by_account(self, account_id: int) -> List[InvestmentHolding]:
        """Get all holdings for an account"""
        return self.session.query(InvestmentHolding).filter(
            InvestmentHolding.account_id == account_id
        ).all()
    
    def get_by_ticker(self, account_id: int, ticker_symbol: str) -> Optional[InvestmentHolding]:
        """Get holding by ticker symbol"""
        return self.session.query(InvestmentHolding).filter(
            InvestmentHolding.account_id == account_id,
            InvestmentHolding.ticker_symbol == ticker_symbol
        ).first()
    
    def update_holding_value(
        self, account_id: int, ticker_symbol: str, current_price: Decimal
    ) -> Optional[InvestmentHolding]:
        """Update current price and value for a holding"""
        holding = self.get_by_ticker(account_id, ticker_symbol)
        if not holding:
            return None
        
        holding.current_price = current_price
        holding.current_value = holding.quantity * current_price
        holding.last_updated = datetime_utils.utc_now()
        
        self.session.commit()
        self.session.refresh(holding)
        
        return holding
    
    def update_account_balances(self, account_id: int) -> bool:
        """Update account balances based on holdings"""
        holdings = self.get_by_account(account_id)
        if not holdings:
            return False
        
        account = self.session.query(InvestmentAccount).get(account_id)
        if not account:
            return False
        
        # Calculate total investment value
        investment_balance = sum(h.current_value or 0 for h in holdings)
        
        # Update the account
        account.investment_balance = investment_balance
        account.last_updated = datetime_utils.utc_now()
        
        self.session.commit()
        return True
```

Extension to AccountRepository:

```python
class AccountRepository(BaseRepository):
    # ... existing methods from ADR-016, ADR-019, and ADR-020 ...
    
    def get_investment_accounts_by_user(self, user_id: int) -> List[InvestmentAccount]:
        """Get all investment accounts for a specific user."""
        return self.session.query(InvestmentAccount).filter(
            InvestmentAccount.user_id == user_id,
            InvestmentAccount.is_closed == False
        ).all()
    
    def get_retirement_contribution_total(self, user_id: int) -> Decimal:
        """Get total retirement contributions for the current year"""
        retirement_accounts = self.session.query(RetirementAccount).filter(
            RetirementAccount.user_id == user_id,
            RetirementAccount.is_closed == False
        ).all()
        
        return sum(account.ytd_contributions for account in retirement_accounts)
    
    def get_hsa_contribution_total(self, user_id: int) -> Decimal:
        """Get total HSA contributions for the current year"""
        hsa_accounts = self.session.query(HSAAccount).filter(
            HSAAccount.user_id == user_id,
            HSAAccount.is_closed == False
        ).all()
        
        return sum(account.ytd_contributions for account in hsa_accounts)
```

### API Layer Implementation

We will implement the following endpoints for investment account management:

```python
@router.post("/accounts/investments", response_model=InvestmentAccountResponseUnion)
def create_investment_account(
    account_data: InvestmentAccountCreateUnion,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new investment account."""
    data_dict = account_data.model_dump()
    data_dict["user_id"] = current_user.id
    data_dict["last_updated"] = datetime_utils.utc_now()
    return account_service.create_account(data_dict)

@router.get("/accounts/investments", response_model=List[InvestmentAccountResponseUnion])
def get_investment_accounts(
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get all investment accounts for the current user."""
    return account_service.get_investment_accounts(current_user.id)

@router.post("/accounts/{account_id}/holdings", response_model=InvestmentHoldingResponse)
def add_investment_holding(
    account_id: int,
    holding_data: InvestmentHoldingCreate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    holding_service: InvestmentHoldingService = Depends(get_investment_holding_service)
):
    """Add a new holding to an investment account."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify account is an investment account
    if not isinstance(account, InvestmentAccount):
        raise HTTPException(status_code=400, detail="Account is not an investment account")
    
    data_dict = holding_data.model_dump()
    data_dict["account_id"] = account_id
    data_dict["last_updated"] = datetime_utils.utc_now()
    
    # Calculate current value if price is provided
    if data_dict.get("current_price") and data_dict.get("quantity"):
        data_dict["current_value"] = data_dict["current_price"] * data_dict["quantity"]
    
    holding = holding_service.create_holding(data_dict)
    
    # Update account balances
    holding_service.update_account_balances(account_id)
    
    return holding

@router.get("/accounts/{account_id}/holdings", response_model=List[InvestmentHoldingResponse])
def get_investment_holdings(
    account_id: int,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    holding_service: InvestmentHoldingService = Depends(get_investment_holding_service)
):
    """Get all holdings for an investment account."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify account is an investment account
    if not isinstance(account, InvestmentAccount):
        raise HTTPException(status_code=400, detail="Account is not an investment account")
    
    return holding_service.get_holdings_by_account(account_id)

@router.get("/portfolio/summary", response_model=PortfolioSummaryResponse)
def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    portfolio_service: InvestmentPortfolioService = Depends(get_portfolio_service)
):
    """Get investment portfolio summary."""
    return portfolio_service.get_portfolio_summary(current_user.id)

@router.get("/portfolio/allocation", response_model=AssetAllocationResponse)
def get_asset_allocation(
    current_user: User = Depends(get_current_user),
    portfolio_service: InvestmentPortfolioService = Depends(get_portfolio_service)
):
    """Get asset allocation across all investment accounts."""
    return portfolio_service.get_asset_allocation(current_user.id)

@router.get("/accounts/retirement/{account_id}/projections", response_model=RetirementProjectionResponse)
def calculate_retirement_projections(
    account_id: int,
    monthly_contribution: Decimal = Query(..., description="Monthly contribution amount"),
    years_to_retirement: int = Query(..., description="Years until retirement"),
    expected_return_rate: Decimal = Query(7.0, description="Expected annual return rate (%)"),
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    portfolio_service: InvestmentPortfolioService = Depends(get_portfolio_service)
):
    """Calculate retirement account projections."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify account is a retirement account
    if not isinstance(account, RetirementAccount):
        raise HTTPException(status_code=400, detail="Account is not a retirement account")
    
    return portfolio_service.calculate_retirement_projections(
        account_id, 
        monthly_contribution,
        years_to_retirement,
        expected_return_rate
    )

@router.get("/accounts/contribution-limits", response_model=ContributionLimitResponse)
def check_contribution_limits(
    current_user: User = Depends(get_current_user),
    portfolio_service: InvestmentPortfolioService = Depends(get_portfolio_service)
):
    """Check contribution limits for tax-advantaged accounts."""
    return portfolio_service.check_contribution_limits(current_user.id)
```

### Account Type Registry Updates

We'll update the AccountTypeRegistry to include the new investment account types:

```python
# During application initialization
account_type_registry = AccountTypeRegistry()

# Register investment account types
account_type_registry.register(
    account_type_id="brokerage",
    model_class=BrokerageAccount,
    schema_class=BrokerageAccountCreate,
    name="Brokerage Account",
    description="Investment account for stocks, bonds, ETFs, and other securities",
    category="Investments"
)

account_type_registry.register(
    account_type_id="retirement",
    model_class=RetirementAccount,
    schema_class=RetirementAccountCreate,
    name="Retirement Account",
    description="Tax-advantaged account for retirement savings (401k, IRA, etc.)",
    category="Investments"
)

account_type_registry.register(
    account_type_id="hsa",
    model_class=HSAAccount,
    schema_class=HSAAccountCreate,
    name="Health Savings Account",
    description="Tax-advantaged account for medical expenses with investment options",
    category="Investments"
)

account_type_registry.register(
    account_type_id="crypto",
    model_class=CryptoAccount,
    schema_class=CryptoAccountCreate,
    name="Cryptocurrency Account",
    description="Digital wallet or exchange account for cryptocurrencies",
    category="Investments"
)
```

## Consequences

### Positive

1. **Comprehensive Financial Picture**: Users can track all their investments in one place, providing a more complete view of their financial situation.

2. **Tax Planning Support**: Proper tracking of tax-advantaged accounts helps users optimize contributions and tax strategies.

3. **Retirement Planning Tools**: Projection features help users understand if they're on track for retirement goals.

4. **Modern Financial Assets**: Support for cryptocurrency accounts acknowledges the evolution of personal finance.

5. **Health & Wealth Integration**: HSA support bridges the gap between health expenses and long-term investing.

### Negative

1. **Increased Schema Complexity**: The investment holdings model adds another dimension of complexity to the account structure.

2. **Data Currency Challenges**: Investment values change frequently, requiring strategies to keep data reasonably current.

3. **Performance Considerations**: Complex portfolio calculations and asset allocation analysis may impact performance for users with large portfolios.

### Neutral

1. **UI Expansion Required**: Frontend components need significant expansion to display holdings, allocation charts, and projections.

2. **Integration Points**: Investment accounts need integration with the rest of the financial picture (net worth calculations, cashflow analysis, etc.).

## Performance Impact

- **Single Account Retrieval**: < 10ms (direct ID lookup with polymorphic loading)
- **Investment Account List**: < 50ms for typical users (2-5 investment accounts)
- **Portfolio Summary**: < 100ms for portfolios with up to 50 holdings
- **Asset Allocation Calculation**: < 150ms (requires aggregation of holdings data)
- **Retirement Projections**: < 50ms (primarily math calculations)

### Optimization Strategies

To maintain performance with the complex portfolio calculations:

1. **Account Balance Denormalization**:
   - Store aggregated investment_balance and cash_balance in the account record
   - Update these totals whenever holdings change
   - This avoids summing all holdings for basic balance queries

2. **Caching Investment Data**:
   - Cache portfolio summary and asset allocation with a TTL of 24 hours
   - Invalidate cache when holdings are updated
   - Allow user-initiated refresh for up-to-date values

3. **Batch Processing**:
   - Process holdings updates in batches
   - Use background tasks for price updates
   - Leverage database transactions for consistency

4. **Indexed Queries**:
   - Index account_id in the investment_holdings table
   - Index asset_type for efficient allocation queries
   - Consider composite indices for common query patterns

## Integration with Existing Features

### Net Worth Integration

The investment account types will integrate with Debtonator's net worth calculations:

1. **Asset Classification**:
   - Investment accounts will be classified as assets
   - Margin balances will be tracked as liabilities
   - Tax treatment will be considered for accurate net worth reporting

2. **Value Aggregation**:
   - Investment balances will be included in total assets
   - Investment growth will be factored into net worth trends
   - Currency conversion will be applied for consistent totals

3. **Reporting Integration**:
   - Investment performance will be included in financial reports
   - Asset allocation will be visualized in portfolio dashboards
   - Tax exposure will be highlighted for tax planning

### Cashflow Analysis Integration

Investment accounts will integrate with cashflow analysis in the following ways:

1. **Contribution Planning**:
   - Scheduled contributions will be included in cashflow forecasts
   - Tax implications of contributions will be noted
   - Required Minimum Distributions (RMDs) will be projected for eligible accounts

2. **Income Recognition**:
   - Dividend income will be projected based on holdings
   - Interest from cash balances will be estimated
   - Capital gains distributions will be forecasted for mutual funds

3. **Tax Liability Estimation**:
   - Potential tax liabilities from investment activities will be estimated
   - Tax-advantaged account withdrawals will be distinguished from taxable accounts
   - Early withdrawal penalties will be highlighted where applicable

## Special Considerations

### HSA Account Implementation Details

HSA accounts deserve special attention due to their dual nature as both health expense and investment vehicles:

1. **Dual Balance Tracking**:
   - Cash balance available for immediate health expenses
   - Investment balance for long-term growth
   - Investment threshold setting to maintain adequate cash reserves

2. **Qualified Expense Tracking**:
   - Optional categorization of expenses as qualified medical expenses
   - Running total of qualified expenses for tax-free withdrawal planning
   - Documentation links for expense substantiation

3. **Family vs. Individual Coverage**:
   - Different contribution limits based on coverage type
   - Family: $8,300 in 2025 (as per research)
   - Individual: $4,150 in 2025 (as per research)
   - Catch-up contributions for users over 55

4. **Integration with Health Plans**:
   - Linked high-deductible health plan information
   - Deductible tracking for financial planning
   - Coordination with insurance accounts for premium payments

### Cryptocurrency Considerations

Cryptocurrency accounts have unique requirements:

1. **High Precision Requirements**:
   - Eight decimal places for quantities (to handle small fractional amounts)
   - Higher precision for prices (some cryptocurrencies trade at very low or very high prices)
   - Special formatting for display purposes

2. **Wallet Security**:
   - Only store public addresses/identifiers
   - Never store private keys or seed phrases
   - Clear guidance on security best practices

3. **Multi-Wallet Support**:
   - Different account types (exchange, hardware wallet, software wallet)
   - Special transaction types (staking, lending, yield farming)
   - Distinction between custodial and non-custodial holdings

4. **Tax Implications**:
   - Capital gains tracking for taxable events
   - Special handling for forks, airdrops, and other crypto-specific events
   - Integration with tax reporting features

### Retirement Account Specifics

Retirement accounts have specific characteristics that require specialized handling:

1. **Account Type Variations**:
   - Traditional vs. Roth tax treatment
   - Employer-sponsored vs. individual accounts
   - Special rules for each account type

2. **Contribution Tracking**:
   - Annual limits with age-based catch-up provisions
   - Employer match tracking for complete contribution picture
   - After-tax and Roth contribution distinctions

3. **Vesting Schedules**:
   - Track vested vs. unvested portions of employer contributions
   - Calculate vesting based on employment duration
   - Project future vesting for financial planning

4. **Distribution Planning**:
   - Different rules based on account type and age
   - Required Minimum Distribution (RMD) calculations
   - Early withdrawal penalty considerations

## Implementation Timeline

The investment account types will be implemented in three phases:

### Phase 1: Core Models and Schema (Week 1-2)

- Database model implementation
- Pydantic schema creation
- Repository layer implementation
- Basic service methods
- Initial API endpoints

### Phase 2: Portfolio Analytics (Week 3-4)

- Holdings management
- Asset allocation calculations
- Portfolio summary features
- Contribution limit tracking
- Data visualization endpoints

### Phase 3: Financial Planning (Week 5-6)

- Retirement projection tools
- Tax optimization suggestions
- Integration with net worth and cashflow
- Performance reporting features
- Data currency management

## Testing Strategy

Testing for investment account types will be comprehensive:

1. **Model Validation Tests**:
   - Verify inheritance hierarchy works correctly
   - Test polymorphic loading and saving
   - Ensure holding relationships function properly
   - Validate balance calculations

2. **Calculation Accuracy Tests**:
   - Test asset allocation calculations
   - Validate retirement projections against known examples
   - Test contribution limit checks
   - Verify portfolio summary calculations

3. **Integration Tests**:
   - Test interaction between holdings and account balances
   - Verify net worth integration
   - Test cashflow integration
   - Validate tax-advantaged account logic

4. **Performance Tests**:
   - Benchmark portfolio calculations
   - Test with large numbers of holdings
   - Verify caching effectiveness
   - Measure API response times

## Documentation Requirements

The investment account implementation will require the following documentation:

1. **Technical Documentation**:
   - Complete API specification for all endpoints
   - Database schema diagrams
   - Portfolio calculation methodologies
   - Holding management guidelines

2. **User Documentation**:
   - Account setup guides for each investment type
   - Portfolio tracking best practices
   - Tax advantage explainers
   - Retirement planning guides

3. **Developer Guides**:
   - Frontend integration examples
   - Portfolio visualization examples
   - User-initiated updates pattern
   - Performance optimization tips

## References

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-020: Loan Account Types Expansion](/code/debtonator/docs/adr/backend/020-loan-account-types-expansion.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)

## Notes

### Real-Time Price Updates Considerations

While real-time price updates are outside the scope of this ADR, the system is designed to accommodate future integration with market data providers:

1. **Updating Mechanism**:
   - The holding model includes last_updated timestamp
   - The update_holding_value repository method provides the interface for price updates
   - Account balances are updated whenever holdings change

2. **Integration Points**:
   - Future market data API could update prices via the existing methods
   - Batch updates could be processed for efficiency
   - User-triggered refreshes could be implemented

3. **Balance Consistency**:
   - Transaction boundaries ensure holdings and account balances stay in sync
   - Denormalized totals enable efficient queries while maintaining data integrity
   - Clear update patterns prevent race conditions

### Tax Lot Tracking Future Extension

While not implemented in this initial version, the model is designed to allow future extension to tax lot tracking:

1. **Future Expansion Path**:
   - Add InvestmentLot model related to InvestmentHolding
   - Track purchase date, cost basis, and quantity per lot
   - Implement lot selection methods (FIFO, LIFO, specific identification)

2. **Current Accommodation**:
   - The cost_basis field in holdings provides basic tax information
   - The model structure allows adding the lot relationship without breaking changes
   - API design anticipates the need for tax-aware operations

3. **Tax Reporting Preparation**:
   - Current structure captures essential data for basic tax reporting
   - Design allows for more sophisticated tax analysis in the future
   - Clear separation of taxable vs. tax-advantaged accounts

## Updates

| Date | Revision | Author | Description |
|------|----------|--------|-------------|
| 2025-04-11 | 1.0 | Debtonator Team | Initial draft |
