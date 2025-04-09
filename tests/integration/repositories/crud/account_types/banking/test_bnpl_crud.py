# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for BNPL account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.bnpl import BNPLAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from tests.helpers.schema_factories.account_types.banking.bnpl_schema_factories import (
    create_bnpl_account_schema,
)

pytestmark = pytest.mark.asyncio


class TestBNPLAccountCrud:
    """Test CRUD operations for BNPL accounts."""

    @pytest.fixture
    async def repository(
        self, db_session: AsyncSession, feature_flag_service: FeatureFlagService
    ) -> AccountRepository:
        """Create a repository for testing."""
        return RepositoryFactory.create_account_repository(
            session=db_session,
            account_type="bnpl",
            feature_flag_service=feature_flag_service,
        )

    async def test_create_bnpl_account(self, repository: AccountRepository):
        """Test creating a BNPL account following the four-step pattern."""
        # 1. ARRANGE: Nothing needed here

        # 2. SCHEMA: Create and validate through Pydantic schema
        account_schema = create_bnpl_account_schema(
            name="My Affirm Account",
            bnpl_provider="Affirm",
            current_balance=Decimal("400.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=0,
            installment_amount=Decimal("100.00"),
            payment_frequency="biweekly",
        )

        # Convert validated schema to dict for repository
        validated_data = account_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        # Ensure only invalid fields are excluded
        invalid_fields = ["available_credit"]
        filtered_data = {
            k: v for k, v in validated_data.items() if k not in invalid_fields
        }
        result = await repository.create_typed_account("bnpl", filtered_data)

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert isinstance(result, BNPLAccount)
        assert result.id is not None
        assert result.name == "My Affirm Account"
        assert result.bnpl_provider == "Affirm"
        assert result.current_balance == Decimal("400.00")
        assert result.installment_count == 4
        assert result.installments_paid == 0
        assert result.installment_amount == Decimal("100.00")
        assert result.payment_frequency == "biweekly"

    async def test_get_bnpl_account(
        self, repository: AccountRepository, test_bnpl_account: BNPLAccount
    ):
        """Test retrieving a BNPL account by ID."""
        # 1. ARRANGE: Use fixture for test account

        # 2. ACT: Get account by ID
        result = await repository.get(test_bnpl_account.id)

        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert isinstance(result, BNPLAccount)
        assert result.id == test_bnpl_account.id
        assert result.name == test_bnpl_account.name
        assert result.bnpl_provider == test_bnpl_account.bnpl_provider

    async def test_update_bnpl_account(
        self, repository: AccountRepository, test_bnpl_account: BNPLAccount
    ):
        """Test updating a BNPL account."""
        # 1. ARRANGE: Use fixture for test account
        account_id = test_bnpl_account.id

        # 2. SCHEMA: Create update data with schema
        update_schema = create_bnpl_account_schema(
            name="Updated Affirm Account",
            installments_paid=1,  # Increment the installments paid
        )

        validated_data = update_schema.model_dump()

        # 3. ACT: Update the account
        result = await repository.update(account_id, validated_data)

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert isinstance(result, BNPLAccount)
        assert result.id == account_id
        assert result.name == "Updated Affirm Account"
        assert result.installments_paid == 1
        # Original properties should remain unchanged
        assert result.bnpl_provider == test_bnpl_account.bnpl_provider
        assert result.installment_count == test_bnpl_account.installment_count
        assert result.installment_amount == test_bnpl_account.installment_amount

    async def test_delete_bnpl_account(
        self, repository: AccountRepository, test_bnpl_account: BNPLAccount
    ):
        """Test deleting (soft delete) a BNPL account."""
        # 1. ARRANGE: Use fixture for test account
        account_id = test_bnpl_account.id

        # 2. ACT: Delete the account
        result = await repository.delete(account_id)

        # 3. ASSERT: Verify soft deletion
        assert result is True

        # Verify the account is marked as closed, not physically deleted
        account = await repository.get(account_id)
        assert account is not None
        assert account.is_closed is True

    async def test_mark_bnpl_payment_made(
        self, repository: AccountRepository, test_bnpl_account: BNPLAccount
    ):
        """Test updating a BNPL account to mark a payment as made."""
        # 1. ARRANGE: Use fixture for test account
        account_id = test_bnpl_account.id
        original_balance = test_bnpl_account.current_balance
        installment_amount = test_bnpl_account.installment_amount

        # 2. SCHEMA: Create update data to record a payment
        update_schema = create_bnpl_account_schema(
            current_balance=original_balance - installment_amount,
            installments_paid=test_bnpl_account.installments_paid + 1,
        )

        validated_data = update_schema.model_dump()

        # 3. ACT: Update the account
        result = await repository.update(account_id, validated_data)

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.current_balance == original_balance - installment_amount
        assert result.installments_paid == test_bnpl_account.installments_paid + 1

    async def test_feature_flag_controls_account_creation(
        self, repository: AccountRepository, feature_flag_service: FeatureFlagService
    ):
        """Test that feature flags control BNPL account creation."""
        # 1. ARRANGE: Disable the feature flag
        await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)

        # 2. SCHEMA: Create valid schema
        account_schema = create_bnpl_account_schema()
        validated_data = account_schema.model_dump()

        # 3. ACT & ASSERT: Should fail when flag is disabled
        with pytest.raises(ValueError) as excinfo:
            await repository.create_typed_account("bnpl", validated_data)

        assert "not available" in str(excinfo.value) or "not enabled" in str(
            excinfo.value
        )

        # Now enable the flag and retry
        await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)
        # Ensure only invalid fields are excluded
        invalid_fields = ["available_credit"]
        filtered_data = {
            k: v for k, v in validated_data.items() if k not in invalid_fields
        }
        result = await repository.create_typed_account("bnpl", filtered_data)

        # 4. ASSERT: Should succeed when flag is enabled
        assert result is not None
        assert result.account_type == "bnpl"
