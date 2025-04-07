"""
Unit tests for account_types package initialization.

Tests ensure that all account type error classes are properly exported
from the account_types package.
"""

import pytest

from src.errors.account_types import (
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


def test_inheritance_relationships():
    """Test that inheritance relationships are properly maintained."""
    from src.errors.accounts import AccountError
    
    # Check that all base account type errors inherit from AccountError
    assert issubclass(CheckingAccountError, AccountError)
    assert issubclass(SavingsAccountError, AccountError)
    assert issubclass(CreditAccountError, AccountError)
    assert issubclass(BNPLAccountError, AccountError)
    assert issubclass(EWAAccountError, AccountError)
    assert issubclass(PaymentAppAccountError, AccountError)
    
    # Check that specific checking account errors inherit from CheckingAccountError
    assert issubclass(CheckingInsufficientFundsError, CheckingAccountError)
    assert issubclass(CheckingInternationalBankingError, CheckingAccountError)
    assert issubclass(CheckingInvalidRoutingNumberError, CheckingAccountError)
    assert issubclass(CheckingOverdraftError, CheckingAccountError)
    
    # Check that specific savings account errors inherit from SavingsAccountError
    assert issubclass(SavingsCompoundFrequencyError, SavingsAccountError)
    assert issubclass(SavingsInterestRateError, SavingsAccountError)
    assert issubclass(SavingsMinimumBalanceError, SavingsAccountError)
    assert issubclass(SavingsWithdrawalLimitError, SavingsAccountError)
    
    # Check that specific credit account errors inherit from CreditAccountError
    assert issubclass(CreditAPRError, CreditAccountError)
    assert issubclass(CreditAutopayError, CreditAccountError)
    assert issubclass(CreditCreditLimitExceededError, CreditAccountError)
    assert issubclass(CreditPaymentDueError, CreditAccountError)
    assert issubclass(CreditStatementError, CreditAccountError)
    
    # Check that specific BNPL account errors inherit from BNPLAccountError
    assert issubclass(BNPLInstallmentCountError, BNPLAccountError)
    assert issubclass(BNPLInstallmentError, BNPLAccountError)
    assert issubclass(BNPLLifecycleError, BNPLAccountError)
    assert issubclass(BNPLNextPaymentDateError, BNPLAccountError)
    assert issubclass(BNPLPaymentFrequencyError, BNPLAccountError)
    assert issubclass(BNPLProviderError, BNPLAccountError)
    
    # Check that specific EWA account errors inherit from EWAAccountError
    assert issubclass(EWAAdvancePercentageError, EWAAccountError)
    assert issubclass(EWAEarningsValidationError, EWAAccountError)
    assert issubclass(EWANextPaydayError, EWAAccountError)
    assert issubclass(EWAPayPeriodError, EWAAccountError)
    assert issubclass(EWAProviderError, EWAAccountError)
    assert issubclass(EWATransactionFeeError, EWAAccountError)
    
    # Check that specific payment app account errors inherit from PaymentAppAccountError
    assert issubclass(PaymentAppCardInformationError, PaymentAppAccountError)
    assert issubclass(PaymentAppLinkedAccountError, PaymentAppAccountError)
    assert issubclass(PaymentAppPlatformFeatureError, PaymentAppAccountError)
    assert issubclass(PaymentAppTransferError, PaymentAppAccountError)
    assert issubclass(PaymentAppUnsupportedPlatformError, PaymentAppAccountError)
