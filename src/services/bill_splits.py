from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.decimal_precision import DecimalPrecision
from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability
from src.schemas.bill_splits import (
    BillSplitCreate,
    BillSplitSuggestionResponse,
    BillSplitUpdate,
    BillSplitValidation,
    BulkOperationError,
    BulkOperationResult,
    BulkSplitOperation,
    HistoricalAnalysis,
    ImpactAnalysis,
    OptimizationMetrics,
    OptimizationSuggestion,
    PatternMetrics,
    SplitPattern,
    SplitSuggestion,
)


class BillSplitValidationError(Exception):
    """Custom exception for bill split validation errors"""

    pass


class BillSplitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_bill_splits(self, liability_id: int) -> List[BillSplit]:
        """Get all splits for a specific liability."""
        stmt = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_account_splits(self, account_id: int) -> List[BillSplit]:
        """Get all splits for a specific account."""
        stmt = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.account_id == account_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def create_split(
        self, liability_id: int, account_id: int, amount: Decimal
    ) -> BillSplit:
        """Create a new bill split (internal use)."""
        split = BillSplit(
            liability_id=liability_id,
            account_id=account_id,
            amount=amount,
            created_at=date.today(),
            updated_at=date.today(),
        )
        self.db.add(split)
        await self.db.flush()

        # Fetch fresh copy with relationships
        stmt = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .filter(BillSplit.id == split.id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def create_bill_split(self, split: BillSplitCreate) -> BillSplit:
        """Create a new bill split (API use)."""
        # Verify liability exists
        stmt = (
            select(Liability)
            .options(joinedload(Liability.splits))
            .where(Liability.id == split.liability_id)
        )
        result = await self.db.execute(stmt)
        liability = result.unique().scalar_one_or_none()
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {split.liability_id} not found"
            )

        # Verify account exists and has sufficient balance/credit
        stmt = select(Account).where(Account.id == split.account_id)
        result = await self.db.execute(stmt)
        account = result.unique().scalar_one_or_none()
        if not account:
            raise BillSplitValidationError(
                f"Account with id {split.account_id} not found"
            )

        # Validate account has sufficient balance/credit
        if account.type == "credit":
            available_credit = (
                account.total_limit + account.available_balance
                if account.total_limit
                else Decimal("0")
            )
            if split.amount > available_credit:
                raise BillSplitValidationError(
                    f"Account {account.name} has insufficient credit "
                    f"(needs {split.amount}, has {available_credit})"
                )
        else:  # checking/savings
            if split.amount > account.available_balance:
                raise BillSplitValidationError(
                    f"Account {account.name} has insufficient balance "
                    f"(needs {split.amount}, has {account.available_balance})"
                )

        return await self.create_split(
            liability_id=split.liability_id,
            account_id=split.account_id,
            amount=split.amount,
        )

    async def update_bill_split(
        self, split_id: int, split: BillSplitUpdate
    ) -> Optional[BillSplit]:
        """Update an existing bill split."""
        stmt = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.id == split_id)
        )
        result = await self.db.execute(stmt)
        db_split = result.unique().scalar_one_or_none()
        if not db_split:
            return None

        if split.amount is not None:
            # Validate new amount against account balance/credit
            stmt = select(Account).where(Account.id == db_split.account_id)
            result = await self.db.execute(stmt)
            account = result.unique().scalar_one()

            if account.type == "credit":
                available_credit = (
                    account.total_limit + account.available_balance
                    if account.total_limit
                    else Decimal("0")
                )
                if split.amount > available_credit:
                    raise BillSplitValidationError(
                        f"Account {account.name} has insufficient credit "
                        f"(needs {split.amount}, has {available_credit})"
                    )
            else:  # checking/savings
                if split.amount > account.available_balance:
                    raise BillSplitValidationError(
                        f"Account {account.name} has insufficient balance "
                        f"(needs {split.amount}, has {account.available_balance})"
                    )

            db_split.amount = split.amount
            db_split.updated_at = date.today()

        await self.db.flush()

        # Fetch fresh copy with relationships
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def delete_bill_split(self, split_id: int) -> bool:
        """Delete a specific bill split. Returns True if successful."""
        result = await self.db.execute(
            delete(BillSplit).where(BillSplit.id == split_id)
        )
        return result.rowcount > 0

    async def delete_bill_splits(self, liability_id: int) -> None:
        """Delete all splits for a liability."""
        await self.db.execute(
            delete(BillSplit).where(BillSplit.liability_id == liability_id)
        )
        await self.db.commit()

    async def validate_splits(
        self, validation: BillSplitValidation
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate bill splits against multiple criteria:
        1. Sum of splits equals liability amount
        2. All accounts exist and have sufficient balance/credit
        3. No duplicate accounts
        4. All amounts are positive

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Verify liability exists
            stmt = select(Liability).where(Liability.id == validation.liability_id)
            result = await self.db.execute(stmt)
            liability = result.unique().scalar_one_or_none()
            if not liability:
                return False, f"Liability with id {validation.liability_id} not found"

            # Verify total amount matches liability
            if abs(validation.total_amount - liability.amount) > Decimal("0.01"):
                return False, (
                    f"Total amount {validation.total_amount} does not match "
                    f"liability amount {liability.amount}"
                )

            # Get all accounts involved in splits
            account_ids = [split.account_id for split in validation.splits]
            stmt = select(Account).where(Account.id.in_(account_ids))
            result = await self.db.execute(stmt)
            accounts = {acc.id: acc for acc in result.scalars().all()}

            # Verify all accounts exist
            missing_accounts = set(account_ids) - set(accounts.keys())
            if missing_accounts:
                return False, f"Accounts not found: {missing_accounts}"

            # Check for duplicate accounts
            if len(account_ids) != len(set(account_ids)):
                return False, "Duplicate accounts found in splits"

            # Validate each split
            for split in validation.splits:
                account = accounts[split.account_id]

                # Validate account has sufficient balance/credit
                if account.type == "credit":
                    available_credit = (
                        account.total_limit + account.available_balance
                        if account.total_limit
                        else Decimal("0")
                    )
                    if split.amount > available_credit:
                        return False, (
                            f"Account {account.name} has insufficient credit "
                            f"(needs {split.amount}, has {available_credit})"
                        )
                else:  # checking/savings
                    if split.amount > account.available_balance:
                        return False, (
                            f"Account {account.name} has insufficient balance "
                            f"(needs {split.amount}, has {account.available_balance})"
                        )

            return True, None

        except Exception as e:
            return False, str(e)

    def _generate_pattern_id(self, splits: List[Dict[str, any]]) -> str:
        """Generate a unique pattern ID from a set of splits."""
        # Sort splits by account ID to ensure consistent pattern IDs
        sorted_splits = sorted(splits, key=lambda x: x["account_id"])
        pattern_parts = []
        for split in sorted_splits:
            # Use percentage of total to identify similar patterns with different absolute amounts
            pattern_parts.append(f"{split['account_id']}:{split['percentage']:.2f}")
        return "|".join(pattern_parts)

    def _calculate_confidence_score(
        self, occurrences: int, total_patterns: int, first_seen: date, last_seen: date
    ) -> float:
        """Calculate a confidence score based on frequency and recency."""
        today = date.today()
        days_since_first = (today - first_seen).days
        days_since_last = (today - last_seen).days

        # Frequency score (0-0.6)
        # Adjust frequency score based on proportion of total patterns
        frequency_score = min(0.6, (occurrences / max(total_patterns, 1)) * 0.6)

        # Recency score (0-0.4)
        # More recent patterns get higher scores
        max_history = 365 * 2  # 2 years
        days_since_last = min(days_since_last, max_history)  # Cap at max history
        recency_score = 0.4 * (1 - (days_since_last / max_history))

        # Weight recent patterns more heavily if they occur frequently
        weighted_score = (frequency_score * 0.7) + (recency_score * 0.3)

        return min(0.9, max(0.1, weighted_score))  # Ensure score is between 0.1 and 0.9

    async def analyze_historical_patterns(
        self, liability_id: int
    ) -> HistoricalAnalysis:
        """Perform comprehensive historical analysis of bill splits."""
        # Get the liability and its category
        stmt = (
            select(Liability)
            .options(joinedload(Liability.category))
            .where(Liability.id == liability_id)
        )
        result = await self.db.execute(stmt)
        liability = result.unique().scalar_one_or_none()
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {liability_id} not found"
            )

        # Get all splits for similar liabilities
        similar_stmt = (
            select(BillSplit)
            .join(BillSplit.liability)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(
                or_(
                    Liability.name == liability.name,
                    Liability.category_id == liability.category_id,
                )
            )
            .order_by(BillSplit.created_at)
        )
        result = await self.db.execute(similar_stmt)
        all_splits = result.unique().scalars().all()

        # Group splits by liability
        liability_splits: Dict[int, List[Dict]] = {}
        total_splits = 0
        for split in all_splits:
            total_splits += 1
            if split.liability_id not in liability_splits:
                liability_splits[split.liability_id] = []

            # Calculate total for this liability's splits
            liability_total = sum(
                s.amount for s in all_splits if s.liability_id == split.liability_id
            )

            liability_splits[split.liability_id].append(
                {
                    "account_id": split.account_id,
                    "amount": split.amount,
                    "percentage": (
                        (split.amount / liability_total) if liability_total else 0
                    ),
                    "created_at": split.created_at,
                }
            )

        # Analyze patterns
        patterns: Dict[str, Dict] = {}
        account_usage: Dict[int, int] = {}

        for splits in liability_splits.values():
            pattern_id = self._generate_pattern_id(splits)

            if pattern_id not in patterns:
                total_amount = sum(split["amount"] for split in splits)
                patterns[pattern_id] = {
                    "pattern_id": pattern_id,
                    "account_splits": {
                        split["account_id"]: split["percentage"] for split in splits
                    },
                    "total_occurrences": 0,
                    "first_seen": splits[0]["created_at"],
                    "last_seen": splits[0]["created_at"],
                    "total_amount": total_amount,
                    "amounts": [],
                }

            pattern = patterns[pattern_id]
            pattern["total_occurrences"] += 1
            pattern["amounts"].append(sum(split["amount"] for split in splits))
            pattern["last_seen"] = max(pattern["last_seen"], splits[-1]["created_at"])

            # Track account usage
            for split in splits:
                account_usage[split["account_id"]] = (
                    account_usage.get(split["account_id"], 0) + 1
                )

        # Convert patterns to SplitPattern objects
        pattern_objects = []
        for pattern in patterns.values():
            average_total = sum(pattern["amounts"]) / len(pattern["amounts"])
            confidence_score = self._calculate_confidence_score(
                pattern["total_occurrences"],
                len(liability_splits),
                pattern["first_seen"],
                pattern["last_seen"],
            )

            pattern_objects.append(
                SplitPattern(
                    pattern_id=pattern["pattern_id"],
                    account_splits=pattern["account_splits"],
                    total_occurrences=pattern["total_occurrences"],
                    first_seen=pattern["first_seen"],
                    last_seen=pattern["last_seen"],
                    average_total=average_total,
                    confidence_score=confidence_score,
                )
            )

        # Sort patterns by confidence score
        pattern_objects.sort(key=lambda x: x.confidence_score, reverse=True)

        # Calculate metrics
        metrics = PatternMetrics(
            total_splits=total_splits,
            unique_patterns=len(patterns),
            most_common_pattern=pattern_objects[0] if pattern_objects else None,
            average_splits_per_bill=(
                total_splits / len(liability_splits) if liability_splits else 0
            ),
            account_usage_frequency=account_usage,
        )

        # Group patterns by category
        category_patterns: Dict[int, List[SplitPattern]] = {}
        if liability.category_id:
            category_patterns[liability.category_id] = pattern_objects

        # Analyze seasonal patterns (group by month)
        seasonal_patterns: Dict[str, List[SplitPattern]] = {}
        for pattern in pattern_objects:
            month = pattern.last_seen.strftime("%B")
            if month not in seasonal_patterns:
                seasonal_patterns[month] = []
            seasonal_patterns[month].append(pattern)

        return HistoricalAnalysis(
            liability_id=liability_id,
            analysis_date=date.today(),
            patterns=pattern_objects,
            metrics=metrics,
            category_patterns=category_patterns,
            seasonal_patterns=seasonal_patterns,
        )

    async def get_historical_split_patterns(
        self, liability_id: int, min_frequency: int = 2
    ) -> List[Dict[int, Decimal]]:
        """
        Analyze historical split patterns for similar liabilities.
        Returns a list of account-to-amount mappings that occur frequently.
        """
        # Get the liability to find similar ones
        stmt = select(Liability).where(Liability.id == liability_id)
        result = await self.db.execute(stmt)
        liability = result.unique().scalar_one_or_none()
        if not liability:
            return []

        # Find similar liabilities (same name or category)
        similar_liabilities = select(Liability.id).where(
            and_(
                Liability.id != liability_id,
                or_(
                    Liability.name == liability.name,
                    Liability.category_id == liability.category_id,
                ),
            )
        )
        result = await self.db.execute(similar_liabilities)
        similar_ids = [r[0] for r in result.all()]
        if not similar_ids:
            return []

        # Get splits for similar liabilities
        splits_stmt = select(BillSplit).where(BillSplit.liability_id.in_(similar_ids))
        result = await self.db.execute(splits_stmt)
        splits = result.scalars().all()

        # Analyze patterns
        patterns: Dict[str, Dict] = {}
        for split in splits:
            pattern_key = f"{split.liability_id}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {"accounts": {}, "total": Decimal("0")}
            patterns[pattern_key]["accounts"][split.account_id] = split.amount
            patterns[pattern_key]["total"] += split.amount

        # Convert amounts to percentages and find common patterns
        normalized_patterns: Dict[str, int] = {}
        for pattern in patterns.values():
            if abs(pattern["total"]) < Decimal("0.01"):
                continue

            # Create normalized pattern string (account:percentage) with exact decimal places
            total = pattern["total"]
            pattern_str = "|".join(
                f"{acc}:{amt}:{total}"  # Store original amounts and total instead of percentages
                for acc, amt in sorted(pattern["accounts"].items())
            )
            normalized_patterns[pattern_str] = (
                normalized_patterns.get(pattern_str, 0) + 1
            )

        # Filter by minimum frequency and convert back to account:amount mappings
        frequent_patterns = []
        for pattern_str, freq in normalized_patterns.items():
            if freq >= min_frequency:
                pattern = {}
                for acc_split in pattern_str.split("|"):
                    acc_id, amount, total = acc_split.split(":")
                    # Calculate new amount while preserving original proportions
                    # Use DecimalPrecision for rounding to ensure proper handling
                    proportion = Decimal(amount) / Decimal(total)
                    new_amount = proportion * liability.amount
                    pattern[int(acc_id)] = DecimalPrecision.round_for_display(
                        new_amount
                    )
                frequent_patterns.append(pattern)

        return frequent_patterns

    async def suggest_splits(self, liability_id: int) -> BillSplitSuggestionResponse:
        """
        Generate split suggestions for a liability based on:
        1. Historical patterns
        2. Available balances
        3. Credit limits
        """
        # Get the liability
        stmt = select(Liability).where(Liability.id == liability_id)
        result = await self.db.execute(stmt)
        liability = result.unique().scalar_one_or_none()
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {liability_id} not found"
            )

        # Get all active accounts
        stmt = select(Account)
        result = await self.db.execute(stmt)
        accounts = result.scalars().all()

        # Get historical patterns
        patterns = await self.get_historical_split_patterns(liability_id)

        if patterns:
            # Use the most common historical pattern
            pattern = patterns[0]
            suggestions = []
            for account_id, amount in pattern.items():
                account = next((a for a in accounts if a.id == account_id), None)
                if not account:
                    continue

                suggestions.append(
                    SplitSuggestion(
                        account_id=account_id,
                        amount=amount,
                        confidence_score=0.8,
                        reason=f"Based on historical split pattern for {liability.name}",
                    )
                )

            return BillSplitSuggestionResponse(
                liability_id=liability_id,
                total_amount=liability.amount,
                suggestions=suggestions,
                historical_pattern=True,
                pattern_frequency=len(patterns),
            )

        # If no historical pattern, suggest based on available funds
        suggestions = []
        remaining_amount = liability.amount

        # First try primary account
        primary_account = next(
            (a for a in accounts if a.id == liability.primary_account_id), None
        )
        if primary_account:
            available = (
                primary_account.total_limit + primary_account.available_balance
                if primary_account.type == "credit" and primary_account.total_limit
                else primary_account.available_balance
            )
            if available >= remaining_amount:
                suggestions.append(
                    SplitSuggestion(
                        account_id=primary_account.id,
                        amount=remaining_amount,
                        confidence_score=0.6,
                        reason="Primary account has sufficient funds",
                    )
                )
                remaining_amount = Decimal("0")

        # If primary account can't cover it, suggest splits across available accounts
        if remaining_amount > 0:
            # Sort accounts by available funds (descending)
            # Get all accounts except primary
            other_accounts = [
                a for a in accounts if a.id != liability.primary_account_id
            ]

            # Calculate available funds for each account
            def get_available_funds(account):
                if account.type == "credit" and account.total_limit:
                    return account.total_limit + account.available_balance
                return account.available_balance

            # Try primary account first with partial amount
            if primary_account:
                available = get_available_funds(primary_account)
                if available > 0:
                    split_amount = min(remaining_amount, available)
                    suggestions.append(
                        SplitSuggestion(
                            account_id=primary_account.id,
                            amount=split_amount,
                            confidence_score=0.4,
                            reason=f"Primary account has {available:.2f} available",
                        )
                    )
                    remaining_amount -= split_amount

            # Sort other accounts by available funds
            sorted_accounts = sorted(
                other_accounts, key=get_available_funds, reverse=True
            )

            for account in sorted_accounts:
                if remaining_amount <= 0:
                    break

                available = (
                    account.total_limit + account.available_balance
                    if account.type == "credit" and account.total_limit
                    else account.available_balance
                )

                if available > 0:
                    split_amount = min(remaining_amount, available)
                    suggestions.append(
                        SplitSuggestion(
                            account_id=account.id,
                            amount=split_amount,
                            confidence_score=0.4,
                            reason=f"Account has {available:.2f} available",
                        )
                    )
                    remaining_amount -= split_amount

        return BillSplitSuggestionResponse(
            liability_id=liability_id,
            total_amount=liability.amount,
            suggestions=suggestions,
            historical_pattern=False,
        )

    async def calculate_split_totals(self, liability_id: int) -> Decimal:
        """Calculate the total amount of all splits for a given liability."""
        stmt = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        splits = result.unique().scalars().all()

        # Use DecimalPrecision to handle the sum with proper precision
        total = sum(split.amount for split in splits)
        return DecimalPrecision.round_for_calculation(total)

    async def process_bulk_operation(
        self, operation: BulkSplitOperation
    ) -> BulkOperationResult:
        """
        Process a bulk bill split operation with transaction support.
        Validates and processes multiple splits in a single transaction.
        """
        processed_count = len(operation.splits)
        result = BulkOperationResult(
            success=True,
            processed_count=processed_count,
            success_count=0,
            failure_count=processed_count,  # Initially all are considered failed
            successful_splits=list(),
            errors=list(),
        )

        try:
            # Start transaction
            async with self.db.begin_nested() as nested:
                for index, split in enumerate(operation.splits):
                    try:
                        # Process based on operation type
                        if operation.operation_type == "create":
                            processed_split = await self.create_bill_split(split)
                            result.successful_splits = [
                                *result.successful_splits,
                                processed_split,
                            ]
                            result.success_count += 1
                            result.failure_count -= 1
                        elif operation.operation_type == "update":
                            if not hasattr(split, "id"):
                                raise ValueError("Update operation requires split ID")
                            processed_split = await self.update_bill_split(
                                split.id, split
                            )
                            if processed_split:
                                result.successful_splits = [
                                    *result.successful_splits,
                                    processed_split,
                                ]
                                result.success_count += 1
                                result.failure_count -= 1
                            else:
                                raise ValueError(f"Split with ID {split.id} not found")

                    except Exception as e:
                        result.errors = [
                            *result.errors,
                            BulkOperationError(
                                index=index,
                                split_data=split,
                                error_message=str(e),
                                error_type=(
                                    "validation"
                                    if isinstance(e, BillSplitValidationError)
                                    else "processing"
                                ),
                            ),
                        ]
                        if operation.validate_only:
                            result.success = False
                            await nested.rollback()
                            return result
                        continue

                if operation.validate_only:
                    await nested.rollback()
                else:
                    await nested.commit()

        except Exception as e:
            result.success = False
            result.errors = [
                *result.errors,
                BulkOperationError(
                    index=-1,
                    split_data=operation.splits[0] if operation.splits else None,
                    error_message=f"Transaction error: {str(e)}",
                    error_type="transaction",
                ),
            ]
            return result

        result.success = result.failure_count == 0 and len(result.errors) == 0
        return result

    async def calculate_optimization_metrics(
        self, splits: List[BillSplitCreate], accounts: Dict[int, Account]
    ) -> OptimizationMetrics:
        """Calculate optimization metrics for a set of splits."""
        credit_utilization = {}
        balance_impact = {}
        total_risk_score = 0
        total_accounts = len(splits)

        for split in splits:
            account = accounts[split.account_id]

            # Calculate credit utilization for credit accounts
            if account.type == "credit" and account.total_limit:
                current_balance = abs(account.available_balance)
                new_balance = current_balance + split.amount
                utilization = (new_balance / account.total_limit) * 100
                credit_utilization[account.id] = utilization

                # Higher utilization = higher risk
                risk_factor = min(
                    Decimal("1.0"), utilization / Decimal("90")
                )  # 90% utilization = max risk
                total_risk_score += risk_factor

            # Calculate balance impact for all accounts
            if account.type == "credit":
                balance_impact[account.id] = -split.amount
            else:
                balance_impact[account.id] = -split.amount
                # Higher percentage of available balance = higher risk
                risk_factor = min(
                    Decimal("1.0"),
                    split.amount / max(account.available_balance, Decimal("0.01")),
                )
                total_risk_score += risk_factor

        # Calculate average risk score (0-1)
        risk_score = (
            total_risk_score / Decimal(total_accounts)
            if total_accounts > 0
            else Decimal("1.0")
        )

        # Calculate optimization score (inverse of risk score)
        optimization_score = Decimal("1.0") - (
            risk_score * Decimal("0.8")
        )  # Scale to allow some room for improvement

        return OptimizationMetrics(
            credit_utilization=credit_utilization,
            balance_impact=balance_impact,
            risk_score=risk_score,
            optimization_score=optimization_score,
        )

    async def analyze_split_impact(
        self, splits: List[BillSplitCreate]
    ) -> ImpactAnalysis:
        """Analyze the impact of a split configuration."""
        # Get all accounts involved
        account_ids = [split.account_id for split in splits]
        stmt = select(Account).where(Account.id.in_(account_ids))
        result = await self.db.execute(stmt)
        accounts = {acc.id: acc for acc in result.scalars().all()}

        # Calculate current metrics
        metrics = await self.calculate_optimization_metrics(splits, accounts)

        # Calculate short-term impact (30 days)
        short_term_impact = {}
        for split in splits:
            account = accounts[split.account_id]
            # Project 30-day impact considering recurring bills
            stmt = (
                select(func.sum(BillSplit.amount))
                .join(BillSplit.liability)
                .where(
                    and_(
                        BillSplit.account_id == account.id,
                        Liability.due_date <= date.today() + timedelta(days=30),
                    )
                )
            )
            result = await self.db.execute(stmt)
            upcoming_bills = result.scalar() or Decimal("0")
            short_term_impact[account.id] = -(upcoming_bills + split.amount)

        # Calculate long-term impact (90 days)
        long_term_impact = {}
        for split in splits:
            account = accounts[split.account_id]
            # Project 90-day impact considering recurring bills
            stmt = (
                select(func.sum(BillSplit.amount))
                .join(BillSplit.liability)
                .where(
                    and_(
                        BillSplit.account_id == account.id,
                        Liability.due_date <= date.today() + timedelta(days=90),
                    )
                )
            )
            result = await self.db.execute(stmt)
            upcoming_bills = result.scalar() or Decimal("0")
            long_term_impact[account.id] = -(upcoming_bills + split.amount)

        # Identify risk factors
        risk_factors = []
        for account_id, utilization in metrics.credit_utilization.items():
            if utilization > 80:
                risk_factors.append(
                    f"High credit utilization ({utilization:.1f}%) on account {accounts[account_id].name}"
                )

        for account_id, impact in short_term_impact.items():
            account = accounts[account_id]
            if account.type != "credit" and abs(impact) > account.available_balance:
                risk_factors.append(
                    f"Insufficient 30-day funds in account {account.name}"
                )

        # Generate recommendations
        recommendations = []
        if risk_factors:
            if any(
                utilization > 80 for utilization in metrics.credit_utilization.values()
            ):
                recommendations.append(
                    "Consider redistributing credit usage across accounts"
                )

            if any(
                abs(impact) > accounts[acc_id].available_balance
                for acc_id, impact in short_term_impact.items()
                if accounts[acc_id].type != "credit"
            ):
                recommendations.append(
                    "Consider using credit accounts for short-term flexibility"
                )

        return ImpactAnalysis(
            split_configuration=splits,
            metrics=metrics,
            short_term_impact=short_term_impact,
            long_term_impact=long_term_impact,
            risk_factors=risk_factors,
            recommendations=recommendations,
        )

    async def generate_optimization_suggestions(
        self, liability_id: int
    ) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for bill splits."""
        # Get current splits if they exist
        current_splits = await self.get_bill_splits(liability_id)

        # Get the liability
        stmt = select(Liability).where(Liability.id == liability_id)
        result = await self.db.execute(stmt)
        liability = result.unique().scalar_one_or_none()
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {liability_id} not found"
            )

        # Get all active accounts
        stmt = select(Account)
        result = await self.db.execute(stmt)
        accounts = {acc.id: acc for acc in result.scalars().all()}

        suggestions = []

        # Convert current splits to BillSplitCreate objects
        original_splits = (
            [
                BillSplitCreate(
                    liability_id=split.liability_id,
                    account_id=split.account_id,
                    amount=split.amount,
                )
                for split in current_splits
            ]
            if current_splits
            else []
        )

        # If no current splits, use primary account as original
        if not original_splits:
            original_splits = [
                BillSplitCreate(
                    liability_id=liability_id,
                    account_id=liability.primary_account_id,
                    amount=liability.amount,
                )
            ]

        # Get current metrics
        current_metrics = await self.calculate_optimization_metrics(
            original_splits, accounts
        )

        # Strategy 1: Balance credit utilization
        if any(util > 50 for util in current_metrics.credit_utilization.values()):
            credit_accounts = {
                id: acc
                for id, acc in accounts.items()
                if acc.type == "credit" and acc.total_limit
            }

            if len(credit_accounts) > 1:
                # Distribute amount across credit accounts based on available credit
                total_available = sum(
                    acc.total_limit + acc.available_balance
                    for acc in credit_accounts.values()
                )

                suggested_splits = []
                remaining_amount = liability.amount

                for acc_id, account in credit_accounts.items():
                    if remaining_amount <= 0:
                        break

                    available_credit = account.total_limit + account.available_balance
                    split_amount = min(
                        (available_credit / total_available) * liability.amount,
                        remaining_amount,
                    )

                    suggested_splits.append(
                        BillSplitCreate(
                            liability_id=liability_id,
                            account_id=acc_id,
                            amount=split_amount,
                        )
                    )
                    remaining_amount -= split_amount

                if suggested_splits:
                    metrics = await self.calculate_optimization_metrics(
                        suggested_splits, accounts
                    )

                    if metrics.optimization_score > current_metrics.optimization_score:
                        suggestions.append(
                            OptimizationSuggestion(
                                original_splits=original_splits,
                                suggested_splits=suggested_splits,
                                improvement_metrics=metrics,
                                reasoning=[
                                    "Balances credit utilization across accounts",
                                    "Reduces risk of high utilization on single account",
                                ],
                                priority=(
                                    1
                                    if metrics.optimization_score
                                    > current_metrics.optimization_score + 0.2
                                    else 2
                                ),
                            )
                        )

        # Strategy 2: Mix credit and checking accounts for large amounts
        if liability.amount > Decimal("1000"):
            checking_accounts = {
                id: acc
                for id, acc in accounts.items()
                if acc.type in ["checking", "savings"]
            }

            if checking_accounts and any(
                acc.type == "credit" for acc in accounts.values()
            ):
                suggested_splits = []
                remaining_amount = liability.amount

                # Use checking accounts for 40% if possible
                checking_portion = liability.amount * Decimal("0.4")
                for acc_id, account in checking_accounts.items():
                    if remaining_amount <= 0:
                        break

                    split_amount = min(
                        checking_portion, account.available_balance, remaining_amount
                    )

                    if split_amount > 0:
                        suggested_splits.append(
                            BillSplitCreate(
                                liability_id=liability_id,
                                account_id=acc_id,
                                amount=split_amount,
                            )
                        )
                        remaining_amount -= split_amount

                # Use credit accounts for remaining amount
                if remaining_amount > 0:
                    credit_accounts = {
                        id: acc
                        for id, acc in accounts.items()
                        if acc.type == "credit" and acc.total_limit
                    }

                    for acc_id, account in credit_accounts.items():
                        if remaining_amount <= 0:
                            break

                        available_credit = (
                            account.total_limit + account.available_balance
                        )
                        split_amount = min(available_credit, remaining_amount)

                        if split_amount > 0:
                            suggested_splits.append(
                                BillSplitCreate(
                                    liability_id=liability_id,
                                    account_id=acc_id,
                                    amount=split_amount,
                                )
                            )
                            remaining_amount -= split_amount

                if suggested_splits and remaining_amount <= 0:
                    metrics = await self.calculate_optimization_metrics(
                        suggested_splits, accounts
                    )

                    if metrics.optimization_score > current_metrics.optimization_score:
                        suggestions.append(
                            OptimizationSuggestion(
                                original_splits=original_splits,
                                suggested_splits=suggested_splits,
                                improvement_metrics=metrics,
                                reasoning=[
                                    "Balances usage between checking and credit accounts",
                                    "Preserves credit availability for emergencies",
                                    "Utilizes available checking balance effectively",
                                ],
                                priority=(
                                    2
                                    if metrics.optimization_score
                                    > current_metrics.optimization_score + 0.15
                                    else 3
                                ),
                            )
                        )

        return suggestions

    async def validate_bulk_operation(
        self, operation: BulkSplitOperation
    ) -> BulkOperationResult:
        """
        Validate a bulk operation without executing it.
        This is a dry-run that checks all validations but doesn't commit changes.
        """
        operation.validate_only = True
        return await self.process_bulk_operation(operation)
