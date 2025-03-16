# ADR-013: Decimal Precision Handling in Financial Calculations

## Status

Proposed

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

We will implement a comprehensive decimal precision strategy with the following key components:

1. **Multi-tier Precision Model**:
   - **External Boundaries (Input/Output)**: Strictly enforce 2 decimal places
   - **Internal Calculations**: Use 4 decimal places to minimize rounding errors
   - **Storage**: Maintain 4 decimal places in the database to preserve calculation accuracy

2. **Validation Strategy**:
   - Validate all user inputs to ensure they have no more than 2 decimal places
   - Document that internal calculations may work with 4 decimal places
   - Implement explicit rounding at system boundaries

3. **Rounding Policy**:
   - Define consistent rounding methods for specific use cases (e.g., ROUND_HALF_UP for most cases)
   - Add helper utilities to enforce these rounding rules
   - Document where and when rounding occurs

4. **Database Schema Updates**:
   - Update decimal column definitions to support 4 decimal places internally
   - Maintain backward compatibility with existing data

This approach balances the need for accuracy in financial calculations with the practical considerations of financial reporting and user expectations.

## Technical Details

### Implementation Components

1. **BaseDecimalField Class**:
   ```python
   class BaseDecimalField:
       """Base class for decimal field handling with precision control."""
       
       @staticmethod
       def round_for_display(value: Decimal) -> Decimal:
           """Round to 2 decimal places for user display."""
           return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
           
       @staticmethod
       def round_for_calculation(value: Decimal) -> Decimal:
           """Round to 4 decimal places for internal calculations."""
           return value.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
           
       @staticmethod
       def validate_input_precision(value: Decimal) -> bool:
           """Validate that input has no more than 2 decimal places."""
           return value.as_tuple().exponent >= -2
   ```

2. **Database Schema Updates**:
   ```python
   # Old definition
   amount = Column(Numeric(10, 2), nullable=False)
   
   # New definition
   amount = Column(Numeric(12, 4), nullable=False)
   ```

3. **Pydantic Schema Updates**:
   ```python
   class MoneyField(BaseModel):
       """Custom type for money fields with precision control."""
       
       @field_validator("*", mode="before")
       @classmethod
       def validate_input_precision(cls, v: Any) -> Any:
           """Validate that input values have at most 2 decimal places."""
           if isinstance(v, Decimal) and v.as_tuple().exponent < -2:
               raise ValueError("Input values must have at most 2 decimal places")
           return v
   ```

4. **Updated BaseSchemaValidator**:
   ```python
   class BaseSchemaValidator(BaseModel):
       """Base schema validator with both datetime and decimal validation."""
       
       # Existing datetime validation...
       
       @field_validator("*", mode="before")
       @classmethod
       def validate_decimal_precision(cls, value: Any) -> Any:
           """Validates that decimal values don't exceed 2 decimal places at input boundaries."""
           if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
               raise ValueError("Decimal input should have no more than 2 decimal places")
           return value
   ```

5. **Rounding Utilities**:
   ```python
   def round_split_amounts(amounts: List[Decimal], total: Decimal) -> List[Decimal]:
       """
       Round a list of split amounts while ensuring they sum to the expected total.
       Applies the largest remainder method to handle rounding differences.
       
       Args:
           amounts: List of unrounded amounts that should sum to total
           total: The expected sum after rounding
           
       Returns:
           List of amounts rounded to 2 decimal places that sum to total
       """
       # Round each amount to 2 decimal places
       rounded = [amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for amount in amounts]
       
       # Calculate the difference due to rounding
       rounded_sum = sum(rounded)
       remainder = (total - rounded_sum).quantize(Decimal('0.01'))
       
       if remainder == Decimal('0'):
           return rounded
           
       # Distribute the remainder using the largest remainder method
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

### Migration Strategy

1. **Phase 1: Core Utilities**
   - Create the BaseDecimalField utility class
   - Add rounding utilities to a dedicated module
   - Update the BaseSchemaValidator to enforce input validation

2. **Phase 2: Database Schema Updates**
   - Create Alembic migration to update decimal columns
   - Test data migration with sample datasets
   - Update SQLAlchemy model definitions

3. **Phase 3: Service Layer Integration**
   - Update services to use 4-decimal precision for calculations
   - Add explicit rounding at API boundaries
   - Implement specialized rounding for bill splits

4. **Phase 4: Testing and Documentation**
   - Update tests to verify precision behavior
   - Document precision handling in technical documentation
   - Add developer guidelines for working with monetary values

## Consequences

### Positive

- **Improved Calculation Accuracy**: Reduced cumulative rounding errors in multi-step calculations
- **Consistent Behavior**: Clear, documented approach to decimal precision throughout the application
- **Better Split Handling**: More accurate handling of bill splits and allocations
- **Regulatory Compliance**: Better alignment with financial accounting practices
- **Testing Clarity**: Tests will have a clear expectation of precision requirements

### Negative

- **Migration Effort**: Requires updates to database schema, models, and calculation logic
- **Potential Backward Compatibility Issues**: Existing data may need conversion
- **Added Complexity**: More sophisticated handling of precision and rounding
- **Development Overhead**: Developers must understand when to apply rounding

### Neutral

- **Changed Validation Behavior**: Input validation remains strict, but internal calculations have more flexibility
- **Documentation Requirements**: Need to clearly document precision expectations

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

- Initial implementation will be conservative, focusing on core financial fields
- Future work may include more sophisticated rounding strategies for specific use cases
- Consider formal verification of critical financial algorithms

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-03-15 | 1.0 | Cline | Initial draft proposal |
