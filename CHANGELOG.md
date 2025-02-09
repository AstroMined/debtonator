# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Cashflow visualization implementation
  - Basic forecast display with key metrics
  - Account balance overview
  - Required funds indicators for different time periods (14/30/60/90 days)
  - Real-time data updates with 5-minute polling
  - Mobile-responsive metric cards
  - Error handling with user feedback
  - Loading state management
- Frontend service layer for cashflow management
  - API endpoint integration for forecast data
  - Date range filtering support
  - Error handling with proper user feedback
  - Data transformation utilities

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
