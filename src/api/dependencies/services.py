"""
Service dependency providers for FastAPI.

This module provides FastAPI dependency functions that create and inject service
instances into API routes.
"""

from fastapi import Depends

from src.api.dependencies.repositories import (
    get_account_repository,
    get_credit_limit_history_repository,
    get_statement_history_repository,
    get_transaction_history_repository,
)
from src.repositories.accounts import AccountRepository
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.services.accounts import AccountService


def get_account_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    statement_repo: StatementHistoryRepository = Depends(
        get_statement_history_repository
    ),
    credit_limit_repo: CreditLimitHistoryRepository = Depends(
        get_credit_limit_history_repository
    ),
    transaction_repo: TransactionHistoryRepository = Depends(
        get_transaction_history_repository
    ),
) -> AccountService:
    """
    Dependency provider for account service.

    Args:
        account_repo (AccountRepository): Account repository from dependency injection
        statement_repo (StatementHistoryRepository): Statement history repository from dependency injection
        credit_limit_repo (CreditLimitHistoryRepository): Credit limit history repository from dependency injection
        transaction_repo (TransactionHistoryRepository): Transaction history repository from dependency injection

    Returns:
        AccountService: Account service instance
    """
    return AccountService(
        account_repo=account_repo,
        statement_repo=statement_repo,
        credit_limit_repo=credit_limit_repo,
        transaction_repo=transaction_repo,
    )
