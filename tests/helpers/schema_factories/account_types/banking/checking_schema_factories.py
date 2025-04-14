"""
Checking account schema factory functions.

This module provides factory functions for creating valid CheckingAccount-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.account_types.banking.checking import (
    CheckingAccountCreate,
    CheckingAccountResponse,
    CheckingAccountUpdate,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    COMMON_AMOUNTS,
    factory_function,
)


@factory_function(CheckingAccountCreate)
def create_checking_account_schema(
    name: str = "Test Checking Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Test Bank",
    routing_number: Optional[str] = None,
    has_overdraft_protection: bool = False,
    overdraft_limit: Optional[Decimal] = None,
    monthly_fee: Optional[Decimal] = None,
    interest_rate: Optional[Decimal] = None,
    # International banking fields
    iban: Optional[str] = None,
    swift_bic: Optional[str] = None,
    sort_code: Optional[str] = None,
    branch_code: Optional[str] = None,
    account_format: str = "local",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CheckingAccountCreate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance (defaults to 1000.00)
        available_balance: Available balance (defaults to same as current_balance)
        institution: Bank or financial institution name
        routing_number: Account routing number (defaults to "123456789")
        has_overdraft_protection: Whether overdraft protection is enabled
        overdraft_limit: Overdraft limit (required if has_overdraft_protection is True)
        monthly_fee: Monthly account maintenance fee
        interest_rate: Annual interest rate (if interest-bearing)
        iban: International Bank Account Number
        swift_bic: SWIFT/BIC code for international transfers
        sort_code: Sort code (used in UK and other countries)
        branch_code: Branch code (used in various countries)
        account_format: Account number format (local, iban, etc.)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CheckingAccountCreate schema
    """
    if current_balance is None:
        current_balance = COMMON_AMOUNTS["large"]  # 1000.00

    if available_balance is None:
        available_balance = current_balance

    if routing_number is None and kwargs.get("routing_number") is None:
        routing_number = "123456789"

    data = {
        "name": name,
        "account_type": "checking",  # This is a literal in the schema
        "current_balance": current_balance,
        "available_balance": available_balance,
        "institution": institution,
        "routing_number": routing_number,
        "has_overdraft_protection": has_overdraft_protection,
        "account_format": account_format,
        # Explicitly set credit-specific fields to None to prevent inheriting from base schema
        "available_credit": None,
        "total_limit": None,
        "last_statement_balance": None,
        "last_statement_date": None,
    }

    # Only add overdraft_limit if has_overdraft_protection is True
    if has_overdraft_protection and overdraft_limit is not None:
        data["overdraft_limit"] = overdraft_limit
    elif has_overdraft_protection:
        data["overdraft_limit"] = COMMON_AMOUNTS["medium"]  # 100.00

    # Add optional fields if provided
    if monthly_fee is not None:
        data["monthly_fee"] = monthly_fee

    if interest_rate is not None:
        data["interest_rate"] = interest_rate

    # Add international banking fields if provided
    if iban is not None:
        data["iban"] = iban
        if account_format == "local":
            data["account_format"] = "iban"

    if swift_bic is not None:
        data["swift_bic"] = swift_bic

    if sort_code is not None:
        data["sort_code"] = sort_code

    if branch_code is not None:
        data["branch_code"] = branch_code

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(CheckingAccountUpdate)
def create_checking_account_update_schema(
    name: Optional[str] = None,
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: Optional[str] = None,
    routing_number: Optional[str] = None,
    has_overdraft_protection: Optional[bool] = None,
    overdraft_limit: Optional[Decimal] = None,
    monthly_fee: Optional[Decimal] = None,
    interest_rate: Optional[Decimal] = None,
    # International banking fields
    iban: Optional[str] = None,
    swift_bic: Optional[str] = None,
    sort_code: Optional[str] = None,
    branch_code: Optional[str] = None,
    account_format: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CheckingAccountUpdate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance
        available_balance: Available balance
        institution: Bank or financial institution name
        routing_number: Account routing number
        has_overdraft_protection: Whether overdraft protection is enabled
        overdraft_limit: Overdraft limit
        monthly_fee: Monthly account maintenance fee
        interest_rate: Annual interest rate (if interest-bearing)
        iban: International Bank Account Number
        swift_bic: SWIFT/BIC code for international transfers
        sort_code: Sort code (used in UK and other countries)
        branch_code: Branch code (used in various countries)
        account_format: Account number format (local, iban, etc.)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CheckingAccountUpdate schema
    """
    data = {}

    # Only include fields that are provided (not None)
    if name is not None:
        data["name"] = name

    if current_balance is not None:
        data["current_balance"] = current_balance

    if available_balance is not None:
        data["available_balance"] = available_balance

    if institution is not None:
        data["institution"] = institution

    if routing_number is not None:
        data["routing_number"] = routing_number

    if has_overdraft_protection is not None:
        data["has_overdraft_protection"] = has_overdraft_protection

    if overdraft_limit is not None:
        data["overdraft_limit"] = overdraft_limit

    if monthly_fee is not None:
        data["monthly_fee"] = monthly_fee

    if interest_rate is not None:
        data["interest_rate"] = interest_rate
        
    # Explicitly set credit-specific fields to None to prevent inheriting from base schema
    data["available_credit"] = None
    data["total_limit"] = None
    data["last_statement_balance"] = None
    data["last_statement_date"] = None

    # Add international banking fields if provided
    if iban is not None:
        data["iban"] = iban

    if swift_bic is not None:
        data["swift_bic"] = swift_bic

    if sort_code is not None:
        data["sort_code"] = sort_code

    if branch_code is not None:
        data["branch_code"] = branch_code

    if account_format is not None:
        data["account_format"] = account_format

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(CheckingAccountResponse)
def create_checking_account_response_schema(
    id: int = 1,
    name: str = "Test Checking Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Test Bank",
    routing_number: Optional[str] = None,
    has_overdraft_protection: bool = False,
    overdraft_limit: Optional[Decimal] = None,
    monthly_fee: Optional[Decimal] = None,
    interest_rate: Optional[Decimal] = None,
    created_at: Optional[Any] = None,
    updated_at: Optional[Any] = None,
    # International banking fields
    iban: Optional[str] = None,
    swift_bic: Optional[str] = None,
    sort_code: Optional[str] = None,
    branch_code: Optional[str] = None,
    account_format: str = "local",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CheckingAccountResponse schema instance.

    Args:
        id: Account ID
        name: Account name
        current_balance: Current account balance (defaults to 1000.00)
        available_balance: Available balance (defaults to same as current_balance)
        institution: Bank or financial institution name
        routing_number: Account routing number (defaults to "123456789")
        has_overdraft_protection: Whether overdraft protection is enabled
        overdraft_limit: Overdraft limit (required if has_overdraft_protection is True)
        monthly_fee: Monthly account maintenance fee
        interest_rate: Annual interest rate (if interest-bearing)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        iban: International Bank Account Number
        swift_bic: SWIFT/BIC code for international transfers
        sort_code: Sort code (used in UK and other countries)
        branch_code: Branch code (used in various countries)
        account_format: Account number format (local, iban, etc.)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CheckingAccountResponse schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    # Use the create schema factory to generate the base data
    base_data = create_checking_account_schema(
        name=name,
        current_balance=current_balance,
        available_balance=available_balance,
        institution=institution,
        routing_number=routing_number,
        has_overdraft_protection=has_overdraft_protection,
        overdraft_limit=overdraft_limit,
        monthly_fee=monthly_fee,
        interest_rate=interest_rate,
        iban=iban,
        swift_bic=swift_bic,
        sort_code=sort_code,
        branch_code=branch_code,
        account_format=account_format,
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
    
    # Ensure credit-specific fields are explicitly set to None
    response_data["available_credit"] = None
    response_data["total_limit"] = None
    response_data["last_statement_balance"] = None
    response_data["last_statement_date"] = None

    # Add any additional fields from kwargs
    response_data.update(kwargs)

    return response_data
