"""
Fixtures for AccountService instances.

This module provides fixtures for AccountService objects needed by integration tests.
All fixtures follow the Real Objects Testing Philosophy without mocks.
"""

import pytest_asyncio

from src.repositories.accounts import AccountRepository
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.services.accounts import AccountService
from src.services.feature_flags import FeatureFlagService


@pytest_asyncio.fixture
async def account_service(
    account_repository: AccountRepository,
    statement_history_repository: StatementHistoryRepository,
    credit_limit_history_repository: CreditLimitHistoryRepository,
    transaction_history_repository: TransactionHistoryRepository,
    feature_flag_service: FeatureFlagService,
) -> AccountService:
    """
    Create and initialize an account service for testing.

    This fixture creates a real account service instance with all required repositories
    to follow ADR-012 (Validation Layer Standardization) and the Real Objects Testing Philosophy.

    Args:
        account_repository: Repository for account operations
        statement_history_repository: Repository for statement history
        credit_limit_history_repository: Repository for credit limit history
        transaction_history_repository: Repository for transaction history
        feature_flag_service: Service for feature flags

    Returns:
        AccountService: Service for account operations
    """
    return AccountService(
        session=account_repository.session,
        feature_flag_service=feature_flag_service,
    )
