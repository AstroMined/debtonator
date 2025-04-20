# ADR 003: Dynamic Accounts and Bill Split Management

## Status

Deprecated

## Context

The initial implementation used hard-coded account names (AMEX, UFCU, Unlimited) in the database schema and frontend components. This approach limited the application's flexibility and reusability for different users with different account structures.

## Decision

We decided to:

1. Remove hard-coded account references from the database schema
2. Implement a dynamic account management system
3. Create a new bill_splits table to support splitting bills across multiple accounts
4. Update the frontend to dynamically fetch and display available accounts

### Technical Details

1. Database Changes:
   - Removed account-specific amount columns (amex_amount, unlimited_amount, ufcu_amount)
   - Added bill_splits table with relationships to bills and accounts
   - Maintained account_id foreign key in bills table for primary account

2. Schema Structure:

   ```sql
   CREATE TABLE bill_splits (
       id INTEGER PRIMARY KEY,
       bill_id INTEGER REFERENCES bills(id),
       account_id INTEGER REFERENCES accounts(id),
       amount DECIMAL(10,2),
       created_at DATE,
       updated_at DATE,
       UNIQUE(bill_id, account_id)
   )
   ```

3. API Changes:
   - Added accounts API endpoints for CRUD operations
   - Updated bills API to handle split payments
   - Added bill splits API endpoints

4. Frontend Changes:
   - Dynamic account selection in forms
   - Support for split payment entry
   - Updated bill display to show split information

## Consequences

### Positive

1. Application is now more flexible and can be used by any user with any account structure
2. Better separation of concerns with dedicated account management
3. More accurate modeling of bill payments that are split across accounts
4. Improved data normalization and database design
5. Easier to add new accounts or modify existing ones
6. Frontend components are more reusable and maintainable

### Negative

1. Increased complexity in bill management logic
2. Additional database queries needed for split information
3. More complex frontend forms for split payment entry
4. Migration needed for existing data

### Mitigations

1. Implemented efficient database indexing
2. Created clear API documentation
3. Added validation for split payment totals
4. Provided migration path for existing data

## References

- Database schema design documentation
- FastAPI endpoint documentation
- Frontend component specifications
