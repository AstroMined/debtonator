from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.realtime_cashflow import RealtimeCashflowResponse
from src.services.realtime_cashflow import RealtimeCashflowService
from src.database.database import get_db

router = APIRouter(
    prefix="/realtime-cashflow",
    tags=["realtime-cashflow"]
)

@router.get("/", response_model=RealtimeCashflowResponse)
async def get_realtime_cashflow(
    db: AsyncSession = Depends(get_db)
) -> RealtimeCashflowResponse:
    """
    Get real-time cashflow data across all accounts.
    
    Returns:
        RealtimeCashflowResponse: Current financial position including:
            - Account balances
            - Total available funds
            - Total available credit
            - Total liabilities due
            - Net position
            - Next bill due date
            - Minimum balance required
            - Projected deficit (if any)
    """
    service = RealtimeCashflowService(db)
    data = await service.get_realtime_cashflow()
    return RealtimeCashflowResponse(data=data)
