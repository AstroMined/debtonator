"""
FastAPI dependency injection components.

This package contains various dependency providers for FastAPI endpoints,
simplifying dependency injection and ensuring consistent service and
repository usage across the API.
"""

from src.api.dependencies.repositories import (get_account_repository,
                                               get_repository_factory)
