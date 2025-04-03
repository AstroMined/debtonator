"""
Unit tests for the FeatureFlag model.

Tests the FeatureFlag model fields, constraints, and behavior
as part of ADR-024 Feature Flags.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag

pytestmark = pytest.mark.asyncio


async def test_create_boolean_feature_flag(db_session: AsyncSession):
    """Test creating a simple boolean feature flag."""
    flag = FeatureFlag(
        name="enable_dark_mode",
        description="Enable dark mode UI",
        flag_type="boolean",
        value=True,
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "enable_dark_mode"
    assert flag.description == "Enable dark mode UI"
    assert flag.flag_type == "boolean"
    assert flag.value is True
    assert flag.is_system is False


async def test_create_percentage_feature_flag(db_session: AsyncSession):
    """Test creating a percentage rollout feature flag."""
    flag = FeatureFlag(
        name="new_dashboard_rollout",
        description="Percentage of users who see the new dashboard",
        flag_type="percentage",
        value=25.5,  # 25.5% of users
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "new_dashboard_rollout"
    assert flag.flag_type == "percentage"
    assert flag.value == 25.5


async def test_create_user_segment_feature_flag(db_session: AsyncSession):
    """Test creating a user segment feature flag."""
    user_segments = ["premium", "beta_testers"]
    flag = FeatureFlag(
        name="advanced_reporting",
        description="Enable advanced reporting for specific user segments",
        flag_type="user_segment",
        value=user_segments,
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "advanced_reporting"
    assert flag.flag_type == "user_segment"
    assert flag.value == user_segments


async def test_create_time_based_feature_flag(db_session: AsyncSession):
    """Test creating a time-based feature flag."""
    time_config = {
        "start": "2025-04-01T00:00:00Z",
        "end": "2025-04-30T23:59:59Z",
        "days_of_week": [1, 2, 3, 4, 5],  # Weekdays only
        "hours": {"start": 9, "end": 17},  # Business hours
    }
    flag = FeatureFlag(
        name="seasonal_promotion",
        description="April promotion - only active during business hours",
        flag_type="time_based",
        value=time_config,
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "seasonal_promotion"
    assert flag.flag_type == "time_based"
    assert flag.value["start"] == time_config["start"]
    assert flag.value["end"] == time_config["end"]
    assert flag.value["days_of_week"] == time_config["days_of_week"]
    assert flag.value["hours"] == time_config["hours"]


async def test_create_complex_feature_flag(db_session: AsyncSession):
    """Test creating a complex feature flag with nested JSON configuration."""
    complex_config = {
        "version": "1.0",
        "account_types": ["checking", "savings"],
        "minimum_balance": str(
            Decimal("1000.00")
        ),  # Convert Decimal to string for JSON
        "regions": ["US", "CA", "EU"],
        "thresholds": {
            "transaction_limit": 10000,
            "notification_trigger": 8000,
            "warning_level": "high",
        },
    }
    flag = FeatureFlag(
        name="high_value_account_features",
        description="Features for high-value accounts",
        flag_type="complex",
        value=complex_config,
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "high_value_account_features"
    assert flag.flag_type == "complex"
    assert flag.value["account_types"] == complex_config["account_types"]
    assert flag.value["minimum_balance"] == complex_config["minimum_balance"]
    assert (
        flag.value["thresholds"]["transaction_limit"]
        == complex_config["thresholds"]["transaction_limit"]
    )


async def test_update_feature_flag_value(db_session: AsyncSession):
    """Test updating a feature flag's value."""
    # Start with 25% rollout
    flag = FeatureFlag(
        name="feature_rollout",
        description="Percentage rollout of a feature",
        flag_type="percentage",
        value=25.0,
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.value == 25.0

    # Update to 50% rollout
    flag.value = 50.0
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.value == 50.0


async def test_system_flag_creation(db_session: AsyncSession):
    """Test creating a system flag."""
    flag = FeatureFlag(
        name="system_maintenance_mode",
        description="Enable system maintenance mode",
        flag_type="boolean",
        value=False,
        is_system=True,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "system_maintenance_mode"
    assert flag.is_system is True


async def test_flag_metadata(db_session: AsyncSession):
    """Test setting and retrieving flag metadata."""
    metadata = {
        "owner": "billing_team",
        "created_by": "user123",
        "documentation_url": "https://docs.example.com/features/new_billing",
        "risk_level": "medium",
    }

    flag = FeatureFlag(
        name="new_billing_system",
        description="New billing system integration",
        flag_type="boolean",
        value=False,
        flag_metadata=metadata,
        is_system=False,
    )
    db_session.add(flag)
    await db_session.commit()
    await db_session.refresh(flag)

    assert flag.name == "new_billing_system"
    assert flag.flag_metadata == metadata
    assert flag.flag_metadata["owner"] == "billing_team"
    assert flag.flag_metadata["risk_level"] == "medium"
