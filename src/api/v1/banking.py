"""
Banking API endpoints for Debtonator.

This module implements API endpoints for banking-specific operations,
including overview data, upcoming payments, and account type-specific operations.

Implemented as part of ADR-016 Account Type Expansion.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.api.dependencies.services import get_account_service
from src.errors.accounts import AccountError, AccountNotFoundError, AccountTypeError
from src.errors.feature_flags import FeatureDisabledError
from src.schemas.account_types import (
    AccountResponseUnion,
    BankingAccountCreateUnion,
    BankingAccountResponseUnion,
)
from src.schemas.account_types.banking.bnpl import BNPLAccountStatusUpdate
from src.services.accounts import AccountService

router = APIRouter()


@router.get(
    "/overview",
    response_model=Dict[str, Any],
    summary="Get banking overview",
    description="Provides consolidated information about the user's financial position "
    "across all banking account types, including cash balances, credit utilization, "
    "debt balances, and overall financial metrics.",
)
async def get_banking_overview(
    user_id: int = Query(..., description="User ID to get banking overview for"),
    account_service: AccountService = Depends(get_account_service),
):
    """
    Get a comprehensive overview of all banking accounts for a user.

    This endpoint provides consolidated information about the user's financial position
    across all banking account types, including cash balances, credit utilization,
    debt balances, and overall financial metrics.

    Args:
        user_id: ID of the user to get banking overview for
        account_service: Account service instance

    Returns:
        Dictionary containing banking overview metrics with keys:
        - total_cash: Total cash balance across all accounts
        - checking_balance: Total balance in checking accounts
        - savings_balance: Total balance in savings accounts
        - payment_app_balance: Total balance in payment app accounts
        - credit_used: Total credit used across credit accounts
        - credit_limit: Total credit limit across credit accounts
        - credit_available: Total available credit
        - credit_utilization: Percentage of credit used
        - bnpl_balance: Total BNPL outstanding balance
        - ewa_balance: Total EWA outstanding balance
        - total_debt: Total debt across all accounts

    Raises:
        HTTPException: If user_id is invalid or an error occurs
    """
    try:
        overview = await account_service.get_banking_overview(user_id)
        return overview
    except AccountError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )


@router.get(
    "/upcoming-payments",
    response_model=List[Dict[str, Any]],
    summary="Get upcoming payments",
    description="Provides a consolidated list of all upcoming payments from "
    "various banking account types, including credit card statements, "
    "BNPL installments, and other scheduled payments.",
)
async def get_upcoming_payments(
    user_id: int = Query(..., description="User ID to get upcoming payments for"),
    days: int = Query(
        14, description="Days to look ahead for upcoming payments", ge=1, le=90
    ),
    account_service: AccountService = Depends(get_account_service),
):
    """
    Get all upcoming payments for a user across banking account types.

    This endpoint provides a consolidated list of all upcoming payments from
    various banking account types, including credit card statements, BNPL installments,
    and other scheduled payments within the specified time period.

    Args:
        user_id: ID of the user to get upcoming payments for
        days: Number of days to look ahead for payments (1-90)
        account_service: Account service instance

    Returns:
        List of upcoming payments with due dates and amounts, each containing:
        - account_id: ID of the account
        - account_name: Name of the account
        - account_type: Type of account (credit, bnpl, etc.)
        - due_date: Payment due date
        - amount: Payment amount
        - payment_type: Type of payment (statement, installment, etc.)
        - status: Payment status (due, paid, etc.)
        - details: Additional payment details

    Raises:
        HTTPException: If user_id is invalid, days is out of range, or an error occurs
    """
    try:
        payments = await account_service.get_upcoming_payments(user_id, days)
        return payments
    except AccountError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )


@router.post(
    "/accounts",
    response_model=BankingAccountResponseUnion,
    status_code=status.HTTP_201_CREATED,
    summary="Create banking account",
    description="Creates a new banking account based on the provided account type "
    "and data. Handles all account types defined in the banking category, "
    "performing appropriate validation based on the account type.",
)
async def create_banking_account(
    account: BankingAccountCreateUnion,
    account_service: AccountService = Depends(get_account_service),
):
    """
    Create a new banking account of the appropriate type.

    This endpoint creates a new banking account based on the provided account type
    and data. It handles all account types defined in the banking category,
    performing appropriate validation based on the account type.

    Supported account types:
    - checking: Regular checking accounts
    - savings: Interest-bearing savings accounts
    - credit: Credit card accounts with credit limits
    - bnpl: Buy Now Pay Later accounts for installment payments
    - ewa: Earned Wage Access accounts for early wage access
    - payment_app: Digital payment app accounts (PayPal, Venmo, etc.)

    Args:
        account: Account creation data with account_type discriminator
        account_service: Account service instance

    Returns:
        Created account with ID and complete account details

    Raises:
        HTTPException: If validation fails or account creation fails
    """
    try:
        created_account = await account_service.create_account(account)
        return created_account
    except AccountTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AccountError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )


@router.post(
    "/accounts/bnpl/{account_id}/update-status",
    response_model=AccountResponseUnion,
    summary="Update BNPL account status",
    description="Updates the status of a Buy Now, Pay Later (BNPL) account, "
    "handling lifecycle events such as installment payments, payment date updates, "
    "and account closure when all installments are paid.",
)
async def update_bnpl_account_status(
    account_id: int = Path(..., description="ID of the BNPL account to update"),
    status_update: BNPLAccountStatusUpdate = None,
    account_service: AccountService = Depends(get_account_service),
):
    """
    Update the status of a BNPL account.

    This endpoint updates the status of a Buy Now, Pay Later (BNPL) account,
    handling lifecycle events such as installment payments, payment date updates,
    and account closure when all installments are paid.

    The endpoint can be used in two ways:
    1. With a status_update object to explicitly update specific fields
    2. Without status_update to trigger automatic status update based on payment schedule

    Args:
        account_id: ID of the BNPL account to update
        status_update: Optional status update data, including installments_paid and next_payment_date
        account_service: Account service instance

    Returns:
        Updated account information

    Raises:
        HTTPException: If account not found, not a BNPL account, or update fails
    """
    try:
        # Get the account to verify it's a BNPL account
        account = await account_service.get_account(account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)

        if account.account_type != "bnpl":
            raise AccountTypeError(
                account_type=account.account_type,
                message=f"Account {account_id} is not a BNPL account, it is a {account.account_type} account",
            )

        # If status_update is provided, use it to update the account
        if status_update:
            # Convert the BNPLAccountStatusUpdate to a dictionary
            update_data = status_update.model_dump(exclude_unset=True)

            # Perform the update with the specific BNPL account type
            updated_account = await account_service.update_account(
                account_id, update_data
            )

            if not updated_account:
                raise AccountNotFoundError(account_id=account_id)

            return updated_account

        # If no status update data is provided, use the dynamically loaded
        # update_bnpl_status method from the service layer
        updated_account = await account_service._apply_type_specific_function(
            "bnpl", "update_bnpl_status", account_id
        )

        if not updated_account:
            raise AccountNotFoundError(account_id=account_id)

        return updated_account

    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccountTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AccountError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )
    except TypeError as e:
        # Catch parameter mismatches which likely indicate API implementation issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API implementation error: {str(e)}",
        )
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get(
    "/accounts/types",
    response_model=List[Dict[str, Any]],
    summary="Get banking account types",
    description="Returns a list of all banking account types available in the system, "
    "including their names, descriptions, and categories. The list is filtered "
    "based on active feature flags.",
)
async def get_banking_account_types(
    account_service: AccountService = Depends(get_account_service),
):
    """
    Get a list of available banking account types.

    This endpoint returns a list of all banking account types available in the system,
    including their names, descriptions, and categories. The list is filtered
    based on active feature flags.

    Args:
        account_service: Account service instance (unused but required for dependency injection)

    Returns:
        List of available banking account types, each containing:
        - account_type: Type identifier (e.g., "checking", "savings")
        - name: Display name of the account type
        - description: Detailed description
        - category: Account type category
        - icon: Icon identifier for UI representation

    Raises:
        HTTPException: If an error occurs while retrieving account types
    """
    try:
        # Use account type registry to get banking account types
        from src.registry.account_types import account_type_registry

        # Get all account types in the "banking" category
        types = account_type_registry.get_types_by_category("banking")

        # Return serialized list
        return [
            {
                "account_type": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "icon": t.icon,
                "supports_multi_currency": t.features.get("multi_currency", False),
                "supports_international": t.features.get("international", False),
            }
            for t in types
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving account types: {str(e)}",
        )


@router.get(
    "/currency/exchange-rates",
    response_model=Dict[str, Any],
    summary="Get current exchange rates",
    description="Returns current exchange rates for currency conversion. "
    "Requires the MULTI_CURRENCY_SUPPORT_ENABLED feature flag.",
)
async def get_exchange_rates(
    base_currency: str = Query("USD", description="Base currency code (ISO 4217)"),
    account_service: AccountService = Depends(get_account_service),
):
    """
    Get current exchange rates for currency conversion.

    This endpoint returns the current exchange rates for the specified base currency,
    which can be used for currency conversion in multi-currency accounts.

    Args:
        base_currency: Base currency code in ISO 4217 format (default: USD)
        account_service: Account service instance

    Returns:
        Dictionary containing:
        - base_currency: The base currency code
        - rates: Dictionary mapping currency codes to exchange rates
        - timestamp: Timestamp of the rates (ISO 8601 format)

    Raises:
        HTTPException: If base_currency is invalid or an error occurs

    Note:
        This endpoint requires the MULTI_CURRENCY_SUPPORT_ENABLED feature flag.
        The feature flag check is handled by the middleware based on the endpoint path.
    """
    try:
        # Use account service to get exchange rates
        exchange_rates = await account_service._apply_type_specific_function(
            "banking", "get_current_exchange_rates", base_currency
        )

        if not exchange_rates:
            # If no specific implementation, return mock data
            # In a real implementation, this would call an exchange rate API
            from datetime import datetime

            # Sample exchange rates (for demonstration purposes)
            rates = {
                "EUR": 0.91,
                "GBP": 0.77,
                "JPY": 155.45,
                "CAD": 1.36,
                "AUD": 1.48,
                "CHF": 0.89,
                "CNY": 7.10,
                "INR": 83.20,
                "MXN": 16.80,
                "BRL": 5.05,
            }

            exchange_rates = {
                "base_currency": base_currency,
                "rates": rates,
                "timestamp": datetime.utcnow().isoformat(),
            }

        return exchange_rates
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exchange rates: {str(e)}",
        )


@router.put(
    "/accounts/{account_id}/currency",
    response_model=AccountResponseUnion,
    summary="Update account currency",
    description="Updates the currency of an account. Requires the MULTI_CURRENCY_SUPPORT_ENABLED feature flag.",
)
async def update_account_currency(
    account_id: int = Path(..., description="ID of the account to update"),
    currency: str = Query(..., description="New currency code (ISO 4217)"),
    account_service: AccountService = Depends(get_account_service),
):
    """
    Update the currency of an account.

    This endpoint updates the currency of an account. The account's balances
    will be converted to the new currency using the current exchange rate.

    Args:
        account_id: ID of the account to update
        currency: New currency code in ISO 4217 format (e.g., USD, EUR, GBP)
        account_service: Account service instance

    Returns:
        Updated account information

    Raises:
        HTTPException: If account not found, currency is invalid, or update fails

    Note:
        This endpoint requires the MULTI_CURRENCY_SUPPORT_ENABLED feature flag.
        The feature flag check is handled by the middleware based on the endpoint path.
    """
    try:
        # Get the account to verify it exists
        account = await account_service.get_account(account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)

        # Call the service function to update the currency
        # First try to use the type-specific function if available
        updated_account = await account_service._apply_type_specific_function(
            account.account_type, "update_account_currency", account_id, currency
        )

        # If no type-specific function is available, use a generic update
        if not updated_account:
            update_data = {"currency": currency}
            updated_account = await account_service.update_account(
                account_id, update_data
            )

        if not updated_account:
            raise AccountNotFoundError(account_id=account_id)

        return updated_account
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccountError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating account currency: {str(e)}",
        )


@router.put(
    "/accounts/{account_id}/international",
    response_model=AccountResponseUnion,
    summary="Update international banking details",
    description="Updates the international banking details of an account. "
    "Requires the INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED feature flag.",
)
async def update_international_details(
    account_id: int = Path(..., description="ID of the account to update"),
    iban: Optional[str] = Query(None, description="International Bank Account Number"),
    swift_bic: Optional[str] = Query(None, description="SWIFT/BIC code"),
    sort_code: Optional[str] = Query(None, description="Sort code (UK/Ireland)"),
    branch_code: Optional[str] = Query(None, description="Branch code"),
    country_code: str = Query(..., description="Country code (ISO 3166-1 alpha-2)"),
    account_service: AccountService = Depends(get_account_service),
):
    """
    Update the international banking details of an account.

    This endpoint updates the international banking details of an account,
    such as IBAN, SWIFT/BIC code, sort code, and branch code.

    Args:
        account_id: ID of the account to update
        iban: International Bank Account Number (optional)
        swift_bic: SWIFT/BIC code (optional)
        sort_code: Sort code for UK/Ireland banking (optional)
        branch_code: Branch code for various countries (optional)
        country_code: Country code in ISO 3166-1 alpha-2 format (required)
        account_service: Account service instance

    Returns:
        Updated account information

    Raises:
        HTTPException: If account not found, details are invalid, or update fails

    Note:
        This endpoint requires the INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED feature flag.
        The feature flag check is handled by the middleware based on the endpoint path.
        Different fields are required based on the country code:
        - IBAN is required for most European countries
        - SWIFT/BIC is required for international transfers
        - Sort code is required for UK and Ireland
        - Branch code format varies by country
    """
    try:
        # Get the account to verify it exists
        account = await account_service.get_account(account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)

        # Check if account type supports international banking
        from src.registry.account_types import account_type_registry

        account_type_info = account_type_registry.get_type_by_id(account.account_type)

        if not account_type_info or not account_type_info.features.get(
            "international", False
        ):
            raise AccountTypeError(
                account_type=account.account_type,
                message=f"Account type {account.account_type} does not support international banking features",
            )

        # Prepare update data
        update_data = {"country_code": country_code}
        if iban is not None:
            update_data["iban"] = iban
        if swift_bic is not None:
            update_data["swift_bic"] = swift_bic
        if sort_code is not None:
            update_data["sort_code"] = sort_code
        if branch_code is not None:
            update_data["branch_code"] = branch_code

        # Call the service function to update the international details
        # First try to use the type-specific function if available
        updated_account = await account_service._apply_type_specific_function(
            account.account_type,
            "update_international_details",
            account_id,
            update_data,
        )

        # If no type-specific function is available, use a generic update
        if not updated_account:
            updated_account = await account_service.update_account(
                account_id, update_data
            )

        if not updated_account:
            raise AccountNotFoundError(account_id=account_id)

        return updated_account
    except AccountNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccountTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AccountError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FeatureDisabledError as e:
        # This is actually handled by middleware, but included for completeness
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature disabled: {e.feature_name}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating international banking details: {str(e)}",
        )
