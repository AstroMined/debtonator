"""
Unit tests for errors package initialization.

Tests ensure that all error classes are properly exported from the errors package.
"""

import pytest

from src.errors import (
    # Base error classes
    AccountError,
    AccountNotFoundError,
    AccountTypeError,
    AccountValidationError,
    AccountOperationError,
    
    # Feature flag errors
    FeatureFlagAccountError,
    
    # HTTP exceptions
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    AccountOperationHTTPException,
    FeatureFlagAccountHTTPException,
    
    # Utilities
    account_error_to_http_exception,
    
    # Checking account errors
    CheckingAccountError,
    CheckingInsufficientFundsError,
    CheckingInternationalBankingError,
    CheckingInvalidRoutingNumberError,
    CheckingOverdraftError,
    
    # Savings account errors
    SavingsAccountError,
    SavingsCompoundFrequencyError,
    SavingsInterestRateError,
    SavingsMinimumBalanceError,
    SavingsWithdrawalLimitError,
    
    # Credit account errors
    CreditAccountError,
    CreditAPRError,
    CreditAutopayError,
    CreditCreditLimitExceededError,
    CreditPaymentDueError,
    CreditStatementError,
    
    # BNPL account errors
    BNPLAccountError,
    BNPLInstallmentCountError,
    BNPLInstallmentError,
    BNPLLifecycleError,
    BNPLNextPaymentDateError,
    BNPLPaymentFrequencyError,
    BNPLProviderError,
    
    # EWA account errors
    EWAAccountError,
    EWAAdvancePercentageError,
    EWAEarningsValidationError,
    EWANextPaydayError,
    EWAPayPeriodError,
    EWAProviderError,
    EWATransactionFeeError,
    
    # Payment app account errors
    PaymentAppAccountError,
    PaymentAppCardInformationError,
    PaymentAppLinkedAccountError,
    PaymentAppPlatformFeatureError,
    PaymentAppTransferError,
    PaymentAppUnsupportedPlatformError,
)


def test_base_error_classes_exported():
    """Test that base error classes are properly exported."""
    assert AccountError.__name__ == "AccountError"
    assert AccountNotFoundError.__name__ == "AccountNotFoundError"
    assert AccountTypeError.__name__ == "AccountTypeError"
    assert AccountValidationError.__name__ == "AccountValidationError"
    assert AccountOperationError.__name__ == "AccountOperationError"


def test_feature_flag_errors_exported():
    """Test that feature flag errors are properly exported."""
    assert FeatureFlagAccountError.__name__ == "FeatureFlagAccountError"


def test_http_exceptions_exported():
    """Test that HTTP exceptions are properly exported."""
    assert AccountHTTPException.__name__ == "AccountHTTPException"
    assert AccountNotFoundHTTPException.__name__ == "AccountNotFoundHTTPException"
    assert AccountTypeHTTPException.__name__ == "AccountTypeHTTPException"
    assert AccountValidationHTTPException.__name__ == "AccountValidationHTTPException"
    assert AccountOperationHTTPException.__name__ == "AccountOperationHTTPException"
    assert FeatureFlagAccountHTTPException.__name__ == "FeatureFlagAccountHTTPException"


def test_utilities_exported():
    """Test that utility functions are properly exported."""
    assert callable(account_error_to_http_exception)


def test_checking_account_errors_exported():
    """Test that checking account errors are properly exported."""
    assert CheckingAccountError.__name__ == "CheckingAccountError"
    assert CheckingInsufficientFundsError.__name__ == "CheckingInsufficientFundsError"
    assert CheckingInternationalBankingError.__name__ == "CheckingInternationalBankingError"
    assert CheckingInvalidRoutingNumberError.__name__ == "CheckingInvalidRoutingNumberError"
    assert CheckingOverdraftError.__name__ == "CheckingOverdraftError"


def test_savings_account_errors_exported():
    """Test that savings account errors are properly exported."""
    assert SavingsAccountError.__name__ == "SavingsAccountError"
    assert SavingsCompoundFrequencyError.__name__ == "SavingsCompoundFrequencyError"
    assert SavingsInterestRateError.__name__ == "SavingsInterestRateError"
    assert SavingsMinimumBalanceError.__name__ == "SavingsMinimumBalanceError"
    assert SavingsWithdrawalLimitError.__name__ == "SavingsWithdrawalLimitError"


def test_credit_account_errors_exported():
    """Test that credit account errors are properly exported."""
    assert CreditAccountError.__name__ == "CreditAccountError"
    assert CreditAPRError.__name__ == "CreditAPRError"
    assert CreditAutopayError.__name__ == "CreditAutopayError"
    assert CreditCreditLimitExceededError.__name__ == "CreditCreditLimitExceededError"
    assert CreditPaymentDueError.__name__ == "CreditPaymentDueError"
    assert CreditStatementError.__name__ == "CreditStatementError"


def test_bnpl_account_errors_exported():
    """Test that BNPL account errors are properly exported."""
    assert BNPLAccountError.__name__ == "BNPLAccountError"
    assert BNPLInstallmentCountError.__name__ == "BNPLInstallmentCountError"
    assert BNPLInstallmentError.__name__ == "BNPLInstallmentError"
    assert BNPLLifecycleError.__name__ == "BNPLLifecycleError"
    assert BNPLNextPaymentDateError.__name__ == "BNPLNextPaymentDateError"
    assert BNPLPaymentFrequencyError.__name__ == "BNPLPaymentFrequencyError"
    assert BNPLProviderError.__name__ == "BNPLProviderError"


def test_ewa_account_errors_exported():
    """Test that EWA account errors are properly exported."""
    assert EWAAccountError.__name__ == "EWAAccountError"
    assert EWAAdvancePercentageError.__name__ == "EWAAdvancePercentageError"
    assert EWAEarningsValidationError.__name__ == "EWAEarningsValidationError"
    assert EWANextPaydayError.__name__ == "EWANextPaydayError"
    assert EWAPayPeriodError.__name__ == "EWAPayPeriodError"
    assert EWAProviderError.__name__ == "EWAProviderError"
    assert EWATransactionFeeError.__name__ == "EWATransactionFeeError"


def test_payment_app_account_errors_exported():
    """Test that payment app account errors are properly exported."""
    assert PaymentAppAccountError.__name__ == "PaymentAppAccountError"
    assert PaymentAppCardInformationError.__name__ == "PaymentAppCardInformationError"
    assert PaymentAppLinkedAccountError.__name__ == "PaymentAppLinkedAccountError"
    assert PaymentAppPlatformFeatureError.__name__ == "PaymentAppPlatformFeatureError"
    assert PaymentAppTransferError.__name__ == "PaymentAppTransferError"
    assert PaymentAppUnsupportedPlatformError.__name__ == "PaymentAppUnsupportedPlatformError"


def test_module_imports():
    """Test that all modules are properly imported."""
    import src.errors.accounts
    import src.errors.feature_flags
    import src.errors.http_exceptions
    import src.errors.utils
    import src.errors.account_types
    
    assert src.errors.accounts.__name__ == "src.errors.accounts"
    assert src.errors.feature_flags.__name__ == "src.errors.feature_flags"
    assert src.errors.http_exceptions.__name__ == "src.errors.http_exceptions"
    assert src.errors.utils.__name__ == "src.errors.utils"
    assert src.errors.account_types.__name__ == "src.errors.account_types"
