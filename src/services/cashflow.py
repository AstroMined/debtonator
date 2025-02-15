"""DEPRECATED: Use src.services.cashflow.main instead."""

from warnings import warn

from .cashflow.main import CashflowService

warn(
    "This module is deprecated. Use src.services.cashflow.main instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['CashflowService']
