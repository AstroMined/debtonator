"""
Account type registry initialization.

This module handles the registration of all account types with the AccountTypeRegistry.
It is called during application startup to ensure all account types are available
for use throughout the application.

Implemented as part of ADR-016 Account Type Expansion.
"""

from src.models.account_types.banking import (
    BNPLAccount,
    CheckingAccount,
    CreditAccount,
    EWAAccount,
    PaymentAppAccount,
    SavingsAccount,
)
from src.registry.account_types import account_type_registry
from src.schemas.account_types.banking import (
    BNPLAccountCreate,
    CheckingAccountCreate,
    CreditAccountCreate,
    EWAAccountCreate,
    PaymentAppAccountCreate,
    SavingsAccountCreate,
)


def register_account_types() -> None:
    """
    Register all account types with the AccountTypeRegistry.

    This function should be called during application startup to ensure
    all account types are available for use throughout the application.
    """
    # Banking Account Types
    account_type_registry.register(
        account_type_id="checking",
        model_class=CheckingAccount,
        schema_class=CheckingAccountCreate,
        name="Checking Account",
        description="Standard transaction account for day-to-day banking",
        category="Banking",
        feature_flag="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    account_type_registry.register(
        account_type_id="savings",
        model_class=SavingsAccount,
        schema_class=SavingsAccountCreate,
        name="Savings Account",
        description="Interest-bearing account for saving money",
        category="Banking",
        feature_flag="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    account_type_registry.register(
        account_type_id="credit",
        model_class=CreditAccount,
        schema_class=CreditAccountCreate,
        name="Credit Card",
        description="Revolving credit account with a credit limit",
        category="Banking",
        feature_flag="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    account_type_registry.register(
        account_type_id="payment_app",
        model_class=PaymentAppAccount,
        schema_class=PaymentAppAccountCreate,
        name="Payment App",
        description="Digital wallet like PayPal, Venmo, or Cash App",
        category="Banking",
        feature_flag="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    account_type_registry.register(
        account_type_id="bnpl",
        model_class=BNPLAccount,
        schema_class=BNPLAccountCreate,
        name="Buy Now, Pay Later",
        description="Short-term installment plan for purchases",
        category="Banking",
        feature_flag="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    account_type_registry.register(
        account_type_id="ewa",
        model_class=EWAAccount,
        schema_class=EWAAccountCreate,
        name="Earned Wage Access",
        description="Early access to earned wages before payday",
        category="Banking",
        feature_flag="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    # TODO: Register additional account types as they are implemented
    # - Investment account types (Phase 3 ADR-020)
    # - Loan account types (Phase 4 ADR-021)
    # - Bill/obligation account types (Phase 5 ADR-022)
