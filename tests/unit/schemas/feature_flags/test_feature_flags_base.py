"""
Tests for base feature flag schemas and enums.

This module contains tests for the FeatureFlagType enum and FeatureFlagBase schema,
which are the foundation for all other feature flag schemas.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import FeatureFlagBase, FeatureFlagType


def test_valid_flag_types():
    """Test that all flag types can be accessed."""
    assert FeatureFlagType.BOOLEAN == "boolean"
    assert FeatureFlagType.PERCENTAGE == "percentage"
    assert FeatureFlagType.USER_SEGMENT == "user_segment"
    assert FeatureFlagType.TIME_BASED == "time_based"
    assert FeatureFlagType.ENVIRONMENT == "environment"


def test_enum_from_string():
    """Test that string values can be converted to enum values."""
    assert FeatureFlagType("boolean") == FeatureFlagType.BOOLEAN
    assert FeatureFlagType("percentage") == FeatureFlagType.PERCENTAGE
    assert FeatureFlagType("user_segment") == FeatureFlagType.USER_SEGMENT
    assert FeatureFlagType("time_based") == FeatureFlagType.TIME_BASED
    assert FeatureFlagType("environment") == FeatureFlagType.ENVIRONMENT


def test_invalid_flag_type():
    """Test that invalid flag types raise a ValueError."""
    with pytest.raises(ValueError):
        FeatureFlagType("invalid_type")


def test_valid_feature_flag_base():
    """Test that valid data passes validation."""
    flag = FeatureFlagBase(
        name="TEST_FLAG",
        description="Test flag description",
    )
    assert flag.name == "TEST_FLAG"
    assert flag.description == "Test flag description"


def test_optional_description():
    """Test that description is optional."""
    flag = FeatureFlagBase(name="TEST_FLAG")
    assert flag.name == "TEST_FLAG"
    assert flag.description is None


def test_feature_flag_base_name_validation_edge_cases():
    """Test edge cases for feature flag name validation."""
    # Valid name with numbers
    flag = FeatureFlagBase(name="TEST_FLAG_123")
    assert flag.name == "TEST_FLAG_123"

    # Valid name with underscores
    flag = FeatureFlagBase(name="TEST_FLAG_WITH_UNDERSCORES")
    assert flag.name == "TEST_FLAG_WITH_UNDERSCORES"

    # Invalid name starting with number
    with pytest.raises(
        ValidationError, match="Feature flag name must start with an uppercase letter"
    ):
        FeatureFlagBase(name="1TEST_FLAG")

    # Invalid name with lowercase letters
    with pytest.raises(
        ValidationError, match="Feature flag name must contain only uppercase letters"
    ):
        FeatureFlagBase(name="TEST_flag")

    # Invalid name with special characters
    with pytest.raises(
        ValidationError, match="Feature flag name must contain only uppercase letters"
    ):
        FeatureFlagBase(name="TEST-FLAG")

    # Invalid name with spaces
    with pytest.raises(
        ValidationError, match="Feature flag name must contain only uppercase letters"
    ):
        FeatureFlagBase(name="TEST FLAG")


def test_name_format_validation():
    """Test that flag names must be in uppercase with underscores."""
    # Valid name
    flag = FeatureFlagBase(name="TEST_FLAG_123")
    assert flag.name == "TEST_FLAG_123"

    # Invalid name - lowercase
    with pytest.raises(ValidationError) as exc:
        FeatureFlagBase(name="test_flag")
    assert "Feature flag name must start with an uppercase letter" in str(exc.value)

    # Invalid name - special characters
    with pytest.raises(ValidationError) as exc:
        FeatureFlagBase(name="TEST-FLAG")
    assert (
        "Feature flag name must contain only uppercase letters, numbers, and underscores"
        in str(exc.value)
    )

    # Invalid name - starting with number
    with pytest.raises(ValidationError) as exc:
        FeatureFlagBase(name="1TEST_FLAG")
    assert "Feature flag name must start with an uppercase letter" in str(exc.value)
