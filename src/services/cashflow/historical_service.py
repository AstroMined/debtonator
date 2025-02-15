from datetime import date, datetime, timedelta
from decimal import Decimal
from statistics import mean, stdev
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo
from sqlalchemy import select

from src.schemas.cashflow import (
    HistoricalTrendMetrics,
    HistoricalPeriodAnalysis,
    SeasonalityAnalysis,
    HistoricalTrendsResponse
)

from .base import BaseService
from .transaction_service import TransactionService
from .types import DateType

class HistoricalService(BaseService):
    """Service for analyzing historical cashflow trends and patterns."""

    def __init__(self, db):
        super().__init__(db)
        self._transaction_service = TransactionService(db)

    async def get_historical_trends(
        self,
        account_ids: List[int],
        start_date: DateType,
        end_date: DateType
    ) -> HistoricalTrendsResponse:
        """Analyze historical trends for specified accounts and date range.
        
        Args:
            account_ids: List of account IDs to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            HistoricalTrendsResponse with trend analysis
        """
        # Get all transactions for the specified accounts and date range
        transactions = await self._transaction_service.get_historical_transactions(
            account_ids, start_date, end_date
        )
        
        # Calculate trend metrics
        metrics = await self._calculate_trend_metrics(transactions)
        
        # Analyze periods (e.g., monthly, quarterly)
        period_analysis = await self._analyze_historical_periods(
            transactions, start_date, end_date
        )
        
        # Analyze seasonality
        seasonality = await self._analyze_seasonality(transactions)
        
        return HistoricalTrendsResponse(
            metrics=metrics,
            period_analysis=period_analysis,
            seasonality=seasonality,
            timestamp=date.today()
        )

    async def _calculate_trend_metrics(
        self,
        transactions: List[Dict]
    ) -> HistoricalTrendMetrics:
        """Calculate trend metrics from historical transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            HistoricalTrendMetrics with calculated metrics
        """
        if not transactions:
            raise ValueError("No transactions available for trend analysis")

        # Calculate daily net changes
        daily_changes = []
        daily_totals: Dict[date, Decimal] = {}

        for trans in transactions:
            trans_date = trans["date"]
            if trans_date not in daily_totals:
                daily_totals[trans_date] = Decimal("0")
            daily_totals[trans_date] += trans["amount"]

        daily_changes = list(daily_totals.values())

        # Calculate metrics
        avg_daily_change = Decimal(str(mean(daily_changes)))
        volatility = Decimal(str(stdev(daily_changes))) if len(daily_changes) > 1 else Decimal("0")

        # Determine trend direction and strength
        total_days = len(daily_changes)
        if total_days < 2:
            trend_direction = "stable"
            trend_strength = Decimal("0")
        else:
            start_balance = sum(t["amount"] for t in transactions[:total_days//4])
            end_balance = sum(t["amount"] for t in transactions[-total_days//4:])
            
            if abs(end_balance - start_balance) < volatility:
                trend_direction = "stable"
                trend_strength = Decimal("0.3")
            else:
                trend_direction = "increasing" if end_balance > start_balance else "decreasing"
                trend_strength = min(
                    Decimal("1"),
                    abs(end_balance - start_balance) / (volatility * Decimal("10"))
                )

        # Calculate seasonal factors
        seasonal_factors = {}
        for trans in transactions:
            month = trans["date"].strftime("%B").lower()
            if month not in seasonal_factors:
                seasonal_factors[month] = Decimal("0")
            seasonal_factors[month] += trans["amount"]

        # Calculate confidence score
        base_confidence = Decimal("0.7")
        transaction_factor = min(
            Decimal("0.2"),
            Decimal(str(len(transactions))) / Decimal("10")
        )
        volatility_ratio = volatility / (abs(avg_daily_change) + Decimal("0.01"))
        volatility_factor = max(
            Decimal("0"),
            Decimal("0.1") * (Decimal("1") - min(volatility_ratio, Decimal("1")))
        )
        
        confidence_score = min(
            base_confidence + transaction_factor + volatility_factor,
            Decimal("1.0")
        )
        confidence_score = max(confidence_score, Decimal("0.1"))

        return HistoricalTrendMetrics(
            average_daily_change=avg_daily_change,
            volatility=volatility,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            seasonal_factors=seasonal_factors,
            confidence_score=confidence_score
        )

    async def _analyze_historical_periods(
        self,
        transactions: List[Dict],
        start_date: date,
        end_date: date
    ) -> List[HistoricalPeriodAnalysis]:
        """Analyze transactions in specific periods (e.g., monthly).
        
        Args:
            transactions: List of transaction dictionaries
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of HistoricalPeriodAnalysis for each period
        """
        periods = []
        current_start = start_date

        while current_start < end_date:
            # Define period end (monthly periods)
            if current_start.month == 12:
                current_end = datetime(
                    current_start.year + 1, 1, 1,
                    tzinfo=ZoneInfo("UTC")
                ) - timedelta(days=1)
            else:
                current_end = datetime(
                    current_start.year,
                    current_start.month + 1, 1,
                    tzinfo=ZoneInfo("UTC")
                ) - timedelta(days=1)
            
            # Filter transactions for current period
            period_transactions = [
                t for t in transactions
                if current_start <= t["date"] <= current_end
            ]
            
            if period_transactions:
                # Calculate period metrics
                inflow = Decimal("0")
                outflow = Decimal("0")
                for t in period_transactions:
                    if t["type"] == "income":
                        inflow += abs(t["amount"])
                    else:  # payment
                        outflow += abs(t["amount"])
                
                # Find significant events
                type_averages = {}
                for t in period_transactions:
                    if t["type"] not in type_averages:
                        type_averages[t["type"]] = []
                    type_averages[t["type"]].append(abs(t["amount"]))
                
                # Calculate average for each type
                type_thresholds = {}
                for t_type, amounts in type_averages.items():
                    avg = Decimal(str(mean(amounts)))
                    type_thresholds[t_type] = avg * Decimal("1.1")
                
                significant_events = []
                for t in period_transactions:
                    threshold = type_thresholds.get(t["type"], Decimal("0"))
                    if abs(t["amount"]) > threshold:
                        significant_events.append({
                            "date": t["date"].isoformat(),
                            "description": (
                                f"Large {t['type']} in {t['category']} "
                                f"({abs(t['amount'])})"
                            )
                        })

                periods.append(HistoricalPeriodAnalysis(
                    period_start=current_start,
                    period_end=current_end,
                    average_balance=mean(t["amount"] for t in period_transactions),
                    peak_balance=max(t["amount"] for t in period_transactions),
                    lowest_balance=min(t["amount"] for t in period_transactions),
                    total_inflow=inflow,
                    total_outflow=outflow,
                    net_change=inflow - outflow,
                    significant_events=significant_events
                ))
            
            current_start = current_end + timedelta(days=1)
            if not isinstance(current_start, datetime):
                current_start = datetime.combine(
                    current_start,
                    datetime.min.time(),
                    tzinfo=ZoneInfo("UTC")
                )

        return periods

    async def _analyze_seasonality(
        self,
        transactions: List[Dict]
    ) -> SeasonalityAnalysis:
        """Analyze seasonal patterns in transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            SeasonalityAnalysis with seasonal patterns
        """
        # Initialize pattern dictionaries
        monthly_patterns = {i: Decimal("0") for i in range(1, 13)}
        day_of_week_patterns = {i: Decimal("0") for i in range(7)}
        day_of_month_patterns = {i: Decimal("0") for i in range(1, 32)}
        holiday_impacts = {}

        # Analyze patterns
        for trans in transactions:
            trans_date = trans["date"]
            amount = trans["amount"]

            # Monthly patterns
            monthly_patterns[trans_date.month] += amount

            # Day of week patterns
            day_of_week_patterns[trans_date.weekday()] += amount

            # Day of month patterns
            day_of_month_patterns[trans_date.day] += amount

            # Holiday impacts
            for holiday, holiday_date in self._holidays.items():
                # Check if transaction is within 7 days of holiday
                holiday_date_this_year = holiday_date.replace(
                    year=trans_date.year
                )
                days_to_holiday = (trans_date - holiday_date_this_year).days
                if -7 <= days_to_holiday <= 7:
                    if holiday not in holiday_impacts:
                        holiday_impacts[holiday] = Decimal("0")
                    holiday_impacts[holiday] += amount

        # Calculate seasonal strength
        monthly_variance = stdev(monthly_patterns.values()) if len(set(monthly_patterns.values())) > 1 else 0
        daily_variance = stdev(day_of_month_patterns.values()) if len(set(day_of_month_patterns.values())) > 1 else 0
        
        max_variance = max(monthly_variance, daily_variance)
        total_volume = sum(abs(t["amount"]) for t in transactions)
        
        seasonal_strength = min(
            Decimal("1"),
            Decimal(str(max_variance)) / (total_volume / Decimal("12"))
        ) if total_volume > 0 else Decimal("0")

        return SeasonalityAnalysis(
            monthly_patterns=monthly_patterns,
            day_of_week_patterns=day_of_week_patterns,
            day_of_month_patterns=day_of_month_patterns,
            holiday_impacts=holiday_impacts,
            seasonal_strength=seasonal_strength
        )
