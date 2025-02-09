# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

[Previous releases remain unchanged...]
