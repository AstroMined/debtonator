# Active Context: Debtonator

## Current Focus
Major architectural change to support dynamic accounts and bill splits, improving flexibility and reusability of the application. Frontend components and database schema have been updated to remove hard-coded account references.

## Recent Changes

### Dynamic Account Management
1. **Database Schema**
   - Removed hard-coded account columns
   - Added bill_splits table
   - Improved data normalization
   - Migration path implemented

2. **API Implementation**
   - New accounts API endpoints
   - Updated bills API for splits
   - Bill splits API endpoints
   - Validation for split totals

3. **Frontend Updates**
   - Dynamic account selection
   - Split payment support
   - Updated bill display
   - Improved form validation

## Active Decisions

### Database Design
- ✓ Using SQLite for development
- ✓ Schema matches Excel structure
- ✓ Proper indexing implemented
- ✓ Relationships and constraints defined
- ✓ Dynamic account support
- ✓ Bill splits functionality

### API Structure
- ✓ Bills API endpoints implemented
  - CRUD operations
  - Date range filtering
  - Unpaid bills filtering
  - Payment status management
  - Split payment support
- ✓ Income API endpoints implemented
  - CRUD operations
  - Deposit status tracking
  - Undeposited amount calculations
- ✓ Cashflow API endpoints implemented
  - Forecast calculations
  - Account balance tracking
  - Minimum required calculations
- ✓ Accounts API endpoints implemented
  - CRUD operations
  - Balance tracking
  - Credit limit management

### Frontend Architecture
- ✓ React-based SPA with TypeScript
- ✓ Vite for build tooling
- ✓ Component-based design
- ✓ Testing setup with Jest and React Testing Library
- ✓ ESLint and Prettier for code quality
- ✓ Material-UI integration
- ✓ Mobile-first approach
- ✓ Base layout components
- ✓ Dynamic account management
- ✓ Bill split support
- Real-time calculations

## Next Steps

### Immediate Tasks
1. ✓ Set up development environment
2. ✓ Implement database schema
3. ✓ Design and implement bills API endpoints
4. ✓ Implement income API endpoints
5. ✓ Implement cashflow API endpoints
6. ✓ Create data migration tools
7. ✓ Set up frontend development environment
8. ✓ Implement base layout components
9. ✓ Implement dynamic account management
10. Feature component development
    - Bills management interface
      - ✓ Bill entry form with split support
      - ✓ Bills list/grid view with dynamic accounts
        - Dynamic account columns
        - Split payment display
        - Payment status management
        - Mobile responsive design
      - ✓ Payment status updates
      - ✓ Auto-pay management
    - Income tracking interface
      - Income entry form
      - Income list view
      - Deposit status tracking
    - Cashflow visualization
      - Forecast charts
      - Account balance displays
      - Required funds indicators

### Technical Planning
1. ✓ Design API Endpoints
2. ✓ Plan Business Logic
3. ✓ Frontend Layout Foundation
4. ✓ Bill Entry Form Implementation
5. ✓ Dynamic Account Management

6. Feature Components
   - Component specifications
   - State management implementation
   - API integration
   - Real-time updates
   - Mobile optimization

7. Testing Strategy
   - Unit tests for components
   - Integration tests
   - E2E testing
   - Performance testing

### Documentation Needs
1. ✓ Bills API documentation
2. ✓ Income API documentation
3. ✓ Cashflow API documentation
4. ✓ Layout components documentation
5. ✓ Bill Entry Form documentation
6. ✓ Account Management documentation
7. Feature components documentation (in progress)

## Known Issues

### Technical Challenges
- Real-time calculations
- State management
- Performance optimization
- Form validation patterns
- Data caching strategy
- Account balance tracking
- ✓ Split payment validation and display

## Current Questions
1. How to handle real-time updates efficiently?
2. Best approach for recurring bill creation?
3. Optimal state management solution?
4. Most efficient way to implement calculations?
5. Best practices for data caching?
6. How to optimize component re-renders?
7. How to implement optimistic updates?
8. Strategy for error boundary implementation?
9. How to handle complex split payment scenarios?
10. Best approach for account balance reconciliation?

## Risk Assessment

### High Priority
- Component performance
- State management complexity
- Mobile user experience
- Split payment validation
- Account balance accuracy

### Medium Priority
- Testing coverage
- Documentation completeness
- Error handling
- Loading states
- Migration reliability

### Low Priority
- UI/UX refinements
- Animation implementations
- Analytics integration
- Performance optimizations
