# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.29] - 2025-02-13

### Added
- Payment scheduling system
  - New payment_schedules table for managing scheduled payments
  - Support for automatic and manual payment processing
  - API endpoints for managing payment schedules
  - Integration with existing payment system
  - Comprehensive test coverage for service and API layers
  - Date range and liability-based schedule filtering
  - Auto-processing capability for due payments

### Changed
- Enhanced payment system with scheduling support
- Improved test infrastructure with proper async handling
- Updated API documentation with new endpoints

## [0.3.28] - 2025-02-13

### Fixed
- Fixed SQLAlchemy cartesian product warning in income service
  - Separated count query from data query in list method
  - Improved query performance by removing unnecessary joins
  - Enhanced test reliability
  - Maintained full test coverage

[Previous entries...]
