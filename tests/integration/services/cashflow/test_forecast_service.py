"""Integration tests for the cashflow forecast service."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.liabilities import Liability
from src.schemas.cashflow import AccountForecastRequest, CustomForecastParameters
from src.services.cashflow.cashflow_forecast_service import ForecastService
from src.utils.datetime_utils import (
    days_from_now,
    ensure_utc,
    naive_days_from_now,
    naive_end_of_day,
    naive_start_of_day,
    utc_now,
)


@pytest.mark.asyncio
async def test_get_forecast(
    db_session: AsyncSession, test_checking_account, test_category
):
    """Test getting cashflow forecast for a date range."""
    # Arrange: Create test data
    # We use the test_checking_account fixture instead of creating a new account

    # Create liabilities
    today = date.today()
    liabilities = [
        Liability(
            name="Rent",
            amount=Decimal("800.00"),
            due_date=naive_days_from_now(5),  # 5 days in the future
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Utilities",
            amount=Decimal("100.00"),
            due_date=naive_days_from_now(10),  # 10 days in the future
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Internet",
            amount=Decimal("50.00"),
            due_date=naive_days_from_now(15),  # 15 days in the future
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
    ]
    for liability in liabilities:
        db_session.add(liability)
    await db_session.commit()

    # Create income
    income_entries = [
        Income(
            date=naive_days_from_now(3),  # 3 days in the future
            source="Salary",
            amount=Decimal("2000.00"),
            deposited=False,
            account_id=test_checking_account.id,
        ),
        Income(
            date=naive_days_from_now(17),  # 17 days in the future
            source="Freelance",
            amount=Decimal("500.00"),
            deposited=False,
            account_id=test_checking_account.id,
        ),
    ]
    for income in income_entries:
        db_session.add(income)
    await db_session.commit()

    # Create forecast service
    service = ForecastService(session=db_session)

    # Act: Get forecast for date range
    start_date = today
    end_date = today + timedelta(days=20)

    # Create request parameters with proper datetime conversion
    start_datetime = ensure_utc(naive_start_of_day(start_date))
    end_datetime = ensure_utc(naive_end_of_day(end_date))

    request = AccountForecastRequest(
        account_id=test_checking_account.id,
        start_date=start_datetime,
        end_date=end_datetime,
        include_pending=True,
        include_recurring=True,
        include_transfers=True,
    )

    forecast_response = await service.get_account_forecast(request)

    # Assert: Validate forecast results
    assert (
        len(forecast_response.daily_forecasts) == 21
    )  # 21 days including start and end date
    assert forecast_response.daily_forecasts[0].date.date() == start_date
    assert (
        forecast_response.daily_forecasts[0].projected_balance
        == test_checking_account.available_balance
    )  # Initial balance

    # Check balance after first income
    assert forecast_response.daily_forecasts[
        3
    ].projected_balance == test_checking_account.available_balance + Decimal("2000.00")

    # Check balance after first liability
    assert forecast_response.daily_forecasts[
        5
    ].projected_balance == test_checking_account.available_balance + Decimal(
        "2000.00"
    ) - Decimal(
        "800.00"
    )

    # Check balance after second liability
    assert forecast_response.daily_forecasts[
        10
    ].projected_balance == test_checking_account.available_balance + Decimal(
        "2000.00"
    ) - Decimal(
        "800.00"
    ) - Decimal(
        "100.00"
    )

    # Check balance after third liability and second income
    assert forecast_response.daily_forecasts[
        17
    ].projected_balance == test_checking_account.available_balance + Decimal(
        "2000.00"
    ) + Decimal(
        "500.00"
    ) - Decimal(
        "800.00"
    ) - Decimal(
        "100.00"
    ) - Decimal(
        "50.00"
    )


@pytest.mark.asyncio
async def test_get_required_funds(
    db_session: AsyncSession, test_checking_account, test_category
):
    """Test calculating required funds for a date range."""
    # Arrange: Create test liabilities
    today = date.today()
    liabilities = [
        Liability(
            name="Rent",
            amount=Decimal("800.00"),
            due_date=naive_days_from_now(5),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Utilities",
            amount=Decimal("100.00"),
            due_date=naive_days_from_now(10),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Internet",
            amount=Decimal("50.00"),
            due_date=naive_days_from_now(15),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
    ]
    for liability in liabilities:
        db_session.add(liability)
    await db_session.commit()

    # Create forecast service
    service = ForecastService(session=db_session)

    # Act: Get required funds for date range
    start_date = today
    end_date = today + timedelta(days=20)
    required_funds = await service.get_required_funds(
        test_checking_account.id, start_date, end_date
    )

    # Assert: Sum of all liabilities in range
    assert required_funds == Decimal("950.00")  # 800 + 100 + 50


@pytest.mark.asyncio
async def test_get_forecast_empty_range(
    db_session: AsyncSession, test_checking_account
):
    """Test getting forecast with no liabilities or income in range."""
    # Create forecast service
    service = ForecastService(session=db_session)

    # Act: Get forecast for empty date range
    today = date.today()
    start_date = today + timedelta(days=100)  # Future date with no entries
    end_date = start_date + timedelta(days=5)

    # Create request parameters with proper datetime conversion
    start_datetime = ensure_utc(naive_start_of_day(start_date))
    end_datetime = ensure_utc(naive_end_of_day(end_date))

    request = AccountForecastRequest(
        account_id=test_checking_account.id,
        start_date=start_datetime,
        end_date=end_datetime,
        include_pending=True,
        include_recurring=True,
        include_transfers=True,
    )

    forecast_response = await service.get_account_forecast(request)

    # Assert: Verify forecast has correct length and balances
    assert (
        len(forecast_response.daily_forecasts) == 6
    )  # 6 days including start and end date
    for entry in forecast_response.daily_forecasts:
        assert entry.projected_balance == test_checking_account.available_balance


@pytest.mark.asyncio
async def test_get_required_funds_empty_range(
    db_session: AsyncSession, test_checking_account
):
    """Test getting required funds with no liabilities in range."""
    # Create forecast service
    service = ForecastService(session=db_session)

    # Act: Get required funds for empty date range
    today = date.today()
    start_date = today + timedelta(days=100)  # Future date with no entries
    end_date = start_date + timedelta(days=5)
    required_funds = await service.get_required_funds(
        test_checking_account.id, start_date, end_date
    )

    # Assert: No funds required for empty range
    assert required_funds == Decimal("0.00")


@pytest.mark.asyncio
async def test_get_custom_forecast(
    db_session: AsyncSession, test_checking_account, test_category
):
    """Test getting custom forecast with specific parameters."""
    # Arrange: We use the test_checking_account fixture instead of creating a new account

    # Create liabilities
    today = date.today()
    liabilities = [
        Liability(
            name="Rent",
            amount=Decimal("800.00"),
            due_date=naive_days_from_now(5),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Utilities",
            amount=Decimal("100.00"),
            due_date=naive_days_from_now(10),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Internet",
            amount=Decimal("50.00"),
            due_date=naive_days_from_now(15),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
    ]
    for liability in liabilities:
        db_session.add(liability)
    await db_session.commit()

    # Create income
    income_entries = [
        Income(
            date=naive_days_from_now(3),
            source="Salary",
            amount=Decimal("2000.00"),
            deposited=False,
            account_id=test_checking_account.id,
        ),
        Income(
            date=naive_days_from_now(17),
            source="Freelance",
            amount=Decimal("500.00"),
            deposited=False,
            account_id=test_checking_account.id,
        ),
    ]
    for income in income_entries:
        db_session.add(income)
    await db_session.commit()

    # Create forecast service
    service = ForecastService(session=db_session)

    # Schema: Create custom forecast parameters with UTC-aware datetimes (ADR-011 compliant)
    params = CustomForecastParameters(
        start_date=utc_now(),
        end_date=days_from_now(20),
        include_pending=True,
        account_ids=[test_checking_account.id],
        confidence_threshold=Decimal("0.8"),
    )

    # Act: Get custom forecast
    forecast = await service.get_custom_forecast(params)

    # Assert: Verify forecast structure and content
    assert forecast.parameters == params
    assert len(forecast.results) == 21  # 21 days including start and end
    assert forecast.overall_confidence >= Decimal("0.0")
    assert forecast.overall_confidence <= Decimal("1.0")

    # Verify summary statistics
    assert "total_projected_income" in forecast.summary_statistics
    assert "total_projected_expenses" in forecast.summary_statistics
    assert "average_confidence" in forecast.summary_statistics
    assert "min_balance" in forecast.summary_statistics
    assert "max_balance" in forecast.summary_statistics

    # Verify first day's projections
    first_day = forecast.results[0]
    # Compare only the date portion of the datetime
    assert first_day.date.date() == today
    assert first_day.projected_balance == test_checking_account.available_balance
    assert first_day.confidence_score >= Decimal("0.0")
    assert first_day.confidence_score <= Decimal("1.0")

    # Verify income day projections (day 3)
    income_day = forecast.results[3]
    assert income_day.projected_income == Decimal("2000.00")
    assert "income_Salary" in income_day.contributing_factors

    # Verify expense day projections (day 5)
    expense_day = forecast.results[5]
    assert expense_day.projected_expenses == Decimal("800.00")
    assert "liability_Housing" in expense_day.contributing_factors


@pytest.mark.asyncio
async def test_get_custom_forecast_filtered(
    db_session: AsyncSession, test_checking_account, test_category
):
    """Test getting custom forecast with category filters."""
    # Arrange: We use the test_checking_account fixture instead of creating a new account

    # Create liabilities
    today = date.today()
    liabilities = [
        Liability(
            name="Rent",
            amount=Decimal("800.00"),
            due_date=naive_days_from_now(5),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Utilities",
            amount=Decimal("100.00"),
            due_date=naive_days_from_now(10),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
        Liability(
            name="Internet",
            amount=Decimal("50.00"),
            due_date=naive_days_from_now(15),
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            recurring=False,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
        ),
    ]
    for liability in liabilities:
        db_session.add(liability)
    await db_session.commit()

    # Create income
    income_entries = [
        Income(
            date=naive_days_from_now(3),
            source="Salary",
            amount=Decimal("2000.00"),
            deposited=False,
            account_id=test_checking_account.id,
        ),
        Income(
            date=naive_days_from_now(17),
            source="Freelance",
            amount=Decimal("500.00"),
            deposited=False,
            account_id=test_checking_account.id,
        ),
    ]
    for income in income_entries:
        db_session.add(income)
    await db_session.commit()

    # Create forecast service
    service = ForecastService(session=db_session)

    # Schema: Create custom forecast parameters with category filters (ADR-011 compliant)
    params = CustomForecastParameters(
        start_date=utc_now(),
        end_date=days_from_now(20),
        include_pending=True,
        account_ids=[test_checking_account.id],
        categories=["Utilities"],  # Only include utilities
        confidence_threshold=Decimal("0.8"),
    )

    # Act: Get custom forecast with filter
    forecast = await service.get_custom_forecast(params)

    # Assert: Verify utilities expenses are included but housing is not
    utilities_total = Decimal("0.0")
    housing_total = Decimal("0.0")

    for day in forecast.results:
        for factor, amount in day.contributing_factors.items():
            if "expense_bill" in factor:
                # In the filtered test, we should only have the Utilities and Internet expenses
                utilities_total += amount

    assert utilities_total == Decimal("150.00")  # 100 + 50
    assert housing_total == Decimal("0.00")  # Housing category was filtered out


@pytest.mark.asyncio
async def test_get_custom_forecast_no_accounts(db_session: AsyncSession):
    """Test custom forecast with no valid accounts."""
    # Arrange: Create forecast service
    service = ForecastService(session=db_session)

    # Schema: Create parameters with non-existent account (ADR-011 compliant)
    params = CustomForecastParameters(
        start_date=utc_now(),
        end_date=days_from_now(20),
        include_pending=True,
        account_ids=[999],  # Non-existent account
        confidence_threshold=Decimal("0.8"),
    )

    # Act & Assert: Verify appropriate error is raised
    with pytest.raises(ValueError, match="No valid accounts found for analysis"):
        await service.get_custom_forecast(params)
