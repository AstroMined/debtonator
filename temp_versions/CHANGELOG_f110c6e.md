# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
