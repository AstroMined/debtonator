# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.7] - 2025-03-20

### Added
- Implemented three missing repositories for completing ADR-014:
  * CreditLimitHistoryRepository with comprehensive methods for limit tracking
  * BalanceReconciliationRepository for balance adjustment management
  * TransactionHistoryRepository for transaction analysis and patterns
- Enhanced BaseRepository with additional features:
  * Added bulk_update() method for efficient multi-record updates
  * Implemented transaction() async context manager for transaction handling
  * Added comprehensive error handling and proper context management
- Added schema factory functions for test data generation:
  * create_credit_limit_history_schema() for testing limit history
  * create_balance_reconciliation_schema() for reconciliation testing
  * create_transaction_history_schema() for transaction data

### Changed
- Enhanced repository implementation to complete ADR-014:
  * Updated dependency providers to support all repositories
  * Expanded test coverage with standardized pattern
  * Finalized API dependency injection setup
  * Updated implementation checklist to track 100% completion
- Improved repository test pattern implementation:
  * Applied Arrange-Schema-Act-Assert pattern consistently
  * Added validation error tests to all repository tests
  * Enhanced test fixtures with consistent pattern
  * All tests properly use model_dump() to convert schemas to dicts

## [0.5.6] - 2025-03-20

### Added
- Created repository test pattern guide in docs/guides/repository_test_pattern.md
- Added schema factory functions in tests/helpers/schema_factories.py to simplify test creation
- Enhanced ADR-014 with detailed validation strategy examples
- Created reference implementation in test_bill_split_repository.py showing proper validation flow

### Changed
- Updated ADR-014 to clarify validation responsibilities across layers
- Enhanced ADR-014 implementation checklist with specific testing strategy steps
- Improved Repository Test Template Pattern documentation
- Refactored test_bill_split_repository.py to follow proper validation flow

## [0.5.5] - 2025-03-19

### Added
- Implemented four core repository classes for ADR-014:
  * RecurringBillRepository with 16+ specialized methods for bill pattern management
  * StatementHistoryRepository with 12+ specialized methods for statement tracking
  * BalanceHistoryRepository with 14+ specialized methods for balance history analysis
  * CategoryRepository with 17+ specialized methods for hierarchical category management
- Created comprehensive integration tests for all new repositories:
  * test_recurring_bill_repository.py with 8+ detailed test cases
  * test_statement_history_repository.py with 12+ detailed test cases
  * test_balance_history_repository.py with 12+ detailed test cases
  * test_category_repository.py with 15+ detailed test cases

### Changed
- Enhanced dependency injection system with new repositories:
  * Added get_recurring_bill_repository dependency provider
  * Added get_statement_history_repository dependency provider
  * Added get_balance_history_repository dependency provider
  * Added get_category_repository dependency provider
- Updated repository layer implementation for ADR-014:
  * Improved repository pattern with consistent method naming conventions
  * Enhanced domain-specific analysis capabilities across all repositories
  * Updated ADR-014 implementation checklist to reflect progress (85% complete)

## [0.5.4] - 2025-03-19

### Added
- Implemented Income Repository for repository pattern (ADR-014):
  * Created comprehensive IncomeRepository with complete CRUD operations
  * Added 12+ specialized query methods for income operations
  * Implemented financial analysis methods for income data
  * Added statistical analysis methods for income by period
  * Created get_income_repository() dependency provider

### Changed
- Enhanced repository layer implementation for ADR-014:
  * Updated dependency injection system with IncomeRepository
  * Improved repository pattern documentation
  * Added income financial analysis capabilities to repository layer
  * Updated ADR-014 implementation checklist to reflect progress (75% complete)

## [0.5.3] - 2025-03-19

### Added
- Implemented BillSplitRepository for repository pattern (ADR-014):
  * Created comprehensive BillSplitRepository with complete CRUD operations
  * Added 10+ specialized query methods for bill split operations
  * Implemented bulk_create_splits() method with transaction support
  * Added financial analysis methods (calculate_split_totals, get_split_distribution)
  * Created get_bill_split_repository() dependency provider

### Changed
- Enhanced repository layer implementation for ADR-014:
  * Updated dependency injection system with BillSplitRepository
  * Improved integration test framework with comprehensive bill split repository tests
  * Added bill split financial analysis capabilities to repository layer
  * Updated ADR-014 implementation checklist to reflect progress (70% complete)

## [0.5.2] - 2025-03-19

### Added
- Implemented Payment and PaymentSource repositories (ADR-014):
  * Created PaymentRepository with complete CRUD operations and specialized query methods
  * Created PaymentSourceRepository for payment allocation tracking
  * Added 10+ specialized methods for payment operations
  * Created test structure for both repositories
  * Added dependency providers for repository injection

### Changed
- Enhanced repository pattern implementation for financial records:
  * Added payment retrieval methods by bill, account, and date range
  * Implemented account-based payment source queries
  * Added calculation utilities for financial analysis
  * Improved relationship loading with specialized methods
  * Updated ADR-014 implementation checklist to reflect progress

## [0.5.1] - 2025-03-19

### Added
- Implemented LiabilityRepository with comprehensive CRUD operations and specialized methods
- Added 15+ specialized query methods for bill-related functionality
- Created integration test skeleton for repository testing
- Added dependency provider for LiabilityRepository

### Changed
- Updated ADR-014 implementation checklist to track progress
- Changed ADR-014 status from "Proposed" to "Accepted - In Implementation"
- Updated progress tracking in documentation files

### Improved
- Enhanced repository pattern implementation with relationship loading capabilities
- Added support for complex bill querying and filtering
- Improved bill payment status management

## [0.5.0] - 2025-03-19

### Added
- Implemented repository layer foundation (ADR-014):
  * Created BaseRepository with generic CRUD operations
  * Implemented RepositoryFactory for dependency injection
  * Added comprehensive type safety with generics
  * Created detailed implementation checklist
- Implemented advanced repository features:
  * Added pagination with get_paginated() method
  * Added relationship loading with joinedload
  * Implemented bulk_create() for transaction support
  * Added filtering and ordering capabilities
- Implemented first model-specific repository:
  * Created AccountRepository with specialized methods
  * Added methods for account-specific operations
  * Implemented relationship loading patterns
  * Added balance update and statement management functions

### Changed
- Enhanced service layer architecture with repository pattern:
  * Improved separation between data access and business logic
  * Standardized data access patterns
  * Reduced code duplication in data operations
  * Increased code maintainability

## [0.4.27] - 2025-03-19

### Added
- Created ADR-014 for Repository Layer implementation:
  * Designed a comprehensive architecture to separate CRUD operations from business logic
  * Defined BaseRepository with generic CRUD operations
  * Outlined model-specific repository pattern with type safety
  * Developed dependency injection approach for repositories
  * Included advanced repository features (pagination, filtering, joins)

### Changed
- Updated architectural documentation with repository pattern approach:
  * Updated active_context.md with current focus on Repository Layer
  * Updated progress.md with implementation planning and status tracking
  * Added Service Layer Architecture section to progress tracking

## [0.4.26] - 2025-03-19

### Changed
- Updated model `__repr__` methods to format monetary values with 2 decimal places:
  * Fixed BillSplit.__repr__ to use f-string formatting with .2f
  * Fixed Income.__repr__ to use f-string formatting with .2f
  * Fixed RecurringBill.__repr__ to use f-string formatting with .2f

### Fixed
- Fixed test failures related to decimal precision representation:
  * Fixed test_bill_split_crud in tests/unit/models/test_bill_splits_models.py
  * Fixed test_income_str_representation in tests/unit/models/test_income_models.py
  * Fixed test_recurring_bill_str_representation in tests/unit/models/test_recurring_bills_models.py
- Completed ADR-013 implementation with all steps at 100%:
  * Updated implementation checklist to mark Quality Assurance phase as complete
  * Updated progress tracking to 100% (from 98%)
  * Updated "What's Left to Build" section in progress.md to reflect completion

## [0.4.25] - 2025-03-19

### Changed
- Improved bill splits testing approach using integration-only tests:
  * Removed mock-based unit tests in favor of real database testing
  * Enhanced integration test file with comprehensive decimal precision tests
  * Followed architectural principle that services interact with multiple layers and should be tested without mocks

### Added
- Enhanced integration tests for bill splits in tests/integration/services/test_bill_splits_services.py:
  * Added test cases for the "$100 split three ways" scenario
  * Added tests for common bill split scenarios with challenging divisions
  * Added test for precision of calculated amounts in distribution suggestions
  * Added test for equal distribution with largest remainder method

### Fixed
- Updated ADR-013 implementation progress:
  * Updated implementation checklist to reflect integration-based testing approach
  * Improved overall implementation progress to 98% (from 93%)
  * Clarified service test methodology in test documentation

## [0.4.24] - 2025-03-19

### Added
- Enhanced ADR-013 documentation with comprehensive Pydantic V2 compatibility section:
  * Added detailed section on Pydantic V2 compatibility and breaking changes
  * Created comprehensive documentation on dictionary validation strategy
  * Included usage examples for all Annotated types with code samples
  * Expanded benefits section with 10 clear advantages of the new approach
  * Updated Examples section with three schema usage scenarios
  * Added new revision entry (3.1) to track documentation enhancements

- Implemented service tests for bill splits decimal precision handling:
  * Created `tests/unit/services/test_bill_splits.py` with 7 detailed test cases
  * Added tests for equal distribution with largest remainder method
  * Implemented special test cases for the "$100 split three ways" scenario
  * Added tests for common bill amount distributions
  * Created mock-based tests to isolate decimal precision validation
  * Added tests for precise split amount validation

### Changed
- Updated ADR-013 implementation checklist to reflect progress:
  * Documentation phase completed (100%)
  * Service tests implementation progress updated (33%)
  * Overall implementation progress improved to 93%
  * Updated remaining priority tasks to reflect current status

## [0.4.23] - 2025-03-19

### Fixed
- Fixed credit utilization impact value in recommendations schema test:
  * Fixed `test_bill_payment_timing_recommendation_valid` to use Decimal("0.05") instead of Decimal("5.00") for credit_utilization_impact
  * Resolved validation error: "Input should be less than or equal to 1"
  * All schema tests now using correct 0-1 range for percentage values
  * All 316 tests now passing successfully
  * Confirmed proper validation for PercentageDecimal type with Field(ge=0, le=1, multiple_of=Decimal("0.0001"))

## [0.4.22] - 2025-03-19

### Fixed
- Fixed schema tests for Pydantic V2 percentage range validation:
  * Fixed `test_impact_analysis_schemas.py` to use 0-1 range for credit utilization (changed from 0-100 range)
  * Updated `test_recommendations_schemas.py` to use 0-1 range for credit utilization impact
  * Updated `impact_analysis.py` schema to properly use PercentageDecimal without redundant constraints
  * Updated `recommendations.py` schema to use PercentageDecimal with proper percentage range
  * Updated validation error message patterns to match Pydantic V2 format
  * Fixed test case values to match the 0-1 percentage scale
  * Replaced `decimal_places=1` with `multiple_of=Decimal("0.1")` in recommendations.py
- Updated ADR-013 implementation checklist to reflect progress (91% complete, back to previous level)

## [0.4.21] - 2025-03-19

### Fixed
- Fixed schema tests for Pydantic V2 decimal validation:
  * Updated `test_accounts_schemas.py` with correct error message expectations for 'multiple_of' validation
  * Fixed `test_bill_splits_schemas.py` with Decimal objects in assertions instead of float values
  * Updated `test_balance_reconciliation_schemas.py` with proper error message patterns
  * Fixed `test_income_schemas.py` validation error message assertions
  * Updated `test_income_trends_schemas.py` to use Decimal objects in comparisons
  * Fixed `test_payment_patterns_schemas.py` to use Decimal instead of float for confidence scores
  * Updated `test_payment_schedules_schemas.py` with correct decimal validation error messages
  * Fixed `test_payments_schemas.py` with proper error expectations
  * Updated `test_realtime_cashflow_schemas.py` decimal precision test expectations
  * Fixed `test_recommendations_schemas.py` decimal precision error messages
  * Updated `test_recurring_bills_schemas.py` decimal precision validation messages
- Updated ADR-013 implementation checklist to reflect fixed schema tests (91% complete, up from 87%)

## [0.4.20] - 2025-03-19

### Fixed
- Fixed `impact_analysis.py` schema to use Pydantic V2 Annotated types:
  * Replaced `BaseSchemaValidator.money_field()` calls with `MoneyDecimal` type
  * Replaced `BaseSchemaValidator.percentage_field()` calls with `PercentageDecimal` type
  * Updated percentage ranges from 0-100 to 0-1 to match PercentageDecimal expectations
  * Fixed AttributeError that occurred when running schema tests
- Updated implementation checklist to accurately reflect completed schema files

## [0.4.19] - 2025-03-19

### Changed
- Updated schema test files for Pydantic V2 compatibility:
  * Updated test_accounts_schemas.py to reflect Pydantic V2 error messages
  * Updated test_bill_splits_schemas.py with new validation pattern expectations
  * Updated test_payments_schemas.py with correct error message expectations
  * Updated test_deposit_schedules_schemas.py for Pydantic V2 compatibility
  * Updated test_credit_limits_schemas.py with new validation message expectations
  * Updated test_balance_history_schemas.py with proper error message patterns
  * Updated test_cashflow_base_schemas.py with correct decimal validation patterns
  * Updated test_cashflow_metrics_schemas.py with Pydantic V2 validation messages
  * Added appropriate type imports to all updated test files

### Fixed
- Fixed percentage field validation messages in test_cashflow_account_analysis_schemas.py
- Fixed percentage field validation messages in test_cashflow_historical_schemas.py
- Updated ADR-013 implementation checklist to reflect 100% test completion
- Updated progress tracking in active_context.md and progress.md

## [0.4.18] - 2025-03-19

### Added
- Completed schema file updates for Pydantic V2 compatibility:
  * Updated all remaining schema files with Annotated types approach
  * Implemented MoneyDecimal type for 2 decimal place monetary fields
  * Implemented PercentageDecimal type for 4 decimal place percentage fields
  * Implemented dictionary validation for collections of decimal values
  * All schema files now use the Pydantic V2-compatible approach

### Changed
- Enhanced ADR-013 Implementation Checklist:
  * Improved progress tracking (91% complete, up from 89%)
  * Completed Phase 3 (Schema Updates) of the implementation
  * Updated task priorities to focus on schema tests and documentation
  * Enhanced overall documentation with new approach details

### Fixed
- Updated validation patterns for consistency across all schema files
- Replaced all BaseSchemaValidator utility methods with direct type annotations
- Improved field constraints documentation across all schema files
- Added proper field descriptions for better API documentation

## [0.4.17] - 2025-03-19

### Changed
- Continued implementation of Pydantic V2 compatible decimal precision handling:
  * Updated `src/schemas/income.py` with MoneyDecimal type annotations
  * Updated `src/schemas/income_trends.py` with MoneyDecimal and PercentageDecimal types
  * Updated `src/schemas/transactions.py` with MoneyDecimal type annotations
  * Replaced all utility method calls with direct type annotations
  * Converted percentage fields to PercentageDecimal for proper validation
  * Added proper Field constraints with descriptions

### Fixed
- Updated ADR-013 implementation checklist to accurately reflect progress (85% complete, up from 82%)
- Added comprehensive field descriptions to all updated schema files

## [0.4.16] - 2025-03-18

### Changed
- Continued implementation of Pydantic V2 compatible decimal precision handling:
  * Updated `src/schemas/cashflow/forecasting.py` with MoneyDecimal and PercentageDecimal types
  * Updated `src/schemas/cashflow/historical.py` with MoneyDecimal and PercentageDecimal types
  * Updated `src/schemas/cashflow/account_analysis.py` with MoneyDecimal, PercentageDecimal, and CorrelationDecimal types
  * Replaced all utility method calls with direct type annotations
  * Updated test files to match the new validation approach
  * Added proper dictionary type aliases for collections of decimal values

### Fixed
- Updated schema tests with correct Pydantic V2 validation error message patterns
- Updated implementation checklist to accurately reflect progress (82% complete, up from 77%)

## [0.4.15] - 2025-03-18

### Changed
- Continued implementation of Pydantic V2 compatible decimal precision handling:
  * Updated `src/schemas/cashflow/base.py` with new MoneyDecimal type annotations
  * Updated `src/schemas/cashflow/metrics.py` with new MoneyDecimal type annotations
  * Replaced all utility method calls (money_field) with direct type annotations
  * Added proper Field constraints with descriptions to maintain validation
  * Maintained consistent Field naming and documentation conventions

### Fixed
- Fixed implementation checklist to accurately reflect progress (77% complete, up from 76%)

## [0.4.14] - 2025-03-18

### Added
- Implemented Pydantic V2 compatible approach for decimal precision handling:
  * Created Annotated type definitions in schemas/__init__.py (MoneyDecimal, PercentageDecimal, etc.)
  * Implemented dictionary validation strategy for decimal fields
  * Updated BaseSchemaValidator with model_validator for dictionaries
  * Updated accounts.py schema with new Annotated types as proof of concept
  * Updated bill_splits.py schema with dictionary validation for IntPercentageDict

### Changed
- Replaced utility methods with direct type annotations:
  * Replaced money_field() calls with MoneyDecimal type annotations
  * Replaced percentage_field() calls with PercentageDecimal type annotations
  * Implemented typed dictionary support with IntMoneyDict and IntPercentageDict
  * Enhanced schema field documentation with migration to Annotated types
  * Maintained all field constraints and validation behavior

## [0.4.13] - 2025-03-18

### Changed
- Reverted ConstrainedDecimal implementation due to Pydantic V2 incompatibility:
  * Identified that `ConstrainedDecimal` class has been removed in Pydantic V2
  * Performed git reset to previous working commit (f31eb74)
  * Created comprehensive implementation plan compatible with Pydantic V2
  * Documented new approach in `docs/adr/013-decimal-precision-handling-update.md`

### Added
- Created new implementation plan for decimal precision handling with Pydantic V2:
  * Added `docs/adr/compliance/adr013_implementation_checklist_v2.md` with phased approach
  * Created `docs/adr/compliance/annotated_types_reference.py` with examples
  * Designed robust dictionary validation strategy for decimal values
  * Developed detailed examples using Annotated types with Field constraints
  * Reset progress tracking for components requiring revision

## [0.4.12] - 2025-03-17

### Fixed
- Fixed parameter passing in cashflow schema files:
  * Repaired corrupted `src/schemas/cashflow/base.py` file with proper indentation and structure
  * Fixed money_field() and percentage_field() calls to use proper keyword arguments (default=...)
  * Updated `src/schemas/cashflow/metrics.py` with keyword parameter format
  * Fixed `src/schemas/cashflow/forecasting.py` to use correct parameter passing
  * Updated `src/schemas/cashflow/historical.py` to use keyword parameters
  * Fixed "takes 2 positional arguments but 3 were given" errors in BaseSchemaValidator calls
- Fixed test file corruption:
  * Repaired `tests/unit/schemas/test_accounts_schemas.py` with duplicated content
  * Fixed syntax error with imports appearing after function definition
  * Restored proper structure with imports at the beginning of file

## [0.4.11] - 2025-03-17

### Added
- Enhanced schema validation tests for decimal precision handling:
  * Added comprehensive tests for monetary field validation with 2 decimal places
  * Added tests for percentage field validation with 4 decimal places
  * Added tests for "$100 split three ways" case across schema test files
  * Added epsilon tolerance tests for sum validation
  * Added tests for money_field() vs percentage_field() validation

### Changed
- Updated bill_splits, payments, and accounts schema tests:
  * Enhanced test_bill_splits_schemas.py with all decimal precision formats
  * Updated test_payments_schemas.py with epsilon tolerance tests
  * Enhanced test_accounts_schemas.py for money_field() utility
  * Added test for BaseSchemaValidator field methods
- Updated cashflow schema tests for percentage validation:
  * Enhanced tests for percentage fields with 4 decimal places
  * Added validation tests for risk assessment percentage fields
  * Verified appropriate validation for different precision needs
- Updated ADR-013 implementation checklist to 90% complete (up from 86%)
  * Marked Schema Tests as completed (6/6)
  * Updated BaseSchemaValidator implementation as completed
  * Reorganized remaining priority tasks

### Fixed
- Fixed error message assertions across all schema test files
- Standardized validation test patterns for decimal precision
- Enhanced test coverage to verify decimal validation consistency

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

## [0.3.47] - 2025-02-15

### Added
- Payment pattern analysis system
  - Pattern detection with confidence scoring:
    * Regular payment pattern detection
    * Irregular payment identification
    * Seasonal pattern recognition
    * Monthly pattern analysis
  - Comprehensive metrics tracking:
    * Frequency metrics (average days between, std dev, min/max)
    * Amount statistics (average, std dev, min/max, total)
    * Pattern-specific confidence scoring
  - Features include:
    * Account-specific pattern analysis
    * Category-based pattern detection
    * Date range filtering
    * Minimum sample size configuration
    * Pattern type classification
    * Detailed analysis notes
  - Comprehensive test coverage including:
    * Regular payment scenarios
    * Irregular payment detection
    * Seasonal pattern identification
    * Insufficient data handling
    * Date range filtering
    * All tests passing

## [0.3.46] - 2025-02-15

### Added
- Balance history system
  - New balance_history table for tracking balance changes
  - Balance history schemas with Pydantic models
  - Balance history service with:
    * Balance change recording
    * Historical data retrieval
    * Balance trend analysis
    * Reconciliation support
    * Volatility calculation
    * Trend direction detection
  - Comprehensive test coverage including:
    * Balance recording scenarios
    * Historical data retrieval
    * Trend analysis
    * Reconciliation workflow
    * Error handling
    * All tests passing

## [0.3.45] - 2025-02-15

### Added
- Account-specific forecasts system
  - Account-specific forecast schemas
    * AccountForecastRequest for configurable options
    * AccountForecastResult for daily forecast details
    * AccountForecastResponse for complete forecast data
    * AccountForecastMetrics for account-specific metrics
  - Features include:
    * Daily balance projections
    * Recurring bill handling with monthly patterns
    * Credit utilization tracking for credit accounts
    * Warning flags for low balances and high utilization
    * Confidence scoring system
    * Transaction-level detail tracking
    * Balance volatility calculation
  - Comprehensive test coverage including:
    * Basic forecast scenarios
    * Credit account handling
    * Warning flag detection
    * Recurring bill patterns
    * All tests passing

## [0.3.44] - 2025-02-15

### Added
- Historical trends analysis system
  - Pattern detection with confidence scoring
    * Transaction type-based averages
    * 1.1x threshold for significant events
    * Explicit decimal conversions
    * Minimum confidence floor of 0.1
  - Holiday impact analysis
    * Extended date range to ±7 days
    * Proper holiday date calculations
    * Improved impact detection
  - Seasonality analysis
    * Monthly patterns tracking
    * Day of week patterns
    * Day of month patterns
    * Holiday impact tracking
  - Significant event detection
    * Transaction type-based thresholds
    * Amount-based event descriptions
    * Improved detection accuracy
  - Comprehensive test coverage including:
    * Empty data handling
    * Significant event detection
    * Seasonal pattern analysis
    * Holiday impact verification
    * All tests passing

## [0.3.43] - 2025-02-14

### Added
- Custom forecast system
  - New schemas for custom forecasting:
    * CustomForecastParameters for configurable forecast options
    * CustomForecastResult for daily forecast details
    * CustomForecastResponse for complete forecast data
  - Features include:
    * Account filtering
    * Category-based filtering
    * Confidence scoring
    * Risk factor assessment
    * Contributing factor tracking
    * Summary statistics
  - Comprehensive test coverage including:
    * Basic forecast scenarios
    * Category filtering
    * Account validation
    * All tests passing

## [0.3.42] - 2025-02-14

### Added
- Cross-account analysis system
  - Account correlation analysis
    * Transfer frequency tracking
    * Common category identification
    * Relationship type detection (complementary/supplementary/independent)
    * Correlation scoring
  - Transfer pattern analysis
    * Average transfer amounts
    * Transfer frequency tracking
    * Category distribution analysis
    * Typical transfer timing detection
  - Usage pattern analysis
    * Primary use detection
    * Average transaction size calculation
    * Common merchant tracking
    * Peak usage day identification
    * Category preference analysis
    * Credit utilization tracking
  - Balance distribution analysis
    * Average balance tracking
    * Balance volatility calculation
    * 30-day min/max tracking
    * Typical balance range analysis
    * Total funds percentage calculation
  - Risk assessment system
    * Overdraft risk calculation
    * Credit utilization risk tracking
    * Payment failure risk assessment
    * Volatility scoring
    * Overall risk scoring
  - New API endpoint `/realtime-cashflow/cross-account-analysis`
  - Comprehensive test coverage including:
    * Account correlation scenarios
    * Transfer pattern detection
    * Usage pattern analysis
    * Balance distribution calculations
    * Risk assessment accuracy
    * All tests passing

## [0.3.41] - 2025-02-14

### Added
- Real-time cashflow tracking system
  - Account balance aggregation across all accounts
  - Real-time available funds calculation
  - Available credit tracking
  - Next bill due date tracking
  - Days until next bill calculation
  - Minimum balance requirements
  - Projected deficit calculation
  - Comprehensive test coverage including:
    * Account balance aggregation
    * Available funds calculation
    * Next bill identification
    * Deficit scenarios
    * All tests passing


## [0.3.40] - 2025-02-14

### Added
- Income analysis API endpoints
  - New POST `/api/v1/income-analysis/trends` endpoint for comprehensive income analysis
  - New GET `/api/v1/income-analysis/trends/source/{source}` endpoint for source-specific analysis
  - New GET `/api/v1/income-analysis/trends/period` endpoint for period-based analysis
  - Features include:
    * Pattern detection with confidence scoring
    * Source-specific trend analysis
    * Period-based income analysis
    * Seasonality metrics
    * Source statistics
  - Comprehensive test coverage including:
    * Empty data handling
    * Source-specific analysis
    * Period-based analysis
    * Invalid parameter handling
    * All tests passing with proper fixtures

## [0.3.39] - 2025-02-14

### Added
- Recurring income system
  - New recurring_income table for managing recurring income templates
  - Support for generating income entries from recurring patterns
  - Auto-deposit configuration
  - Monthly income generation capability
  - Proper relationship handling between accounts, recurring income, and income entries
  - Comprehensive test coverage including:
    * Template creation and validation
    * Income generation functionality
    * Auto-deposit handling
    * SQLite-compatible date handling
    * All tests passing with 100% coverage

## [0.3.38] - 2025-02-14

### Added
- Deposit scheduling system
  - New deposit_schedules table for managing income deposits
  - Support for scheduling deposits to specific accounts
  - Recurring deposit configuration
  - Validation for deposit amounts against income
  - Relationship tracking between income and accounts
  - Comprehensive test coverage including:
    * Schedule creation and validation
    * Amount validation against income
    * Schedule updates and deletions
    * Pending deposit tracking
    * Account-specific filtering

## [0.3.37] - 2025-02-14

### Added
- Income trends analysis system
  - Pattern detection with confidence scoring
    * Weekly, monthly, and irregular pattern detection
    * Confidence scoring for pattern reliability
    * Next occurrence prediction for reliable patterns
  - Seasonality analysis
    * Monthly peak and trough detection
    * Variance coefficient calculation
    * Confidence scoring for seasonal patterns
  - Source statistics tracking
    * Total and average amount calculations
    * Reliability scoring based on consistency
    * Standard deviation and variance tracking
  - Comprehensive test coverage including:
    * Pattern detection scenarios
    * Seasonality analysis
    * Source statistics calculation
    * Error handling
    * Edge cases
  - Technical improvements:
    * Proper Decimal type handling
    * Strong type safety with Pydantic
    * Efficient database queries

## [0.3.36] - 2025-02-14

### Added
- Income categorization system
  - New income_categories table for managing income categories
  - Category relationship added to income records
  - RESTful API endpoints for category management:
    * Create, read, update, delete operations
    * List all categories
    * Assign categories to income
  - Comprehensive validation at schema and service levels
  - Complete test coverage including:
    * Service layer tests (8 test cases)
    * API endpoint tests (9 test cases)
    * Error handling scenarios
    * Duplicate category prevention

## [0.3.35] - 2025-02-14

### Added
- Bill splits impact analysis system
  - Account impact calculations with projected balances
  - Credit utilization tracking and projections
  - Cashflow impact analysis with deficit detection
  - Risk scoring system with weighted factors
  - Recommendation generation based on risk factors
  - Comprehensive test coverage including:
    * Basic split impact scenarios
    * High-risk scenarios
    * Cashflow impact calculations
    * Credit utilization risk detection

## [0.3.34] - 2025-02-14

### Added
- Bill splits bulk operations API endpoints
  - New POST `/api/v1/bill-splits/bulk` endpoint for processing bulk operations
  - New POST `/api/v1/bill-splits/bulk/validate` endpoint for validation-only mode
  - Comprehensive integration tests for API endpoints
  - Fixed decimal serialization in API tests
  - Complete test coverage including:
    * Successful bulk operations
    * Validation failures
    * Invalid liability scenarios
    * Transaction rollback testing

## [0.3.33] - 2025-02-13

### Added
- Bill splits bulk operations system
  - Bulk operation schema with create/update support
  - Transaction-based bulk processing
  - Validation-only mode for dry runs
  - Comprehensive error tracking
  - Rollback support for failed operations
  - Detailed operation results
  - Success/failure tracking per split
  - Complete test coverage including:
    * Successful bulk operations
    * Partial failure scenarios
    * Validation-only operations
    * Transaction rollback
    * Error handling

## [0.3.32] - 2025-02-13

### Added
- Bill splits historical analysis system
  - Pattern identification with confidence scoring
  - Category and seasonal pattern grouping
  - Account usage frequency tracking
  - New GET `/api/v1/bill-splits/analysis/{bill_id}` endpoint
  - Comprehensive test coverage for analysis features
  - Pattern-based metrics and insights
  - Historical trend analysis
  - Weighted confidence scoring based on frequency and recency
  - Detailed pattern metrics including:
    * Total splits analyzed
    * Unique patterns identified
    * Average splits per bill
    * Account usage statistics
    * Category-based patterns
    * Seasonal trends

## [0.3.31] - 2025-02-13

### Added
- Bill splits suggestion system
  - Historical pattern-based suggestions with confidence scoring
  - Available funds-based suggestions across multiple accounts
  - New GET `/api/v1/bill-splits/suggestions/{bill_id}` endpoint
  - Comprehensive test coverage for service and API layers
  - Smart account selection based on available balances and credit limits
  - Detailed suggestion reasoning and confidence scores

## [0.3.30] - 2025-02-13

### Added
- Enhanced bill splits validation system
  - Comprehensive validation rules at schema and service levels
  - Balance and credit limit validation for accounts
  - Duplicate account detection
  - Total amount validation against liability
  - Custom BillSplitValidationError for better error handling
  - Complete test coverage for validation scenarios
  - Integration with existing bill splits system

### Changed
- Improved bill splits service with robust validation
- Enhanced test infrastructure for bill splits
- Updated documentation with validation rules

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

## [0.3.23] - 2025-02-13

### Fixed
- Fixed auto-pay functionality and validation
  - Fixed Decimal serialization in auto-pay settings
  - Improved auto-pay state management
  - Enhanced auto-pay candidates functionality
  - Fixed validation for preferred_pay_date
  - Removed redundant custom validator in favor of Pydantic Field validation
  - Enhanced test coverage for invalid settings
  - Improved validation error handling in API
  - Added detailed error response validation in tests
  - Standardized model_dump usage across all serialization points

## [0.3.22] - 2025-02-13

### Fixed
- Fixed category API error handling
  - Added proper CategoryError handling in API endpoints
  - Updated error response status codes
  - Fixed Pydantic circular imports in schemas
  - Updated validator methods for Pydantic v2 compatibility
  - Improved error messages for duplicate categories

## [0.3.21] - 2025-02-13

### Fixed
- Fixed recurring bills test suite
  - Added category_id to all test fixtures
  - Updated test assertions for generated bills
  - Fixed category relationship testing
  - Standardized category handling in tests
  - Fixed all test failures
  - Improved test coverage for bill generation

## [0.3.20] - 2025-02-13

### Fixed
- Fixed category handling in liabilities and recurring bills
  - Added proper category_id field to RecurringBill model
  - Updated RecurringBill schemas to include category_id
  - Fixed category relationship in RecurringBill service
  - Updated test fixtures to use category_id
  - Fixed string category usage in liability generation
  - Improved test coverage for category relationships
  - Fixed '_sa_instance_state' errors in tests

### Changed
- Enhanced recurring bills system
  - Added category relationship to RecurringBill model
  - Improved liability generation with proper category handling
  - Updated test infrastructure for better category support

## [0.3.19] - 2025-02-12

### Added
- Hierarchical category management system
  - Parent-child category relationships
  - Full path property for category hierarchy
  - Circular reference prevention
  - Comprehensive validation
  - Category service with CRUD operations
  - Support for nested categories
  - Category error handling
  - Complete test coverage
    - Service layer tests
    - Hierarchical operations
    - Error scenarios
    - 16 test cases covering all functionality

### Changed
- Enhanced category model with hierarchical support
- Improved category service with validation
- Updated test infrastructure for categories

## [0.3.18] - 2025-02-12

### Added
- Auto-pay functionality for bills
  - Auto-pay settings management
  - Preferred payment date configuration
  - Payment method selection
  - Minimum balance requirements
  - Retry on failure options
  - Email notification support
  - Auto-pay status tracking
  - Last attempt tracking
  - Candidate bill identification
  - Manual processing capability
  - Comprehensive test coverage
    - Service layer tests
    - API endpoint tests
    - Edge case handling
    - Validation testing

### Changed
- Enhanced liability model with auto-pay fields
- Improved payment processing system
- Updated API documentation

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
