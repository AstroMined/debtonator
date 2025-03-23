# ADR-016: Account Type Expansion

## Status

Proposed

## Context

The current system supports three account types: checking, savings, and credit. However, there's a need to expand this to support additional account types such as investment, loan, mortgage, and others. Each account type has unique properties and behaviors that don't fit well into the current model where all account types share the same database table with optional fields.

Current limitations:

1. All account types share the same fields, with validation to ensure certain fields are only used with specific account types
2. Adding new account-type-specific fields requires modifying the base Account model
3. Business logic for different account types is mixed in services
4. Test fixtures attempt to create account types not supported by the schema

## Decision

We propose to refactor the account model to use a polymorphic inheritance pattern:

1. Create a base `Account` model with common fields
2. Create specific models for each account type that inherit from the base model
3. Use SQLAlchemy's polymorphic relationships to handle the different account types
4. Move type-specific fields and methods to the appropriate subclass
5. Update schemas to reflect the new model structure
6. Update repositories and services to work with the polymorphic model

## Consequences

### Positive

- Cleaner separation of concerns for different account types
- Type-specific fields and validation contained in appropriate models
- Easier to add new account types without modifying existing code
- More intuitive object model that better represents the domain
- Improved type safety and IDE support

### Negative

- Significant refactoring effort required
- Potential for complex queries across the inheritance hierarchy
- Migration of existing data needed

### Neutral

- Changes to repository layer to handle polymorphic queries
- Updates to service layer to work with specific account types

## Implementation Plan

This refactoring will be deferred until after current refactoring efforts are complete. The implementation will follow these phases:

1. Design the polymorphic model structure
2. Create new models and schemas
3. Update repositories to work with the new structure
4. Migrate existing data
5. Update services and API endpoints
6. Update tests to use the new model structure

## Additional Technical Debt Identified

During implementation, we identified several layers of technical debt related to account type handling:

1. **Field Naming**: The field is named `type` in the schema instead of the more descriptive `account_type`, leading to ambiguity and confusion.

2. **Parameter Mapping**: Schema factories use `account_type` as a parameter but map it to `type` in the schema, creating a disconnect between the API and implementation.

3. **Inconsistent Schema Creation**: Some tests create schemas directly while others use factories, leading to inconsistencies and bugs.

These issues should be addressed as part of the polymorphic model refactoring, ensuring that:

- Field names clearly represent domain concepts
- Parameter names in factories match schema field names
- Schema creation is consistent throughout the codebase

## Alternatives Considered

1. **Extend the current approach**: Continue adding fields to the base Account model and use validation to ensure they're only used with appropriate types. This was rejected due to increasing complexity and poor separation of concerns.

2. **Separate tables for each account type**: Create entirely separate models and tables for each account type without inheritance. This was rejected due to duplication of common fields and logic.

3. **EAV (Entity-Attribute-Value) pattern**: Store type-specific attributes in a separate table. This was rejected due to complexity and performance concerns.
