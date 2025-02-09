from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.cashflow import CashflowForecast
from ..models.bills import Bill
from ..models.income import Income
from ..schemas.cashflow import CashflowCreate, CashflowUpdate, CashflowFilters

class CashflowService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, cashflow_data: CashflowCreate) -> CashflowForecast:
        """Create a new cashflow forecast"""
        forecast = CashflowForecast(**cashflow_data.model_dump())
        forecast.calculate_deficits()
        forecast.calculate_required_income()
        forecast.calculate_hourly_rates()
        
        self.session.add(forecast)
        await self.session.commit()
        await self.session.refresh(forecast)
        return forecast

    async def get(self, forecast_id: int) -> Optional[CashflowForecast]:
        """Get a cashflow forecast by ID"""
        result = await self.session.get(CashflowForecast, forecast_id)
        return result

    async def update(
        self, 
        forecast_id: int, 
        forecast_data: CashflowUpdate
    ) -> Optional[CashflowForecast]:
        """Update a cashflow forecast"""
        forecast = await self.get(forecast_id)
        if not forecast:
            return None

        update_data = forecast_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(forecast, field, value)

        forecast.calculate_deficits()
        forecast.calculate_required_income()
        forecast.calculate_hourly_rates()
        
        await self.session.commit()
        await self.session.refresh(forecast)
        return forecast

    async def delete(self, forecast_id: int) -> bool:
        """Delete a cashflow forecast"""
        forecast = await self.get(forecast_id)
        if not forecast:
            return False

        await self.session.delete(forecast)
        await self.session.commit()
        return True

    async def list(
        self,
        filters: Optional[CashflowFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[CashflowForecast], int]:
        """List cashflow forecasts with optional filtering"""
        query = select(CashflowForecast)

        if filters:
            conditions = []
            if filters.start_date:
                conditions.append(CashflowForecast.forecast_date >= filters.start_date)
            if filters.end_date:
                conditions.append(CashflowForecast.forecast_date <= filters.end_date)
            if filters.min_balance:
                conditions.append(CashflowForecast.balance >= filters.min_balance)
            if filters.max_balance:
                conditions.append(CashflowForecast.balance <= filters.max_balance)

            if conditions:
                query = query.where(and_(*conditions))

        # Get total count
        count_query = select(CashflowForecast)
        if filters and conditions:
            count_query = count_query.where(and_(*conditions))
        total = len((await self.session.execute(count_query)).scalars().all())

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = result.scalars().all()

        return items, total

    async def calculate_90_day_forecast(self, start_date: date) -> List[CashflowForecast]:
        """Calculate 90-day rolling forecast"""
        forecasts = []
        current_date = start_date

        for _ in range(90):
            # Get bills due on this date
            bills_query = select(Bill).where(
                and_(
                    Bill.due_date >= current_date,
                    Bill.due_date < current_date + timedelta(days=1),
                    Bill.paid == False
                )
            )
            bills_result = await self.session.execute(bills_query)
            bills = bills_result.scalars().all()
            total_bills = sum(bill.amount for bill in bills)

            # Get expected income on this date
            income_query = select(Income).where(
                and_(
                    Income.date >= current_date,
                    Income.date < current_date + timedelta(days=1),
                    Income.deposited == False
                )
            )
            income_result = await self.session.execute(income_query)
            incomes = income_result.scalars().all()
            total_income = sum(income.amount for income in incomes)

            # Calculate balance and forecast
            previous_forecast = forecasts[-1] if forecasts else None
            previous_balance = previous_forecast.balance if previous_forecast else Decimal(0)
            current_balance = previous_balance + total_income - total_bills

            # Create forecast for this date
            forecast = CashflowForecast(
                forecast_date=current_date,
                total_bills=total_bills,
                total_income=total_income,
                balance=current_balance,
                forecast=current_balance,  # Simple forecast for now
                min_14_day=Decimal(0),  # Will be updated later
                min_30_day=Decimal(0),
                min_60_day=Decimal(0),
                min_90_day=Decimal(0),
                daily_deficit=Decimal(0),
                yearly_deficit=Decimal(0),
                required_income=Decimal(0),
                hourly_rate_40=Decimal(0),
                hourly_rate_30=Decimal(0),
                hourly_rate_20=Decimal(0)
            )

            forecasts.append(forecast)
            current_date += timedelta(days=1)

        # Calculate minimum required amounts for each period
        for i, forecast in enumerate(forecasts):
            if i >= 13:  # 14-day minimum
                forecast.min_14_day = min(f.balance for f in forecasts[i-13:i+1])
            if i >= 29:  # 30-day minimum
                forecast.min_30_day = min(f.balance for f in forecasts[i-29:i+1])
            if i >= 59:  # 60-day minimum
                forecast.min_60_day = min(f.balance for f in forecasts[i-59:i+1])
            if i >= 89:  # 90-day minimum
                forecast.min_90_day = min(f.balance for f in forecasts[i-89:i+1])

            # Calculate other metrics
            forecast.calculate_deficits()
            forecast.calculate_required_income()
            forecast.calculate_hourly_rates()

            # Save forecast
            self.session.add(forecast)

        await self.session.commit()
        return forecasts

    async def get_minimum_required(self, forecast_id: int) -> Optional[CashflowForecast]:
        """Get minimum required funds for all periods"""
        forecast = await self.get(forecast_id)
        if not forecast:
            return None
        return forecast

    async def get_deficit_calculation(self, forecast_id: int) -> Optional[CashflowForecast]:
        """Get deficit calculations"""
        forecast = await self.get(forecast_id)
        if not forecast:
            return None
        return forecast

    async def get_hourly_rates(self, forecast_id: int) -> Optional[CashflowForecast]:
        """Get hourly rates for different work hours"""
        forecast = await self.get(forecast_id)
        if not forecast:
            return None
        return forecast
