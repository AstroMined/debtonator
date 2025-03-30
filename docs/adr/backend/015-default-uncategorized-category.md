# 015: Default "Uncategorized" Category Implementation

**Date**: 2025-03-23  
**Status**: Accepted  
**Deciders**: Team  
**References**: [ADR-012](./012-validation-layer-standardization.md), [ADR-014](./014-repository-layer-for-crud-operations.md)

## Context

When creating liabilities (bills) in the application, we needed to determine how to handle category assignment. Requiring users to specify a category during initial data entry creates friction and potentially forces them to make premature categorization decisions.

## Decision

We have implemented a default "Uncategorized" category that:

1. Has a fixed ID (1) defined in a constants file
2. Is automatically created during database initialization
3. Is protected from modification and deletion
4. Is used when no category is explicitly specified for a liability

## Implementation Details

1. **Constants File**: Created `src/constants.py` with:
   ```python
   DEFAULT_CATEGORY_ID = 1
   DEFAULT_CATEGORY_NAME = "Uncategorized"
   DEFAULT_CATEGORY_DESCRIPTION = "Default category for uncategorized items"
   ```

2. **Category Model**: Added a `system` flag to identify protected categories:
   ```python
   system: Mapped[bool] = mapped_column(
       Boolean, 
       default=False, 
       doc="System flag for protected categories that cannot be modified or deleted"
   )
   ```

3. **Category Repository**: Added protection for system categories:
   - Override `update()` and `delete()` methods to prevent modification of system categories
   - Added `get_default_category_id()` method to retrieve the default category ID

4. **Database Initialization**: Modified `init_db.py` to ensure the default category exists

5. **Schema Factory**: Updated the liability schema factory to use the default category ID

## Consequences

### Positive

- Improved user experience - users don't need to categorize items immediately
- No null values in the database, maintaining referential integrity
- Foundation for future ML categorization - the system can suggest categories for items in the "Uncategorized" category
- Protection mechanisms prevent accidental modification or deletion of the default category

### Negative

- Additional complexity in the repository layer
- Need to ensure the default category exists in all environments
- Need to test against the possibility of orphaned records if the default category is somehow removed

### Neutral

- New entries will default to "Uncategorized" rather than requiring explicit selection
- UI will need to indicate which items still need categorization

## Notes

This approach balances data integrity (requiring a valid foreign key) with user experience (not requiring immediate categorization). It also creates a foundation for future machine learning categorization functionality.

## Implementation Note (Added 2025-03-29)

The initial implementation of category hierarchies and relationships introduced circular references in the schema layer, which required using Pydantic's `ForwardRef` and `model_rebuild()` mechanisms. To improve code quality and eliminate these circular dependencies, we refactored to follow a "Reference by ID + Service Composition" pattern:

1. Schema layer now uses ID references instead of embedded objects
2. Service layer composes rich response objects at runtime
3. This maintains all functionality while eliminating circular references
4. The approach better aligns with our architecture principles from ADR-012

This refactoring did not change the core decision about default categories, only improved the implementation approach.
