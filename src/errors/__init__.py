"""
Errors module initialization.

This module dynamically imports all submodules and makes their exports available
at the package level for backward compatibility.
"""

# Dynamic import for account types
import importlib
import os
import pkgutil
from pathlib import Path

# Account type errors - using the hierarchical structure
from src.errors.account_types import (
    BNPLAccountError,
    BNPLInstallmentCountError,
    BNPLInstallmentError,
    BNPLLifecycleError,
    BNPLNextPaymentDateError,
    BNPLPaymentFrequencyError,
    BNPLProviderError,
    CheckingAccountError,
    CheckingInsufficientFundsError,
    CheckingInternationalBankingError,
    CheckingInvalidRoutingNumberError,
    CheckingOverdraftError,
    CreditAccountError,
    CreditAPRError,
    CreditAutopayError,
    CreditCreditLimitExceededError,
    CreditPaymentDueError,
    CreditStatementError,
    EWAAccountError,
    EWAAdvancePercentageError,
    EWAEarningsValidationError,
    EWANextPaydayError,
    EWAPayPeriodError,
    EWAProviderError,
    EWATransactionFeeError,
    PaymentAppAccountError,
    PaymentAppCardInformationError,
    PaymentAppLinkedAccountError,
    PaymentAppPlatformFeatureError,
    PaymentAppTransferError,
    PaymentAppUnsupportedPlatformError,
    SavingsAccountError,
    SavingsCompoundFrequencyError,
    SavingsInterestRateError,
    SavingsMinimumBalanceError,
    SavingsWithdrawalLimitError,
)

# Base error classes
from src.errors.accounts import (
    AccountError,
    AccountNotFoundError,
    AccountOperationError,
    AccountTypeError,
    AccountValidationError,
)

# Feature flag errors
from src.errors.feature_flags import FeatureFlagAccountError

# HTTP exceptions
from src.errors.http_exceptions import (
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountOperationHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    FeatureFlagAccountHTTPException,
)

# Utilities
from src.errors.utils import account_error_to_http_exception


def _import_submodules(package_name):
    """Dynamically import all submodules."""
    package = importlib.import_module(package_name)
    for _, name, is_pkg in pkgutil.iter_modules(
        package.__path__, package.__name__ + "."
    ):
        if is_pkg:
            _import_submodules(name)
        else:
            try:
                module = importlib.import_module(name)
                # Add all objects from the module to the package namespace
                for obj_name in dir(module):
                    if not obj_name.startswith("_"):  # Skip private members
                        obj = getattr(module, obj_name)
                        # Only import error classes
                        if isinstance(obj, type) and issubclass(obj, Exception):
                            globals()[obj_name] = obj
            except ImportError as e:
                print(f"Error importing {name}: {e}")


# Import any additional account type errors that might be added in the future
try:
    _import_submodules("src.errors.account_types")
except ImportError:
    # During first import, the submodules might not exist yet
    pass
