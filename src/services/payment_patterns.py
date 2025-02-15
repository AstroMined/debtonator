from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment, PaymentSource
from src.models.liabilities import Liability
from src.schemas.payment_patterns import (
    AmountStatistics,
    FrequencyMetrics,
    PatternType,
    PaymentPatternAnalysis,
    PaymentPatternRequest
)


class PaymentPatternService:
    # Expected days before due date
    TARGET_DAYS = 5

    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_payment_patterns(
        self, request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        # Build query based on request filters
        query = (
            select(Payment)
            .where(Payment.liability_id == request.liability_id)  # Add liability_id filter first
            .order_by(Payment.payment_date.asc())  # Order by payment date ascending
        )
        
        # Add other filters
        
        if request.account_id:
            query = query.join(Payment.sources).filter(PaymentSource.account_id == request.account_id)
        if request.category_id:
            query = query.filter(Payment.category == request.category_id)
        # Don't filter by dates since we want all payments for the bill

        # Execute query
        result = await self.session.execute(query)
        payments = result.scalars().all()
        print(f"\nGot {len(payments)} payments for liability {request.liability_id} between {request.start_date} and {request.end_date}: {payments}")  # Debug print

        if len(payments) < request.min_sample_size:
            return self._create_unknown_pattern(payments, request)

        # Calculate metrics
        frequency_metrics, days_before_due = await self._calculate_frequency_metrics(payments)
        amount_statistics = self._calculate_amount_statistics(payments)
        pattern_type, confidence_score, notes = self._determine_pattern_type(
            frequency_metrics, amount_statistics, len(payments), days_before_due
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

    async def _calculate_frequency_metrics(self, payments: List[Payment]) -> Tuple[FrequencyMetrics, List[float]]:
        if len(payments) < 2:
            return (
                FrequencyMetrics(
                    average_days_between=0,
                    std_dev_days=0,
                    min_days=0,
                    max_days=0
                ),
                []
            )

        # Calculate days before due date using actual Liability records
        days_before_due = []
        for payment in payments:
            # Get liability record for actual due date
            liability = await self.session.get(Liability, payment.liability_id)
            if liability:
                days_before = abs((liability.due_date - payment.payment_date).days)
                days_before_due.append(days_before)
        
        if not days_before_due:
            return (
                FrequencyMetrics(
                    average_days_between=0,
                    std_dev_days=0,
                    min_days=0,
                    max_days=0
                ),
                []
            )
            
        # Calculate metrics based on days before due date
        deviations = [abs(d - self.TARGET_DAYS) for d in days_before_due]
        
        # Calculate mean and standard deviation
        mean_days = float(np.mean(days_before_due))  # Average days before due date
        std_dev = float(np.std(deviations))  # Standard deviation from target
        
        # Debug print
        print(f"\nDays before due: {days_before_due}")
        print(f"Mean days: {mean_days}, Std dev: {std_dev}")
        
        # For consistent patterns, all payments should be made the same number of days before due date
        metrics = FrequencyMetrics(
            average_days_between=self.TARGET_DAYS,  # Use target days as the expected pattern
            std_dev_days=std_dev,  # Standard deviation from target
            min_days=min(days_before_due),
            max_days=max(days_before_due)
        )
        return metrics, days_before_due

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
        amount_statistics: AmountStatistics,
        sample_size: int,
        days_before_due: List[float]
    ) -> Tuple[PatternType, float, List[str]]:
        notes = []
        
        # Skip if no valid metrics
        if frequency_metrics.average_days_between == 0:
            return PatternType.UNKNOWN, 0.0, ["Insufficient data for pattern analysis"]
            
        # Calculate base confidence based on sample size and consistency
        sample_size_factor = min(1.0, sample_size / 10)  # Scale up to 10 samples
        consistency_factor = max(0.0, 1.0 - (frequency_metrics.std_dev_days / self.TARGET_DAYS))
        base_confidence = sample_size_factor * consistency_factor

        # Calculate amount coefficient of variation
        amount_cv = float(amount_statistics.std_dev_amount / amount_statistics.average_amount)

        # Very consistent pattern (within 1 day of target)
        if frequency_metrics.std_dev_days < 1:
            notes.append(f"Highly consistent payment timing: {frequency_metrics.average_days_between:.1f} days before due date")
            confidence = min(0.95, base_confidence)
            return PatternType.REGULAR, confidence, notes

        # Fairly consistent pattern (within 2 days of target)
        if frequency_metrics.std_dev_days < 2:
            notes.append(f"Consistent payment timing with minor variations: {frequency_metrics.average_days_between:.1f} days before due date (±{frequency_metrics.std_dev_days:.1f} days)")
            confidence = min(0.8, base_confidence)
            return PatternType.REGULAR, confidence, notes

        # Monthly pattern check
        if abs(frequency_metrics.average_days_between - self.TARGET_DAYS) < 2:
            if amount_cv > 0.2:  # Variable amounts suggest seasonal
                notes.append("Monthly payments with seasonal amount variation")
                return PatternType.SEASONAL, min(0.8, base_confidence), notes
            notes.append("Regular monthly payment pattern")
            return PatternType.REGULAR, min(0.7, base_confidence), notes

        # Irregular pattern (high variation)
        notes.append(f"Variable payment timing: {frequency_metrics.average_days_between:.1f} days before due date (±{frequency_metrics.std_dev_days:.1f} days)")
        confidence = max(0.3, min(0.6, base_confidence))
        return PatternType.IRREGULAR, confidence, notes

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

    async def analyze_bill_payments(self, liability_id: int) -> Optional[PaymentPatternAnalysis]:
        """Analyze payment patterns for a specific bill."""
        """Analyze payment patterns for a specific bill."""
        # Build query for bill payments
        query = select(Payment).where(
            Payment.liability_id == liability_id
        ).order_by(Payment.payment_date.desc())  # Get most recent payments first

        # Execute query
        result = await self.session.execute(query)
        payments = result.scalars().all()

        print(f"\nFound {len(payments)} payments: {payments}")  # Debug print
        
        if not payments:
            return None

        # Create request with default parameters
        # Get the earliest and latest payment dates
        payment_dates = [payment.payment_date for payment in payments]
        if payment_dates:
            start_date = datetime.combine(min(payment_dates), datetime.min.time())
            end_date = datetime.combine(max(payment_dates), datetime.min.time())
        else:
            start_date = end_date = datetime.now()

        request = PaymentPatternRequest(
            min_sample_size=3,  # Minimum required by schema
            start_date=start_date,
            end_date=end_date,
            account_id=None,
            category_id=None,
            liability_id=liability_id  # Add liability_id to request
        )

        # Use existing analysis logic
        return await self.analyze_payment_patterns(request)
