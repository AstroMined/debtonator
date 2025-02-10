# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-10

### Changed
- Major architectural change: Separated bills and payments
- Implemented new Liability model to replace Bill model
- Added dedicated Payment and PaymentSource models
- Updated database schema for better payment tracking
- Improved relationship modeling between accounts and payments

### Removed
- Legacy Bill model and associated direct relationships

## [0.4.4] - 2025-02-09

### Fixed
- Test infrastructure improvements
  - Fixed incorrect HTTP status code expectations in tests
  - Standardized HTTP status codes (201 for POST success)
  - Improved test assertions for API responses

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

[Previous entries remain unchanged...]
