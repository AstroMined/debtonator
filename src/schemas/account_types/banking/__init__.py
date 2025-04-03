"""
Banking account type schemas for polymorphic account validation.

This package contains schemas for banking-related account types:
- CheckingAccount: For transaction accounts with debit cards
- SavingsAccount: For interest-bearing savings accounts
- CreditAccount: For credit card accounts
- PaymentAppAccount: For digital wallets like PayPal, Venmo, Cash App, etc.
- BNPLAccount: For Buy Now Pay Later installment plans
- EWAAccount: For Earned Wage Access accounts

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from src.schemas.account_types.banking.bnpl import (
    BNPLAccountCreate,
    BNPLAccountResponse,
)
from src.schemas.account_types.banking.checking import (
    CheckingAccountCreate,
    CheckingAccountResponse,
)
from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
)
from src.schemas.account_types.banking.ewa import EWAAccountCreate, EWAAccountResponse
from src.schemas.account_types.banking.payment_app import (
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
)
from src.schemas.account_types.banking.savings import (
    SavingsAccountCreate,
    SavingsAccountResponse,
)

__all__ = [
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
