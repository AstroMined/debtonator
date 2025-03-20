"""
Repository dependency providers for FastAPI.

This module provides FastAPI dependency functions that create and inject repository 
instances into API routes and services.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.repositories.factory import RepositoryFactory
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payments import PaymentRepository
from src.repositories.payment_sources import PaymentSourceRepository
from src.repositories.bill_splits import BillSplitRepository


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


def get_payment_source_repository(db: AsyncSession = Depends(get_db)) -> PaymentSourceRepository:
    """
    Dependency provider for payment source repository.
    
    Args:
        db (AsyncSession): Database session from dependency injection
        
    Returns:
        PaymentSourceRepository: Payment source repository instance
    """
    return PaymentSourceRepository(db)


def get_bill_split_repository(db: AsyncSession = Depends(get_db)) -> BillSplitRepository:
    """
    Dependency provider for bill split repository.
    
    Args:
        db (AsyncSession): Database session from dependency injection
        
    Returns:
        BillSplitRepository: Bill split repository instance
    """
    return BillSplitRepository(db)
