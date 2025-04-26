from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payments import PaymentRepository
from src.schemas.payment_patterns import PatternType, PaymentPatternAnalysis
from src.schemas.recommendations import (
    BillPaymentTimingRecommendation,
    ConfidenceLevel,
    ImpactMetrics,
    RecommendationResponse,
)
from src.services.base import BaseService
from src.services.cashflow.cashflow_metrics_service import MetricsService
from src.services.feature_flags import FeatureFlagService
from src.services.payment_patterns import BillPaymentPatternService
from src.utils.datetime_utils import ensure_utc, utc_now


class RecommendationService(BaseService):
    """
    Service for generating financial recommendations.
    
    This service analyzes payment patterns, account statuses, and cashflow to generate
    actionable financial recommendations, particularly around bill payment timing.
    
    Attributes:
        _session: SQLAlchemy async session
        _feature_flag_service: Optional feature flag service
        pattern_service: Service for analyzing bill payment patterns
        metrics_service: Service for cashflow metrics operations
    """
    
    def __init__(
        self,
        session: AsyncSession,
        pattern_service: Optional[BillPaymentPatternService] = None,
        metrics_service: Optional[MetricsService] = None,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None
    ):
        """
        Initialize the recommendation service.
        
        Args:
            session: SQLAlchemy async session
            pattern_service: Optional pattern analysis service (created if not provided)
            metrics_service: Optional metrics service (created if not provided)
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)
        
        # Initialize dependent services
        if pattern_service:
            self.pattern_service = pattern_service
        else:
            self.pattern_service = BillPaymentPatternService(
                session, feature_flag_service, config_provider
            )
            
        if metrics_service:
            self.metrics_service = metrics_service
        else:
            self.metrics_service = MetricsService(
                session, feature_flag_service, config_provider
            )

    async def get_bill_payment_recommendations(
        self, account_ids: Optional[List[int]] = None
    ) -> RecommendationResponse:
        """
        Generate bill payment timing recommendations based on historical patterns.
        
        Args:
            account_ids: Optional list of account IDs to filter by
            
        Returns:
            Response containing recommendations with impact analysis
        """
        # Initialize results
        recommendations: List[BillPaymentTimingRecommendation] = []
        total_savings = Decimal("0")
        confidence_sum = Decimal("0")

        # Get repositories
        liability_repo = await self._get_repository(LiabilityRepository)

        # Get active bills
        bills = await liability_repo.get_active_bills()

        for bill in bills:
            recommendation = await self._analyze_bill_payment_timing(bill, account_ids)
            if recommendation:
                recommendations.append(recommendation)
                if recommendation.impact.savings_potential:
                    total_savings += recommendation.impact.savings_potential
                confidence_sum += self._confidence_to_decimal(recommendation.confidence)

        avg_confidence = (
            confidence_sum / len(recommendations) if recommendations else Decimal("0")
        )

        # Create timestamp with proper timezone
        generated_at = utc_now()

        return RecommendationResponse(
            recommendations=recommendations,
            total_savings_potential=total_savings,
            average_confidence=avg_confidence,
            generated_at=generated_at
        )

    async def _analyze_bill_payment_timing(
        self, bill: Liability, account_ids: Optional[List[int]]
    ) -> Optional[BillPaymentTimingRecommendation]:
        """
        Analyze payment patterns for a bill and generate timing recommendations.
        
        Args:
            bill: Liability to analyze
            account_ids: Optional list of account IDs to filter by
            
        Returns:
            Recommendation for optimal payment timing or None if no recommendation
        """
        # Get payment patterns
        pattern_analysis: Optional[PaymentPatternAnalysis] = (
            await self.pattern_service.analyze_bill_payments(bill.id)
        )
        
        if not pattern_analysis:
            return None

        # Get affected accounts
        affected_accounts = await self._get_affected_accounts(bill.id, account_ids)
        
        if not affected_accounts:
            return None

        # Analyze optimal payment timing
        optimal_date, confidence, reason = await self._calculate_optimal_payment_date(
            bill, pattern_analysis, affected_accounts
        )
        
        if not optimal_date:
            return None

        # Calculate impact metrics
        impact = await self._calculate_impact_metrics(
            bill, optimal_date, affected_accounts
        )

        # Create recommendation with proper timezone handling
        current_due_date = ensure_utc(bill.due_date)
        recommended_date = ensure_utc(optimal_date)
        
        return BillPaymentTimingRecommendation(
            bill_id=bill.id,
            current_due_date=current_due_date,
            recommended_date=recommended_date,
            reason=reason,
            confidence=confidence,
            impact=impact,
            historical_pattern_strength=pattern_analysis.confidence_score,
            affected_accounts=[acc.id for acc in affected_accounts],
            created_at=utc_now()
        )

    async def _get_affected_accounts(
        self, bill_id: int, account_ids: Optional[List[int]]
    ) -> List[Account]:
        """
        Get accounts affected by a bill's payments.
        
        Args:
            bill_id: ID of the bill to analyze
            account_ids: Optional list of account IDs to filter by
            
        Returns:
            List of affected accounts
        """
        # Get repositories
        payment_repo = await self._get_repository(PaymentRepository)
        account_repo = await self._get_repository(AccountRepository)
        
        # Get recent payments for the bill with sources loaded
        payments = await payment_repo.get_recent_bill_payments(bill_id, limit=5)
        
        # Get unique account IDs from payment sources
        account_ids_set = set()
        for payment in payments:
            for source in payment.sources:
                if not account_ids or source.account_id in account_ids:
                    account_ids_set.add(source.account_id)
        
        # Get account details
        if not account_ids_set:
            return []
        
        # Get accounts with those IDs
        accounts = []
        for account_id in account_ids_set:
            account = await account_repo.get(account_id)
            if account:
                accounts.append(account)
                
        return accounts

    async def _calculate_optimal_payment_date(
        self,
        bill: Liability,
        pattern_analysis: PaymentPatternAnalysis,
        accounts: List[Account],
    ) -> Tuple[Optional[date], Optional[ConfidenceLevel], str]:
        """
        Calculate the optimal payment date based on patterns and account status.
        
        Args:
            bill: Liability to analyze
            pattern_analysis: Analysis of payment patterns
            accounts: Affected accounts
            
        Returns:
            Tuple of (optimal date, confidence level, reason)
        """
        if pattern_analysis.pattern_type == PatternType.REGULAR:
            return await self._analyze_regular_pattern(bill, pattern_analysis, accounts)
        elif pattern_analysis.pattern_type == PatternType.IRREGULAR:
            return await self._analyze_irregular_pattern(
                bill, pattern_analysis, accounts
            )
        elif pattern_analysis.pattern_type == PatternType.SEASONAL:
            return await self._analyze_seasonal_pattern(
                bill, pattern_analysis, accounts
            )

        # Default case for UNKNOWN pattern type
        return None, None, ""

    async def _calculate_impact_metrics(
        self,
        bill: Liability,
        recommended_date: date,
        accounts: List[Account],
    ) -> ImpactMetrics:
        """
        Calculate the impact of the recommendation on accounts.
        
        Args:
            bill: The liability being analyzed
            recommended_date: Recommended payment date
            accounts: List of affected accounts
            
        Returns:
            Impact metrics for the recommendation
        """
        # Initialize impact metrics
        balance_impact = Decimal("0")
        credit_impact = None
        savings = Decimal("0")

        # Convert dates to ensure consistent types
        current_due = ensure_utc(bill.due_date).date()
        recommended = ensure_utc(recommended_date).date() if isinstance(recommended_date, datetime) else recommended_date

        # Calculate impacts based on cashflow projections
        current_metrics = await self.metrics_service.get_metrics_for_date(
            current_due
        )
        recommended_metrics = await self.metrics_service.get_metrics_for_date(
            recommended
        )

        if recommended_metrics and current_metrics:
            balance_impact = (
                recommended_metrics.projected_balance
                - current_metrics.projected_balance
            )

            # Calculate potential savings
            if balance_impact > 0:
                savings = balance_impact * Decimal("0.1")  # Estimated savings

            # Calculate credit utilization impact for credit accounts
            credit_accounts = [acc for acc in accounts if acc.account_type == "credit"]
            if credit_accounts:
                current_util = self._calculate_credit_utilization(credit_accounts)
                recommended_util = self._calculate_credit_utilization(
                    credit_accounts, balance_impact
                )
                credit_impact = recommended_util - current_util

        # Calculate risk score (0-100)
        risk_score = self._calculate_risk_score(balance_impact, credit_impact, accounts)

        return ImpactMetrics(
            balance_impact=balance_impact,
            credit_utilization_impact=credit_impact,
            risk_score=risk_score,
            savings_potential=savings if savings > 0 else None,
        )

    def _calculate_credit_utilization(
        self,
        accounts: List[Account],
        balance_adjustment: Decimal = Decimal("0"),
    ) -> Decimal:
        """
        Calculate the weighted average credit utilization across accounts.
        
        Args:
            accounts: List of credit accounts
            balance_adjustment: Optional balance adjustment amount
            
        Returns:
            Weighted average credit utilization percentage
        """
        total_limit = sum(acc.credit_limit for acc in accounts if acc.credit_limit)
        if not total_limit:
            return Decimal("0")

        total_used = (
            sum(abs(acc.available_balance) for acc in accounts) + balance_adjustment
        )

        return (total_used / total_limit) * Decimal("100")

    def _calculate_risk_score(
        self,
        balance_impact: Decimal,
        credit_impact: Optional[Decimal],
        accounts: List[Account],  # Keep this for potential future use and API compatibility
    ) -> Decimal:
        """
        Calculate a risk score for the recommendation.
        
        Args:
            balance_impact: Impact on account balance
            credit_impact: Impact on credit utilization (if applicable)
            accounts: Affected accounts
            
        Returns:
            Risk score from 0-100 (lower is less risky)
        """
        score = Decimal("50")  # Base score

        # Adjust for balance impact
        if balance_impact > 0:
            score += Decimal("20")
        elif balance_impact < 0:
            score -= Decimal("20")

        # Adjust for credit utilization impact
        if credit_impact:
            if credit_impact < 0:  # Decreased utilization is good
                score += Decimal("15")
            else:
                score -= Decimal("15")

        # Ensure score stays within 0-100
        return min(max(score, Decimal("0")), Decimal("100"))

    def _confidence_to_decimal(self, confidence: ConfidenceLevel) -> Decimal:
        """
        Convert confidence level to decimal score.
        
        Args:
            confidence: Confidence level enum value
            
        Returns:
            Decimal score representing confidence level
        """
        return {
            ConfidenceLevel.HIGH: Decimal("1.0"),
            ConfidenceLevel.MEDIUM: Decimal("0.6"),
            ConfidenceLevel.LOW: Decimal("0.3"),
        }[confidence]

    async def _analyze_regular_pattern(
        self,
        bill: Liability,
        pattern_analysis: PaymentPatternAnalysis,
        accounts: List[Account],  # Keep this for potential future use and API compatibility
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """
        Analyze regular payment patterns for optimal timing.
        
        Args:
            bill: Liability to analyze
            pattern_analysis: Analysis of payment patterns
            accounts: Affected accounts
            
        Returns:
            Tuple of (optimal date, confidence level, reason)
        """
        # For regular patterns, use the average days before due date
        days_before = int(pattern_analysis.frequency_metrics.average_days_between)
        optimal_date = bill.due_date - timedelta(days=days_before)

        # Set confidence based on standard deviation and pattern confidence
        if (
            pattern_analysis.frequency_metrics.std_dev_days <= 1
        ):  # Very consistent (±1 day)
            confidence = ConfidenceLevel.HIGH
            reason = f"Highly consistent payment pattern {days_before} days before due date (±{pattern_analysis.frequency_metrics.std_dev_days:.1f} days)"
        elif (
            pattern_analysis.frequency_metrics.std_dev_days <= 3
        ):  # Fairly consistent (±3 days)
            confidence = ConfidenceLevel.MEDIUM
            reason = f"Consistent payment pattern {days_before} days before due date (±{pattern_analysis.frequency_metrics.std_dev_days:.1f} days)"
        else:  # More variable
            confidence = ConfidenceLevel.LOW
            reason = f"Variable payment pattern averaging {days_before} days before due date (±{pattern_analysis.frequency_metrics.std_dev_days:.1f} days)"

        # Adjust confidence based on pattern's confidence score
        if pattern_analysis.confidence_score < 0.5:
            confidence = ConfidenceLevel.LOW
            reason += " (Limited historical data)"

        return optimal_date, confidence, reason

    async def _analyze_irregular_pattern(
        self,
        bill: Liability,
        pattern_analysis: PaymentPatternAnalysis,  # Keep this for potential future use and API compatibility
        accounts: List[Account],  # Keep this for potential future use and API compatibility
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """
        Analyze irregular payment patterns for optimal timing.
        
        Args:
            bill: Liability to analyze
            pattern_analysis: Analysis of payment patterns
            accounts: Affected accounts
            
        Returns:
            Tuple of (optimal date, confidence level, reason)
        """
        # For irregular patterns, focus on cashflow optimization
        best_date = None
        best_balance = Decimal("-999999")

        # Check different potential dates
        for days in range(1, 15):  # Check up to 2 weeks before due date
            check_date = bill.due_date - timedelta(days=days)
            metrics = await self.metrics_service.get_metrics_for_date(check_date)
            if metrics and metrics.projected_balance > best_balance:
                best_date = check_date
                best_balance = metrics.projected_balance

        if best_date:
            return (
                best_date,
                ConfidenceLevel.MEDIUM,
                "Optimized for best cashflow position",
            )
        return None, ConfidenceLevel.LOW, "Unable to determine optimal date"

    async def _analyze_seasonal_pattern(
        self,
        bill: Liability,
        pattern_analysis: PaymentPatternAnalysis,
        accounts: List[Account],  # Keep this for potential future use and API compatibility
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """
        Analyze seasonal payment patterns for optimal timing.
        
        Args:
            bill: Liability to analyze
            pattern_analysis: Analysis of payment patterns
            accounts: Affected accounts
            
        Returns:
            Tuple of (optimal date, confidence level, reason)
        """
        # For seasonal patterns, consider the current season's typical behavior
        current_month = utc_now().month
        if not pattern_analysis.seasonal_metrics:
            return None, ConfidenceLevel.LOW, "Insufficient seasonal data"

        season_data = pattern_analysis.seasonal_metrics.get((current_month - 1) // 3)

        if season_data:
            days_before = int(season_data.avg_days_before_due)
            optimal_date = bill.due_date - timedelta(days=days_before)
            return (
                optimal_date,
                ConfidenceLevel.MEDIUM,
                f"Seasonal pattern suggests {days_before} days before due date",
            )
        return None, ConfidenceLevel.LOW, "No seasonal pattern for current season"
