from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def handle_db_error(error: IntegrityError) -> None:
    """Handle database errors and raise appropriate HTTP exceptions"""
    if "unique" in str(error).lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource already exists",
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(error),
    )
