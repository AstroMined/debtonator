from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.schemas.recommendations import (
    BillPaymentTimingRecommendation,
    ConfidenceLevel,
    ImpactMetrics,
    RecommendationResponse,
)
from src.schemas.payment_patterns import PatternType
from src.services.payment_patterns import PaymentPatternService
from src.services.cashflow import CashflowService


class RecommendationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pattern_service = PaymentPatternService(session)
        self.cashflow_service = CashflowService(session)

    async def get_bill_payment_recommendations(
        self, account_ids: Optional[List[int]] = None
    ) -> RecommendationResponse:
        """Generate bill payment timing recommendations based on historical patterns."""
        recommendations: List[BillPaymentTimingRecommendation] = []
        total_savings = Decimal("0")
        confidence_sum = Decimal("0")

        # Get active bills
        stmt = select(Liability).where(Liability.active == True)
        result = await self.session.execute(stmt)
        bills = result.scalars().all()

        for bill in bills:
            recommendation = await self._analyze_bill_payment_timing(
                bill, account_ids
            )
            if recommendation:
                recommendations.append(recommendation)
                if recommendation.impact.savings_potential:
                    total_savings += recommendation.impact.savings_potential
                confidence_sum += self._confidence_to_decimal(
                    recommendation.confidence
                )

        avg_confidence = (
            confidence_sum / len(recommendations)
            if recommendations
            else Decimal("0")
        )

        return RecommendationResponse(
            recommendations=recommendations,
            total_savings_potential=total_savings,
            average_confidence=avg_confidence,
        )

    async def _analyze_bill_payment_timing(
        self, bill: Liability, account_ids: Optional[List[int]]
    ) -> Optional[BillPaymentTimingRecommendation]:
        """Analyze payment patterns for a bill and generate timing recommendations."""
        # Get payment patterns
        patterns = await self.pattern_service.analyze_bill_payments(bill.id)
        print(f"\nAnalyzing bill {bill.id} with patterns: {patterns}")
        if not patterns:
            print("No patterns found")
            return None

        # Get affected accounts
        affected_accounts = await self._get_affected_accounts(
            bill.id, account_ids
        )
        print(f"Found affected accounts: {affected_accounts}")
        if not affected_accounts:
            print("No affected accounts found")
            return None

        # Analyze optimal payment timing
        optimal_date, confidence, reason = await self._calculate_optimal_payment_date(
            bill, patterns, affected_accounts
        )
        print(f"Optimal payment date: {optimal_date}, confidence: {confidence}, reason: {reason}")
        if not optimal_date:
            print("No optimal date found")
            return None

        # Calculate impact metrics
        impact = await self._calculate_impact_metrics(
            bill, optimal_date, affected_accounts
        )

        return BillPaymentTimingRecommendation(
            bill_id=bill.id,
            current_due_date=bill.due_date,
            recommended_date=optimal_date,
            reason=reason,
            confidence=confidence,
            impact=impact,
            historical_pattern_strength=patterns.confidence_score,
            affected_accounts=[acc.id for acc in affected_accounts],
        )

    async def _get_affected_accounts(
        self, bill_id: int, account_ids: Optional[List[int]]
    ) -> List[Account]:
        """Get accounts affected by a bill's payments."""
        # Get recent payments for the bill
        stmt = (
            select(Payment)
            .options(selectinload(Payment.sources))
            .where(Payment.liability_id == bill_id)
            .order_by(Payment.payment_date.desc())
            .limit(5)
        )
        result = await self.session.execute(stmt)
        payments = result.scalars().all()

        # Get unique account IDs from payment sources
        account_ids_set = set()
        for payment in payments:
            for source in payment.sources:
                if (
                    not account_ids
                    or source.account_id in account_ids
                ):
                    account_ids_set.add(source.account_id)

        # Get account details
        if not account_ids_set:
            return []

        stmt = select(Account).where(Account.id.in_(account_ids_set))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def _calculate_optimal_payment_date(
        self,
        bill: Liability,
        patterns: any,  # PaymentPatternResponse type
        accounts: List[Account],
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """Calculate the optimal payment date based on patterns and account status."""
        if patterns.pattern_type == PatternType.REGULAR:
            return await self._analyze_regular_pattern(
                bill, patterns, accounts
            )
        elif patterns.pattern_type == PatternType.IRREGULAR:
            return await self._analyze_irregular_pattern(
                bill, patterns, accounts
            )
        elif patterns.pattern_type == PatternType.SEASONAL:
            return await self._analyze_seasonal_pattern(
                bill, patterns, accounts
            )
        
        # Default case for UNKNOWN pattern type
        return None, None, ""

    async def _calculate_impact_metrics(
        self,
        bill: Liability,
        recommended_date: date,
        accounts: List[Account],
    ) -> ImpactMetrics:
        """Calculate the impact of the recommendation on accounts."""
        # Initialize impact metrics
        balance_impact = Decimal("0")
        credit_impact = None
        savings = Decimal("0")

        # Calculate impacts based on cashflow projections
        current_metrics = await self.cashflow_service.get_metrics_for_date(
            bill.due_date
        )
        recommended_metrics = await self.cashflow_service.get_metrics_for_date(
            recommended_date
        )

        if recommended_metrics and current_metrics:
            balance_impact = (
                recommended_metrics.projected_balance - current_metrics.projected_balance
            )
            
            # Calculate potential savings
            if balance_impact > 0:
                savings = balance_impact * Decimal("0.1")  # Estimated savings

            # Calculate credit utilization impact for credit accounts
            credit_accounts = [
                acc for acc in accounts if acc.type == "credit"
            ]
            if credit_accounts:
                current_util = self._calculate_credit_utilization(
                    credit_accounts
                )
                recommended_util = self._calculate_credit_utilization(
                    credit_accounts, balance_impact
                )
                credit_impact = recommended_util - current_util

        # Calculate risk score (0-100)
        risk_score = self._calculate_risk_score(
            balance_impact, credit_impact, accounts
        )

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
        """Calculate the weighted average credit utilization across accounts."""
        total_limit = sum(
            acc.total_limit for acc in accounts if acc.total_limit
        )
        if not total_limit:
            return Decimal("0")

        total_used = sum(
            abs(acc.available_balance) for acc in accounts
        ) + balance_adjustment

        return (total_used / total_limit) * Decimal("100")

    def _calculate_risk_score(
        self,
        balance_impact: Decimal,
        credit_impact: Optional[Decimal],
        accounts: List[Account],
    ) -> Decimal:
        """Calculate a risk score for the recommendation."""
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
        """Convert confidence level to decimal score."""
        return {
            ConfidenceLevel.HIGH: Decimal("1.0"),
            ConfidenceLevel.MEDIUM: Decimal("0.6"),
            ConfidenceLevel.LOW: Decimal("0.3"),
        }[confidence]

    async def _analyze_regular_pattern(
        self,
        bill: Liability,
        patterns: any,
        accounts: List[Account],
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """Analyze regular payment patterns for optimal timing."""
        # For regular patterns, use the average days before due date
        days_before = int(patterns.frequency_metrics.average_days_between)
        optimal_date = bill.due_date - timedelta(days=days_before)
        
        # Set confidence based on standard deviation and pattern confidence
        if patterns.frequency_metrics.std_dev_days <= 1:  # Very consistent (±1 day)
            confidence = ConfidenceLevel.HIGH
            reason = f"Highly consistent payment pattern {days_before} days before due date (±{patterns.frequency_metrics.std_dev_days:.1f} days)"
        elif patterns.frequency_metrics.std_dev_days <= 3:  # Fairly consistent (±3 days)
            confidence = ConfidenceLevel.MEDIUM
            reason = f"Consistent payment pattern {days_before} days before due date (±{patterns.frequency_metrics.std_dev_days:.1f} days)"
        else:  # More variable
            confidence = ConfidenceLevel.LOW
            reason = f"Variable payment pattern averaging {days_before} days before due date (±{patterns.frequency_metrics.std_dev_days:.1f} days)"
        
        # Adjust confidence based on pattern's confidence score
        if patterns.confidence_score < 0.5:
            confidence = ConfidenceLevel.LOW
            reason += " (Limited historical data)"
        
        return optimal_date, confidence, reason

    async def _analyze_irregular_pattern(
        self,
        bill: Liability,
        patterns: any,
        accounts: List[Account],
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """Analyze irregular payment patterns for optimal timing."""
        # For irregular patterns, focus on cashflow optimization
        best_date = None
        best_balance = Decimal("-999999")
        
        # Check different potential dates
        for days in range(1, 15):  # Check up to 2 weeks before due date
            check_date = bill.due_date - timedelta(days=days)
            metrics = await self.cashflow_service.get_metrics_for_date(
                check_date
            )
            if metrics and metrics.projected_balance > best_balance:
                best_date = check_date
                best_balance = metrics.projected_balance

        if best_date:
            return (
                best_date,
                ConfidenceLevel.MEDIUM,
                "Optimized for best cashflow position",
            )
        return None, None, ""

    async def _analyze_seasonal_pattern(
        self,
        bill: Liability,
        patterns: any,
        accounts: List[Account],
    ) -> Tuple[Optional[date], ConfidenceLevel, str]:
        """Analyze seasonal payment patterns for optimal timing."""
        # For seasonal patterns, consider the current season's typical behavior
        current_month = datetime.now().month
        if not patterns.seasonal_metrics:
            return None, None, ""

        season_data = patterns.seasonal_metrics.get((current_month - 1) // 3)
        
        if season_data:
            days_before = int(season_data.avg_days_before_due)
            optimal_date = bill.due_date - timedelta(days=days_before)
            return (
                optimal_date,
                ConfidenceLevel.MEDIUM,
                f"Seasonal pattern suggests {days_before} days before due date",
            )
        return None, None, ""
