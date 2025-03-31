# Debtonator Code Review Checklist

## Overview

This checklist serves as a comprehensive verification tool for ensuring code quality and architectural compliance across the Debtonator application. It contains critical requirements derived from Architecture Decision Records (ADRs), system patterns, and implementation guides. All items are considered mandatory requirements.

## Repository Layer (ADR-014)

### Structure

- [ ] Repository extends `BaseRepository` with proper generic type parameters
- [ ] Repository constructor accepts a session parameter and passes it to the parent class
- [ ] Repository includes appropriate model-specific methods beyond CRUD operations
- [ ] Repository focuses purely on data access with no business logic or validation

### Transaction Management

- [ ] Bulk operations correctly handle transactions
- [ ] Methods with multiple DB operations use proper transaction boundaries
- [ ] Error handling includes appropriate transaction rollback
- [ ] Complex operations that modify multiple entities use a single transaction

### Query Performance

- [ ] Relationship loading uses appropriate strategies (joinedload/selectinload)
- [ ] Pagination implemented for methods returning large result sets
- [ ] Query filters are properly indexed in the database model
- [ ] Complex joins avoid Cartesian products

### SQL Aggregation

- [ ] Uses `func.sum(column)` with `group_by()` for proper aggregation
- [ ] For counting with LEFT JOINs, uses `func.count(specific_column)` instead of `func.count()`
- [ ] Handles NULL values appropriately in aggregations
- [ ] Tests aggregation queries with both empty and populated related tables

## Service Layer (ADR-012, ADR-014)

### Validation Flow

- [ ] Service methods validate input through Pydantic schemas before passing to repositories
- [ ] Complex business rules are validated in the service layer, not repositories
- [ ] State validation (e.g., account balance checks) are in service layer
- [ ] Relationship validation (e.g., entity existence) occurs in service layer
- [ ] Service methods handle validation errors with clear, actionable messages

### Repository Usage

- [ ] Services use repositories for all data access
- [ ] Services only pass validated data to repositories
- [ ] Services handle repository errors appropriately
- [ ] Services never construct DB models directly, using repositories instead

### Business Logic

- [ ] Service methods implement all business rules
- [ ] State management logic is in service layer, not models
- [ ] Cross-entity validation is handled in service layer
- [ ] No SQL queries or ORM operations directly in service methods

## Schema Validation (ADR-012)

### Schema Structure

- [ ] Schema extends `BaseSchemaValidator` for consistent validation
- [ ] Field constraints use Pydantic's Field annotations
- [ ] Cross-field validation uses proper validator methods
- [ ] Field documentation is clear and complete

### Pydantic V2 Compatibility

- [ ] Uses `@field_validator` instead of deprecated `@validator`
- [ ] Validator methods have the `@classmethod` decorator
- [ ] Validators use the proper signature without passing the class as first argument
- [ ] Uses `model_dump()` instead of deprecated `dict()`

### Dictionary Validation

- [ ] Dictionary fields with decimal values have proper validation
- [ ] Nested dictionaries are properly validated
- [ ] Dictionary validations handle invalid values appropriately
- [ ] Complex nested structures use validator methods for deep validation

## Decimal Precision (ADR-013)

### Type Annotations

- [ ] Monetary values use `MoneyDecimal` annotated type
- [ ] Percentage values use `PercentageDecimal` annotated type
- [ ] Dictionary fields with decimal values use appropriate dictionary types
- [ ] Field constraints are declared using Pydantic V2 Annotated types with Field

### Database Storage

- [ ] Database columns use `Numeric(12, 4)` for monetary values
- [ ] Internal calculations maintain 4 decimal precision
- [ ] UI/API boundaries enforce 2 decimal precision
- [ ] Rounding operations use appropriate rounding mode (ROUND_HALF_UP)

### Distribution Strategies

- [ ] Bill splits and allocations use largest remainder method
- [ ] Fixed total distributions ensure exact sums
- [ ] Percentage distributions use 4 decimal precision internally
- [ ] Money distribution utilities are used consistently

## Datetime Handling (ADR-011)

### UTC Compliance

- [ ] All datetime fields use UTC for storage and calculations
- [ ] No timezone parameters in SQLAlchemy DateTime columns
- [ ] All datetime creation uses functions from `datetime_utils.py`
- [ ] Pydantic schemas validate datetime fields for UTC timezone

### Utility Function Usage

- [ ] Uses `utc_now()` instead of `datetime.now()`
- [ ] Uses `utc_datetime()` for creating datetime objects
- [ ] Uses `days_ago()` and `days_from_now()` for date arithmetic
- [ ] Uses comparison utilities for datetime comparisons (`datetime_equals()`, etc.)

### Utility Function Usage Compliance

- [ ] NEVER uses `datetime.now()` directly (must use `utc_now()` instead)
- [ ] NEVER creates naive datetimes with `datetime(year, month, day)` (must use `utc_datetime()` instead)
- [ ] NEVER uses raw timedelta arithmetic (must use appropriate utility functions)
- [ ] Uses correct utility function for each common task (see ADR-011 reference table)

### Date Range Handling

- [ ] Date ranges are inclusive of both start and end dates
- [ ] Date range queries use `start_of_day()` and `end_of_day()` from `datetime_utils.py`
- [ ] Comparison operators use `<=` for end date (inclusive)
- [ ] Date range boundaries are clearly documented in method signatures
- [ ] Date range method documentation explicitly states "inclusive of both dates"

### Cross-Database Compatibility

- [ ] Database date values are normalized with `normalize_db_date()`
- [ ] Date comparisons use `date_equals()` or `datetime_equals()` utilities
- [ ] SQL queries avoid database-specific date functions
- [ ] Date collection operations use appropriate utility functions (`date_in_collection()`, etc.)
- [ ] Date filtering uses database-agnostic comparison functions
- [ ] Tests include cross-database compatible date assertions
- [ ] Repository methods normalize datetime values from database results

## Models and SQLAlchemy (ADR-012)

### Model Structure

- [ ] Model focuses on data structure, not business logic
- [ ] No `@validates` decorators in model (validation belongs in schema layer)
- [ ] Relationships are properly defined with `back_populates`
- [ ] Model includes appropriate indexes and constraints

### Relationship Configuration

- [ ] Cascade behavior is appropriate for the relationship
- [ ] Foreign keys are properly defined
- [ ] Lazy loading settings make sense for the relationship
- [ ] Many-to-many relationships use association tables correctly

### Type Annotations

- [ ] Uses `Mapped[Type]` annotations for fields
- [ ] Nullable fields use `Optional[Type]` or `Mapped[Optional[Type]]`
- [ ] Collection relationships use proper collection types
- [ ] Default values are appropriate and type-safe

### Optimization Patterns

- [ ] Complex queries have appropriate indexes
- [ ] Composite indexes for commonly filtered fields
- [ ] Lazy loading used only where appropriate
- [ ] Bulk operations optimize for performance

## Testing Patterns

### Repository Testing

- [ ] Tests follow the Arrange-Schema-Act-Assert pattern
- [ ] Uses schema factories to create test data
- [ ] Tests include error cases and edge conditions
- [ ] Tests verify proper relationship handling
- [ ] Tests create data through Pydantic schemas before passing to repositories
- [ ] Tests convert schemas to dictionaries using `model_dump()` before repository calls
- [ ] Tests never pass raw dictionaries directly to repository methods
- [ ] Tests follow strict No Mocks Policy (no unittest.mock or MagicMock usage)

### Schema Testing

- [ ] Tests verify field constraints as defined
- [ ] Tests include validation error cases
- [ ] Tests cover cross-field validators
- [ ] Tests include dictionary validation if applicable

### Service Testing

- [ ] Tests verify service validation logic
- [ ] Tests verify service business rules
- [ ] Tests cover error handling and edge cases
- [ ] Tests use real repositories with test database fixtures
- [ ] Tests never use unittest.mock or MagicMock

### Integration Tests

- [ ] Tests verify component interactions
- [ ] Tests verify transaction boundaries
- [ ] Tests validate expected database state
- [ ] Tests include performance considerations for complex queries

## API Layer (ADR-010)

### Endpoint Design

- [ ] API endpoints follow consistent URL patterns
- [ ] API endpoints use appropriate HTTP methods
- [ ] API responses follow standardized formats
- [ ] API documentation is complete and accurate

### API Dependencies

- [ ] Endpoints use appropriate dependency injection
- [ ] Services are injected with repositories
- [ ] Authentication and authorization is properly enforced
- [ ] Error handling is consistent and informative

### Response Formatting

- [ ] Response models are properly defined
- [ ] Pagination is implemented for list endpoints
- [ ] Error responses are consistent and informative
- [ ] Decimal values are properly formatted at API boundaries

## Documentation

### Code Documentation

- [ ] Function and method docstrings are complete and accurate
- [ ] Parameters and return values are documented
- [ ] Complex logic is explained with comments
- [ ] Error conditions are documented

### API Documentation

- [ ] API endpoints have complete documentation
- [ ] Request and response models are documented
- [ ] Error cases are documented
- [ ] Examples are provided for complex endpoints

## Cross-Cutting Concerns

### Error Handling

- [ ] Exceptions are caught and handled appropriately
- [ ] Error messages are clear and actionable
- [ ] Error handling doesn't swallow important exceptions
- [ ] Custom exceptions are used where appropriate

### Type Safety

- [ ] Functions and methods have type annotations
- [ ] Variables have appropriate type annotations
- [ ] Generic types are used appropriately
- [ ] Type narrowing is used correctly

### Security

- [ ] Input validation is thorough
- [ ] No sensitive data in logs or error messages
- [ ] Authentication checks are consistent
- [ ] Authorization checks are enforced

## ADR Implementation Status

### ADR-011: DateTime Standardization

- [ ] SQLAlchemy models use simple `DateTime()` without timezone parameter
- [ ] New datetime objects are created with `utc_now()` or `utc_datetime()`
- [ ] Pydantic validators ensure datetimes have UTC timezone
- [ ] Date range handling follows inclusive pattern with proper boundaries

### ADR-012: Validation Layer Standardization

- [ ] SQLAlchemy models only have database constraints, no business logic
- [ ] Pydantic schemas handle data structure validation
- [ ] Service layer implements business rules and validation
- [ ] Clear separation of concerns between layers

### ADR-013: Decimal Precision Handling

- [ ] Monetary values use 2 decimal places at UI/API boundaries
- [ ] Database stores 4 decimal places for monetary values
- [ ] Pydantic V2 Annotated types used for field constraints
- [ ] Dictionary fields with decimal values properly validated

### ADR-014: Repository Layer

- [ ] Repository pattern used for data access
- [ ] BaseRepository extended for model-specific repositories
- [ ] Repository-specific methods added as needed
- [ ] Repository tests follow the Arrange-Schema-Act-Assert pattern

### ADR-015: Default Category Implementation

- [ ] Default "Uncategorized" category used when no category specified
- [ ] System flag protects system categories from modification
- [ ] Repository methods respect system category protection
- [ ] Default category exists in all environments
- [ ] Repository update() and delete() methods check system flag before modification
- [ ] Constants file defines DEFAULT_CATEGORY_ID and DEFAULT_CATEGORY_NAME
- [ ] Database initialization ensures default category creation
- [ ] Service methods handle default category as a special case

### ADR-017: Payment Source Schema Simplification

- [ ] Single `PaymentSourceCreate` schema used for creation
- [ ] PaymentSource treated as child entity of Payment
- [ ] Repository handles parent-child relationship
- [ ] Tests use updated schema approach
- [ ] Repository.create() method handles payment_id assignment
- [ ] PaymentRepository manages parent-child relationship properly
- [ ] No circular dependencies in schema definitions
- [ ] No standalone PaymentSource creation (always through a Payment)
- [ ] Tests verify parent-child relationship integrity

## Code Organization

- [ ] Code is modularized appropriately
- [ ] Files follow consistent naming conventions
- [ ] Related functionality is grouped logically
- [ ] Code follows project structure conventions
