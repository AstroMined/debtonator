from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.schemas.impact_analysis import (
    AccountImpact,
    CashflowImpact,
    RiskFactor,
    SplitImpactAnalysis,
    SplitImpactRequest
)

class ImpactAnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_split_impact(self, request: SplitImpactRequest) -> SplitImpactAnalysis:
        """Analyze the impact of proposed bill splits on accounts and cashflow."""
        # Get the liability and validate it exists
        liability = await self._get_liability(request.liability_id)
        if not liability:
            raise ValueError(f"Liability {request.liability_id} not found")

        # Get all affected accounts
        account_ids = [split["account_id"] for split in request.splits]
        accounts = await self._get_accounts(account_ids)
        
        # Calculate account impacts
        account_impacts = await self._calculate_account_impacts(accounts, request.splits)
        
        # Calculate cashflow impacts
        cashflow_impacts = await self._calculate_cashflow_impacts(
            accounts,
            request.splits,
            request.analysis_period_days
        )
        
        # Analyze risk factors
        risk_factors = await self._analyze_risk_factors(
            accounts,
            request.splits,
            cashflow_impacts
        )
        
        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            account_impacts,
            cashflow_impacts,
            risk_factors
        )
        
        return SplitImpactAnalysis(
            total_amount=sum(Decimal(str(split["amount"])) for split in request.splits),
            account_impacts=account_impacts,
            cashflow_impacts=cashflow_impacts,
            risk_factors=risk_factors,
            overall_risk_score=overall_risk,
            recommendations=recommendations
        )

    async def _get_liability(self, liability_id: int) -> Optional[Liability]:
        """Retrieve a liability by ID."""
        result = await self.session.execute(
            select(Liability).where(Liability.id == liability_id)
        )
        return result.scalar_one_or_none()

    async def _get_accounts(self, account_ids: List[int]) -> List[Account]:
        """Retrieve multiple accounts by their IDs."""
        result = await self.session.execute(
            select(Account).where(Account.id.in_(account_ids))
        )
        return list(result.scalars().all())

    async def _calculate_account_impacts(
        self,
        accounts: List[Account],
        splits: List[dict]
    ) -> List[AccountImpact]:
        """Calculate the impact on each account involved in the splits."""
        impacts = []
        
        for account in accounts:
            # Find the split amount for this account
            split_amount = Decimal('0')
            for split in splits:
                if split["account_id"] == account.id:
                    split_amount = Decimal(str(split["amount"]))
                    break
            
            # Calculate projected balance
            projected_balance = account.available_balance - split_amount
            
            # Calculate credit utilization for credit accounts
            current_utilization = None
            projected_utilization = None
            if account.type == "credit" and account.total_limit:
                current_utilization = (
                    abs(account.available_balance) / account.total_limit * 100
                )
                projected_utilization = (
                    abs(projected_balance) / account.total_limit * 100
                )
            
            # Calculate risk score for this account
            risk_score = self._calculate_account_risk_score(
                account,
                split_amount,
                projected_balance,
                projected_utilization
            )
            
            impacts.append(AccountImpact(
                account_id=account.id,
                current_balance=account.available_balance,
                projected_balance=projected_balance,
                current_credit_utilization=current_utilization,
                projected_credit_utilization=projected_utilization,
                risk_score=risk_score
            ))
        
        return impacts

    async def _calculate_cashflow_impacts(
        self,
        accounts: List[Account],
        splits: List[dict],
        analysis_period_days: int
    ) -> List[CashflowImpact]:
        """Calculate cashflow impacts over the analysis period."""
        impacts = []
        today = date.today()
        
        # Get all upcoming bills in the analysis period
        end_date = today + timedelta(days=analysis_period_days)
        upcoming_bills = await self._get_upcoming_bills(today, end_date)
        
        # Calculate impacts for each month in the period
        current_date = today
        while current_date <= end_date:
            month_bills = sum(
                bill.amount for bill in upcoming_bills
                if bill.due_date.month == current_date.month
            )
            
            # Calculate available funds across all accounts
            available_funds = sum(account.available_balance for account in accounts)
            
            # Calculate projected deficit
            projected_deficit = None
            if available_funds < month_bills:
                projected_deficit = month_bills - available_funds
            
            impacts.append(CashflowImpact(
                date=current_date,
                total_bills=month_bills,
                available_funds=available_funds,
                projected_deficit=projected_deficit
            ))
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return impacts

    async def _get_upcoming_bills(
        self,
        start_date: date,
        end_date: date
    ) -> List[Liability]:
        """Get all upcoming bills in the given date range."""
        result = await self.session.execute(
            select(Liability).where(
                Liability.due_date.between(start_date, end_date)
            )
        )
        return list(result.scalars().all())

    async def _analyze_risk_factors(
        self,
        accounts: List[Account],
        splits: List[dict],
        cashflow_impacts: List[CashflowImpact]
    ) -> List[RiskFactor]:
        """Analyze various risk factors for the proposed splits."""
        risk_factors = []
        
        # Check for high credit utilization
        for account in accounts:
            if account.type == "credit" and account.total_limit:
                split_amount = sum(
                    Decimal(str(split["amount"]))
                    for split in splits
                    if split["account_id"] == account.id
                )
                projected_balance = account.available_balance - split_amount
                utilization = (
                    abs(projected_balance) / account.total_limit * 100
                )
                
                if utilization > 80:
                    # Calculate severity based on how much it exceeds 80%
                    # and weight it more heavily for higher utilization
                    excess = utilization - Decimal('80')
                    severity = min(int(excess * Decimal('7.5')), 100)  # 7.5 means 90% utilization = 75 severity
                    if utilization > 90:
                        severity = min(severity + 30, 100)  # Extra penalty for >90% utilization
                    
                    risk_factors.append(RiskFactor(
                        name="High Credit Utilization",
                        severity=severity,
                        description=f"Credit utilization for account {account.id} will exceed 80%"
                    ))
        
        # Check for low account balances
        for account in accounts:
            if account.type == "checking":
                split_amount = sum(
                    Decimal(str(split["amount"]))
                    for split in splits
                    if split["account_id"] == account.id
                )
                projected_balance = account.available_balance - split_amount
                
                if projected_balance < 1000:
                    risk_factors.append(RiskFactor(
                        name="Low Account Balance",
                        severity=min(int((1000 - projected_balance) / 10), 100),
                        description=f"Account {account.id} balance will fall below $1,000"
                    ))
        
        # Check for cashflow deficits
        for impact in cashflow_impacts:
            if impact.projected_deficit:
                risk_factors.append(RiskFactor(
                    name="Cashflow Deficit",
                    severity=min(int(impact.projected_deficit / 100), 100),
                    description=f"Projected deficit of ${impact.projected_deficit} on {impact.date}"
                ))
        
        return risk_factors

    def _calculate_account_risk_score(
        self,
        account: Account,
        split_amount: Decimal,
        projected_balance: Decimal,
        projected_utilization: Optional[Decimal]
    ) -> int:
        """Calculate a risk score for a specific account."""
        risk_score = 0
        
        if account.type == "credit":
            # Higher risk for high credit utilization
            if projected_utilization:
                if projected_utilization > 90:
                    risk_score += 50
                elif projected_utilization > 80:
                    risk_score += 40
                elif projected_utilization > 70:
                    risk_score += 30
        else:
            # Higher risk for low checking balances
            if projected_balance < 500:
                risk_score += 50
            elif projected_balance < 1000:
                risk_score += 40
            elif projected_balance < 2000:
                risk_score += 30
        
        # Risk based on split amount relative to current balance
        balance_ratio = split_amount / abs(account.available_balance)
        if balance_ratio > 0.5:
            risk_score += 40
        elif balance_ratio > 0.3:
            risk_score += 30
        elif balance_ratio > 0.1:
            risk_score += 20
        
        return min(risk_score, 100)

    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> int:
        """Calculate overall risk score based on individual risk factors."""
        if not risk_factors:
            return 0
            
        # Weight higher severity risks more heavily
        weighted_sum = sum(factor.severity * 1.5 if factor.severity > 70 else factor.severity
                         for factor in risk_factors)
        return min(int(weighted_sum / len(risk_factors)), 100)

    def _generate_recommendations(
        self,
        account_impacts: List[AccountImpact],
        cashflow_impacts: List[CashflowImpact],
        risk_factors: List[RiskFactor]
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
            
            if impact.projected_credit_utilization and impact.projected_credit_utilization > 80:
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
