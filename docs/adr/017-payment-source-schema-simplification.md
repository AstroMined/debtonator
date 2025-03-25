# ADR-017: PaymentSource Schema Simplification

## Status
Proposed

## Context
The PaymentSource model currently has two parallel schema definitions for creation:
- `PaymentSourceCreate`: Requires a payment_id, causing circular dependency issues
- `PaymentSourceCreateNested`: Used within a parent Payment creation, doesn't require payment_id

This dual approach creates several problems:
1. Circular dependencies in schema definitions
2. Confusion in tests and fixtures about which schema to use
3. Technical debt requiring developers to understand both patterns
4. Potential for inconsistent validation across creation paths
5. Test failures when using the wrong schema pattern

We've already implemented an initial solution in the form of `PaymentSourceCreateNested`, but still maintain the original `PaymentSourceCreate` schema, leading to the current technical debt.

## Decision
We will simplify to a single schema approach for PaymentSource creation:

1. Remove the current `PaymentSourceCreate` class that requires payment_id
2. Rename `PaymentSourceCreateNested` to `PaymentSourceCreate`
3. Make `PaymentSourceCreate` the only creation schema for payment sources
4. Modify repositories to handle payment_id assignment at the repository level
5. Update schema factories and tests to use the simplified pattern

This approach recognizes that payment sources are child entities that should always be created in the context of a payment, and the payment_id should be managed by the repository layer rather than required in the schema.

## Consequences

### Positive
- Simpler, more intuitive API for creating payment sources
- Elimination of circular dependencies
- Reduced technical debt
- Clearer parent-child relationship modeling
- Less code to maintain
- More consistent validation

### Negative
- Requires coordinated changes across multiple layers
- Necessitates updates to all tests using payment sources

## Implementation Checklist

### 1. Schema Layer
- [ ] Rename `PaymentSourceCreateNested` to `PaymentSourceCreate`
- [ ] Remove the current `PaymentSourceCreate` schema
- [ ] Update documentation to explain the parent-child relationship
- [ ] Update schema validation to reflect the simplified approach
- [ ] Ensure schema unit tests pass after changes

### 2. Schema Factory Layer
- [ ] Remove `create_payment_source_schema` function
- [ ] Rename `create_payment_source_nested_schema` to `create_payment_source_schema`
- [ ] Remove payment_id requirement from the factory
- [ ] Update documentation and examples
- [ ] Verify schema factory tests

### 3. Repository Layer
- [ ] Modify `PaymentSourceRepository.create()` to handle payment_id assignment
- [ ] Update `PaymentSourceRepository.bulk_create_sources()` for the new schema
- [ ] Ensure `PaymentRepository` properly manages the parent-child relationship
- [ ] Add documentation explaining the relationship management
- [ ] Run repository tests to verify changes

### 4. Test Layer
- [ ] Update all test fixtures using payment sources
- [ ] Fix any remaining repository integration tests
- [ ] Update any service tests that interact with payment sources
- [ ] Ensure validation tests properly test the constraints
- [ ] Run full test suite to verify all changes

## Work Already Completed

The groundwork for this refactoring has already been laid:

1. Created `PaymentSourceCreateNested` schema that doesn't require payment_id
2. Updated `PaymentCreate` schema to use the nested schema
3. Created schema factories for both approaches
4. Fixed tests to use the appropriate schemas in most places
5. Implemented repository methods that can work with both approaches
6. Fixed immediate test failures caused by schema validation errors

This ADR builds on these changes to fully resolve the technical debt by completing the migration to a single schema approach.
