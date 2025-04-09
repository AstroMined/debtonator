"""
Account type registry for polymorphic account management.

The AccountTypeRegistry provides a central registry for all account types in the system,
storing the associated model classes, schema classes, and metadata for each type.
This enables dynamic account type management and validation.

Implements the singleton pattern for global access to registered account types.
"""

from typing import Any, ClassVar, Dict, List, Optional, Type


class RegistryNotInitializedException(Exception):
    """
    Raised when a registry operation is attempted but the registry is not initialized.

    This exception indicates that the account type registry has not been properly
    initialized before being used, which is a critical system error.
    """


class AccountTypeRegistry:
    """
    Registry for managing account types and their associated classes and metadata.

    This class implements the singleton pattern to ensure a single registry instance
    exists across the application. Account types can be registered with their
    associated model classes, schema classes, and metadata, and can be retrieved
    by type ID or filtered by category.

    Implemented as part of ADR-016 Account Type Expansion.
    """

    _instance: ClassVar[Optional["AccountTypeRegistry"]] = None

    def __new__(cls) -> "AccountTypeRegistry":
        """
        Create a new AccountTypeRegistry instance or return the existing instance.

        Returns:
            AccountTypeRegistry: The singleton registry instance
        """
        if cls._instance is None:
            cls._instance = super(AccountTypeRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the registry with an empty dictionary."""
        self._registry: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        account_type_id: str,
        model_class: Type,
        schema_class: Type,
        name: str,
        description: str,
        category: str,
        repository_module: Optional[str] = None,
        service_module: Optional[str] = None,
        feature_flag: Optional[str] = None,
    ) -> None:
        """
        Register a new account type with its associated classes and metadata.

        Args:
            account_type_id: The unique identifier for the account type
            model_class: The SQLAlchemy model class for this account type
            schema_class: The Pydantic schema class for this account type
            name: The human-readable name of the account type
            description: A description of the account type
            category: The category this account type belongs to (e.g., Banking, Investment)
            repository_module: Optional module path for type-specific repository operations
            service_module: Optional module path for type-specific service operations
            feature_flag: Optional feature flag that controls this account type's availability
        """
        self._registry[account_type_id] = {
            "model_class": model_class,
            "schema_class": schema_class,
            "name": name,
            "description": description,
            "category": category,
            "repository_module": repository_module,  # Store the repository module path
            "service_module": service_module,  # Store the service module path
            "feature_flag": feature_flag,
        }

    def get_model_class(self, account_type_id: str) -> Optional[Type]:
        """
        Get the model class for a given account type.

        Args:
            account_type_id: The account type identifier

        Returns:
            The SQLAlchemy model class for the account type, or None if not found
        """
        return self._registry.get(account_type_id, {}).get("model_class")

    def get_schema_class(self, account_type_id: str) -> Optional[Type]:
        """
        Get the schema class for a given account type.

        Args:
            account_type_id: The account type identifier

        Returns:
            The Pydantic schema class for the account type, or None if not found
        """
        return self._registry.get(account_type_id, {}).get("schema_class")

    def get_all_types(self, feature_flag_service=None) -> List[Dict[str, Any]]:
        """
        Get all registered account types.

        Args:
            feature_flag_service: Optional feature flag service to filter types by enabled flags

        Returns:
            A list of dictionaries with account type information

        Raises:
            RegistryNotInitializedException: If the registry has not been initialized
        """
        if not self._registry:
            raise RegistryNotInitializedException(
                "Account type registry has not been initialized"
            )

        result = []

        for type_id, info in self._registry.items():
            # Skip types that are controlled by disabled feature flags
            if feature_flag_service and info.get("feature_flag"):
                if not feature_flag_service.is_enabled(info["feature_flag"]):
                    continue

            result.append(
                {
                    "id": type_id,
                    "name": info["name"],
                    "description": info["description"],
                    "category": info["category"],
                }
            )

        return result

    def get_types_by_category(
        self, category: str, feature_flag_service=None
    ) -> List[Dict[str, Any]]:
        """
        Get account types filtered by category.

        Args:
            category: The category to filter by
            feature_flag_service: Optional feature flag service to filter types by enabled flags

        Returns:
            A list of dictionaries with account type information for the specified category
        """
        result = []

        for type_id, info in self._registry.items():
            if info["category"] != category:
                continue

            # Skip types that are controlled by disabled feature flags
            if feature_flag_service and info.get("feature_flag"):
                if not feature_flag_service.is_enabled(info["feature_flag"]):
                    continue

            result.append(
                {
                    "id": type_id,
                    "name": info["name"],
                    "description": info["description"],
                    "category": info["category"],
                }
            )

        return result

    def is_valid_account_type(
        self, account_type_id: str, feature_flag_service=None
    ) -> bool:
        """
        Check if an account type ID is valid and available.

        Args:
            account_type_id: The account type identifier to check
            feature_flag_service: Optional feature flag service to check if type is enabled

        Returns:
            True if the account type is valid and available, False otherwise

        Raises:
            RegistryNotInitializedException: If the registry has not been initialized
        """
        if not self._registry:
            raise RegistryNotInitializedException(
                "Account type registry has not been initialized"
            )

        if account_type_id not in self._registry:
            return False

        # Check if the account type is controlled by a feature flag
        if feature_flag_service and self._registry[account_type_id].get("feature_flag"):
            flag = self._registry[account_type_id]["feature_flag"]
            return feature_flag_service.is_enabled(flag)

        return True

    def get_repository_module(self, account_type_id: str) -> Optional[str]:
        """
        Get the repository module path for a given account type.

        Args:
            account_type_id: The account type identifier

        Returns:
            The repository module path for the account type, or None if not found
        """
        return self._registry.get(account_type_id, {}).get("repository_module")

    def get_service_module(self, account_type_id: str) -> Optional[str]:
        """
        Get the service module path for a given account type.

        Args:
            account_type_id: The account type identifier

        Returns:
            The service module path for the account type, or None if not found
        """
        return self._registry.get(account_type_id, {}).get("service_module")

    def get_categories(self, feature_flag_service=None) -> List[str]:
        """
        Get all unique categories of registered account types.

        Args:
            feature_flag_service: Optional feature flag service to filter by enabled flags

        Returns:
            A list of unique category names
        """
        categories = set()

        for type_id, info in self._registry.items():
            # Skip types that are controlled by disabled feature flags
            if feature_flag_service and info.get("feature_flag"):
                if not feature_flag_service.is_enabled(info["feature_flag"]):
                    continue

            categories.add(info["category"])

        return sorted(list(categories))


# Global instance for convenience - follows singleton pattern
account_type_registry = AccountTypeRegistry()
