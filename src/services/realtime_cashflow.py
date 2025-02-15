from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
from collections import defaultdict
import statistics

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.models.transaction_history import TransactionHistory
from src.schemas.realtime_cashflow import AccountBalance, RealtimeCashflow
from src.schemas.cashflow import (
    CrossAccountAnalysis, AccountCorrelation, TransferPattern,
    AccountUsagePattern, BalanceDistribution, AccountRiskAssessment
)


class RealtimeCashflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_account_balances(self) -> List[AccountBalance]:
        """Fetch current balances for all accounts."""
        query = select(Account)
        result = await self.db.execute(query)
        accounts = result.scalars().all()

        return [
            AccountBalance(
                account_id=account.id,
                name=account.name,
                type=account.type,
                current_balance=account.available_balance,
                available_credit=account.available_credit,
                total_limit=account.total_limit
            )
            for account in accounts
        ]

    async def get_upcoming_bill(self) -> Tuple[Optional[datetime], Optional[int]]:
        """Get the next upcoming bill and days until due."""
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date >= datetime.now().date()
        ).order_by(Liability.due_date)
        
        result = await self.db.execute(query)
        bills = result.scalars().all()

        if not bills:
            return None, None

        # Get the earliest bill
        next_bill = min(bills, key=lambda x: x.due_date)
        days_until = (next_bill.due_date - datetime.now().date()).days
        return next_bill.due_date, days_until

    async def calculate_minimum_balance(self) -> Decimal:
        """Calculate minimum balance required for upcoming bills."""
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date <= (datetime.now() + timedelta(days=14)).date()
        )
        result = await self.db.execute(query)
        upcoming_bills = result.scalars().all()

        return sum((bill.amount for bill in upcoming_bills), Decimal(0))

    async def get_realtime_cashflow(self) -> RealtimeCashflow:
        """Get real-time cashflow data across all accounts."""
        account_balances = await self.get_account_balances()
        
        total_funds = sum(
            (acc.current_balance for acc in account_balances 
             if acc.type != "credit"),
            Decimal(0)
        )
        
        total_credit = sum(
            (acc.available_credit for acc in account_balances 
             if acc.type == "credit" and acc.available_credit is not None),
            Decimal(0)
        )

        # Get upcoming bills
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date >= datetime.now().date()
        )
        result = await self.db.execute(query)
        upcoming_bills = result.scalars().all()
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
            projected_deficit=projected_deficit
        )

    async def analyze_account_correlations(self) -> Dict[str, Dict[str, AccountCorrelation]]:
        """Analyze correlations between accounts based on transaction patterns."""
        # Get all accounts
        query = select(Account)
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        correlations = {}

        for acc1 in accounts:
            correlations[str(acc1.id)] = {}
            for acc2 in accounts:
                if acc1.id >= acc2.id:
                    continue

                # Get transfers between accounts
                transfers_query = select(PaymentSource).join(
                    Payment,
                    PaymentSource.payment_id == Payment.id
                ).where(
                    and_(
                        PaymentSource.account_id.in_([acc1.id, acc2.id]),
                        Payment.category == "Transfer"
                    )
                )
                result = await self.db.execute(transfers_query)
                transfers = result.scalars().all()

                # Calculate correlation metrics
                transfer_frequency = len(transfers)
                
                # Get common categories from transactions
                categories_query = select(TransactionHistory.description).where(
                    TransactionHistory.account_id.in_([acc1.id, acc2.id])
                )
                result = await self.db.execute(categories_query)
                categories = result.scalars().all()
                common_categories = list(set(categories))

                # Determine relationship type
                relationship_type = "independent"
                if transfer_frequency > 5:
                    relationship_type = "complementary" if acc1.type != acc2.type else "supplementary"

                correlations[str(acc1.id)][str(acc2.id)] = AccountCorrelation(
                    correlation_score=Decimal(transfer_frequency / 10).min(Decimal('1')),
                    transfer_frequency=transfer_frequency,
                    common_categories=common_categories[:10],  # Limit to top 10 categories
                    relationship_type=relationship_type
                )

        return correlations

    async def analyze_transfer_patterns(self) -> List[TransferPattern]:
        """Analyze transfer patterns between accounts."""
        patterns = []
        
        # Get all transfers
        transfers_query = select(
            PaymentSource, 
            Payment,
            func.count(PaymentSource.id).label('frequency'),
            func.avg(PaymentSource.amount).label('avg_amount')
        ).join(
            Payment,
            PaymentSource.payment_id == Payment.id
        ).where(
            Payment.category == "Transfer"
        ).group_by(
            PaymentSource.account_id,
            Payment.category
        )
        
        result = await self.db.execute(transfers_query)
        transfers = result.all()

        for transfer in transfers:
            source = transfer[0]
            payment = transfer[1]
            frequency = transfer[2]
            avg_amount = Decimal(str(transfer[3]))

            # Get category distribution
            category_query = select(
                Payment.category,
                func.sum(PaymentSource.amount).label('total_amount')
            ).join(
                PaymentSource,
                PaymentSource.payment_id == Payment.id
            ).where(
                PaymentSource.account_id == source.account_id
            ).group_by(
                Payment.category
            )
            
            cat_result = await self.db.execute(category_query)
            categories = {row[0]: Decimal(str(row[1])) for row in cat_result}

            patterns.append(TransferPattern(
                source_account_id=source.account_id,
                target_account_id=payment.id,  # Using payment ID as target for this example
                average_amount=avg_amount,
                frequency=frequency,
                typical_day_of_month=None,  # Would require more complex analysis
                category_distribution=categories
            ))

        return patterns

    async def analyze_usage_patterns(self) -> Dict[int, AccountUsagePattern]:
        """Analyze usage patterns for each account."""
        patterns = {}
        query = select(Account)
        result = await self.db.execute(query)
        accounts = result.scalars().all()

        for account in accounts:
            # Get transaction history
            transactions_query = select(TransactionHistory).where(
                TransactionHistory.account_id == account.id
            )
            result = await self.db.execute(transactions_query)
            transactions = result.scalars().all()

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
                        if account.type == "credit" and account.total_limit
                        else None
                    )
                )
                continue

            # Calculate metrics
            amounts = [tx.amount for tx in transactions]
            avg_transaction = sum(amounts, Decimal(0)) / len(amounts)
            volatility = statistics.stdev(amounts) if len(amounts) > 1 else Decimal(0)
            
            # Get common merchants (from description)
            merchants = defaultdict(int)
            for tx in transactions:
                if tx.description:
                    merchants[tx.description] += 1
            
            # Get peak usage days
            days = [tx.transaction_date.day for tx in transactions]
            peak_days = list(set(days))[:31]  # Limit to 31 days

            # Calculate utilization rate for credit accounts
            utilization_rate = None
            if account.type == "credit" and account.total_limit:
                utilization_rate = abs(account.available_balance) / account.total_limit

            patterns[account.id] = AccountUsagePattern(
                account_id=account.id,
                primary_use=self._determine_primary_use(transactions),
                average_transaction_size=avg_transaction,
                common_merchants=sorted(merchants, key=merchants.get, reverse=True)[:10],
                peak_usage_days=peak_days,
                category_preferences=self._calculate_category_preferences(transactions),
                utilization_rate=utilization_rate
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
        self, 
        transactions: List[TransactionHistory]
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

        return {k: v/total for k, v in categories.items()}

    async def analyze_balance_distribution(self) -> Dict[int, BalanceDistribution]:
        """Analyze balance distribution across accounts."""
        distributions = {}
        query = select(Account)
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        total_balance = sum(
            abs(acc.available_balance) for acc in accounts if acc.type != "credit"
        )

        for account in accounts:
            # Get historical balances from transaction history
            balance_query = select(TransactionHistory).where(
                and_(
                    TransactionHistory.account_id == account.id,
                    TransactionHistory.transaction_date >= (
                        datetime.now() - timedelta(days=30)
                    )
                )
            ).order_by(TransactionHistory.transaction_date)
            
            result = await self.db.execute(balance_query)
            transactions = result.scalars().all()

            if not transactions:
                continue

            # Calculate balance metrics
            balances = [tx.amount for tx in transactions]
            avg_balance = statistics.mean(balances)
            balance_volatility = statistics.stdev(balances) if len(balances) > 1 else Decimal(0)
            
            distributions[account.id] = BalanceDistribution(
                account_id=account.id,
                average_balance=Decimal(str(avg_balance)),
                balance_volatility=Decimal(str(balance_volatility)),
                min_balance_30d=min(balances),
                max_balance_30d=max(balances),
                typical_balance_range=(
                    Decimal(str(avg_balance - balance_volatility)),
                    Decimal(str(avg_balance + balance_volatility))
                ),
                percentage_of_total=(
                    abs(account.available_balance) / total_balance 
                    if total_balance > 0 and account.type != "credit"
                    else Decimal(0)
                )
            )

        return distributions

    async def assess_account_risks(self) -> Dict[int, AccountRiskAssessment]:
        """Assess risks for each account."""
        risks = {}
        query = select(Account)
        result = await self.db.execute(query)
        accounts = result.scalars().all()

        for account in accounts:
            # Get recent transactions
            transactions_query = select(TransactionHistory).where(
                and_(
                    TransactionHistory.account_id == account.id,
                    TransactionHistory.transaction_date >= (
                        datetime.now() - timedelta(days=30)
                    )
                )
            )
            result = await self.db.execute(transactions_query)
            transactions = result.scalars().all()

            # Initialize risk metrics with defaults if no transactions
            balances = [tx.amount for tx in transactions] if transactions else [account.available_balance]
            volatility = statistics.stdev(balances) if len(balances) > 1 else Decimal(0)

            # Calculate overdraft risk
            overdraft_risk = Decimal(0)
            if account.type != "credit":
                min_balance = min(balances)
                overdraft_risk = (
                    Decimal('1') if min_balance < 0 
                    else (Decimal('0.5') if min_balance < 100 
                    else Decimal('0'))
                )

            # Calculate credit utilization risk
            credit_utilization_risk = None
            if account.type == "credit" and account.total_limit:
                utilization = abs(account.available_balance) / account.total_limit
                credit_utilization_risk = min(utilization, Decimal('1'))

            # Calculate payment failure risk based on transaction patterns
            payment_failure_risk = Decimal('0.5') if volatility > 1000 else Decimal('0.2')

            # Calculate volatility score
            max_volatility = max(abs(amount) for amount in balances)
            volatility_score = min(
                volatility / max_volatility if max_volatility > 0 else Decimal(0),
                Decimal('1')
            )

            # Calculate overall risk score
            risk_factors = [
                overdraft_risk,
                credit_utilization_risk if credit_utilization_risk is not None else Decimal(0),
                payment_failure_risk,
                volatility_score
            ]
            overall_risk = sum(risk_factors, Decimal(0)) / len(risk_factors)

            risks[account.id] = AccountRiskAssessment(
                account_id=account.id,
                overdraft_risk=overdraft_risk,
                credit_utilization_risk=credit_utilization_risk,
                payment_failure_risk=payment_failure_risk,
                volatility_score=volatility_score,
                overall_risk_score=overall_risk
            )

        return risks

    async def get_cross_account_analysis(self) -> CrossAccountAnalysis:
        """Get comprehensive cross-account analysis."""
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
            timestamp=datetime.now().date()
        )
