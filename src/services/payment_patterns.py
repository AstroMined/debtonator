"""
Payment pattern service implementation.

This module provides services for analyzing payment patterns, including
frequency detection, amount analysis, and pattern classification.
"""

from typing import Any, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment
from src.repositories.payment_patterns import PaymentPatternRepository
from src.schemas.payment_patterns import (
    AmountStatistics,
    FrequencyMetrics,
    PatternType,
    PaymentPatternAnalysis,
    PaymentPatternRequest,
)
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService


# TODO: Create a separate ExpensePatternService for analyzing non-bill payment patterns
class BillPaymentPatternService(BaseService):
    """
    Service for analyzing payment patterns for bills.
    
    Provides comprehensive analysis of payment patterns, including frequency
    detection, amount analysis, and pattern classification.
    """
    
    # Expected days before due date
    TARGET_DAYS = 5

    def __init__(
        self, 
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize service with database session and optional services.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
            feature_flag_service (Optional[FeatureFlagService]): Feature flag service
            config_provider (Optional[Any]): Configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def analyze_payment_patterns(
        self, request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        """
        Analyze payment patterns based on the provided request criteria.
        
        This method retrieves payments matching the filter criteria and performs
        comprehensive pattern analysis, including frequency detection, amount
        analysis, and pattern classification.
        
        Args:
            request (PaymentPatternRequest): Filter criteria and analysis parameters
            
        Returns:
            PaymentPatternAnalysis: Comprehensive pattern analysis result
        """
        # Get repository
        pattern_repo = await self._get_repository(PaymentPatternRepository)
        
        # Get payments using repository
        payments = await pattern_repo.get_payments_with_filters(
            liability_id=request.liability_id,
            account_id=request.account_id,
            category_id=request.category_id,
            start_date=request.start_date,
            end_date=request.end_date,
            order_by_asc=True,  # Always ascending for pattern analysis
        )
        
        # Debug info
        print(
            f"\nGot {len(payments)} payments for liability {request.liability_id} between {request.start_date} and {request.end_date}"
        )
        for p in payments:
            print(
                f"  Payment: {p.amount} on {p.payment_date} (liability_id={p.liability_id})"
            )

        # Not enough data for analysis
        if len(payments) < request.min_sample_size:
            return self._create_unknown_pattern(payments, request)

        # Calculate metrics using repository methods
        avg_days, std_dev_days, min_days, max_days = await pattern_repo.calculate_payment_frequency_metrics(payments)
        frequency_metrics = FrequencyMetrics(
            average_days_between=avg_days,
            std_dev_days=std_dev_days,
            min_days=min_days,
            max_days=max_days,
        )
        
        avg_amount, std_dev_amount, min_amount, max_amount, total_amount = await pattern_repo.calculate_amount_statistics(payments)
        amount_statistics = AmountStatistics(
            average_amount=avg_amount,
            std_dev_amount=std_dev_amount,
            min_amount=min_amount,
            max_amount=max_amount,
            total_amount=total_amount,
        )
        
        # Determine pattern type (business logic stays in service)
        pattern_type, confidence_score, notes = self._determine_pattern_type(
            frequency_metrics, amount_statistics, len(payments)
        )

        # Get date range using repository method
        first_payment, last_payment = await pattern_repo.get_date_range_for_pattern_analysis(
            payments,
            default_start_date=request.start_date,
            default_end_date=request.end_date,
        )

        # Get suggested category using repository method
        suggested_category = await pattern_repo.get_most_common_category(payments)

        # Return comprehensive analysis
        return PaymentPatternAnalysis(
            pattern_type=pattern_type,
            confidence_score=confidence_score,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=len(payments),
            analysis_period_start=first_payment,
            analysis_period_end=last_payment,
            suggested_category=suggested_category,
            notes=notes,
        )

    # These methods are now in the repository layer
    # Keeping them as private methods to maintain backwards compatibility
    # but they simply delegate to the repository implementation
    
    async def _calculate_frequency_metrics(
        self, payments: List[Payment]
    ) -> FrequencyMetrics:
        """
        Calculate frequency metrics for a list of payments.
        
        This method delegates to the repository layer implementation.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            
        Returns:
            FrequencyMetrics: Metrics about payment frequency
        """
        # This method is retained for backwards compatibility,
        # but now delegates to the repository implementation
        pattern_repo = await self._get_repository(PaymentPatternRepository)
        avg_days, std_dev_days, min_days, max_days = await pattern_repo.calculate_payment_frequency_metrics(payments)
        
        return FrequencyMetrics(
            average_days_between=avg_days,
            std_dev_days=std_dev_days,
            min_days=min_days,
            max_days=max_days,
        )
        
    async def _calculate_amount_statistics(
        self, payments: List[Payment]
    ) -> AmountStatistics:
        """
        Calculate amount statistics for a list of payments.
        
        This method delegates to the repository layer implementation.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            
        Returns:
            AmountStatistics: Statistical analysis of payment amounts
        """
        # This method is retained for backwards compatibility,
        # but now delegates to the repository implementation
        pattern_repo = await self._get_repository(PaymentPatternRepository)
        avg_amount, std_dev_amount, min_amount, max_amount, total_amount = await pattern_repo.calculate_amount_statistics(payments)
        
        return AmountStatistics(
            average_amount=avg_amount,
            std_dev_amount=std_dev_amount,
            min_amount=min_amount,
            max_amount=max_amount,
            total_amount=total_amount,
        )

    def _determine_pattern_type(
        self,
        frequency_metrics: FrequencyMetrics,
        amount_statistics: AmountStatistics,
        sample_size: int,
    ) -> Tuple[PatternType, float, List[str]]:
        notes = []

        # Handle same-day payments
        if frequency_metrics.average_days_between == 0:
            return PatternType.UNKNOWN, 0.0, ["All payments occurred on the same day"]

        # Calculate base confidence based on sample size
        sample_size_factor = min(1.0, sample_size / 10)  # Scale up to 10 samples

        # Calculate timing consistency
        timing_cv = (
            frequency_metrics.std_dev_days / frequency_metrics.average_days_between
            if frequency_metrics.average_days_between > 0
            else float("inf")
        )

        # Calculate amount consistency
        amount_cv = float(
            amount_statistics.std_dev_amount / amount_statistics.average_amount
        )

        # Check for gaps in payment sequence
        max_expected_interval = (
            frequency_metrics.average_days_between * 1.25
        )  # More sensitive gap detection
        if frequency_metrics.max_days > max_expected_interval:
            gap_size = (
                frequency_metrics.max_days - frequency_metrics.average_days_between
            )
            notes.append(
                f"Irregular pattern with significant gap: {gap_size:.1f} days longer than expected interval"
            )
            confidence = min(
                0.5, 0.2 + (sample_size_factor * 0.3)
            )  # Lower confidence for gapped patterns
            return PatternType.IRREGULAR, confidence, notes

        # Check for irregular timing patterns
        if timing_cv > 0.12:  # More strict timing variation threshold
            notes.append(
                f"Irregular payment timing: {frequency_metrics.average_days_between:.1f} days between payments (±{frequency_metrics.std_dev_days:.1f} days)"
            )
            confidence = min(0.6, 0.3 + (sample_size_factor * 0.3))
            return PatternType.IRREGULAR, confidence, notes

        # Seasonal pattern detection
        if amount_cv > 0.2:  # Significant amount variation
            if timing_cv < 0.2:  # But consistent timing
                if 25 <= frequency_metrics.average_days_between <= 35:
                    notes.append("Monthly payments with seasonal amount variation")
                else:
                    notes.append(
                        f"Regular {frequency_metrics.average_days_between:.1f}-day intervals with seasonal amount variation"
                    )
                confidence = min(0.8, sample_size_factor)
                return PatternType.SEASONAL, confidence, notes

        # Regular pattern detection
        if timing_cv < 0.15:  # Slightly more lenient for borderline cases
            notes.append(
                f"Consistent payment timing: every {frequency_metrics.average_days_between:.1f} days"
            )
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
        notes.append(
            f"Irregular payment pattern with variable timing: {frequency_metrics.average_days_between:.1f} days between payments (±{frequency_metrics.std_dev_days:.1f} days)"
        )
        # Lower confidence for irregular patterns
        confidence = min(0.6, 0.3 + (sample_size_factor * 0.3))
        return PatternType.IRREGULAR, confidence, notes

    async def _create_unknown_pattern(
        self, payments: List[Payment], request: PaymentPatternRequest
    ) -> PaymentPatternAnalysis:
        """
        Create an unknown pattern analysis result when insufficient data is available.
        
        Args:
            payments (List[Payment]): Limited list of payments (below minimum sample size)
            request (PaymentPatternRequest): Original analysis request
            
        Returns:
            PaymentPatternAnalysis: Pattern analysis with UNKNOWN type
        """
        # Get repository
        pattern_repo = await self._get_repository(PaymentPatternRepository)
        
        # Use request dates if available, otherwise use the repository method
        start_date, end_date = await pattern_repo.get_date_range_for_pattern_analysis(
            payments,
            default_start_date=request.start_date,
            default_end_date=request.end_date,
        )

        # Ensure we have at least one payment for sample_size validation
        sample_size = max(1, len(payments))
        
        # Calculate amount statistics using repository method
        amount_statistics = await self._calculate_amount_statistics(payments)

        return PaymentPatternAnalysis(
            pattern_type=PatternType.UNKNOWN,
            confidence_score=0.0,
            frequency_metrics=FrequencyMetrics(
                average_days_between=0, std_dev_days=0, min_days=0, max_days=0
            ),
            amount_statistics=amount_statistics,
            sample_size=sample_size,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            notes=["Insufficient data for pattern analysis"],
        )

    async def _suggest_category(self, payments: List[Payment]) -> Optional[str]:
        """
        Get the most common category from a list of payments.
        
        This method delegates to the repository layer implementation.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            
        Returns:
            Optional[str]: Most common category or None if no categories
        """
        # This method is retained for backwards compatibility,
        # but now delegates to the repository implementation
        pattern_repo = await self._get_repository(PaymentPatternRepository)
        return await pattern_repo.get_most_common_category(payments)

    async def analyze_bill_payments(
        self, liability_id: int
    ) -> Optional[PaymentPatternAnalysis]:
        """
        Analyze payment patterns for a specific bill.
        
        Args:
            liability_id (int): ID of the liability/bill to analyze
            
        Returns:
            Optional[PaymentPatternAnalysis]: Pattern analysis or None if no payments
        """
        # Get repositories
        pattern_repo = await self._get_repository(PaymentPatternRepository)
        
        # Get bill payments using repository
        payments = await pattern_repo.get_bill_payments(liability_id)

        print(f"\nFound {len(payments)} payments:")
        for p in payments:
            print(
                f"  Payment: {p.amount} on {p.payment_date} (liability_id={p.liability_id})"
            )

        if not payments:
            return None

        # Get date range using repository method
        start_date, end_date = await pattern_repo.get_date_range_for_pattern_analysis(payments)

        # Create request with appropriate parameters
        request = PaymentPatternRequest(
            min_sample_size=2,  # Lower minimum for bill-specific analysis
            start_date=start_date,
            end_date=end_date,
            account_id=None,
            category_id=None,
            liability_id=liability_id,  # Add liability_id to request
        )

        # Use existing analysis logic
        return await self.analyze_payment_patterns(request)
