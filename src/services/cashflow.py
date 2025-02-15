from decimal import Decimal
from datetime import date, timedelta, datetime
from typing import List, Dict, Union, Tuple, Optional
from sqlalchemy import select, func, extract
from zoneinfo import ZoneInfo
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from statistics import mean, stdev
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.models.income import Income
from src.models.categories import Category
from src.schemas.cashflow import (
    CustomForecastParameters, CustomForecastResponse, CustomForecastResult,
    HistoricalTrendMetrics, HistoricalPeriodAnalysis, SeasonalityAnalysis,
    HistoricalTrendsResponse, AccountForecastRequest, AccountForecastResponse,
    AccountForecastMetrics, AccountForecastResult
)

class CashflowService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._warning_thresholds = {
            "low_balance": Decimal("100.00"),  # Warning when balance drops below $100
            "high_credit_utilization": Decimal("0.80"),  # Warning at 80% credit utilization
            "large_outflow": Decimal("1000.00")  # Warning for outflows over $1000
        }
        self._holidays = {
            # Add major US holidays that might impact cashflow
            "new_years": date(date.today().year, 1, 1),
            "christmas": date(date.today().year, 12, 25),
            "thanksgiving": date(date.today().year, 11, 25),  # Approximate
            "tax_day": date(date.today().year, 4, 15),
        }
    
    async def get_account_forecast(
        self,
        params: AccountForecastRequest
    ) -> AccountForecastResponse:
        """Generate account-specific forecast with detailed metrics."""
        # Verify account exists and get its details
        account = await self.db.get(Account, params.account_id)
        if not account:
            raise ValueError(f"Account with id {params.account_id} not found")

        # Initialize metrics
        metrics = await self._calculate_account_metrics(
            account,
            params.start_date,
            params.end_date,
            params.include_pending,
            params.include_recurring
        )

        # Generate daily forecasts
        daily_forecasts = await self._generate_account_daily_forecasts(
            account,
            params.start_date,
            params.end_date,
            params.include_pending,
            params.include_recurring,
            params.include_transfers
        )

        # Calculate overall confidence
        overall_confidence = await self._calculate_forecast_confidence(
            account,
            daily_forecasts,
            metrics
        )

        return AccountForecastResponse(
            account_id=account.id,
            forecast_period=(params.start_date, params.end_date),
            metrics=metrics,
            daily_forecasts=daily_forecasts,
            overall_confidence=overall_confidence,
            timestamp=date.today()
        )

    async def _calculate_account_metrics(
        self,
        account: Account,
        start_date: date,
        end_date: date,
        include_pending: bool,
        include_recurring: bool
    ) -> AccountForecastMetrics:
        """Calculate account-specific forecast metrics."""
        # Get historical transactions for volatility calculation
        historical_start = start_date - timedelta(days=90)  # Look back 90 days
        transactions = await self._get_historical_transactions(
            [account.id],
            historical_start,
            start_date
        )

        # Calculate projected transactions
        projected_transactions = await self._get_projected_transactions(
            account,
            start_date,
            end_date,
            include_pending,
            include_recurring
        )

        # Calculate metrics
        daily_balances = []
        inflows = []
        outflows = []
        current_balance = account.available_balance

        for trans in projected_transactions:
            current_balance += trans["amount"]
            daily_balances.append(current_balance)
            if trans["amount"] > 0:
                inflows.append(trans["amount"])
            else:
                outflows.append(abs(trans["amount"]))

        # Identify low balance dates
        low_balance_dates = [
            trans["date"] for trans in projected_transactions
            if (current_balance + trans["amount"]) < self._warning_thresholds["low_balance"]
        ]

        # Calculate credit utilization for credit accounts
        credit_utilization = None
        if account.type == "credit" and account.total_limit:
            if daily_balances:
                credit_utilization = abs(min(daily_balances)) / account.total_limit
            else:
                credit_utilization = abs(account.available_balance) / account.total_limit

        # Calculate balance volatility
        balance_volatility = Decimal(str(stdev(daily_balances))) if len(daily_balances) > 1 else Decimal("0")

        return AccountForecastMetrics(
            average_daily_balance=Decimal(str(mean(daily_balances))) if daily_balances else Decimal("0"),
            minimum_projected_balance=min(daily_balances) if daily_balances else account.available_balance,
            maximum_projected_balance=max(daily_balances) if daily_balances else account.available_balance,
            average_inflow=Decimal(str(mean(inflows))) if inflows else Decimal("0"),
            average_outflow=Decimal(str(mean(outflows))) if outflows else Decimal("0"),
            projected_low_balance_dates=low_balance_dates,
            credit_utilization=credit_utilization,
            balance_volatility=balance_volatility,
            forecast_confidence=Decimal("0.9")  # Will be adjusted in _calculate_forecast_confidence
        )

    async def _generate_account_daily_forecasts(
        self,
        account: Account,
        start_date: date,
        end_date: date,
        include_pending: bool,
        include_recurring: bool,
        include_transfers: bool
    ) -> List[AccountForecastResult]:
        """Generate daily forecast results for an account."""
        daily_forecasts = []
        current_balance = account.available_balance
        current_date = start_date

        while current_date <= end_date:
            # Get day's transactions
            day_transactions = await self._get_day_transactions(
                account,
                current_date,
                include_pending,
                include_recurring,
                include_transfers
            )

            # Calculate day's inflow/outflow
            day_inflow = sum(t["amount"] for t in day_transactions if t["amount"] > 0)
            day_outflow = sum(abs(t["amount"]) for t in day_transactions if t["amount"] < 0)

            # Update balance
            current_balance += (day_inflow - day_outflow)

            # Generate warning flags
            warning_flags = []
            if current_balance < self._warning_thresholds["low_balance"]:
                warning_flags.append("low_balance")
            if account.type == "credit" and account.total_limit:
                utilization = abs(current_balance) / account.total_limit
                if utilization > self._warning_thresholds["high_credit_utilization"]:
                    warning_flags.append("high_credit_utilization")
            if day_outflow > self._warning_thresholds["large_outflow"]:
                warning_flags.append("large_outflow")

            # Calculate confidence score for the day
            confidence_score = self._calculate_day_confidence(
                account,
                current_balance,
                day_transactions,
                warning_flags
            )

            daily_forecasts.append(AccountForecastResult(
                date=current_date,
                projected_balance=current_balance,
                projected_inflow=day_inflow,
                projected_outflow=day_outflow,
                confidence_score=confidence_score,
                contributing_transactions=[
                    {"amount": t["amount"], "description": t["description"]}
                    for t in day_transactions
                ],
                warning_flags=warning_flags
            ))

            current_date += timedelta(days=1)

        return daily_forecasts

    async def _get_day_transactions(
        self,
        account: Account,
        target_date: date,
        include_pending: bool,
        include_recurring: bool,
        include_transfers: bool
    ) -> List[Dict]:
        """Get all transactions for a specific day."""
        transactions = []

        # Get bills due on this date
        bills_query = (
            select(Liability)
            .where(
                Liability.primary_account_id == account.id,
                Liability.due_date == target_date
            )
        )
        if not include_pending:
            bills_query = bills_query.where(Liability.status != "pending")
        bills = (await self.db.execute(bills_query)).scalars().all()
        
        for bill in bills:
            transactions.append({
                "amount": -bill.amount,
                "description": f"Bill: {bill.name}",
                "type": "bill"
            })

        # Get income expected on this date
        income_query = (
            select(Income)
            .where(
                Income.account_id == account.id,
                Income.date == target_date
            )
        )
        if not include_pending:
            income_query = income_query.where(Income.deposited == True)
        income_entries = (await self.db.execute(income_query)).scalars().all()

        for income in income_entries:
            transactions.append({
                "amount": income.amount,
                "description": f"Income: {income.source}",
                "type": "income"
            })

        # Add recurring transactions if requested
        if include_recurring:
            recurring_query = (
                select(Liability)
                .where(
                    Liability.primary_account_id == account.id,
                    Liability.recurring == True
                )
            )
            recurring_bills = (await self.db.execute(recurring_query)).scalars().all()
            
            for bill in recurring_bills:
                # Check if this is a recurring instance for this date
                current_date = bill.due_date
                while current_date <= target_date:
                    if current_date == target_date:
                        transactions.append({
                            "amount": -bill.amount,
                            "description": f"Recurring Bill: {bill.name}",
                            "type": "recurring_bill"
                        })
                        break
                    # Advance to next occurrence
                    # Advance to next occurrence
                    next_month = current_date.month + 1
                    next_year = current_date.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    current_date = date(next_year, next_month, current_date.day)

        # Add transfers if requested
        if include_transfers:
            # Implementation for transfers would go here
            pass

        return transactions

    def _calculate_day_confidence(
        self,
        account: Account,
        balance: Decimal,
        transactions: List[Dict],
        warning_flags: List[str]
    ) -> Decimal:
        """Calculate confidence score for a day's forecast."""
        base_confidence = Decimal("0.9")  # Start with 90% confidence

        # Reduce confidence based on warning flags
        confidence_deductions = {
            "low_balance": Decimal("0.2"),
            "high_credit_utilization": Decimal("0.15"),
            "large_outflow": Decimal("0.1")
        }
        
        for flag in warning_flags:
            if flag in confidence_deductions:
                base_confidence -= confidence_deductions[flag]

        # Adjust for transaction volume
        if len(transactions) > 5:  # High transaction volume increases uncertainty
            base_confidence -= Decimal("0.1")

        # Ensure confidence stays within valid range
        return max(min(base_confidence, Decimal("1.0")), Decimal("0.1"))

    async def _calculate_forecast_confidence(
        self,
        account: Account,
        daily_forecasts: List[AccountForecastResult],
        metrics: AccountForecastMetrics
    ) -> Decimal:
        """Calculate overall confidence score for the forecast."""
        if not daily_forecasts:
            return Decimal("0.0")

        # Average of daily confidence scores
        avg_confidence = mean(f.confidence_score for f in daily_forecasts)

        # Adjust for account type specific factors
        if account.type == "credit":
            # Lower confidence if projected to exceed credit limit
            if metrics.credit_utilization and metrics.credit_utilization > Decimal("0.9"):
                avg_confidence *= Decimal("0.8")
        else:  # checking/savings
            # Lower confidence if multiple low balance warnings
            low_balance_days = len([f for f in daily_forecasts if "low_balance" in f.warning_flags])
            if low_balance_days > len(daily_forecasts) // 4:  # More than 25% of days
                avg_confidence *= Decimal("0.85")

        # Adjust for volatility
        if metrics.balance_volatility > metrics.average_daily_balance * Decimal("0.2"):
            avg_confidence *= Decimal("0.9")

        return max(min(Decimal(str(avg_confidence)), Decimal("1.0")), Decimal("0.1"))

    async def get_metrics_for_date(
        self,
        target_date: date
    ) -> Optional[CustomForecastResult]:
        """Get cashflow metrics for a specific date."""
        # Get all accounts
        accounts_query = select(Account)
        accounts = (await self.db.execute(accounts_query)).scalars().all()
        
        if not accounts:
            return None

        # Get day's transactions
        day_transactions = []
        total_balance = Decimal("0")
        total_inflow = Decimal("0")
        total_outflow = Decimal("0")

        for account in accounts:
            transactions = await self._get_day_transactions(
                account,
                target_date,
                include_pending=True,
                include_recurring=True,
                include_transfers=True
            )
            day_transactions.extend(transactions)
            
            # Update totals
            total_balance += account.available_balance
            for trans in transactions:
                if trans["amount"] > 0:
                    total_inflow += trans["amount"]
                else:
                    total_outflow += abs(trans["amount"])

        # Calculate confidence score
        confidence_score = self._calculate_day_confidence(
            accounts[0],  # Use first account for base calculation
            total_balance,
            day_transactions,
            []  # No warning flags for this calculation
        )

        return CustomForecastResult(
            date=target_date,
            projected_balance=total_balance,
            projected_income=total_inflow,
            projected_expenses=total_outflow,
            confidence_score=confidence_score,
            contributing_factors={
                "total_accounts": len(accounts),
                "total_transactions": len(day_transactions)
            },
            risk_factors={}
        )

    async def get_forecast(
        self,
        account_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Union[date, Decimal]]]:
        """Get cashflow forecast for the specified date range."""
        return await calculate_forecast(self.db, account_id, start_date, end_date)
    
    async def get_required_funds(
        self,
        account_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """Get required funds for bills in the specified date range."""
        return await calculate_required_funds(self.db, account_id, start_date, end_date)
    
    def get_daily_deficit(self, min_amount: Decimal, days: int) -> Decimal:
        """Calculate daily deficit needed to cover minimum required amount."""
        return calculate_daily_deficit(min_amount, days)
    
    def get_yearly_deficit(self, daily_deficit: Decimal) -> Decimal:
        """Calculate yearly deficit based on daily deficit."""
        return calculate_yearly_deficit(daily_deficit)
    
    def get_required_income(
        self,
        yearly_deficit: Decimal,
        tax_rate: Decimal = Decimal("0.80")
    ) -> Decimal:
        """Calculate required gross income to cover yearly deficit."""
        return calculate_required_income(yearly_deficit, tax_rate)
    
    async def get_custom_forecast(
        self,
        params: CustomForecastParameters
    ) -> CustomForecastResponse:
        """Get a custom forecast based on provided parameters."""
        return await calculate_custom_forecast(self.db, params)

    async def get_historical_trends(
        self,
        account_ids: List[int],
        start_date: date,
        end_date: date
    ) -> HistoricalTrendsResponse:
        """Analyze historical trends for specified accounts and date range."""
        # Get all transactions for the specified accounts and date range
        transactions = await self._get_historical_transactions(account_ids, start_date, end_date)
        
        # Calculate trend metrics
        metrics = await self._calculate_trend_metrics(transactions)
        
        # Analyze periods (e.g., monthly, quarterly)
        period_analysis = await self._analyze_historical_periods(transactions, start_date, end_date)
        
        # Analyze seasonality
        seasonality = await self._analyze_seasonality(transactions)
        
        return HistoricalTrendsResponse(
            metrics=metrics,
            period_analysis=period_analysis,
            seasonality=seasonality,
            timestamp=date.today()
        )

    async def _get_historical_transactions(
        self,
        account_ids: List[int],
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Retrieve historical transactions for analysis."""
        # Get payments
        payments_query = (
            select(Payment)
            .options(selectinload(Payment.sources))
            .where(
                Payment.payment_date.between(start_date, end_date)
            )
        )
        payments = (await self.db.execute(payments_query)).scalars().all()

        # Get income with explicit account filtering
        income_query = (
            select(Income)
            .where(
                Income.account_id.in_(account_ids),
                Income.date.between(start_date, end_date),
                Income.deposited == True  # Only include deposited income
            )
        )
        income_entries = (await self.db.execute(income_query)).scalars().all()

        # Combine and format transactions
        transactions = []
        
        for payment in payments:
            for source in payment.sources:
                if source.account_id in account_ids:
                    transactions.append({
                        "date": payment.payment_date if payment.payment_date.tzinfo else payment.payment_date.replace(tzinfo=ZoneInfo("UTC")),
                        "amount": -source.amount,  # Negative for outflow
                        "type": "payment",
                        "account_id": source.account_id,
                        "category": payment.category
                    })

        for income in income_entries:
            transactions.append({
                "date": datetime.combine(income.date, datetime.min.time(), tzinfo=ZoneInfo("UTC")),
                "amount": income.amount,  # Positive for inflow
                "type": "income",
                "account_id": income.account_id,
                "category": "income"
            })

        return sorted(transactions, key=lambda x: x["date"])

    async def _calculate_trend_metrics(
        self,
        transactions: List[Dict]
    ) -> HistoricalTrendMetrics:
        """Calculate trend metrics from historical transactions."""
        if not transactions:
            raise ValueError("No transactions available for trend analysis")

        # Calculate daily net changes
        daily_changes = []
        daily_totals: Dict[date, Decimal] = {}

        for trans in transactions:
            trans_date = trans["date"]
            if trans_date not in daily_totals:
                daily_totals[trans_date] = Decimal("0")
            daily_totals[trans_date] += trans["amount"]

        daily_changes = list(daily_totals.values())

        # Calculate metrics
        avg_daily_change = Decimal(str(mean(daily_changes)))
        volatility = Decimal(str(stdev(daily_changes))) if len(daily_changes) > 1 else Decimal("0")

        # Determine trend direction and strength
        total_days = len(daily_changes)
        if total_days < 2:
            trend_direction = "stable"
            trend_strength = Decimal("0")
        else:
            start_balance = sum(t["amount"] for t in transactions[:total_days//4])
            end_balance = sum(t["amount"] for t in transactions[-total_days//4:])
            
            if abs(end_balance - start_balance) < volatility:
                trend_direction = "stable"
                trend_strength = Decimal("0.3")
            else:
                trend_direction = "increasing" if end_balance > start_balance else "decreasing"
                trend_strength = min(
                    Decimal("1"),
                    abs(end_balance - start_balance) / (volatility * Decimal("10"))
                )

        # Calculate seasonal factors
        seasonal_factors = {}
        for trans in transactions:
            month = trans["date"].strftime("%B").lower()
            if month not in seasonal_factors:
                seasonal_factors[month] = Decimal("0")
            seasonal_factors[month] += trans["amount"]

        # Calculate confidence score based on data quality
        # Start with a base confidence of 0.7
        base_confidence = Decimal("0.7")
        
        # Adjust for number of transactions (more transactions = higher confidence)
        transaction_factor = min(Decimal("0.2"), Decimal(str(len(transactions))) / Decimal("10"))
        
        # Adjust for volatility (lower volatility relative to average = higher confidence)
        volatility_ratio = volatility / (abs(avg_daily_change) + Decimal("0.01"))
        volatility_factor = max(Decimal("0"), Decimal("0.1") * (Decimal("1") - min(volatility_ratio, Decimal("1"))))
        
        # Calculate final confidence score with explicit Decimal conversions
        confidence_score = min(
            base_confidence + transaction_factor + volatility_factor,
            Decimal("1.0")
        )
        # Ensure minimum confidence of 0.1 with explicit Decimal comparison
        confidence_score = max(confidence_score, Decimal("0.1"))

        return HistoricalTrendMetrics(
            average_daily_change=avg_daily_change,
            volatility=volatility,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            seasonal_factors=seasonal_factors,
            confidence_score=confidence_score
        )

    async def _analyze_historical_periods(
        self,
        transactions: List[Dict],
        start_date: date,
        end_date: date
    ) -> List[HistoricalPeriodAnalysis]:
        """Analyze transactions in specific periods (e.g., monthly)."""
        periods = []
        current_start = start_date

        while current_start < end_date:
            # Define period end (monthly periods)
            if current_start.month == 12:
                current_end = datetime(current_start.year + 1, 1, 1, tzinfo=ZoneInfo("UTC")) - timedelta(days=1)
            else:
                current_end = datetime(current_start.year, current_start.month + 1, 1, tzinfo=ZoneInfo("UTC")) - timedelta(days=1)
            
            # Filter transactions for current period
            period_transactions = [
                t for t in transactions
                if current_start <= t["date"] <= current_end
            ]
            
            if period_transactions:
                # Calculate period metrics with explicit Decimal conversions
                inflow = Decimal("0")
                outflow = Decimal("0")
                for t in period_transactions:
                    if t["type"] == "income":
                        inflow += abs(t["amount"])
                    else:  # payment
                        outflow += abs(t["amount"])
                
                # Find significant events (large transactions)
                # Calculate averages by transaction type
                type_averages = {}
                for t in period_transactions:
                    if t["type"] not in type_averages:
                        type_averages[t["type"]] = []
                    type_averages[t["type"]].append(abs(t["amount"]))
                
                # Calculate average for each type with explicit Decimal conversions
                type_thresholds = {}
                for t_type, amounts in type_averages.items():
                    avg = Decimal(str(mean(amounts)))
                    # Lower threshold to 1.1x for better detection
                    type_thresholds[t_type] = avg * Decimal("1.1")
                
                significant_events = []
                for t in period_transactions:
                    threshold = type_thresholds.get(t["type"], Decimal("0"))
                    if abs(t["amount"]) > threshold:
                        significant_events.append({
                            "date": t["date"].isoformat(),
                            "description": f"Large {t['type']} in {t['category']} ({abs(t['amount'])})"
                        })

                periods.append(HistoricalPeriodAnalysis(
                    period_start=current_start,
                    period_end=current_end,
                    average_balance=mean(t["amount"] for t in period_transactions),
                    peak_balance=max(t["amount"] for t in period_transactions),
                    lowest_balance=min(t["amount"] for t in period_transactions),
                    total_inflow=inflow,
                    total_outflow=outflow,
                    net_change=inflow - outflow,
                    significant_events=significant_events
                ))
            
            current_start = current_end + timedelta(days=1)
            if not isinstance(current_start, datetime):
                current_start = datetime.combine(current_start, datetime.min.time(), tzinfo=ZoneInfo("UTC"))

        return periods

    async def _get_projected_transactions(
        self,
        account: Account,
        start_date: date,
        end_date: date,
        include_pending: bool,
        include_recurring: bool
    ) -> List[Dict]:
        """Get projected transactions for an account in the specified date range."""
        transactions = []

        # Get bills due in the date range
        bills_query = (
            select(Liability)
            .where(
                Liability.primary_account_id == account.id,
                Liability.due_date.between(start_date, end_date)
            )
        )
        if not include_pending:
            bills_query = bills_query.where(Liability.status != "pending")
        bills = (await self.db.execute(bills_query)).scalars().all()
        
        for bill in bills:
            transactions.append({
                "date": bill.due_date,
                "amount": -bill.amount,  # Negative for outflow
                "description": f"Bill: {bill.name}",
                "type": "bill"
            })

        # Get expected income in the date range
        income_query = (
            select(Income)
            .where(
                Income.account_id == account.id,
                Income.date.between(start_date, end_date)
            )
        )
        if not include_pending:
            income_query = income_query.where(Income.deposited == True)
        income_entries = (await self.db.execute(income_query)).scalars().all()

        for income in income_entries:
            transactions.append({
                "date": income.date,
                "amount": income.amount,  # Positive for inflow
                "description": f"Income: {income.source}",
                "type": "income"
            })

        # Add recurring transactions if requested
        if include_recurring:
            recurring_query = (
                select(Liability)
                .where(
                    Liability.primary_account_id == account.id,
                    Liability.recurring == True
                )
            )
            recurring_bills = (await self.db.execute(recurring_query)).scalars().all()
            
            for bill in recurring_bills:
                # Generate recurring instances within date range
                current_date = bill.due_date
                while current_date <= end_date:
                    if current_date >= start_date:
                        transactions.append({
                            "date": current_date,
                            "amount": -bill.amount,
                            "description": f"Recurring Bill: {bill.name}",
                            "type": "recurring_bill"
                        })
                    # Advance to next occurrence based on recurrence pattern
                    # This is a simplified version - would need more complex logic
                    # for different recurrence patterns
                    # Advance to next occurrence
                    next_month = current_date.month + 1
                    next_year = current_date.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    current_date = date(next_year, next_month, current_date.day)

        # Sort transactions by date
        return sorted(transactions, key=lambda x: x["date"])

    async def _analyze_seasonality(
        self,
        transactions: List[Dict]
    ) -> SeasonalityAnalysis:
        """Analyze seasonal patterns in transactions."""
        # Initialize pattern dictionaries
        monthly_patterns = {i: Decimal("0") for i in range(1, 13)}
        day_of_week_patterns = {i: Decimal("0") for i in range(7)}
        day_of_month_patterns = {i: Decimal("0") for i in range(1, 32)}
        holiday_impacts = {}

        # Analyze patterns
        for trans in transactions:
            trans_date = trans["date"]
            amount = trans["amount"]

            # Monthly patterns
            monthly_patterns[trans_date.month] += amount

            # Day of week patterns
            day_of_week_patterns[trans_date.weekday()] += amount

            # Day of month patterns
            day_of_month_patterns[trans_date.day] += amount

            # Holiday impacts
            for holiday, holiday_date in self._holidays.items():
                # Check if transaction is within 7 days before or after the holiday
                holiday_date_this_year = holiday_date.replace(year=trans_date.year)
                days_to_holiday = (trans_date - holiday_date_this_year).days
                if -7 <= days_to_holiday <= 7:  # Within 7 days before or after holiday
                    if holiday not in holiday_impacts:
                        holiday_impacts[holiday] = Decimal("0")
                    holiday_impacts[holiday] += amount

        # Calculate seasonal strength
        monthly_variance = stdev(monthly_patterns.values()) if len(set(monthly_patterns.values())) > 1 else 0
        daily_variance = stdev(day_of_month_patterns.values()) if len(set(day_of_month_patterns.values())) > 1 else 0
        
        max_variance = max(monthly_variance, daily_variance)
        total_volume = sum(abs(t["amount"]) for t in transactions)
        
        seasonal_strength = min(
            Decimal("1"),
            Decimal(str(max_variance)) / (total_volume / Decimal("12"))
        ) if total_volume > 0 else Decimal("0")

        return SeasonalityAnalysis(
            monthly_patterns=monthly_patterns,
            day_of_week_patterns=day_of_week_patterns,
            day_of_month_patterns=day_of_month_patterns,
            holiday_impacts=holiday_impacts,
            seasonal_strength=seasonal_strength
        )

async def calculate_forecast(
    db: AsyncSession,
    account_id: int,
    start_date: date,
    end_date: date
) -> List[Dict[str, Union[date, Decimal]]]:
    """Calculate daily cashflow forecast for the specified date range."""
    # Get account with relationships
    account = await db.get(Account, account_id)
    if not account:
        raise ValueError(f"Account with id {account_id} not found")
    
    # Get all unpaid liabilities in date range with relationships
    result = await db.execute(
        select(Liability)
        .outerjoin(Payment)
        .where(
            Liability.primary_account_id == account_id,
            Liability.due_date >= start_date,
            Liability.due_date <= end_date,
            Payment.id == None  # No associated payments
        )
    )
    liabilities = result.scalars().all()
    
    # Get all income in date range with relationships
    result = await db.execute(
        select(Income)
        .where(
            Income.account_id == account_id,
            Income.date >= start_date,
            Income.date <= end_date,
            Income.deposited == False
        )
    )
    income_entries = result.scalars().all()
    
    # Create daily forecast
    forecast = []
    current_balance = account.available_balance
    current_date = start_date
    
    while current_date <= end_date:
        # Add liabilities due on this date
        liabilities_due = sum(
            liability.amount for liability in liabilities
            if liability.due_date == current_date
        )
        current_balance -= liabilities_due
        
        # Add income on this date
        income_received = sum(
            income.amount for income in income_entries
            if income.date == current_date
        )
        current_balance += income_received
        
        forecast.append({
            "date": current_date,
            "balance": current_balance
        })
        
        current_date += timedelta(days=1)
    
    return forecast

async def calculate_required_funds(
    db: AsyncSession,
    account_id: int,
    start_date: date,
    end_date: date
) -> Decimal:
    """Calculate total required funds for bills in the specified date range."""
    result = await db.execute(
        select(Liability)
        .outerjoin(Payment)
        .where(
            Liability.primary_account_id == account_id,
            Liability.due_date >= start_date,
            Liability.due_date <= end_date,
            Payment.id == None  # No associated payments
        )
    )
    liabilities = result.scalars().all()
    return sum(liability.amount for liability in liabilities)

def calculate_daily_deficit(min_amount: Decimal, days: int) -> Decimal:
    """Calculate daily deficit needed to cover minimum required amount."""
    if min_amount >= 0:
        return Decimal("0.00")
    # Round to 2 decimal places with ROUND_HALF_UP
    return Decimal(str(round(float(abs(min_amount)) / days, 2)))

def calculate_yearly_deficit(daily_deficit: Decimal) -> Decimal:
    """Calculate yearly deficit based on daily deficit."""
    return daily_deficit * 365

def calculate_required_income(
    yearly_deficit: Decimal,
    tax_rate: Decimal = Decimal("0.80")
) -> Decimal:
    """
    Calculate required gross income to cover yearly deficit.
    Default tax_rate of 0.80 assumes 20% tax rate.
    """
    return yearly_deficit / tax_rate

async def calculate_custom_forecast(
    db: AsyncSession,
    params: "CustomForecastParameters"  # type: ignore
) -> "CustomForecastResponse":  # type: ignore
    """Calculate a custom forecast based on provided parameters."""
    results = []
    total_confidence = Decimal("0.0")
    summary_stats: Dict[str, Decimal] = {
        "total_projected_income": Decimal("0.0"),
        "total_projected_expenses": Decimal("0.0"),
        "average_confidence": Decimal("0.0"),
        "min_balance": Decimal("999999999.99"),
        "max_balance": Decimal("-999999999.99")
    }

    # Get accounts to analyze
    accounts_query = select(Account)
    if params.account_ids:
        accounts_query = accounts_query.where(Account.id.in_(params.account_ids))
    accounts = (await db.execute(accounts_query)).scalars().all()
    
    if not accounts:
        raise ValueError("No valid accounts found for analysis")

    # Initialize starting balances
    current_balances = {
        acc.id: acc.available_balance for acc in accounts
    }

    # Get liabilities query
    liabilities_query = (
        select(Liability)
        .outerjoin(Payment)
        .where(
            Liability.due_date >= params.start_date,
            Liability.due_date <= params.end_date,
            Payment.id == None  # No associated payments
        )
    )
    if params.account_ids:
        liabilities_query = liabilities_query.where(
            Liability.primary_account_id.in_(params.account_ids)
        )
    if params.categories:
        liabilities_query = liabilities_query.where(
            Liability.category_id.in_(
                select(Category.id).where(Category.name.in_(params.categories))
            )
        )
    
    # Get income query
    income_query = (
        select(Income)
        .where(
            Income.date >= params.start_date,
            Income.date <= params.end_date,
            Income.deposited == False
        )
    )
    if params.account_ids:
        income_query = income_query.where(
            Income.account_id.in_(params.account_ids)
        )
    
    # Fetch data
    liabilities = (await db.execute(liabilities_query)).scalars().all()
    income_entries = (await db.execute(income_query)).scalars().all()
    
    current_date = params.start_date
    days_processed = 0
    
    while current_date <= params.end_date:
        # Calculate daily projections
        daily_expenses = Decimal("0.0")
        daily_income = Decimal("0.0")
        contributing_factors: Dict[str, Decimal] = {}
        risk_factors: Dict[str, Decimal] = {}
        
        # Process liabilities
        daily_liabilities = [
            l for l in liabilities if l.due_date == current_date
        ]
        for liability in daily_liabilities:
            daily_expenses += liability.amount
            # Get category name from the database
            category_query = select(Category).where(Category.id == liability.category_id)
            category = (await db.execute(category_query)).scalar_one()
            contributing_factors[f"liability_{category.name}"] = liability.amount
            
            # Risk assessment for liability
            if liability.amount > current_balances[liability.primary_account_id]:
                risk_factors["insufficient_funds"] = Decimal("0.3")
        
        # Process income
        daily_income_entries = [
            i for i in income_entries if i.date == current_date
        ]
        for income in daily_income_entries:
            daily_income += income.amount
            contributing_factors[f"income_{income.source}"] = income.amount
        
        # Update balances
        for acc_id in current_balances:
            # Simplified balance update - in reality would need more complex logic
            # for handling split payments and income distribution
            current_balances[acc_id] += (daily_income / len(current_balances))
            current_balances[acc_id] -= (daily_expenses / len(current_balances))
        
        # Calculate confidence score
        base_confidence = Decimal("1.0")
        if risk_factors:
            base_confidence -= sum(risk_factors.values())
        
        confidence_score = max(min(base_confidence, Decimal("1.0")), Decimal("0.0"))
        
        # Create forecast result
        total_balance = sum(current_balances.values())
        result = {
            "date": current_date,
            "projected_balance": total_balance,
            "projected_income": daily_income,
            "projected_expenses": daily_expenses,
            "confidence_score": confidence_score,
            "contributing_factors": contributing_factors,
            "risk_factors": risk_factors
        }
        
        results.append(result)
        
        # Update summary statistics
        summary_stats["total_projected_income"] += daily_income
        summary_stats["total_projected_expenses"] += daily_expenses
        summary_stats["min_balance"] = min(summary_stats["min_balance"], total_balance)
        summary_stats["max_balance"] = max(summary_stats["max_balance"], total_balance)
        total_confidence += confidence_score
        days_processed += 1
        
        current_date += timedelta(days=1)
    
    # Calculate average confidence
    summary_stats["average_confidence"] = (
        total_confidence / days_processed if days_processed > 0 else Decimal("0.0")
    )
    
    return CustomForecastResponse(
        parameters=params,
        results=[
            CustomForecastResult(
                date=r["date"],
                projected_balance=r["projected_balance"],
                projected_income=r["projected_income"],
                projected_expenses=r["projected_expenses"],
                confidence_score=r["confidence_score"],
                contributing_factors=r["contributing_factors"],
                risk_factors=r["risk_factors"]
            ) for r in results
        ],
        overall_confidence=summary_stats["average_confidence"],
        summary_statistics=summary_stats,
        timestamp=date.today()
    )
