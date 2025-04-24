# ADR-023: Account Types Frontend

## Status

Proposed

## Executive Summary

This ADR defines the frontend implementation for the expanded account type system established in ADRs 016, 019, 020, 021, and 022. It creates a consistent yet flexible architecture for managing diverse account types through reusable components, specialized forms and displays, category-based organization, and integration with existing features like bill splits and cashflow analysis. The implementation provides users with a comprehensive view of their financial situation while maintaining specialized functionality for each account type.

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

### User Stories

#### Category 1: Account Management

##### **US-1.1: View All Accounts**

- As a user, I want to view all my accounts organized by category
- So that I can quickly understand my overall financial position

##### **US-1.2: Add Account by Type**

- As a user, I want to add a new account by selecting its specific type
- So that I can track all my financial accounts in one place

##### **US-1.3: Manage Account Details**

- As a user, I want to update account details with type-specific information
- So that I can keep my account information accurate and up-to-date

##### **US-1.4: Delete Accounts**

- As a user, I want to delete/close accounts while maintaining historical records
- So that I can manage obsolete accounts without losing transaction history

#### Category 2: Financial Analysis

##### **US-2.1: View Financial Dashboard**

- As a user, I want a comprehensive dashboard showing all account types
- So that I can understand my complete financial picture

##### **US-2.2: Analyze Debt and Loans**

- As a user, I want to see debt reduction strategies across credit and loan accounts
- So that I can make informed decisions about prioritizing debt payments

##### **US-2.3: Track Investment Performance**

- As a user, I want to track performance across investment account types
- So that I can monitor my investment strategy and returns

#### Category 3: Integration Features

##### **US-3.1: Split Bills Across Account Types**

- As a user, I want to split bills across different account types
- So that I can manage shared expenses from multiple payment sources

##### **US-3.2: Setup Automatic Payments**

- As a user, I want to configure automatic payments from various account types
- So that I can ensure bills are paid on time from the right accounts

### User Interface and Click Paths

#### Account Overview Page

**Elements:**

- Category headers with summary information
- Account cards with type-specific displays
- Toggle between card view and list view
- Actions for adding, editing, and deleting accounts

##### **Click Path:** Add New Account

1. User navigates to Accounts page
2. User clicks "Add Account" button
3. User selects account category (Banking, Loans, Investments, Bills)
4. User selects specific account type within the category
5. User completes type-specific form with required fields
6. System validates input and creates account
7. New account appears in the appropriate category section

#### Account Detail View

**Elements:**

- Account header with name, type, and key metrics
- Type-specific fields and information
- Related transaction history
- Action buttons for common operations

##### **Click Path:** Update Account Balance

1. User navigates to specific account detail page
2. User clicks "Update Balance" button
3. System presents appropriate form based on account type
4. User enters new balance information
5. System validates and updates account
6. Updated balance reflected throughout the system

### Wireframes

```wireframe
+-------------------------------------------------------------+
| Header                                                      |
+-------------------------------------------------------------+
| Sidebar            |  Category Tabs                         |
|                    |  [Banking] [Loans] [Investments] [Bills]|
| Dashboard          |                                        |
| Accounts           |  BANKING ACCOUNTS                      |
| Bills              |  +------------------------+            |
| Income             |  | Checking Account       |            |
| Reports            |  | Current Balance: $1,250|            |
|                    |  | Available: $1,250      |            |
|                    |  | [Update] [Transactions]|            |
|                    |  +------------------------+            |
|                    |                                        |
|                    |  +------------------------+            |
|                    |  | Credit Card            |            |
|                    |  | Balance: $350          |            |
|                    |  | Available: $4,650      |            |
|                    |  | [Make Payment] [View]  |            |
|                    |  +------------------------+            |
|                    |                                        |
|                    |  + Add Account                         |
+-------------------------------------------------------------+
| Footer                                                      |
+-------------------------------------------------------------+
```

```wireframe
+-------------------------------------------------------------+
| Header                                                      |
+-------------------------------------------------------------+
| Sidebar            |  Add New Account                       |
|                    |                                        |
| Dashboard          |  Select Account Category:              |
| Accounts           |                                        |
| Bills              |  [Banking] [Loans] [Investments] [Bills]|
| Income             |                                        |
| Reports            |  Select Account Type:                  |
|                    |                                        |
|                    |  [Checking] [Savings] [Credit]         |
|                    |  [BNPL]     [EWA]     [Payment App]    |
|                    |                                        |
|                    |  Enter Account Details:                |
|                    |  +-----------------------------+       |
|                    |  | Account Form Fields         |       |
|                    |  +-----------------------------+       |
|                    |                                        |
|                    |  [Cancel]        [Create Account]      |
+-------------------------------------------------------------+
| Footer                                                      |
+-------------------------------------------------------------+
```

## Technical Details

### Architecture Overview

The account types frontend implementation follows a component-based architecture using React with TypeScript. It leverages Material-UI for a consistent visual design, Redux Toolkit for state management, React Query for API communication, and React Hook Form for form handling. The architecture supports dynamic component loading based on account type, allowing for specialized interfaces while maintaining a consistent user experience.

### Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **UI Component Library**: Material-UI v5
- **State Management**: Redux Toolkit
- **API Communication**: React Query
- **Form Handling**: React Hook Form with Yup validation
- **Routing**: React Router v6
- **Data Visualization**: Recharts
- **Testing**: Jest, React Testing Library, Cypress

### Component Structure

```typescript
interface AccountFormProps {
  initialData?: AccountFormData;
  accountType: string;
  onSubmit: (data: AccountFormData) => Promise<void>;
  onCancel: () => void;
}

const AccountForm: React.FC<AccountFormProps> = ({
  initialData,
  accountType,
  onSubmit,
  onCancel
}) => {
  // Implementation that loads type-specific components
  // and handles common form logic
};
```

The frontend components will be organized in a hierarchical structure:

```tree
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

### State Management

The application uses Redux Toolkit for state management with a domain-driven slice architecture:

```typescript
// Account slice with support for polymorphic account types
const accountsSlice = createSlice({
  name: 'accounts',
  initialState,
  reducers: {
    addAccount: (state, action: PayloadAction<Account>) => {
      accountsAdapter.addOne(state, action.payload);
    },
    updateAccount: (state, action: PayloadAction<Update<Account>>) => {
      accountsAdapter.updateOne(state, action.payload);
    },
    removeAccount: (state, action: PayloadAction<string>) => {
      accountsAdapter.removeOne(state, action.payload);
    },
    setAccounts: (state, action: PayloadAction<Account[]>) => {
      accountsAdapter.setAll(state, action.payload);
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchAccounts.fulfilled, (state, action) => {
      accountsAdapter.setAll(state, action.payload);
      state.loading = false;
    });
    // Additional async action handlers
  }
});
```

### API Integration

We'll implement a robust API client to interact with the backend services:

```typescript
// API client for account operations
const accountsApi = {
  getAccounts: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.accountType) params.append('account_type', filters.accountType);
    if (filters.category) params.append('category', filters.category);
    
    const response = await axios.get(`/api/accounts?${params.toString()}`);
    return response.data;
  },
  
  getAccount: async (accountId: string) => {
    const response = await axios.get(`/api/accounts/${accountId}`);
    return response.data;
  },
  
  createAccount: async (accountData: AccountCreateData) => {
    const response = await axios.post('/api/accounts', accountData);
    return response.data;
  },
  
  updateAccount: async (accountId: string, accountData: Partial<AccountUpdateData>) => {
    const response = await axios.put(`/api/accounts/${accountId}`, accountData);
    return response.data;
  },
  
  deleteAccount: async (accountId: string) => {
    const response = await axios.delete(`/api/accounts/${accountId}`);
    return response.data;
  }
};
```

### Form Validation

We'll implement robust form validation using React Hook Form with Yup schemas:

```typescript
// Example validation schema for a mortgage account
const mortgageAccountSchema = yup.object({
  name: yup.string().required('Account name is required'),
  institution: yup.string().required('Institution name is required'),
  account_number: yup.string().optional(),
  account_type: yup.string().oneOf(['mortgage']).required(),
  original_loan_amount: yup
    .number()
    .positive('Loan amount must be positive')
    .required('Original loan amount is required'),
  interest_rate: yup
    .number()
    .min(0, 'Interest rate cannot be negative')
    .max(30, 'Interest rate is too high')
    .required('Interest rate is required'),
  term_months: yup
    .number()
    .integer('Term must be a whole number')
    .min(1, 'Term must be at least 1 month')
    .required('Loan term is required'),
  payment_amount: yup
    .number()
    .positive('Payment amount must be positive')
    .required('Payment amount is required'),
  payment_due_day: yup
    .number()
    .integer('Payment day must be a whole number')
    .min(1, 'Payment day must be between 1 and 31')
    .max(31, 'Payment day must be between 1 and 31')
    .required('Payment due day is required'),
  property_address: yup.string().required('Property address is required'),
  property_type: yup
    .string()
    .oneOf(['single_family', 'condo', 'townhouse', 'multi_family', 'mobile_home', 'other'])
    .required('Property type is required'),
  is_primary_residence: yup.boolean().required(),
  mortgage_type: yup
    .string()
    .oneOf(['fixed', 'arm', 'balloon', 'interest_only', 'reverse'])
    .required('Mortgage type is required')
});
```

### Performance Optimizations

We'll implement several performance optimizations to ensure a smooth user experience:

```typescript
// Virtualized list for efficient rendering of many accounts
const AccountList: React.FC<AccountListProps> = ({ accounts, onSelect }) => {
  const sortedAccounts = useMemo(() => 
    [...accounts].sort((a, b) => a.name.localeCompare(b.name)),
    [accounts]
  );
  
  // Virtualized list for performance with large datasets
  return (
    <List height={500} width="100%" itemCount={sortedAccounts.length} itemSize={72}>
      {({ index, style }) => {
        const account = sortedAccounts[index];
        return (
          <ListItem 
            style={style} 
            key={account.id}
            button
            onClick={() => onSelect(account)}
          >
            <ListItemAvatar>
              <Avatar>{getAccountIcon(account.account_type)}</Avatar>
            </ListItemAvatar>
            <ListItemText 
              primary={account.name} 
              secondary={`${formatCurrency(account.current_balance)} • ${account.institution}`} 
            />
          </ListItem>
        );
      }}
    </List>
  );
};

// Memoized selectors for efficient state derivation
const selectAccountsByCategory = createSelector(
  [selectAccounts, (_, category) => category],
  (accounts, category) => accounts.filter(account => getAccountCategory(account.account_type) === category)
);

// Code splitting for account type components
const CheckingAccountForm = React.lazy(() => import('./banking/CheckingAccountForm'));
const SavingsAccountForm = React.lazy(() => import('./banking/SavingsAccountForm'));
const CreditAccountForm = React.lazy(() => import('./banking/CreditAccountForm'));
```

### Accessibility Features

We'll implement comprehensive accessibility features throughout the interface:

```typescript
// Accessible account card component example
const AccessibleAccountCard: React.FC<AccountCardProps> = ({ account, onEdit, onDelete }) => {
  return (
    <Card
      aria-labelledby={`account-title-${account.id}`}
      tabIndex={0}
    >
      <CardHeader
        id={`account-title-${account.id}`}
        title={account.name}
        subheader={account.institution}
        aria-describedby={`account-balance-${account.id}`}
      />
      <CardContent>
        <Typography 
          id={`account-balance-${account.id}`}
          variant="h6"
        >
          Balance: {formatCurrency(account.current_balance)}
        </Typography>
        {/* Account type-specific content */}
      </CardContent>
      <CardActions>
        <Button
          startIcon={<EditIcon />}
          onClick={onEdit}
          aria-label={`Edit ${account.name}`}
        >
          Edit
        </Button>
        <Button
          startIcon={<DeleteIcon />}
          onClick={onDelete}
          aria-label={`Delete ${account.name}`}
        >
          Delete
        </Button>
      </CardActions>
    </Card>
  );
};
```

### Security Considerations

We'll implement robust security measures throughout the interface:

```typescript
// Input sanitization for account data
const sanitizeAccountInput = (data: any): AccountFormData => {
  return {
    name: DOMPurify.sanitize(data.name),
    institution: DOMPurify.sanitize(data.institution),
    account_number: data.account_number ? DOMPurify.sanitize(data.account_number) : undefined,
    account_type: DOMPurify.sanitize(data.account_type),
    // Type-specific fields would be sanitized based on the account type
    ...sanitizeTypeSpecificFields(data),
  };
};

// CSRF protection for API requests
axios.interceptors.request.use(config => {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (token) {
    config.headers['X-CSRF-Token'] = token;
  }
  return config;
});

// Permission checking for sensitive operations
const canEditAccount = (account: Account, user: User): boolean => {
  return account.user_id === user.id || user.roles.includes('admin');
};
```

## Consequences

### Positive

1. **Consistent User Experience**: Users will have a unified experience across all account types while still benefiting from specialized features for each account category.

2. **Improved Discoverability**: The category-based organization makes it easier for users to find and add the specific account types they need.

3. **Enhanced Visualization**: Type-specific displays provide more relevant information for each account type, improving financial clarity for users.

4. **Simplified Maintenance**: The component architecture makes it easier to add new account types in the future without significant code changes.

5. **Comprehensive Financial View**: The integrated dashboard provides a holistic view of the user's financial situation across diverse account types.

6. **Better Data Entry**: Type-specific forms capture exactly the right data for each account type, improving data quality.

7. **Specialized Analysis**: Category-specific analysis tools (like debt payoff calculators) provide more valuable insights for each financial domain.

### Negative

1. **Implementation Complexity**: The comprehensive approach requires significant frontend development effort with many specialized components.

2. **Performance Considerations**: Dynamic component loading and specialized visualizations may impact performance on slower devices.

3. **Testing Overhead**: Each account type requires separate testing for forms, displays, and integrations, increasing QA requirements.

4. **Increased Bundle Size**: Supporting many account types could increase the application bundle size without careful code splitting.

5. **Maintenance Challenge**: Future updates need to maintain compatibility across all account type implementations.

### Neutral

1. **Learning Curve**: Users may need time to learn how to navigate the expanded account type system.

2. **UI Customization**: The specialized displays may make it harder for users to customize their view preferences.

3. **Feature Discovery**: Users may not initially discover all account type-specific features without guidance.

4. **Integration Requirements**: Backend API changes will require corresponding frontend updates to maintain compatibility.

## Quality Considerations

- **Component Reusability**: The architecture emphasizes reusable components and patterns to minimize redundancy.
- **Type Safety**: TypeScript interfaces ensure consistent data handling across account types.
- **Design Consistency**: Material-UI components provide a consistent visual language despite varying account features.
- **Testing Coverage**: Each account type component requires comprehensive unit and integration testing.
- **Documentation**: Component documentation is essential given the complexity of type-specific implementations.
- **Code Organization**: Clear directory structure separates account type concerns while maintaining consistent patterns.

## Performance and Resource Considerations

### Initial Load and Bundle Size

- **Baseline Metrics**:
  - Target initial load time: < 2.5 seconds on 4G connection
  - Target main bundle size: < 250KB (gzipped)
  - Target first contentful paint: < 1.5 seconds

- **Code Splitting Strategy**:
  - Split account type components by category
  - Lazy load type-specific forms only when needed
  - Implement route-based code splitting

- **Rendering Performance**:
  - Virtualized lists for account collections with > 20 items
  - Memoization for complex calculations and derived data
  - Optimized re-rendering with proper component boundaries

- **Data Fetching and Caching**:
  - Implement stale-while-revalidate pattern with React Query
  - Cache account type definitions and registry data
  - Batch API requests for dashboard data

### Mobile Optimization

- Target bundle size for mobile: < 200KB (gzipped)
- Progressive enhancement for complex visualizations
- Touch-optimized UI elements with appropriate sizing
- Battery-friendly animations and transitions

### Performance Monitoring

- Implement Real User Monitoring (RUM) for account type operations
- Track rendering times for different account types
- Monitor bundle size impact of new account type additions
- Establish performance budgets for critical user flows

## Development Considerations

### Implementation Effort

- **Estimated Development Time**: 10 weeks total
  - Core infrastructure: 2 weeks
  - Banking account types: 2 weeks
  - Loan account types: 2 weeks
  - Investment account types: 2 weeks
  - Bills/Obligations account types: 2 weeks

### Team Structure

- 2 frontend developers (React/TypeScript)
- 1 UI/UX designer
- 1 QA engineer
- Coordination with backend team

### Implementation Challenges

- Balancing consistency with type-specific functionality
- Managing complex form validation across diverse account types
- Ensuring performance with dynamic component loading
- Cross-browser compatibility for specialized visualizations

### Testing Requirements

- Unit tests for all account type components
- Integration tests for form submission flows
- Visual regression tests for account type displays
- End-to-end tests for key user journeys
- Accessibility testing across all account types

## Security and Compliance Considerations

- Implement input validation for all account type forms
- Sanitize user input to prevent XSS attacks
- Enforce proper authorization for account operations
- Ensure sensitive account data is properly masked
- Implement audit logging for account operations
- Comply with WCAG 2.1 accessibility guidelines

## Timeline

### Phase 1: Core Infrastructure (Weeks 1-2**

- Account type registry implementation
- Common component architecture
- API client integration
- Base form and display components
- Account creation flow

### Phase 2: Banking Accounts (Weeks 3-4**

- Checking, savings, and credit account components
- BNPL, EWA, and payment app account components
- Banking overview dashboard
- Balance update workflows

### Phase 3: Loans and Obligations (Weeks 5-6**

- Mortgage, auto, personal, and student loan components
- Debt payoff visualization tools
- Payment scheduling interfaces
- Loan comparison tools

### Phase 4: Investments (Weeks 7-8**

- Brokerage, retirement, and HSA account components
- Investment performance visualization
- Holdings management interface
- Asset allocation charts

### Phase 5: Dashboard Integration (Weeks 9-10**

- Comprehensive financial dashboard
- Cross-account analysis tools
- Mobile optimization
- Performance testing and optimization

## Monitoring & Success Metrics

### User Engagement Metrics

- Account creation completion rate (target: >90%)
- Average time to add a new account (target: <2 minutes)
- Account type distribution across users
- Dashboard engagement time

### Performance Metrics

- Form submission success rate (target: >98%)
- Average page load time (target: <2 seconds)
- API response time (target: <300ms)
- Client-side rendering time (target: <100ms)

### Business Impact Metrics

- Increase in accounts added per user (target: +30%)
- Reduction in support tickets related to account management (target: -40%)
- Improvement in user financial visibility (measured via surveys)
- Increase in feature usage across account types

## Team Impact

- **Development Team**: Higher initial development effort, but improved maintainability long-term
- **Design Team**: Need for comprehensive design system with account type variations
- **QA Team**: Increased testing scope across diverse account types
- **Support Team**: Potential reduction in support tickets with better UX
- **Product Team**: Better ability to implement targeted financial features

## Related Documents

- [ADR-016: Account Type Expansion - Foundation](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-019: Banking Account Types Expansion](/code/debtonator/docs/adr/backend/019-banking-account-types-expansion.md)
- [ADR-020: Loan Account Types Expansion](/code/debtonator/docs/adr/backend/020-loan-account-types-expansion.md)
- [ADR-021: Investment Account Types Expansion](/code/debtonator/docs/adr/backend/021-investment-account-types-expansion.md)
- [ADR-022: Bills and Obligations Account Types Expansion](/code/debtonator/docs/adr/backend/022-bills-and-obligations-account-types-expansion.md)
- [Frontend Component Guidelines](/code/debtonator/docs/frontend/component-guidelines.md)
- [Accessibility Requirements](/code/debtonator/docs/frontend/accessibility.md)

## Notes

### Accessibility Considerations

The account type UI implementation will prioritize accessibility:

1. **Screen Reader Compatibility**:
   - All form fields will have appropriate labels
   - Charts and visualizations will include text alternatives
   - Complex components will use ARIA attributes appropriately
   - Keyboard navigation will be fully supported

2. **Visual Accessibility**:
   - Color schemes will adhere to WCAG contrast requirements
   - Icons will include text labels or tooltips
   - Text sizes will be adjustable
   - All information conveyed by color will also be available without color

3. **Cognitive Accessibility**:
   - Forms will include clear validation messages
   - Complex financial concepts will include explanations
   - Step-by-step flows will guide users through complex tasks
   - Consistent patterns will be used throughout the interface

### Mobile UI Optimization

The account type UI will be optimized for mobile devices:

1. **Responsive Layout**:
   - Forms will adapt to smaller screens
   - Tables will convert to card layouts on mobile
   - Touch targets will be appropriately sized
   - Content will be prioritized for mobile views

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
| 2025-04-11 | 1.0 | Debtonator Team | Initial draft |
| 2025-04-21 | 1.1 | Debtonator Team | Updated to follow standardized template structure |
