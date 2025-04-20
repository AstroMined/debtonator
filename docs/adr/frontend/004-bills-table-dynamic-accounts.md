# ADR 004: Bills Table Dynamic Account Support

## Status

Proposed (very rough draft based on old backend architecture, needs significant updates)

## Context

The Bills Table/Grid view component initially used hard-coded account columns (AMEX, Unlimited, UFCU) for displaying bill amounts. This approach was:
- Inflexible for different account configurations
- Not reusable across different users
- Difficult to maintain as account structures change
- Inconsistent with the new dynamic account management system

## Decision

We decided to enhance the Bills Table/Grid view to support dynamic account columns and bill splits by:

1. Removing hard-coded account columns
2. Implementing dynamic column generation based on available accounts
3. Adding support for split payment display
4. Enhancing the mobile responsiveness for dynamic columns

### Technical Implementation

1. **Dynamic Column Generation**
   - Account columns are generated from the list of available accounts
   - Each account gets its own column with proper formatting
   - Column visibility is configurable based on screen size

2. **Split Payment Display**
   - Added splitAmounts mapping in the BillTableRow type
   - Implemented logic to show either split amount or full amount based on account
   - Enhanced tooltips to show split payment details

3. **Mobile Optimization**
   - Implemented responsive column visibility
   - Primary account and auto-pay columns hide on mobile
   - Maintained essential columns for mobile view

4. **Data Management**
   - Added proper TypeScript types for bill splits
   - Implemented null checks for optional fields
   - Enhanced error handling for undefined values

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
```

## Consequences

### Positive

1. **Flexibility**
   - Support for any number of accounts
   - Easy to add/remove account columns
   - Adaptable to different account structures

2. **Maintainability**
   - Reduced code duplication
   - Easier to update column logic
   - Better type safety with TypeScript

3. **User Experience**
   - Clearer split payment visualization
   - Better mobile experience
   - More intuitive account management

4. **Performance**
   - Optimized column rendering
   - Efficient split amount calculations
   - Better memory usage

### Negative

1. **Complexity**
   - More complex column generation logic
   - Additional type checking required
   - More sophisticated state management

2. **Learning Curve**
   - New developers need to understand dynamic column system
   - More complex testing requirements
   - Additional documentation needed

## Alternatives Considered

1. **Configurable Fixed Columns**
   - Would allow some customization
   - Still not truly dynamic
   - Wouldn't support arbitrary account numbers

2. **Nested Column Groups**
   - More complex UI structure
   - Harder to maintain
   - Poor mobile experience

3. **Separate Mobile View**
   - Duplicated logic
   - Inconsistent user experience
   - Higher maintenance burden

## Additional Context

This change aligns with ADR-003 (Dynamic Accounts and Bill Splits) by implementing the frontend visualization of the dynamic account system. It completes the transition from hard-coded accounts to a fully dynamic account management system.
