"""
Tests for feature flag history and metrics schemas.

This module contains tests for the schemas used to track feature flag history and metrics,
including FlagHistoryEntry, FlagHistoryResponse, and FlagMetricsResponse.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import (
    FlagHistoryEntry,
    FlagHistoryResponse,
    FlagMetricsResponse,
)
from src.utils.datetime_utils import utc_now


# FlagHistoryEntry tests
def test_flag_history_entry_schema():
    """Test the flag history entry schema."""
    now = utc_now()
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="update",
        old_value=False,
        new_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.timestamp == now
    assert entry.change_type == "update"
    assert entry.old_value is False
    assert entry.new_value is True


def test_flag_history_entry_create():
    """Test a history entry for flag creation."""
    now = utc_now()
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="create",
        new_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.timestamp == now
    assert entry.change_type == "create"
    assert entry.old_value is None
    assert entry.new_value is True


def test_flag_history_entry_delete():
    """Test a history entry for flag deletion."""
    now = utc_now()
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="delete",
        old_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.timestamp == now
    assert entry.change_type == "delete"
    assert entry.old_value is True
    assert entry.new_value is None


def test_flag_history_entry_with_complex_values():
    """Test flag history entries with complex values."""
    now = utc_now()

    # Test with boolean value
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="update",
        old_value=False,
        new_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.change_type == "update"
    assert entry.old_value is False
    assert entry.new_value is True

    # Test with percentage value
    entry = FlagHistoryEntry(
        flag_name="PERCENTAGE_FLAG",
        timestamp=now,
        change_type="update",
        old_value=25,
        new_value=50,
    )
    assert entry.old_value == 25
    assert entry.new_value == 50

    # Test with user segment value
    entry = FlagHistoryEntry(
        flag_name="USER_SEGMENT_FLAG",
        timestamp=now,
        change_type="update",
        old_value=["admin"],
        new_value=["admin", "beta"],
    )
    assert entry.old_value == ["admin"]
    assert entry.new_value == ["admin", "beta"]

    # Test with environment value
    entry = FlagHistoryEntry(
        flag_name="ENV_FLAG",
        timestamp=now,
        change_type="update",
        old_value={"environments": ["dev"], "default": False},
        new_value={"environments": ["dev", "staging"], "default": True},
    )
    assert entry.old_value["environments"] == ["dev"]
    assert entry.new_value["environments"] == ["dev", "staging"]
    assert entry.old_value["default"] is False
    assert entry.new_value["default"] is True


# FlagHistoryResponse tests
def test_flag_history_response_schema():
    """Test the flag history response schema."""
    now = utc_now()
    entry1 = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="create",
        new_value=False,
    )
    entry2 = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="update",
        old_value=False,
        new_value=True,
    )

    response = FlagHistoryResponse(
        flag_name="TEST_FLAG",
        history=[entry1, entry2],
    )
    assert response.flag_name == "TEST_FLAG"
    assert len(response.history) == 2
    assert response.history[0].change_type == "create"
    assert response.history[1].change_type == "update"


def test_flag_history_response_edge_cases():
    """Test edge cases for flag history response."""
    now = utc_now()

    # Test with empty history list
    history = FlagHistoryResponse(
        flag_name="TEST_FLAG",
        history=[],
    )
    assert history.flag_name == "TEST_FLAG"
    assert history.history == []

    # Test with single history entry
    history = FlagHistoryResponse(
        flag_name="TEST_FLAG",
        history=[
            FlagHistoryEntry(
                flag_name="TEST_FLAG",
                timestamp=now,
                change_type="create",
                new_value=True,
            )
        ],
    )
    assert history.flag_name == "TEST_FLAG"
    assert len(history.history) == 1
    assert history.history[0].flag_name == "TEST_FLAG"
    assert history.history[0].change_type == "create"
    assert history.history[0].new_value is True

    # Test with multiple history entries
    history = FlagHistoryResponse(
        flag_name="TEST_FLAG",
        history=[
            FlagHistoryEntry(
                flag_name="TEST_FLAG",
                timestamp=now,
                change_type="update",
                old_value=False,
                new_value=True,
            ),
            FlagHistoryEntry(
                flag_name="TEST_FLAG",
                timestamp=now.replace(hour=now.hour - 1),
                change_type="create",
                new_value=False,
            ),
        ],
    )
    assert history.flag_name == "TEST_FLAG"
    assert len(history.history) == 2
    assert history.history[0].change_type == "update"
    assert history.history[1].change_type == "create"

    # Test with different flag names in history entries
    # This is technically valid but might indicate a bug in the application
    history = FlagHistoryResponse(
        flag_name="TEST_FLAG",
        history=[
            FlagHistoryEntry(
                flag_name="TEST_FLAG",
                timestamp=now,
                change_type="update",
                old_value=False,
                new_value=True,
            ),
            FlagHistoryEntry(
                flag_name="DIFFERENT_FLAG",  # Different flag name
                timestamp=now.replace(hour=now.hour - 1),
                change_type="create",
                new_value=False,
            ),
        ],
    )
    assert history.flag_name == "TEST_FLAG"
    assert len(history.history) == 2
    assert history.history[0].flag_name == "TEST_FLAG"
    assert history.history[1].flag_name == "DIFFERENT_FLAG"  # Different from parent


# FlagMetricsResponse tests
def test_flag_metrics_response_schema():
    """Test the flag metrics response schema."""
    now = utc_now()
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=2500,
        layers={
            "repository": 1250,
            "service": 980,
            "api": 270,
        },
        last_checked=now,
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 2500
    assert metrics.layers["repository"] == 1250
    assert metrics.layers["service"] == 980
    assert metrics.layers["api"] == 270
    assert metrics.last_checked == now


def test_flag_metrics_without_last_checked():
    """Test flag metrics response without last_checked."""
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=0,
        layers={
            "repository": 0,
            "service": 0,
            "api": 0,
        },
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 0
    assert metrics.last_checked is None


def test_flag_metrics_with_missing_layer():
    """Test flag metrics response with a missing layer."""
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=1000,
        layers={
            "repository": 500,
            "api": 500,
            # 'service' layer is missing
        },
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 1000
    assert "repository" in metrics.layers
    assert "api" in metrics.layers
    assert "service" not in metrics.layers


def test_flag_metrics_response_with_partial_data():
    """Test flag metrics response with partial data."""
    # Test with minimal data
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=0,
        layers={},
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 0
    assert metrics.layers == {}
    assert metrics.last_checked is None

    # Test with partial layer data
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=500,
        layers={
            "repository": 500,
            # Missing service and api layers
        },
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 500
    assert metrics.layers["repository"] == 500
    assert "service" not in metrics.layers
    assert "api" not in metrics.layers

    # Test with all layers but zero counts
    metrics = FlagMetricsResponse(
        flag_name="UNUSED_FLAG",
        check_count=0,
        layers={
            "repository": 0,
            "service": 0,
            "api": 0,
        },
    )
    assert metrics.flag_name == "UNUSED_FLAG"
    assert metrics.check_count == 0
    assert metrics.layers["repository"] == 0
    assert metrics.layers["service"] == 0
    assert metrics.layers["api"] == 0
