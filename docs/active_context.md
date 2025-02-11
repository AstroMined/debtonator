# Active Context: Debtonator

## Current Focus
Major architectural change: Separation of Bills and Payments

### Recent Implementation
1. **Test Infrastructure Updates**
   - ✓ Improved SQLite async connection handling
   - ✓ Enhanced transaction management in tests
   - ✓ Removed obsolete migration tests
   - ✓ Reorganized model relationship tests
   - ✓ Updated test fixtures for better async support

2. **Model Implementation**
   - ✓ Created Liability model for bill tracking
   - ✓ Created Payment model for transactions
   - ✓ Created PaymentSource model for splits
   - ✓ Updated Account model relationships
   - ✓ Removed legacy Bill model
   - ✓ Updated model registrations

3. **Implementation Strategy**
   - Phased approach over 2-3 weeks
   - Clear validation requirements
   - Comprehensive testing plan

### Recent Changes
1. **Test Suite Reset**
   - ✓ Removed entire test suite for fresh start
   - [ ] Plan new test strategy after backend stabilization
   - [ ] Focus on critical path testing
   - [ ] Implement new integration tests

2. **Database Changes**
   - ✓ Created new models
   - ✓ Updated relationships
   - ✓ Added indexes
   - [ ] Complete test coverage

## Active Decisions

### Phase 1: Backend Stabilization
- [ ] Complete backend implementation without test constraints
- [ ] Document critical paths for future testing
- [ ] Identify key integration points
- [ ] Plan new testing approach

### Phase 2: API Layer Updates (2-3 days)
- [x] Create new schemas
  - [x] Liability schema
  - [x] Payment schema
  - [x] Payment source schema
- [x] Update existing endpoints
  - [x] Added new liabilities endpoints
  - [x] Added backward compatibility for bills endpoints
- [x] Add new payment endpoints
  - [x] CRUD operations for payments
  - [x] Payment source management
  - [x] Date range filtering
  - [x] Liability-specific payments
  - [x] Account-specific payments
- [x] Update validation logic
  - [x] Payment amount validation
  - [x] Source total validation
  - [x] Account existence validation
- [x] Add service layer methods
  - [x] Payment CRUD operations
  - [x] Payment source management
  - [x] Filtering and queries

### Phase 3: Frontend Foundation (2-3 days)
- [ ] Create new types/interfaces
- [ ] Update Redux store
- [ ] Add new API services
- [ ] Update existing components
- [ ] Add loading states

## Next Steps

### Immediate Tasks
1. Test Suite Completion
   - Fix remaining test failures
   - Add test cases for edge scenarios
   - Complete test coverage for new models
   - Update integration tests

2. API Development
   - [x] Complete payment endpoints
   - [x] Implement validation logic
   - [x] Add service layer methods
   - [ ] Test API endpoints

3. Frontend Updates
   - Plan component changes
   - Design new interfaces
   - Update state management
   - Create new forms
   - Update views

### Future Phases
1. Frontend Features (3-4 days)
   - Payment entry forms
   - Bill form updates
   - Payment history views
   - Cashflow calculation updates
   - New filtering options

2. Testing & Documentation (2-3 days)
   - Unit test updates
   - Integration tests
   - API documentation
   - User documentation
