"""
System initialization service.

This module provides services for initializing and ensuring required system data
exists in the database during application startup.
"""

from src.repositories.categories import CategoryRepository


async def ensure_system_categories(category_repo: CategoryRepository) -> None:
    """
    Ensure system categories exist - called during initialization.

    This leverages the repository layer to check for and create the default
    category if needed, maintaining architectural consistency.

    Args:
        category_repo (CategoryRepository): Repository for Category operations
    """
    # This already handles creation if needed and ensures it's marked as a system category
    await category_repo.get_default_category_id()

    # Future system categories could be added here
    # For example: await category_repo.get_or_create_system_category("Bills", "Default bills category")
