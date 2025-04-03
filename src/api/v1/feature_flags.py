"""
API endpoints for managing feature flags.

This module provides endpoints for viewing and managing feature flags.
Access to these endpoints is controlled by environment configuration.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.dependencies.feature_flags import (
    get_feature_flag_service,
    get_flag_management_enabled,
)
from src.api.response_formatter import get_formatter
from src.schemas.feature_flags import (
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagUpdate,
)
from src.services.feature_flags import FeatureFlagService

router = APIRouter()


class FeatureFlagManagementDisabled(HTTPException):
    """Exception raised when feature flag management is disabled."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Feature flag management is disabled in this environment",
        )


def check_management_enabled():
    """Check if feature flag management is enabled.

    Raises:
        FeatureFlagManagementDisabled: If feature flag management is disabled
    """
    if not get_flag_management_enabled():
        raise FeatureFlagManagementDisabled()


@router.get(
    "/flags",
    response_model=List[FeatureFlagResponse],
    status_code=status.HTTP_200_OK,
    summary="List all feature flags",
    description="Get a list of all feature flags and their current values",
)
async def list_feature_flags(
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
        include_details: bool = Query(
        False, description="Include flag details and metadata"
    ),
    prefix: Optional[str] = Query(None, description="Filter flags by prefix"),
    enabled_only: bool = Query(False, description="Show only enabled flags"),
):
    """
    List all feature flags.

    Args:
        request: The FastAPI request
        service: Feature flag service
        formatter: Response formatter
        include_details: Whether to include flag details and metadata
        prefix: Optional prefix to filter flags by
        enabled_only: Whether to show only enabled flags

    Returns:
        List of feature flags
    """
    # Check if management is enabled, even for read-only operations
    check_management_enabled()

    flags = await service.get_all_flags(
        include_details=include_details, prefix=prefix, enabled_only=enabled_only
    )

    return flags


@router.get(
    "/flags/{name}",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific feature flag",
    description="Get details of a specific feature flag by name",
)
async def get_feature_flag(
    name: str,
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    ):
    """
    Get a specific feature flag by name.

    Args:
        name: The name of the feature flag
        request: The FastAPI request
        service: Feature flag service
        formatter: Response formatter

    Returns:
        Feature flag details
    """
    # Check if management is enabled, even for read-only operations
    check_management_enabled()

    flag = await service.get_flag(name)
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{name}' not found",
        )

    return flag


@router.put(
    "/flags/{name}",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a feature flag",
    description="Update an existing feature flag's value and configuration",
)
async def update_feature_flag(
    name: str,
    flag_update: FeatureFlagUpdate,
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    ):
    """
    Update a feature flag.

    Args:
        name: The name of the feature flag to update
        flag_update: The update data
        request: The FastAPI request
        service: Feature flag service
        formatter: Response formatter

    Returns:
        Updated feature flag
    """
    # Check if management is enabled
    check_management_enabled()

    flag = await service.update_flag(name, flag_update)
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{name}' not found",
        )

    return flag


@router.post(
    "/flags",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a feature flag",
    description="Create a new feature flag with the specified configuration",
)
async def create_feature_flag(
    flag_create: FeatureFlagCreate,
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    ):
    """
    Create a new feature flag.

    Args:
        flag_create: The feature flag to create
        request: The FastAPI request
        service: Feature flag service
        formatter: Response formatter

    Returns:
        Created feature flag
    """
    # Check if management is enabled
    check_management_enabled()

    # Check if flag already exists
    existing_flag = await service.get_flag(flag_create.name)
    if existing_flag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Feature flag '{flag_create.name}' already exists",
        )

    flag = await service.create_flag(flag_create)
    return flag


@router.post(
    "/flags/bulk",
    response_model=Dict[str, FeatureFlagResponse],
    status_code=status.HTTP_200_OK,
    summary="Bulk update feature flags",
    description="Update multiple feature flags in a single operation",
)
async def bulk_update_feature_flags(
    updates: Dict[str, FeatureFlagUpdate],
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    ):
    """
    Bulk update feature flags.

    Args:
        updates: Dictionary of feature flag updates keyed by flag name
        request: The FastAPI request
        service: Feature flag service
        formatter: Response formatter

    Returns:
        Dictionary of updated feature flags keyed by flag name
    """
    # Check if management is enabled
    check_management_enabled()

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )

    results = await service.bulk_update_flags(updates)
    return results
