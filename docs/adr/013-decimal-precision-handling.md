# ADR-013: Decimal Precision Handling in Financial Calculations

## Status

Accepted

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
   - Continue using our current Pydantic schema validators that enforce 2 decimal places for inputs
   - Allow higher precision for internal service layer operations
   - Explicitly round values at API boundaries when returning responses
   
   Example from inventory: Our `validate_amount_precision()` in schemas and `decimal_places=2` in Field definitions will continue to enforce 2 decimal place validation at API/UI boundaries.

3. **Rounding and Remainder Distribution Strategies**:
   - Implement the "Largest Remainder Method" for bill splits and allocations
   - Use consistent `ROUND_HALF_UP` policy for general monetary rounding
   - Add specialized utilities for percentage-based distributions and allocations
   - For splits with fixed totals (e.g., $100 split three ways), use integer division and modulo operations with cents
   - Provide clear, well-documented utilities for each rounding scenario

4. **Database Schema Updates**:
   - Update all 23 identified monetary columns from `Numeric(10, 2)` to `Numeric(12, 4)`
   - Create a single Alembic migration to handle all these changes
   - Document data scaling for existing production values

This approach balances the need for accuracy in financial calculations with the practical considerations of financial reporting and user expectations. The systematic inventory confirms that this change will primarily affect bill splits, percentage-based calculations, and running balance calculations where precision is most critical.

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
               
       @staticmethod
       def validate_sum_equals_total(items: List[Any], total: Decimal, amount_attr: str = 'amount', epsilon: Optional[Decimal] = None) -> bool:
           """
           Validates that a sum of values equals an expected total within a small epsilon.
           
           Args:
               items: List of objects with amount attributes
               total: Expected total
               amount_attr: Name of the attribute containing the amount
               epsilon: Maximum allowed difference (defaults to DecimalPrecision.EPSILON)
               
           Returns:
               bool: True if sum matches total within epsilon, False otherwise
           """
           if not items:
               return total == Decimal('0')
               
           if epsilon is None:
               epsilon = DecimalPrecision.EPSILON
               
           sum_value = sum(getattr(item, amount_attr) for item in items)
           return abs(sum_value - total) <= epsilon
   ```

2. **Database Schema Updates**:
   ```python
   # Old definition
   amount = Column(Numeric(10, 2), nullable=False)
   
   # New definition
   amount = Column(Numeric(12, 4), nullable=False)
   ```

3. **Centralized Schema Validation with BaseSchemaValidator**:
   ```python
   class BaseSchemaValidator(BaseModel):
       """Base schema validator with both datetime and decimal validation."""
       
       # Existing datetime validation...
       
       @classmethod
       def money_field(cls, description: str, **kwargs) -> Field:
           """
           Creates a standard monetary field with 2 decimal places.
           
           Implementing ADR-013, this method standardizes the creation of monetary
           fields with proper decimal precision validation.
           
           Args:
               description: Field description
               **kwargs: Additional Field parameters
               
           Returns:
               Field: Configured Field instance with decimal_places=2
           """
           return Field(
               decimal_places=2,
               description=description,
               **kwargs
           )
       
       @classmethod
       def percentage_field(cls, description: str, **kwargs) -> Field:
           """
           Creates a percentage field with 4 decimal places.
           
           This special case is for percentage fields that require higher precision,
           as specified in ADR-013.
           
           Args:
               description: Field description
               **kwargs: Additional Field parameters
               
           Returns:
               Field: Configured Field instance with decimal_places=4
           """
           return Field(
               decimal_places=4,
               ge=0,
               le=1,
               description=description,
               **kwargs
           )
       
       @field_validator("*", mode="before")
       @classmethod
       def validate_decimal_precision(cls, value: Any) -> Any:
           """Validates that decimal values don't exceed the specified decimal places at API boundaries."""
           if isinstance(value, Decimal):
               # Check if we're in a field validation (field name is available)
               field_name = getattr(cls.validate_decimal_precision, 'field_name', None)
               
               if field_name and field_name in cls.model_fields:
                   field_info = cls.model_fields[field_name]
                   # Check if this field has a custom decimal_places setting
                   if hasattr(field_info, 'json_schema_extra') and field_info.json_schema_extra and 'decimal_places' in field_info.json_schema_extra:
                       decimal_places = field_info.json_schema_extra['decimal_places']
                       if decimal_places != 2:
                           # Special handling for non-standard precision (e.g., 4 decimal places for percentages)
                           if value.as_tuple().exponent < -decimal_places:
                               raise ValueError(f"Value must have at most {decimal_places} decimal places")
                           return value
               
               # Standard case: Use the DecimalPrecision utility to validate input precision (2 decimal places)
               if not DecimalPrecision.validate_input_precision(value):
                   raise ValueError("Decimal input should have no more than 2 decimal places")
           
           return value
   ```

4. **Schema Field Implementation Example**:
   ```python
   # Example of using the standardized fields
   class BalanceDistribution(BaseSchemaValidator):
       """Schema for balance distribution data."""
       account_id: int = Field(
           ...,
           description="ID of the account"
       )
       average_balance: Decimal = BaseSchemaValidator.money_field(
           description="Average account balance"
       )
       percentage_of_total: Decimal = BaseSchemaValidator.percentage_field(
           description="Percentage of total funds across all accounts"
       )
   ```

5. **Additional Specialized Distribution Utilities**:
   ```python
   @staticmethod
   def distribute_by_percentage(total: Decimal, percentages: List[Decimal]) -> List[Decimal]:
       """
       Distribute a total amount according to percentages, ensuring the sum equals the original total.
       
       Args:
           total: Total amount to distribute
           percentages: List of percentages (should sum to 100%)
           
       Returns:
           List of distributed amounts that sum exactly to the total
       """
       # Validate percentages
       percentage_sum = sum(percentages)
       if abs(percentage_sum - Decimal('100')) > Decimal('0.0001'):
           raise ValueError(f"Percentages must sum to 100%, got {percentage_sum}%")
       
       # Calculate amounts with 4 decimal precision
       amounts = [total * (p / Decimal('100')) for p in percentages]
       
       # Round to 2 decimal places for initial allocation
       rounded = [amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for amount in amounts]
       
       # Calculate difference due to rounding
       rounded_sum = sum(rounded)
       remainder = (total - rounded_sum).quantize(Decimal('0.01'))
       
       # Distribute remainder using largest fractional part method
       if remainder != Decimal('0'):
           # Find indices of amounts with the largest fractional parts
           fractional_parts = [(i, (amounts[i] - rounded[i]).copy_abs()) 
                             for i in range(len(amounts))]
           fractional_parts.sort(key=lambda x: x[1], reverse=True)
           
           # Add or subtract cents from amounts with the largest fractional parts
           cents_to_distribute = int(remainder * 100)
           for i in range(abs(cents_to_distribute)):
               idx = fractional_parts[i % len(fractional_parts)][0]
               if cents_to_distribute > 0:
                   rounded[idx] += Decimal('0.01')
               else:
                   rounded[idx] -= Decimal('0.01')
       
       return rounded
   ```

6. **Bill Split Implementation Example**:
   ```python
   def split_bill_amount(total: Decimal, splits: int) -> List[Decimal]:
       """
       Split a bill amount into equal parts, handling rounding appropriately.
       
       Args:
           total: The total bill amount
           splits: Number of ways to split the bill
           
       Returns:
           List of equal split amounts that sum exactly to the original total
       """
       # Calculate with 4 decimal precision for accuracy
       per_split = (total / splits).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
       
       # Create list of equal amounts
       split_amounts = [per_split] * splits
       
       # Round and ensure the sum matches the original total
       return round_split_amounts(split_amounts, total)
   ```

### Implementation Strategy

Our implementation follows a centralized approach to maintain consistency and minimize code duplication:

1. **Phase 1: Core Utilities**
   - Created the `DecimalPrecision` utility module in `src/core/decimal_precision.py`
   - Implemented rounding, validation, and distribution utilities
   - Added utility functions for common operations like sum validation
   - Comprehensive test coverage for all utility functions

2. **Phase 2: BaseSchemaValidator Enhancement**
   - Enhanced `BaseSchemaValidator` in `src/schemas/__init__.py` with:
     - `money_field()` method for standardized 2-decimal monetary fields
     - `percentage_field()` method for standardized 4-decimal percentage fields
     - Enhanced validation that respects field-specific decimal precision
   - Created a unified validation approach that handles both standard and special cases
   
3. **Phase 3: Database Schema Updates**
   - Updated all database models to use `Numeric(12, 4)` for decimal fields
   - Created a simplified database reset approach instead of complex migrations:
     ```python
     # Example migration operation for all monetary fields
     op.alter_column('accounts', 'available_balance', 
                    type_=sa.Numeric(12, 4), 
                    existing_type=sa.Numeric(10, 2))
     
     op.alter_column('liabilities', 'amount', 
                    type_=sa.Numeric(12, 4), 
                    existing_type=sa.Numeric(10, 2))
     
     # ...and so on for all 23 columns identified in the inventory
     ```
   - Test data migration with sample datasets using test fixtures
   - Update SQLAlchemy model definitions to reflect new precision

3. **Phase 3: Service Layer Integration (Week 3)**
   - BillSplitService: Update to use largest remainder method
   - PaymentService: Update payment distribution logic
   - BalanceService: Update calculation methods
   - Add explicit rounding at API response boundaries

4. **Phase 4: Testing and Documentation (Week 4)**
   - Update test assertions to account for new precision rules
   - Add specialized test cases for splitting and distribution logic
   - Document precision handling in technical documentation
   - Create developer guidelines for working with monetary values

## Consequences

### Positive

- **Improved Calculation Accuracy**: Reduced cumulative rounding errors in multi-step calculations
- **Consistent Behavior**: Clear, documented approach to decimal precision throughout the application
- **Better Split Handling**: More accurate handling of bill splits and allocations with guaranteed exact totals
- **Regulatory Compliance**: Better alignment with financial accounting practices
- **Testing Clarity**: Tests will have a clear expectation of precision requirements
- **Avoided Penny Problems**: Solved the "$100 split three ways" problem (33.33 + 33.33 + 33.34 = 100.00)

### Negative

- **Migration Effort**: Requires updates to database schema, models, and calculation logic
- **Potential Backward Compatibility Issues**: Existing data may need conversion
- **Added Complexity**: More sophisticated handling of precision and rounding
- **Development Overhead**: Developers must understand when to apply rounding

### Neutral

- **Changed Validation Behavior**: Input validation remains strict, but internal calculations have more flexibility
- **Documentation Requirements**: Need to clearly document precision expectations
- **Implementation Consistency**: Schema updates require coordinated changes across multiple files

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

## Notes

- Initial implementation focuses on 23 identified monetary fields across 14 model files
- Specialized handling for BillSplit and PaymentSource, which are particularly vulnerable to precision issues
- Future refinements may include percentage-based interest calculations
- Consider formal verification of critical financial algorithms

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
   - BalanceDistribution.percentage_of_total - This field represents calculated percentages where 4 decimal places provide necessary precision (e.g., 0.0123 or 1.23%).

Refer to `/docs/decimal_fields_inventory.md` for the complete inventory of affected fields and their categorization, which now includes all models and schemas with monetary fields.

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-03-15 | 1.0 | Cline | Initial draft proposal |
| 2025-03-16 | 1.1 | Cline | Added systematic inventory results; Refined implementation details; Added specific field listings; Updated migration strategy with timeline |
| 2025-03-16 | 2.0 | Cline | Completed comprehensive inventory of all 187 decimal fields; Updated status to Accepted; Added detailed classification of database vs. schema fields and precision requirements |
| 2025-03-16 | 2.1 | Cline | Implemented centralized approach with enhanced BaseSchemaValidator; Added utility field methods and improved DecimalPrecision core module; Updated implementation strategy to focus on consistency and standardization |
