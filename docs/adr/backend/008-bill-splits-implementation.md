# ADR 008: Bill Splits Implementation

## Status
Proposed (very rough draft based on old backend architecture, needs significant updates)

## Context
The bill splits feature needed enhancement to properly handle primary account amounts and validation. The original implementation had issues with split amount validation and didn't properly handle the primary account's portion of the bill.

## Decision
We decided to:
1. Calculate primary account amount as (total bill amount - sum of splits)
2. Automatically create a split entry for the primary account
3. Enhance validation to ensure:
   - Split amounts sum up to total bill amount
   - All account references are valid
   - No negative split amounts
4. Improve error handling and response validation
5. Implement proper schema validation for bill creation and updates

## Technical Details
- Primary account split is created automatically after other splits
- Split amounts are validated before any database operations
- Response schemas properly handle split relationships
- Error messages provide clear guidance for validation issues
- Optimistic updates in frontend handle split calculations

## Consequences

### Positive
- More reliable bill split creation and validation
- Clear error messages for validation issues
- Consistent handling of primary account amounts
- Better data integrity for split payments
- Improved user experience with clear feedback

### Negative
- Slightly more complex bill creation process
- Additional database operations for primary account splits
- More complex state management for optimistic updates

## Implementation Notes
- Updated BillService to handle primary account splits
- Enhanced validation in bills schema
- Added split-specific error handling
- Improved response validation
- Updated frontend components to handle new split logic

## Related
- ADR-003: Dynamic Accounts and Bill Splits
- ADR-004: Bills Table Dynamic Accounts
