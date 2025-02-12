# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2025-02-09

### Fixed
- Test infrastructure improvements
  - Fixed database setup in unit tests
  - Resolved async session handling issues
  - Improved test fixtures
  - Enhanced error handling in tests
  - Fixed greenlet spawn errors
  - Improved transaction handling

### Added
- Test coverage analysis and reporting
  - Generated coverage reports (70% overall)
  - Identified critical areas needing tests
  - Mapped coverage gaps in API endpoints
  - Analyzed service layer coverage
  - Documented well-covered areas (>90%)
  - Identified areas needing improvement

## [0.4.2] - 2025-02-09

### Fixed
- Test infrastructure improvements
  - Fixed circular imports in model relationships
  - Enhanced model dependency management
  - Improved test database setup
  - Added proper test session handling
- Model relationship improvements
  - Fixed circular dependencies in models
  - Enhanced type hints for relationships
  - Improved model initialization order
  - Better dependency management

## [0.4.1] - 2025-02-09

### Fixed
- Test infrastructure improvements
  - Fixed test client configuration for API endpoints
  - Enhanced debug logging for test failures
  - Improved response content handling in tests
  - Fixed JSON formatting in test data
- API endpoint routing
  - Fixed router prefix handling
  - Improved URL path consistency
  - Enhanced debug logging for route registration

## [0.4.0] - 2025-02-09

### Added
- Enhanced income management system
  - Added positive amount validation with database constraint
  - Improved account balance handling for deposits
  - Added proper balance recalculation for income updates
  - Enhanced account-based income filtering
  - Added consistent URL handling for API endpoints

### Fixed
- Account balance updates for income changes
  - Proper balance recalculation when updating deposited income
  - Fixed balance updates for new deposits
  - Improved error handling for invalid amounts
- API endpoint consistency
  - Fixed URL handling with consistent trailing slashes
  - Improved error responses for validation failures
  - Enhanced filtering parameter handling

### Enhanced
- Test coverage expansion
  - Added comprehensive income API integration tests
  - Enhanced income service unit tests
  - Added balance update validation tests
  - Improved test data setup and assertions

## [0.3.4] - 2025-02-09

### Fixed
- Test infrastructure improvements
  - Fixed SQLite foreign key constraint handling
  - Enhanced test database configuration with proper constraints
  - Improved test fixtures with complete data setup
  - Added proper SQLAlchemy text() usage for raw SQL
- Model relationship fixes
  - Added account_id to Income model with migration
  - Created proper back-reference in Account model
  - Enhanced bill fixtures with required fields
- Calculation improvements
  - Fixed daily deficit calculation rounding
  - Ensured consistent decimal handling
  - Improved test assertions for calculations

## [0.3.3] - 2025-02-09

### Added
- Comprehensive backend test infrastructure
  - Pytest test suite with async support
  - Test database configuration with SQLite
  - Reusable test fixtures for database and API clients
  - Proper test isolation and cleanup

### Enhanced
- Account API improvements
  - Added proper status codes (201 for creation)
  - Implemented enum-based validation for account types
  - Added PATCH support for partial updates
  - Enhanced error handling and validation

### Added
- Unit tests for Account model
  - Account creation validation
  - Balance calculations
  - Credit limit handling
  - Available credit updates
- Integration tests for Account API
  - CRUD operations testing
  - Input validation testing
  - Error handling scenarios
  - Status code compliance

## [0.3.2] - 2025-02-09

### Enhanced
- Bills component performance optimization
  - Improved memoization with useCallback for event handlers
  - Enhanced Redux integration with type-safe hooks
  - Optimized bulk payment updates with batch processing
  - Added optimistic updates for better UX
  - Improved error handling with local error state
  - Enhanced TypeScript type safety
  - Reduced unnecessary re-renders
  - Better state management for pending updates
  - Efficient data fetching with proper loading states

## [0.3.1] - 2025-02-09

### Fixed
- Bill splits validation and creation
  - Fixed primary account amount calculation
  - Improved split amount validation
  - Enhanced error handling for splits
  - Fixed response validation for bill operations
- System integration issues
  - Resolved account management validation
  - Fixed bill creation with splits
  - Improved balance tracking accuracy

### Changed
- Enhanced bill splits implementation
  - Primary account amount now calculated as (total - splits)
  - Automatic split creation for primary account
  - Improved validation error messages
  - Better error handling for edge cases

## [0.3.0] - 2025-02-09

### Added
- Bulk import functionality for bills and income
  - Support for CSV and JSON file formats
  - File upload interface with drag-and-drop support
  - Data validation and preview before import
  - Progress tracking and error reporting
  - Import status notifications
  - Documentation for import file formats

### Changed
- Enhanced bills and income tables with import capabilities
- Updated API endpoints to handle bulk data imports
- Improved error handling for data validation

## [0.2.0] - 2025-02-09

### Added
- Enhanced balance tracking system
  - Real-time balance history tracking (last 30 entries)
  - Visual balance change indicators with up/down arrows
  - Color-coded balance status
  - Expandable account details in accounts table
  - Credit account-specific information display
  - Balance history state management
    - Efficient state updates with Redux Toolkit
    - Memoized balance calculations
    - Optimistic UI updates
    - Type-safe state handling

### Added
- Enhanced navigation structure and user interface
  - Added breadcrumb navigation for better context
  - Implemented active route highlighting
  - Created collapsible account summary in sidebar
    - Total balance display with color indicators
    - Available credit tracking
    - Individual account balances
    - Collapsible sections for better organization
  - Improved mobile navigation drawer
  - Added sticky positioning for better UX
  - Enhanced visual feedback for current location
  - Version display in sidebar footer

### Enhanced
- Bills state management with advanced features
  - Normalized state structure using Record<id, item>
  - Real-time calculations with memoized selectors
  - Optimistic updates with automatic rollback
  - Comprehensive pending updates tracking
  - Enhanced TypeScript type safety
  - Efficient filtering and calculations
  - New selectors for:
    - Pending updates status
    - Optimistic calculations
    - Bill filtering by multiple criteria
    - Account-specific bill totals
  - Improved error handling with rollback
  - Automatic state recalculation
  - Performance optimizations:
    - Memoized selectors
    - Normalized state
    - Efficient updates
    - Batched calculations

## [Previous Changes]

### Added
- Global state management with Redux Toolkit
  - Type-safe state implementation with TypeScript
  - Domain-specific slices for accounts, bills, income, and cashflow
  - Efficient selectors with memoization
  - Real-time state synchronization
  - Comprehensive state management for:
    - Account balances and limits
    - Bill payments and splits
    - Income deposits and tracking
    - Cashflow forecasts and calculations
  - Enhanced performance through optimized re-renders
  - Improved data consistency across components

### Added
- Account management interface implementation
  - Account table/grid view with dynamic data display
  - Balance and credit limit tracking visualization
  - Statement balance history tracking
  - Mobile-responsive design
  - Error handling with user feedback
  - Loading state management
  - Real-time updates
- Frontend service layer for account management
  - API endpoint integration for CRUD operations
  - Error handling with proper user feedback
  - Data transformation utilities
  - Type-safe interfaces
  - Currency formatting utilities

### Added
- Enhanced cashflow visualization with interactive charts
  - 90-day rolling forecast chart with date range selection
  - Account balance trends chart with toggle functionality
  - Required funds comparison chart with period selection
  - Cross-account balance comparison with real-time updates
  - Interactive tooltips with detailed data points
  - Mobile-responsive chart layouts
  - Brush component for date range selection
  - Legend toggles for account visibility
  - Visual deficit/surplus indicators
  - Recharts integration for smooth animations
  - Memoized calculations for performance
  - Error handling with fallback UI
  - Loading states with skeleton placeholders
- Frontend service layer enhancements
  - Historical data fetching with date range support
  - Account-specific balance history tracking
  - Real-time data updates with 5-minute polling
  - Data transformation utilities for chart formatting
  - Error handling with proper user feedback

### Added
- Income tracking interface implementation
  - Income entry form with validation
  - Income list/grid view with filtering and sorting
  - Deposit status tracking
  - Target account selection
  - Error handling with user feedback
  - Loading state management
  - Mobile responsive design
  - Real-time updates
- Frontend service layer for income management
  - API endpoint integration
  - Error handling
  - Loading states
  - Deposit status management
  - Target account selection
- Frontend service layer for bills management
  - API endpoint integration
  - Error handling with proper user feedback
  - Loading state management
  - Payment status management
  - Split payment support
  - Real-time updates
- Error boundary implementation
  - Global error boundary component
  - Graceful error recovery
  - User-friendly error messages
  - Retry functionality
- Enhanced Bills Table UI/UX (ADR-005)
  - Improved split payment visualization with tooltips and indicators
  - Enhanced mobile responsiveness with smart column management
  - Added row virtualization for better performance
  - Improved visual feedback for payment status and overdue bills
  - Added detailed tooltips for payment information
  - Enhanced accessibility with better keyboard navigation

### Changed
- Major architectural change to support dynamic accounts instead of hard-coded account names
- Added new bill_splits table to support splitting bills across multiple accounts
- Updated bill entry form to support dynamic account selection and bill splits
- Added accounts API endpoints for managing accounts
- Improved database schema to be more flexible and maintainable
- Updated frontend components to handle dynamic accounts and split payments
- Enhanced form validation for split payment totals
- Enhanced Bills Table/Grid view with dynamic account support
  - Replaced hard-coded account columns with dynamic columns
  - Added split payment display and tracking
  - Improved payment status management with bulk actions
  - Enhanced mobile responsiveness for dynamic columns
  - Added advanced filtering and sorting capabilities

### Added
- New account management features
  - CRUD operations for accounts
  - Balance tracking
  - Credit limit management
- Bill splitting functionality
  - Support for splitting bills across multiple accounts
  - Split amount validation
  - Split payment tracking
- Dynamic account selection in forms
- API endpoints for managing accounts and bill splits
- Migration path for existing data
- New ADR documenting the architectural change

### Technical Details
- Removed hard-coded account columns (amex_amount, unlimited_amount, ufcu_amount)
- Added bill_splits table with proper relationships and constraints
- Implemented database migration with data preservation
- Added new API endpoints for account management
- Updated frontend components for dynamic account handling
- Enhanced validation for split payment totals
- Added comprehensive test coverage for new features

## [0.1.0] - 2024-02-08

### Added
- Bills Table/Grid component
  - Material-UI DataGrid integration
  - Sortable columns with custom sorting
  - Payment status toggle with visual feedback
  - Status indicators (paid/unpaid/overdue)
  - Currency formatting for amounts
  - Auto-pay status indicators
  - Mobile-responsive design
  - Loading states and error handling
  - Default sorting by due date
  - Customized cell rendering
  - Tooltip information
  - Keyboard navigation support
  - Account-specific amount columns
  - Paid date tracking and display
  - Days overdue calculation with tooltip display
  - Bulk payment actions with selection model
  - Advanced filtering with GridToolbar
  - Dynamic column visibility for mobile
  - Pagination with configurable page size
  - Striped rows for better readability

- Bill Entry Form component
  - Form validation with Formik and Yup
  - Material-UI form controls
  - Date picker with historical date support
  - Account selection dropdown
  - Auto-pay toggle switch
  - Amount validation with decimal places
  - Mobile-responsive layout
  - Error handling and feedback
  - Support for editing existing bills
  - Unit tests with Jest and React Testing Library

- Frontend layout foundation
  - Material-UI integration with custom theme
  - Responsive navigation system
  - Top app bar with mobile menu toggle
  - Sidebar with navigation links
  - Mobile-friendly drawer
  - Page container with proper spacing
  - Theme configuration
  - Custom color palette
  - Typography settings
  - Component style overrides

### Changed
- Converted from Excel-based system to database schema
- Updated bill tracking to use proper relationships
- Enhanced account management with transaction tracking
- Implemented versioned API structure (v1)
- Updated project documentation to include frontend setup
- Enhanced development workflow with frontend tooling
- Removed date restrictions to support historical data entry
