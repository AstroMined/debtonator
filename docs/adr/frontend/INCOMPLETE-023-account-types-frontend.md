# ADR-023: Account Types API Integration and Frontend

## Status

Proposed

## Context

The previous ADRs (016, 019, 020, 021, and 022) have established a comprehensive polymorphic account model framework and implemented specific account types across various categories: Banking, Loans, Investments, and Bills/Obligations. With the backend implementation complete, we now need to integrate these account types with the API layer and develop corresponding frontend components to provide a cohesive user experience.

The current limitations in our application include:

1. Lack of unified API endpoints that can handle all account types consistently
2. Missing frontend components for specialized account type forms and displays
3. No consistent approach to type-specific operations and validations in the frontend
4. Inconsistent error handling and user feedback across account types
5. Limited visualization capabilities for different account categories

These limitations prevent users from fully utilizing the expanded account type capabilities and obtaining a holistic view of their financial situation.

## Decision

We will implement a comprehensive API integration and frontend architecture that supports all account types defined in the previous ADRs. This implementation will follow a consistent pattern while accommodating the unique characteristics of each account type.

Our approach includes:

1. **Unified API Layer**:
   - Implementing consistent endpoints for all account operations
   - Supporting polymorphic account types through discriminated unions
   - Providing specialized endpoints for type-specific operations

2. **Frontend Component Architecture**:
   - Developing reusable components for common account operations
   - Creating specialized form components for each account type
   - Implementing type-specific displays and visualizations

3. **Frontend Organization**:
   - Organizing accounts by logical categories in the UI
   - Providing consistent navigation and discoverability
   - Supporting customizable dashboard views

4. **Integration Strategy**:
   - Phased rollout of account type support
   - Clear migration path for existing accounts
   - Comprehensive testing approach

## Technical Details

### API Layer Architecture

#### Unified Account Endpoints

We will implement a set of unified endpoints that can handle all account types:

```python
@router.post("/accounts", response_model=AccountResponseUnion)
def create_account(
    account_data: AccountCreateUnion,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new account of any type."""
    data_dict = account_data.model_dump()
    data_dict["user_id"] = current_user.id
    return account_service.create_account(data_dict)

@router.get("/accounts", response_model=List[AccountResponseUnion])
def get_accounts(
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    category: Optional[str] = Query(None, description="Filter by account category"),
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get all accounts for the current user with optional filtering."""
    if account_type:
        return account_service.get_accounts_by_type(current_user.id, account_type)
    elif category:
        return account_service.get_accounts_by_category(current_user.id, category)
    else:
        return account_service.get_user_accounts(current_user.id)

@router.get("/accounts/{account_id}", response_model=AccountResponseUnion)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get a specific account by ID."""
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.put("/accounts/{account_id}", response_model=AccountResponseUnion)
def update_account(
    account_id: int,
    account_data: AccountUpdateUnion,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Update an account."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    data_dict = account_data.model_dump(exclude_unset=True)
    return account_service.update_account(account_id, data_dict)

@router.delete("/accounts/{account_id}", response_model=AccountDeletionResponse)
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Delete (or mark as closed) an account."""
    # Verify account belongs to user
    account = account_service.get_account(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    
    result = account_service.delete_account(account_id)
    return {"success": result, "message": "Account deleted successfully"}
```

#### Category-Specific Endpoints

In addition to the unified endpoints, we will maintain the specialized endpoints for category-specific operations:

```python
@router.get("/account-types", response_model=List[AccountTypeInfo])
def get_account_types(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get all available account types with optional category filtering."""
    if category:
        return account_type_registry.get_types_by_category(category)
    else:
        return account_type_registry.get_all_types()

@router.get("/account-categories", response_model=List[AccountCategory])
def get_account_categories():
    """Get all account categories."""
    return account_type_registry.get_all_categories()

@router.get("/dashboard/financial-overview", response_model=FinancialOverviewResponse)
def get_financial_overview(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get a comprehensive financial overview across all account types."""
    return dashboard_service.get_financial_overview(current_user.id)
```

### Frontend Architecture

#### Component Organization

We will organize the frontend components in a hierarchical structure:

```
src/
  components/
    accounts/
      common/
        AccountForm.tsx
        AccountList.tsx
        AccountCard.tsx
        DeleteAccountDialog.tsx
      banking/
        CheckingAccountForm.tsx
        SavingsAccountForm.tsx
        CreditAccountForm.tsx
        BNPLAccountForm.tsx
        EWAAccountForm.tsx
        PaymentAppAccountForm.tsx
      loans/
        LoanAccountForm.tsx
        MortgageAccountForm.tsx
        StudentLoanAccountForm.tsx
        PersonalLoanAccountForm.tsx
        AutoLoanAccountForm.tsx
      investments/
        BrokerageAccountForm.tsx
        RetirementAccountForm.tsx
        HSAAccountForm.tsx
        CryptoAccountForm.tsx
        InvestmentHoldingForm.tsx
      obligations/
        UtilityAccountForm.tsx
        SubscriptionAccountForm.tsx
        InsuranceAccountForm.tsx
        TaxAccountForm.tsx
        SupportPaymentAccountForm.tsx
        ObligationPaymentForm.tsx
    dashboard/
      AccountSummary.tsx
      NetWorthChart.tsx
      UpcomingBillsList.tsx
      DebtOverview.tsx
      InvestmentOverview.tsx
```

#### Reusable Component Patterns

We will implement reusable component patterns to ensure consistency:

```typescript
// GenericAccountForm component pattern
const GenericAccountForm = ({
  accountType,
  initialData,
  onSubmit,
  onCancel
}: GenericAccountFormProps) => {
  // Common fields for all account types (name, institution, etc.)
  const commonFields = { /* ... */ };
  
  // Dynamically load type-specific fields based on accountType
  const TypeSpecificFields = getFieldsComponentForType(accountType);
  
  return (
    <Form onSubmit={onSubmit}>
      {/* Common fields rendered here */}
      <CommonFields {...commonFields} />
      
      {/* Type-specific fields rendered here */}
      <TypeSpecificFields initialData={initialData} />
      
      <FormActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button type="submit" variant="primary">Save</Button>
      </FormActions>
    </Form>
  );
};

// TypeSpecificFields dynamically loaded by account type
const getFieldsComponentForType = (accountType: string) => {
  switch (accountType) {
    case 'checking':
      return CheckingAccountFields;
    case 'savings':
      return SavingsAccountFields;
    case 'credit':
      return CreditAccountFields;
    // ...other account types
    default:
      return GenericAccountFields;
  }
};
```

### Account Type Registration and Discovery

We will implement a frontend registration system that mirrors the backend registry:

```typescript
// Account type registry for frontend
interface AccountTypeDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: React.ComponentType;
  formComponent: React.ComponentType<any>;
  detailComponent: React.ComponentType<any>;
  cardComponent: React.ComponentType<any>;
  supportsFeatures: string[];
}

const accountTypeRegistry: Record<string, AccountTypeDefinition> = {
  // Banking accounts
  checking: {
    id: 'checking',
    name: 'Checking Account',
    description: 'Day-to-day transaction account',
    category: 'Banking',
    icon: BankIcon,
    formComponent: CheckingAccountForm,
    detailComponent: CheckingAccountDetail,
    cardComponent: CheckingAccountCard,
    supportsFeatures: ['billSplit', 'transfer', 'directDeposit']
  },
  // Additional account types...
};

// Utility functions for working with the registry
const getAccountTypeDefinition = (typeId: string): AccountTypeDefinition => {
  return accountTypeRegistry[typeId] || accountTypeRegistry.generic;
};

const getAccountTypesByCategory = (category: string): AccountTypeDefinition[] => {
  return Object.values(accountTypeRegistry)
    .filter(def => def.category === category);
};
```

### Dashboard and Financial Overview

To provide a holistic financial view, we'll implement a comprehensive dashboard:

```typescript
const FinancialDashboard = () => {
  const { data: accounts, isLoading: accountsLoading } = useQuery(
    ['accounts'],
    () => api.getAccounts()
  );
  
  const { data: overview, isLoading: overviewLoading } = useQuery(
    ['financial-overview'],
    () => api.getFinancialOverview()
  );
  
  if (accountsLoading || overviewLoading) {
    return <Spinner />;
  }
  
  // Group accounts by category
  const accountsByCategory = groupAccountsByCategory(accounts);
  
  return (
    <DashboardLayout>
      <NetWorthSummary 
        assets={overview.assets}
        liabilities={overview.liabilities}
      />
      
      <CashflowForecast 
        upcomingBills={overview.upcomingBills}
        projectedIncome={overview.projectedIncome}
      />
      
      <AccountCategorySummaries>
        <BankingAccountsSummary accounts={accountsByCategory.Banking} />
        <DebtSummary accounts={accountsByCategory.Loans} />
        <InvestmentsSummary accounts={accountsByCategory.Investments} />
        <BillsSummary accounts={accountsByCategory.Bills} />
      </AccountCategorySummaries>
      
      <ActionButtons>
        <AddAccountButton />
        <RecordPaymentButton />
        <UpdateBalancesButton />
      </ActionButtons>
    </DashboardLayout>
  );
};
```

### Type-Specific Forms and Validations

Each account type will have dedicated form components with appropriate validations:

```typescript
// Example for MortgageAccountForm
const MortgageAccountForm = ({ initialData, onSubmit }) => {
  // Form state using React Hook Form
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: initialData || {
      name: '',
      institution: '',
      account_number: '',
      account_type: 'mortgage',
      original_loan_amount: '',
      interest_rate: '',
      term_months: '',
      start_date: '',
      payment_amount: '',
      payment_due_day: '',
      property_address: '',
      property_type: 'single_family',
      is_primary_residence: true,
      escrow_amount: '',
      mortgage_type: 'fixed'
    }
  });
  
  // Custom validations
  const validateInterestRate = (value) => {
    const rate = parseFloat(value);
    return (rate >= 0 && rate <= 20) || 'Interest rate must be between 0% and 20%';
  };
  
  // Form submission handler
  const onFormSubmit = (data) => {
    // Convert string values to appropriate types
    const formattedData = {
      ...data,
      original_loan_amount: parseFloat(data.original_loan_amount),
      interest_rate: parseFloat(data.interest_rate),
      term_months: parseInt(data.term_months, 10),
      payment_amount: parseFloat(data.payment_amount),
      payment_due_day: parseInt(data.payment_due_day, 10),
      escrow_amount: data.escrow_amount ? parseFloat(data.escrow_amount) : null
    };
    
    onSubmit(formattedData);
  };
  
  return (
    <form onSubmit={handleSubmit(onFormSubmit)}>
      {/* Common account fields */}
      <TextField
        label="Account Name"
        {...register('name', { required: 'Account name is required' })}
        error={!!errors.name}
        helperText={errors.name?.message}
      />
      
      {/* Mortgage-specific fields */}
      <TextField
        label="Original Loan Amount"
        type="number"
        {...register('original_loan_amount', { 
          required: 'Loan amount is required',
          min: { value: 1, message: 'Amount must be greater than 0' }
        })}
        error={!!errors.original_loan_amount}
        helperText={errors.original_loan_amount?.message}
      />
      
      <TextField
        label="Interest Rate (%)"
        type="number"
        {...register('interest_rate', { 
          required: 'Interest rate is required',
          validate: validateInterestRate
        })}
        error={!!errors.interest_rate}
        helperText={errors.interest_rate?.message}
      />
      
      {/* Additional mortgage-specific fields */}
      <TextField
        label="Property Address"
        {...register('property_address', { required: 'Property address is required' })}
        error={!!errors.property_address}
        helperText={errors.property_address?.message}
      />
      
      <Select
        label="Property Type"
        {...register('property_type')}
      >
        <MenuItem value="single_family">Single Family Home</MenuItem>
        <MenuItem value="condo">Condominium</MenuItem>
        <MenuItem value="townhouse">Townhouse</MenuItem>
        <MenuItem value="multi_family">Multi-Family Home</MenuItem>
        <MenuItem value="mobile_home">Mobile Home</MenuItem>
        <MenuItem value="other">Other</MenuItem>
      </Select>
      
      <FormControlLabel
        control={
          <Checkbox
            {...register('is_primary_residence')}
            defaultChecked={initialData?.is_primary_residence ?? true}
          />
        }
        label="This is my primary residence"
      />
      
      <Select
        label="Mortgage Type"
        {...register('mortgage_type')}
      >
        <MenuItem value="fixed">Fixed Rate</MenuItem>
        <MenuItem value="arm">Adjustable Rate (ARM)</MenuItem>
        <MenuItem value="balloon">Balloon</MenuItem>
        <MenuItem value="interest_only">Interest Only</MenuItem>
        <MenuItem value="reverse">Reverse Mortgage</MenuItem>
      </Select>
      
      <Button type="submit" variant="contained" color="primary">
        Save Mortgage Account
      </Button>
    </form>
  );
};
```

### Account Type Display Components

Each account type will have specialized display components:

```typescript
// Example for CreditAccountCard
const CreditAccountCard = ({ account }) => {
  // Calculate credit utilization
  const utilization = account.credit_limit > 0 
    ? (account.current_balance / account.credit_limit) * 100 
    : 0;
  
  // Determine utilization color
  const getUtilizationColor = (percent) => {
    if (percent < 30) return 'success.main';
    if (percent < 70) return 'warning.main';
    return 'error.main';
  };
  
  // Format due date
  const formattedDueDate = account.statement_due_date
    ? formatDate(account.statement_due_date)
    : 'Not available';
  
  // Calculate days until payment due
  const daysUntilDue = account.statement_due_date
    ? getDaysBetween(new Date(), new Date(account.statement_due_date))
    : null;
  
  return (
    <Card>
      <CardHeader
        avatar={<CreditCardIcon />}
        title={account.name}
        subheader={account.institution}
      />
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="caption">Current Balance</Typography>
            <Typography variant="h6" color="text.primary">
              {formatCurrency(account.current_balance)}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption">Available Credit</Typography>
            <Typography variant="h6" color="text.primary">
              {formatCurrency(account.credit_limit - account.current_balance)}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="caption">Credit Utilization</Typography>
            <LinearProgress
              variant="determinate"
              value={Math.min(utilization, 100)}
              sx={{ height: 8, borderRadius: 4, bgcolor: 'background.paper', mt: 1, mb: 1 }}
              color={utilization > 80 ? "error" : utilization > 30 ? "warning" : "success"}
            />
            <Typography variant="body2" color={getUtilizationColor(utilization)}>
              {utilization.toFixed(1)}% of {formatCurrency(account.credit_limit)}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Divider />
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption">Statement Balance</Typography>
            <Typography variant="body1">
              {formatCurrency(account.statement_balance || 0)}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption">Payment Due</Typography>
            <Typography 
              variant="body1" 
              color={daysUntilDue && daysUntilDue < 5 ? "error.main" : "text.primary"}
            >
              {formattedDueDate}
              {daysUntilDue && daysUntilDue > 0 && (
                <Typography variant="caption" display="block">
                  {daysUntilDue} {daysUntilDue === 1 ? 'day' : 'days'} remaining
                </Typography>
              )}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
      <CardActions>
        <Button size="small" startIcon={<EditIcon />}>Edit</Button>
        <Button 
          size="small" 
          startIcon={<PaymentIcon />}
          disabled={!account.statement_balance}
        >
          Make Payment
        </Button>
        <Button size="small" startIcon={<MoreVertIcon />}>More</Button>
      </CardActions>
    </Card>
  );
};
```

### Category-Specific Financial Analysis

Special components for analyzing each account category:

```typescript
// Example for debt analysis and payoff strategies
const DebtPayoffAnalysis = ({ debtAccounts }) => {
  const [extraPaymentAmount, setExtraPaymentAmount] = useState(100);
  const [selectedStrategy, setSelectedStrategy] = useState('snowball');
  
  // Client-side data processing to compute payoff strategies
  const snowballStrategy = useMemo(() => {
    return [...debtAccounts]
      .sort((a, b) => a.current_balance - b.current_balance);
  }, [debtAccounts]);
  
  const avalancheStrategy = useMemo(() => {
    return [...debtAccounts]
      .sort((a, b) => {
        // Sort by interest rate (descending)
        const rateA = getInterestRate(a);
        const rateB = getInterestRate(b);
        return rateB - rateA;
      });
  }, [debtAccounts]);
  
  // Get interest rate based on account type
  const getInterestRate = (account) => {
    switch (account.account_type) {
      case 'credit':
        return account.apr || 0;
      case 'personal_loan':
      case 'auto_loan':
      case 'mortgage':
      case 'student_loan':
        return account.interest_rate || 0;
      default:
        return 0;
    }
  };
  
  // Calculate total debt
  const totalDebt = debtAccounts.reduce(
    (sum, account) => sum + account.current_balance, 
    0
  );
  
  // Calculate minimum monthly payments
  const totalMinimumPayment = debtAccounts.reduce(
    (sum, account) => sum + getMinimumPayment(account), 
    0
  );
  
  // Get minimum payment based on account type
  const getMinimumPayment = (account) => {
    switch (account.account_type) {
      case 'credit':
        return account.minimum_payment || 0;
      case 'personal_loan':
      case 'auto_loan':
      case 'mortgage':
      case 'student_loan':
        return account.payment_amount || 0;
      default:
        return 0;
    }
  };
  
  // Fetch payoff projections from API
  const { data: payoffProjection, isLoading } = useQuery(
    ['debt-payoff', selectedStrategy, extraPaymentAmount],
    () => api.getDebtPayoffProjection({
      strategy: selectedStrategy,
      extraPayment: extraPaymentAmount
    })
  );
  
  return (
    <Container>
      <Typography variant="h5" gutterBottom>Debt Payoff Strategies</Typography>
      
      <Box mb={4}>
        <Typography variant="subtitle1">Your Debt Summary</Typography>
        <Typography variant="h4">{formatCurrency(totalDebt)}</Typography>
        <Typography variant="body2">
          Total minimum monthly payment: {formatCurrency(totalMinimumPayment)}
        </Typography>
      </Box>
      
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Payoff Strategy</InputLabel>
            <Select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
            >
              <MenuItem value="snowball">
                Snowball (Smallest Balance First)
              </MenuItem>
              <MenuItem value="avalanche">
                Avalanche (Highest Interest First)
              </MenuItem>
            </Select>
            <FormHelperText>
              {selectedStrategy === 'snowball' 
                ? 'Focus on the smallest debts first for psychological wins'
                : 'Focus on highest interest rates first to minimize interest paid'}
            </FormHelperText>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <TextField
            label="Extra Monthly Payment"
            type="number"
            value={extraPaymentAmount}
            onChange={(e) => setExtraPaymentAmount(Number(e.target.value))}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
            fullWidth
          />
        </Grid>
      </Grid>
      
      {isLoading ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              {selectedStrategy === 'snowball' ? 'Snowball' : 'Avalanche'} Payment Order
            </Typography>
            <DebtPaymentOrderList 
              accounts={selectedStrategy === 'snowball' ? snowballStrategy : avalancheStrategy}
              getInterestRate={getInterestRate}
              getMinimumPayment={getMinimumPayment}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              With Your Current Plan
            </Typography>
            {payoffProjection && (
              <>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Box>
                    <Typography variant="subtitle2">Debt-Free Date</Typography>
                    <Typography variant="body1">
                      {formatDate(payoffProjection.debtFreeDate)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2">Total Interest Paid</Typography>
                    <Typography variant="body1">
                      {formatCurrency(payoffProjection.totalInterestPaid)}
                    </Typography>
                  </Box>
                </Box>
                
                <Typography variant="subtitle2">Payoff Timeline</Typography>
                <DebtPayoffChart payoffData={payoffProjection.timeline} />
                
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>Your Savings</Typography>
                  <Typography variant="body2">
                    With an extra {formatCurrency(extraPaymentAmount)} per month, you'll be debt-free 
                    <strong> {payoffProjection.monthsSaved} months sooner</strong> and save 
                    <strong> {formatCurrency(payoffProjection.interestSaved)} in interest!</strong>
                  </Typography>
                </Box>
              </>
            )}
          </Grid>
        </Grid>
      )}
    </Container>
  );
};
```

### Frontend Integration with Backend Endpoints

API client implementation for interacting with the backend:

```typescript
// api.ts - API client for account operations
const api = {
  // Account CRUD operations
  getAccounts: async (filters = {}) => {
    const queryParams = new URLSearchParams();
    if (filters.accountType) queryParams.append('account_type', filters.accountType);
    if (filters.category) queryParams.append('category', filters.category);
    
    const response = await fetch(`/api/accounts?${queryParams.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch accounts');
    return response.json();
  },
  
  getAccount: async (accountId) => {
    const response = await fetch(`/api/accounts/${accountId}`);
    if (!response.ok) throw new Error('Failed to fetch account');
    return response.json();
  },
  
  createAccount: async (accountData) => {
    const response = await fetch('/api/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(accountData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update account');
    }
    
    return response.json();
  },
  
  deleteAccount: async (accountId) => {
    const response = await fetch(`/api/accounts/${accountId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete account');
    }
    
    return response.json();
  },
  
  // Account type information
  getAccountTypes: async (category) => {
    const url = category 
      ? `/api/account-types?category=${encodeURIComponent(category)}`
      : '/api/account-types';
      
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch account types');
    return response.json();
  },
  
  getAccountCategories: async () => {
    const response = await fetch('/api/account-categories');
    if (!response.ok) throw new Error('Failed to fetch account categories');
    return response.json();
  },
  
  // Dashboard and overview
  getFinancialOverview: async () => {
    const response = await fetch('/api/dashboard/financial-overview');
    if (!response.ok) throw new Error('Failed to fetch financial overview');
    return response.json();
  },
  
  // Category-specific operations
  getBankingOverview: async () => {
    const response = await fetch('/api/banking/overview');
    if (!response.ok) throw new Error('Failed to fetch banking overview');
    return response.json();
  },
  
  getUpcomingPayments: async (days = 30) => {
    const response = await fetch(`/api/banking/upcoming-payments?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch upcoming payments');
    return response.json();
  },
  
  getDebtPayoffProjection: async ({strategy, extraPayment}) => {
    const response = await fetch('/api/accounts/debt-reduction-strategies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({strategy, extraPayment})
    });
    if (!response.ok) throw new Error('Failed to fetch debt payoff projection');
    return response.json();
  },
  
  calculateLoanPayoffWithExtraPayment: async (loanId, extraPayment) => {
    const response = await fetch(`/api/accounts/loans/${loanId}/extra-payment-impact?extra_payment=${extraPayment}`);
    if (!response.ok) throw new Error('Failed to calculate loan payoff');
    return response.json();
  },
  
  getPortfolioSummary: async () => {
    const response = await fetch('/api/portfolio/summary');
    if (!response.ok) throw new Error('Failed to fetch portfolio summary');
    return response.json();
  },
  
  getAssetAllocation: async () => {
    const response = await fetch('/api/portfolio/allocation');
    if (!response.ok) throw new Error('Failed to fetch asset allocation');
    return response.json();
  },
  
  getUpcomingBills: async (days = 30) => {
    const response = await fetch(`/api/bills/upcoming?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch upcoming bills');
    return response.json();
  },
  
  recordObligationPayment: async (accountId, paymentData) => {
    const response = await fetch(`/api/accounts/obligations/${accountId}/payments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(paymentData)
    });
    if (!response.ok) throw new Error('Failed to record payment');
    return response.json();
  }
};
```

### React Context for Account Type Management

To share account type information across components:

```typescript
// AccountTypesContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

interface AccountTypeContextType {
  accountTypes: AccountType[];
  accountCategories: AccountCategory[];
  getTypeInfo: (typeId: string) => AccountType | undefined;
  getTypesByCategory: (category: string) => AccountType[];
  isLoading: boolean;
  error: Error | null;
}

const AccountTypesContext = createContext<AccountTypeContextType | undefined>(undefined);

export const AccountTypesProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [accountTypes, setAccountTypes] = useState<AccountType[]>([]);
  const [accountCategories, setAccountCategories] = useState<AccountCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    const fetchAccountTypeData = async () => {
      try {
        setIsLoading(true);
        
        const [types, categories] = await Promise.all([
          api.getAccountTypes(),
          api.getAccountCategories()
        ]);
        
        setAccountTypes(types);
        setAccountCategories(categories);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load account types'));
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAccountTypeData();
  }, []);
  
  const getTypeInfo = (typeId: string) => {
    return accountTypes.find(type => type.id === typeId);
  };
  
  const getTypesByCategory = (category: string) => {
    return accountTypes.filter(type => type.category === category);
  };
  
  const value = {
    accountTypes,
    accountCategories,
    getTypeInfo,
    getTypesByCategory,
    isLoading,
    error
  };
  
  return (
    <AccountTypesContext.Provider value={value}>
      {children}
    </AccountTypesContext.Provider>
  );
};

export const useAccountTypes = () => {
  const context = useContext(AccountTypesContext);
  if (context === undefined) {
    throw new Error('useAccountTypes must be used within an AccountTypesProvider');
  }
  return context;
};
```

## Navigation and User Experience

### Account Type Selection Flow

```typescript
// AccountCreationFlow.tsx
import React, { useState } from 'react';
import { useAccountTypes } from '../contexts/AccountTypesContext';

const AccountCreationFlow = () => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const { accountCategories, getTypesByCategory } = useAccountTypes();
  
  // Reset type selection when category changes
  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setSelectedType(null);
  };
  
  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>Add a New Account</Typography>
      
      {/* Step 1: Select Account Category */}
      {!selectedCategory && (
        <>
          <Typography variant="h6" gutterBottom>
            What type of account would you like to add?
          </Typography>
          <Grid container spacing={3}>
            {accountCategories.map(category => (
              <Grid item xs={6} sm={3} key={category.id}>
                <CategoryCard
                  category={category}
                  onClick={() => handleCategorySelect(category.id)}
                />
              </Grid>
            ))}
          </Grid>
        </>
      )}
      
      {/* Step 2: Select Account Type */}
      {selectedCategory && !selectedType && (
        <>
          <Button 
            startIcon={<ArrowBackIcon />} 
            onClick={() => setSelectedCategory(null)}
            sx={{ mb: 2 }}
          >
            Back to Categories
          </Button>
          
          <Typography variant="h6" gutterBottom>
            Select the specific type of {selectedCategory} account
          </Typography>
          
          <Grid container spacing={3}>
            {getTypesByCategory(selectedCategory).map(type => (
              <Grid item xs={12} sm={6} key={type.id}>
                <AccountTypeCard
                  type={type}
                  onClick={() => setSelectedType(type.id)}
                />
              </Grid>
            ))}
          </Grid>
        </>
      )}
      
      {/* Step 3: Account Form */}
      {selectedCategory && selectedType && (
        <>
          <Button 
            startIcon={<ArrowBackIcon />} 
            onClick={() => setSelectedType(null)}
            sx={{ mb: 2 }}
          >
            Back to Account Types
          </Button>
          
          <Typography variant="h6" gutterBottom>
            Enter your {selectedType} account details
          </Typography>
          
          <DynamicAccountForm
            accountType={selectedType}
            onSubmit={handleSubmit}
            onCancel={() => setSelectedType(null)}
          />
        </>
      )}
    </Container>
  );
};

// Dynamic form component that renders the correct form based on account type
const DynamicAccountForm = ({ accountType, onSubmit, onCancel }) => {
  // Use account type registry to get the correct form component
  const FormComponent = getAccountTypeDefinition(accountType).formComponent;
  
  return (
    <FormComponent
      onSubmit={onSubmit}
      onCancel={onCancel}
    />
  );
};
```

### Account Grouping and Visualization

```typescript
// AccountsOverviewPage.tsx
import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import { useAccountTypes } from '../contexts/AccountTypesContext';

const AccountsOverviewPage = () => {
  const [viewMode, setViewMode] = useState<'category' | 'list'>('category');
  const { getTypeInfo } = useAccountTypes();
  
  const { data: accounts, isLoading } = useQuery(
    ['accounts'],
    () => api.getAccounts()
  );
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  // Group accounts by category
  const accountsByCategory = accounts.reduce((grouped, account) => {
    const typeInfo = getTypeInfo(account.account_type);
    const category = typeInfo?.category || 'Other';
    
    if (!grouped[category]) {
      grouped[category] = [];
    }
    
    grouped[category].push(account);
    return grouped;
  }, {});
  
  // Calculate totals for each category
  const categoryTotals = Object.entries(accountsByCategory).reduce((totals, [category, categoryAccounts]) => {
    // Sum assets (positive) and liabilities (negative)
    const assets = categoryAccounts
      .filter(account => isCategoryAsset(category, account.account_type))
      .reduce((sum, account) => sum + account.current_balance, 0);
      
    const liabilities = categoryAccounts
      .filter(account => !isCategoryAsset(category, account.account_type))
      .reduce((sum, account) => sum + account.current_balance, 0);
    
    totals[category] = {
      assets,
      liabilities,
      netValue: assets - liabilities
    };
    
    return totals;
  }, {});
  
  // Helper to determine if an account type is an asset
  const isCategoryAsset = (category: string, accountType: string) => {
    // Banking accounts are assets except for credit
    if (category === 'Banking') {
      return accountType !== 'credit' && 
             accountType !== 'bnpl' && 
             accountType !== 'ewa';
    }
    
    // Investments are assets
    if (category === 'Investments') {
      return true;
    }
    
    // Loans are never assets
    if (category === 'Loans') {
      return false;
    }
    
    // Bills/Obligations are never assets
    if (category === 'Bills') {
      return false;
    }
    
    return true; // Default assumption
  };
  
  return (
    <Container>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Accounts</Typography>
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, newMode) => newMode && setViewMode(newMode)}
        >
          <ToggleButton value="category">
            <CategoryIcon />
            <Typography variant="caption" ml={1}>By Category</Typography>
          </ToggleButton>
          <ToggleButton value="list">
            <ListIcon />
            <Typography variant="caption" ml={1}>List View</Typography>
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>
      
      {viewMode === 'category' ? (
        // Category view
        <>
          {Object.entries(accountsByCategory).map(([category, categoryAccounts]) => (
            <Box key={category} mb={4}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5">{category}</Typography>
                <Typography variant="h6">
                  {formatCurrency(categoryTotals[category].netValue)}
                </Typography>
              </Box>
              
              <Grid container spacing={3}>
                {categoryAccounts.map(account => (
                  <Grid item xs={12} md={6} lg={4} key={account.id}>
                    <DynamicAccountCard account={account} />
                  </Grid>
                ))}
                
                <Grid item xs={12} md={6} lg={4}>
                  <AddAccountButton category={category} />
                </Grid>
              </Grid>
            </Box>
          ))}
        </>
      ) : (
        // List view
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Account</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Institution</TableCell>
                <TableCell align="right">Balance</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {accounts.map(account => (
                <TableRow key={account.id}>
                  <TableCell>{account.name}</TableCell>
                  <TableCell>
                    {getTypeInfo(account.account_type)?.name || account.account_type}
                  </TableCell>
                  <TableCell>{account.institution}</TableCell>
                  <TableCell align="right">{formatCurrency(account.current_balance)}</TableCell>
                  <TableCell>
                    <IconButton size="small">
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

// Dynamic account card component that renders the correct card based on account type
const DynamicAccountCard = ({ account }) => {
  // Use account type registry to get the correct card component
  const CardComponent = getAccountTypeDefinition(account.account_type).cardComponent;
  
  return <CardComponent account={account} />;
};
```

## Consequences

### Positive

1. **Consistent User Experience**: Users will have a unified experience across all account types while still benefiting from specialized features.

2. **Improved Discoverability**: The category-based organization makes it easier for users to find and add the account types they need.

3. **Enhanced Visualization**: Type-specific displays provide more relevant information for each account type.

4. **Simplified Maintenance**: The component architecture makes it easier to add new account types in the future.

5. **Comprehensive Financial View**: The integrated dashboard provides a holistic view of the user's financial situation.

### Negative

1. **Implementation Complexity**: The comprehensive approach requires significant frontend development effort.

2. **Performance Considerations**: Dynamic component loading and specialized visualizations may impact performance on slower devices.

3. **Testing Overhead**: Each account type requires separate testing for forms, displays, and integrations.

### Neutral

1. **Learning Curve**: Users may need time to learn how to navigate the expanded account type system.

2. **UI Customization**: The specialized displays may make it harder for users to customize their view.

## Performance Impact

- **Component Loading**: Dynamic component loading adds a small overhead but improves code organization
- **Form Validation**: Client-side validation for complex forms may impact performance on mobile devices
- **Data Visualization**: Chart rendering may be resource-intensive for complex financial data
- **API Interactions**: Multiple API calls for specialized data may increase load times

### Optimization Strategies

1. **Code Splitting**:
   - Use React.lazy and Suspense for component loading
   - Split code by account category for more efficient loading
   - Implement progressive enhancement for complex features

2. **Data Caching**:
   - Use React Query's caching capabilities to minimize API calls
   - Implement stale-while-revalidate pattern for common data
   - Optimize API response size for mobile devices

3. **Rendering Optimization**:
   - Use virtualization for long account lists
   - Implement pagination for history and transaction data
   - Lazy load visualizations and charts

4. **Bundle Optimization**:
   - Analyze and reduce bundle size with tools like Webpack Bundle Analyzer
   - Optimize third-party dependencies
   - Implement tree shaking for unused components

## Integration with Existing Features

### Bill Split Integration

The account type UI will integrate with Debtonator's core bill splitting functionality:

1. **Bill Split Form**:
   - Select any compatible account type for bill splits
   - Display appropriate validation based on account type
   - Show clear error messages for incompatible account types

2. **Account Selection**:
   - Filter available accounts based on split compatibility
   - Group accounts by category in selection dropdowns
   - Display appropriate account details in split entries

3. **Payment Tracking**:
   - Link bill payments to account transactions
   - Update account balances based on split payments
   - Provide clear visualization of payment allocations

### Cashflow Analysis Integration

The account types will integrate with cashflow analysis features:

1. **Forecast Integration**:
   - Include all account types in cashflow projections
   - Apply appropriate calculation rules based on account type
   - Display forecasted balances with type-specific context

2. **Income and Expense Tracking**:
   - Link income sources to appropriate account types
   - Track expenses across all account types
   - Provide categorized summaries by account type

3. **Financial Planning**:
   - Integrate account-specific projections into overall financial plan
   - Calculate cross-account impacts for financial decisions
   - Provide optimization suggestions based on account types

## Implementation Timeline

The API integration and frontend implementation will be rolled out in phases:

### Phase 1: Core Infrastructure (Week 1-2)
- Unified API endpoints implementation
- Account type registry development
- Base component architecture
- Common form and display components

### Phase 2: Banking Accounts (Week 3-4)
- Banking account forms and displays
- Banking overview dashboard
- Checking and savings account management
- Credit card and payment app implementation

### Phase 3: Loans and Obligations (Week 5-6)
- Loan account forms and displays
- Obligation account forms and displays
- Payment recording interfaces
- Debt reduction tools

### Phase 4: Investments (Week 7-8)
- Investment account forms and displays
- Portfolio visualization tools
- Holdings management interfaces
- Retirement planning tools

### Phase 5: Dashboard Integration (Week 9-10)
- Comprehensive financial dashboard
- Cross-account analysis tools
- Print and export functionality
- User preference persistence

## Testing Strategy

The frontend implementation will be tested comprehensively:

1. **Component Testing**:
   - Unit tests for all form components
   - Snapshot tests for display components
   - Integration tests for form submission flows
   - Visual regression tests for UI components

2. **API Integration Testing**:
   - Mock API response testing
   - Error handling and edge case testing
   - Loading state and performance testing
   - Authentication and authorization testing

3. **User Flow Testing**:
   - End-to-end tests for account creation flows
   - User journey testing for key scenarios
   - Cross-browser and device testing
   - Accessibility testing for all components

4. **Performance Testing**:
   - Load time benchmarking
   - Component rendering performance
   - Memory usage profiling
   - Mobile device performance testing

## Documentation Requirements

The frontend implementation will require comprehensive documentation:

1. **Developer Documentation**:
   - Component API documentation
   - State management patterns
   - Account type registry usage
   - Error handling patterns

2. **Design System Documentation**:
   - UI component guidelines
   - Form pattern usage
   - Visualization standards
   - Accessibility requirements

3. **User Documentation**:
   - Account type setup guides
   - Feature tutorials
   - FAQ and troubleshooting
   - Best practices for financial management

## References

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-020: Loan Account Types Expansion](/code/debtonator/docs/adr/backend/020-loan-account-types-expansion.md)
- [ADR-021: Investment Account Types Expansion](/code/debtonator/docs/adr/backend/021-investment-account-types-expansion.md)
- [ADR-022: Bills and Obligations Account Types Expansion](/code/debtonator/docs/adr/backend/022-bills-and-obligations-account-types-expansion.md)
- [Account Type Expansion Research](/code/debtonator/docs/adr/backend/016-account-type-expansion-research.md)

## Notes

### Accessibility Considerations

The account type UI implementation will prioritize accessibility:

1. **Screen Reader Compatibility**:
   - All form fields have appropriate labels
   - Charts and visualizations include text alternatives
   - Complex components use ARIA attributes appropriately
   - Keyboard navigation is fully supported

2. **Visual Accessibility**:
   - Color schemes adhere to WCAG contrast requirements
   - Icons include text labels or tooltips
   - Text sizes are adjustable
   - All information conveyed by color is also available without color

3. **Cognitive Accessibility**:
   - Forms include clear validation messages
   - Complex financial concepts include explanations
   - Step-by-step flows guide users through complex tasks
   - Consistent patterns are used throughout the interface

### Mobile Optimization

The account type UI will be optimized for mobile devices:

1. **Responsive Layout**:
   - Forms adapt to smaller screens
   - Tables convert to card layouts on mobile
   - Touch targets are appropriately sized
   - Content prioritization for mobile views

2. **Performance Optimization**:
   - Reduced bundle size for mobile devices
   - Optimized image loading
   - Efficient re-rendering strategies
   - Battery-friendly animations and transitions

3. **Mobile-Specific UX**:
   - Support for gestures and touch interactions
   - Simplified navigation for smaller screens
   - Form input optimized for touch keyboards
   - Offline capability for basic operations

## Updates

| Date | Revision | Author | Description |
|------|----------|--------|-------------|
| 2025-04-11 | 1.0 | Debtonator Team | Initial draft |detail || 'Failed to create account');
    }
    
    return response.json();
  },
  
  updateAccount: async (accountId, accountData) => {
    const response = await fetch(`/api/accounts/${accountId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(accountData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update account');
    }
    
    return response.json();
  },
  
  deleteAccount: async (accountId) => {
    const response = await fetch(`/api/accounts/${accountId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.