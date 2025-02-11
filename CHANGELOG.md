# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-02-10

### Changed
- Improved test infrastructure with better async SQLite handling
- Enhanced transaction management in test fixtures
- Reorganized model relationship tests for better clarity

### Removed
- Obsolete migration test files (test_migration_script.py)
- Legacy migration-related test code

### Fixed
- SQLite async connection handling in tests
- Transaction management in test fixtures
- Test database cleanup and initialization

## [0.2.0] - 2025-02-09

### Added
- New Liability model replacing Bills
- Payment model for transaction tracking
- PaymentSource model for split payments
- Comprehensive model relationship tests
- Migration scripts for database changes

### Changed
- Updated Account model relationships
- Enhanced database schema for better payment tracking
- Improved test infrastructure

### Removed
- Legacy Bill model
- Deprecated database schema

## [0.1.0] - 2025-02-08

### Added
- Initial project setup
- Basic database schema
- Core models implementation
- Test infrastructure
- Frontend foundation
