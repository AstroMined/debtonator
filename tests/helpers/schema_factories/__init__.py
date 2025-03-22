"""
Schema factory functions for tests.

This module provides domain-organized factory functions that generate valid 
Pydantic schema instances for use in tests.

IMPORTANT: This module no longer re-exports factory functions for backward compatibility.
All imports should be made directly from the specific domain modules.

Example:
    from tests.helpers.schema_factories.accounts import create_account_schema
    from tests.helpers.schema_factories.payments import create_payment_schema
"""

# No exports - all imports must be explicit from domain modules
