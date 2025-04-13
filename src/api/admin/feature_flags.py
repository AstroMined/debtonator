"""
Admin API endpoints for managing feature flags.

This module provides administrative endpoints for advanced feature flag management,
including requirements management, history, and metrics. These endpoints provide
functionality beyond the basic feature flag management in the v1 API.

Note: These endpoints are currently open without authentication as the application
is designed as a single-tenant application without auth. Once user authentication
is implemented, these endpoints should be secured with proper authorization checks.

This is part of the implementation of ADR-024: Feature Flag System.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.dependencies.feature_flags import (
    get_feature_flag_repository,
    get_feature_flag_service,
)
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import (
    FeatureFlagResponse,
    FeatureFlagUpdate,
    FlagHistoryResponse,
    FlagMetricsResponse,
    RequirementsResponse,
    RequirementsUpdate,
)
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.requirements import get_default_requirements

router = APIRouter(prefix="/api/admin", tags=["admin", "feature-flags"])


@router.get(
    "/feature-flags",
    response_model=List[FeatureFlagResponse],
    status_code=status.HTTP_200_OK,
    summary="List all feature flags",
    description="Get a list of all feature flags including their value, type, and metadata",
)
async def list_feature_flags(
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    include_details: bool = Query(
        True, description="Include flag details and metadata"
    ),
    prefix: Optional[str] = Query(None, description="Filter flags by prefix"),
    enabled_only: bool = Query(False, description="Show only enabled flags"),
):
    """
    List all feature flags.

    Args:
        request: FastAPI request object
        service: Feature flag service
        include_details: Whether to include flag details and metadata
        prefix: Optional prefix to filter flags by
        enabled_only: Whether to show only enabled flags

    Returns:
        List of feature flags
    """
    flags = await service.get_all_flags(
        include_details=include_details, prefix=prefix, enabled_only=enabled_only
    )

    return flags


@router.get(
    "/feature-flags/{flag_name}",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feature flag details",
    description="Get detailed information about a specific feature flag",
)
async def get_feature_flag(
    flag_name: str,
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
):
    """
    Get a specific feature flag by name.

    Args:
        flag_name: The name of the feature flag
        request: FastAPI request object
        service: Feature flag service

    Returns:
        Feature flag details

    Raises:
        HTTPException: If the flag doesn't exist
    """
    flag = await service.get_flag(flag_name)
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found",
        )

    return flag


@router.put(
    "/feature-flags/{flag_name}",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_200_OK,
    summary="Update feature flag",
    description="Update an existing feature flag's value and configuration",
)
async def update_feature_flag(
    flag_name: str,
    update: FeatureFlagUpdate,
    request: Request,
    service: FeatureFlagService = Depends(get_feature_flag_service),
):
    """
    Update a feature flag.

    Args:
        flag_name: The name of the feature flag to update
        update: The update data
        request: FastAPI request object
        service: Feature flag service

    Returns:
        Updated feature flag

    Raises:
        HTTPException: If the flag doesn't exist
    """
    flag = await service.update_flag(flag_name, update)
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found",
        )

    return flag


@router.get(
    "/feature-flags/{flag_name}/requirements",
    response_model=RequirementsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feature flag requirements",
    description="Get the requirements for a specific feature flag",
)
async def get_flag_requirements(
    flag_name: str,
    request: Request,
    repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
):
    """
    Get requirements for a specific feature flag.

    Args:
        flag_name: The name of the feature flag
        request: FastAPI request object
        repository: Feature flag repository

    Returns:
        Requirements response with flag name and requirements mapping

    Raises:
        HTTPException: If the flag doesn't exist
    """
    try:
        requirements = await repository.get_requirements(flag_name)
        return RequirementsResponse(
            flag_name=flag_name,
            requirements=requirements,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving requirements: {str(e)}",
        )


@router.put(
    "/feature-flags/{flag_name}/requirements",
    response_model=RequirementsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update feature flag requirements",
    description="Update the requirements for a specific feature flag",
)
async def update_flag_requirements(
    flag_name: str,
    update: RequirementsUpdate,
    request: Request,
    repository: FeatureFlagRepository = Depends(get_feature_flag_repository),
):
    """
    Update requirements for a specific feature flag.

    Args:
        flag_name: The name of the feature flag
        update: The update data
        request: FastAPI request object
        repository: Feature flag repository

    Returns:
        Requirements response with flag name and updated requirements mapping

    Raises:
        HTTPException: If the flag doesn't exist or requirements are invalid
    """
    try:
        # Update the requirements
        updated_flag = await repository.update_requirements(
            flag_name, update.requirements
        )

        # Return the updated requirements
        return RequirementsResponse(
            flag_name=flag_name,
            requirements=updated_flag.requirements or {},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating requirements: {str(e)}",
        )


@router.get(
    "/feature-flags/{flag_name}/history",
    response_model=List[FlagHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get feature flag history",
    description="Get the history of changes to a feature flag",
)
async def get_flag_history(
    flag_name: str,
    request: Request,
):
    """
    Get history for a specific feature flag.

    NOTE: This endpoint is a placeholder. History tracking is not yet implemented.

    Args:
        flag_name: The name of the feature flag
        request: FastAPI request object

    Returns:
        List of history entries

    Raises:
        HTTPException: Always returns 501 Not Implemented
    """
    # This feature is not yet implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feature flag history tracking is not yet implemented",
    )


@router.get(
    "/feature-flags/{flag_name}/metrics",
    response_model=FlagMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get feature flag metrics",
    description="Get usage metrics for a feature flag",
)
async def get_flag_metrics(
    flag_name: str,
    request: Request,
):
    """
    Get usage metrics for a specific feature flag.

    NOTE: This endpoint is a placeholder. Metrics tracking is not yet implemented.

    Args:
        flag_name: The name of the feature flag
        request: FastAPI request object

    Returns:
        Metrics response

    Raises:
        HTTPException: Always returns 501 Not Implemented
    """
    # This feature is not yet implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feature flag metrics tracking is not yet implemented",
    )


@router.get(
    "/feature-flags/default-requirements",
    response_model=Dict[str, Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get default requirements",
    description="Get the default requirements mapping for feature flags",
)
async def get_default_flag_requirements():
    """
    Get the default requirements mapping for feature flags.

    This endpoint provides access to the built-in default requirements
    that are used when a feature flag doesn't have custom requirements.

    Returns:
        Dictionary of default requirements
    """
    return get_default_requirements()
