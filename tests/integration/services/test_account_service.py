import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from src.models.accounts import Account as AccountModel
from src.services.accounts import AccountService
from src.schemas.accounts import AccountCreate, AccountUpdate
from src.schemas.credit_limits import CreditLimitUpdate

@pytest.mark.asyncio
class TestAccountService:
    async def test_create_account_checking(self, db_session):
        service = AccountService(db_session)
        account_data = AccountCreate(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000.00")
        )
        
        account = await service.create_account(account_data)
        assert account.name == "Test Checking"
        assert account.type == "checking"
        assert account.available_balance == Decimal("1000.00")
        assert account.total_limit is None
        assert account.available_credit is None

    async def test_create_account_credit(self, db_session):
        service = AccountService(db_session)
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00"),
            total_limit=Decimal("5000.00")
        )
        
        account = await service.create_account(account_data)
        assert account.name == "Test Credit"
        assert account.type == "credit"
        assert account.available_balance == Decimal("0.00")
        assert account.total_limit == Decimal("5000.00")
        assert account.available_credit == Decimal("5000.00")

    async def test_create_credit_account_without_limit_fails(self, db_session):
        service = AccountService(db_session)
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00")
        )
        
        with pytest.raises(ValueError, match="Credit accounts must have a total limit"):
            await service.create_account(account_data)

    async def test_update_account_type_with_balance_fails(self, db_session):
        service = AccountService(db_session)
        
        # Create credit account with balance
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-500.00"),
            total_limit=Decimal("5000.00")
        )
        account = await service.create_account(account_data)
        
        # Try to change type to checking
        update_data = AccountUpdate(type="checking")
        with pytest.raises(ValueError, match="Cannot change type of credit account with non-zero balance"):
            await service.update_account(account.id, update_data)

    async def test_update_credit_limit(self, db_session):
        service = AccountService(db_session)
        
        # Create credit account
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00"),
            total_limit=Decimal("5000.00")
        )
        account = await service.create_account(account_data)
        
        # Update credit limit
        update_data = CreditLimitUpdate(
            credit_limit=Decimal("10000.00"),
            effective_date=date.today(),
            reason="Credit increase"
        )
        updated = await service.update_credit_limit(account.id, update_data)
        
        assert updated.total_limit == Decimal("10000.00")
        assert updated.available_credit == Decimal("10000.00")

    async def test_update_credit_limit_with_balance_fails(self, db_session):
        service = AccountService(db_session)
        
        # Create credit account with balance
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-1500.00"),
            total_limit=Decimal("5000.00")
        )
        account = await service.create_account(account_data)
        
        # Try to update credit limit below current balance
        update_data = CreditLimitUpdate(
            credit_limit=Decimal("1000.00"),
            effective_date=date.today(),
            reason="Credit decrease"
        )
        with pytest.raises(ValueError, match="New credit limit 1000.00 is less than current balance 1500.00"):
            await service.update_credit_limit(account.id, update_data)

    async def test_update_statement_balance(self, db_session):
        service = AccountService(db_session)
        
        # Create credit account
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00"),
            total_limit=Decimal("5000.00")
        )
        account = await service.create_account(account_data)
        
        # Update statement balance
        statement_date = date.today()
        statement_datetime = datetime.combine(statement_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        updated = await service.update_statement_balance(
            account.id,
            statement_balance=Decimal("1000.00"),
            statement_date=statement_date,
            minimum_payment=Decimal("25.00"),
            due_date=statement_date + timedelta(days=25)
        )
        
        assert updated.last_statement_balance == Decimal("1000.00")
        assert updated.last_statement_date.date() == statement_date

    async def test_update_statement_balance_exceeds_limit_fails(self, db_session):
        service = AccountService(db_session)
        
        # Create credit account
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00"),
            total_limit=Decimal("5000.00")
        )
        account = await service.create_account(account_data)
        
        # Try to update statement balance above limit
        with pytest.raises(ValueError, match="Statement balance 6000.00 exceeds credit limit 5000.00"):
            await service.update_statement_balance(
                account.id,
                statement_balance=Decimal("6000.00"),
                statement_date=date.today()
            )

    async def test_delete_account_with_balance_fails(self, db_session):
        service = AccountService(db_session)
        
        # Create checking account with balance
        account_data = AccountCreate(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000.00")
        )
        account = await service.create_account(account_data)
        
        # Try to delete account with balance
        with pytest.raises(ValueError, match="Cannot delete account with non-zero balance: 1000.00"):
            await service.delete_account(account.id)

    async def test_delete_account_success(self, db_session):
        service = AccountService(db_session)
        
        # Create checking account with zero balance
        account_data = AccountCreate(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("0.00")
        )
        account = await service.create_account(account_data)
        
        # Delete account
        result = await service.delete_account(account.id)
        assert result is True
        
        # Verify account is deleted
        deleted = await service.get_account(account.id)
        assert deleted is None

    async def test_validate_transaction(self, db_session):
        service = AccountService(db_session)
        
        # Create checking account
        account_data = AccountCreate(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000.00")
        )
        account = await service.create_account(account_data)
        
        # Test valid debit transaction
        is_valid, error = await service.validate_transaction(
            account,
            {
                "amount": Decimal("500.00"),
                "transaction_type": "debit"
            }
        )
        assert is_valid is True
        assert error is None
        
        # Test invalid debit transaction (exceeds balance)
        is_valid, error = await service.validate_transaction(
            account,
            {
                "amount": Decimal("1500.00"),
                "transaction_type": "debit"
            }
        )
        assert is_valid is False
        assert "exceeds available balance" in error

    async def test_validate_credit_transaction(self, db_session):
        service = AccountService(db_session)
        
        # Create credit account
        account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00"),
            total_limit=Decimal("5000.00")
        )
        account = await service.create_account(account_data)
        
        # Test valid debit transaction
        is_valid, error = await service.validate_transaction(
            account,
            {
                "amount": Decimal("3000.00"),
                "transaction_type": "debit"
            }
        )
        assert is_valid is True
        assert error is None
        
        # Test invalid debit transaction (exceeds credit limit)
        is_valid, error = await service.validate_transaction(
            account,
            {
                "amount": Decimal("6000.00"),
                "transaction_type": "debit"
            }
        )
        assert is_valid is False
        assert "exceeds available credit" in error
        
    async def test_validate_credit_limit_history(self, db_session):
        """Test validation of credit limit history creation"""
        service = AccountService(db_session)
        
        # Create credit account
        credit_account_data = AccountCreate(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("0.00"),
            total_limit=Decimal("5000.00")
        )
        credit_account = await service.create_account(credit_account_data)
        
        # Create checking account
        checking_account_data = AccountCreate(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000.00")
        )
        checking_account = await service.create_account(checking_account_data)
        
        # Test validation with credit account (should succeed)
        is_valid, error = await service.validate_credit_limit_history(credit_account.id)
        assert is_valid is True
        assert error is None
        
        # Test validation with checking account (should fail)
        is_valid, error = await service.validate_credit_limit_history(checking_account.id)
        assert is_valid is False
        assert "Credit limit history can only be created for credit accounts" in error
        
        # Test validation with non-existent account
        is_valid, error = await service.validate_credit_limit_history(9999)
        assert is_valid is False
        assert "Account with ID 9999 not found" in error
