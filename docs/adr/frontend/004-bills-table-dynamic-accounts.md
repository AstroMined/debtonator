# ADR-004: Bills Table Dynamic Account Support

## Status

Accepted

## Executive Summary

This ADR defines the implementation of a dynamic Bills Table component that generates columns based on available user accounts rather than using hard-coded account columns. By removing fixed account references, implementing dynamic column generation, adding support for bill splits visualization, and enhancing mobile responsiveness, this architecture enables flexible bill management across any number of accounts while providing an intuitive user experience for both single and split payments.

## Context

The Bills Table/Grid view component initially used hard-coded account columns (AMEX, Unlimited, UFCU) for displaying bill amounts. This approach presented several limitations:

- Inflexible for different account configurations, limiting user customization
- Not reusable across different users with varying account structures
- Difficult to maintain as account structures change or expand
- Inconsistent with the new dynamic account management system from ADR-003
- Poor experience for mobile users with many accounts
- No support for visualizing bill splits across multiple accounts

These limitations prevented users from effectively managing bills across their actual accounts and created code maintenance challenges as we scale to support more diverse financial situations. The rigid column structure also made it impossible to support the bill splitting functionality introduced in our backend.

## Decision

We will enhance the Bills Table/Grid view to support dynamic account columns and bill splits by:

1. Removing hard-coded account columns in favor of dynamic generation
2. Implementing flexible column generation based on available user accounts
3. Adding support for split payment visualization
4. Enhancing mobile responsiveness for dynamic column management
5. Improving TypeScript type safety for bill and account data structures

### User Stories

#### Category 1: Account Visualization

##### **US-1.1: Dynamic Account Columns**

- As a user, I want to see columns for each of my actual accounts in the bills table
- So that I can understand which bills are assigned to which accounts

##### **US-1.2: Account Filtering**

- As a user, I want to filter the bills table to show only bills for specific accounts
- So that I can focus on managing bills for particular accounts

#### Category 2: Bill Split Visualization

##### **US-2.1: Split Payment Visibility**

- As a user, I want to clearly see when a bill is split across multiple accounts
- So that I can understand how my bills are distributed

##### **US-2.2: Split Amount Details**

- As a user, I want to see the specific amount allocated to each account for split bills
- So that I can verify the split is configured correctly

#### Category 3: Mobile Responsiveness

##### **US-3.1: Mobile-Optimized View**

- As a mobile user, I want the bills table to adapt to my smaller screen
- So that I can effectively manage my bills on mobile devices

##### **US-3.2: Prioritized Information**

- As a mobile user, I want the most important bill information visible by default
- So that I can quickly see critical bill data without horizontal scrolling

### User Interface and Click Paths

#### Primary View: Bills Table

**Elements:**

- Bill details (name, due date, amount, status)
- Dynamic account columns with amounts
- Status indicators for paid/unpaid bills
- Split payment indicators
- Action buttons (pay, edit, delete)
- Filtering controls

##### **Click Path:** Viewing Bill Splits

1. User navigates to Bills page
2. Bills table loads with dynamic account columns
3. User sees split bills with multiple values across account columns
4. User hovers over a split amount to see tooltip with details
5. Split amounts sum to total bill amount for verification

##### **Click Path:** Filtering Bills by Account

1. User clicks on account filter dropdown
2. User selects specific account(s) from available options
3. Table refreshes to show only bills with assignments to selected accounts
4. User can reset filter to show all bills again

### Wireframes

```wireframe
+-------------------------------------------------------------+
| Bills Table                                  [Filter ▼] [+]  |
+-------------------------------------------------------------+
| Bill     | Amount  | Due     | Status  | Account Columns... |
|          |         |         |         | Chase | Amex | UFCU |
+-------------------------------------------------------------+
| Rent     | $1,500  | 1st     | Unpaid  | $1,500|  -   |  -   |
| Electric | $120    | 15th    | Paid ✓  | $120  |  -   |  -   |
| Credit   | $800    | 25th    | Unpaid  |  -    | $800 |  -   |
| Internet | $80     | 10th    | Unpaid  | $40   |  -   | $40  |
+-------------------------------------------------------------+
|                  Showing 4 bills  |  Paid: 1  Unpaid: 3     |
+-------------------------------------------------------------+
```

The Internet bill row shows a split payment across two accounts (Chase and UFCU).

Mobile-optimized view:

```wireframe
+----------------------------+
| Bills Table         [+]    |
+----------------------------+
| Bill     | Amount  | Due   |
+----------------------------+
| Rent     | $1,500  | 1st   |
| Electric | $120    | 15th  |
| Credit   | $800    | 25th  |
| Internet | $80     | 10th  |
+----------------------------+
| Account: [All Accounts ▼]  |
+----------------------------+
```

On mobile, account columns collapse and are accessible through a filter dropdown.

## Technical Details

### Architecture Overview

The Bills Table component follows a data-driven approach where columns are generated dynamically based on available accounts. The implementation uses a responsive design pattern that adjusts column visibility based on screen size while maintaining data consistency across all views.

### Technology Stack

- **React with TypeScript**: Strong typing for component props and state
- **Material-UI**: Grid and responsive layout components
- **Redux**: State management for bills and accounts data
- **React Query**: Data fetching and caching
- **CSS Media Queries**: Responsive design adjustments

### Component Structure

```typescript
interface BillTableRow extends Bill {
  status: BillStatus;
  daysOverdue: number;
  splitAmounts?: { [accountId: number]: number };
}

interface BillsTableProps {
  bills: Bill[];
  accounts: Account[];
  onPaymentToggle: (billId: number, paid: boolean) => void;
  onBulkPaymentToggle?: (billIds: number[], paid: boolean) => void;
  loading?: boolean;
}

const BillsTable: React.FC<BillsTableProps> = ({
  bills,
  accounts,
  onPaymentToggle,
  onBulkPaymentToggle,
  loading = false
}) => {
  // Column generation logic
  const columns = useMemo(() => {
    // Base columns (bill name, amount, due date, status)
    const baseColumns = [
      /* ... */
    ];
    
    // Generate dynamic account columns
    const accountColumns = accounts.map(account => ({
      field: `account_${account.id}`,
      headerName: account.name,
      width: 120,
      renderCell: (params: GridCellParams) => {
        const bill = params.row as BillTableRow;
        const splitAmount = bill.splitAmounts?.[account.id];
        
        // Different rendering for primary account, split accounts, etc.
        if (bill.primaryAccountId === account.id) {
          // Render primary account cell
        } else if (splitAmount) {
          // Render split amount cell
        } else {
          // Render empty cell
        }
      },
      // Hide on smaller screens based on priority
      hide: account.isPrimary ? false : window.innerWidth < 768
    }));
    
    return [...baseColumns, ...accountColumns];
  }, [accounts]);
  
  return (
    <div className="bills-table-container">
      <DataGrid
        rows={bills}
        columns={columns}
        loading={loading}
        checkboxSelection
        onSelectionModelChange={handleSelectionChange}
        components={{
          Toolbar: BillsTableToolbar,
          NoRowsOverlay: EmptyBillsMessage
        }}
      />
    </div>
  );
};
```

### State Management

The implementation leverages Redux for managing bill and account data:

```typescript
// In bills slice
interface BillsState {
  items: Bill[];
  loading: boolean;
  error: string | null;
  splitAmounts: Record<number, Record<number, number>>;
}

// Selectors
export const selectBillSplitAmounts = (state: RootState, billId: number) => 
  state.bills.splitAmounts[billId] || {};

export const selectBillWithSplits = createSelector(
  [(state: RootState) => state.bills.items, selectBillSplitAmounts],
  (bills, splitAmounts) => bills.map(bill => ({
    ...bill,
    splitAmounts: splitAmounts[bill.id] || {}
  }))
);

// In accounts slice
export const selectActiveAccounts = (state: RootState) =>
  state.accounts.items.filter(account => account.isActive);
```

### API Integration

```typescript
// Data fetching with React Query
const { data: bills, isLoading: billsLoading } = useQuery(
  ['bills'],
  () => api.getBills(),
  {
    select: (data) => processBillData(data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  }
);

const { data: accounts, isLoading: accountsLoading } = useQuery(
  ['accounts'],
  () => api.getAccounts(),
  {
    select: (data) => data.filter(account => account.isActive),
    staleTime: 5 * 60 * 1000, // 5 minutes
  }
);

// Process data to include split information
const processBillData = (bills: Bill[]): BillTableRow[] => {
  return bills.map(bill => {
    // Calculate split amounts for each account
    const splitAmounts = bill.splits.reduce((acc, split) => {
      acc[split.accountId] = split.amount;
      return acc;
    }, {} as Record<number, number>);
    
    return {
      ...bill,
      status: calculateBillStatus(bill),
      daysOverdue: calculateDaysOverdue(bill),
      splitAmounts
    };
  });
};
```

### Form Validation

The implementation includes validation for bill splits to ensure they always sum to the total bill amount:

```typescript
const validateSplitAmounts = (splits: BillSplit[], totalAmount: number): boolean => {
  const sum = splits.reduce((acc, split) => acc + split.amount, 0);
  return Math.abs(sum - totalAmount) < 0.01; // Account for floating point precision
};
```

### Performance Optimizations

1. **Virtualized Grid**: Only renders visible rows for better performance with large datasets
2. **Memoized Columns**: Column definitions are memoized to prevent unnecessary recalculations
3. **Responsive Column Hiding**: Less important columns are hidden on smaller screens
4. **Pagination**: Server-side pagination for large bill datasets
5. **Data Normalization**: Normalized data structure in Redux store

### Accessibility Features

1. **Screen Reader Support**: Properly labeled grid cells and headers
2. **Keyboard Navigation**: Full keyboard support for navigating the table
3. **High Contrast Mode**: Compatible with high contrast settings
4. **Text Sizing**: Supports browser text size adjustments
5. **Clear Split Indicators**: Visual and text indicators for split bills

### Security Considerations

1. **Input Sanitization**: All user inputs are sanitized before display
2. **Data Validation**: Account IDs and bill IDs are validated before use
3. **Proper Typing**: TypeScript interfaces reduce potential for runtime errors
4. **Error Handling**: Graceful error handling for missing or invalid data

## Consequences

### Positive

1. **Flexibility**
   - Support for any number of accounts without code changes
   - Easy to add/remove account columns based on user configuration
   - Adaptable to different account structures and user preferences
   - Compatible with any future account types from ADR-016

2. **Maintainability**
   - Reduced code duplication through dynamic generation
   - Better separation of data and presentation concerns
   - Improved type safety with TypeScript interfaces
   - More testable component structure

3. **User Experience**
   - Clearer visualization of bill assignments across accounts
   - Intuitive representation of split payments
   - Better experience across device sizes
   - More personalized view based on user's actual accounts

4. **Performance**
   - Optimized column rendering with virtualization
   - Efficient handling of large bill datasets
   - Better memory usage through normalized data structures
   - Responsive adjustments without full re-renders

### Negative

1. **Implementation Complexity**
   - More complex column generation logic compared to fixed columns
   - Additional edge cases to handle with dynamic data
   - More sophisticated state management requirements
   - Need for careful responsive design considerations

2. **Learning Curve**
   - New developers need to understand the dynamic column system
   - Additional testing complexity for variable column configurations
   - More comprehensive documentation requirements
   - Higher initial development effort

3. **Testing Overhead**
   - Need to test across multiple account configurations
   - Edge cases with various split payment scenarios
   - Responsive testing across different screen sizes
   - Accessibility testing for dynamic content

### Neutral

1. **Data Requirements**
   - Needs complete account data before rendering efficiently
   - Requires additional split amount calculations
   - May need server-side adjustments for efficient data loading
   - Changes the expected data structure for bills

## Quality Considerations

- **Code Organization**: The implementation follows a clear separation of concerns between data processing, column generation, and rendering logic
- **Type Safety**: Comprehensive TypeScript interfaces prevent common runtime errors
- **Reusability**: Components are designed for reuse in other parts of the application
- **Testing**: Unit tests cover dynamic column generation and bill split calculations
- **Documentation**: Inline documentation explains the dynamic column architecture and data requirements

## Performance and Resource Considerations

- **Initial Load Time**: The dynamic column approach adds minimal overhead (~20ms) to initial render time
- **Memory Usage**: Normalized data structure reduces memory footprint for large datasets
- **Render Efficiency**: Memoized columns and virtualized grid ensure smooth scrolling
- **Network Requests**: Optimized data fetching with React Query reduces unnecessary API calls
- **Mobile Performance**: Responsive optimizations ensure good performance on mobile devices

## Development Considerations

- **Implementation Effort**: Estimated 2-3 weeks for complete implementation
- **Team Members**: Requires 1 frontend developer with React/TypeScript experience
- **Integration Points**: Needs coordination with backend API for bill split data structure
- **Testing Requirements**: Comprehensive test suite for various account configurations
- **Documentation Needs**: Technical documentation and usage examples for other developers

## Security and Compliance Considerations

- **Data Exposure**: Only authorized account data is displayed in the table
- **Input Validation**: All user inputs are validated before processing
- **Error Handling**: Graceful error handling for API failures
- **Secure Data Transmission**: Uses HTTPS for all API requests
- **Audit Logging**: Changes to bill assignments are logged for audit purposes

## Timeline

- **Design Phase**: 1 week (wireframes, component structure, data model)
- **Implementation Phase**: 2 weeks (core functionality, testing)
- **Testing Phase**: 1 week (unit tests, integration tests)
- **Documentation Phase**: 3 days (developer documentation, user guidance)
- **Total Duration**: Approximately 4 weeks

## Monitoring & Success Metrics

- **Usability Testing**: Track time to complete common bill management tasks
- **Error Rates**: Monitor error rates in bill assignment and split creation
- **Performance Monitoring**: Track render times across different account configurations
- **User Feedback**: Collect user feedback on the clarity of bill/account relationships
- **Support Tickets**: Measure reduction in support tickets related to bill management

## Team Impact

- **Frontend Team**: Needs to understand the dynamic column architecture
- **Backend Team**: Must ensure API provides necessary account and bill split data
- **QA Team**: Requires test cases for various account configurations
- **Documentation Team**: Update user guides for bill management features
- **Training**: Brief training session for customer support on explaining the new UI

## Related Documents

- [ADR-003: Dynamic Accounts and Bill Splits](/code/debtonator/docs/adr/archive/003-dynamic-accounts-and-bill-splits.md)
- [ADR-008: Bill Splits Implementation](/code/debtonator/docs/adr/archive/008-bill-splits-implementation.md)
- [ADR-016: Account Type Expansion](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- Frontend Component Design Documentation (in development)

## Notes

During the implementation planning, we identified several key considerations:

1. The dynamic column approach should scale well for users with up to 10-15 accounts, which covers our target user base.
2. For users with more accounts, we'll implement column prioritization based on account usage and primary status.
3. Split bill visualization needs to be intuitive without cluttering the UI for users who don't use split payments.
4. The mobile experience prioritizes essential information while making account-specific details available through additional interactions.

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2024-08-15 | 0.1 | Original Author | Initial draft with basic approach |
| 2025-04-21 | 1.0 | Frontend Team | Updated to match template with comprehensive details |
