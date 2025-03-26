from typing import List

import pytest_asyncio

from src.models.categories import Category
from src.models.income_categories import IncomeCategory


@pytest_asyncio.fixture
async def test_category(db_session) -> Category:
    """Create a test category for use in tests."""
    # Create model instance directly
    category = Category(
        name="Test Bill Category",
        description="Test category for bill tests",
    )
    
    # Add to session manually
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    
    return category


@pytest_asyncio.fixture
async def test_income_category(db_session) -> IncomeCategory:
    """Create a test income category for use in tests."""
    # Create model instance directly
    income_category = IncomeCategory(
        name="Test Income Category",
        description="Test category for income",
    )
    
    # Add to session manually
    db_session.add(income_category)
    await db_session.flush()
    await db_session.refresh(income_category)
    
    return income_category


@pytest_asyncio.fixture
async def test_multiple_categories(db_session) -> List[IncomeCategory]:
    """Fixture to create multiple income categories for testing."""
    # Create multiple income categories with various attributes
    category_data = [
        {
            "name": "Salary",
            "description": "Regular employment income",
        },
        {
            "name": "Freelance",
            "description": "Income from freelance work",
        },
        {
            "name": "Investments",
            "description": "Income from investments",
        },
        {
            "name": "Rental Income",
            "description": "Income from rental properties",
        },
    ]

    # Create the categories using direct model instantiation
    created_categories = []
    for data in category_data:
        # Create model instance directly
        income_category = IncomeCategory(
            name=data["name"],
            description=data["description"],
        )
        
        # Add to session manually
        db_session.add(income_category)
        created_categories.append(income_category)
    
    # Flush to get IDs and establish database rows
    await db_session.flush()
    
    # Refresh all entries to make sure they reflect what's in the database
    for category in created_categories:
        await db_session.refresh(category)
        
    return created_categories
