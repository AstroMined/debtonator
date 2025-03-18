# ADR-013 Update: Decimal Precision Handling with Pydantic V2 Compatibility

## Status

Implemented (Revised)

## Context

Our financial application handles monetary values throughout its codebase, from user inputs to complex calculations and final outputs. We've encountered several challenges with decimal precision:

1. **Validation Inconsistencies**: Tests expect validation errors for values with more than 2 decimal places, but some internal calculations naturally produce results with higher precision.

2. **Rounding Errors**: When performing operations like splitting bills, dividing amounts, or calculating percentages, standard 2-decimal precision can lead to rounding errors that accumulate across multiple calculations.

3. **Data Model Constraints**: Our current database schema and Pydantic models enforce 2-decimal places for monetary values, which may be insufficient for internal calculations.

4. **Test Expectations**: Our test suite expects specific behavior (validation failures for >2 decimal places) that conflicts with allowing higher internal precision.

The financial industry typically follows certain practices regarding decimal precision:
- Displaying monetary values with 2 decimal places in user interfaces
- Storing 2 decimal places for official records and financial statements
- Using higher precision (4-6 decimal places) for internal calculations to minimize rounding errors
- Implementing specific rounding strategies at boundary points (e.g., when finalizing transactions)

## Decision

Based on a systematic review of all decimal fields in the codebase (documented in `/docs/decimal_fields_inventory.md`), which identified 187 decimal fields across 37 schema files and 16 model files, we will implement a comprehensive decimal precision strategy with the following key components:

1. **Two-Tier Precision Model**:
   - **UI/API Boundary Fields**: Strictly enforce 2 decimal places for all user inputs and outputs
   - **Database Storage and Calculations**: Use 4 decimal places for all monetary values to maintain precision
     
   This approach clearly separates presentation precision (what users see) from calculation precision (what the system uses internally).

2. **Validation Strategy**:
   - Use Pydantic V2's Annotated types with Field constraints to enforce 2 decimal places for monetary inputs 
   - Allow higher precision for internal service layer operations
   - Explicitly round values at API boundaries when returning responses

3. **Rounding and Remainder Distribution Strategies**:
   - Implement the "Largest Remainder Method" for bill splits and allocations
   - Use consistent `ROUND_HALF_UP` policy for general monetary rounding
   - Add specialized utilities for percentage-based distributions and allocations
   - For splits with fixed totals (e.g., $100 split three ways), use integer division and modulo operations with cents
   - Provide clear, well-documented utilities for each rounding scenario

4. **Database Schema Updates**:
   - Update all 23 identified monetary columns from `Numeric(10, 2)` to `Numeric(12, 4)`
   - Document data scaling for existing production values

This approach balances the need for accuracy in financial calculations with the practical considerations of financial reporting and user expectations. The systematic inventory confirms that this change will primarily affect bill splits, percentage-based calculations, and running balance calculations where precision is most critical.

## Implementation Revision

**Critical Update (3/18/2025)**: Our initial implementation approach used Pydantic's `ConstrainedDecimal` class, which has been completely removed in Pydantic V2. We have revised our implementation to use Pydantic V2's recommended pattern with Annotated types, which maintains the same validation goals while being compatible with Pydantic V2.

The revised implementation is documented in detail in:
- `docs/adr/compliance/adr013_implementation_checklist_v2.md` (revised implementation plan)
- `docs/adr/compliance/annotated_types_reference.py` (reference implementation)

## Technical Details

### Implementation Components

1. **DecimalPrecision Utility Module** (no changes from original ADR):
   ```python
   from decimal import Decimal, ROUND_HALF_UP
   from typing import List, Union, Optional, Any
   
   class DecimalPrecision:
       """Utility class for handling decimal precision in financial calculations."""
       
       # Precision constants
       DISPLAY_PRECISION = Decimal('0.01')  # 2 decimal places
       CALCULATION_PRECISION = Decimal('0.0001')  # 4 decimal places
       
       # Epsilon for comparing decimal equality in financial calculations
       EPSILON = Decimal('0.01')
       
       @staticmethod
       def round_for_display(value: Decimal) -> Decimal:
           """Round to 2 decimal places for user display."""
           return value.quantize(DecimalPrecision.DISPLAY_PRECISION, rounding=ROUND_HALF_UP)
           
       @staticmethod
       def round_for_calculation(value: Decimal) -> Decimal:
           """Round to 4 decimal places for internal calculations."""
           return value.quantize(DecimalPrecision.CALCULATION_PRECISION, rounding=ROUND_HALF_UP)
           
       @staticmethod
       def validate_input_precision(value: Decimal) -> bool:
           """Validate that input has no more than 2 decimal places."""
           return value.as_tuple().exponent >= -2
           
       @staticmethod
       def distribute_with_largest_remainder(total: Decimal, parts: int) -> List[Decimal]:
           """
           Distribute a total amount into equal parts without losing cents.
           
           Args:
               total: Total amount to distribute
               parts: Number of parts to distribute into
               
           Returns:
               List of distributed amounts that sum exactly to the total
           """
           # Step 1: Calculate base amount (integer division)
           cents = int(total * 100)
           base_cents = cents // parts
           
           # Step 2: Calculate remainder
           remainder_cents = cents - (base_cents * parts)
           
           # Step 3: Distribute base amounts
           result = [Decimal(base_cents) / 100] * parts
           
           # Step 4: Distribute remainder one cent at a time
           for i in range(remainder_cents):
               result[i] += Decimal('0.01')
               
           return result
       
       # Other utility methods remain unchanged...
   ```

2. **Database Schema Updates** (no changes from original ADR):
   ```python
   # Old definition
   amount = Column(Numeric(10, 2), nullable=False)
   
   # New definition
   amount = Column(Numeric(12, 4), nullable=False)
   ```

3. **Pydantic V2 Annotated Types** (revised approach):
   ```python
   from typing import Annotated, Dict
   from decimal import Decimal
   from pydantic import BaseModel, Field, model_validator
   
   # 2 decimal places for monetary values
   MoneyDecimal = Annotated[
       Decimal,
       Field(multiple_of=Decimal("0.01"), description="Monetary value with 2 decimal places")
   ]
   
   # 4 decimal places for percentage values (0-1 range)
   PercentageDecimal = Annotated[
       Decimal,
       Field(ge=0, le=1, multiple_of=Decimal("0.0001"), description="Percentage value with 4 decimal places (0-1 range)")
   ]
   
   # 4 decimal places for correlation values (-1 to 1 range)
   CorrelationDecimal = Annotated[
       Decimal,
       Field(ge=-1, le=1, multiple_of=Decimal("0.0001"), description="Correlation value with 4 decimal places (-1 to 1 range)")
   ]
   
   # 4 decimal places for general ratio values (no min/max constraints)
   RatioDecimal = Annotated[
       Decimal,
       Field(multiple_of=Decimal("0.0001"), description="Ratio value with 4 decimal places")
   ]
   
   # Dictionary type aliases
   MoneyDict = Dict[str, MoneyDecimal]
   PercentageDict = Dict[str, PercentageDecimal]
   IntMoneyDict = Dict[int, MoneyDecimal]
   IntPercentageDict = Dict[int, PercentageDecimal]
   ```

4. **Schema Implementation with Annotated Types** (revised approach):
   ```python
   # Example schema class using Annotated types
   class BalanceDistribution(BaseSchemaValidator):
       """Schema for balance distribution data."""
       account_id: int = Field(description="ID of the account")
       average_balance: MoneyDecimal = Field(description="Average account balance")
       percentage_of_total: PercentageDecimal = Field(description="Percentage of total funds across all accounts")
   ```

5. **Dictionary Validation** (new in the revised approach):
   ```python
   class BaseSchemaValidator(BaseModel):
       """Base schema validator with UTC timezone and decimal validation."""
       
       # Existing model configuration...
       
       @model_validator(mode='after')
       def validate_decimal_dictionaries(self) -> 'BaseSchemaValidator':
           """Validate all dictionary fields with decimal values for proper precision."""
           for field_name, field_value in self.__dict__.items():
               # Skip non-dictionary fields
               if not isinstance(field_value, dict):
                   continue
                   
               field_info = self.model_fields.get(field_name)
               if not field_info or not hasattr(field_info, 'annotation'):
                   continue
                   
               # Check dictionary field types
               annotation = field_info.annotation
               
               # Handle MoneyDict fields
               if annotation == MoneyDict or annotation == IntMoneyDict:
                   for key, value in field_value.items():
                       if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
                           raise ValueError(f"Dictionary value for key '{key}' should have no more than 2 decimal places")
               
               # Handle PercentageDict fields
               elif annotation == PercentageDict or annotation == IntPercentageDict:
                   for key, value in field_value.items():
                       if isinstance(value, Decimal):
                           # Check decimal places
                           if value.as_tuple().exponent < -4:
                               raise ValueError(f"Dictionary value for key '{key}' should have no more than 4 decimal places")
                           # Check range
                           if value < 0 or value > 1:
                               raise ValueError(f"Percentage value for key '{key}' must be between 0 and 1")
           return self
       
       # Other validators remain unchanged...
   ```

### Implementation Strategy (Revised)

Our implementation follows a phased approach detailed in `docs/adr/compliance/adr013_implementation_checklist_v2.md`:

1. **Phase 1: Core Type Definitions**
   - Update `src/schemas/__init__.py` with Annotated type definitions
   - Remove utility methods in favor of direct type annotations
   - Add dictionary type definitions
   - Update documentation and examples

2. **Phase 2: Dictionary Validation Strategy**
   - Implement dictionary validation for decimal precision
   - Add model validators to BaseSchemaValidator
   - Create specialized dictionary types if needed

3. **Phase 3: Schema Updates**
   - Update all 22 schema files to use the new Annotated types
   - Replace utility method calls with direct type annotations
   - Fix any validation issues

4. **Phase 4: Test Updates**
   - Update all schema tests to reflect new validation behavior
   - Add dictionary validation tests
   - Update error message expectations

5. **Phase 5-8: Service Tests, Documentation Updates, etc.**
   - Remaining phases align with the original plan but with updated approaches

## Consequences

### Positive

- **Pydantic V2 Compatibility**: Implementation works with the latest Pydantic version
- **Type Safety**: Provides distinct types that carry their validation rules with them
- **Cleaner Schema Code**: Field constraints are declared alongside the field definition
- **Simpler Mental Model**: Direct type annotations are easier to understand than utility methods
- **Better IDE Integration**: Improved type hints for better IDE support
- All positive consequences from the original ADR remain valid

### Negative

- **Migration Effort**: Requires updates to all schema files
- **Testing Updates**: Tests need to be updated for new error messages
- **Dictionary Validation Complexity**: Dictionary validation requires special handling
- All negative consequences from the original ADR remain valid

### Neutral

- **Changed Implementation Approach**: Using Annotated types rather than custom validators
- **Documentation Updates**: Need to clearly document the new approach

## Benefits of the New Approach

1. **Simplicity**: Leverages Pydantic's built-in validation rather than creating a parallel system
2. **Type Safety**: Provides distinct types that carry their validation rules with them
3. **Cleaner Schema Code**: Field constraints are declared alongside the field definition
4. **Simpler Mental Model**: Direct type annotations are easier to understand than utility methods
5. **Better IDE Integration**: Improved type hints for better IDE support
6. **Future-Proof**: Aligned with Pydantic's design direction

## Affected Fields

The affected fields remain the same as in the original ADR. All monetary fields in the database will use 4 decimal places, while API boundaries will enforce 2 decimal places with one exception (BalanceDistribution.percentage_of_total which requires 4 decimal places).

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-03-15 | 1.0 | Cline | Initial draft proposal |
| 2025-03-16 | 1.1 | Cline | Added systematic inventory results; Refined implementation details; Added specific field listings; Updated migration strategy with timeline |
| 2025-03-16 | 2.0 | Cline | Completed comprehensive inventory of all 187 decimal fields; Updated status to Accepted; Added detailed classification of database vs. schema fields and precision requirements |
| 2025-03-16 | 2.1 | Cline | Implemented centralized approach with enhanced BaseSchemaValidator; Added utility field methods and improved DecimalPrecision core module; Updated implementation strategy to focus on consistency and standardization |
| 2025-03-18 | 3.0 | Cline | Completely revised implementation approach to use Pydantic V2's Annotated types instead of ConstrainedDecimal which was removed in Pydantic V2; Added dictionary validation strategy; Updated sample code and implementation plan |
