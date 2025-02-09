# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
