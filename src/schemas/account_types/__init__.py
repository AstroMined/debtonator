"""
Account type schemas for polymorphic account validation.

This package contains schemas for validating and serializing polymorphic account types.
Each account type has its own dedicated schema with type-specific fields and validation.
This module also provides discriminated unions for API requests and responses.

Implemented as part of ADR-016 Account Type Expansion.
"""

from typing import Annotated, Optional, Union

from pydantic import Field, create_model

# Import banking account types
from src.schemas.account_types.banking import (
    BNPLAccountCreate,
    BNPLAccountResponse,
    CheckingAccountCreate,
    CheckingAccountResponse,
    CreditAccountCreate,
    CreditAccountResponse,
    EWAAccountCreate,
    EWAAccountResponse,
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
    SavingsAccountCreate,
    SavingsAccountResponse,
)

# Discriminated union for account creation
AccountCreateUnion = Annotated[
    Union[
        CheckingAccountCreate,
        SavingsAccountCreate,
        CreditAccountCreate,
        PaymentAppAccountCreate,
        BNPLAccountCreate,
        EWAAccountCreate,
        # Additional account types will be added here as they are implemented
    ],
    Field(discriminator="account_type"),
]

# Discriminated union for account responses
AccountResponseUnion = Annotated[
    Union[
        CheckingAccountResponse,
        SavingsAccountResponse,
        CreditAccountResponse,
        PaymentAppAccountResponse,
        BNPLAccountResponse,
        EWAAccountResponse,
        # Additional account types will be added here as they are implemented
    ],
    Field(discriminator="account_type"),
]

# Banking-specific discriminated unions
BankingAccountCreateUnion = Annotated[
    Union[
        CheckingAccountCreate,
        SavingsAccountCreate,
        CreditAccountCreate,
        PaymentAppAccountCreate,
        BNPLAccountCreate,
        EWAAccountCreate,
    ],
    Field(discriminator="account_type"),
]

BankingAccountResponseUnion = Annotated[
    Union[
        CheckingAccountResponse,
        SavingsAccountResponse,
        CreditAccountResponse,
        PaymentAppAccountResponse,
        BNPLAccountResponse,
        EWAAccountResponse,
    ],
    Field(discriminator="account_type"),
]

__all__ = [
    # Discriminated unions
    "AccountCreateUnion",
    "AccountResponseUnion",
    "BankingAccountCreateUnion",
    "BankingAccountResponseUnion",
    # Reexport all banking account types
    "CheckingAccountCreate",
    "CheckingAccountResponse",
    "SavingsAccountCreate",
    "SavingsAccountResponse",
    "CreditAccountCreate",
    "CreditAccountResponse",
    "PaymentAppAccountCreate",
    "PaymentAppAccountResponse",
    "BNPLAccountCreate",
    "BNPLAccountResponse",
    "EWAAccountCreate",
    "EWAAccountResponse",
]
