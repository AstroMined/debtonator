from decimal import Decimal
from datetime import date
from typing import List, Optional, Tuple, Dict
from sqlalchemy import select, delete, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit
from src.models.accounts import Account
from src.schemas.bill_splits import (
    BillSplitCreate,
    BillSplitUpdate,
    BillSplitValidation,
    SplitSuggestion,
    BillSplitSuggestionResponse
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
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .where(BillSplit.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_account_splits(self, account_id: int) -> List[BillSplit]:
        """Get all splits for a specific account."""
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .where(BillSplit.account_id == account_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def create_split(self, liability_id: int, account_id: int, amount: Decimal) -> BillSplit:
        """Create a new bill split (internal use)."""
        split = BillSplit(
            liability_id=liability_id,
            account_id=account_id,
            amount=amount,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(split)
        await self.db.flush()

        # Fetch fresh copy with relationships
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
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
            raise BillSplitValidationError(f"Liability with id {split.liability_id} not found")

        # Verify account exists and has sufficient balance/credit
        stmt = select(Account).where(Account.id == split.account_id)
        result = await self.db.execute(stmt)
        account = result.unique().scalar_one_or_none()
        if not account:
            raise BillSplitValidationError(f"Account with id {split.account_id} not found")

        # Validate account has sufficient balance/credit
        if account.type == "credit":
            available_credit = (
                account.total_limit + account.available_balance
                if account.total_limit
                else Decimal('0')
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
            amount=split.amount
        )

    async def update_bill_split(self, split_id: int, split: BillSplitUpdate) -> Optional[BillSplit]:
        """Update an existing bill split."""
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
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
                    else Decimal('0')
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

    async def validate_splits(self, validation: BillSplitValidation) -> Tuple[bool, Optional[str]]:
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
            if abs(validation.total_amount - liability.amount) > Decimal('0.01'):
                return False, (
                    f"Total amount {validation.total_amount} does not match "
                    f"liability amount {liability.amount}"
                )

            # Get all accounts involved in splits
            account_ids = [split.account_id for split in validation.splits]
            stmt = (
                select(Account)
                .where(Account.id.in_(account_ids))
            )
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
                        else Decimal('0')
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

    async def get_historical_split_patterns(
        self,
        liability_id: int,
        min_frequency: int = 2
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
        similar_liabilities = (
            select(Liability.id)
            .where(
                and_(
                    Liability.id != liability_id,
                    or_(
                        Liability.name == liability.name,
                        Liability.category_id == liability.category_id
                    )
                )
            )
        )
        result = await self.db.execute(similar_liabilities)
        similar_ids = [r[0] for r in result.all()]
        if not similar_ids:
            return []

        # Get splits for similar liabilities
        splits_stmt = (
            select(BillSplit)
            .where(BillSplit.liability_id.in_(similar_ids))
        )
        result = await self.db.execute(splits_stmt)
        splits = result.scalars().all()

        # Analyze patterns
        patterns: Dict[str, Dict] = {}
        for split in splits:
            pattern_key = f"{split.liability_id}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    "accounts": {},
                    "total": Decimal('0')
                }
            patterns[pattern_key]["accounts"][split.account_id] = split.amount
            patterns[pattern_key]["total"] += split.amount

        # Convert amounts to percentages and find common patterns
        normalized_patterns: Dict[str, int] = {}
        for pattern in patterns.values():
            if abs(pattern["total"]) < Decimal('0.01'):
                continue
            
            # Create normalized pattern string (account:percentage) with exact decimal places
            total = pattern["total"]
            pattern_str = "|".join(
                f"{acc}:{amt}:{total}"  # Store original amounts and total instead of percentages
                for acc, amt in sorted(pattern["accounts"].items())
            )
            normalized_patterns[pattern_str] = normalized_patterns.get(pattern_str, 0) + 1

        # Filter by minimum frequency and convert back to account:amount mappings
        frequent_patterns = []
        for pattern_str, freq in normalized_patterns.items():
            if freq >= min_frequency:
                pattern = {}
                for acc_split in pattern_str.split("|"):
                    acc_id, amount, total = acc_split.split(":")
                    # Calculate new amount while preserving original proportions
                    pattern[int(acc_id)] = (Decimal(amount) / Decimal(total) * liability.amount).quantize(Decimal('0.01'))
                frequent_patterns.append(pattern)

        return frequent_patterns

    async def suggest_splits(
        self,
        liability_id: int
    ) -> BillSplitSuggestionResponse:
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
            raise BillSplitValidationError(f"Liability with id {liability_id} not found")

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

                suggestions.append(SplitSuggestion(
                    account_id=account_id,
                    amount=amount,
                    confidence_score=0.8,
                    reason=f"Based on historical split pattern for {liability.name}"
                ))

            return BillSplitSuggestionResponse(
                liability_id=liability_id,
                total_amount=liability.amount,
                suggestions=suggestions,
                historical_pattern=True,
                pattern_frequency=len(patterns)
            )

        # If no historical pattern, suggest based on available funds
        suggestions = []
        remaining_amount = liability.amount

        # First try primary account
        primary_account = next(
            (a for a in accounts if a.id == liability.primary_account_id),
            None
        )
        if primary_account:
            available = (
                primary_account.total_limit + primary_account.available_balance
                if primary_account.type == "credit" and primary_account.total_limit
                else primary_account.available_balance
            )
            if available >= remaining_amount:
                suggestions.append(SplitSuggestion(
                    account_id=primary_account.id,
                    amount=remaining_amount,
                    confidence_score=0.6,
                    reason="Primary account has sufficient funds"
                ))
                remaining_amount = Decimal('0')

        # If primary account can't cover it, suggest splits across available accounts
        if remaining_amount > 0:
            # Sort accounts by available funds (descending)
            # Get all accounts except primary
            other_accounts = [a for a in accounts if a.id != liability.primary_account_id]
            
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
                    suggestions.append(SplitSuggestion(
                        account_id=primary_account.id,
                        amount=split_amount,
                        confidence_score=0.4,
                        reason=f"Primary account has {available:.2f} available"
                    ))
                    remaining_amount -= split_amount
            
            # Sort other accounts by available funds
            sorted_accounts = sorted(
                other_accounts,
                key=get_available_funds,
                reverse=True
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
                    suggestions.append(SplitSuggestion(
                        account_id=account.id,
                        amount=split_amount,
                        confidence_score=0.4,
                        reason=f"Account has {available:.2f} available"
                    ))
                    remaining_amount -= split_amount

        return BillSplitSuggestionResponse(
            liability_id=liability_id,
            total_amount=liability.amount,
            suggestions=suggestions,
            historical_pattern=False
        )

    async def calculate_split_totals(self, liability_id: int) -> Decimal:
        """Calculate the total amount of all splits for a given liability."""
        stmt = (
            select(BillSplit)
            .options(
                joinedload(BillSplit.liability),
                joinedload(BillSplit.account)
            )
            .where(BillSplit.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        splits = result.unique().scalars().all()
        return sum(split.amount for split in splits)
