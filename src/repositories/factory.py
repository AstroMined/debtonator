"""
Repository factory implementation.

This module provides a factory for creating repositories with specialized functionality
based on account types. It dynamically loads type-specific repository modules and
binds their functions to the base repository instance.

It also handles feature flag enforcement through proxies that intercept repository
method calls and apply feature flag restrictions based on centralized configuration.

Implemented as part of ADR-016 Account Type Expansion, ADR-019 Banking Account Types,
and ADR-024 Feature Flag System.
"""

import importlib
import inspect
import logging
from typing import Any, Dict, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import (
    DatabaseConfigProvider,
    InMemoryConfigProvider,
)
from src.registry.account_types import account_type_registry
from src.repositories.accounts import AccountRepository
from src.repositories.base_repository import BaseRepository
from src.repositories.proxies.feature_flag_proxy import FeatureFlagRepositoryProxy
from src.services.feature_flags import FeatureFlagService

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """
    Factory for creating repositories with specialized functionality.

    This class implements the factory pattern for creating repositories with
    type-specific functionality. It dynamically loads repository modules based
    on account types and binds their functions to the base repository instance.
    """

    # Cache for loaded repository modules
    _module_cache: Dict[str, Any] = {}

    @classmethod
    async def create_account_repository(
        cls,
        session: AsyncSession,
        account_type: Optional[str] = None,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ) -> AccountRepository:
        """
        Create an account repository with specialized functionality based on account type.

        Args:
            session: SQLAlchemy async session
            account_type: Optional account type to determine specialized functionality
            feature_flag_service: Optional feature flag service for feature validation
            config_provider: Optional config provider for feature requirements

        Returns:
            AccountRepository with specialized functionality for the given type,
            wrapped with FeatureFlagRepositoryProxy if feature_flag_service is provided
        """
        # Create the base repository
        base_repo = AccountRepository(session)

        # If no account type is specified, return the base repository
        if not account_type:
            # Wrap with proxy if feature flag service is provided
            if feature_flag_service:
                return await cls._wrap_with_proxy(
                    base_repo, feature_flag_service, session, config_provider
                )
            return base_repo

        # If account type is specified but registry is not available,
        # try to load the module using default path structure
        module_path = cls._get_module_path(account_type)
        if not module_path:
            # Wrap with proxy if feature flag service is provided
            if feature_flag_service:
                return await cls._wrap_with_proxy(
                    base_repo, feature_flag_service, session, config_provider
                )
            return base_repo

        # Get the specialized module
        module = cls._get_or_load_module(module_path)
        if not module:
            # Wrap with proxy if feature flag service is provided
            if feature_flag_service:
                return await cls._wrap_with_proxy(
                    base_repo, feature_flag_service, session, config_provider
                )
            return base_repo

        # Bind specialized functions to the base repository
        cls._bind_module_functions(base_repo, module, session)

        # Wrap with proxy if feature flag service is provided
        if feature_flag_service:
            return await cls._wrap_with_proxy(
                base_repo, feature_flag_service, session, config_provider
            )

        return base_repo

    @classmethod
    async def _wrap_with_proxy(
        cls,
        repository: Any,
        feature_flag_service: FeatureFlagService,
        session: AsyncSession,
        config_provider: Optional[Any] = None,
    ) -> Any:
        """
        Wrap a repository with the FeatureFlagRepositoryProxy.

        Args:
            repository: Repository instance to wrap
            feature_flag_service: Feature flag service for checking flag values
            session: SQLAlchemy async session
            config_provider: Optional config provider for feature requirements

        Returns:
            Wrapped repository
        """
        # Create config provider if not provided
        if config_provider is None:
            # Try to use database config provider
            try:
                config_provider = DatabaseConfigProvider(session)
                logger.debug(
                    "Using DatabaseConfigProvider for feature flag requirements"
                )
            except Exception as e:
                # Fall back to in-memory provider if database provider fails
                logger.warning(
                    f"Could not create DatabaseConfigProvider: {e}. Using InMemoryConfigProvider"
                )
                config_provider = InMemoryConfigProvider()

        # Create and return the proxy
        return FeatureFlagRepositoryProxy(
            repository=repository,
            feature_flag_service=feature_flag_service,
            config_provider=config_provider,
        )

    @classmethod
    def _get_module_path(cls, account_type: str) -> Optional[str]:
        """
        Get the module path for a given account type.

        Args:
            account_type: Account type identifier

        Returns:
            Module path or None if not found
        """
        # Try to get the module path from the registry
        if account_type_registry:
            module_path = account_type_registry.get_repository_module(account_type)
            if module_path:
                return module_path

        # If registry doesn't have a module path, try to use a default path based on the type
        if "_" in account_type:
            category, sub_type = account_type.split("_", 1)
            return f"src.repositories.account_types.{category}.{sub_type}"

        # Try to map common account types to default modules
        type_to_module = {
            "checking": "src.repositories.account_types.banking.checking",
            "savings": "src.repositories.account_types.banking.savings",
            "credit": "src.repositories.account_types.banking.credit",
            "bnpl": "src.repositories.account_types.banking.bnpl",
            "payment_app": "src.repositories.account_types.banking.payment_app",
            "ewa": "src.repositories.account_types.banking.ewa",
            "mortgage": "src.repositories.account_types.loan.mortgage",
            "personal": "src.repositories.account_types.loan.personal",
            "auto": "src.repositories.account_types.loan.auto",
            "student": "src.repositories.account_types.loan.student",
            "brokerage": "src.repositories.account_types.investment.brokerage",
            "retirement": "src.repositories.account_types.investment.retirement",
            "crypto": "src.repositories.account_types.investment.crypto",
        }

        return type_to_module.get(account_type)

    @classmethod
    def _get_or_load_module(cls, module_path: str) -> Optional[Any]:
        """
        Get a cached module or load it if not cached.

        Args:
            module_path: Module path to load

        Returns:
            Loaded module or None if loading fails
        """
        # Return cached module if available
        if module_path in cls._module_cache:
            return cls._module_cache[module_path]

        # Try to import the module
        try:
            module = importlib.import_module(module_path)
            cls._module_cache[module_path] = module
            return module
        except ImportError as e:
            # Log the error but don't raise an exception
            logger.warning(f"Could not import repository module {module_path}: {e}")
            return None

    @classmethod
    def _bind_module_functions(
        cls,
        repo: BaseRepository,
        module: Any,
        session: AsyncSession,
    ) -> None:
        """
        Bind functions from the module to the repository instance.

        Args:
            repo: Repository instance to bind functions to
            module: Module containing functions to bind
            session: SQLAlchemy async session to pass to the bound functions
        """
        # Find all async functions in the module that take a session as first parameter
        for name, func in inspect.getmembers(module, inspect.iscoroutinefunction):
            if name.startswith("_"):
                continue

            # Create a bound method that passes the session to the function
            async def bound_method(*args, _func=func, **kwargs):
                return await _func(session, *args, **kwargs)

            # Set the bound method's name and docstring
            bound_method.__name__ = name
            bound_method.__doc__ = func.__doc__

            # Bind the method to the repository instance
            setattr(repo, name, bound_method)

        logger.debug(f"Bound {module.__name__} functions to repository")


class RepositoryFactoryHelper:
    """
    Helper class with utility methods for working with repositories.
    """

    @staticmethod
    async def get_available_repository_functions(account_type: str) -> Set[str]:
        """
        Get the names of specialized repository functions available for an account type.

        Args:
            account_type: Account type to check

        Returns:
            Set of function names available for this account type
        """
        module_path = RepositoryFactory._get_module_path(account_type)
        if not module_path:
            return set()

        module = RepositoryFactory._get_or_load_module(module_path)
        if not module:
            return set()

        functions = {
            name
            for name, func in inspect.getmembers(module, inspect.iscoroutinefunction)
            if not name.startswith("_")
        }

        return functions
