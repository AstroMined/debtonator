"""
Account service dependencies.

This module provides dependencies for injecting account-related services
into FastAPI route handlers. It leverages FastAPI's dependency injection system
to create and provide service instances with all their required dependencies.

Implements service layer integration for ADR-016 Account Type Expansion,
ADR-019 Banking Account Types, and ADR-024 Feature Flags.
"""

from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_session

# Feature flag service dependency
from src.api.dependencies.services.feature_flags import get_feature_flag_service
from src.services.accounts import AccountService
from src.services.factory import ServiceFactory
from src.services.feature_flags import FeatureFlagService


async def get_account_service(
    session: AsyncSession = Depends(get_session),
    feature_flag_service: Optional[FeatureFlagService] = Depends(
        get_feature_flag_service
    ),
) -> AccountService:
    """
    Get an instance of AccountService with all required dependencies.

    This dependency creates an AccountService instance with proper repository
    dependencies and feature flag integration, using the ServiceFactory to
    create repositories with proper typing support.

    Args:
        session: Database session from FastAPI dependency
        feature_flag_service: Feature flag service from FastAPI dependency

    Returns:
        AccountService: Fully configured account service instance
    """
    # Use the service factory to create the account service
    return ServiceFactory.create_account_service(
        session=session,
        feature_flag_service=feature_flag_service,
    )
