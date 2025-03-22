"""
Integration tests for the AccountRepository.

This module contains tests for the AccountRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.accounts import AccountRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.schemas.accounts import AccountCreate, AccountUpdate
from src.schemas.statement_history import StatementHistoryCreate
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.statement_history import create_statement_history_schema


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def statement_history_repository(db_session: AsyncSession) -> StatementHistoryRepository:
    """Fixture for StatementHistoryRepository with test database session."""
    return StatementHistoryRepository(db_session)


@pytest_asyncio.fixture
async def test_account(account_repository: AccountRepository) -> Account:
    """Create a test checking account for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Checking Account",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    
    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_credit_account(account_repository: AccountRepository) -> Account:
    """Create a test credit account for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Credit Card",
        account_type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),
    )
    
    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
) -> StatementHistory:
    """Create a test statement history entry for a credit account."""
    # 1. ARRANGE: No setup needed for this fixture
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    statement_schema = create_statement_history_schema(
        account_id=test_credit_account.id,
        statement_date=datetime.utcnow() - timedelta(days=15),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=datetime.utcnow() + timedelta(days=15),
    )
    
    # Convert validated schema to dict for repository
    validated_data = statement_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    return await statement_history_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_accounts(account_repository: AccountRepository) -> List[Account]:
    """Create multiple test accounts of different types."""
    # 1. ARRANGE: No setup needed for this fixture
    
    # Create accounts of different types
    account_types = [
        ("Checking A", "checking", Decimal("1200.00")),
        ("Savings B", "savings", Decimal("5000.00")),
        ("Credit Card C", "credit", Decimal("-700.00")),
        ("Investment D", "investment", Decimal("10000.00")),
    ]
    
    accounts = []
    for name, acc_type, balance in account_types:
        # 2. SCHEMA: Create and validate through Pydantic schema
        account_schema = create_account_schema(
            name=name,
            account_type=acc_type,
            available_balance=balance,
            total_limit=Decimal("3000.00") if acc_type == "credit" else None,
            available_credit=Decimal("2300.00") if acc_type == "credit" else None,
        )
        
        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        account = await account_repository.create(validated_data)
        accounts.append(account)
    
    return accounts


class TestAccountRepository:
    """
    Tests for the AccountRepository.

    These tests follow the standard 4-step pattern (Arrange-Schema-Act-Assert)
    for repository testing, simulating proper service-to-repository validation flow.
    """

    @pytest.mark.asyncio
    async def test_create_account(self, account_repository: AccountRepository):
        """Test creating an account with proper validation flow."""
        # 1. ARRANGE: No setup needed for this test
        
        # 2. SCHEMA: Create and validate through Pydantic schema
        account_schema = create_account_schema(
            name="New Test Account",
            account_type="savings",
            available_balance=Decimal("2500.00"),
            description="Test savings account created through repository",
        )
        
        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()
        
        # 3. ACT: Pass validated data to repository
        result = await account_repository.create(validated_data)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.name == "New Test Account"
        assert result.type == "savings"
        assert result.available_balance == Decimal("2500.00")
        assert result.description == "Test savings account created through repository"
        assert result.created_at is not None
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_account(
        self, account_repository: AccountRepository, test_account: Account
    ):
        """Test retrieving an account by ID."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get the account by ID
        result = await account_repository.get(test_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_account.id
        assert result.name == test_account.name
        assert result.type == test_account.type
        assert result.available_balance == test_account.available_balance

    @pytest.mark.asyncio
    async def test_update_account(
        self, account_repository: AccountRepository, test_account: Account
    ):
        """Test updating an account with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. SCHEMA: Create and validate update data through Pydantic schema
        update_schema = AccountUpdate(
            id=test_account.id,
            name="Updated Account Name",
            description="Updated account description",
        )
        
        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump(exclude={"id"})
        
        # 3. ACT: Pass validated data to repository
        result = await account_repository.update(test_account.id, update_data)
        
        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_account.id
        assert result.name == "Updated Account Name"
        assert result.description == "Updated account description"
        # Fields not in update_data should remain unchanged
        assert result.type == test_account.type
        assert result.available_balance == test_account.available_balance
        assert result.updated_at > test_account.updated_at

    @pytest.mark.asyncio
    async def test_delete_account(
        self, account_repository: AccountRepository, test_account: Account
    ):
        """Test deleting an account."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Delete the account
        result = await account_repository.delete(test_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is True
        
        # Verify the account is actually deleted
        deleted_check = await account_repository.get(test_account.id)
        assert deleted_check is None

    @pytest.mark.asyncio
    async def test_get_by_name(
        self, account_repository: AccountRepository, test_account: Account
    ):
        """Test getting an account by name."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get account by name
        result = await account_repository.get_by_name(test_account.name)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_account.id
        assert result.name == test_account.name

    @pytest.mark.asyncio
    async def test_get_with_statement_history(
        self,
        account_repository: AccountRepository,
        test_credit_account: Account,
        test_statement_history: StatementHistory,
    ):
        """Test getting an account with its statement history loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get account with statement history
        result = await account_repository.get_with_statement_history(test_credit_account.id)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_account.id
        assert hasattr(result, "statement_history")
        assert len(result.statement_history) >= 1
        
        # Check that statement history is loaded correctly
        statement = result.statement_history[0]
        assert statement.account_id == test_credit_account.id

    @pytest.mark.asyncio
    async def test_get_with_relationships(
        self,
        account_repository: AccountRepository,
        test_credit_account: Account,
        test_statement_history: StatementHistory,
    ):
        """Test getting an account with multiple relationships loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get account with specified relationships
        result = await account_repository.get_with_relationships(
            test_credit_account.id,
            include_statements=True,
            include_balance_history=True,
            include_credit_limit_history=True,
        )
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_account.id
        assert hasattr(result, "statement_history")
        assert hasattr(result, "balance_history")
        assert hasattr(result, "credit_limit_history")
        
        # Check that statement history is loaded correctly
        assert len(result.statement_history) >= 1
        statement = result.statement_history[0]
        assert statement.account_id == test_credit_account.id

    @pytest.mark.asyncio
    async def test_get_accounts_with_statements(
        self,
        account_repository: AccountRepository,
        test_credit_account: Account,
        test_statement_history: StatementHistory,
    ):
        """Test getting accounts with statement history loaded."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get all accounts with statements
        results = await account_repository.get_accounts_with_statements()
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1
        
        # Find our test credit account
        test_account_found = False
        for account in results:
            if account.id == test_credit_account.id:
                test_account_found = True
                assert hasattr(account, "statement_history")
                assert len(account.statement_history) >= 1
                break
        
        assert test_account_found, "Test credit account not found in results"

    @pytest.mark.asyncio
    async def test_get_active_accounts(
        self, account_repository: AccountRepository, test_multiple_accounts: List[Account]
    ):
        """Test getting all active accounts."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get all active accounts
        results = await account_repository.get_active_accounts()
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= len(test_multiple_accounts)
        
        # Verify all test accounts are in the results
        test_account_ids = {account.id for account in test_multiple_accounts}
        result_account_ids = {account.id for account in results}
        assert test_account_ids.issubset(result_account_ids)

    @pytest.mark.asyncio
    async def test_get_by_type(
        self, account_repository: AccountRepository, test_multiple_accounts: List[Account]
    ):
        """Test getting accounts by type."""
        # 1. ARRANGE: Setup is already done with fixtures
        
        # 2. ACT: Get accounts by type (checking)
        results = await account_repository.get_by_type("checking")
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1
        for account in results:
            assert account.type == "checking"
        
        # Also test with credit type
        credit_results = await account_repository.get_by_type("credit")
        assert len(credit_results) >= 1
        for account in credit_results:
            assert account.type == "credit"

    @pytest.mark.asyncio
    async def test_update_balance(
        self, account_repository: AccountRepository, test_account: Account
    ):
        """Test updating an account balance."""
        # 1. ARRANGE: Setup is already done with fixtures
        original_balance = test_account.available_balance
        amount_change = Decimal("250.00")
        
        # 2. ACT: Update the account balance
        result = await account_repository.update_balance(test_account.id, amount_change)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_account.id
        assert result.available_balance == original_balance + amount_change

    @pytest.mark.asyncio
    async def test_update_balance_credit_account(
        self, account_repository: AccountRepository, test_credit_account: Account
    ):
        """Test updating a credit account balance which should update available credit."""
        # 1. ARRANGE: Setup is already done with fixtures
        original_balance = test_credit_account.available_balance
        original_credit = test_credit_account.available_credit
        amount_change = Decimal("-200.00")  # Increasing debt (more negative balance)
        
        # 2. ACT: Update the credit account balance
        result = await account_repository.update_balance(test_credit_account.id, amount_change)
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_account.id
        assert result.available_balance == original_balance + amount_change
        # For credit accounts, available credit should decrease when balance becomes more negative
        assert result.available_credit == original_credit - abs(amount_change)

    @pytest.mark.asyncio
    async def test_update_statement_balance(
        self, account_repository: AccountRepository, test_credit_account: Account
    ):
        """Test updating an account's statement balance and date."""
        # 1. ARRANGE: Setup is already done with fixtures
        new_statement_balance = Decimal("750.00")
        statement_date = datetime.utcnow()
        
        # 2. ACT: Update statement balance and date
        result = await account_repository.update_statement_balance(
            test_credit_account.id, new_statement_balance, statement_date
        )
        
        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_credit_account.id
        assert result.last_statement_balance == new_statement_balance
        # Compare dates with some tolerance for datetime precision differences
        date_diff = abs((result.last_statement_date - statement_date).total_seconds())
        assert date_diff < 2  # Less than 2 seconds difference

    @pytest.mark.asyncio
    async def test_find_accounts_with_low_balance(
        self, account_repository: AccountRepository, test_multiple_accounts: List[Account]
    ):
        """Test finding accounts with balance below threshold."""
        # 1. ARRANGE: Setup is already done with fixtures
        threshold = Decimal("1500.00")
        
        # 2. ACT: Find accounts with low balance
        results = await account_repository.find_accounts_with_low_balance(threshold)
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 2  # Should find checking and credit accounts
        for account in results:
            assert account.available_balance < threshold

    @pytest.mark.asyncio
    async def test_find_credit_accounts_near_limit(
        self, account_repository: AccountRepository, test_credit_account: Account
    ):
        """Test finding credit accounts near their credit limit."""
        # 1. ARRANGE: Setup is already done with fixtures
        # First update the credit account to be closer to limit
        update_data = {
            "available_balance": Decimal("-1800.00"),  # Close to total_limit of 2000
            "available_credit": Decimal("200.00"),
        }
        await account_repository.update(test_credit_account.id, update_data)
        
        # 2. ACT: Find credit accounts near limit (90% by default)
        results = await account_repository.find_credit_accounts_near_limit()
        
        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1
        
        # Verify our test account is in the results
        test_account_found = False
        for account in results:
            if account.id == test_credit_account.id:
                test_account_found = True
                # Verify it's actually near limit
                assert account.type == "credit"
                assert account.total_limit is not None
                assert account.available_credit is not None
                assert account.available_credit < (account.total_limit * Decimal("0.1"))
                break
        
        assert test_account_found, "Test credit account not found in near-limit accounts"

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test handling of validation errors that would be caught by the Pydantic schema."""
        # Try creating a schema with invalid data
        try:
            invalid_schema = AccountCreate(
                name="",  # Invalid empty name
                account_type="invalid_type",  # Invalid account type
                available_balance=None,  # Missing required field
            )
            assert False, "Schema should have raised a validation error"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            error_str = str(e).lower()
            assert "name" in error_str or "account_type" in error_str or "available_balance" in error_str
