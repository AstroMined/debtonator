<!-- markdownlint-disable MD029 -->
# ADR-013: Decimal Precision Handling

## Status

Implemented

## Executive Summary

This ADR establishes a comprehensive two-tier precision model for financial calculations throughout the Debtonator platform that balances accuracy with usability. By using 4 decimal places for database storage and internal calculations while enforcing 2 decimal places at UI/API boundaries, the system prevents cumulative rounding errors while maintaining familiar financial presentation formats. The implementation leverages Pydantic V2's Annotated types with Field constraints to create specialized decimal types (MoneyDecimal, PercentageDecimal) that encapsulate validation rules, includes robust handling for decimal dictionaries, and implements specialized distribution algorithms to solve common financial calculation challenges like the "$100 split three ways" problem. This standardized approach, fully implemented across all 187 identified decimal fields in the system, ensures consistent decimal handling throughout the application with minimal performance impact.

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

## Evolution from Original Implementation

Our original implementation approach used Pydantic's `ConstrainedDecimal` class, which was completely removed in Pydantic V2. We revised our implementation to use Pydantic V2's recommended pattern with Annotated types, which maintains the same validation goals while being compatible with Pydantic V2.

### Pydantic V2 Compatibility

Pydantic V2 represents a significant evolution from V1, introducing breaking changes that affect our decimal validation strategy. Key changes affecting our implementation:

1. **Removal of Constrained Types**: Pydantic V2 removed the entire `ConstrainedX` class family, including `ConstrainedDecimal` that our original implementation relied on.

2. **New Annotated Types Pattern**: Pydantic V2 recommends using Python's `typing.Annotated` with `Field` constraints for validation, offering a more integrated approach with Python's type system.

3. **Validator Changes**: The validator decorators changed from `@validator` to `@field_validator` and `@model_validator` with different behavior and syntax.

4. **Error Message Changes**: Validation error messages follow a new pattern, using "Input should be a multiple of X" instead of "Decimal input should have no more than X decimal places".

### Revised Validation Strategy

Our revised implementation centers on clearly defined Annotated types that encapsulate their validation rules:

```python
# 2 decimal places for monetary values (e.g., $100.00)
MoneyDecimal = Annotated[
    Decimal,
    Field(multiple_of=Decimal("0.01"), description="Monetary value with 2 decimal places")
]

# 4 decimal places for percentage values (0-1 range, e.g., 0.1234 = 12.34%)
PercentageDecimal = Annotated[
    Decimal,
    Field(ge=0, le=1, multiple_of=Decimal("0.0001"), 
          description="Percentage value with 4 decimal places (0-1 range)")
]

# 4 decimal places for correlation values (-1 to 1 range)
CorrelationDecimal = Annotated[
    Decimal,
    Field(ge=-1, le=1, multiple_of=Decimal("0.0001"), 
          description="Correlation value with 4 decimal places (-1 to 1 range)")
]
```

This approach creates specialized decimal types that:

- Carry their validation rules with them
- Provide clear documentation through type hints
- Enforce consistent validation across the codebase
- Can be imported and used directly in schema definitions

### Dictionary Validation Strategy

Our implementation includes specialized handling for dictionaries containing decimal values, a common pattern in financial data structures. Dictionaries present unique validation challenges because:

1. Simple type aliases like `MoneyDict = Dict[str, MoneyDecimal]` don't automatically validate each value in the dictionary.

2. Nested dictionaries may contain decimal values at different levels.

3. In-place modifications to dictionaries could bypass validation.

Our solution implements a thorough validation strategy:

1. **Dictionary Type Aliases**: Clear type aliases for common dictionary patterns.

  ```python
  MoneyDict = Dict[str, MoneyDecimal]
  PercentageDict = Dict[str, PercentageDecimal]
  IntMoneyDict = Dict[int, MoneyDecimal]
  ```

2. **Model-level Validation**: A `validate_decimal_dictionaries` validator that checks all dictionary fields after model construction, enforcing proper precision for each value based on the field's annotation.

3. **Custom Dictionary Classes**: For advanced use cases, validated dictionary classes that enforce precision constraints when values are set or modified.

This comprehensive approach ensures consistent decimal validation throughout our codebase, including within complex nested data structures.

## Technical Details

### Implementation Components

1. **DecimalPrecision Utility Module**:

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

2. **Database Schema Updates**:

   ```python
   # Old definition
   amount = Column(Numeric(10, 2), nullable=False)
   
   # New definition
   amount = Column(Numeric(12, 4), nullable=False)
   ```

3. **Pydantic V2 Annotated Types**:

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

4. **Schema Implementation with Annotated Types**:

   ```python
   # Example schema class using Annotated types
   class BalanceDistribution(BaseSchemaValidator):
       """Schema for balance distribution data."""
       account_id: int = Field(description="ID of the account")
       average_balance: MoneyDecimal = Field(description="Average account balance")
       percentage_of_total: PercentageDecimal = Field(description="Percentage of total funds across all accounts")
   ```

5. **Dictionary Validation**:

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

### Implementation Strategy

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

5. **Phase 5: Service Tests**
   - Update service tests to handle the new precision model
   - Implement tests for the "$100 split three ways" scenario
   - Test largest remainder method for distribution

6. **Phase 6: API Response Formatting**
   - Implement response formatter middleware
   - Add @with_formatted_response decorator
   - Create get_decimal_formatter() dependency

7. **Phase 7: Documentation**
   - Update developer documentation for decimal handling
   - Create examples for common scenarios
   - Document dictionary validation approach

8. **Phase 8: Quality Assurance**
   - Conduct comprehensive testing
   - Verify all money-related features
   - Complete final documentation review

## Consequences

### Positive

- **Pydantic V2 Compatibility**: Implementation works with the latest Pydantic version
- **Type Safety**: Provides distinct types that carry their validation rules with them
- **Cleaner Schema Code**: Field constraints are declared alongside the field definition
- **Simpler Mental Model**: Direct type annotations are easier to understand than utility methods
- **Better IDE Integration**: Improved type hints for better IDE support
- **Improved Calculation Accuracy**: Reduced cumulative rounding errors in multi-step calculations
- **Consistent Behavior**: Clear, documented approach to decimal precision throughout the application
- **Better Split Handling**: More accurate handling of bill splits and allocations with guaranteed exact totals
- **Regulatory Compliance**: Better alignment with financial accounting practices
- **Testing Clarity**: Tests have a clear expectation of precision requirements
- **Avoided Penny Problems**: Solved the "$100 split three ways" problem (33.33 + 33.33 + 33.34 = 100.00)

### Negative

- **Migration Effort**: Requires updates to all schema files
- **Testing Updates**: Tests need to be updated for new error messages
- **Dictionary Validation Complexity**: Dictionary validation requires special handling
- **Potential Backward Compatibility Issues**: Existing data may need conversion
- **Added Complexity**: More sophisticated handling of precision and rounding
- **Development Overhead**: Developers must understand when to apply rounding

### Neutral

- **Changed Implementation Approach**: Using Annotated types rather than custom validators
- **Documentation Updates**: Need to clearly document the new approach
- **Changed Validation Behavior**: Input validation remains strict, but internal calculations have more flexibility
- **Implementation Consistency**: Schema updates require coordinated changes across multiple files

## Benefits of the New Approach

1. **Simplicity**: Leverages Pydantic's built-in validation rather than creating a parallel system
2. **Type Safety**: Provides distinct types that carry their validation rules with them
3. **Cleaner Schema Code**: Field constraints are declared alongside the field definition
4. **Simpler Mental Model**: Direct type annotations are easier to understand than utility methods
5. **Better IDE Integration**: Improved type hints for better IDE support
6. **Future-Proof**: Aligned with Pydantic's design direction
7. **Self-Documenting**: Type definitions clearly express validation intent and constraints
8. **Consistent Validation**: Enforces the same validation behavior across all schema files
9. **Reduced Boilerplate**: Eliminates repeated validation code across schema definitions
10. **Explicit Precision Rules**: Makes the two-tier precision model (2 vs 4 decimal places) explicit in the type system

### Usage Examples

#### Basic Schema Definition

```python
class PaymentCreate(BaseSchemaValidator):
    """Schema for creating a new payment."""
    
    payment_date: datetime
    amount: MoneyDecimal = Field(description="Payment amount in dollars") 
    description: str | None = None
    
    # Percentage field with 4 decimal places (0-1 range)
    confidence_score: PercentageDecimal = Field(default=0.95)
```

#### Dictionary Fields

```python
class AccountAnalysis(BaseSchemaValidator):
    """Schema for account analysis results."""
    
    account_id: int
    
    # Dictionary of category distributions (percentage per category)
    category_distribution: PercentageDict = Field(
        description="Distribution of spending across categories"
    )
    
    # Dictionary of daily balances (date string -> balance)
    daily_balances: MoneyDict = Field(
        description="Account balance on each day"
    )
```

#### Complex Schema with Mixed Precision

```python
class FinancialAnalysisResult(BaseSchemaValidator):
    """Schema for financial analysis results."""
    
    # 2 decimal places for monetary values
    total_assets: MoneyDecimal
    total_liabilities: MoneyDecimal
    net_worth: MoneyDecimal
    
    # 4 decimal places for percentages (0-1 range)
    debt_to_income_ratio: PercentageDecimal
    savings_rate: PercentageDecimal
    
    # 4 decimal places for correlations (-1 to 1 range)
    income_spending_correlation: CorrelationDecimal
    
    # Dictionary of monetary values by account
    account_balances: IntMoneyDict
    
    # Dictionary of percentage values by category
    category_allocations: PercentageDict
```

## Performance Impact

- **Database Storage**: Slight increase in storage requirements for decimal fields
- **Calculation Speed**: Negligible impact on performance from using 4 decimal places
- **Memory Usage**: Minor increase in memory usage for in-flight calculations

## Compliance & Security

- **Improved Accuracy**: Enhanced precision supports better audit compliance
- **Financial Regulations**: Better alignment with standard accounting practices
- **Error Reduction**: Minimized rounding errors reduce discrepancies in financial reporting
- **No Security Impact**: This change does not directly affect security posture

## Dependencies

- Python `decimal` module with proper rounding modes
- SQLAlchemy and database support for 4-decimal precision
- Pydantic 2.x with field validation support
- Alembic for database migrations

## Monitoring & Success Metrics

- **Reduction in Rounding Issues**: Track and measure reduction in rounding-related discrepancies
- **Test Reliability**: Monitor stability of financial calculation tests
- **Split Accuracy**: Verify that bill splits and allocations consistently sum to expected totals
- **Developer Adoption**: Track consistent use of new decimal handling utilities

## Team Impact

- **Training Needed**: Developers need to understand the precision model and when to apply rounding
- **Code Review Updates**: Add decimal precision handling to code review checklist
- **Documentation**: Update coding standards and onboarding materials
- **Testing Guidelines**: Provide clear guidance on testing financial calculations

## Related Documents

- ADR-011: Datetime Standardization
- ADR-012: Validation Layer Standardization
- Financial calculation best practices documentation

## Affected Fields

Based on our comprehensive inventory analysis, the following classification of fields emerged:

1. **Database Models (37 fields)**: All database models with monetary fields should use `Numeric(12, 4)` to support intermediate calculations with higher precision. Key examples include:
   - BillSplit.amount - Critical for splitting calculations and remainder distribution
   - PaymentSource.amount - Used in payment distribution
   - Account balances - Running totals requiring precision to prevent accumulation errors
   - Transaction amounts - Used in multi-step calculations

2. **Pydantic Schemas (150 fields)**: All Pydantic schemas with monetary fields at the API/UI boundary should enforce 2 decimal places. This ensures that:
   - User inputs are validated consistently
   - API responses show the standard 2 decimal places
   - The system presents a consistent financial interface

Of particular note, we identified only one field that requires 4 decimal places at the API boundary:

- `BalanceDistribution.percentage_of_total` - This field represents calculated percentages where 4 decimal places provide necessary precision (e.g., 0.0123 or 1.23%).

Refer to `/docs/decimal_fields_inventory.md` for the complete inventory of affected fields and their categorization, which now includes all models and schemas with monetary fields.

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-03-15 | 1.0 | Cline | Initial draft proposal |
| 2025-03-16 | 1.1 | Cline | Added systematic inventory results; Refined implementation details; Added specific field listings; Updated migration strategy with timeline |
| 2025-03-16 | 2.0 | Cline | Completed comprehensive inventory of all 187 decimal fields; Updated status to Accepted; Added detailed classification of database vs. schema fields and precision requirements |
| 2025-03-16 | 2.1 | Cline | Implemented centralized approach with enhanced BaseSchemaValidator; Added utility field methods and improved DecimalPrecision core module; Updated implementation strategy to focus on consistency and standardization |
| 2025-03-18 | 3.0 | Cline | Completely revised implementation approach to use Pydantic V2's Annotated types instead of ConstrainedDecimal which was removed in Pydantic V2; Added dictionary validation strategy; Updated sample code and implementation plan |
| 2025-03-19 | 3.1 | Cline | Enhanced documentation with comprehensive Pydantic V2 compatibility section; Expanded dictionary validation strategy details; Added usage examples for Annotated types; Updated benefits section |
| 2025-03-29 | 4.0 | Cline | Consolidated decimal precision handling documents into a single unified ADR; Updated status to "Implemented"; Maintained complete version history; Enhanced structure for better readability |
