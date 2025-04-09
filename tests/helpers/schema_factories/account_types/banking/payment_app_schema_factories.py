"""
Payment app account schema factory functions.

This module provides factory functions for creating valid PaymentAppAccount-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.account_types.banking.payment_app import (
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    COMMON_AMOUNTS,
    factory_function,
)


@factory_function(PaymentAppAccountCreate)
def create_payment_app_account_schema(
    name: str = "Test Payment App",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "PayPal",
    platform: str = "PayPal",
    has_debit_card: bool = False,
    card_last_four: Optional[str] = None,
    linked_account_ids: Optional[str] = None,
    supports_direct_deposit: bool = True,
    supports_crypto: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentAppAccountCreate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance (defaults to 250.00)
        available_balance: Available balance (defaults to same as current_balance)
        institution: Financial institution name (defaults to match platform)
        platform: Payment platform (PayPal, Venmo, Cash App, etc.)
        has_debit_card: Whether account has an associated debit card
        card_last_four: Last four digits of associated card (required if has_debit_card is True)
        linked_account_ids: Comma-separated list of linked account IDs
        supports_direct_deposit: Whether account supports direct deposit
        supports_crypto: Whether account supports cryptocurrency
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentAppAccountCreate schema
    """
    if current_balance is None:
        current_balance = COMMON_AMOUNTS["medium"] * Decimal("2.5")  # 250.00

    if available_balance is None:
        available_balance = current_balance

    data = {
        "name": name,
        "account_type": "payment_app",  # This is a literal in the schema
        "current_balance": current_balance,
        "available_balance": available_balance,
        "institution": institution,
        "platform": platform,
        "has_debit_card": has_debit_card,
        "supports_direct_deposit": supports_direct_deposit,
        "supports_crypto": supports_crypto,
    }

    # Handle card_last_four logic - this is required if has_debit_card is True
    if has_debit_card:
        if card_last_four is not None:
            data["card_last_four"] = card_last_four
        else:
            data["card_last_four"] = "1234"  # Default last four digits
    elif card_last_four is not None:
        # This will cause validation to fail, but we'll include it to test validation
        data["card_last_four"] = card_last_four

    # Add linked account IDs if provided
    if linked_account_ids is not None:
        data["linked_account_ids"] = linked_account_ids

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(PaymentAppAccountResponse)
def create_payment_app_account_response_schema(
    id: int = 1,
    name: str = "Test Payment App",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "PayPal",
    platform: str = "PayPal",
    has_debit_card: bool = False,
    card_last_four: Optional[str] = None,
    linked_account_ids: Optional[str] = None,
    supports_direct_deposit: bool = True,
    supports_crypto: bool = False,
    created_at: Optional[Any] = None,
    updated_at: Optional[Any] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentAppAccountResponse schema instance.

    Args:
        id: Account ID
        name: Account name
        current_balance: Current account balance (defaults to 250.00)
        available_balance: Available balance (defaults to same as current_balance)
        institution: Financial institution name (defaults to match platform)
        platform: Payment platform (PayPal, Venmo, Cash App, etc.)
        has_debit_card: Whether account has an associated debit card
        card_last_four: Last four digits of associated card (required if has_debit_card is True)
        linked_account_ids: Comma-separated list of linked account IDs
        supports_direct_deposit: Whether account supports direct deposit
        supports_crypto: Whether account supports cryptocurrency
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentAppAccountResponse schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    # Use the create schema factory to generate the base data
    base_data = create_payment_app_account_schema(
        name=name,
        current_balance=current_balance,
        available_balance=available_balance,
        institution=institution,
        platform=platform,
        has_debit_card=has_debit_card,
        card_last_four=card_last_four,
        linked_account_ids=linked_account_ids,
        supports_direct_deposit=supports_direct_deposit,
        supports_crypto=supports_crypto,
    )

    # Convert the Pydantic model to a dictionary
    base_dict = base_data.model_dump()

    # Add response-specific fields
    response_data = {
        "id": id,
        "created_at": created_at,
        "updated_at": updated_at,
        **base_dict,
    }

    # Add any additional fields from kwargs
    response_data.update(kwargs)

    return response_data
