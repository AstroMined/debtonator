# ADR 005: Bills Table UI/UX Enhancements

## Status

Accepted

## Context

The Bills Table component needed improvements in several areas:
- Split payment visualization was not intuitive
- Mobile responsiveness needed enhancement
- Performance with large datasets needed optimization
- Visual feedback for payment status and overdue bills needed improvement

## Decision

We decided to enhance the Bills Table component with:

1. Split Payment Visualization
   - Added tooltips to show split payment details
   - Enhanced account column rendering with primary/split indicators
   - Improved visual distinction between primary and split amounts

2. Mobile Responsiveness
   - Implemented smart column hiding based on screen size
   - Kept essential columns visible on mobile (status, amount, primary account)
   - Adjusted column widths dynamically

3. Performance Optimization
   - Added row virtualization
   - Optimized memo dependencies
   - Enhanced rendering efficiency for large datasets

4. Visual Feedback
   - Added distinct styling for overdue rows
   - Enhanced status indicators with more detailed tooltips
   - Improved payment status visualization

## Consequences

### Positive

1. Better User Experience
   - Clearer visualization of split payments
   - More intuitive mobile interface
   - Better performance with large datasets
   - Enhanced visual feedback

2. Maintainability
   - Better organized component code
   - Improved type safety
   - More efficient rendering logic

3. Accessibility
   - Better tooltip information
   - Enhanced keyboard navigation
   - Improved mobile usability

### Negative

1. Increased Complexity
   - More complex column management logic
   - Additional state management considerations
   - More sophisticated rendering optimizations

2. Testing Requirements
   - Need for additional test cases
   - More complex mobile testing scenarios
   - Performance testing requirements

## Technical Details

1. Column Management
```typescript
const columns = useMemo(() => {
  const defaultColumns = getDefaultColumns();
  if (isMobile) {
    return defaultColumns.filter((col: GridColDef) => 
      !col.field.startsWith('account_') || 
      col.field === `account_${accounts[0]?.id}`
    );
  }
  return defaultColumns;
}, [isMobile, accounts]);
```

2. Split Payment Display
```typescript
renderCell: (params: GridRenderCellParams<BillTableRow>) => {
  const amount = params.row.splitAmounts?.[account.id] || 
    (params.row.account_id === account.id ? params.row.amount : 0);
  const isMainAccount = params.row.account_id === account.id;
  
  return (
    <Tooltip title={isMainAccount ? 'Primary Account' : 'Split Payment'}>
      <Box>
        {formatCurrency(amount)}
      </Box>
    </Tooltip>
  );
}
```

3. Performance Optimization
```typescript
sx={{
  '& .MuiDataGrid-virtualScroller': {
    overflowX: 'hidden',
  },
  '& .MuiDataGrid-columnHeader': {
    minWidth: isMobile ? 100 : 120,
  },
}}
```

## Related

- ADR-003: Dynamic Accounts and Bill Splits
- ADR-004: Bills Table Dynamic Accounts
