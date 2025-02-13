# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.25] - 2025-02-13

### Fixed
- Fixed auto-pay settings serialization
  - Fixed Decimal serialization in auto-pay settings JSON storage
  - Updated test assertions to handle string representation of Decimal values
  - Improved auto-pay candidates test with proper date range
  - Enhanced test coverage for auto-pay functionality

## [0.3.24] - 2025-02-13

### Fixed
- Fixed category relationship handling in liability tests
  - Updated test cases to properly create Category instances
  - Fixed '_sa_instance_state' errors in liability tests
  - Improved test assertions for category relationships
  - Standardized category handling across all liability tests

[Previous entries remain unchanged...]
