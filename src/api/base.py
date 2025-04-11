from fastapi import APIRouter

from src.api.response_formatter import format_response
from src.api.v1 import api_v1_router
from src.api.admin import admin_router
from src.utils.config import settings

api_router = APIRouter()


# Format decimal values in all responses
def get_decimal_formatter():
    """Dependency for automatic response formatting with proper decimal precision.

    This dependency can be used in FastAPI endpoints to automatically format
    decimal values in responses according to ADR-013 standards.

    Example:
        @router.get("/items")
        async def get_items(formatter: Callable = Depends(get_decimal_formatter)):
            items = [{"price": Decimal("10.12345")}]
            return formatter({"items": items})

    Returns:
        Callable that formats API responses
    """
    return format_response


# Include versioned routers
api_router.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

# Include admin router
api_router.include_router(admin_router)
