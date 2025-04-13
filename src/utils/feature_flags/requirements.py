"""
Default feature flag requirements mapping.

This module defines the default requirements for feature flags across repository,
service, and API layers. It provides a fallback when requirements haven't been
explicitly defined in the database.

Each feature flag has a mapping of required methods and endpoints for each layer:
- repository: Dictionary mapping repository methods to required account types
- service: Dictionary mapping service methods to required account types
- api: Dictionary mapping API endpoints to required account types

This is part of the implementation of ADR-024: Feature Flag System.
"""

from typing import Any, Dict, List

# Type aliases for better readability
Requirements = Dict[str, Dict[str, Dict[str, List[str]]]]
LayerRequirements = Dict[str, List[str]]


def get_default_requirements() -> Requirements:
    """
    Get the default feature flag requirements.

    Returns:
        Dictionary mapping feature names to layer requirements
    """
    return {
        "BANKING_ACCOUNT_TYPES_ENABLED": {
            "repository": {
                # Account repository methods
                "create_typed_entity": ["bnpl", "ewa", "payment_app"],
                "update_typed_entity": ["bnpl", "ewa", "payment_app"],
                "get_by_type": ["bnpl", "ewa", "payment_app"],
                # Account type-specific repository methods
                "apply_account_type_rules": ["bnpl", "ewa", "payment_app"],
                "validate_account_type_constraints": ["bnpl", "ewa", "payment_app"],
            },
            "service": {
                # Account service methods
                "create_account": ["bnpl", "ewa", "payment_app"],
                "update_account": ["bnpl", "ewa", "payment_app"],
                "get_account_by_type": ["bnpl", "ewa", "payment_app"],
                # Banking service methods
                "get_banking_overview": ["bnpl", "ewa", "payment_app"],
                "get_upcoming_payments": ["bnpl", "ewa", "payment_app"],
            },
            "api": {
                # Account API endpoints
                "/api/v1/accounts/banking": ["bnpl", "ewa", "payment_app"],
                "/api/v1/accounts/{account_id}": ["bnpl", "ewa", "payment_app"],
                # Banking overview endpoint
                "/api/v1/banking/overview": ["bnpl", "ewa", "payment_app"],
                "/api/v1/banking/upcoming-payments": ["bnpl", "ewa", "payment_app"],
            },
        },
        "BNPL_ACCOUNTS_ENABLED": {
            "repository": {
                # BNPL account type repository methods
                "create_typed_entity": ["bnpl"],
                "update_typed_entity": ["bnpl"],
                "get_by_type": ["bnpl"],
                # BNPL-specific repository methods
                "update_account_status": ["bnpl"],
                "record_payment": ["bnpl"],
                "get_available_credit": ["bnpl"],
            },
            "service": {
                # BNPL account service methods
                "create_account": ["bnpl"],
                "update_account": ["bnpl"],
                "get_account_by_type": ["bnpl"],
                # BNPL-specific service methods
                "update_bnpl_status": ["bnpl"],
                "process_bnpl_payment": ["bnpl"],
                "calculate_available_credit": ["bnpl"],
            },
            "api": {
                # BNPL API endpoints
                "/api/v1/accounts/bnpl": ["bnpl"],
                "/api/v1/accounts/bnpl/{account_id}": ["bnpl"],
                "/api/v1/accounts/bnpl/{account_id}/update-status": ["bnpl"],
                "/api/v1/accounts/bnpl/{account_id}/payments": ["bnpl"],
            },
        },
        "EWA_ACCOUNTS_ENABLED": {
            "repository": {
                # EWA account type repository methods
                "create_typed_entity": ["ewa"],
                "update_typed_entity": ["ewa"],
                "get_by_type": ["ewa"],
                # EWA-specific repository methods
                "get_available_advances": ["ewa"],
                "record_advance": ["ewa"],
                "record_repayment": ["ewa"],
            },
            "service": {
                # EWA account service methods
                "create_account": ["ewa"],
                "update_account": ["ewa"],
                "get_account_by_type": ["ewa"],
                # EWA-specific service methods
                "calculate_available_advance": ["ewa"],
                "process_advance_request": ["ewa"],
                "process_repayment": ["ewa"],
            },
            "api": {
                # EWA API endpoints
                "/api/v1/accounts/ewa": ["ewa"],
                "/api/v1/accounts/ewa/{account_id}": ["ewa"],
                "/api/v1/accounts/ewa/{account_id}/advances": ["ewa"],
                "/api/v1/accounts/ewa/{account_id}/repayments": ["ewa"],
            },
        },
        "PAYMENT_APP_ACCOUNTS_ENABLED": {
            "repository": {
                # Payment App account type repository methods
                "create_typed_entity": ["payment_app"],
                "update_typed_entity": ["payment_app"],
                "get_by_type": ["payment_app"],
                # Payment App-specific repository methods
                "record_transaction": ["payment_app"],
                "get_balance": ["payment_app"],
                "get_transaction_history": ["payment_app"],
            },
            "service": {
                # Payment App account service methods
                "create_account": ["payment_app"],
                "update_account": ["payment_app"],
                "get_account_by_type": ["payment_app"],
                # Payment App-specific service methods
                "process_payment": ["payment_app"],
                "process_transfer": ["payment_app"],
                "get_transaction_history": ["payment_app"],
            },
            "api": {
                # Payment App API endpoints
                "/api/v1/accounts/payment-app": ["payment_app"],
                "/api/v1/accounts/payment-app/{account_id}": ["payment_app"],
                "/api/v1/accounts/payment-app/{account_id}/transactions": [
                    "payment_app"
                ],
                "/api/v1/accounts/payment-app/{account_id}/transfers": ["payment_app"],
            },
        },
        "MULTI_CURRENCY_SUPPORT_ENABLED": {
            "repository": {
                # Multi-currency repository methods
                "convert_currency": ["*"],  # Applied to all account types
                "get_exchange_rate": ["*"],
                "set_account_currency": ["*"],
            },
            "service": {
                # Multi-currency service methods
                "convert_amount": ["*"],
                "get_current_exchange_rate": ["*"],
                "update_account_currency": ["*"],
            },
            "api": {
                # Multi-currency API endpoints
                "/api/v1/currency/exchange-rates": ["*"],
                "/api/v1/accounts/{account_id}/currency": ["*"],
            },
        },
        "INTERNATIONAL_ACCOUNTS_ENABLED": {
            "repository": {
                # International account repository methods
                "validate_international_account": ["checking", "savings", "bnpl"],
                "set_country_code": ["checking", "savings", "bnpl"],
                "get_by_country": ["checking", "savings", "bnpl"],
            },
            "service": {
                # International account service methods
                "validate_international_details": ["checking", "savings", "bnpl"],
                "update_country_settings": ["checking", "savings", "bnpl"],
                "get_accounts_by_country": ["checking", "savings", "bnpl"],
            },
            "api": {
                # International account API endpoints
                "/api/v1/accounts/international": ["checking", "savings", "bnpl"],
                "/api/v1/accounts/{account_id}/country": [
                    "checking",
                    "savings",
                    "bnpl",
                ],
            },
        },
    }


def get_initial_requirements_for_repository() -> Dict[str, Any]:
    """
    Get just the repository layer requirements for seeding the database.

    Returns:
        Dictionary mapping feature names to repository requirements
    """
    all_requirements = get_default_requirements()
    repository_requirements = {}

    for feature_name, layers in all_requirements.items():
        if "repository" in layers:
            repository_requirements[feature_name] = {"repository": layers["repository"]}

    return repository_requirements


def get_initial_requirements_for_service() -> Dict[str, Any]:
    """
    Get just the service layer requirements for seeding the database.

    Returns:
        Dictionary mapping feature names to service requirements
    """
    all_requirements = get_default_requirements()
    service_requirements = {}

    for feature_name, layers in all_requirements.items():
        if "service" in layers:
            service_requirements[feature_name] = {"service": layers["service"]}

    return service_requirements


def get_initial_requirements_for_api() -> Dict[str, Any]:
    """
    Get just the API layer requirements for seeding the database.

    Returns:
        Dictionary mapping feature names to API requirements
    """
    all_requirements = get_default_requirements()
    api_requirements = {}

    for feature_name, layers in all_requirements.items():
        if "api" in layers:
            api_requirements[feature_name] = {"api": layers["api"]}

    return api_requirements
