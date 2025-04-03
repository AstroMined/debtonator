"""
Tests for feature flag context utilities.

This module contains tests for the feature flag context utilities,
including environment detection, percentage rollout calculations,
and context building. All tests follow the Real Objects Testing Philosophy.
"""

import os
import platform

import pytest
from fastapi.testclient import TestClient

from src.api.dependencies.feature_flags import build_context_from_request
from src.utils.feature_flags.context import (
    Environment,
    EnvironmentContext,
    create_default_context,
    create_environment_context,
    detect_environment,
    generate_hash_id,
    is_feature_enabled_for_percentage,
)
from src.version import VERSION


def test_environment_enum():
    """Test the Environment enum values."""
    assert Environment.DEVELOPMENT == "development"
    assert Environment.STAGING == "staging"
    assert Environment.PRODUCTION == "production"
    assert Environment.TEST == "test"


def test_environment_context_model():
    """Test the EnvironmentContext model."""
    # Create a context with real data
    context = EnvironmentContext(
        environment=Environment.DEVELOPMENT,
        hostname="test-host",
        application_version="1.0.0",
        request_id="test-request-id",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        metadata={"key": "value"},
    )

    # Test fields
    assert context.environment == Environment.DEVELOPMENT
    assert context.hostname == "test-host"
    assert context.application_version == "1.0.0"
    assert context.request_id == "test-request-id"
    assert context.ip_address == "127.0.0.1"
    assert context.user_agent == "Test Agent"
    assert context.metadata == {"key": "value"}

    # Test properties
    assert context.is_development is True
    assert context.is_staging is False
    assert context.is_production is False
    assert context.is_test is False


def test_detect_environment_default(env_setup):
    """Test environment detection with default values."""
    # No environment variable set, should default to development
    os.environ.clear()  # Clear any existing env vars
    assert detect_environment() == Environment.DEVELOPMENT


def test_detect_environment_from_env_var(env_setup):
    """Test environment detection from environment variables."""
    # Test each environment type
    env_cases = [
        ("development", Environment.DEVELOPMENT),
        ("staging", Environment.STAGING),
        ("production", Environment.PRODUCTION),
        ("test", Environment.TEST),
        ("prod", Environment.PRODUCTION),  # Alias
        ("stage", Environment.STAGING),  # Alias
    ]

    for env_name, expected in env_cases:
        # Set real environment variable for testing
        os.environ["APP_ENV"] = env_name
        assert detect_environment() == expected


def test_detect_environment_pytest(env_setup):
    """Test environment detection in pytest environment."""
    # In a test environment like pytest, we should get TEST
    # We're already in pytest, so this should return TEST
    assert detect_environment() == Environment.TEST


def test_generate_hash_id():
    """Test hash ID generation."""
    # Test deterministic hash generation
    assert generate_hash_id("test") == generate_hash_id("test")

    # Test different inputs produce different hashes
    assert generate_hash_id("test1") != generate_hash_id("test2")

    # Test hash format (MD5 is 32 hexadecimal characters)
    assert len(generate_hash_id("test")) == 32
    assert all(c in "0123456789abcdef" for c in generate_hash_id("test"))


def test_percentage_rollout_edge_cases():
    """Test percentage rollout with edge cases."""
    # 0% should always be disabled
    assert is_feature_enabled_for_percentage(0, "test") is False

    # 100% should always be enabled
    assert is_feature_enabled_for_percentage(100, "test") is True

    # Negative percentage should be disabled
    assert is_feature_enabled_for_percentage(-10, "test") is False

    # Percentage > 100 should be enabled
    assert is_feature_enabled_for_percentage(110, "test") is True


def test_percentage_rollout_consistency():
    """Test percentage rollout consistency for the same identifier."""
    # Same identifier should give consistent results
    identifier = "test-identifier"
    result = is_feature_enabled_for_percentage(50, identifier)

    # Test multiple times to ensure consistency
    for _ in range(10):
        assert is_feature_enabled_for_percentage(50, identifier) is result


def test_percentage_rollout_distribution():
    """Test percentage rollout distribution across identifiers."""
    # Generate a large number of unique identifiers
    identifiers = [f"test-{i}" for i in range(1000)]

    # Calculate the percentage of enabled flags for different percentages
    test_percentages = [0, 25, 50, 75, 100]
    results = {}

    for percentage in test_percentages:
        # Count how many identifiers are enabled at this percentage
        enabled_count = sum(
            1 for i in identifiers if is_feature_enabled_for_percentage(percentage, i)
        )

        # Store the percentage enabled
        results[percentage] = (enabled_count / len(identifiers)) * 100

    # Verify distribution is close to expected
    # Allow for some statistical variance - standard deviation should be reasonable
    assert abs(results[0] - 0) < 1  # Should be very close to 0%
    assert abs(results[25] - 25) < 5  # Should be within ~5% of 25%
    assert abs(results[50] - 50) < 5  # Should be within ~5% of 50%
    assert abs(results[75] - 75) < 5  # Should be within ~5% of 75%
    assert abs(results[100] - 100) < 1  # Should be very close to 100%


def test_create_environment_context():
    """Test environment context creation."""
    # Test with minimal parameters
    context = create_environment_context()
    assert context.environment == detect_environment()
    assert context.hostname == platform.node()
    assert context.application_version == VERSION
    assert context.request_id is None
    assert context.ip_address is None
    assert context.user_agent is None
    assert context.metadata == {}

    # Test with all parameters
    context = create_environment_context(
        request_id="test-request-id",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        metadata={"key": "value"},
        application_version="1.0.0",
    )
    assert context.environment == detect_environment()
    assert context.hostname == platform.node()
    assert context.application_version == "1.0.0"
    assert context.request_id == "test-request-id"
    assert context.ip_address == "127.0.0.1"
    assert context.user_agent == "Test Agent"
    assert context.metadata == {"key": "value"}


def test_create_default_context():
    """Test default context creation."""
    context = create_default_context()
    assert context.environment == detect_environment()
    assert context.hostname == platform.node()
    assert context.application_version == VERSION
    assert context.request_id is None
    assert context.ip_address is None
    assert context.user_agent is None
    assert context.metadata == {}


@pytest.mark.asyncio
async def test_build_context_from_request():
    """Test building context from a real HTTP request."""
    # We need to import inside the test to avoid circular imports

    # Create a test app for this specific test
    from fastapi import FastAPI, Request

    test_app = FastAPI()

    @test_app.get("/test-endpoint-for-context")
    async def test_endpoint(request: Request):
        # Build context from the real request
        context = build_context_from_request(request)
        return {
            "environment": context.environment,
            "request_id": context.request_id,
            "ip_address": context.ip_address,
            "user_agent": context.user_agent,
        }

    # Use a test client with our isolated test_app
    client = TestClient(test_app)

    # Make request to this endpoint with custom headers
    response = client.get(
        "/test-endpoint-for-context",
        headers={"X-Request-ID": "test-id", "User-Agent": "Test Client"},
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "test-id"
    assert data["user_agent"] == "Test Client"
    assert data["environment"] in [e.value for e in Environment]

    # No cleanup needed as test_app is isolated to this test
