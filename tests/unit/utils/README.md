# Unit Tests for Utility Functions

This directory contains unit tests for the utility functions used throughout the Debtonator application. These tests verify the behavior of helper functions that provide common functionality across multiple components.

## Purpose

Utility tests serve to verify:

1. **Function Behavior**: Test that utility functions produce expected outputs
2. **Error Handling**: Test that functions handle edge cases and errors appropriately
3. **Compatibility**: Ensure functions work with expected input types
4. **Consistency**: Verify functions behave consistently across different contexts

## Directory Structure

```tree
utils/
├── datetime_utils/                     # Tests for datetime utility functions
│   ├── test_aware_functions.py
│   ├── test_comparison_functions.py
│   ├── test_conversion_functions.py
│   ├── test_naive_functions.py
│   └── test_range_operations.py
├── db/                                 # Tests for database utility functions
│   └── README.md                       # Notes on testing db utils
├── feature_flags/                      # Tests for feature flag utilities
│   ├── README.md                       # Notes on testing feature flag utils
│   └── test_context_utils.py
├── test_datetime_utils.py              # Tests for datetime utils (main module)
└── test_decimal_precision.py           # Tests for decimal precision functions
```

## Testing Focus Areas

### Datetime Utilities

The `datetime_utils/` directory tests are organized by functionality:

```python
def test_ensure_utc():
    """Test ensuring that datetimes are UTC-aware."""
    # Test with naive datetime
    naive_dt = datetime(2023, 1, 1, 12, 0, 0)
    utc_dt = ensure_utc(naive_dt)
    
    assert utc_dt.tzinfo is not None
    assert utc_dt.tzinfo == timezone.utc
    
    # Test with already UTC datetime
    already_utc = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = ensure_utc(already_utc)
    
    assert result is already_utc  # Should return the same object
    
    # Test with non-UTC timezone
    est = timezone(timedelta(hours=-5))
    est_dt = datetime(2023, 1, 1, 7, 0, 0, tzinfo=est)
    utc_result = ensure_utc(est_dt)
    
    assert utc_result.tzinfo == timezone.utc
    assert utc_result.hour == 12  # 7 EST = 12 UTC
```

### Decimal Precision

The `test_decimal_precision.py` file tests decimal precision handling:

```python
def test_money_decimal():
    """Test MoneyDecimal type for monetary values."""
    # Test rounding to 2 decimal places
    value = MoneyDecimal("10.125")
    assert value == Decimal("10.13")
    
    # Test string formatting
    assert str(value) == "10.13"
    
    # Test from float (usually avoided but tested for robustness)
    float_value = MoneyDecimal.from_float(10.125)
    assert float_value == Decimal("10.13")
    
    # Test adding two MoneyDecimal values
    sum_value = MoneyDecimal("10.10") + MoneyDecimal("5.05")
    assert sum_value == Decimal("15.15")
    assert isinstance(sum_value, Decimal)
```

### Feature Flag Utilities

The `feature_flags/` directory tests feature flag utility functions:

```python
def test_context_from_request():
    """Test creating feature flag context from a request."""
    # Create mock request with required attributes
    request = Mock()
    request.client.host = "192.168.1.1"
    request.headers = {"User-Agent": "Test Browser"}
    
    # Create context
    context = context_from_request(request)
    
    assert context.ip_address == "192.168.1.1"
    assert context.client_info["user_agent"] == "Test Browser"
    assert context.evaluation_time is not None
```

## Integration Test Candidates

Some utility functions require integration tests:

1. **DB Error Handling**: Functions that interact with real database errors
2. **Feature Flag Configuration**: Functions that interact with registry singletons
3. **Http Exception Utilities**: Functions that interact with HTTP handlers

These are documented in subdirectory README.md files with coverage statistics and testing approaches.

## Best Practices

1. **Test Pure Functions**: Focus on inputs and outputs for pure functions
2. **Test All Edge Cases**: Include tests for boundary conditions and error cases
3. **Follow ADR-011**: Ensure datetime tests comply with timezone standards
4. **Test Decimal Precision**: Verify decimal rounding and precision handling
5. **Document Integration Needs**: Clearly identify functions that need integration tests
