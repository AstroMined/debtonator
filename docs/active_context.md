# Active Context: Debtonator

## Current Focus
Implementing API endpoints and business logic for the bill and cashflow management system. Core bills, income, and cashflow API endpoints have been implemented. Moving on to data migration tools and frontend development.

## Recent Analysis

### API Implementation
1. **Income API**
   - CRUD operations completed
   - Deposit status tracking
   - Undeposited amount calculations
   - Date range filtering
   - Source categorization
   - Relationship with transactions

2. **Cashflow API**
   - 90-day rolling forecast
   - Minimum required funds tracking
   - Deficit calculations
   - Required income projections
   - Hourly rate calculations
   - Account balance tracking

3. **Formula Translations**
   - Income calculations implemented
     ```python
     undeposited_amount = amount if not deposited else Decimal(0)
     ```
   - Cashflow calculations implemented
     ```python
     daily_deficit = min_amount / 14 if min_amount < 0 else Decimal(0)
     yearly_deficit = daily_deficit * 365
     required_income = abs(yearly_deficit) / Decimal('0.8')
     hourly_rate = required_income / 52 / hours_per_week
     ```

## Active Decisions

### Database Design
- ✓ Using SQLite for development
- ✓ Schema matches Excel structure
- ✓ Proper indexing implemented
- ✓ Relationships and constraints defined

### API Structure
- ✓ Bills API endpoints implemented
  - CRUD operations
  - Date range filtering
  - Unpaid bills filtering
  - Payment status management
- ✓ Income API endpoints implemented
  - CRUD operations
  - Deposit status tracking
  - Undeposited amount calculations
- ✓ Cashflow API endpoints implemented
  - Forecast calculations
  - Account balance tracking
  - Minimum required calculations

### Frontend Architecture
- React-based SPA
- Component-based design
- Real-time calculations
- Mobile-first approach

## Next Steps

### Immediate Tasks
1. ✓ Set up development environment
2. ✓ Implement database schema
3. ✓ Design and implement bills API endpoints
4. ✓ Implement income API endpoints
5. ✓ Implement cashflow API endpoints
6. Create data migration tools
   - Excel data extraction script
   - Data transformation utilities
   - Database import procedures
   - Data validation checks
7. Begin frontend development
   - Set up React project
   - Design component hierarchy
   - Implement core components
   - Integrate with API

### Technical Planning
1. ✓ Design API Endpoints
   - ✓ Define RESTful routes for each model
   - ✓ Plan calculation endpoints
   - ✓ Document request/response schemas
   - ✓ Define validation rules

2. ✓ Plan Business Logic
   - ✓ Bill creation/update workflows
   - ✓ Income tracking process
   - ✓ Transaction handling
   - ✓ Cashflow calculation logic

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
1. ✓ Bills API documentation
2. ✓ Income API documentation
3. ✓ Cashflow API documentation
4. Frontend component documentation

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
