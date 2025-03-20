from datetime import datetime
from decimal import Decimal

import pytest

from src.models.transaction_history import TransactionHistory
from src.services.accounts import AccountService


@pytest.mark.asyncio
async def test_calculate_available_credit(db_session, base_credit_account):
    """Test available credit calculation for a credit account"""
    service = AccountService(db_session)

    # Add some test transactions
    debit_transaction = TransactionHistory(
        account_id=base_credit_account.id,
        amount=Decimal("100.00"),
        transaction_type="debit",
        description="Test debit",
        transaction_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    credit_transaction = TransactionHistory(
        account_id=base_credit_account.id,
        amount=Decimal("50.00"),
        transaction_type="credit",
        description="Test credit",
        transaction_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    db_session.add(debit_transaction)
    db_session.add(credit_transaction)
    await db_session.flush()

    # Calculate available credit
    result = await service.calculate_available_credit(base_credit_account.id)

    # Verify results
    assert result is not None
    assert result.account_id == base_credit_account.id
    assert result.account_name == base_credit_account.name
    assert result.total_limit == Decimal("2000.00")
    assert result.current_balance == Decimal("-500.00")
    assert result.pending_transactions == Decimal("50.00")  # 100 debit - 50 credit
    assert result.adjusted_balance == Decimal("-450.00")  # -500 + 50
    assert result.available_credit == Decimal("1550.00")  # 2000 - |-450|


@pytest.mark.asyncio
async def test_calculate_available_credit_no_transactions(
    db_session, base_credit_account
):
    """Test available credit calculation with no transactions"""
    service = AccountService(db_session)

    result = await service.calculate_available_credit(base_credit_account.id)

    assert result is not None
    assert result.account_id == base_credit_account.id
    assert result.total_limit == Decimal("2000.00")
    assert result.current_balance == Decimal("-500.00")
    assert result.pending_transactions == Decimal("0")
    assert result.adjusted_balance == Decimal("-500.00")
    assert result.available_credit == Decimal("1500.00")  # 2000 - |-500|


@pytest.mark.asyncio
async def test_calculate_available_credit_non_credit_account(db_session, base_account):
    """Test available credit calculation fails for non-credit account"""
    service = AccountService(db_session)

    with pytest.raises(
        ValueError,
        match="Available credit calculation only available for credit accounts",
    ):
        await service.calculate_available_credit(base_account.id)


@pytest.mark.asyncio
async def test_calculate_available_credit_account_not_found(db_session):
    """Test available credit calculation returns None for non-existent account"""
    service = AccountService(db_session)

    result = await service.calculate_available_credit(999)
    assert result is None
