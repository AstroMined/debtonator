# ADR 002: Support for Historical Data Entry in Forms

## Status

Deprecated

## Context

When implementing the Bill Entry Form, we initially restricted date selection to future dates only. However, this limitation conflicted with several important use cases:

1. Data Migration Support
   - The project requires preserving historical data since 2017
   - Migration tools are specifically built to handle historical records
   - Manual data entry might be needed for missing or incorrect historical records

2. Business Requirements
   - Users need to record bills that were missed in the system but already paid
   - Historical record keeping is crucial for financial tracking
   - Backlogged data entry during initial system setup
   - Correction of data entry mistakes discovered later

3. Cashflow Analysis
   - Historical payment data is essential for identifying patterns and trends
   - Past records help in forecasting future cashflow needs
   - Complete financial history improves analysis accuracy

## Decision

We decided to remove date restrictions and allow historical data entry in forms, specifically:

1. Removed the `disablePast` prop from Material-UI DatePicker components
2. Eliminated the `.min(new Date())` validation from Yup schemas
3. Maintained date format validation and null checks
4. Added support for historical dates in form state management

## Consequences

### Positive

1. Better support for data migration and historical record keeping
2. Improved user experience for correcting past entries
3. More accurate financial analysis with complete historical data
4. Flexibility in handling various data entry scenarios
5. Consistency with Excel-based system's capabilities

### Negative

1. Slightly increased complexity in date validation
2. Need for additional UI feedback to distinguish historical entries
3. Potential for accidental historical entries

### Mitigations

1. Clear UI indicators for historical dates
2. Proper validation messages
3. Comprehensive unit tests for date handling
4. Documentation of date handling behavior

## Related Decisions

- ADR 001: Database Schema Design

## Notes

- Future enhancements might include:
  - Audit trails for historical entries
  - Visual indicators for backdated entries
  - Reporting features for historical data analysis
