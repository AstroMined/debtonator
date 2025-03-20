import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.schemas.income_trends import (
    IncomePattern,
    IncomeTrendsAnalysis,
    IncomeTrendsRequest,
    SeasonalityMetrics,
    SourceStatistics,
)


class IncomeTrendsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_trends(
        self, request: IncomeTrendsRequest
    ) -> IncomeTrendsAnalysis:
        """Analyze income trends based on historical data"""
        # Get income data within date range
        query = select(Income)
        if request.start_date:
            query = query.where(Income.date >= request.start_date)
        if request.end_date:
            query = query.where(Income.date <= request.end_date)
        if request.source:
            query = query.where(Income.source == request.source)

        result = await self.db.execute(query)
        income_records = result.scalars().all()

        if not income_records:
            raise ValueError("No income records found for the specified criteria")

        # Group records by source
        source_records: Dict[str, List[Income]] = defaultdict(list)
        for record in income_records:
            source_records[record.source].append(record)

        # Analyze patterns for each source
        patterns: List[IncomePattern] = []
        source_stats: List[SourceStatistics] = []

        for source, records in source_records.items():
            pattern = await self._analyze_source_pattern(source, records)
            # For irregular patterns, always include them regardless of confidence
            if (
                pattern.frequency == "irregular"
                or pattern.confidence_score >= request.min_confidence
            ):
                patterns.append(pattern)

            stats = await self._calculate_source_statistics(source, records)
            source_stats.append(stats)

        # Analyze seasonality across all records
        seasonality = await self._analyze_seasonality(income_records)

        # Calculate overall predictability
        predictability = self._calculate_overall_predictability(patterns, source_stats)

        return IncomeTrendsAnalysis(
            patterns=patterns,
            seasonality=seasonality,
            source_statistics=source_stats,
            analysis_date=date.today(),
            data_start_date=min(r.date for r in income_records),
            data_end_date=max(r.date for r in income_records),
            overall_predictability_score=predictability,
        )

    async def _analyze_source_pattern(
        self, source: str, records: List[Income]
    ) -> IncomePattern:
        """Analyze pattern for a specific income source"""
        dates = [r.date for r in records]
        amounts = [r.amount for r in records]

        # Calculate intervals between dates
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

        if not intervals:
            return IncomePattern(
                source=source,
                frequency="irregular",
                average_amount=sum(amounts) / len(amounts),
                confidence_score=Decimal("0.0"),
                last_occurrence=max(dates),
                next_predicted=None,
            )

        # Determine frequency pattern
        avg_interval = Decimal(str(statistics.mean(intervals)))
        interval_std = Decimal(
            str(statistics.stdev(intervals) if len(intervals) > 1 else float("inf"))
        )

        frequency, confidence = self._determine_frequency(avg_interval, interval_std)

        # Predict next occurrence if pattern is reliable
        next_predicted = None
        if confidence > Decimal("0.7"):
            next_predicted = max(dates) + timedelta(days=round(float(avg_interval)))

        return IncomePattern(
            source=source,
            frequency=frequency,
            average_amount=sum(amounts) / len(amounts),
            confidence_score=confidence,
            last_occurrence=max(dates),
            next_predicted=next_predicted,
        )

    def _determine_frequency(
        self, avg_interval: Decimal, interval_std: Decimal
    ) -> Tuple[str, Decimal]:
        """Determine frequency pattern and confidence score"""
        # Define expected intervals
        patterns = {
            "weekly": Decimal("7"),
            "biweekly": Decimal("14"),
            "monthly": Decimal("30"),
        }

        # Find closest matching pattern
        best_match = "irregular"
        best_confidence = Decimal("0.0")

        for pattern, expected in patterns.items():
            deviation = abs(avg_interval - expected)
            if deviation <= Decimal("2") and interval_std <= Decimal("2"):
                confidence = (
                    Decimal("1.0")
                    - (deviation / Decimal("4"))
                    - (interval_std / Decimal("4"))
                )
                if confidence > best_confidence:
                    best_match = pattern
                    best_confidence = confidence

        return best_match, max(Decimal("0.0"), min(Decimal("1.0"), best_confidence))

    async def _calculate_source_statistics(
        self, source: str, records: List[Income]
    ) -> SourceStatistics:
        """Calculate statistical metrics for an income source"""
        amounts = [r.amount for r in records]

        return SourceStatistics(
            source=source,
            total_occurrences=len(records),
            total_amount=sum(amounts),
            average_amount=sum(amounts) / len(amounts),
            min_amount=min(amounts),
            max_amount=max(amounts),
            standard_deviation=Decimal(
                str(statistics.stdev(amounts) if len(amounts) > 1 else 0)
            ),
            reliability_score=self._calculate_reliability_score(records),
        )

    def _calculate_reliability_score(self, records: List[Income]) -> Decimal:
        """Calculate reliability score based on consistency of amounts and timing"""
        if len(records) < 2:
            return Decimal("0.0")

        amounts = [r.amount for r in records]
        dates = [r.date for r in records]

        # Calculate coefficient of variation for amounts
        mean_amount = sum(amounts) / len(amounts)
        std_amount = Decimal(str(statistics.stdev(amounts)))
        cv_amount = std_amount / mean_amount if mean_amount > 0 else Decimal("inf")

        # Calculate consistency of intervals
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        mean_interval = Decimal(str(statistics.mean(intervals)))
        std_interval = Decimal(str(statistics.stdev(intervals)))
        cv_interval = (
            std_interval / mean_interval if mean_interval > 0 else Decimal("inf")
        )

        # Combine metrics into reliability score
        amount_reliability = Decimal("1.0") / (Decimal("1.0") + cv_amount)
        interval_reliability = Decimal("1.0") / (Decimal("1.0") + cv_interval)

        return (amount_reliability + interval_reliability) / Decimal("2.0")

    async def _analyze_seasonality(
        self, records: List[Income]
    ) -> Optional[SeasonalityMetrics]:
        """Analyze seasonal patterns in income data"""
        if len(records) < 12:  # Need at least a year of data
            return None

        # Group by month
        monthly_totals = defaultdict(list)
        for record in records:
            monthly_totals[record.date.month].append(record.amount)

        # Calculate monthly averages with Decimal
        monthly_averages = {}
        for month, amounts in monthly_totals.items():
            total = sum(amounts)
            count = Decimal(str(len(amounts)))
            monthly_averages[month] = total / count

        if not monthly_averages:
            return None

        # Find peaks and troughs
        avg_values = list(monthly_averages.values())
        avg_amount = sum(avg_values) / len(avg_values)
        std_amount = Decimal(str(statistics.stdev(avg_values)))

        peak_months = [
            month
            for month, amount in monthly_averages.items()
            if amount > (avg_amount + Decimal("0.5") * std_amount)
        ]

        trough_months = [
            month
            for month, amount in monthly_averages.items()
            if amount < (avg_amount - Decimal("0.5") * std_amount)
        ]

        # Calculate coefficient of variation
        cv = std_amount / avg_amount if avg_amount > 0 else Decimal("inf")

        # Determine confidence based on data consistency
        confidence = Decimal("1.0") / (Decimal("1.0") + cv)

        return SeasonalityMetrics(
            period="monthly",
            peak_months=peak_months,
            trough_months=trough_months,
            variance_coefficient=float(cv),
            confidence_score=confidence,
        )

    def _calculate_overall_predictability(
        self, patterns: List[IncomePattern], statistics: List[SourceStatistics]
    ) -> float:
        """Calculate overall predictability score"""
        if not patterns or not statistics:
            return 0.0

        # Weight factors
        pattern_weight = Decimal("0.4")
        reliability_weight = Decimal("0.6")

        # Average pattern confidence
        pattern_scores = [Decimal(str(p.confidence_score)) for p in patterns]
        pattern_score = sum(pattern_scores) / len(pattern_scores)

        # Average reliability score
        reliability_scores = [Decimal(str(s.reliability_score)) for s in statistics]
        reliability_score = sum(reliability_scores) / len(reliability_scores)

        result = (pattern_score * pattern_weight) + (
            reliability_score * reliability_weight
        )
        return float(result)
