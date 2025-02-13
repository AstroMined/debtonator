# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.17] - 2025-02-12

### Added
- Integration tests for recurring bills API
  - Complete test coverage for all endpoints
  - Proper async/await patterns
  - Account validation in service layer
  - Test fixtures with model defaults
  - Edge case handling
  - Response validation
  - Bill generation testing

### Changed
- Improved test infrastructure
  - Switched to HTTPX AsyncClient for better async testing
  - Enhanced fixture management
  - Standardized timestamp handling
  - Better error handling in recurring bills service

## [0.3.16] - 2025-02-12

### Added
- Comprehensive test suite for recurring bills service
  - 100% test coverage achieved
  - Test fixtures for accounts and recurring bills
  - CRUD operation testing
  - Bill generation functionality testing
  - Edge case handling
  - Duplicate prevention testing
  - Active/inactive bill filtering tests
  - 12 test cases covering all functionality

### Changed
- Improved test infrastructure
  - Enhanced database initialization
  - Better async operation handling
  - Standardized test patterns
  - Cleaner test organization

## [Unreleased]

## [0.3.15] - 2025-02-12

### Added
- Recurring bills system
  - New recurring_bills table for bill templates
  - Support for generating liabilities from recurring patterns
  - API endpoints for managing recurring bills
  - Monthly bill generation capability
  - Proper relationship handling between accounts, recurring bills, and liabilities
  - Automatic recurring flag setting on generated liabilities
  - Support for auto-pay configuration

## [0.3.14] - 2025-02-12

### Added
- Real-time available credit calculation
  - New API endpoint for calculating available credit
  - Support for pending transaction consideration
  - Accurate credit limit tracking
  - Balance impact analysis
  - Comprehensive test coverage
  - Validation for credit account types
  - Detailed credit availability breakdown

## [0.3.13] - 2025-02-12

### Added
- Balance reconciliation system
  - New balance_reconciliation table for tracking balance adjustments
  - Support for account balance reconciliation with history
  - API endpoints for managing reconciliations
  - Automatic balance updates on reconciliation
  - Comprehensive test coverage for reconciliation service and API
  - Validation for account balance adjustments
  - Historical tracking of balance changes with reasons

## [0.3.12] - 2025-02-12

### Added
- Comprehensive API enhancement plan documented in ADR 010
- Phased approach for implementing API improvements:
  - Phase 1: Account Management Enhancement
  - Phase 2: Bill Management Expansion
  - Phase 3: Bill Splits Optimization
  - Phase 4: Income System Enhancement
  - Phase 5: Cashflow Analysis Extension
  - Phase 6: Reporting & Analysis

## [0.3.12] - 2025-02-12

### Added
- Transaction history system
  - New transaction_history table for tracking account transactions
  - Support for credit and debit transactions
  - Account relationship for transaction history
  - API endpoints for managing transactions
  - Balance impact tracking for each transaction
  - Comprehensive test coverage for transaction service
- Service layer improvements
  - Transaction service with 100% test coverage
  - Automatic balance updates on transactions
  - Proper relationship loading
  - Error handling and validation

## [0.3.11] - 2025-02-12

### Added
- Credit limit history tracking system
  - New credit_limit_history table for tracking limit changes
  - Account relationship for credit limit history
  - API endpoints for managing credit limits
  - Historical tracking of limit changes with reasons
  - Validation for credit account types

## [0.3.10] - 2025-02-12

### Added
- Statement balance history tracking system
  - New statement_history table for historical records
  - Account relationship for tracking statement history
  - API endpoints for managing statement history
  - Ordered retrieval of statement records
  - Support for minimum payments and due dates

## [0.3.9] - 2025-02-12

### Added
- Comprehensive test suite for bill splits service
- Comprehensive test suite for liabilities service
- Test fixtures for bulk import testing
- Test data files for CSV and JSON imports

### Changed
- Improved bill splits service test coverage from 32% to 100%
- Improved liabilities service test coverage from 32% to 100%
- Improved bulk import service test coverage from 31% to 91%
- Increased overall service layer coverage from 63% to 94%
- Fixed method name mismatch in bulk import service
- Enhanced error handling in bulk import service
- Improved file handling in bulk import tests

## [0.3.8] - 2025-02-12

### Added
- Comprehensive test suite for cashflow service
- Test fixtures for cashflow testing
- Test patterns for decimal precision handling

### Changed
- Improved cashflow service test coverage from 38% to 100%
- Increased overall service layer coverage from 56% to 63%
- Fixed relationship naming (income_entries → income)
- Enhanced test fixtures with required fields

## [0.3.7] - 2025-02-12

### Added
- Comprehensive test suite for income service
- Base income fixture for testing
- Test patterns for service layer testing

### Changed
- Improved income service test coverage from 19% to 86%
- Increased overall service layer coverage from 38% to 56%
- Enhanced test infrastructure with better async handling

## [0.3.6] - 2025-02-12

### Fixed
- Fixed SQLAlchemy identity map warning in payment service
- Improved payment source relationship handling
- Enhanced session management in payment updates

## [0.3.5] - 2025-02-11

### Changed
- Standardized relationship loading across all services
  - Added joinedload() for all relationships in SELECT queries
  - Replaced .refresh() calls with proper SELECT queries
  - Fixed relationship field names (income_entries → income)
  - Fixed field names (bill_id → liability_id)
  - Improved query efficiency by preventing N+1 queries

### Fixed
- Fixed incorrect relationship field names in income service
- Fixed incorrect field name in liabilities service
- Fixed func.count() usage in income service list method

## [0.3.4] - 2025-02-10

### Removed
- Deprecated bills schema
- Unused bills service
- Deprecated bills endpoints
- Obsolete router configuration

### Changed
- Migrated all bill functionality to liabilities
- Updated router configuration for cleaner architecture
- Improved test coverage and organization

## [0.3.3] - 2025-02-09

### Added
- Support for bill splits across multiple accounts
- Split payment validation
- Split payment tracking
- Balance impact tracking per account

### Changed
- Enhanced bill management interface
- Improved payment tracking system
- Updated cashflow calculations

## [0.3.2] - 2025-02-08

### Added
- Dynamic account management
- Credit limit tracking
- Statement balance history
- Account-specific transaction history

### Changed
- Improved balance calculations
- Enhanced cashflow forecasting
- Updated account interface

## [0.3.1] - 2025-02-07

### Added
- Income tracking system
- Deposit status tracking
- Running total of undeposited income
- Target account selection for deposits

### Changed
- Enhanced cashflow calculations
- Improved balance forecasting
- Updated income interface

## [0.3.0] - 2025-02-06

### Added
- Bill management system
- Payment tracking
- Due date monitoring
- Auto-pay status tracking

### Changed
- Complete frontend redesign
- Enhanced user interface
- Improved navigation

## [0.2.0] - 2025-02-05

### Added
- Account management
- Balance tracking
- Basic bill tracking
- Simple cashflow monitoring

### Changed
- Updated database schema
- Improved API structure
- Enhanced error handling

## [0.1.0] - 2025-02-04

### Added
- Initial release
- Basic functionality
- Core database structure
- Simple API endpoints
