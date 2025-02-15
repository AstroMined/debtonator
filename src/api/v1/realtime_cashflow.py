from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.realtime_cashflow import RealtimeCashflowResponse
from src.schemas.cashflow import CrossAccountAnalysis
from src.services.realtime_cashflow import RealtimeCashflowService
from src.database.database import get_db

router = APIRouter(
    prefix="/realtime-cashflow",
    tags=["realtime-cashflow"]
)

@router.get(
    "/",
    response_model=RealtimeCashflowResponse,
    description="Get real-time cashflow data across all accounts"
)
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

@router.get(
    "/cross-account-analysis",
    response_model=CrossAccountAnalysis,
    description="Get comprehensive cross-account analysis including correlations, "
                "transfer patterns, usage patterns, balance distribution, and risk assessment"
)
async def get_cross_account_analysis(
    db: AsyncSession = Depends(get_db)
) -> CrossAccountAnalysis:
    """
    Get comprehensive cross-account analysis.
    
    Returns:
        CrossAccountAnalysis: Detailed analysis including:
            - Account correlations and relationships
            - Transfer patterns between accounts
            - Usage patterns per account
            - Balance distribution analysis
            - Risk assessment for each account
    """
    service = RealtimeCashflowService(db)
    return await service.get_cross_account_analysis()
