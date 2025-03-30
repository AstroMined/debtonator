# ADR 007: Bulk Import Functionality

## Status
Accepted

## Context
Users need the ability to import historical data for bills and income from CSV or JSON files. This is particularly important for:
- Migrating data from other financial systems
- Bulk updating historical records
- Maintaining data consistency across systems

## Decision
Implement bulk import functionality for both bills and income data with the following features:

### Data Formats
- Support CSV and JSON file formats
- Provide template downloads for correct format
- Include validation before import

### Architecture Components
1. Backend:
   - New API endpoints for bulk imports
   - Data validation and transformation services
   - Progress tracking for large imports
   - Transaction handling for data consistency

2. Frontend:
   - File upload modal component
   - Preview table for data verification
   - Validation summary display
   - Progress indicator for large imports

### Data Validation
- Match existing schema requirements
- Validate account references
- Ensure bill split consistency
- Check date formats and ranges
- Verify numerical values

### Error Handling
- Provide detailed validation errors
- Allow partial imports with valid records
- Roll back on critical failures
- Report success/failure counts

## Consequences

### Positive
- Easier data migration from other systems
- Efficient bulk data entry
- Reduced manual entry errors
- Better system interoperability

### Negative
- Increased complexity in data validation
- Need for additional error handling
- Potential performance impact with large imports
- Additional testing requirements

### Mitigations
1. Implement chunked processing for large imports
2. Add comprehensive validation before processing
3. Provide clear error messages and recovery options
4. Include progress tracking for user feedback

## Implementation Notes

### API Endpoints
```typescript
POST /api/v1/income/bulk-import
POST /api/v1/bills/bulk-import
```

### File Format Templates
```typescript
// Income CSV Format
date,source,amount,deposited,account_id

// Bills CSV Format
month,day_of_month,bill_name,amount,account_id,auto_pay,splits
```

### Validation Rules
1. Required fields must be present
2. Dates must be valid
3. Amounts must be positive numbers
4. Account IDs must exist in system
5. Bill splits must sum to total amount
6. No duplicate entries by date/name

### Error Response Format
```json
{
  "success": false,
  "errors": [
    {
      "row": 1,
      "field": "amount",
      "message": "Amount must be a positive number"
    }
  ],
  "processed": 10,
  "failed": 2,
  "succeeded": 8
}
```

## References
- [Project Brief](../project_brief.md)
- [System Patterns](../system_patterns.md)
- [Tech Context](../tech_context.md)
