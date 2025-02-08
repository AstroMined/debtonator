# Active Context: Debtonator

## Current Focus
Implementing API endpoints and business logic for the bill and cashflow management system. Database schema has been implemented with all necessary models, relationships, and indexes.

## Recent Analysis

### Spreadsheet Structure
1. **Bills Sheet**
   - 4,970 rows of historical data (2017-2025)
   - 13 columns tracking bill details
   - Complex formulas for account-specific calculations
   - Conditional formatting for payment status
   - Notable patterns:
     * Regular bills (e.g., "Helping Hands" $560)
     * Utilities (AT&T, COA)
     * Rent payments
     * Mixed payment methods (Auto Pay vs Manual)

2. **Income Sheet**
   - 528 rows of income records
   - 5 key columns for income tracking
   - Formulas for calculating undeposited amounts
   - Date-based organization
   - Key income sources:
     * Regular employment (ScienceLogic: $2,887.92)
     * Recurring payments (Mom Rent: $250)
     * Historical sources (Fire Dept, Capitol Courier)

3. **Cashflow Sheet**
   - 890 rows of cashflow data
   - Special calculations in first 5 rows
   - Rolling 90-day forecast
   - Complex SUMPRODUCT formulas for totals
   - Account tracking:
     * AMEX available credit
     * UFCU available balance
     * Unlimited available credit
     * Pending deposits

### Key Formulas Identified

#### Bills
```excel
Due Date = DATEVALUE(CONCATENATE(Month,"/",Day,"/25"))
Account Amount = IF(Account="AMEX",IF(Paid="Yes",0,Amount),0)
```

#### Income
```excel
Undeposited = IF(Deposited="No",Amount,0)
```

#### Cashflow
```excel
Min Period = MIN(I8:I22)  # 14-day minimum
Daily Deficit = IF(MinPeriod<0,MinPeriod/14,0)
Yearly Deficit = DailyDeficit*365
Required Income = (ABS(YearlyDeficit)/0.8)
Hourly Rate = RequiredIncome/52/hours
```

## Active Decisions

### Database Design
- ✓ Using SQLite for development
- ✓ Schema matches Excel structure
- ✓ Proper indexing implemented
- ✓ Relationships and constraints defined

### API Structure (In Progress)
- Define RESTful endpoints for each model
- Implement calculation endpoints
- Add real-time update capabilities
- Enforce strong validation rules

### Frontend Architecture
- React-based SPA
- Component-based design
- Real-time calculations
- Mobile-first approach

## Next Steps

### Immediate Tasks
1. ✓ Set up development environment
   - Python virtual environment with UV
   - SQLite database with async support
   - Configuration management (.env)
   - FastAPI project structure
2. ✓ Implement database schema
   - Created core SQLAlchemy models (bills, income, accounts)
   - Added supporting models (transactions, recurring bills, forecasts)
   - Set up Alembic migrations
   - Implemented relationships and foreign keys
   - Added performance indexes
   - Implemented calculation methods
3. Design and implement API endpoints
   - Bills management endpoints (CRUD operations)
   - Income tracking endpoints (CRUD operations)
   - Account management endpoints (CRUD operations)
   - Cashflow calculation endpoints
4. Create data migration tools
   - Excel data extraction script
   - Data transformation utilities
   - Database import procedures
   - Data validation checks

### Technical Planning
1. Design API Endpoints
   - Define RESTful routes for each model
   - Plan calculation endpoints
   - Document request/response schemas
   - Define validation rules

2. Plan Business Logic
   - Bill creation/update workflows
   - Income tracking process
   - Transaction handling
   - Cashflow calculation logic

3. Testing Strategy
   - Unit tests for models and calculations
   - Integration tests for API endpoints
   - Test data generation
   - Performance testing approach

4. Frontend Architecture
   - Component hierarchy
   - State management
   - API integration patterns
   - Real-time update strategy

### Documentation Needs
1. API documentation
2. Database schema documentation
3. Component documentation
4. Testing documentation

## Known Issues

### Data Migration Challenges
- Date format conversions (handling dates from 2017-2025)
- Formula translations (especially SUMPRODUCT and complex IF conditions)
- Historical data preservation (maintaining 8+ years of records)
- Data validation rules
- Account balance history reconstruction
- Payment status history preservation
- Auto-pay configuration migration

### Technical Challenges
- Real-time calculations
- Mobile responsiveness
- State management
- Performance optimization

## Current Questions
1. How to handle real-time updates efficiently?
2. Best approach for recurring bill creation?
3. Optimal state management solution?
4. Most efficient way to implement calculations?
5. How to handle historical vs future dates in calculations?
6. What's the best way to track payment method changes?
7. How to maintain account balance accuracy with pending transactions?
8. Should we maintain the 80% tax consideration in income requirements?
9. How to handle bill amount changes for recurring bills?
10. What's the best way to implement the 14/30/60/90 day forecasting?

## Risk Assessment

### High Priority
- Data integrity during migration
- Calculation accuracy
- Performance with large datasets
- Mobile user experience

### Medium Priority
- State management complexity
- API design scalability
- Testing coverage
- Documentation completeness

### Low Priority
- UI/UX refinements
- Additional features
- Performance optimizations
- Analytics implementation
