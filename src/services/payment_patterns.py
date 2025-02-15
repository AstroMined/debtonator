from datetime import datetime
from decimal import Decimal
import numpy as np
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment, PaymentSource
from src.schemas.payment_patterns import (
    AmountStatistics,
    FrequencyMetrics,
    PatternType,
    PaymentPatternAnalysis,
    PaymentPatternRequest
)


class PaymentPatternService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_payment_patterns(
        self, request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        # Build query based on request filters
        query = select(Payment).order_by(Payment.payment_date)
        
        if request.account_id:
            query = query.join(Payment.sources).filter(PaymentSource.account_id == request.account_id)
        if request.category_id:
            query = query.filter(Payment.category == request.category_id)
        if request.start_date:
            query = query.filter(Payment.payment_date >= request.start_date)
        if request.end_date:
            query = query.filter(Payment.payment_date <= request.end_date)

        # Execute query
        result = await self.session.execute(query)
        payments = result.scalars().all()

        if len(payments) < request.min_sample_size:
            return self._create_unknown_pattern(payments, request)

        # Calculate metrics
        frequency_metrics = self._calculate_frequency_metrics(payments)
        amount_statistics = self._calculate_amount_statistics(payments)
        pattern_type, confidence_score, notes = self._determine_pattern_type(
            frequency_metrics, amount_statistics
        )

        return PaymentPatternAnalysis(
            pattern_type=pattern_type,
            confidence_score=confidence_score,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=len(payments),
            analysis_period_start=payments[0].payment_date,
            analysis_period_end=payments[-1].payment_date,
            suggested_category=self._suggest_category(payments),
            notes=notes
        )

    def _calculate_frequency_metrics(self, payments: List[Payment]) -> FrequencyMetrics:
        if len(payments) < 2:
            return FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            )

        # Calculate days between payments
        dates = [payment.payment_date for payment in payments]
        days_between = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        
        return FrequencyMetrics(
            average_days_between=float(np.mean(days_between)),
            std_dev_days=float(np.std(days_between)),
            min_days=min(days_between),
            max_days=max(days_between)
        )

    def _calculate_amount_statistics(self, payments: List[Payment]) -> AmountStatistics:
        if not payments:
            return AmountStatistics(
                average_amount=Decimal('0'),
                std_dev_amount=Decimal('0'),
                min_amount=Decimal('0'),
                max_amount=Decimal('0'),
                total_amount=Decimal('0')
            )

        amounts = [payment.amount for payment in payments]
        return AmountStatistics(
            average_amount=Decimal(str(np.mean(amounts))),
            std_dev_amount=Decimal(str(np.std(amounts))),
            min_amount=min(amounts),
            max_amount=max(amounts),
            total_amount=sum(amounts)
        )

    def _determine_pattern_type(
        self,
        frequency_metrics: FrequencyMetrics,
        amount_statistics: AmountStatistics
    ) -> Tuple[PatternType, float, List[str]]:
        notes = []
        
        # Initialize base confidence score
        confidence_score = 1.0
        
        # Check frequency consistency
        frequency_cv = frequency_metrics.std_dev_days / frequency_metrics.average_days_between
        amount_cv = float(amount_statistics.std_dev_amount / amount_statistics.average_amount)

        # Highly regular pattern
        if frequency_cv < 0.1 and amount_cv < 0.1:
            notes.append("Highly consistent payment pattern detected")
            return PatternType.REGULAR, 0.95, notes

        # Regular pattern with some variation
        if frequency_cv < 0.2 and amount_cv < 0.2:
            notes.append("Regular payment pattern with minor variations")
            return PatternType.REGULAR, 0.8, notes

        # Check for irregular pattern first based on frequency
        if frequency_cv > 0.2:
            notes.append("Irregular payment pattern detected")
            confidence_score = max(0.3, 1.0 - (frequency_cv + amount_cv) / 2)
            return PatternType.IRREGULAR, confidence_score, notes

        # For consistent frequencies, check monthly patterns
        if frequency_metrics.average_days_between > 28 and frequency_metrics.average_days_between < 32:
            notes.append("Monthly payment pattern detected")
            # High amount variation suggests seasonal pattern
            if amount_cv > 0.2:
                notes.append("Variable amounts suggest seasonal pattern")
                return PatternType.SEASONAL, 0.8, notes
            # Low amount variation suggests regular pattern
            return PatternType.REGULAR, 0.7, notes

        # Default to irregular if no other patterns match
        notes.append("Irregular payment pattern detected")
        confidence_score = max(0.3, 1.0 - (frequency_cv + amount_cv) / 2)
        return PatternType.IRREGULAR, confidence_score, notes

    def _create_unknown_pattern(
        self,
        payments: List[Payment],
        request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        # Use request dates if available, otherwise use current time
        start_date = request.start_date if request.start_date else datetime.utcnow()
        end_date = request.end_date if request.end_date else datetime.utcnow()
        
        return PaymentPatternAnalysis(
            pattern_type=PatternType.UNKNOWN,
            confidence_score=0.0,
            frequency_metrics=FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            ),
            amount_statistics=self._calculate_amount_statistics(payments),
            sample_size=len(payments),
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            notes=["Insufficient data for pattern analysis"]
        )

    def _suggest_category(self, payments: List[Payment]) -> Optional[str]:
        if not payments:
            return None
            
        # Get the most common category
        categories = {}
        for payment in payments:
            if payment.category:
                categories[payment.category] = categories.get(payment.category, 0) + 1
                
        if not categories:
            return None
            
        most_common = max(categories.items(), key=lambda x: x[1])[0]
        return most_common
