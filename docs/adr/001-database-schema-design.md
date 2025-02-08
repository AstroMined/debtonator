# ADR-001: Database Schema Design

## Status

Proposed

## Context

- Converting Excel-based financial tracking system to web application
- 8+ years of historical data (2017-2025)
- Complex relationships between bills, income, and cashflow
- Need to maintain data integrity and calculation accuracy
- Must support future features like real-time updates and mobile access

### Key Considerations
- Historical data preservation (4,970 bills, 528 income records)
- Account balance tracking
- Payment status history
- Recurring bill patterns
- Complex calculations and forecasting
- Multiple account types (AMEX, UFCU, Unlimited)

## Decision

Propose a normalized database schema with the following core tables:

### Bills
```sql
CREATE TABLE bills (
    id INTEGER PRIMARY KEY,
    month VARCHAR(10),
    day_of_month INTEGER,
    due_date DATE,
    paid_date DATE,
    bill_name VARCHAR(255),
    amount DECIMAL(10,2),
    up_to_date BOOLEAN,
    account_id INTEGER,
    auto_pay BOOLEAN,
    paid BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### Income
```sql
CREATE TABLE income (
    id INTEGER PRIMARY KEY,
    date DATE,
    source VARCHAR(255),
    amount DECIMAL(10,2),
    deposited BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Accounts
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50),
    type VARCHAR(20),
    available_balance DECIMAL(10,2),
    available_credit DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### AccountTransactions
```sql
CREATE TABLE account_transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    bill_id INTEGER NULL,
    income_id INTEGER NULL,
    amount DECIMAL(10,2),
    transaction_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (income_id) REFERENCES income(id)
);
```

### RecurringBills
```sql
CREATE TABLE recurring_bills (
    id INTEGER PRIMARY KEY,
    bill_name VARCHAR(255),
    amount DECIMAL(10,2),
    day_of_month INTEGER,
    account_id INTEGER,
    auto_pay BOOLEAN,
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### CashflowForecasts
```sql
CREATE TABLE cashflow_forecasts (
    id INTEGER PRIMARY KEY,
    date DATE,
    total_bills DECIMAL(10,2),
    total_income DECIMAL(10,2),
    balance DECIMAL(10,2),
    forecast DECIMAL(10,2),
    min_14_day DECIMAL(10,2),
    min_30_day DECIMAL(10,2),
    min_60_day DECIMAL(10,2),
    min_90_day DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Technical Details

### Implementation Approach

1. Development Database:
   - SQLite for initial development
   - Simple setup and portability
   - No configuration needed

2. Production Database:
   - MySQL/MariaDB for production
   - Better performance for concurrent access
   - More robust backup solutions

### Migration Strategy
1. Create schema in SQLite
2. Develop migration scripts
3. Import historical data
4. Verify data integrity
5. Plan MySQL migration

### Indexing Strategy
```sql
-- Bills table indexes
CREATE INDEX idx_bills_due_date ON bills(due_date);
CREATE INDEX idx_bills_paid_date ON bills(paid_date);
CREATE INDEX idx_bills_account_id ON bills(account_id);

-- Income table indexes
CREATE INDEX idx_income_date ON income(date);
CREATE INDEX idx_income_deposited ON income(deposited);

-- Account transactions indexes
CREATE INDEX idx_transactions_date ON account_transactions(transaction_date);
CREATE INDEX idx_transactions_account ON account_transactions(account_id);

-- Cashflow forecasts indexes
CREATE INDEX idx_forecasts_date ON cashflow_forecasts(date);
```

## Consequences

### Positive
- Normalized structure prevents data redundancy
- Clear relationships between entities
- Easy to extend for future features
- Supports historical data preservation
- Enables efficient querying
- Maintains data integrity

### Negative
- More complex than current Excel structure
- Requires careful migration planning
- Need to maintain referential integrity
- May require more complex queries for some calculations

### Neutral
- Different calculation approach needed
- Will require stored procedures or application logic
- Need to handle timezone considerations
- Regular backup strategy required

## Performance Impact
- Indexed queries should perform well
- May need optimization for large datasets
- Consider caching for frequent calculations
- Monitor query performance during development

## Cost Considerations
- Free open-source databases
- Low infrastructure requirements
- Development time for migration
- Testing and validation effort

## Compliance & Security
- Financial data requires encryption
- Access control needed
- Audit trail for changes
- Regular backups required

## Dependencies
- SQLite for development
- MySQL/MariaDB for production
- Backup solution
- Migration tools

## Timeline
1. Schema implementation: 1 week
2. Migration scripts: 1 week
3. Testing and validation: 1 week
4. Production deployment: 1 week

## Monitoring & Success Metrics
- Data integrity checks
- Query performance metrics
- Migration success rate
- Application performance

## Team Impact
- Training on new schema
- Documentation requirements
- Testing procedures
- Operational procedures

## Related Documents
- Project Brief
- Technical Context
- System Patterns

## Notes
- Consider versioning for schema changes
- Plan for future extensibility
- Document all constraints and relationships
- Maintain Excel backup during transition

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-02-08 | 1.0 | Cline | Initial version |
