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
            query = query.filter(Payment.category == request.category_id)
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

    async def _calculate_frequency_metrics(self, payments: List[Payment]) -> FrequencyMetrics:
        if len(payments) < 2:
            return FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            )

        # Calculate days before due date for each payment
        days_before = []
        for payment in payments:
            # Extract due date from payment description
            if payment.description and "Due date:" in payment.description:
                try:
                    due_date_str = payment.description.split("Due date: ")[1]
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    delta = (due_date - payment.payment_date).days
                    days_before.append(delta)
                except (ValueError, IndexError):
                    print(f"Failed to parse due date from description: {payment.description}")
                    continue

        if len(days_before) < 2:  # Need at least 2 valid measurements
            return FrequencyMetrics(
                average_days_between=0,
                std_dev_days=0,
                min_days=0,
                max_days=0
            )

        # Calculate metrics
        mean_days = float(np.mean(days_before))
        std_dev = float(np.std(days_before))

        return FrequencyMetrics(
            average_days_between=mean_days,
            std_dev_days=std_dev,
            min_days=min(days_before),
            max_days=max(days_before)
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
        
        # Skip if no valid metrics
        if frequency_metrics.average_days_between == 0:
            return PatternType.UNKNOWN, 0.0, ["Insufficient data for pattern analysis"]
            
        # Calculate base confidence based on sample size
        sample_size_factor = min(1.0, sample_size / 10)  # Scale up to 10 samples

        # Calculate timing consistency
        timing_cv = frequency_metrics.std_dev_days / frequency_metrics.average_days_between if frequency_metrics.average_days_between > 0 else float('inf')
        
        # Calculate amount consistency
        amount_cv = float(amount_statistics.std_dev_amount / amount_statistics.average_amount)

        # Seasonal pattern detection (check first)
        if amount_cv > 0.2:  # Significant amount variation
            if timing_cv < 0.2:  # But consistent timing
                if 25 <= frequency_metrics.average_days_between <= 35:
                    notes.append("Monthly payments with seasonal amount variation")
                else:
                    notes.append(f"Regular {frequency_metrics.average_days_between:.1f}-day intervals with seasonal amount variation")
                confidence = min(0.8, sample_size_factor)
                return PatternType.SEASONAL, confidence, notes

        # Regular pattern detection
        if timing_cv < 0.1:  # Very consistent intervals
            notes.append(f"Highly consistent payment timing: every {frequency_metrics.average_days_between:.1f} days")
            # High confidence for very consistent patterns
            if sample_size <= 3:
                confidence = 0.5  # Fixed confidence for minimal samples
            else:
                # Base confidence of 0.85 for consistent patterns
                # Add up to 0.1 based on sample size
                confidence = min(0.95, 0.85 + (sample_size_factor * 0.1))
                # Boost confidence for very low standard deviation
                if frequency_metrics.std_dev_days < 2.0:
                    confidence = min(0.95, confidence + 0.05)
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
        payment_dates = [payment.payment_date for payment in payments]
        if payment_dates:
            # Include the full day for both start and end dates
            # Use a date just before the first payment to ensure we include it
            start_date = datetime.combine(min(payment_dates), datetime.min.time()) - timedelta(days=1)
            end_date = datetime.combine(max(payment_dates), datetime.max.time())
        else:
            start_date = end_date = datetime.now()

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
