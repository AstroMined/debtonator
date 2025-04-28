"""
Income Trends Service for analyzing patterns in income data.

This service provides functionality to analyze income trends, including:
- Frequency pattern detection
- Seasonality analysis
- Source-specific statistics
- Overall income predictability scoring

Implements ADR-014 Repository Layer Compliance by using repositories
for all data access operations rather than direct database queries.
"""

import statistics
from datetime import timedelta
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.repositories.income_trends import IncomeTrendsRepository
from src.schemas.income_trends import (
    IncomePattern,
    IncomeTrendsAnalysis,
    IncomeTrendsRequest,
    SeasonalityMetrics,
    SourceStatistics,
)
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import ensure_utc, utc_now


class IncomeTrendsService(BaseService):
    """
    Service for analyzing income trends based on historical data.

    This service uses the IncomeTrendsRepository for data access operations,
    following ADR-014 Repository Layer Compliance. It processes income data
    to identify patterns, seasonality, and provide statistical analysis.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """Initialize the service with session and optional services.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service
            config_provider: Optional config provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def analyze_trends(
        self, request: IncomeTrendsRequest
    ) -> IncomeTrendsAnalysis:
        """Analyze income trends based on historical data.

        This method retrieves income records matching the request criteria
        and analyzes them for patterns, seasonality, and statistical metrics.

        Args:
            request: Parameters for the trends analysis

        Returns:
            Comprehensive analysis of income trends

        Raises:
            ValueError: If no income records are found for the specified criteria
        """
        # Get repository
        repo = await self._get_repository(IncomeTrendsRepository)

        # Get income data within date range using repository
        income_records = await repo.get_income_records(
            start_date=request.start_date,
            end_date=request.end_date,
            source=request.source,
        )

        if not income_records:
            raise ValueError("No income records found for the specified criteria")

        # Group records by source using repository method
        source_records = await repo.group_records_by_source(income_records)

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
        seasonality = await self._analyze_seasonality(income_records, repo)

        # Calculate overall predictability
        predictability = self._calculate_overall_predictability(patterns, source_stats)

        # Get min and max dates from records using repository
        min_date, max_date = await repo.get_min_max_dates(income_records)

        # Return complete analysis
        return IncomeTrendsAnalysis(
            patterns=patterns,
            seasonality=seasonality,
            source_statistics=source_stats,
            analysis_date=utc_now(),
            data_start_date=ensure_utc(min_date),
            data_end_date=ensure_utc(max_date),
            overall_predictability_score=predictability,
        )

    async def _analyze_source_pattern(
        self, source: str, records: List[Income]
    ) -> IncomePattern:
        """Analyze pattern for a specific income source.

        Args:
            source: Income source name
            records: List of income records for this source

        Returns:
            Detected pattern for this income source
        """
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
                last_occurrence=ensure_utc(max(dates)),
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
            next_predicted = ensure_utc(
                max(dates) + timedelta(days=round(float(avg_interval)))
            )

        return IncomePattern(
            source=source,
            frequency=frequency,
            average_amount=sum(amounts) / len(amounts),
            confidence_score=confidence,
            last_occurrence=ensure_utc(max(dates)),
            next_predicted=next_predicted,
        )

    def _determine_frequency(
        self, avg_interval: Decimal, interval_std: Decimal
    ) -> Tuple[str, Decimal]:
        """Determine frequency pattern and confidence score.

        Args:
            avg_interval: Average interval between income dates
            interval_std: Standard deviation of intervals

        Returns:
            Tuple of (frequency_pattern, confidence_score)
        """
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
        """Calculate statistical metrics for an income source.

        Args:
            source: Income source name
            records: List of income records for this source

        Returns:
            Statistical metrics for this income source
        """
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
        """Calculate reliability score based on consistency of amounts and timing.

        Args:
            records: List of income records to analyze

        Returns:
            Reliability score between 0 and 1
        """
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
        self, records: List[Income], repo: IncomeTrendsRepository
    ) -> Optional[SeasonalityMetrics]:
        """Analyze seasonal patterns in income data.

        Args:
            records: List of income records to analyze
            repo: IncomeTrendsRepository for data access operations

        Returns:
            Seasonality metrics if sufficient data exists, None otherwise
        """
        if len(records) < 12:  # Need at least a year of data
            return None

        # Group by month using repository method
        monthly_records = await repo.get_records_by_month(records)

        # Calculate monthly averages with Decimal
        monthly_averages = {}
        for month, month_records in monthly_records.items():
            amounts = [r.amount for r in month_records]
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
        """Calculate overall predictability score.

        Args:
            patterns: List of detected income patterns
            statistics: List of source statistics

        Returns:
            Predictability score between 0 and 1
        """
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
