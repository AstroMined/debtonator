"""
Account types errors package.

This package contains error classes for different account types.
"""

# Import banking account types errors
from src.errors.account_types.banking import (
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

# Future account type categories (e.g., investment, loan) will be imported here
