# ADR 009: Separation of Bills and Payments

## Status
Proposed

## Context
The current implementation tightly couples bills with their payment methods, making it difficult to handle:
- Split payments across time periods
- Different payment sources for the same bill
- Non-scheduled transactions (e.g., groceries)
- Historical payment tracking
- Future expansion to general financial transaction tracking

## Decision
Implement a modified double-entry accounting approach with three core entities:

1. Bills (Liabilities)
   - Represent what is owed
   - Track due dates and amounts
   - Support recurring patterns
   - Categorization support

2. Payments (Transactions)
   - Record actual payments made
   - Link to bills (optional)
   - Support non-bill expenses
   - Track payment dates

3. Payment Sources (Entries)
   - Track which accounts funded payments
   - Support split payments
   - Maintain account balance accuracy

### Schema Changes

```sql
CREATE TABLE bills (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    amount DECIMAL(10,2),
    due_date DATE,
    description TEXT,
    recurring BOOLEAN,
    recurrence_pattern JSON,
    category VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    bill_id INTEGER NULL,
    amount DECIMAL(10,2),
    payment_date DATE,
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(id)
);

CREATE TABLE payment_sources (
    id INTEGER PRIMARY KEY,
    payment_id INTEGER,
    account_id INTEGER,
    amount DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

## Implementation Phases

### Phase 1: Database Changes
- Create new tables
- Create migration scripts
- Update database models
- Add new indexes
- Write data migration tests

### Phase 2: API Layer Updates
- Create new schemas for bills/payments
- Update existing endpoints
- Add new payment endpoints
- Update validation logic
- Add new service layer methods

### Phase 3: Frontend Foundation
- Create new types/interfaces
- Update Redux store
- Add new API services
- Update existing components
- Add loading states

### Phase 4: Frontend Features
- Add payment entry forms
- Update bill forms
- Add payment history views
- Update cashflow calculations
- Add new filtering options

### Phase 5: Testing & Documentation
- Update unit tests
- Add integration tests
- Update API documentation
- Update user documentation
- Add migration guide

## Consequences

### Positive
- Clear separation of bills and payments
- Better support for complex payment scenarios
- Natural fit for non-bill expenses
- Improved historical tracking
- Better analytics capabilities
- More flexible payment handling
- Easier to extend for future features

### Negative
- More complex data model
- Migration effort required
- Additional API endpoints needed
- More complex frontend state management
- Additional validation requirements

### Neutral
- Changes to calculation methods needed
- Different approach to balance tracking
- Updated backup procedures required

## Technical Impact
- Database schema changes
- API endpoint updates
- Frontend component updates
- New service layer methods
- Updated testing requirements

## Migration Strategy
1. Create new tables
2. Migrate existing bill data
3. Create payment records
4. Update frontend components
5. Validate data integrity
6. Deploy in phases

## Validation & Testing
- Data migration tests
- API endpoint tests
- Frontend integration tests
- Balance calculation tests
- Payment validation tests

## Timeline
- Phase 1: 1-2 days
- Phase 2: 2-3 days
- Phase 3: 2-3 days
- Phase 4: 3-4 days
- Phase 5: 2-3 days

Total: 10-15 days (2-3 weeks)

## Related
- ADR-001: Database Schema Design
- ADR-003: Dynamic Accounts and Bill Splits
- ADR-008: Bill Splits Implementation
