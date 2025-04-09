"""
Database utility functions.

NOTE: This module crosses layers between database and HTTP concerns.
It would be more appropriate to move this functionality to src/errors/
to maintain proper separation of concerns.
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def handle_db_error(error: IntegrityError) -> None:
    """
    Handle database errors and raise appropriate HTTP exceptions.
    
    This function crosses layers between database and HTTP concerns.
    It would be more appropriate to move this functionality to src/errors/
    to maintain proper separation of concerns.
    
    Args:
        error: The database integrity error to handle
        
    Raises:
        HTTPException: With appropriate status code based on the error
    """
    if "unique" in str(error).lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource already exists",
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(error),
    )
