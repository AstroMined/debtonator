"""
Account type-specific repository modules.

This package provides specialized repository operations for different account types.
Each subpackage or module contains functions specific to a particular account type,
enabling a clean separation of concerns and modularity as we scale to hundreds of
account types.

Implemented as part of ADR-016 Account Type Expansion.
"""

from src.repositories.account_types.banking import *  # noqa

# Future imports from other category modules will go here
# from src.repositories.account_types.investment import *  # noqa
# from src.repositories.account_types.loan import *  # noqa
