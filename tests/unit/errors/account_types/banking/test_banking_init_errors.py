"""
Unit tests for banking account types package initialization.

Tests ensure that all banking account type error classes are properly exported
from the banking package.
"""

from src.errors.account_types.banking import (  # Checking account errors; Savings account errors; Credit account errors; BNPL account errors; EWA account errors; Payment app account errors
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


def test_checking_account_errors_exported():
    """Test that checking account errors are properly exported."""
    assert CheckingAccountError.__name__ == "CheckingAccountError"
    assert CheckingInsufficientFundsError.__name__ == "CheckingInsufficientFundsError"
    assert (
        CheckingInternationalBankingError.__name__
        == "CheckingInternationalBankingError"
    )
    assert (
        CheckingInvalidRoutingNumberError.__name__
        == "CheckingInvalidRoutingNumberError"
    )
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
    assert (
        PaymentAppUnsupportedPlatformError.__name__
        == "PaymentAppUnsupportedPlatformError"
    )


def test_module_imports():
    """Test that all modules are properly imported."""
    from src.errors.account_types.banking import (
        bnpl,
        checking,
        credit,
        ewa,
        payment_app,
        savings,
    )

    assert checking.__name__ == "src.errors.account_types.banking.checking"
    assert savings.__name__ == "src.errors.account_types.banking.savings"
    assert credit.__name__ == "src.errors.account_types.banking.credit"
    assert bnpl.__name__ == "src.errors.account_types.banking.bnpl"
    assert ewa.__name__ == "src.errors.account_types.banking.ewa"
    assert payment_app.__name__ == "src.errors.account_types.banking.payment_app"
