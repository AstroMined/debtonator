from datetime import datetime, timedelta, timezone
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


# TODO: Create a separate ExpensePatternService for analyzing non-bill payment patterns
class BillPaymentPatternService:
    # Expected days before due date
    TARGET_DAYS = 5

    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_payment_patterns(
        self, request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        # Build base query
        query = select(Payment).order_by(Payment.payment_date.asc())
        
        # Add filters
        if request.liability_id:
            query = query.where(Payment.liability_id == request.liability_id)
        if request.account_id:
            query = query.join(Payment.sources).filter(PaymentSource.account_id == request.account_id)
        if request.category_id:
            query = query.filter(Payment.category.ilike(f"%{request.category_id}%"))  # Case-insensitive partial match
        if request.start_date:
            query = query.filter(Payment.payment_date >= request.start_date)
        if request.end_date:
            query = query.filter(Payment.payment_date <= request.end_date)

        # Execute query
        result = await self.session.execute(query)
        payments = result.scalars().all()
        print(f"\nGot {len(payments)} payments for liability {request.liability_id} between {request.start_date} and {request.end_date}")
        for p in payments:
            print(f"  Payment: {p.amount} on {p.payment_date} (liability_id={p.liability_id})")

        if len(payments) < request.min_sample_size:
            return self._create_unknown_pattern(payments, request)

        # Calculate metrics
        frequency_metrics = await self._calculate_frequency_metrics(payments)
        amount_statistics = self._calculate_amount_statistics(payments)
        pattern_type, confidence_score, notes = self._determine_pattern_type(
            frequency_metrics, amount_statistics, len(payments)
        )

        # Ensure payment dates are UTC
        first_payment = payments[0].payment_date
        last_payment = payments[-1].payment_date
        if not first_payment.tzinfo:
            first_payment = first_payment.replace(tzinfo=timezone.utc)
        if not last_payment.tzinfo:
            last_payment = last_payment.replace(tzinfo=timezone.utc)

        return PaymentPatternAnalysis(
            pattern_type=pattern_type,
            confidence_score=confidence_score,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=len(payments),
            analysis_period_start=first_payment,
            analysis_period_end=last_payment,
            suggested_category=self._suggest_category(payments),
            notes=notes
        )

    async def _calculate_frequency_metrics(self, payments: List[Payment]) -> FrequencyMetrics:
        if len(payments) < 2:
            return FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            )

        # Calculate days between consecutive payments
        days_between = []
        payment_dates = []
        
        # Ensure all payment dates are UTC
        for payment in payments:
            payment_date = payment.payment_date if payment.payment_date.tzinfo else payment.payment_date.replace(tzinfo=timezone.utc)
            payment_dates.append(payment_date)
        
        # Sort dates to ensure correct interval calculation
        payment_dates.sort()
        
        # Check if all payments are on the same day
        if (max(payment_dates) - min(payment_dates)).days == 0:
            return FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            )
        
        # Calculate intervals between consecutive payments
        for i in range(len(payment_dates) - 1):
            delta = (payment_dates[i + 1] - payment_dates[i]).days
            if delta > 0:  # Only count non-zero intervals
                days_between.append(delta)

        if not days_between:  # If no valid intervals found
            return FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            )

        # Calculate metrics
        mean_days = float(np.mean(days_between))
        std_dev = float(np.std(days_between))

        return FrequencyMetrics(
            average_days_between=mean_days,
            std_dev_days=std_dev,
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
        amount_statistics: AmountStatistics,
        sample_size: int
    ) -> Tuple[PatternType, float, List[str]]:
        notes = []
        
        # Handle same-day payments
        if frequency_metrics.average_days_between == 0:
            return PatternType.UNKNOWN, 0.0, ["All payments occurred on the same day"]
            
        # Calculate base confidence based on sample size
        sample_size_factor = min(1.0, sample_size / 10)  # Scale up to 10 samples

        # Calculate timing consistency
        timing_cv = frequency_metrics.std_dev_days / frequency_metrics.average_days_between if frequency_metrics.average_days_between > 0 else float('inf')
        
        # Calculate amount consistency
        amount_cv = float(amount_statistics.std_dev_amount / amount_statistics.average_amount)

        # Check for gaps in payment sequence
        max_expected_interval = frequency_metrics.average_days_between * 1.25  # More sensitive gap detection
        if frequency_metrics.max_days > max_expected_interval:
            gap_size = frequency_metrics.max_days - frequency_metrics.average_days_between
            notes.append(f"Irregular pattern with significant gap: {gap_size:.1f} days longer than expected interval")
            confidence = min(0.5, 0.2 + (sample_size_factor * 0.3))  # Lower confidence for gapped patterns
            return PatternType.IRREGULAR, confidence, notes

        # Check for irregular timing patterns
        if timing_cv > 0.12:  # More strict timing variation threshold
            notes.append(f"Irregular payment timing: {frequency_metrics.average_days_between:.1f} days between payments (±{frequency_metrics.std_dev_days:.1f} days)")
            confidence = min(0.6, 0.3 + (sample_size_factor * 0.3))
            return PatternType.IRREGULAR, confidence, notes

        # Seasonal pattern detection
        if amount_cv > 0.2:  # Significant amount variation
            if timing_cv < 0.2:  # But consistent timing
                if 25 <= frequency_metrics.average_days_between <= 35:
                    notes.append("Monthly payments with seasonal amount variation")
                else:
                    notes.append(f"Regular {frequency_metrics.average_days_between:.1f}-day intervals with seasonal amount variation")
                confidence = min(0.8, sample_size_factor)
                return PatternType.SEASONAL, confidence, notes

        # Regular pattern detection
        if timing_cv < 0.15:  # Slightly more lenient for borderline cases
            notes.append(f"Consistent payment timing: every {frequency_metrics.average_days_between:.1f} days")
            # High confidence for very consistent patterns
            if sample_size <= 3:
                confidence = 0.5  # Fixed confidence for minimal samples
            else:
                # Base confidence for regular patterns
                base_confidence = 0.7
                # Add up to 0.1 based on sample size
                confidence = min(0.875, base_confidence + (sample_size_factor * 0.1))
                # Small boost for very low standard deviation
                if frequency_metrics.std_dev_days < 2.0:
                    confidence = min(0.875, confidence + 0.075)
            return PatternType.REGULAR, confidence, notes

        # Monthly pattern check (30 ± 5 days)
        if 25 <= frequency_metrics.average_days_between <= 35 and timing_cv < 0.2:
            notes.append("Regular monthly payment pattern")
            # Moderate confidence for monthly patterns
            if timing_cv < 0.15:  # More consistent timing
                confidence = min(0.8, 0.6 + (sample_size_factor * 0.2))
            else:  # Less consistent timing
                confidence = min(0.7, 0.5 + (sample_size_factor * 0.2))
            return PatternType.REGULAR, confidence, notes

        # Irregular pattern (high variation)
        notes.append(f"Irregular payment pattern with variable timing: {frequency_metrics.average_days_between:.1f} days between payments (±{frequency_metrics.std_dev_days:.1f} days)")
        # Lower confidence for irregular patterns
        confidence = min(0.6, 0.3 + (sample_size_factor * 0.3))
        return PatternType.IRREGULAR, confidence, notes

    def _create_unknown_pattern(
        self,
        payments: List[Payment],
        request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        # Use request dates if available, otherwise use current time in UTC
        start_date = request.start_date if request.start_date else datetime.now(timezone.utc)
        end_date = request.end_date if request.end_date else datetime.now(timezone.utc)
        
        # Ensure we have at least one payment for sample_size validation
        sample_size = max(1, len(payments))
        
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
            sample_size=sample_size,
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
        # Build query for bill payments
        query = select(Payment).where(
            Payment.liability_id == liability_id
        ).order_by(Payment.payment_date.asc())  # Order by ascending date to match other methods

        # Execute query
        result = await self.session.execute(query)
        payments = result.scalars().all()

        print(f"\nFound {len(payments)} payments:")
        for p in payments:
            print(f"  Payment: {p.amount} on {p.payment_date} (liability_id={p.liability_id})")
        
        if not payments:
            return None

        # Create request with default parameters
        # Get the earliest and latest payment dates
        payment_dates = [
            payment.payment_date if payment.payment_date.tzinfo 
            else payment.payment_date.replace(tzinfo=timezone.utc)
            for payment in payments
        ]
        
        if payment_dates:
            # Include the full day for both start and end dates in UTC
            min_date = min(payment_dates)
            max_date = max(payment_dates)
            
            # Set time components for start/end dates
            start_date = (min_date.replace(hour=0, minute=0, second=0, microsecond=0) - 
                         timedelta(days=1))
            end_date = max_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            start_date = end_date = datetime.now(timezone.utc)

        request = PaymentPatternRequest(
            min_sample_size=2,  # Lower minimum for bill-specific analysis
            start_date=start_date,
            end_date=end_date,
            account_id=None,
            category_id=None,
            liability_id=liability_id  # Add liability_id to request
        )

        # Use existing analysis logic
        return await self.analyze_payment_patterns(request)
