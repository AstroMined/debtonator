# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Significantly improved project compliance metrics:
  * ADR-011 Compliance: Increased from 19% to 57% fully compliant
  * ADR-012 Compliance: Increased from 57% to 86% fully compliant
  * DRY Principle: Increased from 62% to 90% rated as "Good"
  * SRP Principle: Increased from 95% to 100% rated as "Good"
- Updated schema_review_findings.md with comprehensive compliance metrics
- Applied consistent validation improvements across all refactored files:
  * Removed custom datetime validation in favor of BaseSchemaValidator
  * Replaced ZoneInfo with timezone.utc for consistent timezone handling
  * Updated to ConfigDict from outdated Config class for V2 compliance
  * Added comprehensive docstrings for all classes and validators
  * Improved field constraints for better validation

## [0.3.91] - 2025-03-15

### Changed
- Refactored first 8 schema files to comply with ADR-011 (Datetime Standardization)
  * Added BaseSchemaValidator inheritance to ensure proper UTC handling
  * Converted date fields to datetime with explicit UTC timezone information
  * Added comprehensive field descriptions with UTC timezone requirements
  * Updated all monetary fields with proper decimal_places validation
  * Fixed union type syntax to use modern Type | None pattern
  * Added cross-field validators for data consistency
- Refactored first 8 schema files to comply with ADR-012 (Validation Layer Standardization)
  * Updated balance_reconciliation.py with standardized validation
  * Updated recurring_bills.py with field validators for amount precision
  * Updated cashflow.py with decimal validation for all monetary fields
  * Updated credit_limits.py with proper field constraints
  * Updated income_categories.py with improved field descriptions
  * Updated deposit_schedules.py with validators for monetary precision
  * Updated payment_schedules.py with Decimal instead of float for monetary fields
  * Updated balance_history.py with cross-field validators for data integrity
- Created comprehensive schema_review_findings.md document with detailed analysis of all schema files
- Established standardized patterns for remaining schema refactoring

## [0.3.90] - 2025-03-14

### Added
- Comprehensive model compliance checklist:
  * Created detailed model_compliance_checklist.md document
  * Systematically reviewed all 18 model files against ADR-011 and ADR-012
  * Added file-specific compliance notes with detailed implementation status
  * Documented required changes for non-compliant models

### Changed
- Completed validation layer standardization model review:
  * Confirmed 17 of 18 models are fully compliant with ADR-011 and ADR-012
  * Identified accounts.py as needing minor updates
  * Ran isort and black against all model files for consistent formatting
  * Enhanced documentation about service layer responsibility

### Fixed
- Identified issues in accounts.py model:
  * Unused imports: `validates` from SQLAlchemy
  * Unused imports: `ZoneInfo`
  * Documentation needs minor updates to align with ADR-011

## [0.3.89] - 2025-03-14

### Fixed
- Completed model test suite refactoring to align with ADR-012 implementation:
  * Fixed model tests that were failing due to business logic removal
  * Removed business logic tests from RecurringIncome, Income, and StatementHistory model tests
  * Updated test_income_record fixture to set undeposited_amount directly
  * Refocused model tests purely on data structure and relationships
  * Modified test_cascade_delete_income_entries to use RecurringIncomeService
  * Fixed StatementHistory tests to focus on due_date as a regular field
  * Corrected relationship tests in Deposit Schedules and Income Categories models
  * Ensured all 106 model tests pass successfully

### Changed
- Enhanced test organization following ADR-012 principles:
  * Created clear delineation between model tests and service tests
  * Improved test fixtures to respect separation of concerns
  * Corrected remaining Pylint warnings
  * Maintained proper test coverage while respecting architecture boundaries
  * Created proper test consistency with UTC datetime handling

## [0.3.88] - 2025-03-13

### Changed
- Enhanced validation layer standardization with multiple model improvements:
  * Removed SQLAlchemy event listeners from CreditLimitHistory model
  * Added validate_credit_limit_history to AccountService for robust validation
  * Removed create_liability() business logic from RecurringBill model
  * Added create_liability_from_recurring() to RecurringBillService
  * Enhanced model documentation with clear data structure focus
  * Fixed datetime handling for proper UTC timezone management
  * Improved test cases to focus on model structure rather than validation
  * Enhanced date/datetime comparison handling in service queries

### Added
- Improved BaseSchemaValidator with automatic datetime handling:
  * Added timezone conversion from naive to UTC-aware datetimes
  * Overrode model_validate method to handle SQLAlchemy model conversion
  * Maintained strict validation for explicit user input
  * Improved error messages for datetime validation failures
  * Fixed test inconsistencies between date and datetime objects
  * Eliminated repetitive timezone conversion code across services

## [0.3.87] - 2025-03-13

### Changed
- Enhanced Categories model and service layer separation:
  * Removed business logic methods (full_path, is_ancestor_of, _get_parent) from Category model
  * Added corresponding methods to CategoryService (get_full_path, is_ancestor_of)
  * Updated model documentation to clarify pure data structure focus
  * Fixed SQLAlchemy query handling for eager-loaded relationships
  * Updated API endpoints to populate full_path using service methods
  * Ensured proper full_path population for nested categories
  * Added comprehensive test coverage for both model and service
  * Achieved 100% passing tests across all related components
  * Completed Categories model simplification in alignment with ADR-012

## [0.3.86] - 2025-02-18

### Changed
- Enhanced Payment Service validation layer:
  * Moved basic validation to Pydantic schemas (amount, dates, source totals)
  * Proper UTC enforcement via BaseSchemaValidator
  * Business logic isolated in service layer (account availability, references)
  * Improved separation of concerns aligning with ADR-011 and ADR-012
  * Added comprehensive test coverage for business logic

## [0.3.85] - 2025-02-18

### Added
- Enhanced Account Service with comprehensive validation:
  * Added validate_account_balance for transaction validation
  * Added validate_credit_limit_update for limit changes
  * Added validate_transaction for transaction processing
  * Added validate_statement_update for statement changes
  * Added validate_account_deletion for safe deletion
- Added comprehensive test coverage for Account Service:
  * Account creation validation
  * Credit limit update validation
  * Statement balance validation
  * Account deletion validation
  * Transaction validation
  * Edge case handling

## [0.3.84] - 2025-02-18

### Changed
- Enhanced Income model and service layer separation:
  * Removed calculate_undeposited method from Income model
  * Added _calculate_undeposited_amount to IncomeService
  * Added _update_undeposited_amount to IncomeService
  * Enhanced model documentation with clear responsibility boundaries
  * Improved relationship documentation
  * Organized fields into logical groups
  * Added explicit schema vs service layer responsibilities
  * Maintained proper UTC datetime handling
  * Verified ADR-012 compliance

## [0.3.83] - 2025-02-18

### Changed
- Consolidated project configuration into pyproject.toml:
  * Moved all dependencies from requirements.txt to pyproject.toml with version constraints
  * Migrated pytest configuration from pytest.ini to [tool.pytest.ini_options]
  * Removed redundant requirements.txt and pytest.ini files
  * Updated documentation to reflect centralized configuration
  * Enhanced development setup documentation for UV usage

## [0.3.82] - 2025-02-18

### Changed
- Enhanced Bill/Liability model documentation and organization:
  * Added comprehensive class-level documentation clarifying responsibility boundaries
  * Improved field documentation with validation and service layer notes
  * Organized fields into logical groups with clear comments
  * Added explicit documentation about schema vs service layer responsibilities
  * Maintained proper UTC datetime handling
  * Verified model complies with ADR-012 standards

## [0.3.81] - 2025-02-18

### Changed
- Improved Account model and service layer separation:
  * Removed update_available_credit method from Account model
  * Added _update_available_credit to AccountService
  * Simplified Account model to pure data structure
  * Enhanced service layer credit calculations
  * Updated tests to focus on data integrity
  * Improved separation of concerns
  * Maintained full test coverage

## [0.3.80] - 2025-02-18

### Changed
- Enhanced Analysis/Forecast schema validation:
  * Updated payment_patterns schema with V2-style validators and comprehensive validation
  * Enhanced income_trends schema with proper enum types and cross-field validation
  * Improved realtime_cashflow schema with account type safety and decimal precision
  * Added proper timezone handling across all analysis schemas
  * Added comprehensive JSON schema examples
  * Added validation for business rules and calculations

## [0.3.79] - 2025-02-17

### Added
- Enhanced income schema validation:
  * Added comprehensive field validation with proper constraints
  * Implemented V2-style validators for all income schemas
  * Added proper UTC datetime handling
  * Added amount precision validation
  * Added deposit status validation
  * Added complete test coverage with all tests passing

## [0.3.78] - 2025-02-17

### Changed
- Enhanced bill/liability schema validation:
  * Added comprehensive field validation with proper constraints
  * Implemented V2-style validators for all liability schemas
  * Added proper UTC datetime handling
  * Added amount precision validation
  * Added auto-pay settings validation
  * Added complete test coverage with all tests passing

## [0.3.77] - 2025-02-17

### Added
- Enhanced payment schema validation:
  * Added comprehensive field validation with proper constraints
  * Implemented V2-style validators for all payment schemas
  * Added proper UTC datetime handling
  * Added amount precision validation
  * Added payment source validation with duplicate checks
  * Added complete test coverage with all tests passing

## [0.3.76] - 2025-02-17

### Changed
- Enhanced accounts schema validation:
  * Added comprehensive field validation with proper constraints
  * Implemented credit account specific business rules
  * Added proper datetime handling with UTC enforcement
  * Updated to Pydantic V2 compliant validation patterns
  * Added complete test coverage with all tests passing

## [0.3.75] - 2025-02-17

### Added
- ADR-012: Validation Layer Standardization
  * Defined clear validation boundaries
  * Established schema-based validation patterns
  * Documented service layer business logic
  * Created comprehensive migration strategy

### Changed
- Improved model test coverage to 100%
  * Fixed accounts model after_update event listener test
  * Added test for invalid parent_id in categories
  * Added test for Liability string representation

## [0.3.74] - 2025-02-17

### Changed
- Improved model test coverage:
  * Added test for after_insert event in accounts model
  * Added test for full_path property with no parent in categories model
  * Removed unused imports to improve code quality
  * Overall model test coverage increased to 99%

## [0.3.73] - 2025-02-17

### Fixed
- Fixed statement history due date calculation to be based on statement_date instead of current time
- Fixed transaction history string representation test to match model implementation
- Improved test coverage and accuracy:
  * Updated statement_history_due_date_handling test to verify business rules
  * Updated transaction_history_string_representation test to match model output

## [0.3.72] - 2025-02-17

### Changed
- Centralized model test fixtures in tests/models/conftest.py:
  * Moved duplicate fixtures from individual test files
  * Standardized fixture scope and naming
  * Improved relationship handling in fixtures
  * Enhanced database state management
  * Fixed hardcoded ID references

## [0.3.71] - 2025-02-16

### Added
- Created missing model test files:
  * test_balance_history_models.py with timestamp field testing
  * test_bill_splits_models.py with base model datetime testing
  * test_deposit_schedules_models.py with schedule_date testing
  * test_income_categories_models.py with base model datetime testing
  * test_payment_schedules_models.py with scheduled_date testing

### Changed
- Updated test_accounts_models.py to use naive_utc_now() and naive_utc_from_date()
- Added test_datetime_handling function to test_categories_models.py
- Enhanced test_transaction_history_models.py with datetime component verification
- Standardized datetime testing patterns across all test files
- Improved relationship loading tests with proper refresh patterns

## [0.3.70] - 2025-02-16

### Added
- Added naive_utc_from_date utility function to base_model.py for standardized date creation
- Added comprehensive datetime handling tests to all model test files
- Added explicit UTC validation tests across all models

### Changed
- Updated all model tests to use naive_utc_now() and naive_utc_from_date()
- Improved test coverage for datetime handling
- Enhanced test assertions for naive datetime validation
- Standardized fixture scoping with scope="function"

### Removed
- Removed all direct datetime.now(ZoneInfo("UTC")) usage
- Eliminated redundant timezone handling in tests

## [0.3.69] - 2025-02-16

### Changed
- Standardized datetime handling across all models:
  * Updated StatementHistory to use naive_utc_now
  * Updated BalanceHistory to use naive_utc_now
  * Updated CreditLimitHistory to use naive_utc_now
  * Updated PaymentSchedule datetime columns
  * Updated DepositSchedule datetime columns
  * Updated BalanceReconciliation to use naive_utc_now
  * Updated RecurringIncome to handle UTC dates properly
- Removed all direct timezone manipulation from models
- Improved datetime field documentation
- All models now consistently use naive UTC datetimes

## [0.3.68] - 2025-02-16

### Fixed
- Improved SQLAlchemy async relationship loading in history model tests:
  * Fixed greenlet_spawn errors by using specific relationship loading
  * Updated test_balance_reconciliation_models.py
  * Updated test_credit_limit_history_models.py
  * Updated test_statement_history_models.py
  * Updated test_transaction_history_models.py
- Removed timezone PRAGMA from database.py to align with ADR-011 principles
- Added SQLAlchemy async relationship loading best practices to .clinerules

## [0.3.67] - 2025-02-16

### Added
- Comprehensive model test coverage:
  * Added test_recurring_income_models.py with create_income_entry tests
  * Added test_balance_reconciliation_models.py with edge case tests
  * Added test_credit_limit_history_models.py with validation tests
  * Added test_statement_history_models.py with date handling tests
  * Added test_transaction_history_models.py with transaction type tests
  * All new tests using datetime.utcnow() for consistency
  * Improved overall model test coverage to 97%

## [0.3.66] - 2025-02-16

### Fixed
- Removed model-level timezone handling to align with ADR-011:
  * Removed __init__ timezone handling from Liability model
  * Fixed test assertions to expect naive datetimes
  * Fixed failing tests in liabilities and recurring bills
  * Identified remaining models with timezone handling for future cleanup

### Added
- Comprehensive model audit for datetime standardization:
  * Identified 8 models still using timezone=True
  * Found 2 models with direct timezone manipulation
  * Documented 4 models already conforming to ADR-011
  * Created detailed cleanup plan in active_context.md

## [0.3.65] - 2025-02-16

### Changed
- Completed Model Simplification phase of datetime standardization:
  * Removed timezone=True from all DateTime columns
  * Updated datetime field documentation with UTC requirements
  * Reinitialized database with new schema
  * Completed Phase 2 of datetime standardization project
  * All models now use simple DateTime() columns
  * UTC enforcement moved entirely to Pydantic schemas
  * Improved documentation clarity around UTC storage

## [0.3.64] - 2025-02-16

### Changed
- Updated Analysis/Forecast schemas to use BaseSchemaValidator
  * Added UTC timezone validation to realtime_cashflow schemas
  * Added UTC timezone validation to impact_analysis schemas
  * Converted date fields to timezone-aware datetime in recommendations schemas
  * Added comprehensive test coverage for schema validation
  * Updated period calculations to use UTC datetime
  * Added validation for date ranges and forecast periods
  * All analysis schema tests passing

## [0.3.63] - 2025-02-16

### Changed
- Updated Account/Transaction schemas to use BaseSchemaValidator
  * Converted all date fields to timezone-aware datetime
  * Added UTC validation for statement dates and timestamps
  * Updated field descriptions to indicate UTC requirement
  * Added comprehensive test coverage for UTC validation
  * Fixed AccountUpdate schema to use datetime instead of date
  * All account and transaction schema tests passing

## [0.3.62] - 2025-02-16

### Changed
- Updated Income schemas to use BaseSchemaValidator
  * Converted all date fields to timezone-aware datetime
  * Updated model configurations to Pydantic V2 style
  * Added comprehensive test coverage for UTC validation
  * Added recurring income validation tests
  * All income schema tests passing

## [0.3.61] - 2025-02-16

### Changed
- Updated Bill/Liability schemas to use BaseSchemaValidator
  * Removed custom UTC validators in favor of BaseSchemaValidator
  * Simplified ConfigDict usage to match payment schemas
  * Updated datetime field descriptions for UTC requirement
  * Added comprehensive schema test coverage

## [0.3.60] - 2025-02-16

### Added
- Implemented BaseSchemaValidator with Pydantic V2 style validators
  * UTC timezone enforcement for all datetime fields
  * Clear validation error messages
  * Proper JSON encoding for UTC datetimes
  * Comprehensive test coverage

### Changed
- Updated Payment schemas to use BaseSchemaValidator
  * Converted date fields to timezone-aware datetime
  * Updated model configurations to Pydantic V2 style
  * Improved field descriptions for UTC requirement
  * All payment service tests passing

### Fixed
- Switched to Pydantic V2 style field_validator from deprecated validator
- Reinitialized database with proper datetime columns

## [0.3.59] - 2025-02-15

### Changed
- Updated datetime standardization approach:
  * Removed SQLAlchemy timezone parameters
  * Moved timezone enforcement to Pydantic schemas
  * Simplified model definitions
  * Enhanced validation error messages
  * Updated ADR-011 with new implementation strategy
  * Documented schema-based validation approach

### Deprecated
- SQLAlchemy timezone=True parameter usage
- Multiple layers of timezone enforcement

## [0.3.58] - 2025-02-15

### Fixed
- Improved SQLite timezone handling:
  * Added proper UTC timezone support in SQLite configuration
  * Fixed timezone-aware datetime handling in database engine
  * Updated SQLite connection settings for consistent UTC handling
  * Fixed failing tests in liabilities and recurring bills

## [0.3.57] - 2025-02-15

### Changed
- Completed Phase 1 of datetime standardization:
  * Created BaseDBModel with UTC timezone-aware created_at/updated_at fields
  * Updated all models to inherit from BaseDBModel
  * Converted all date fields to timezone-aware datetime fields
  * Reinitialized database with new schema
  * Standardized datetime handling across all models:
    - Account
    - BillSplit
    - CashflowForecast
    - CreditLimitHistory
    - DepositSchedule
    - Income
    - Liability
    - Payment
    - PaymentSchedule
    - PaymentSource
    - RecurringBill
    - RecurringIncome
    - StatementHistory
    - TransactionHistory
    - BalanceHistory
    - BalanceReconciliation

## [0.3.56] - 2025-02-15

### Changed
- Continued migration to timezone-aware datetime fields:
  * Updated impact analysis schema to use timezone-aware datetime
  * Updated income trends schema to use timezone-aware datetime
  * Updated cashflow schema to use timezone-aware datetime
  * Fixed datetime handling in account forecast tests
  * Added explicit UTC timezone handling

## [0.3.55] - 2025-02-15

### Changed
- Started migration to timezone-aware datetime fields in schemas:
  * Updated Payment model to use timezone-aware datetime fields
  * Fixed datetime handling in payment model tests
  * Identified need to update historical analysis schemas

## [0.3.54] - 2025-02-15

### Fixed
- Payment pattern test improvements:
  * Fixed test assertion in seasonal pattern test to match actual fixture behavior
  * Updated test documentation to accurately reflect 6-month payment pattern
  * All payment pattern tests now passing

## [0.3.53] - 2025-02-15

### Fixed
- Payment pattern analysis improvements:
  * Fixed irregular pattern detection with more accurate timing variation threshold
  * Improved gap detection sensitivity for better pattern classification
  * Enhanced pattern detection notes for better clarity
  * Fixed test assertions to match actual fixture behavior

## [0.3.52] - 2025-02-15

### Fixed
- Payment pattern analysis improvements:
  * Fixed datetime handling with proper UTC timezone support
  * Improved pattern detection with better interval calculations
  * Enhanced confidence scoring for borderline cases
  * Added case-insensitive category matching
  * Fixed test fixtures with timezone-aware dates

## [0.3.51] - 2025-02-15

### Added
- Added warning notes for payments made too close to due dates
- Enhanced pattern detection relative to bill due dates with improved confidence scoring

## [0.3.50] - 2025-02-15

### Changed
- Refactored payment pattern service to focus on bill-specific patterns:
  * Renamed PaymentPatternService to BillPaymentPatternService
  * Updated service to focus on bill payment patterns
  * Improved pattern detection relative to bill due dates
  * Added TODO comments for future ExpensePatternService
  * Updated test fixtures to use proper bill-payment relationships
  * Removed non-bill pattern detection tests
  * Maintained full test coverage

## [0.3.49] - 2025-02-15

### Fixed
- Payment pattern detection improvements:
  * Fixed days before due date calculation
  * Improved pattern confidence scoring
  * Enhanced standard deviation calculations
  * Added proper target days handling
  * Fixed test fixtures for consistent patterns
  * Improved test coverage for pattern detection

## [0.3.48] - 2025-02-15

### Added
- Split analysis system
  - Optimization metrics calculation:
    * Credit utilization tracking per account
    * Balance impact analysis
    * Risk scoring system
    * Optimization scoring
  - Impact analysis features:
    * Short-term (30-day) projections
    * Long-term (90-day) projections
    * Risk factor identification
    * Smart recommendations
  - Optimization suggestions:
    * Credit utilization balancing
    * Mixed account type strategies
    * Priority-based suggestions
  - Comprehensive test coverage including:
    * Metrics calculation scenarios
    * Impact analysis verification
    * Suggestion generation testing
    * All tests passing

### Fixed
- Decimal precision handling in financial calculations
- Type safety improvements in optimization metrics
