# Debtonator v1.0.0

A modern bill and cashflow management system that helps track bills, income, and maintain sufficient account balances for timely bill payments.

[Previous sections remain unchanged until Project Structure]

## Project Structure

```
debtonator/
├── alembic/              # Database migrations
├── docs/                 # Project documentation
│   ├── adr/             # Architecture Decision Records
│   └── ...              # Other documentation
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Redux store and slices
│   │   │   └── slices/  # Feature-specific slices
│   │   └── types/       # TypeScript types
│   └── ...
├── src/                 # Backend application
│   ├── api/            # API endpoints
│   ├── models/         # Database models
│   │   ├── liabilities.py  # Bill tracking (liabilities)
│   │   ├── payments.py     # Payment and source tracking
│   │   └── ...            # Other models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── utils/          # Utilities
└── tests/              # Test suites
    ├── unit/          # Unit tests
    │   └── test_*.py  # Model and service tests
    └── integration/   # Integration tests
        └── test_*.py  # API endpoint tests
```

## Core Architecture

### Double-Entry Payment Tracking
The system uses a modified double-entry accounting approach with three core entities:

1. **Liabilities (Bills)**
   - Represent what is owed
   - Track due dates and amounts
   - Support recurring patterns
   - Categorization support

2. **Payments (Transactions)**
   - Record actual payments made
   - Link to bills (optional)
   - Support non-bill expenses
   - Track payment dates

3. **Payment Sources (Entries)**
   - Track which accounts funded payments
   - Support split payments
   - Maintain account balance accuracy

This architecture provides:
- Clear separation of bills and payments
- Better support for complex payment scenarios
- Natural fit for non-bill expenses
- Improved historical tracking
- Better analytics capabilities
- More flexible payment handling

[Previous sections remain unchanged until Architecture Decisions]

## Architecture Decisions

- [Database Schema Design](docs/adr/001-database-schema-design.md)
- [Historical Data Entry](docs/adr/002-historical-data-entry.md)
- [Dynamic Accounts and Bill Splits](docs/adr/003-dynamic-accounts-and-bill-splits.md)
- [Bills Table Dynamic Accounts](docs/adr/004-bills-table-dynamic-accounts.md)
- [Bills Table UI/UX Enhancements](docs/adr/005-bills-table-enhancements.md)
- [Redux Toolkit State Management](docs/adr/006-redux-toolkit-state-management.md)
- [Bulk Import Functionality](docs/adr/007-bulk-import-functionality.md)
- [Bill Splits Implementation](docs/adr/008-bill-splits-implementation.md)
- [Bills/Payments Separation](docs/adr/009-bills-payments-separation.md)

[Previous sections remain unchanged]
