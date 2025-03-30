# ADR-017: PaymentSource Schema Simplification

## Status
Implemented (Partial) - March 28, 2025

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

### 1. Schema Layer Changes

- [x] Examine current schema structure and dependencies
- [x] Rename `PaymentSourceCreateNested` to `PaymentSourceCreate`
- [x] Remove the current `PaymentSourceCreate` schema class
- [x] Update `PaymentSourceBase` to remove required `payment_id` field
- [x] Modify `PaymentSourceBase` documentation to reflect new parent-child relationship
- [x] Update validation logic to work without requiring payment_id at schema level
- [x] Ensure `PaymentUpdate` uses the simplified schema for its sources

### 2. Schema Factory Layer Changes

- [x] Locate and examine schema factory functions for payment sources
- [x] Remove `create_payment_source_schema` function that required payment_id
- [x] Update factory function to handle payment_id assignment at repository layer
- [x] Update documentation and examples in factory functions
- [x] Add clear comments explaining the relationship management

### 3. Repository Layer Changes

- [x] Modify `PaymentSourceRepository.create()` to handle payment_id assignment
- [x] Update `PaymentSourceRepository.bulk_create_sources()` for the new schema
- [x] Ensure `PaymentRepository.create()` properly manages the parent-child relationship
- [x] Add documentation explaining the relationship management in repository methods
- [x] Update any repository method docstrings to reflect the schema changes

### 4. Test Layer Updates

- [x] Update `test_payment_source_base_validation` to validate without payment_id
- [x] Update `test_payment_update_validation` for the new schema approach
- [x] Identify and update any test fixtures using payment sources
- [x] Fix repository integration tests that rely on the old schema structure
- [ ] Update any service tests that interact with payment sources
- [x] Ensure validation tests properly test the constraints

### 5. Additional Areas to Review

- [ ] Check for any service layer dependencies on the old schema structure
- [ ] Verify API endpoints that create or update payment sources
- [ ] Review any custom validators that might rely on payment_id
- [ ] Check for any references to the old schema in documentation
- [x] Update the status of ADR-017 from "Proposed" to "Accepted"

### 6. Final Verification

- [x] Run unit tests to verify schema changes
- [x] Run integration tests to verify repository changes 
- [x] Perform a final review of all changes for consistency
- [x] Verify that all items in the ADR-017 checklist are completed

## Work Already Completed

The groundwork for this refactoring has already been laid:

1. Created `PaymentSourceCreateNested` schema that doesn't require payment_id
2. Updated `PaymentCreate` schema to use the nested schema
3. Created schema factories for both approaches
4. Fixed tests to use the appropriate schemas in most places
5. Implemented repository methods that can work with both approaches
6. Fixed immediate test failures caused by schema validation errors

This ADR builds on these changes to fully resolve the technical debt by completing the migration to a single schema approach.

## Future Considerations

The following items should be addressed in future sessions to complete the implementation of ADR-017:

1. **PaymentRepository.update()**: 
   - Update the method to properly handle adding/updating payment sources while maintaining the relationship constraints
   - Ensure sources can be added/removed/modified without breaking the rule that a payment must have at least one source

2. **Documentation Improvements**: 
   - Add more explicit documentation at the class level for both repositories that clearly explains the parent-child relationship pattern
   - Add code examples to documentation showing the proper way to create and update payments with sources

3. **ORM Configuration Review**:
   - Verify that the SQLAlchemy cascade rules are properly set to automatically delete sources when a payment is deleted
   - Ensure model relationships are optimally configured for the parent-child pattern

4. **Test Coverage**:
   - Scan the codebase for any remaining tests still using the old pattern
   - Add tests specifically for edge cases around payment source relationships
   - Ensure the "payment must have at least one source" rule is properly tested

5. **Service Layer Updates**:
   - Review and update service methods that create or update payment sources
   - Ensure they follow the new pattern where sources are created only through payments
