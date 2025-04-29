"""
Fixtures for CategoryMatcher service tests.

This module provides fixtures for testing the CategoryMatcher service which handles
transaction categorization and matching.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.category_matcher import CategoryMatcher
from src.services.feature_flags import FeatureFlagService


@pytest.fixture
async def category_matcher(db_session: AsyncSession) -> CategoryMatcher:
    """
    Create a CategoryMatcher service instance for testing.

    Args:
        db_session: SQLAlchemy async session

    Returns:
        CategoryMatcher: Initialized CategoryMatcher service
    """
    return CategoryMatcher(db_session)


@pytest.fixture
async def category_matcher_with_flags(
    db_session: AsyncSession, feature_flag_service: FeatureFlagService
) -> CategoryMatcher:
    """
    Create a CategoryMatcher service instance with feature flags for testing.

    Args:
        db_session: SQLAlchemy async session
        feature_flag_service: Feature flag service instance

    Returns:
        CategoryMatcher: Initialized CategoryMatcher service with feature flags
    """
    return CategoryMatcher(db_session, feature_flag_service)


@pytest.fixture
def income_transaction():
    """
    Create a sample income transaction for testing.

    Returns:
        dict: Sample income transaction data
    """
    return {
        "type": "income",
        "source": "Salary",
        "category": "Income",
        "amount": 2000.00,
        "date": "2025-04-15",
    }


@pytest.fixture
def expense_transaction():
    """
    Create a sample expense transaction for testing.

    Returns:
        dict: Sample expense transaction data
    """
    return {
        "type": "expense",
        "description": "Groceries",
        "category": "Food",
        "amount": -150.00,
        "date": "2025-04-16",
    }


@pytest.fixture
def bill_transaction():
    """
    Create a sample bill transaction for testing.

    Returns:
        dict: Sample bill transaction data
    """
    return {
        "type": "bill",
        "name": "Electricity Bill",
        "category": "Utilities",
        "amount": -85.50,
        "due_date": "2025-04-20",
    }


@pytest.fixture
def transfer_transaction():
    """
    Create a sample transfer transaction for testing.

    Returns:
        dict: Sample transfer transaction data
    """
    return {
        "type": "transfer",
        "description": "To Savings",
        "amount": -500.00,
        "date": "2025-04-17",
    }


@pytest.fixture
def sample_transactions(
    income_transaction, expense_transaction, bill_transaction, transfer_transaction
):
    """
    Create a list of sample transactions of different types for testing.

    Args:
        income_transaction: Income transaction fixture
        expense_transaction: Expense transaction fixture
        bill_transaction: Bill transaction fixture
        transfer_transaction: Transfer transaction fixture

    Returns:
        list: List of sample transactions
    """
    return [
        income_transaction,
        expense_transaction,
        bill_transaction,
        transfer_transaction,
    ]
