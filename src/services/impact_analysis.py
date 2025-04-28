from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.schemas.impact_analysis import (
    AccountImpact,
    CashflowImpact,
    RiskFactor,
    SplitImpactAnalysis,
    SplitImpactRequest,
)
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import ensure_utc, naive_utc_from_date
from src.utils.decimal_precision import DecimalPrecision


class ImpactAnalysisService(BaseService):
    """
    Service for analyzing financial impact of proposed actions.

    This service provides analysis of how financial decisions such as
    bill splits would impact accounts, cashflow, and overall financial health.

    Attributes:
        _session: SQLAlchemy async session
        _feature_flag_service: Optional feature flag service
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the impact analysis service.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def analyze_split_impact(
        self, request: SplitImpactRequest
    ) -> SplitImpactAnalysis:
        """
        Analyze the impact of proposed bill splits on accounts and cashflow.

        Args:
            request: Split impact request containing split configuration

        Returns:
            Comprehensive analysis of bill split impacts

        Raises:
            ValueError: If the liability is not found
        """
        # Get the liability and validate it exists
        liability = await self._get_liability(request.liability_id)
        if not liability:
            raise ValueError(f"Liability {request.liability_id} not found")

        # Get all affected accounts
        account_ids = [split["account_id"] for split in request.splits]
        accounts = await self._get_accounts(account_ids)

        # Calculate account impacts
        account_impacts = await self._calculate_account_impacts(
            accounts, request.splits
        )

        # Calculate cashflow impacts
        cashflow_impacts = await self._calculate_cashflow_impacts(
            accounts, request.splits, request.analysis_period_days
        )

        # Analyze risk factors
        risk_factors = await self._analyze_risk_factors(
            accounts, request.splits, cashflow_impacts
        )

        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(risk_factors)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            account_impacts, cashflow_impacts, risk_factors
        )

        # Calculate total amount with proper precision
        total_amount = DecimalPrecision.round_for_calculation(
            sum(
                DecimalPrecision.round_for_calculation(Decimal(str(split["amount"])))
                for split in request.splits
            )
        )

        return SplitImpactAnalysis(
            total_amount=total_amount,
            account_impacts=account_impacts,
            cashflow_impacts=cashflow_impacts,
            risk_factors=risk_factors,
            overall_risk_score=overall_risk,
            recommendations=recommendations,
        )

    async def _get_liability(self, liability_id: int) -> Optional[Liability]:
        """
        Retrieve a liability by ID.

        Args:
            liability_id: ID of the liability to retrieve

        Returns:
            Liability object if found, None otherwise
        """
        # Get repository
        repo = await self._get_repository(LiabilityRepository)

        # Use repository to get liability
        return await repo.get(liability_id)

    async def _get_accounts(self, account_ids: List[int]) -> List[Account]:
        """
        Retrieve multiple accounts by their IDs.

        Args:
            account_ids: List of account IDs to retrieve

        Returns:
            List of account objects matching the provided IDs
        """
        # Get repository
        repo = await self._get_repository(AccountRepository)

        # Initialize results list
        accounts = []

        # Fetch each account individually to handle cases where some IDs might not exist
        for account_id in account_ids:
            account = await repo.get(account_id)
            if account:
                accounts.append(account)

        return accounts

    async def _calculate_account_impacts(
        self, accounts: List[Account], splits: List[dict]
    ) -> List[AccountImpact]:
        """Calculate the impact on each account involved in the splits."""
        impacts = []

        for account in accounts:
            # Find the split amount for this account
            split_amount = Decimal("0")
            for split in splits:
                if split["account_id"] == account.id:
                    split_amount = DecimalPrecision.round_for_calculation(
                        Decimal(str(split["amount"]))
                    )
                    break

            # Calculate projected balance with 4 decimal precision
            available_balance = DecimalPrecision.round_for_calculation(
                account.available_balance
            )
            projected_balance = DecimalPrecision.round_for_calculation(
                available_balance - split_amount
            )

            # Calculate credit utilization for credit accounts
            current_utilization = None
            projected_utilization = None
            if account.account_type == "credit" and account.total_limit:
                total_limit = DecimalPrecision.round_for_calculation(
                    account.total_limit
                )

                # Calculate with 4 decimal places for internal precision
                current_utilization = DecimalPrecision.round_for_calculation(
                    (abs(available_balance) / total_limit) * Decimal("100")
                )

                projected_utilization = DecimalPrecision.round_for_calculation(
                    (abs(projected_balance) / total_limit) * Decimal("100")
                )

            # Calculate risk score for this account
            risk_score = self._calculate_account_risk_score(
                account, split_amount, projected_balance, projected_utilization
            )

            impacts.append(
                AccountImpact(
                    account_id=account.id,
                    current_balance=account.available_balance,
                    projected_balance=projected_balance,
                    current_credit_utilization=current_utilization,
                    projected_credit_utilization=projected_utilization,
                    risk_score=risk_score,
                )
            )

        return impacts

    async def _calculate_cashflow_impacts(
        self, accounts: List[Account], splits: List[dict], analysis_period_days: int
    ) -> List[CashflowImpact]:
        """
        Calculate cashflow impacts over the analysis period.

        Args:
            accounts: List of affected accounts
            splits: List of split configurations
            analysis_period_days: Number of days to analyze

        Returns:
            List of cashflow impacts for different time periods
        """
        impacts = []
        today = date.today()

        # Get all upcoming bills in the analysis period
        end_date = today + timedelta(days=analysis_period_days)
        upcoming_bills = await self._get_upcoming_bills(today, end_date)

        # Calculate impacts for each month in the period
        current_date = today
        while current_date <= end_date:
            # Sum bill amounts with proper precision
            month_bills = DecimalPrecision.round_for_calculation(
                sum(
                    DecimalPrecision.round_for_calculation(bill.amount)
                    for bill in upcoming_bills
                    if bill.due_date.month == current_date.month
                )
            )

            # Calculate available funds across all accounts with proper precision
            available_funds = DecimalPrecision.round_for_calculation(
                sum(
                    DecimalPrecision.round_for_calculation(account.available_balance)
                    for account in accounts
                )
            )

            # Calculate projected deficit
            projected_deficit = None
            if available_funds < month_bills:
                projected_deficit = DecimalPrecision.round_for_calculation(
                    month_bills - available_funds
                )

            # Use ensure_utc to ensure timezone-aware datetime
            impact_date = ensure_utc(
                datetime.combine(current_date, datetime.min.time())
            )
            impacts.append(
                CashflowImpact(
                    date=impact_date,
                    total_bills=month_bills,
                    available_funds=available_funds,
                    projected_deficit=projected_deficit,
                )
            )

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return impacts

    async def _get_upcoming_bills(
        self, start_date: date, end_date: date
    ) -> List[Liability]:
        """
        Get all upcoming bills in the given date range.

        Args:
            start_date: Start date for the range (inclusive)
            end_date: End date for the range (inclusive)

        Returns:
            List of liabilities due in the specified date range
        """
        # Get repository
        repo = await self._get_repository(LiabilityRepository)

        # Convert dates to naive UTC datetimes for database query
        start_datetime = naive_utc_from_date(
            start_date.year, start_date.month, start_date.day
        )
        end_datetime = naive_utc_from_date(end_date.year, end_date.month, end_date.day)

        # Use repository to get liabilities in date range
        return await repo.get_due_in_range(start_datetime, end_datetime)

    async def _analyze_risk_factors(
        self,
        accounts: List[Account],
        splits: List[dict],
        cashflow_impacts: List[CashflowImpact],
    ) -> List[RiskFactor]:
        """
        Analyze various risk factors for the proposed splits.

        Args:
            accounts: List of affected accounts
            splits: List of split configurations
            cashflow_impacts: Calculated cashflow impacts

        Returns:
            List of identified risk factors
        """
        risk_factors = []

        # Check for high credit utilization
        for account in accounts:
            if account.account_type == "credit" and account.credit_limit:
                # Calculate split amount with 4 decimal precision
                split_amount = DecimalPrecision.round_for_calculation(
                    sum(
                        DecimalPrecision.round_for_calculation(
                            Decimal(str(split["amount"]))
                        )
                        for split in splits
                        if split["account_id"] == account.id
                    )
                )

                # Use 4 decimal precision for all calculations
                available_balance = DecimalPrecision.round_for_calculation(
                    account.available_balance
                )
                total_limit = DecimalPrecision.round_for_calculation(
                    account.credit_limit
                )

                projected_balance = DecimalPrecision.round_for_calculation(
                    available_balance - split_amount
                )
                utilization = DecimalPrecision.round_for_calculation(
                    (abs(projected_balance) / total_limit) * Decimal("100")
                )

                if utilization > Decimal("80"):
                    # Calculate severity based on how much it exceeds 80%
                    # and weight it more heavily for higher utilization
                    excess = DecimalPrecision.round_for_calculation(
                        utilization - Decimal("80")
                    )
                    severity_decimal = DecimalPrecision.round_for_calculation(
                        excess * Decimal("7.5")
                    )
                    severity = min(
                        int(severity_decimal), 100
                    )  # 7.5 means 90% utilization = 75 severity

                    if utilization > Decimal("90"):
                        severity = min(
                            severity + 30, 100
                        )  # Extra penalty for >90% utilization

                    risk_factors.append(
                        RiskFactor(
                            name="High Credit Utilization",
                            severity=severity,
                            description=f"Credit utilization for account {account.id} will exceed 80%",
                        )
                    )

        # Check for low account balances
        for account in accounts:
            if account.account_type == "checking":
                # Calculate split amount and projected balance with 4 decimal precision
                split_amount = DecimalPrecision.round_for_calculation(
                    sum(
                        DecimalPrecision.round_for_calculation(
                            Decimal(str(split["amount"]))
                        )
                        for split in splits
                        if split["account_id"] == account.id
                    )
                )

                available_balance = DecimalPrecision.round_for_calculation(
                    account.available_balance
                )
                projected_balance = DecimalPrecision.round_for_calculation(
                    available_balance - split_amount
                )

                if projected_balance < Decimal("1000"):
                    # Calculate severity with 4 decimal precision
                    severity_calc = DecimalPrecision.round_for_calculation(
                        (Decimal("1000") - projected_balance) / Decimal("10")
                    )
                    severity = min(int(severity_calc), 100)

                    risk_factors.append(
                        RiskFactor(
                            name="Low Account Balance",
                            severity=severity,
                            description=f"Account {account.id} balance will fall below $1,000",
                        )
                    )

        # Check for cashflow deficits
        for impact in cashflow_impacts:
            if impact.projected_deficit:
                # Calculate severity with 4 decimal precision
                deficit = DecimalPrecision.round_for_calculation(
                    impact.projected_deficit
                )
                severity_calc = DecimalPrecision.round_for_calculation(
                    deficit / Decimal("100")
                )
                severity = min(int(severity_calc), 100)

                risk_factors.append(
                    RiskFactor(
                        name="Cashflow Deficit",
                        severity=severity,
                        description=f"Projected deficit of ${deficit} on {impact.date}",
                    )
                )

        return risk_factors

    def _calculate_account_risk_score(
        self,
        account: Account,
        split_amount: Decimal,
        projected_balance: Decimal,
        projected_utilization: Optional[Decimal],
    ) -> int:
        """Calculate a risk score for a specific account."""
        risk_score = 0

        if account.account_type == "credit":
            # Higher risk for high credit utilization
            if projected_utilization:
                util = DecimalPrecision.round_for_calculation(projected_utilization)
                if util > Decimal("90"):
                    risk_score += 50
                elif util > Decimal("80"):
                    risk_score += 40
                elif util > Decimal("70"):
                    risk_score += 30
        else:
            # Higher risk for low checking balances
            bal = DecimalPrecision.round_for_calculation(projected_balance)
            if bal < Decimal("500"):
                risk_score += 50
            elif bal < Decimal("1000"):
                risk_score += 40
            elif bal < Decimal("2000"):
                risk_score += 30

        # Risk based on split amount relative to current balance
        available_balance = DecimalPrecision.round_for_calculation(
            abs(account.available_balance)
        )
        split = DecimalPrecision.round_for_calculation(split_amount)

        # Avoid division by zero
        if available_balance > Decimal("0"):
            balance_ratio = DecimalPrecision.round_for_calculation(
                split / available_balance
            )

            if balance_ratio > Decimal("0.5"):
                risk_score += 40
            elif balance_ratio > Decimal("0.3"):
                risk_score += 30
            elif balance_ratio > Decimal("0.1"):
                risk_score += 20

        return min(risk_score, 100)

    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> int:
        """Calculate overall risk score based on individual risk factors."""
        if not risk_factors:
            return 0

        # Weight higher severity risks more heavily
        weighted_sum = DecimalPrecision.round_for_calculation(
            sum(
                DecimalPrecision.round_for_calculation(
                    Decimal(str(factor.severity)) * Decimal("1.5")
                    if factor.severity > 70
                    else Decimal(str(factor.severity))
                )
                for factor in risk_factors
            )
        )

        risk_count = Decimal(str(len(risk_factors)))
        avg_risk = DecimalPrecision.round_for_calculation(weighted_sum / risk_count)

        return min(int(avg_risk), 100)

    def _generate_recommendations(
        self,
        account_impacts: List[AccountImpact],
        cashflow_impacts: List[CashflowImpact],
        risk_factors: List[RiskFactor],
    ) -> List[str]:
        """Generate recommendations based on the analysis results."""
        recommendations = []

        # Check for high-risk accounts
        for impact in account_impacts:
            if impact.risk_score > 70:
                recommendations.append(
                    f"Consider reducing the split amount for account {impact.account_id} "
                    f"to lower the risk score"
                )

            if (
                impact.projected_credit_utilization
                and impact.projected_credit_utilization > Decimal("80")
            ):
                recommendations.append(
                    f"Credit utilization for account {impact.account_id} will be high. "
                    f"Consider using a different account if possible."
                )

        # Check for cashflow issues
        for impact in cashflow_impacts:
            if impact.projected_deficit:
                recommendations.append(
                    f"Projected deficit of ${impact.projected_deficit} on {impact.date}. "
                    f"Consider adjusting payment timing or finding additional income sources."
                )

        # Add general recommendations based on risk factors
        if any(factor.severity > 80 for factor in risk_factors):
            recommendations.append(
                "Multiple high-severity risk factors detected. "
                "Consider revising the split allocation."
            )

        return recommendations
