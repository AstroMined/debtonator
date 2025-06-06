"""
Bill splits service implementation.

This module provides a service for managing bill splits, including creating, updating, and
analyzing bill splits across accounts. It properly implements the repository pattern
according to ADR-014 Repository Layer Compliance.

Uses ADR-011 compliant datetime handling with utilities from datetime_utils.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.repositories.accounts import AccountRepository
from src.repositories.bill_splits import BillSplitRepository
from src.repositories.liabilities import LiabilityRepository
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
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import end_of_day, ensure_utc, start_of_day
from src.utils.decimal_precision import DecimalPrecision


class BillSplitValidationError(Exception):
    """Custom exception for bill split validation errors"""


class BillSplitService(BaseService):
    """
    Service for handling bill split operations.

    This service manages bill split operations including creating, retrieving,
    updating, and analyzing bill splits across accounts. It provides insights
    into split patterns and suggestions for bill distribution.

    Follows ADR-014 Repository Layer Compliance by using the BaseService pattern.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize bill split service with session and optional feature flag service.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def get_bill_splits(self, liability_id: int) -> List[BillSplit]:
        """
        Get all splits for a specific liability.

        Args:
            liability_id: ID of the liability to get splits for

        Returns:
            List[BillSplit]: List of bill splits for the liability
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Use repository method
        return await bill_split_repo.get_splits_for_bill(liability_id)

    async def get_account_splits(self, account_id: int) -> List[BillSplit]:
        """
        Get all splits for a specific account.

        Args:
            account_id: ID of the account to get splits for

        Returns:
            List[BillSplit]: List of bill splits for the account
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Use repository method
        return await bill_split_repo.get_splits_for_account(account_id)

    async def create_split(
        self, liability_id: int, account_id: int, amount: Decimal
    ) -> BillSplit:
        """
        Create a new bill split (internal use).

        Args:
            liability_id: ID of the liability for the split
            account_id: ID of the account for the split
            amount: Amount for the split

        Returns:
            BillSplit: Created bill split with relationships
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Prepare split data
        split_data = {
            "liability_id": liability_id,
            "account_id": account_id,
            "amount": amount,
            "created_at": date.today(),
            "updated_at": date.today(),
        }

        # Create the split and return it with relationships
        return await bill_split_repo.create(split_data)

    async def create_bill_split(self, split: BillSplitCreate) -> BillSplit:
        """
        Create a new bill split (API use).

        Args:
            split: Bill split data for creation

        Returns:
            BillSplit: Created bill split

        Raises:
            BillSplitValidationError: If validation fails
        """
        # Get repositories using BaseService pattern
        liability_repo = await self._get_repository(LiabilityRepository)
        account_repo = await self._get_repository(AccountRepository)

        # Verify liability exists
        liability = await liability_repo.get_with_relationships(split.liability_id)
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {split.liability_id} not found"
            )

        # Verify account exists
        account = await account_repo.get(split.account_id)
        if not account:
            raise BillSplitValidationError(
                f"Account with id {split.account_id} not found"
            )

        # Validate account has sufficient balance/credit
        if account.account_type == "credit":
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
        """
        Update an existing bill split.

        Args:
            split_id: ID of the bill split to update
            split: Bill split data for update

        Returns:
            Optional[BillSplit]: Updated bill split or None if not found

        Raises:
            BillSplitValidationError: If validation fails
        """
        # Get repositories using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)
        account_repo = await self._get_repository(AccountRepository)

        # Get the bill split with relationships
        db_split = await bill_split_repo.get_with_relationships(split_id)
        if not db_split:
            return None

        # If amount is being updated, validate against account balance/credit
        if split.amount is not None:
            # Get the account
            account = await account_repo.get(db_split.account_id)

            if account.account_type == "credit":
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

            # Prepare update data
            update_data = split.model_dump(exclude_unset=True)
            update_data["updated_at"] = date.today()

            # Update the bill split
            return await bill_split_repo.update(split_id, update_data)

        return db_split

    async def delete_bill_split(self, split_id: int) -> bool:
        """
        Delete a specific bill split.

        Args:
            split_id: ID of the bill split to delete

        Returns:
            bool: True if successful, False if split not found
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Delete the bill split
        return await bill_split_repo.delete(split_id)

    async def delete_bill_splits(self, liability_id: int) -> int:
        """
        Delete all splits for a liability.

        Args:
            liability_id: ID of the liability to delete splits for

        Returns:
            int: Number of splits deleted
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Delete all splits for the liability
        return await bill_split_repo.delete_splits_for_liability(liability_id)

    async def validate_splits(
        self, validation: BillSplitValidation
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate bill splits against multiple criteria:
        1. Sum of splits equals liability amount
        2. All accounts exist and have sufficient balance/credit
        3. No duplicate accounts
        4. All amounts are positive

        Args:
            validation: Validation data containing liability_id, total_amount and splits

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Get repositories using BaseService pattern
            liability_repo = await self._get_repository(LiabilityRepository)
            account_repo = await self._get_repository(AccountRepository)

            # Verify liability exists
            liability = await liability_repo.get(validation.liability_id)
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

            # Get accounts by IDs
            accounts_list = await account_repo.get_accounts_by_ids(account_ids)
            accounts = {acc.id: acc for acc in accounts_list}

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
                if account.account_type == "credit":
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
        self, occurrences: int, total_patterns: int, _first_seen: date, last_seen: date
    ) -> float:
        """
        Calculate a confidence score based on frequency and recency.

        Args:
            occurrences: Number of times this pattern has occurred
            total_patterns: Total number of patterns for normalization
            _first_seen: Date when this pattern was first seen (unused but kept for API compatibility)
            last_seen: Date when this pattern was last seen

        Returns:
            float: Confidence score between 0.1 and 0.9
        """
        today = date.today()
        # Days since last seen is more important for recency
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
        """
        Perform comprehensive historical analysis of bill splits.

        Args:
            liability_id: ID of the liability to analyze

        Returns:
            HistoricalAnalysis: Comprehensive analysis of historical bill split patterns

        Raises:
            BillSplitValidationError: If liability not found
        """
        # Get repositories using BaseService pattern
        liability_repo = await self._get_repository(LiabilityRepository)
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Get the liability with its category
        liability = await liability_repo.get_with_relationships(liability_id)
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {liability_id} not found"
            )

        # Get all liabilities with same name or category
        similar_liabilities = await liability_repo.find_similar_liabilities(
            liability.name, liability.category_id
        )
        similar_liability_ids = [liability.id for liability in similar_liabilities]

        # Get all splits for similar liabilities
        all_splits = await bill_split_repo.get_splits_for_multiple_liabilities(
            similar_liability_ids
        )

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

        Args:
            liability_id: ID of the liability to analyze patterns for
            min_frequency: Minimum frequency threshold for patterns to be included

        Returns:
            List[Dict[int, Decimal]]: List of account-to-amount mappings that occur frequently
        """
        # Get repositories using BaseService pattern
        liability_repo = await self._get_repository(LiabilityRepository)
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Get the liability
        liability = await liability_repo.get(liability_id)
        if not liability:
            return []

        # Find similar liabilities (same name or category)
        similar_liabilities = await liability_repo.find_similar_liabilities(
            liability.name, liability.category_id, exclude_id=liability_id
        )

        similar_ids = [l.id for l in similar_liabilities]
        if not similar_ids:
            return []

        # Get splits for similar liabilities
        splits = await bill_split_repo.get_splits_for_multiple_liabilities(similar_ids)

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
        # Get repositories using BaseService pattern
        liability_repo = await self._get_repository(LiabilityRepository)
        account_repo = await self._get_repository(AccountRepository)

        # Get the liability
        liability = await liability_repo.get(liability_id)
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {liability_id} not found"
            )

        # Get all active accounts
        accounts = await account_repo.get_all()

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
                if account.account_type == "credit" and account.total_limit:
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
                    if account.account_type == "credit" and account.total_limit
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
        """
        Calculate the total amount of all splits for a given liability.

        Args:
            liability_id: ID of the liability to calculate splits for

        Returns:
            Decimal: Total amount of all splits
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Use repository method to calculate the total
        return await bill_split_repo.calculate_split_totals(liability_id)

    async def process_bulk_operation(
        self, operation: BulkSplitOperation
    ) -> BulkOperationResult:
        """
        Process a bulk bill split operation with transaction support.
        Validates and processes multiple splits in a single transaction.

        Args:
            operation: Bulk operation data with splits and operation type

        Returns:
            BulkOperationResult: Result of the bulk operation with success status and details
        """
        # Get repository using BaseService pattern
        bill_split_repo = await self._get_repository(BillSplitRepository)

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
            # Start transaction using the session from _session attribute
            async with self._session.begin_nested() as nested:
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
        """
        Calculate optimization metrics for a set of splits.

        Args:
            splits: List of bill splits to analyze
            accounts: Dictionary of account IDs to Account objects

        Returns:
            OptimizationMetrics: Metrics about optimization, credit utilization, and risk
        """
        credit_utilization = {}
        balance_impact = {}
        total_risk_score = 0
        total_accounts = len(splits)

        for split in splits:
            account = accounts[split.account_id]

            # Calculate credit utilization for credit accounts
            if account.account_type == "credit" and account.total_limit:
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
            if account.account_type == "credit":
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
        """
        Analyze the impact of a split configuration.

        Args:
            splits: List of bill splits to analyze

        Returns:
            ImpactAnalysis: Analysis of impact on accounts, risk factors, and recommendations
        """
        # Get repositories using BaseService pattern
        account_repo = await self._get_repository(AccountRepository)
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Get all accounts involved
        account_ids = [split.account_id for split in splits]
        accounts_list = await account_repo.get_accounts_by_ids(account_ids)
        accounts = {acc.id: acc for acc in accounts_list}

        # Calculate current metrics
        metrics = await self.calculate_optimization_metrics(splits, accounts)

        # Calculate short-term impact (30 days)
        short_term_impact = {}
        for split in splits:
            account = accounts[split.account_id]

            # Get upcoming bills for next 30 days
            today = date.today()
            in_30_days = today + timedelta(days=30)

            # Convert to datetime with proper timezone handling using ADR-011 utility functions
            start_date = start_of_day(
                ensure_utc(datetime.combine(today, datetime.min.time()))
            )
            end_date = end_of_day(
                ensure_utc(datetime.combine(in_30_days, datetime.min.time()))
            )

            # Get splits in date range
            upcoming_bills_splits = await bill_split_repo.get_splits_in_date_range(
                account.id, start_date, end_date
            )

            # Calculate total
            upcoming_bills = sum(split.amount for split in upcoming_bills_splits)
            short_term_impact[account.id] = -(upcoming_bills + split.amount)

        # Calculate long-term impact (90 days)
        long_term_impact = {}
        for split in splits:
            account = accounts[split.account_id]

            # Get upcoming bills for next 90 days
            today = date.today()
            in_90_days = today + timedelta(days=90)

            # Convert to datetime with proper timezone handling using ADR-011 utility functions
            start_date = start_of_day(
                ensure_utc(datetime.combine(today, datetime.min.time()))
            )
            end_date = end_of_day(
                ensure_utc(datetime.combine(in_90_days, datetime.min.time()))
            )

            # Get splits in date range
            upcoming_bills_splits = await bill_split_repo.get_splits_in_date_range(
                account.id, start_date, end_date
            )

            # Calculate total
            upcoming_bills = sum(split.amount for split in upcoming_bills_splits)
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
            if (
                account.account_type != "credit"
                and abs(impact) > account.available_balance
            ):
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
                if accounts[acc_id].account_type != "credit"
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
        """
        Generate optimization suggestions for bill splits.

        Args:
            liability_id: ID of the liability to generate optimization suggestions for

        Returns:
            List[OptimizationSuggestion]: List of optimization suggestions with metrics

        Raises:
            BillSplitValidationError: If liability not found
        """
        # Get repositories using BaseService pattern
        liability_repo = await self._get_repository(LiabilityRepository)
        account_repo = await self._get_repository(AccountRepository)
        bill_split_repo = await self._get_repository(BillSplitRepository)

        # Get current splits if they exist
        current_splits = await bill_split_repo.get_splits_for_bill(liability_id)

        # Get the liability
        liability = await liability_repo.get(liability_id)
        if not liability:
            raise BillSplitValidationError(
                f"Liability with id {liability_id} not found"
            )

        # Get all active accounts
        all_accounts = await account_repo.get_all()
        accounts = {acc.id: acc for acc in all_accounts}

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
                if acc.account_type == "credit" and acc.total_limit
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
                if acc.account_type in ["checking", "savings"]
            }

            if checking_accounts and any(
                acc.account_type == "credit" for acc in accounts.values()
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
                        if acc.account_type == "credit" and acc.total_limit
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

        Args:
            operation: Bulk operation data to validate

        Returns:
            BulkOperationResult: Result of the validation with success status and details
        """
        # Set validate_only flag to ensure no changes are committed
        operation.validate_only = True

        # Process the operation in validation mode
        return await self.process_bulk_operation(operation)
