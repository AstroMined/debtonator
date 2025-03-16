import pytest
from pydantic import ValidationError

from src.schemas.income_categories import (
    IncomeCategoryBase,
    IncomeCategoryCreate,
    IncomeCategoryUpdate,
    IncomeCategory,
)


# Test valid object creation
def test_income_category_base_valid():
    """Test valid income category base schema creation"""
    # With required fields only
    data1 = IncomeCategoryBase(name="Salary")
    assert data1.name == "Salary"
    assert data1.description is None

    # With all fields
    data2 = IncomeCategoryBase(
        name="Freelance Income",
        description="Income from freelance projects and consulting work"
    )
    assert data2.name == "Freelance Income"
    assert data2.description == "Income from freelance projects and consulting work"


def test_income_category_create_valid():
    """Test valid income category create schema creation"""
    # With required fields only
    data1 = IncomeCategoryCreate(name="Salary")
    assert data1.name == "Salary"
    assert data1.description is None

    # With all fields
    data2 = IncomeCategoryCreate(
        name="Freelance Income",
        description="Income from freelance projects and consulting work"
    )
    assert data2.name == "Freelance Income"
    assert data2.description == "Income from freelance projects and consulting work"


def test_income_category_update_valid():
    """Test valid income category update schema creation"""
    # With no fields (all are optional for update)
    data1 = IncomeCategoryUpdate()
    assert data1.name is None
    assert data1.description is None

    # With name only
    data2 = IncomeCategoryUpdate(name="Updated Salary")
    assert data2.name == "Updated Salary"
    assert data2.description is None

    # With description only
    data3 = IncomeCategoryUpdate(description="Updated description for income")
    assert data3.name is None
    assert data3.description == "Updated description for income"

    # With all fields
    data4 = IncomeCategoryUpdate(
        name="Updated Freelance Income",
        description="Updated description for freelance work"
    )
    assert data4.name == "Updated Freelance Income"
    assert data4.description == "Updated description for freelance work"


def test_income_category_valid():
    """Test valid income category schema creation"""
    # With required fields only
    data1 = IncomeCategory(
        id=1,
        name="Salary"
    )
    assert data1.id == 1
    assert data1.name == "Salary"
    assert data1.description is None

    # With all fields
    data2 = IncomeCategory(
        id=2,
        name="Freelance Income",
        description="Income from freelance projects and consulting work"
    )
    assert data2.id == 2
    assert data2.name == "Freelance Income"
    assert data2.description == "Income from freelance projects and consulting work"


# Test field validations
def test_string_length_validation():
    """Test string length validation"""
    # Test empty name in base schema
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        IncomeCategoryBase(name="")

    # Test name too long in base schema
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        IncomeCategoryBase(name="X" * 101)

    # Test description too long in base schema
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        IncomeCategoryBase(
            name="Valid Name",
            description="X" * 501
        )

    # Test empty name in create schema
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        IncomeCategoryCreate(name="")

    # Test name too long in create schema
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        IncomeCategoryCreate(name="X" * 101)

    # Test description too long in create schema
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        IncomeCategoryCreate(
            name="Valid Name",
            description="X" * 501
        )

    # Test empty name in update schema (when provided)
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        IncomeCategoryUpdate(name="")

    # Test name too long in update schema
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        IncomeCategoryUpdate(name="X" * 101)

    # Test description too long in update schema
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        IncomeCategoryUpdate(description="X" * 501)

    # Test empty name in full schema
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        IncomeCategory(id=1, name="")

    # Test name too long in full schema
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        IncomeCategory(id=1, name="X" * 101)

    # Test description too long in full schema
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        IncomeCategory(
            id=1,
            name="Valid Name",
            description="X" * 501
        )


def test_required_fields():
    """Test required fields validation"""
    # Test missing name in base schema
    with pytest.raises(ValidationError, match="Field required"):
        IncomeCategoryBase()

    # Test missing name in create schema
    with pytest.raises(ValidationError, match="Field required"):
        IncomeCategoryCreate()

    # Test missing id in full schema
    with pytest.raises(ValidationError, match="Field required"):
        IncomeCategory(name="Salary")

    # Test missing name in full schema
    with pytest.raises(ValidationError, match="Field required"):
        IncomeCategory(id=1)
