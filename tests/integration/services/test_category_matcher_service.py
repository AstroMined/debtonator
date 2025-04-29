"""
Integration tests for the CategoryMatcher service.

This test suite verifies the CategoryMatcher service's ability to match transactions
to categories, including hierarchical relationships.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.registry.transaction_reference import transaction_reference_registry
from src.services.category_matcher import CategoryMatcher


@pytest.fixture
async def category_matcher(db_session: AsyncSession) -> CategoryMatcher:
    """Fixture to provide a CategoryMatcher instance for tests."""
    return CategoryMatcher(db_session)


@pytest.fixture
async def parent_category(db_session: AsyncSession, category_repository) -> Category:
    """Fixture to create a parent category for hierarchy testing."""
    category_data = {
        "name": "Electronics",
        "description": "Electronic devices and accessories",
        "parent_id": None,
    }
    return await category_repository.create(category_data)


@pytest.fixture
async def child_category(
    db_session: AsyncSession, category_repository, parent_category
) -> Category:
    """Fixture to create a child category for hierarchy testing."""
    category_data = {
        "name": "Computers",
        "description": "Desktop and laptop computers",
        "parent_id": parent_category.id,
    }
    return await category_repository.create(category_data)


@pytest.fixture
async def grandchild_category(
    db_session: AsyncSession, category_repository, child_category
) -> Category:
    """Fixture to create a grandchild category for hierarchy testing."""
    category_data = {
        "name": "Laptops",
        "description": "Portable laptop computers",
        "parent_id": child_category.id,
    }
    return await category_repository.create(category_data)


async def test_matches_category_exact_match(
    category_matcher: CategoryMatcher, test_category: Category
):
    """Test that exact category matches are detected correctly."""
    # Create a transaction with the exact category
    transaction = {
        "type": "expense",
        "description": "Office supplies",
        "category": test_category.name,
        "amount": -50.00,
    }

    # Verify exact match works
    result = await category_matcher.matches_category(transaction, test_category.name)
    assert result is True

    # Verify exact match with Category object works
    result = await category_matcher.matches_category(transaction, test_category)
    assert result is True


async def test_matches_category_no_match(
    category_matcher: CategoryMatcher, test_category: Category
):
    """Test that non-matching categories are correctly identified."""
    # Create a transaction with a different category
    transaction = {
        "type": "expense",
        "description": "Office supplies",
        "category": "Different Category",
        "amount": -50.00,
    }

    # Verify non-match is detected
    result = await category_matcher.matches_category(transaction, test_category.name)
    assert result is False


async def test_matches_category_no_category(category_matcher: CategoryMatcher):
    """Test handling of transactions without a category field."""
    # Create a transaction without a category
    transaction = {
        "type": "expense",
        "description": "Office supplies",
        "amount": -50.00,
    }

    # Verify transaction without category doesn't match any category
    result = await category_matcher.matches_category(transaction, "Any Category")
    assert result is False


async def test_matches_category_hierarchy(
    category_matcher: CategoryMatcher,
    parent_category: Category,
    child_category: Category,
    grandchild_category: Category,
):
    """Test hierarchical category matching works correctly."""
    # Create transactions with different levels of categories
    transactions = [
        {
            "type": "expense",
            "description": "New laptop",
            "category": grandchild_category.name,
            "amount": -1200.00,
        },
        {
            "type": "expense",
            "description": "Desktop computer",
            "category": child_category.name,
            "amount": -1500.00,
        },
        {
            "type": "expense",
            "description": "Smart watch",
            "category": parent_category.name,
            "amount": -350.00,
        },
    ]

    # Test matching with include_child_categories=True (default)
    # Parent should match all children
    for transaction in transactions:
        result = await category_matcher.matches_category(
            transaction, parent_category.name
        )
        assert result is True

    # Middle category should match itself and its children
    assert (
        await category_matcher.matches_category(transactions[0], child_category.name)
        is True
    )
    assert (
        await category_matcher.matches_category(transactions[1], child_category.name)
        is True
    )
    assert (
        await category_matcher.matches_category(transactions[2], child_category.name)
        is False
    )

    # Leaf category should only match itself
    assert (
        await category_matcher.matches_category(
            transactions[0], grandchild_category.name
        )
        is True
    )
    assert (
        await category_matcher.matches_category(
            transactions[1], grandchild_category.name
        )
        is False
    )
    assert (
        await category_matcher.matches_category(
            transactions[2], grandchild_category.name
        )
        is False
    )


async def test_matches_category_without_hierarchy(
    category_matcher: CategoryMatcher,
    parent_category: Category,
    child_category: Category,
    grandchild_category: Category,
):
    """Test category matching without including child categories."""
    # Create a transaction with the grandchild category
    transaction = {
        "type": "expense",
        "description": "New laptop",
        "category": grandchild_category.name,
        "amount": -1200.00,
    }

    # With include_child_categories=False, only exact matches should work
    assert (
        await category_matcher.matches_category(
            transaction, grandchild_category.name, include_child_categories=False
        )
        is True
    )

    assert (
        await category_matcher.matches_category(
            transaction, child_category.name, include_child_categories=False
        )
        is False
    )

    assert (
        await category_matcher.matches_category(
            transaction, parent_category.name, include_child_categories=False
        )
        is False
    )


async def test_get_matching_transactions(
    category_matcher: CategoryMatcher,
    parent_category: Category,
    child_category: Category,
):
    """Test filtering transactions by category."""
    # Create a list of transactions with different categories
    transactions = [
        {
            "type": "expense",
            "description": "New laptop",
            "category": child_category.name,
            "amount": -1200.00,
        },
        {
            "type": "expense",
            "description": "Smart watch",
            "category": parent_category.name,
            "amount": -350.00,
        },
        {
            "type": "expense",
            "description": "Office supplies",
            "category": "Other Category",
            "amount": -50.00,
        },
    ]

    # Get matching transactions for parent category (should include child)
    matching = await category_matcher.get_matching_transactions(
        transactions, parent_category.name
    )
    assert len(matching) == 2
    assert matching[0]["description"] == "New laptop"
    assert matching[1]["description"] == "Smart watch"

    # Get matching transactions for child category
    matching = await category_matcher.get_matching_transactions(
        transactions, child_category.name
    )
    assert len(matching) == 1
    assert matching[0]["description"] == "New laptop"

    # Get matching transactions without hierarchy
    matching = await category_matcher.get_matching_transactions(
        transactions, parent_category.name, include_child_categories=False
    )
    assert len(matching) == 1
    assert matching[0]["description"] == "Smart watch"


async def test_get_category_by_name(
    category_matcher: CategoryMatcher, test_category: Category
):
    """Test retrieving a category by name with caching."""
    # First call should hit the database
    category = await category_matcher.get_category_by_name(test_category.name)
    assert category is not None
    assert category.id == test_category.id
    assert category.name == test_category.name

    # Second call should use the cache
    category = await category_matcher.get_category_by_name(test_category.name)
    assert category is not None
    assert category.id == test_category.id

    # Non-existent category should return None
    category = await category_matcher.get_category_by_name("Non-existent Category")
    assert category is None


async def test_clear_caches(category_matcher: CategoryMatcher, test_category: Category):
    """Test that clearing caches works correctly."""
    # First call to populate cache
    await category_matcher.get_category_by_name(test_category.name)

    # Clear caches
    await category_matcher.clear_caches()

    # Verify caches are cleared (requires internal knowledge)
    assert len(category_matcher._category_cache) == 0
    assert len(category_matcher._relationship_cache) == 0


async def test_get_category_hierarchy(
    category_matcher: CategoryMatcher,
    parent_category: Category,
    child_category: Category,
    grandchild_category: Category,
):
    """Test retrieving a full category hierarchy."""
    # Get hierarchy for the grandchild category
    hierarchy = await category_matcher.get_category_hierarchy(grandchild_category.name)
    assert len(hierarchy) == 3
    assert hierarchy[0] == parent_category.name
    assert hierarchy[1] == child_category.name
    assert hierarchy[2] == grandchild_category.name

    # Get hierarchy for a mid-level category
    hierarchy = await category_matcher.get_category_hierarchy(child_category.name)
    assert len(hierarchy) == 2
    assert hierarchy[0] == parent_category.name
    assert hierarchy[1] == child_category.name

    # Get hierarchy for a top-level category
    hierarchy = await category_matcher.get_category_hierarchy(parent_category.name)
    assert len(hierarchy) == 1
    assert hierarchy[0] == parent_category.name

    # Get hierarchy for non-existent category
    hierarchy = await category_matcher.get_category_hierarchy("Non-existent Category")
    assert len(hierarchy) == 0


async def test_get_category_descendants(
    category_matcher: CategoryMatcher,
    parent_category: Category,
    child_category: Category,
    grandchild_category: Category,
):
    """Test retrieving category descendants."""
    # Get descendants for the parent category
    descendants = await category_matcher.get_category_descendants(parent_category.name)
    assert len(descendants) == 2
    assert child_category.name in descendants
    assert grandchild_category.name in descendants

    # Get descendants for a mid-level category
    descendants = await category_matcher.get_category_descendants(child_category.name)
    assert len(descendants) == 1
    assert grandchild_category.name in descendants

    # Get descendants for a leaf category
    descendants = await category_matcher.get_category_descendants(
        grandchild_category.name
    )
    assert len(descendants) == 0

    # Get descendants for non-existent category
    descendants = await category_matcher.get_category_descendants(
        "Non-existent Category"
    )
    assert len(descendants) == 0


async def test_transaction_registry_integration(
    category_matcher: CategoryMatcher, test_category: Category
):
    """Test integration with the transaction reference registry."""
    # Create transactions of different types with the same category
    transactions = [
        {
            "type": "expense",
            "description": "Office supplies",
            "category": test_category.name,
            "amount": -50.00,
        },
        {
            "type": "bill",
            "name": "Internet bill",
            "category": test_category.name,
            "amount": -89.99,
        },
        {
            "type": "income",
            "source": "Salary",
            "category": test_category.name,
            "amount": 2000.00,
        },
    ]

    # Transaction registry should extract the right field for each type
    for transaction in transactions:
        extracted_category = transaction_reference_registry.extract_category(
            transaction
        )
        assert extracted_category == test_category.name

        # Matcher should work with any transaction type
        result = await category_matcher.matches_category(
            transaction, test_category.name
        )
        assert result is True
