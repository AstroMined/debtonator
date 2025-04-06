"""
Banking account errors package.

This package contains error classes specific to banking account types.
"""

from src.errors.account_types.banking.bnpl import (
    BNPLAccountError,
    BNPLInstallmentCountError,
    BNPLInstallmentError,
    BNPLLifecycleError,
    BNPLNextPaymentDateError,
    BNPLPaymentFrequencyError,
    BNPLProviderError,
)

# Import specific banking account error classes for direct access
from src.errors.account_types.banking.checking import (
    CheckingAccountError,
    CheckingInsufficientFundsError,
    CheckingInternationalBankingError,
    CheckingInvalidRoutingNumberError,
    CheckingOverdraftError,
)
from src.errors.account_types.banking.credit import (
    CreditAccountError,
    CreditAPRError,
    CreditAutopayError,
    CreditCreditLimitExceededError,
    CreditPaymentDueError,
    CreditStatementError,
)
from src.errors.account_types.banking.ewa import (
    EWAAccountError,
    EWAAdvancePercentageError,
    EWAEarningsValidationError,
    EWANextPaydayError,
    EWAPayPeriodError,
    EWAProviderError,
    EWATransactionFeeError,
)
from src.errors.account_types.banking.payment_app import (
    PaymentAppAccountError,
    PaymentAppCardInformationError,
    PaymentAppLinkedAccountError,
    PaymentAppPlatformFeatureError,
    PaymentAppTransferError,
    PaymentAppUnsupportedPlatformError,
)
from src.errors.account_types.banking.savings import (
    SavingsAccountError,
    SavingsCompoundFrequencyError,
    SavingsInterestRateError,
    SavingsMinimumBalanceError,
    SavingsWithdrawalLimitError,
)
