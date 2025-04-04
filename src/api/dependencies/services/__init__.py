"""
Service dependencies module.

This module provides FastAPI dependencies for all application services.
It centralizes all service dependencies for easier importing and management.

Implements dependencies for the Service Layer of ADR-016 Account Type Expansion,
ADR-019 Banking Account Types, and ADR-024 Feature Flags.
"""

from src.api.dependencies.services.accounts import get_account_service
from src.api.dependencies.services.feature_flags import get_feature_flag_service

__all__ = ["get_account_service", "get_feature_flag_service"]
