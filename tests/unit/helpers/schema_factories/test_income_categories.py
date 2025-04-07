"""
Unit tests for income category schema factory functions.

Tests ensure that income category schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

import pytest

from src.schemas.income_categories import IncomeCategoryCreate
from tests.helpers.schema_factories.income_categories import create_income_category_schema


def test_create_income_category_schema():
    """Test creating an IncomeCategoryCreate schema with default values."""
    schema = create_income_category_schema()
    
    assert isinstance(schema, IncomeCategoryCreate)
    assert schema.name == "Test Income Category"
    assert schema.description is None


def test_create_income_category_schema_with_custom_values():
    """Test creating an IncomeCategoryCreate schema with custom values."""
    schema = create_income_category_schema(
        name="Salary",
        description="Monthly salary income"
    )
    
    assert isinstance(schema, IncomeCategoryCreate)
    assert schema.name == "Salary"
    assert schema.description == "Monthly salary income"


def test_create_income_category_schema_with_minimum_name_length():
    """Test creating an IncomeCategoryCreate schema with minimum name length."""
    schema = create_income_category_schema(name="A")  # Minimum one character
    
    assert isinstance(schema, IncomeCategoryCreate)
    assert schema.name == "A"
    assert schema.description is None


def test_create_income_category_schema_with_maximum_name_length():
    """Test creating an IncomeCategoryCreate schema with maximum name length."""
    # Using a name with 100 characters (maximum allowed)
    long_name = "A" * 100
    schema = create_income_category_schema(name=long_name)
    
    assert isinstance(schema, IncomeCategoryCreate)
    assert schema.name == long_name
    assert len(schema.name) == 100


def test_create_income_category_schema_with_long_description():
    """Test creating an IncomeCategoryCreate schema with a long description."""
    # Using a description with 500 characters (maximum allowed)
    long_description = "D" * 500
    schema = create_income_category_schema(description=long_description)
    
    assert isinstance(schema, IncomeCategoryCreate)
    assert schema.name == "Test Income Category"
    assert schema.description == long_description
    assert len(schema.description) == 500


def test_create_income_category_schema_with_additional_fields():
    """Test creating an IncomeCategoryCreate schema with additional fields."""
    schema = create_income_category_schema(
        name="Side Gig",
        custom_field="This should be ignored by the schema"
    )
    
    assert isinstance(schema, IncomeCategoryCreate)
    assert schema.name == "Side Gig"
    assert schema.description is None
    # The custom_field should not be part of the schema
    with pytest.raises(AttributeError):
        _ = schema.custom_field
