from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.cashflow import (
    CashflowCreate,
    CashflowFilters,
    CashflowList,
    CashflowResponse,
    CashflowUpdate,
    DeficitCalculation,
    HourlyRates,
    MinimumRequired,
)
from src.services.cashflow.cashflow_base import CashflowBaseService


router = APIRouter(prefix="/cashflow", tags=["cashflow"])


@router.post("/", response_model=CashflowResponse, status_code=201)
async def create_forecast(
    forecast_data: CashflowCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new cashflow forecast"""
    service = CashflowBaseService(db)
    forecast = await service.create(forecast_data)
    return forecast


@router.get("/{forecast_id}", response_model=CashflowResponse)
async def get_forecast(forecast_id: int, db: AsyncSession = Depends(get_db)):
    """Get a cashflow forecast by ID"""
    service = CashflowBaseService(db)
    forecast = await service.get(forecast_id)
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast


@router.put("/{forecast_id}", response_model=CashflowResponse)
async def update_forecast(
    forecast_id: int, forecast_data: CashflowUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a cashflow forecast"""
    service = CashflowBaseService(db)
    forecast = await service.update(forecast_id, forecast_data)
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast


@router.delete("/{forecast_id}", status_code=204)
async def delete_forecast(forecast_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a cashflow forecast"""
    service = CashflowBaseService(db)
    success = await service.delete(forecast_id)
    if not success:
        raise HTTPException(status_code=404, detail="Forecast not found")


@router.get("/", response_model=CashflowList)
async def list_forecasts(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_balance: Optional[float] = None,
    max_balance: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List cashflow forecasts with optional filtering"""
    filters = CashflowFilters(
        start_date=start_date,
        end_date=end_date,
        min_balance=min_balance,
        max_balance=max_balance,
    )
    service = CashflowBaseService(db)
    items, total = await service.list(filters, skip, limit)
    return CashflowList(items=items, total=total)


@router.post("/forecast/90-day", response_model=list[CashflowResponse])
async def calculate_90_day_forecast(
    start_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
):
    """Calculate 90-day rolling forecast"""
    service = CashflowBaseService(db)
    forecasts = await service.calculate_90_day_forecast(start_date)
    return forecasts


@router.get("/{forecast_id}/minimum-required", response_model=MinimumRequired)
async def get_minimum_required(forecast_id: int, db: AsyncSession = Depends(get_db)):
    """Get minimum required funds for all periods"""
    service = CashflowBaseService(db)
    forecast = await service.get_minimum_required(forecast_id)
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return MinimumRequired(
        min_14_day=forecast.min_14_day,
        min_30_day=forecast.min_30_day,
        min_60_day=forecast.min_60_day,
        min_90_day=forecast.min_90_day,
    )


@router.get("/{forecast_id}/deficit", response_model=DeficitCalculation)
async def get_deficit_calculation(forecast_id: int, db: AsyncSession = Depends(get_db)):
    """Get deficit calculations"""
    service = CashflowBaseService(db)
    forecast = await service.get_deficit_calculation(forecast_id)
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return DeficitCalculation(
        daily_deficit=forecast.daily_deficit,
        yearly_deficit=forecast.yearly_deficit,
        required_income=forecast.required_income,
    )


@router.get("/{forecast_id}/hourly-rates", response_model=HourlyRates)
async def get_hourly_rates(forecast_id: int, db: AsyncSession = Depends(get_db)):
    """Get hourly rates for different work hours"""
    service = CashflowBaseService(db)
    forecast = await service.get_hourly_rates(forecast_id)
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return HourlyRates(
        hourly_rate_40=forecast.hourly_rate_40,
        hourly_rate_30=forecast.hourly_rate_30,
        hourly_rate_20=forecast.hourly_rate_20,
    )
