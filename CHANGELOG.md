# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.9] - 2025-03-16

### Added
- Comprehensive integration tests for API response formatter
- Decimal precision handling in core services (accounts, liabilities, recurring_bills, income)

### Changed
- Enhanced account balance calculations with proper decimal precision
- Improved income deposit calculations with 4-decimal internal precision
- Updated recurring bills service to apply proper rounding for monetary values
- Enhanced liabilities service with consistent decimal handling

## [0.4.8] - 2025-03-16

### Added
- Implemented comprehensive API response formatting for decimal precision:
  * Added src/api/response_formatter.py with utilities for consistent decimal handling
  * Implemented global middleware for all JSON responses
  * Added @with_formatted_response decorator for individual endpoints
  * Created get_decimal_formatter() dependency for manual formatting
- Created comprehensive developer guidelines for working with money:
  * Detailed best practices for decimal precision handling
  * Documented when to use 4 vs 2 decimal places
  * Added examples of common financial calculation patterns
  * Provided guidance on testing monetary calculations

### Changed
- Improved decimal precision handling at API boundaries:
  * Ensured monetary values return with 2 decimal places
  * Preserved 4 decimal places for percentage fields
  * Enhanced accuracy of financial data in API responses
  * Implemented recursive formatting for nested data structures

## [0.4.7] - 2025-03-16

### Changed
- Completed cashflow schema files decimal precision standardization:
  * Updated all remaining cashflow schema files with standardized field methods
  * Applied BaseSchemaValidator.money_field() to all monetary values
  * Applied BaseSchemaValidator.percentage_field() to all percentage values
  * Enhanced separation between monetary and percentage fields
  * Standardized schema validation across all files
  * Maintained existing field constraints and documentation
  * Improved code readability and maintainability

### Fixed
- Improved percentage field validation in cashflow schemas:
  * Standardized confidence scores with proper validation
  * Updated trend strength fields with percentage_field()
  * Fixed decimal precision validation consistency
  * Used appropriate field methods for different validation needs

## [0.4.6] - 2025-03-16

### Changed
- Expanded standardized decimal precision across schema files:
  * Updated 10 additional schema files with standardized field methods
  * Replaced custom decimal validation with BaseSchemaValidator methods
  * Used money_field() for monetary values (2 decimal places)
  * Used percentage_field() for percentage values (4 decimal places)
  * Maintained all field constraints (gt, ge, etc.) and documentation
  * Implemented in balance_history.py, balance_reconciliation.py, deposit_schedules.py, impact_analysis.py, income_trends.py, payment_patterns.py, payment_schedules.py, recurring_bills.py, recommendations.py, and transactions.py

### Fixed
- Improved handling of percentage fields across schemas:
  * Properly used percentage_field() with 4 decimal places for:
    - Credit utilization fields
    - Historical pattern strength metrics
    - Confidence scores
    - Risk assessment fields
  * Maintained appropriate range constraints (0-1 or 0-100)
  * Preserved backward compatibility with existing validation

## [0.4.5] - 2025-03-16

### Added
- Implemented decimal precision handling in critical services:
  * Updated `src/services/bill_splits.py` with proper decimal precision for bill splits
  * Enhanced `src/services/payments.py` with 4-decimal precision for payment calculations
  * Improved `src/services/balance_history.py` for accurate running balances
  * Updated `src/services/cashflow.py` metrics_service with proper precision handling
  * Enhanced `src/services/impact_analysis.py` for percentage and risk calculations

### Changed
- Implemented multi-tier precision model following ADR-013:
  * Using 4 decimal places for all internal calculations
  * Rounding to 2 decimal places at API boundaries
  * Proper decimal handling for financial calculations
  * Improved accuracy in percentage and distribution calculations

## [0.4.4] - 2025-03-16

### Added
- Created ADR-013 implementation checklist:
  * Comprehensive documentation of all required changes for decimal precision handling
  * Detailed list of 37 database fields that need precision updates
  * Service layer enhancement requirements for calculation accuracy
  * Test updates required for validation and verification
  * Placed in new `docs/adr/compliance/` directory for visibility

### Changed
- Selected `src/core` module approach for decimal precision implementation:
  * Elevates decimal precision as core business domain concern
  * Provides clear architectural separation from utilities
  * Creates foundation for other core business modules

## [0.4.3] - 2025-03-15

### Changed
- Completed schema test implementation with 100% coverage:
  * Fixed all 11 failing tests across 6 schema test files
  * Updated schema_test_implementation_checklist.md to reflect 100% completion

### Fixed
- Schema test timezone and error message fixes:
  * Corrected timezone creation in balance_history_schemas.py using proper `timezone(timedelta(hours=5))` pattern
  * Updated error message patterns in accounts_schemas.py to match Pydantic's actual messages
  * Fixed decimal precision test in recommendations_schemas.py to match singular form "decimal place"
  * Updated transaction_schemas.py to use consistent "Datetime must be UTC" error messages
  * Fixed date validation in liabilities_schemas.py with dynamic future dates
  * Updated payment validation tests to reflect that future dates are now allowed
  * Fixed string/list validation tests in recommendations_schemas.py

## [0.4.2] - 2025-03-15

### Added
- Created ADR-013 for decimal precision handling in financial calculations:
  * Defined multi-tier precision model with 2 decimals for I/O and 4 for calculations
  * Outlined implementation components and migration strategy
  * Detailed rounding strategies for bill splits and financial allocations
  * Documented compliance with financial industry standards

### Fixed
- Updated Pydantic V2 validators across schema files:
  * Fixed `income_trends.py` validators to properly use ValidationInfo object
  * Fixed `realtime_cashflow.py` validators to use ValidationInfo object
  * Corrected dictionary-style access to use ValidationInfo.data
- Enhanced BaseSchemaValidator with proper decimal validation:
  * Updated validate_decimal_precision method to enforce 2-decimal constraint
  * Added clear error messages for precision validation failures
  * Added detailed documentation and TODO comments for future improvements
- Fixed test case in test_realtime_cashflow_schemas.py:
  * Updated test_net_position_validation to use 2-decimal precision
  * Aligned test expectations with validation behavior

## [0.4.1] - 2025-03-15

### Added
- Complete test coverage for cashflow module schemas following ADR-011 and ADR-012 standards:
  * Implemented test_cashflow_base_schemas.py for core cashflow schemas
  * Implemented test_cashflow_metrics_schemas.py for financial metrics schemas
  * Implemented test_cashflow_account_analysis_schemas.py for account analysis schemas
  * Implemented test_cashflow_forecasting_schemas.py for forecasting schemas
  * Implemented test_cashflow_historical_schemas.py for historical analysis schemas
- Each test file includes complete validation coverage:
  * Tests for valid object creation with required and optional fields
  * Tests for field validations and constraints
  * Tests for decimal precision validation for monetary fields
  * Tests for UTC datetime validation per ADR-011
  * Tests for business rules and cross-field validations

### Fixed
- Timezone compliance issues in existing test files:
  * Updated test_accounts_schemas.py to use timezone.utc instead of ZoneInfo("UTC")
  * Fixed import statements to include datetime.timezone
  * Ensured consistent timezone handling across tests

## [0.4.0] - 2025-03-15

### Changed
- Decomposed src/schemas/cashflow.py (974 lines) into modular components:
  * Created src/schemas/cashflow/base.py for core cashflow schemas
  * Created src/schemas/cashflow/metrics.py for financial metrics schemas
  * Created src/schemas/cashflow/account_analysis.py for account analysis schemas
  * Created src/schemas/cashflow/forecasting.py for forecasting schemas
  * Created src/schemas/cashflow/historical.py for historical analysis schemas
  * Created src/schemas/cashflow/__init__.py with re-exports for backward compatibility
- Updated schema_test_implementation_checklist.md with new modular structure:
  * Replaced single test file with five specialized test files
  * Updated test plan to align with new modular organization
  * Maintained comprehensive validation test coverage requirements
  * Improved test organization and clarity

### Added
- Updated test implementation plan with modular schema structure:
  * Added test_cashflow_base_schemas.py for core schemas
  * Added test_cashflow_metrics_schemas.py for metrics schemas
  * Added test_cashflow_account_analysis_schemas.py for analysis schemas
  * Added test_cashflow_forecasting_schemas.py for forecasting schemas
  * Added test_cashflow_historical_schemas.py for historical schemas

## [0.3.96] - 2025-03-15

### Added
- Created src/version.py for programmatic version information access:
  * Defined VERSION_MAJOR, VERSION_MINOR, and VERSION_PATCH constants
  * Added VERSION formatted string and VERSION_TUPLE for structured access
  * Added comprehensive docstrings and proper module exports
  * Synchronized with existing version in pyproject.toml
- Implemented three key schema test files:
  * test_realtime_cashflow_schemas.py with comprehensive test coverage for AccountType, AccountBalance, RealtimeCashflow, and RealtimeCashflowResponse
  * test_recommendations_schemas.py with thorough validation for RecommendationType, ConfidenceLevel, ImpactMetrics, RecommendationBase, BillPaymentTimingRecommendation, and RecommendationResponse
  * test_income_categories_schemas.py with complete CRUD schema tests for IncomeCategoryBase, IncomeCategoryCreate, IncomeCategoryUpdate, and IncomeCategory
- Updated schema_test_implementation_checklist.md to track progress:
  * Marked 15 of 21 schema test files as completed (71% complete)
  * Added notes for N/A test categories where appropriate

### Changed
- Improved schema test infrastructure and documentation:
  * Enhanced UTC datetime validation test patterns
  * Improved test documentation for validation requirements
  * Standardized test patterns across new test files
  * Applied consistent testing approaches for schema validation

## [0.3.95] - 2025-03-15

### Added
- Completed implementation of Phase 2 schema test files:
  * test_balance_history_schemas.py with full validation coverage
  * test_payment_schedules_schemas.py with comprehensive test cases
  * test_deposit_schedules_schemas.py with detailed field validation
  * test_recurring_bills_schemas.py with proper recurrence pattern testing 
  * All Phase 2 test files passing with 42 successful test cases

### Fixed
- Discovered and fixed non-UTC timezone creation issue:
  * Identified incorrect pattern: `timezone(hours=5)` causing TypeError
  * Implemented correct pattern: `timezone(timedelta(hours=5))`
  * Added timedelta import to affected files
  * Updated timezone validation assertion pattern to avoid Pylint errors
  * Documented the correct pattern in schema_test_implementation_checklist.md

## [0.3.94] - 2025-03-15

### Added
- Created schema test implementation plan with a comprehensive checklist:
  * Designed standard test file structure and patterns
  * Defined clear test categories for comprehensive coverage
  * Organized files into logical implementation phases
  * Created detailed test template with best practices

### Changed
- Implemented initial schema test files:
  * test_balance_reconciliation_schemas.py with comprehensive validation tests
  * test_bill_splits_schemas.py with field constraint validation
  * test_categories_schemas.py with hierarchical relationship testing

### Fixed 
- Identified and documented critical timezone compliance issue:
  * Tests were using `ZoneInfo("UTC")` instead of `timezone.utc` as mandated by ADR-011
  * Created detailed plan for proper datetime handling in test files
  * Added comprehensive documentation in schema_test_implementation_checklist.md
  * Updated test template with proper timezone.utc usage

## [0.3.93] - 2025-03-15

### Changed
- Completed schema refactoring with final 3 files to achieve 100% compliance with ADR-011 and ADR-012:
  * liabilities.py: Replaced field_validator with model_validator, added explicit UTC timezone mentions
  * accounts.py: Added common field definition functions, extracted shared validator logic
  * payments.py: Created reusable validation functions for decimal precision and payment sources
- Achieved 100% compliance across all schema files:
  * ADR-011 Compliance: Increased from 57% to 100% fully compliant
  * ADR-012 Compliance: Increased from 86% to 100% fully compliant
  * DRY Principle: Increased from 90% to 100% rated as "Good"
  * SRP Principle: Maintained at 100% rated as "Good"
- Updated schema_review_findings.md with final compliance metrics
- Applied consistent validation improvements across all schema files
- Removed "Remaining Issues to Address" section as all issues were resolved
- Updated "Next Steps" section to focus on maintaining standards rather than fixing issues

## [0.3.92] - 2025-03-15

### Changed
- Refactored 8 additional schema files to comply with ADR-011 and ADR-012:
  * transactions.py: Added BaseSchemaValidator inheritance, created local enum
  * categories.py: Improved circular import handling, extracted duplicate validation
  * bill_splits.py: Changed date type to datetime with UTC, fixed error patterns
  * income.py: Removed redundant datetime validation, enhanced field descriptions
  * recommendations.py: Updated to ConfigDict, added detailed field descriptions
  * impact_analysis.py: Replaced ZoneInfo with timezone.utc, improved constraints
  * payment_patterns.py: Removed duplicate validators, enhanced field descriptions
  * income_trends.py: Enhanced documentation, updated ConfigDict usage
  * realtime_cashflow.py: Added detailed validator docstrings, improved constraints
