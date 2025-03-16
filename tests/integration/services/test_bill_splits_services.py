import pytest
from decimal import Decimal
from datetime import date

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit
from src.services.bill_splits import BillSplitService, BillSplitValidationError
from src.schemas.bill_splits import BillSplitCreate, BillSplitValidation

@pytest.fixture(scope="function")
async def checking_account(db_session):
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.flush()
    return account

@pytest.fixture(scope="function")
async def credit_account(db_session):
    account = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.flush()
    return account

@pytest.fixture(scope="function")
async def liability(db_session):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("300.00"),
        due_date=date.today(),
        category_id=1,  # Assuming category 1 exists
        primary_account_id=1,  # Will be updated in tests
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(liability)
    await db_session.flush()
    return liability

async def test_create_bill_split_success(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    split = BillSplitCreate(
        liability_id=liability.id,
        account_id=checking_account.id,
        amount=Decimal("100.00")
    )
    
    result = await service.create_bill_split(split)
    assert result.amount == Decimal("100.00")
    assert result.liability_id == liability.id
    assert result.account_id == checking_account.id

async def test_create_bill_split_insufficient_balance(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    split = BillSplitCreate(
        liability_id=liability.id,
        account_id=checking_account.id,
        amount=Decimal("2000.00")  # More than available balance
    )
    
    with pytest.raises(BillSplitValidationError) as exc:
        await service.create_bill_split(split)
    assert "insufficient balance" in str(exc.value)

async def test_create_bill_split_insufficient_credit(db_session, credit_account, liability):
    service = BillSplitService(db_session)
    # Available credit is 1500 (2000 limit - 500 used)
    split = BillSplitCreate(
        liability_id=liability.id,
        account_id=credit_account.id,
        amount=Decimal("1600.00")  # More than available credit
    )
    
    with pytest.raises(BillSplitValidationError) as exc:
        await service.create_bill_split(split)
    assert "insufficient credit" in str(exc.value)

async def test_validate_splits_success(db_session, checking_account, credit_account, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("200.00")
            ),
            BillSplitCreate(
                liability_id=liability.id,
                account_id=credit_account.id,
                amount=Decimal("100.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is True
    assert error is None

async def test_validate_splits_total_mismatch(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=Decimal("400.00"),  # Different from liability amount
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("400.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "does not match liability amount" in error

async def test_validate_splits_duplicate_accounts(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("150.00")
            ),
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,  # Same account
                amount=Decimal("150.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "Duplicate accounts" in error

async def test_validate_splits_nonexistent_account(db_session, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=99999,  # Non-existent account
                amount=Decimal("300.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "Accounts not found" in error

async def test_suggest_splits_historical_pattern(db_session, checking_account, credit_account, liability):
    """Test split suggestions based on historical patterns"""
    service = BillSplitService(db_session)

    # Create two similar liabilities to meet min_frequency requirement
    for i in range(2):
        similar_liability = Liability(
            name=liability.name,  # Same name to trigger pattern matching
            amount=Decimal("300.00"),
            due_date=date.today(),
            category_id=liability.category_id,
            primary_account_id=checking_account.id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=date.today(),
            updated_at=date.today()
        )
        db_session.add(similar_liability)
        await db_session.flush()

        # Add historical splits
        historical_split1 = BillSplit(
            liability_id=similar_liability.id,
            account_id=checking_account.id,
            amount=Decimal("200.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
        historical_split2 = BillSplit(
            liability_id=similar_liability.id,
            account_id=credit_account.id,
            amount=Decimal("100.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
        db_session.add(historical_split1)
        db_session.add(historical_split2)
        await db_session.flush()

    # Get suggestions
    suggestions = await service.suggest_splits(liability.id)
    
    assert suggestions.liability_id == liability.id
    assert suggestions.total_amount == liability.amount
    assert suggestions.historical_pattern is True
    assert len(suggestions.suggestions) == 2
    
    # Verify suggestions match historical pattern proportions
    checking_suggestion = next(s for s in suggestions.suggestions if s.account_id == checking_account.id)
    credit_suggestion = next(s for s in suggestions.suggestions if s.account_id == credit_account.id)
    
    assert checking_suggestion.amount == Decimal("200.00")
    assert credit_suggestion.amount == Decimal("100.00")
    assert checking_suggestion.confidence_score == 0.8
    assert credit_suggestion.confidence_score == 0.8

async def test_suggest_splits_available_funds(db_session, checking_account, credit_account, liability):
    """Test split suggestions based on available funds when no historical pattern exists"""
    service = BillSplitService(db_session)
    
    # Update liability to use checking account as primary
    liability.primary_account_id = checking_account.id
    await db_session.flush()
    
    # Get suggestions
    suggestions = await service.suggest_splits(liability.id)
    
    assert suggestions.liability_id == liability.id
    assert suggestions.total_amount == liability.amount
    assert suggestions.historical_pattern is False
    assert len(suggestions.suggestions) == 1  # Should only suggest primary account since it has sufficient funds
    
    primary_suggestion = suggestions.suggestions[0]
    assert primary_suggestion.account_id == checking_account.id
    assert primary_suggestion.amount == liability.amount
    assert primary_suggestion.confidence_score == 0.6
    assert "sufficient funds" in primary_suggestion.reason

async def test_suggest_splits_multiple_accounts(db_session, checking_account, credit_account, liability):
    """Test split suggestions across multiple accounts when primary account has insufficient funds"""
    service = BillSplitService(db_session)
    
    # Update liability amount to require multiple accounts
    liability.amount = Decimal("1200.00")  # More than any single account's available funds
    liability.primary_account_id = checking_account.id
    await db_session.flush()
    
    # Get suggestions
    suggestions = await service.suggest_splits(liability.id)
    
    assert suggestions.liability_id == liability.id
    assert suggestions.total_amount == liability.amount
    assert suggestions.historical_pattern is False
    assert len(suggestions.suggestions) == 2  # Should suggest both accounts
    
    total_suggested = sum(s.amount for s in suggestions.suggestions)
    assert total_suggested == liability.amount
    
    # Verify suggestions use available funds appropriately
    for suggestion in suggestions.suggestions:
        if suggestion.account_id == checking_account.id:
            assert suggestion.amount <= checking_account.available_balance
        elif suggestion.account_id == credit_account.id:
            available_credit = credit_account.total_limit + credit_account.available_balance
            assert suggestion.amount <= available_credit

async def test_analyze_historical_patterns(db_session, checking_account, credit_account, liability):
    """Test comprehensive historical pattern analysis"""
    service = BillSplitService(db_session)

    # Create historical data with consistent patterns
    for i in range(3):  # Create 3 similar liabilities
        similar_liability = Liability(
            name=liability.name,
            amount=Decimal("300.00"),
            due_date=date.today(),
            category_id=liability.category_id,
            primary_account_id=checking_account.id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=date.today(),
            updated_at=date.today()
        )
        db_session.add(similar_liability)
        await db_session.flush()

        # Add consistent split pattern
        splits = [
            BillSplit(
                liability_id=similar_liability.id,
                account_id=checking_account.id,
                amount=Decimal("200.00"),
                created_at=date.today(),
                updated_at=date.today()
            ),
            BillSplit(
                liability_id=similar_liability.id,
                account_id=credit_account.id,
                amount=Decimal("100.00"),
                created_at=date.today(),
                updated_at=date.today()
            )
        ]
        for split in splits:
            db_session.add(split)
        await db_session.flush()

    # Get analysis
    analysis = await service.analyze_historical_patterns(liability.id)
    
    # Verify basic analysis properties
    assert analysis.liability_id == liability.id
    assert analysis.analysis_date == date.today()
    
    # Verify patterns were identified
    assert len(analysis.patterns) > 0
    most_common = analysis.patterns[0]  # Should be sorted by confidence
    assert most_common.total_occurrences == 3
    assert abs(most_common.account_splits[checking_account.id] - Decimal("0.67")) < Decimal("0.01")  # ~67% split
    assert abs(most_common.account_splits[credit_account.id] - Decimal("0.33")) < Decimal("0.01")  # ~33% split
    
    # Verify metrics
    assert analysis.metrics.total_splits == 6  # 2 splits * 3 liabilities
    assert analysis.metrics.unique_patterns == 1
    assert analysis.metrics.average_splits_per_bill == 2.0
    assert analysis.metrics.most_common_pattern is not None
    assert checking_account.id in analysis.metrics.account_usage_frequency
    assert credit_account.id in analysis.metrics.account_usage_frequency
    
    # Verify category patterns
    assert liability.category_id in analysis.category_patterns
    assert len(analysis.category_patterns[liability.category_id]) > 0
    
    # Verify seasonal patterns
    current_month = date.today().strftime("%B")
    assert current_month in analysis.seasonal_patterns
    assert len(analysis.seasonal_patterns[current_month]) > 0

async def test_pattern_confidence_scoring(db_session, checking_account, credit_account, liability):
    """Test confidence score calculation for patterns"""
    service = BillSplitService(db_session)
    
    # Create test data with varying dates to test recency impact
    dates = [
        date.today(),  # Recent
        date(2024, 1, 1),  # A bit older
        date(2023, 6, 1),  # Much older
    ]
    
    for test_date in dates:
        similar_liability = Liability(
            name=liability.name,
            amount=Decimal("300.00"),
            due_date=test_date,
            category_id=liability.category_id,
            primary_account_id=checking_account.id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=test_date,
            updated_at=test_date
        )
        db_session.add(similar_liability)
        await db_session.flush()

        splits = [
            BillSplit(
                liability_id=similar_liability.id,
                account_id=checking_account.id,
                amount=Decimal("200.00"),
                created_at=test_date,
                updated_at=test_date
            ),
            BillSplit(
                liability_id=similar_liability.id,
                account_id=credit_account.id,
                amount=Decimal("100.00"),
                created_at=test_date,
                updated_at=test_date
            )
        ]
        for split in splits:
            db_session.add(split)
        await db_session.flush()

    # Get analysis
    analysis = await service.analyze_historical_patterns(liability.id)
    
    # Verify confidence scoring
    assert len(analysis.patterns) > 0
    pattern = analysis.patterns[0]
    
    # Pattern should have high frequency score (3 occurrences)
    # but lower recency score due to older entries
    assert 0.3 < pattern.confidence_score < 0.9  # Reasonable range for mixed recency

async def test_validate_splits_insufficient_funds(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    
    # Update liability amount to test insufficient funds
    liability.amount = Decimal("2000.00")
    await db_session.flush()
    
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,  # Now matches the split amount
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("2000.00")  # More than available balance (1000.00)
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "insufficient balance" in error
