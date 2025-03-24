"""
Integration tests for the IncomeCategoryRepository.

This module contains tests for the IncomeCategoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
IncomeCategoryRepository, ensuring proper validation flow and data integrity.
"""

from decimal import Decimal
from typing import List, Optional, Tuple

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.repositories.income import IncomeRepository
from src.repositories.income_categories import IncomeCategoryRepository
from src.schemas.income import IncomeCreate

# Import schemas and schema factories - essential part of the validation pattern
from src.schemas.income_categories import IncomeCategoryCreate, IncomeCategoryUpdate
from tests.helpers.schema_factories.income import create_income_schema
from tests.helpers.schema_factories.income_categories import (
    create_income_category_schema,
)

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def income_category_repository(
    db_session: AsyncSession,
) -> IncomeCategoryRepository:
    """Fixture for IncomeCategoryRepository with test database session."""
    return IncomeCategoryRepository(db_session)


@pytest_asyncio.fixture
async def income_repository(db_session: AsyncSession) -> IncomeRepository:
    """Fixture for IncomeRepository with test database session."""
    return IncomeRepository(db_session)


@pytest_asyncio.fixture
async def test_income_category(
    income_category_repository: IncomeCategoryRepository,
) -> IncomeCategory:
    """Fixture to create a test income category."""
    # Create and validate through Pydantic schema
    category_schema = create_income_category_schema(
        name="Test Income Category",
        description="A test category for income",
    )

    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()

    # Create category through repository
    return await income_category_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_categories(
    income_category_repository: IncomeCategoryRepository,
) -> List[IncomeCategory]:
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

    # Create the categories using the repository
    created_categories = []
    for data in category_data:
        # Create and validate through Pydantic schema
        category_schema = create_income_category_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = category_schema.model_dump()

        # Create category through repository
        category = await income_category_repository.create(validated_data)
        created_categories.append(category)

    return created_categories


@pytest_asyncio.fixture
async def test_income_entries(
    income_repository: IncomeRepository,
    test_multiple_categories: List[IncomeCategory],
) -> List[Income]:
    """Fixture to create test income entries associated with categories."""
    # Get category IDs for reference
    salary_category_id = test_multiple_categories[0].id
    freelance_category_id = test_multiple_categories[1].id
    investments_category_id = test_multiple_categories[2].id

    # Create income data with various attributes
    income_data = [
        {
            "source": "Monthly Salary",
            "amount": Decimal("3000.00"),
            "account_id": 1,  # Using a default account ID
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Bonus",
            "amount": Decimal("1000.00"),
            "account_id": 1,
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Website Project",
            "amount": Decimal("800.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": False,
        },
        {
            "source": "Logo Design",
            "amount": Decimal("350.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": True,
        },
        {
            "source": "Stock Dividends",
            "amount": Decimal("420.00"),
            "account_id": 1,
            "category_id": investments_category_id,
            "deposited": False,
        },
    ]

    # Create the income entries using the repository
    created_incomes = []
    for data in income_data:
        # Create and validate through Pydantic schema
        income_schema = create_income_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = income_schema.model_dump()

        # Create income through repository
        income = await income_repository.create(validated_data)
        created_incomes.append(income)

    return created_incomes


async def test_create_income_category(
    income_category_repository: IncomeCategoryRepository,
):
    """Test creating an income category with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    category_schema = create_income_category_schema(
        name="New Test Category",
        description="A newly created test category",
    )

    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await income_category_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "New Test Category"
    assert result.description == "A newly created test category"
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_income_category(
    income_category_repository: IncomeCategoryRepository,
    test_income_category: IncomeCategory,
):
    """Test retrieving an income category by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the income category
    result = await income_category_repository.get(test_income_category.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_income_category.id
    assert result.name == test_income_category.name
    assert result.description == test_income_category.description


async def test_update_income_category(
    income_category_repository: IncomeCategoryRepository,
    test_income_category: IncomeCategory,
):
    """Test updating an income category with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = IncomeCategoryUpdate(
        name="Updated Category Name",
        description="Updated category description",
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await income_category_repository.update(
        test_income_category.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_income_category.id
    assert result.name == "Updated Category Name"
    assert result.description == "Updated category description"
    assert result.updated_at > test_income_category.updated_at


async def test_delete_income_category(
    income_category_repository: IncomeCategoryRepository,
    test_income_category: IncomeCategory,
):
    """Test deleting an income category."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the income category
    result = await income_category_repository.delete(test_income_category.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_category = await income_category_repository.get(test_income_category.id)
    assert deleted_category is None


async def test_get_by_name(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
):
    """Test getting an income category by name."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
    test_name = "Salary"

    # 3. ACT: Get category by name
    result = await income_category_repository.get_by_name(test_name)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.name == test_name


async def test_get_with_income(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
    test_income_entries: List[Income],
):
    """Test getting an income category with its related income entries."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
    category_id = test_multiple_categories[0].id  # Salary category

    # 3. ACT: Get category with income entries
    result = await income_category_repository.get_with_income(category_id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == category_id
    assert hasattr(result, "income_entries")
    assert len(result.income_entries) >= 2  # Should have at least 2 income entries
    for income in result.income_entries:
        assert income.category_id == category_id


async def test_get_total_by_category(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
    test_income_entries: List[Income],
):
    """Test getting total amount of income by category."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get income totals by category
    results = await income_category_repository.get_total_by_category()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should have at least 3 categories with income

    # Results should be a list of (category, total) tuples
    for category, total in results:
        assert isinstance(category, IncomeCategory)
        assert isinstance(total, Decimal)

        # Verify totals are correct
        if category.name == "Salary":
            assert total == Decimal("4000.00")  # 3000 + 1000
        elif category.name == "Freelance":
            assert total == Decimal("1150.00")  # 800 + 350
        elif category.name == "Investments":
            assert total == Decimal("420.00")


async def test_get_categories_with_income_counts(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
    test_income_entries: List[Income],
):
    """Test getting income categories with income entry counts."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get categories with income counts
    results = await income_category_repository.get_categories_with_income_counts()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get all categories (4+)

    # Results should be a list of (category, count) tuples
    for category, count in results:
        assert isinstance(category, IncomeCategory)
        assert isinstance(count, int)

        # Verify counts are correct
        if category.name == "Salary":
            assert count == 2  # 2 salary entries
        elif category.name == "Freelance":
            assert count == 2  # 2 freelance entries
        elif category.name == "Investments":
            assert count == 1  # 1 investment entry
        elif category.name == "Rental Income":
            assert count == 0  # No rental income entries


async def test_find_categories_by_prefix(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
):
    """Test finding income categories by name prefix."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Find categories by prefix
    results = await income_category_repository.find_categories_by_prefix("Invest")

    # 4. ASSERT: Verify the operation results
    assert len(results) == 1  # Should find only "Investments"
    assert results[0].name == "Investments"

    # Test with another prefix
    results = await income_category_repository.find_categories_by_prefix("S")
    assert len(results) == 1  # Should find "Salary"
    assert results[0].name == "Salary"


async def test_delete_if_unused(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
    test_income_entries: List[Income],
):
    """Test deleting an income category only if it has no associated income entries."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # Get a category with income entries (should not delete)
    used_category_id = test_multiple_categories[0].id  # Salary category

    # Get a category without income entries (should delete)
    unused_category_id = test_multiple_categories[3].id  # Rental Income category

    # 3. ACT: Try to delete used category
    result_used = await income_category_repository.delete_if_unused(used_category_id)

    # Try to delete unused category
    result_unused = await income_category_repository.delete_if_unused(
        unused_category_id
    )

    # 4. ASSERT: Verify the operation results
    assert result_used is False  # Should not delete used category
    assert result_unused is True  # Should delete unused category

    # Verify used category still exists
    used_category = await income_category_repository.get(used_category_id)
    assert used_category is not None

    # Verify unused category was deleted
    unused_category = await income_category_repository.get(unused_category_id)
    assert unused_category is None


async def test_get_active_categories(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
    test_income_entries: List[Income],
):
    """Test getting income categories that have active associated income."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get active categories
    results = await income_category_repository.get_active_categories()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 active categories

    # Verify that each category is associated with at least one non-deposited income
    active_category_names = [category.name for category in results]
    assert "Freelance" in active_category_names  # Has non-deposited income
    assert "Investments" in active_category_names  # Has non-deposited income
    assert "Salary" not in active_category_names  # All income is deposited


async def test_get_categories_with_stats(
    income_category_repository: IncomeCategoryRepository,
    test_multiple_categories: List[IncomeCategory],
    test_income_entries: List[Income],
):
    """Test getting income categories with detailed statistics."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get categories with stats
    results = await income_category_repository.get_categories_with_stats()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get stats for all categories

    # Check structure of results
    for result in results:
        assert "category" in result
        assert "total_amount" in result
        assert "entry_count" in result
        assert "avg_amount" in result
        assert "pending_count" in result
        assert "pending_amount" in result

    # Find salary stats
    salary_stats = next((r for r in results if r["category"].name == "Salary"), None)
    assert salary_stats is not None
    assert salary_stats["total_amount"] == Decimal("4000.00")
    assert salary_stats["entry_count"] == 2
    assert salary_stats["avg_amount"] == Decimal("2000.00")
    assert salary_stats["pending_count"] == 0
    assert salary_stats["pending_amount"] == Decimal("0.00")

    # Find freelance stats
    freelance_stats = next(
        (r for r in results if r["category"].name == "Freelance"), None
    )
    assert freelance_stats is not None
    assert freelance_stats["total_amount"] == Decimal("1150.00")
    assert freelance_stats["entry_count"] == 2
    assert freelance_stats["avg_amount"] == Decimal("575.00")
    assert freelance_stats["pending_count"] == 1
    assert freelance_stats["pending_amount"] == Decimal("800.00")

    # Find investments stats
    investments_stats = next(
        (r for r in results if r["category"].name == "Investments"), None
    )
    assert investments_stats is not None
    assert investments_stats["total_amount"] == Decimal("420.00")
    assert investments_stats["entry_count"] == 1
    assert investments_stats["avg_amount"] == Decimal("420.00")
    assert investments_stats["pending_count"] == 1
    assert investments_stats["pending_amount"] == Decimal("420.00")


async def test_validation_error_handling():
    """Test handling invalid data that would normally be caught by schema validation."""
    # Try creating a schema with invalid data and expect it to fail validation
    try:
        invalid_schema = IncomeCategoryCreate(
            name="",  # Invalid empty name
            description="Test description",
        )
        assert False, "Schema should have raised a validation error for empty name"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "name" in str(e).lower()

    # Try with too long name
    try:
        invalid_schema = IncomeCategoryCreate(
            name="A" * 101,  # 101 characters, exceeding max length of 100
            description="Test description",
        )
        assert False, "Schema should have raised a validation error for long name"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "name" in str(e).lower() and "length" in str(e).lower()
