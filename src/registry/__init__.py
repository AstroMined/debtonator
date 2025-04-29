"""
Registry module for in-memory configuration and state management.

This module provides registry classes that maintain in-memory state
for various system components. Registries are used to efficiently access
configuration data and runtime state without frequent database queries.

Available registries:
- account_type_registry: Registry for account type definitions
- feature_flag_registry: Registry for feature flag definitions
- transaction_reference_registry: Registry for transaction field access and categorization
"""

from src.registry.account_types import account_type_registry
from src.registry.feature_flags_registry import feature_flag_registry
from src.registry.transaction_reference import transaction_reference_registry

__all__ = [
    "account_type_registry",
    "feature_flag_registry",
    "transaction_reference_registry",
]
