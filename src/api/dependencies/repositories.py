"""
Repository dependency providers for FastAPI.

This module provides FastAPI dependency functions that create and inject repository
instances into API routes and services.
"""

from typing import Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.repositories.base_repository import BaseRepository
from src.repositories.accounts import AccountRepository
from src.repositories.balance_history import BalanceHistoryRepository
from src.repositories.balance_reconciliation import BalanceReconciliationRepository
from src.repositories.bill_splits import BillSplitRepository
from src.repositories.cashflow import CashflowForecastRepository
from src.repositories.categories import CategoryRepository
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.deposit_schedules import DepositScheduleRepository
from src.repositories.factory import RepositoryFactory
from src.repositories.income import IncomeRepository
from src.repositories.income_categories import IncomeCategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payment_schedules import PaymentScheduleRepository
from src.repositories.payment_sources import PaymentSourceRepository
from src.repositories.payments import PaymentRepository
from src.repositories.recurring_bills import RecurringBillRepository
from src.repositories.recurring_income import RecurringIncomeRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.transaction_history import TransactionHistoryRepository


def get_repository_factory(db: AsyncSession = Depends(get_db)) -> RepositoryFactory:
    """
    Dependency provider for repository factory.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        RepositoryFactory: Repository factory instance
    """
    return RepositoryFactory(db)


def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    """
    Dependency provider for account repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        AccountRepository: Account repository instance
    """
    return AccountRepository(db)


def get_liability_repository(db: AsyncSession = Depends(get_db)) -> LiabilityRepository:
    """
    Dependency provider for liability repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        LiabilityRepository: Liability repository instance
    """
    return LiabilityRepository(db)


def get_payment_repository(db: AsyncSession = Depends(get_db)) -> PaymentRepository:
    """
    Dependency provider for payment repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        PaymentRepository: Payment repository instance
    """
    return PaymentRepository(db)


def get_payment_source_repository(
    db: AsyncSession = Depends(get_db),
) -> PaymentSourceRepository:
    """
    Dependency provider for payment source repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        PaymentSourceRepository: Payment source repository instance
    """
    return PaymentSourceRepository(db)


def get_bill_split_repository(
    db: AsyncSession = Depends(get_db),
) -> BillSplitRepository:
    """
    Dependency provider for bill split repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        BillSplitRepository: Bill split repository instance
    """
    return BillSplitRepository(db)


def get_income_repository(db: AsyncSession = Depends(get_db)) -> IncomeRepository:
    """
    Dependency provider for income repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        IncomeRepository: Income repository instance
    """
    return IncomeRepository(db)


def get_recurring_bill_repository(
    db: AsyncSession = Depends(get_db),
) -> RecurringBillRepository:
    """
    Dependency provider for recurring bill repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        RecurringBillRepository: Recurring bill repository instance
    """
    return RecurringBillRepository(db)


def get_statement_history_repository(
    db: AsyncSession = Depends(get_db),
) -> StatementHistoryRepository:
    """
    Dependency provider for statement history repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        StatementHistoryRepository: Statement history repository instance
    """
    return StatementHistoryRepository(db)


def get_balance_history_repository(
    db: AsyncSession = Depends(get_db),
) -> BalanceHistoryRepository:
    """
    Dependency provider for balance history repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        BalanceHistoryRepository: Balance history repository instance
    """
    return BalanceHistoryRepository(db)


def get_category_repository(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    """
    Dependency provider for category repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        CategoryRepository: Category repository instance
    """
    return CategoryRepository(db)


def get_credit_limit_history_repository(
    db: AsyncSession = Depends(get_db),
) -> CreditLimitHistoryRepository:
    """
    Dependency provider for credit limit history repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        CreditLimitHistoryRepository: Credit limit history repository instance
    """
    return CreditLimitHistoryRepository(db)


def get_balance_reconciliation_repository(
    db: AsyncSession = Depends(get_db),
) -> BalanceReconciliationRepository:
    """
    Dependency provider for balance reconciliation repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        BalanceReconciliationRepository: Balance reconciliation repository instance
    """
    return BalanceReconciliationRepository(db)


def get_transaction_history_repository(
    db: AsyncSession = Depends(get_db),
) -> TransactionHistoryRepository:
    """
    Dependency provider for transaction history repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        TransactionHistoryRepository: Transaction history repository instance
    """
    return TransactionHistoryRepository(db)


def get_payment_schedule_repository(
    db: AsyncSession = Depends(get_db),
) -> PaymentScheduleRepository:
    """
    Dependency provider for payment schedule repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        PaymentScheduleRepository: Payment schedule repository instance
    """
    return PaymentScheduleRepository(db)


def get_deposit_schedule_repository(
    db: AsyncSession = Depends(get_db),
) -> DepositScheduleRepository:
    """
    Dependency provider for deposit schedule repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        DepositScheduleRepository: Deposit schedule repository instance
    """
    return DepositScheduleRepository(db)


def get_income_category_repository(
    db: AsyncSession = Depends(get_db),
) -> IncomeCategoryRepository:
    """
    Dependency provider for income category repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        IncomeCategoryRepository: Income category repository instance
    """
    return IncomeCategoryRepository(db)


def get_recurring_income_repository(
    db: AsyncSession = Depends(get_db),
) -> RecurringIncomeRepository:
    """
    Dependency provider for recurring income repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        RecurringIncomeRepository: Recurring income repository instance
    """
    return RecurringIncomeRepository(db)


def get_cashflow_forecast_repository(
    db: AsyncSession = Depends(get_db),
) -> CashflowForecastRepository:
    """
    Dependency provider for cashflow forecast repository.

    Args:
        db (AsyncSession): Database session from dependency injection

    Returns:
        CashflowForecastRepository: Cashflow forecast repository instance
    """
    return CashflowForecastRepository(db)


def get_repository(
    repository_class: Type[BaseRepository], 
    db: AsyncSession = Depends(get_db)
) -> BaseRepository:
    """
    Generic repository provider that can create any repository type.
    
    This function allows creating any repository type dynamically by passing
    the repository class as an argument. It's particularly useful for 
    dependency providers that need to create different repository types.
    
    Args:
        repository_class: The repository class to instantiate
        db: Database session from dependency injection
        
    Returns:
        An instance of the specified repository type
    """
    # Create and return repository instance
    return repository_class(db)
