"""
Service factory implementation.

This module provides a factory for creating services with specialized functionality
based on account types. It dynamically loads type-specific service modules and
binds their functions to the base service instance.

Implemented as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types.
Updated for ADR-024 Feature Flag System to support service proxies for feature enforcement.
"""

import importlib
import inspect
import logging
from typing import Any, Dict, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import ConfigProvider, DatabaseConfigProvider
from src.registry.account_types import account_type_registry
from src.repositories.factory import RepositoryFactory
from src.repositories.feature_flags import FeatureFlagRepository
from src.services.feature_flags import FeatureFlagService
from src.services.proxies.feature_flag_proxy import ServiceProxy

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating services with specialized functionality.

    This class implements the factory pattern for creating services with
    type-specific functionality. It dynamically loads service modules based
    on account types and binds their functions to the base service instance.
    """

    # Cache for loaded service modules
    _module_cache: Dict[str, Any] = {}

    @classmethod
    async def create_account_service(
        cls,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        apply_proxy: bool = True,
    ):
        """
        Create an account service with the ability to handle all account types.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for feature validation
            apply_proxy: Whether to apply the feature flag proxy (defaults to True when feature_flag_service is provided)

        Returns:
            AccountService with ability to load specialized functionality for different types,
            wrapped in a ServiceProxy if feature_flag_service is provided and apply_proxy is True
        """
        # Import here to avoid circular imports
        from src.repositories.credit_limit_history import CreditLimitHistoryRepository
        from src.repositories.statement_history import StatementHistoryRepository
        from src.repositories.transaction_history import TransactionHistoryRepository
        from src.services.accounts import AccountService

        # Create the repositories
        account_repo = await RepositoryFactory.create_account_repository(
            session=session,
            feature_flag_service=feature_flag_service,
        )
        statement_repo = StatementHistoryRepository(session)
        credit_limit_repo = CreditLimitHistoryRepository(session)
        transaction_repo = TransactionHistoryRepository(session)

        # Create the base service
        base_service = AccountService(
            account_repo=account_repo,
            statement_repo=statement_repo,
            credit_limit_repo=credit_limit_repo,
            transaction_repo=transaction_repo,
            feature_flag_service=feature_flag_service,
        )

        # Apply the feature flag proxy if requested and available
        if feature_flag_service and apply_proxy:
            # Get a config provider
            config_provider = await cls._get_config_provider(session)

            # Create a proxied service with feature flag enforcement
            logger.debug(f"Applying ServiceProxy to AccountService")
            return ServiceProxy(
                service=base_service,
                feature_flag_service=feature_flag_service,
                config_provider=config_provider,
            )

        return base_service

    @classmethod
    async def _get_config_provider(cls, session: AsyncSession) -> ConfigProvider:
        """
        Get the database-driven configuration provider.

        Args:
            session: SQLAlchemy async session

        Returns:
            DatabaseConfigProvider instance
        """
        feature_flag_repository = FeatureFlagRepository(session)
        return DatabaseConfigProvider(session)

    @classmethod
    async def bind_account_type_service(
        cls,
        service: Any,
        account_type: str,
        session: AsyncSession,
    ) -> bool:
        """
        Bind specialized functionality for a specific account type to a service.

        Args:
            service: Service instance to bind functions to
            account_type: Account type to determine specialized functionality
            session: SQLAlchemy async session

        Returns:
            True if binding was successful, False otherwise
        """
        # Get the module path for the account type
        module_path = cls._get_module_path(account_type)
        if not module_path:
            return False

        # Get the specialized module
        module = cls._get_or_load_module(module_path)
        if not module:
            return False

        # Bind specialized functions to the service
        cls._bind_module_functions(service, module, session)

        return True

    @classmethod
    def _get_module_path(cls, account_type: str) -> Optional[str]:
        """
        Get the service module path for a given account type.

        Args:
            account_type: Account type identifier

        Returns:
            Module path or None if not found
        """
        # Try to get the module path from the registry
        if account_type_registry:
            # For now, derive service module path from repository module path
            repo_module = account_type_registry.get_repository_module(account_type)
            if repo_module:
                # Convert from repository module path to service module path
                # Example: src.repositories.account_types.banking.checking -> src.services.account_types.banking.checking
                parts = repo_module.split(".")
                if len(parts) >= 2 and parts[1] == "repositories":
                    parts[1] = "services"
                    return ".".join(parts)

        # If registry doesn't have a module path, try to use a default path based on the type
        if "_" in account_type:
            category, sub_type = account_type.split("_", 1)
            return f"src.services.account_types.{category}.{sub_type}"

        # Try to map common account types to default modules
        type_to_module = {
            "checking": "src.services.account_types.banking.checking",
            "savings": "src.services.account_types.banking.savings",
            "credit": "src.services.account_types.banking.credit",
            "bnpl": "src.services.account_types.banking.bnpl",
            "payment_app": "src.services.account_types.banking.payment_app",
            "ewa": "src.services.account_types.banking.ewa",
            "mortgage": "src.services.account_types.loan.mortgage",
            "personal": "src.services.account_types.loan.personal",
            "auto": "src.services.account_types.loan.auto",
            "student": "src.services.account_types.loan.student",
            "brokerage": "src.services.account_types.investment.brokerage",
            "retirement": "src.services.account_types.investment.retirement",
            "crypto": "src.services.account_types.investment.crypto",
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
            logger.warning(f"Could not import service module {module_path}: {e}")
            return None

    @classmethod
    def _bind_module_functions(
        cls,
        service: Any,
        module: Any,
        session: AsyncSession,
    ) -> None:
        """
        Bind functions from the module to the service instance.

        Args:
            service: Service instance to bind functions to
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

            # Bind the method to the service instance
            setattr(service, name, bound_method)

        logger.debug(f"Bound {module.__name__} functions to service")


class ServiceFactoryHelper:
    """
    Helper class with utility methods for working with services.
    """

    @staticmethod
    def get_available_service_functions(account_type: str) -> Set[str]:
        """
        Get the names of specialized service functions available for an account type.

        Args:
            account_type: Account type to check

        Returns:
            Set of function names available for this account type
        """
        module_path = ServiceFactory._get_module_path(account_type)
        if not module_path:
            return set()

        module = ServiceFactory._get_or_load_module(module_path)
        if not module:
            return set()

        functions = {
            name
            for name, func in inspect.getmembers(module, inspect.iscoroutinefunction)
            if not name.startswith("_")
        }

        return functions
