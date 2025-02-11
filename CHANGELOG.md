# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-02-11

### Added
- Expanded test coverage for models (97% coverage)
  - Cashflow model tests with calculation validation
  - Income model tests with deposit tracking
  - RecurringBill model tests with liability creation
  - Comprehensive relationship testing
  - Default value validation
  - Edge case handling

### Fixed
- RecurringBill model now properly creates liabilities
  - Updated to work with new liability model
  - Fixed account relationship handling
  - Added proper category assignment
  - Improved test coverage

## [1.3.0] - 2025-02-10

### Added
- Comprehensive test suite for core models
  - Account model tests with different account types
  - Liability model tests with relationships
  - Payment model tests with split payments
  - Transaction-based test isolation
  - Async/await handling for SQLAlchemy
- Test infrastructure improvements
  - SQLite in-memory database for testing
  - Function-scoped fixtures
  - Transaction rollback after each test
  - Proper relationship loading
  - Clean test state management

## [1.2.0] - 2025-02-10

### Added
- Complete payment endpoints implementation
  - CRUD operations for payments
  - Payment source management
  - Date range filtering
  - Liability-specific endpoints
  - Account-specific endpoints
- Comprehensive payment validation
  - Payment amount validation
  - Source total validation
  - Account existence validation
- Payment service layer
  - Payment processing with sources
  - Bill tracking integration
  - Balance calculations
  - Source management

[Previous entries remain unchanged...]
