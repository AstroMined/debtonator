"""
Buy Now Pay Later (BNPL) account schema factory functions.

This module provides factory functions for creating valid BNPLAccount-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.account_types.banking.bnpl import (
    BNPLAccountCreate,
    BNPLAccountResponse,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    COMMON_AMOUNTS,
    factory_function,
)


@factory_function(BNPLAccountCreate)
def create_bnpl_account_schema(
    name: str = "Test BNPL Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Affirm",
    original_amount: Optional[Decimal] = None,
    installment_count: int = 4,
    installments_paid: int = 0,
    installment_amount: Optional[Decimal] = None,
    payment_frequency: str = "biweekly",
    next_payment_date: Optional[datetime] = None,
    promotion_info: Optional[str] = None,
    late_fee: Optional[Decimal] = None,
    bnpl_provider: str = "Affirm",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BNPLAccountCreate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance (defaults based on installments remaining)
        available_balance: Available balance (defaults to 0 for BNPL accounts)
        institution: Financial institution name
        original_amount: Original purchase amount (defaults to 400.00)
        installment_count: Total number of installments (defaults to 4)
        installments_paid: Number of installments already paid (defaults to 0)
        installment_amount: Amount per installment (defaults to original_amount / installment_count)
        payment_frequency: Payment frequency (weekly, biweekly, monthly)
        next_payment_date: Date of next payment due (defaults to 14 days from now for biweekly)
        promotion_info: Promotional details (e.g., '0% interest for 6 months')
        late_fee: Late payment fee amount
        bnpl_provider: BNPL service provider (Affirm, Klarna, Afterpay, etc.)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BNPLAccountCreate schema
    """
    # Set defaults for required fields
    if original_amount is None:
        original_amount = COMMON_AMOUNTS["medium"] * Decimal("4")  # 400.00

    # Calculate installment amount if not provided
    if installment_amount is None:
        installment_amount = original_amount / installment_count

    # Calculate current balance based on installments remaining
    if current_balance is None:
        remaining_installments = installment_count - installments_paid
        current_balance = installment_amount * remaining_installments

    # For BNPL accounts, available balance is typically 0 as it's a loan, not a line of credit
    if available_balance is None:
        available_balance = Decimal("0")

    # Calculate next payment date based on frequency if not provided
    now = utc_now()
    if next_payment_date is None:
        if payment_frequency == "weekly":
            next_payment_date = now + timedelta(days=7)
        elif payment_frequency == "biweekly":
            next_payment_date = now + timedelta(days=14)
        elif payment_frequency == "monthly":
            # Add roughly a month - this is a simplification
            next_payment_date = now + timedelta(days=30)
        else:
            next_payment_date = now + timedelta(days=14)  # Default to biweekly

    data = {
        "name": name,
        "account_type": "bnpl",  # This is a literal in the schema
        "current_balance": current_balance,
        "available_balance": available_balance,
        "institution": institution,
        "original_amount": original_amount,
        "installment_count": installment_count,
        "installments_paid": installments_paid,
        "installment_amount": installment_amount,
        "payment_frequency": payment_frequency,
        "next_payment_date": next_payment_date,
        "bnpl_provider": bnpl_provider,
    }

    # Add optional fields if provided
    if promotion_info is not None:
        data["promotion_info"] = promotion_info

    if late_fee is not None:
        data["late_fee"] = late_fee

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(BNPLAccountResponse)
def create_bnpl_account_response_schema(
    id: int = 1,
    name: str = "Test BNPL Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Affirm",
    original_amount: Optional[Decimal] = None,
    installment_count: int = 4,
    installments_paid: int = 0,
    installment_amount: Optional[Decimal] = None,
    payment_frequency: str = "biweekly",
    next_payment_date: Optional[datetime] = None,
    promotion_info: Optional[str] = None,
    late_fee: Optional[Decimal] = None,
    bnpl_provider: str = "Affirm",
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BNPLAccountResponse schema instance.

    Args:
        id: Account ID
        name: Account name
        current_balance: Current account balance (defaults based on installments remaining)
        available_balance: Available balance (defaults to 0 for BNPL accounts)
        institution: Financial institution name
        original_amount: Original purchase amount (defaults to 400.00)
        installment_count: Total number of installments (defaults to 4)
        installments_paid: Number of installments already paid (defaults to 0)
        installment_amount: Amount per installment (defaults to original_amount / installment_count)
        payment_frequency: Payment frequency (weekly, biweekly, monthly)
        next_payment_date: Date of next payment due (defaults to 14 days from now for biweekly)
        promotion_info: Promotional details (e.g., '0% interest for 6 months')
        late_fee: Late payment fee amount
        bnpl_provider: BNPL service provider (Affirm, Klarna, Afterpay, etc.)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BNPLAccountResponse schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    # Use the create schema factory to generate the base data
    base_data = create_bnpl_account_schema(
        name=name,
        current_balance=current_balance,
        available_balance=available_balance,
        institution=institution,
        original_amount=original_amount,
        installment_count=installment_count,
        installments_paid=installments_paid,
        installment_amount=installment_amount,
        payment_frequency=payment_frequency,
        next_payment_date=next_payment_date,
        promotion_info=promotion_info,
        late_fee=late_fee,
        bnpl_provider=bnpl_provider,
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
