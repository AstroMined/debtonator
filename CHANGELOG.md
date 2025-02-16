# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
