"""
Environment-related fixtures for testing.

This module provides fixtures for testing environment-related functionality,
such as environment detection and context building.
"""

import os
import sys
from typing import Dict, Generator

import pytest


@pytest.fixture
def env_setup() -> Generator[Dict[str, str], None, None]:
    """
    Set up and tear down environment variables for testing.

    This fixture saves the original environment variables, allows tests to modify
    the environment, and restores the original environment after the test completes.

    Yields:
        Dict[str, str]: A dictionary of the original environment variables
    """
    # Save original environment
    original_env = os.environ.copy()

    # Save original sys.modules state for pytest detection
    original_modules = sys.modules.copy()

    try:
        # Clear environment variables that might affect tests
        os.environ.clear()

        # Yield the original environment for reference
        yield original_env
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)
