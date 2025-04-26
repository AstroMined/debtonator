"""
Service-specific cashflow types and reexport of common cashflow types.

This module serves as a convenience import for the service layer by reexporting
the common cashflow types and adding any service-specific extensions.
"""

# Re-export common types for backward compatibility
from src.common.cashflow_types import CashflowHolidays, CashflowWarningThresholds, DateType

# Add any service-specific types here if needed in the future

