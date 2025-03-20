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
