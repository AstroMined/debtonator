# Debtonator Code Review Checklist

## Overview

This checklist is designed to ensure consistency across all components of the Debtonator application, with a specific focus on backend code quality and adherence to established architectural patterns. It is derived from a comprehensive analysis of all Architecture Decision Records (ADRs) to identify the most relevant standards and patterns.

Each section corresponds to a key architectural area, with specific checklist items that should be verified during code review. Items are prioritized based on their impact on code quality and system integrity.

## Repository Layer (ADR-014)

### Basic Repository Structure
- [ ] Repository extends `BaseRepository` with proper generic type parameters
- [ ] Repository constructor accepts a session parameter and passes it to the parent class
- [ ] Repository includes appropriate model-specific methods beyond CRUD operations
- [ ] Repository does not contain business logic (validation) that belongs in the service layer

### Validation Flow
- [ ] Repository methods assume data has been validated by the service layer
- [ ] Repository does not implement validation logic that should be in services or schemas
- [ ] Repository methods handle relationship loading appropriately (joinedload/selectinload)
- [ ] Repository tests use Pydantic schemas for validation before calling repository methods

### Transaction Management
- [ ] Bulk operations correctly handle transactions
- [ ] Methods with multiple DB operations use proper transaction boundaries
- [ ] Error handling includes appropriate transaction rollback
- [ ] Complex operations that modify multiple entities use a single transaction

### Repository Testing
- [ ] Tests follow the Arrange-Schema-Act-Assert pattern
- [ ] Tests use schema factories to create test data
- [ ] Tests include error cases and edge conditions
- [ ] Tests verify proper relationship handling

## Schema Validation (ADR-012)

### Schema Structure
- [ ] Schema extends `BaseSchemaValidator` for consistent validation
- [ ] Field constraints use Pydantic's Field annotations
- [ ] Cross-field validation uses proper validator methods
- [ ] Validation logic is appropriate for schema layer (no business rules)

### Pydantic V2 Compatibility
- [ ] Uses `@field_validator` instead of deprecated `@validator`
- [ ] Validator methods have the `@classmethod` decorator
- [ ] Validators use the proper signature without passing the class as first argument
- [ ] Uses `model_dump()` instead of deprecated `dict()`

### Decimal Precision (ADR-013)
- [ ] Monetary values use `MoneyDecimal` annotated type
- [ ] Percentage values use `PercentageDecimal` annotated type
- [ ] Dictionary fields with decimal values use appropriate dictionary types
- [ ] Database columns use `Numeric(12, 4)` for monetary values

### Dictionary Validation
- [ ] Dictionary fields with decimal values have proper validation
- [ ] Nested dictionaries are properly validated
- [ ] Dictionary validations handle invalid values appropriately
- [ ] Complex nested structures use validator methods for deep validation

## Datetime Handling (ADR-011)

### UTC Compliance
- [ ] All datetime fields use UTC for storage and calculations
- [ ] No timezone parameters in SQLAlchemy DateTime columns
- [ ] All datetime creation uses functions from `datetime_utils.py`
- [ ] Pydantic schemas validate datetime fields for UTC timezone

### Date Range Handling
- [ ] Date ranges are inclusive of both start and end dates
- [ ] Date range queries use `start_of_day()` and `end_of_day()` from `datetime_utils.py`
- [ ] Comparison operators are used correctly (`<=` for end date)
- [ ] Date range boundaries are clearly documented in method signatures

### Cross-Database Compatibility
- [ ] Database date values are normalized with `normalize_db_date()`
- [ ] Date comparisons use `date_equals()` or `datetime_equals()` utilities
- [ ] SQL queries avoid database-specific date functions
- [ ] Date collection operations use appropriate utility functions

### Utility Function Usage
- [ ] Uses `utc_now()` instead of `datetime.now()`
- [ ] Uses `utc_datetime()` for creating datetime objects
- [ ] Uses `days_ago()` and `days_from_now()` for date arithmetic
- [ ] Uses comparison utilities for datetime comparisons

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

### TypedDict Usage
- [ ] Uses `Mapped[Type]` annotations for fields
- [ ] Nullable fields use `Optional[Type]` or `Mapped[Optional[Type]]`
- [ ] Collection relationships use proper collection types
- [ ] Default values are appropriate and type-safe

### Database Schema
- [ ] Column types match field requirements
- [ ] Decimal columns use `Numeric(12, 4)` for monetary values
- [ ] Indexes support common query patterns
- [ ] Column constraints (unique, nullable) are appropriate

## Service Layer (ADR-012, ADR-014)

### Business Logic
- [ ] Service methods implement all business rules
- [ ] Complex validation is in service layer, not schema or repository
- [ ] Service methods use repositories for data access
- [ ] State management logic is in service layer, not models

### Schema Validation
- [ ] Service methods validate input data through Pydantic schemas
- [ ] Service methods validate business rules not covered by schemas
- [ ] Service methods handle validation errors appropriately
- [ ] Data passed to repositories has been validated

### Repository Usage
- [ ] Services use repositories for all data access
- [ ] Services use appropriate repository methods
- [ ] Services handle repository errors appropriately
- [ ] Services compose repository results as needed

### Error Handling
- [ ] Service methods return clear error messages
- [ ] Service methods use appropriate error types
- [ ] Service methods handle expected error conditions
- [ ] Service methods document error conditions

## General Code Quality

### Documentation
- [ ] Function and method docstrings are complete and accurate
- [ ] Parameters and return values are documented
- [ ] Complex logic is explained with comments
- [ ] Error conditions are documented

### Type Safety
- [ ] Functions and methods have type annotations
- [ ] Variables have appropriate type annotations
- [ ] Generic types are used appropriately
- [ ] Type narrowing is used correctly

### Error Handling
- [ ] Exceptions are caught and handled appropriately
- [ ] Error messages are clear and actionable
- [ ] Error handling doesn't swallow important exceptions
- [ ] Custom exceptions are used where appropriate

### Testing
- [ ] Unit tests cover normal and edge cases
- [ ] Integration tests verify component interactions
- [ ] Tests use appropriate fixtures and mocks
- [ ] Tests verify error conditions

## Implementation Status Checklist

### ADR-011: DateTime Standardization (Implemented)
- [ ] SQLAlchemy models use simple `DateTime()` without timezone parameter
- [ ] New datetime objects are created with `utc_now()` or `utc_datetime()`
- [ ] Pydantic validators ensure datetimes have UTC timezone
- [ ] Date range handling follows inclusive pattern with proper boundaries

### ADR-012: Validation Layer Standardization (Implemented)
- [ ] SQLAlchemy models only have database constraints, no business logic
- [ ] Pydantic schemas handle data structure validation
- [ ] Service layer implements business rules and validation
- [ ] Clear separation of concerns between layers

### ADR-013: Decimal Precision Handling (Implemented)
- [ ] Monetary values use 2 decimal places at UI/API boundaries (MoneyDecimal)
- [ ] Database stores 4 decimal places for monetary values (`Numeric(12, 4)`)
- [ ] Pydantic V2 Annotated types used for field constraints
- [ ] Dictionary fields with decimal values properly validated

### ADR-014: Repository Layer (Implemented)
- [ ] Repository pattern used for data access
- [ ] BaseRepository extended for model-specific repositories
- [ ] Repository-specific methods added as needed
- [ ] Repository tests follow the Arrange-Schema-Act-Assert pattern

### ADR-015: Default Category Implementation (Implemented)
- [ ] Default "Uncategorized" category used when no category specified
- [ ] System flag protects system categories from modification
- [ ] Repository methods respect system category protection
- [ ] Default category exists in all environments

### ADR-017: Payment Source Schema Simplification (Partial)
- [ ] Single `PaymentSourceCreate` schema used for creation
- [ ] PaymentSource treated as child entity of Payment
- [ ] Repository handles parent-child relationship
- [ ] Tests use updated schema approach

### ADR-016: Account Type Expansion (Proposed)
- [ ] [FUTURE] Consistent field naming between schema and parameter
- [ ] [FUTURE] Schema creation consistent throughout codebase
- [ ] [FUTURE] Prepare for polymorphic model structure

## API Enhancement Strategy (ADR-010)
- [ ] API endpoints follow consistent URL patterns
- [ ] API endpoints use appropriate HTTP methods
- [ ] API responses follow standardized formats
- [ ] API documentation is complete and accurate

## Notes for Reviewers

1. **Priority Focus Areas:**
   - Repository layer compliance with ADR-014
   - UTC datetime handling per ADR-011
   - Decimal precision handling per ADR-013
   - Validation layer standardization per ADR-012

2. **Known Technical Debt:**
   - Account type naming inconsistencies (type vs. account_type)
   - Parameter mapping in schema factories
   - Service layer refactoring for repository pattern

3. **Code Organization:**
   - Repository tests should follow Arrange-Schema-Act-Assert pattern
   - Schema factories should be used for test data creation
   - Service methods should focus on business logic
   - Models should focus on data structure only

## Documentation References

- [Repository Pattern Documentation](docs/repository_pattern.md)
- [Validation Strategy Guide](docs/validation_strategy.md)
- [UTC DateTime Standardization Guide](docs/datetime_handling.md)
- [Decimal Precision Implementation Guide](docs/decimal_precision_guide.md)
