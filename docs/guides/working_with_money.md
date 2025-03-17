# Working with Money and Decimal Precision in Debtonator

This guide outlines how to properly handle monetary values and decimal precision in the Debtonator application, following the guidelines established in ADR-013.

## Core Principles

1. **Two-Tier Precision Model**:
   - **API/UI Boundaries**: 2 decimal places for all user inputs and outputs
   - **Internal Calculations**: 4 decimal places for accuracy
   - **Percentage Fields**: 4 decimal places for greater precision

2. **Decimal Type**:
   - Always use `Decimal` from Python's `decimal` module, never `float`
   - Always initialize with string literals: `Decimal('10.25')` not `Decimal(10.25)`
   - Use `ROUND_HALF_UP` for consistent rounding behavior

3. **Field Definitions**:
   - Use `BaseSchemaValidator.money_field()` for monetary values
   - Use `BaseSchemaValidator.percentage_field()` for percentage values

## Using the DecimalPrecision Core Module

The `src.core.decimal_precision` module provides all the utilities needed for handling decimal precision:

```python
from decimal import Decimal
from src.core.decimal_precision import DecimalPrecision

# Round for display (2 decimal places)
amount = Decimal('10.23456')
display_amount = DecimalPrecision.round_for_display(amount)  # 10.23

# Round for internal calculations (4 decimal places) 
calc_amount = DecimalPrecision.round_for_calculation(amount)  # 10.2346

# Validate proper precision for API input
is_valid = DecimalPrecision.validate_input_precision(Decimal('10.25'))  # True
is_valid = DecimalPrecision.validate_input_precision(Decimal('10.256'))  # False

# Distribute total among equal parts
splits = DecimalPrecision.distribute_with_largest_remainder(
    Decimal('100'), 3
)  # [33.34, 33.33, 33.33]

# Distribute by percentage
amounts = DecimalPrecision.distribute_by_percentage(
    Decimal('100'),
    [Decimal('25'), Decimal('45'), Decimal('30')]
)  # [25.00, 45.00, 30.00]

# Split bill equally
equal_splits = DecimalPrecision.split_bill_amount(
    Decimal('100'), 3
)  # [33.34, 33.33, 33.33]

# Validate sum equals total
sources = [
    source1,  # object with amount=Decimal('33.34')
    source2,  # object with amount=Decimal('33.33')
    source3   # object with amount=Decimal('33.33')
]
is_valid = DecimalPrecision.validate_sum_equals_total(
    sources, Decimal('100')
)  # True
```

## Schema Field Definitions

Always use the standardized field methods when defining monetary or percentage fields:

```python
from decimal import Decimal
from pydantic import Field
from src.schemas import BaseSchemaValidator

class PaymentSchema(BaseSchemaValidator):
    # Monetary field (2 decimal places)
    amount: Decimal = BaseSchemaValidator.money_field(
        "Payment amount in dollars",
        ...,  # Required field (can also be None, etc.)
        ge=Decimal('0')  # Must be greater than or equal to 0
    )
    
    # Percentage field (4 decimal places)
    confidence_score: Decimal = BaseSchemaValidator.percentage_field(
        "Confidence score (0-1 scale)",
        default=Decimal('1')  # Default value
    )
```

## API Response Formatting

The application provides multiple ways to ensure proper decimal formatting in API responses:

### 1. Global Middleware (Automatic for All Endpoints)

All JSON responses are automatically processed by the decimal precision middleware, which correctly formats decimal values based on their context.

### 2. Decorator Approach (For Individual Endpoints)

```python
from src.api.response_formatter import with_formatted_response

@router.get("/endpoint")
@with_formatted_response
async def my_endpoint():
    return {"amount": Decimal('10.23456')}  # Will be formatted to "10.23"
```

### 3. Dependency Approach (For Manual Formatting)

```python
from src.api.base import get_decimal_formatter

@router.get("/endpoint")
async def my_endpoint(formatter = Depends(get_decimal_formatter)):
    data = {"amount": Decimal('10.23456')}
    return formatter(data)  # Will be formatted to {"amount": "10.23"}
```

## Service Layer Calculations

Follow these guidelines for decimal handling in service layer calculations:

1. Use 4 decimal places for all internal calculations:
```python
amount1 = DecimalPrecision.round_for_calculation(Decimal('10.2345'))  # 10.2345
amount2 = DecimalPrecision.round_for_calculation(Decimal('5.6789'))   # 5.6789
total = DecimalPrecision.round_for_calculation(amount1 + amount2)     # 15.9134
```

2. Only round to 2 decimal places at API boundaries, not during calculations:
```python
# Wrong
amount1 = DecimalPrecision.round_for_display(Decimal('10.2345'))  # 10.23
amount2 = DecimalPrecision.round_for_display(Decimal('5.6789'))   # 5.68
total = amount1 + amount2                                 # 15.91 (lost precision)

# Right
amount1 = Decimal('10.2345')
amount2 = Decimal('5.6789')
total = amount1 + amount2                                # 15.9134 (full precision)
display_total = DecimalPrecision.round_for_display(total)  # 15.91 (for display only)
```

## Testing Best Practices

When testing financial calculations:

1. Test exact equality with Decimal:
```python
from decimal import Decimal
import pytest

def test_calculate_total():
    # Exact comparison with Decimal
    expected = Decimal('15.91')
    result = DecimalPrecision.round_for_display(calculate_total())
    assert result == expected  # Exact comparison
```

2. Test the "$100 split three ways" case:
```python
def test_split_bill_three_ways():
    total = Decimal('100')
    parts = 3
    splits = DecimalPrecision.distribute_with_largest_remainder(total, parts)
    
    # Check total matches exactly
    assert sum(splits) == total
    
    # Check distribution is correct
    assert splits.count(Decimal('33.33')) == 2
    assert splits.count(Decimal('33.34')) == 1
```

3. Test percentage-based distributions:
```python
def test_percentage_distribution():
    total = Decimal('100')
    percentages = [Decimal('25'), Decimal('45'), Decimal('30')]
    amounts = DecimalPrecision.distribute_by_percentage(total, percentages)
    
    # Check total matches exactly
    assert sum(amounts) == total
    
    # Check distribution is correct
    assert amounts[0] == Decimal('25.00')
    assert amounts[1] == Decimal('45.00')
    assert amounts[2] == Decimal('30.00')
```

## Common Patterns and Examples

### Bill Splitting with Exact Total

```python
def split_bill(total, participants):
    splits = DecimalPrecision.distribute_with_largest_remainder(total, len(participants))
    return dict(zip(participants, splits))

# Example
bill_shares = split_bill(Decimal('100'), ['Alice', 'Bob', 'Charlie'])
# Result: {'Alice': Decimal('33.34'), 'Bob': Decimal('33.33'), 'Charlie': Decimal('33.33')}
```

### Running Balance Calculations

```python
def calculate_running_balance(starting_balance, transactions):
    balance = starting_balance
    running_balances = []
    
    for transaction in transactions:
        amount = transaction.amount
        # Keep full precision for internal calculations
        balance = DecimalPrecision.round_for_calculation(balance + amount)
        running_balances.append(balance)
    
    # Only round to 2 decimal places for display/response
    return [DecimalPrecision.round_for_display(bal) for bal in running_balances]
```

### Handling Percentages

```python
def calculate_percentage(amount, percentage):
    # Percentage can have 4 decimal places, e.g., 12.3456%
    decimal_percentage = percentage / Decimal('100')
    # Use 4 decimal places for calculation
    result = DecimalPrecision.round_for_calculation(amount * decimal_percentage)
    # Round to 2 decimal places at API boundary
    return DecimalPrecision.round_for_display(result)
```

## Edge Cases and Their Handling

1. **Zero Values**: Handle zero values directly, no need for special rounding:
```python
amount = Decimal('0')
```

2. **Very Small Values**: Small values will round to zero at 2 decimal places:
```python
small = Decimal('0.001')
display = DecimalPrecision.round_for_display(small)  # 0.00
```

3. **Negative Values**: Round negative values consistently:
```python
negative = Decimal('-10.235')
display = DecimalPrecision.round_for_display(negative)  # -10.24
```

4. **Division Operations**: Always convert to Decimal first, then divide:
```python
# Wrong
result = 100 / 3  # 33.333333333333336 (float)

# Right
result = Decimal('100') / Decimal('3')  # Decimal('33.33333333333333...')
display = DecimalPrecision.round_for_display(result)  # 33.33
```

## When to Use 4 vs. 2 Decimal Places

- **Use 2 Decimal Places (money_field) for**:
  - Currency amounts (prices, balances, payments)
  - Fee calculations
  - Transaction amounts
  - Bill totals and splits
  - Account balances
  
- **Use 4 Decimal Places (percentage_field) for**:
  - Percentage values (0.0-1.0 scale)
  - Interest rates
  - Confidence scores
  - Trend strengths
  - Risk assessments
  - Pattern strengths
  - Credit utilization rates

Remember, always use 4 decimal places for internal calculations, even for monetary fields, but round to 2 decimal places when displaying or returning monetary values through the API.
