# Cashflow Services Tests

## Purpose

This directory contains integration tests for the cashflow service components in Debtonator. These tests validate the business logic, repository integration, and service operations for cashflow forecasting, metrics, and analysis following the repository pattern defined in ADR-014.

## Related Documentation

- [Services Integration Tests](../README.md)
- [Repository Cashflow Tests](../../repositories/advanced/cashflow/README.md)
- [ADR-014: Repository Layer Compliance](/code/debtonator/docs/adr/implementation/adr014-implementation-checklist.md)

## Architecture

Cashflow services extend BaseService and use specialized repository implementations for different aspects of cashflow functionality:

1. **Metrics Service**: Handles financial metrics and KPIs
2. **Forecast Service**: Handles future cashflow projections
3. **Historical Service**: Analyzes past trends and patterns
4. **Realtime Service**: Provides current financial status
5. **Transaction Service**: Processes transaction data for cashflow analysis

Each service uses `_get_repository()` to access its corresponding repository following the patterns established in ADR-014.

## Implementation Patterns

### Specialized Service Pattern

Cashflow services follow a specialized service pattern where each service focuses on a specific aspect of cashflow management:

```python
@pytest.mark.asyncio
async def test_metrics_service_calculations(db_session):
    """Test metrics service calculates financial KPIs correctly."""
    # Use registered metrics_service fixture
    metrics_service = MetricsService(session=db_session)
    
    # Create test data through model fixtures
    checking = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("1000.00")
    )
    liability = await create_test_liability(
        db_session,
        amount=Decimal("500.00"),
        due_date=ensure_utc(datetime(2025, 1, 15))
    )
    
    # Calculate metrics using the service
    coverage_ratio = await metrics_service.calculate_coverage_ratio(
        start_date=ensure_utc(datetime(2025, 1, 1)),
        end_date=ensure_utc(datetime(2025, 1, 31))
    )
    
    # Verify calculation is correct
    assert coverage_ratio == Decimal("2.00")  # 1000 / 500 = 2.0
```

### Cross-Service Integration

Test how cashflow services integrate with each other:

```python
@pytest.mark.asyncio
async def test_cross_service_integration(db_session, metrics_service, forecast_service):
    """Test integration between metrics and forecast services."""
    # Create test data
    checking = await create_test_checking_account(db_session)
    
    # Generate forecast using forecast service
    forecast = await forecast_service.generate_cashflow_forecast(
        account_id=checking.id,
        days=30
    )
    
    # Use forecast data in metrics service
    risk_assessment = await metrics_service.assess_forecast_risk(forecast)
    
    # Verify cross-service integration works
    assert risk_assessment is not None
    assert "risk_level" in risk_assessment
    assert "recommendations" in risk_assessment
```

## Testing Focus Areas

### Cashflow Calculations

Test that cashflow calculations are mathematically correct:

1. **Financial Metrics**: Test calculation of financial ratios and KPIs
2. **Forecasting Accuracy**: Test projection algorithms and accuracy
3. **Trend Analysis**: Test identification of financial patterns
4. **Coverage Calculations**: Test sufficiency metrics and calculations

### Data Aggregation

Test proper aggregation of financial data across accounts:

```python
@pytest.mark.asyncio
async def test_aggregate_account_balances(db_session, metrics_service):
    """Test aggregation of account balances."""
    # Create multiple test accounts
    checking1 = await create_test_checking_account(
        db_session, 
        name="Checking 1",
        available_balance=Decimal("1000.00")
    )
    checking2 = await create_test_checking_account(
        db_session, 
        name="Checking 2",
        available_balance=Decimal("2000.00")
    )
    savings = await create_test_savings_account(
        db_session, 
        name="Savings",
        available_balance=Decimal("5000.00")
    )
    
    # Test aggregation across accounts
    total_liquid = await metrics_service.get_total_liquid_assets()
    
    # Verify aggregation is correct
    assert total_liquid == Decimal("8000.00")  # 1000 + 2000 + 5000 = 8000
```

### Repository Integration

Test proper repository usage through `_get_repository()`:

```python
@pytest.mark.asyncio
async def test_repository_integration(db_session, mocker):
    """Test cashflow service properly uses repositories."""
    # Create service
    metrics_service = MetricsService(session=db_session)
    
    # Spy on _get_repository method
    spy = mocker.spy(metrics_service, "_get_repository")
    
    # Call service method
    await metrics_service.calculate_coverage_ratio(
        start_date=ensure_utc(datetime(2025, 1, 1)),
        end_date=ensure_utc(datetime(2025, 1, 31))
    )
    
    # Verify repository was accessed correctly
    assert spy.called
    assert spy.call_args[0][0] == CashflowMetricsRepository
```

## Best Practices

1. **Test Specialized Service Functions**: Test the unique functionality of each cashflow service
2. **Test Cross-Service Integration**: Verify services work together correctly
3. **Test Mathematical Accuracy**: Verify financial calculations are precise
4. **Test Aggregation Logic**: Verify data aggregation across accounts
5. **Test Repository Integration**: Verify proper repository usage
6. **Test Error Handling**: Verify appropriate error handling for edge cases

## Testing Guidelines

All cashflow service tests must follow these guidelines:

1. **Write Function-Style Tests**: Write all tests in function style with descriptive docstrings
2. **Use Registered Fixtures**: Use fixtures that are registered in conftest.py
3. **Follow Four-Step Pattern**: Arrange, Schema, Act, Assert pattern for all tests
4. **Provide Clear Docstrings**: Every test should have a clear descriptive docstring
5. **Test Decimal Precision**: Use exact Decimal comparisons for financial calculations
6. **Test Date Handling**: Verify proper UTC datetime handling in all operations

## Recent Improvements

The cashflow services have been fully refactored to comply with ADR-014:

1. **Specialized Services**
   - Removed CashflowService anti-pattern (general facade)
   - Replaced with specialized services for metrics, forecasting, historical analysis
   - Each service inherits from BaseService for proper repository access

2. **Repository Integration**
   - Services use _get_repository() method for standardized repository access
   - Added specialized repositories for each cashflow function
   - Clear separation between different cashflow responsibilities

3. **Dependency Resolution**
   - Resolved circular dependencies in cashflow module
   - Created common domain types module
   - Established proper one-way dependency direction
