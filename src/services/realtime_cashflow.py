import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.models.transaction_history import TransactionHistory
from src.repositories.factory import RepositoryFactory
from src.schemas.cashflow import (
    AccountCorrelation,
    AccountRiskAssessment,
    AccountUsagePattern,
    BalanceDistribution,
    CrossAccountAnalysis,
    TransferPattern,
)
from src.schemas.realtime_cashflow import AccountBalance, RealtimeCashflow
from src.utils.decimal_precision import DecimalPrecision


class RealtimeCashflowService:
    """
    Service for real-time cashflow analysis across accounts.
    
    This service provides real-time cashflow data, account correlations,
    transfer patterns, usage patterns, balance distribution, and risk 
    assessment. Following ADR-014 Repository Layer Compliance, this service
    now uses repositories for all database operations rather than direct
    database access.
    
    The service maintains a clear separation between:
    1. Business logic (in this service)
    2. Data access (in RealtimeCashflowRepository)
    3. API contracts (through schema objects)
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self._realtime_repo = None
        
    @property
    async def realtime_repository(self):
        """
        Get the realtime cashflow repository instance.
        
        Returns:
            RealtimeCashflowRepository: Realtime cashflow repository
        """
        if self._realtime_repo is None:
            self._realtime_repo = await RepositoryFactory.create_realtime_cashflow_repository(
                self.db
            )
        return self._realtime_repo

    async def get_account_balances(self) -> List[AccountBalance]:
        """Fetch current balances for all accounts."""
        repo = await self.realtime_repository
        accounts = await repo.get_all_accounts()

        return [
            AccountBalance(
                account_id=account.id,
                name=account.name,
                type=account.account_type,
                current_balance=account.available_balance,
                available_credit=account.available_credit,
                total_limit=account.total_limit,
            )
            for account in accounts
        ]

    async def get_upcoming_bill(self) -> Tuple[Optional[datetime], Optional[int]]:
        """Get the next upcoming bill and days until due."""
        repo = await self.realtime_repository
        return await repo.get_upcoming_bill()

    async def calculate_minimum_balance(self) -> Decimal:
        """Calculate minimum balance required for upcoming bills."""
        repo = await self.realtime_repository
        return await repo.calculate_minimum_balance(days=14)

    async def get_realtime_cashflow(self) -> RealtimeCashflow:
        """Get real-time cashflow data across all accounts."""
        repo = await self.realtime_repository
        account_balances = await self.get_account_balances()

        total_funds = sum(
            (acc.current_balance for acc in account_balances if acc.type != "credit"),
            Decimal(0),
        )

        total_credit = sum(
            (
                acc.available_credit
                for acc in account_balances
                if acc.type == "credit" and acc.available_credit is not None
            ),
            Decimal(0),
        )

        # Get upcoming bills
        upcoming_bills = await repo.get_unpaid_liabilities()
        total_liabilities = sum((bill.amount for bill in upcoming_bills), Decimal(0))

        next_bill_date, days_until_bill = await self.get_upcoming_bill()
        min_balance = await self.calculate_minimum_balance()

        # Calculate projected deficit
        projected_deficit = None
        if total_funds < min_balance:
            projected_deficit = min_balance - total_funds

        return RealtimeCashflow(
            account_balances=account_balances,
            total_available_funds=total_funds,
            total_available_credit=total_credit,
            total_liabilities_due=total_liabilities,
            net_position=total_funds - total_liabilities,
            next_bill_due=next_bill_date,
            days_until_next_bill=days_until_bill,
            minimum_balance_required=min_balance,
            projected_deficit=projected_deficit,
        )

    async def analyze_account_correlations(
        self,
    ) -> Dict[str, Dict[str, AccountCorrelation]]:
        """Analyze correlations between accounts based on transaction patterns."""
        # Get all accounts from repository
        repo = await self.realtime_repository
        accounts = await repo.get_all_accounts()
        correlations = {}

        for acc1 in accounts:
            correlations[str(acc1.id)] = {}
            for acc2 in accounts:
                if acc1.id >= acc2.id:
                    continue

                # Get transfers between accounts
                transfers = await repo.get_transfers_between_accounts([acc1.id, acc2.id])

                # Calculate correlation metrics
                transfer_frequency = len(transfers)

                # Get transactions with descriptions for each account
                acc1_txs = await repo.get_transaction_history(acc1.id)
                acc2_txs = await repo.get_transaction_history(acc2.id)
                
                # Extract descriptions and find common ones
                acc1_categories = [tx.description for tx in acc1_txs if tx.description]
                acc2_categories = [tx.description for tx in acc2_txs if tx.description]
                common_categories = list(set(acc1_categories) & set(acc2_categories))

                # Determine relationship type
                relationship_type = "independent"
                if transfer_frequency > 5:
                    relationship_type = (
                        "complementary" if acc1.type != acc2.type else "supplementary"
                    )

                correlations[str(acc1.id)][str(acc2.id)] = AccountCorrelation(
                    correlation_score=Decimal(transfer_frequency / 10).min(
                        Decimal("1")
                    ),
                    transfer_frequency=transfer_frequency,
                    common_categories=common_categories[:10],  # Limit to top 10 categories
                    relationship_type=relationship_type,
                )

        return correlations

    async def analyze_transfer_patterns(self) -> List[TransferPattern]:
        """Analyze transfer patterns between accounts."""
        repo = await self.realtime_repository
        patterns = []

        # Get all accounts
        accounts = await repo.get_all_accounts()
        
        # For each account, build transfer patterns
        for account in accounts:
            # Get all transfers for this account
            transfers = await repo.get_transfers_between_accounts([account.id])
            
            if not transfers:
                continue
                
            # Simple aggregation - in real implementation would use repository
            source_accounts = {}
            target_accounts = {}
            
            # Simple frequency calculation
            for transfer in transfers:
                if transfer.account_id not in source_accounts:
                    source_accounts[transfer.account_id] = []
                source_accounts[transfer.account_id].append(transfer)
            
            # For each source account, calculate metrics
            for source_id, source_transfers in source_accounts.items():
                # Calculate average amount
                avg_amount = sum([t.amount for t in source_transfers], Decimal(0)) / len(source_transfers)
                
                # Get payment categories
                categories = await repo.get_payment_categories(source_id)
                
                # Create a transfer pattern
                patterns.append(
                    TransferPattern(
                        source_account_id=source_id,
                        # In a real implementation, we would track target accounts
                        target_account_id=source_id,  # Placeholder
                        average_amount=DecimalPrecision.round_for_calculation(avg_amount),
                        frequency=len(source_transfers),
                        typical_day_of_month=None,  # Would require more complex analysis
                        category_distribution=categories,
                    )
                )

        return patterns

    async def analyze_usage_patterns(self) -> Dict[int, AccountUsagePattern]:
        """Analyze usage patterns for each account."""
        repo = await self.realtime_repository
        patterns = {}
        
        # Get all accounts
        accounts = await repo.get_all_accounts()

        for account in accounts:
            # Get transaction history from repository
            transactions = await repo.get_transaction_history(account.id)

            if not transactions:
                patterns[account.id] = AccountUsagePattern(
                    account_id=account.id,
                    primary_use="general",
                    average_transaction_size=Decimal(0),
                    common_merchants=[],
                    peak_usage_days=[],
                    category_preferences={},
                    utilization_rate=(
                        abs(account.available_balance) / account.total_limit
                        if account.account_type == "credit" and account.total_limit
                        else None
                    ),
                )
                continue

            # Calculate metrics
            amounts = [tx.amount for tx in transactions]
            avg_transaction = sum(amounts, Decimal(0)) / len(amounts)
            volatility = statistics.stdev(amounts) if len(amounts) > 1 else Decimal(0)

            # Get common merchants from repository
            merchants_data = await repo.get_transactions_with_description(account.id)
            
            # Get peak usage days
            days = [tx.transaction_date.day for tx in transactions]
            peak_days = list(set(days))[:31]  # Limit to 31 days

            # Calculate utilization rate for credit accounts
            utilization_rate = None
            if account.account_type == "credit" and account.total_limit:
                utilization_rate = abs(account.available_balance) / account.total_limit

            patterns[account.id] = AccountUsagePattern(
                account_id=account.id,
                primary_use=self._determine_primary_use(transactions),
                average_transaction_size=avg_transaction,
                common_merchants=sorted(merchants_data.keys(), key=merchants_data.get, reverse=True)[:10],
                peak_usage_days=peak_days,
                category_preferences=self._calculate_category_preferences(transactions),
                utilization_rate=utilization_rate,
            )

        return patterns

    def _determine_primary_use(self, transactions: List[TransactionHistory]) -> str:
        """Determine primary use of account based on transaction patterns."""
        categories = [tx.description for tx in transactions if tx.description]
        if not categories:
            return "general"

        # Simple logic - could be made more sophisticated
        most_common = max(set(categories), key=categories.count)
        return most_common.lower()

    def _calculate_category_preferences(
        self, transactions: List[TransactionHistory]
    ) -> Dict[str, Decimal]:
        """Calculate category preferences based on transaction amounts."""
        categories = defaultdict(Decimal)
        total = Decimal(0)

        for tx in transactions:
            if tx.description:
                categories[tx.description] += abs(tx.amount)
                total += abs(tx.amount)

        if total == 0:
            return {}

        return {k: v / total for k, v in categories.items()}

    async def analyze_balance_distribution(self) -> Dict[int, BalanceDistribution]:
        """Analyze balance distribution across accounts."""
        repo = await self.realtime_repository
        distributions = {}
        
        # Get all accounts
        accounts = await repo.get_all_accounts()
        
        # Calculate total balance for percentage calculations
        total_balance = sum(
            abs(acc.available_balance) for acc in accounts if acc.account_type != "credit"
        )

        for account in accounts:
            # Get historical balances using repository
            balances = await repo.get_balance_history_in_range(account.id, 30)
            
            if not balances:
                continue

            # Calculate balance metrics
            avg_balance = statistics.mean(balances)
            balance_volatility = (
                statistics.stdev(balances) if len(balances) > 1 else Decimal(0)
            )

            # Create distribution object with calculated metrics
            distributions[account.id] = BalanceDistribution(
                account_id=account.id,
                average_balance=Decimal(str(avg_balance)),
                balance_volatility=Decimal(str(balance_volatility)),
                min_balance_30d=min(balances),
                max_balance_30d=max(balances),
                typical_balance_range=(
                    Decimal(str(avg_balance - balance_volatility)),
                    Decimal(str(avg_balance + balance_volatility)),
                ),
                percentage_of_total=(
                    abs(account.available_balance) / total_balance
                    if total_balance > 0 and account.account_type != "credit"
                    else Decimal(0)
                ),
            )

        return distributions

    async def assess_account_risks(self) -> Dict[int, AccountRiskAssessment]:
        """Assess risks for each account."""
        repo = await self.realtime_repository
        risks = {}
        
        # Get all accounts
        accounts = await repo.get_all_accounts()

        for account in accounts:
            # Get recent transactions using repository
            balances = await repo.get_balance_history_in_range(account.id, 30)
            
            # Initialize risk metrics with defaults if no transactions
            if not balances:
                balances = [account.available_balance]
                
            volatility = statistics.stdev(balances) if len(balances) > 1 else Decimal(0)

            # Calculate overdraft risk
            overdraft_risk = Decimal(0)
            if account.account_type != "credit":
                min_balance = min(balances)
                overdraft_risk = (
                    Decimal("1")
                    if min_balance < 0
                    else (Decimal("0.5") if min_balance < 100 else Decimal("0"))
                )

            # Calculate credit utilization risk
            credit_utilization_risk = None
            if account.account_type == "credit" and account.total_limit:
                utilization = abs(account.available_balance) / account.total_limit
                credit_utilization_risk = min(utilization, Decimal("1"))

            # Calculate payment failure risk based on transaction patterns
            payment_failure_risk = (
                Decimal("0.5") if volatility > 1000 else Decimal("0.2")
            )

            # Calculate volatility score
            max_volatility = max(abs(amount) for amount in balances)
            volatility_score = min(
                volatility / max_volatility if max_volatility > 0 else Decimal(0),
                Decimal("1"),
            )

            # Calculate overall risk score
            risk_factors = [
                overdraft_risk,
                (
                    credit_utilization_risk
                    if credit_utilization_risk is not None
                    else Decimal(0)
                ),
                payment_failure_risk,
                volatility_score,
            ]
            overall_risk = sum(risk_factors, Decimal(0)) / len(risk_factors)

            risks[account.id] = AccountRiskAssessment(
                account_id=account.id,
                overdraft_risk=overdraft_risk,
                credit_utilization_risk=credit_utilization_risk,
                payment_failure_risk=payment_failure_risk,
                volatility_score=volatility_score,
                overall_risk_score=overall_risk,
            )

        return risks

    async def get_cross_account_analysis(self) -> CrossAccountAnalysis:
        """Get comprehensive cross-account analysis."""
        # All these methods now use repository pattern internally
        correlations = await self.analyze_account_correlations()
        transfer_patterns = await self.analyze_transfer_patterns()
        usage_patterns = await self.analyze_usage_patterns()
        balance_distribution = await self.analyze_balance_distribution()
        risk_assessment = await self.assess_account_risks()

        return CrossAccountAnalysis(
            correlations=correlations,
            transfer_patterns=transfer_patterns,
            usage_patterns=usage_patterns,
            balance_distribution=balance_distribution,
            risk_assessment=risk_assessment,
            timestamp=datetime.now().date(),
        )
