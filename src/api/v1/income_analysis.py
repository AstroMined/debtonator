from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.income_trends import IncomeTrendsRequest, IncomeTrendsAnalysis
from src.services.income_trends import IncomeTrendsService

router = APIRouter(
    prefix="/income-analysis",
    tags=["income-analysis"]
)

@router.post("/trends", response_model=IncomeTrendsAnalysis)
async def analyze_income_trends(
    request: IncomeTrendsRequest,
    db: AsyncSession = Depends(get_db)
) -> IncomeTrendsAnalysis:
    """
    Analyze income trends based on historical data.
    
    Parameters:
    - start_date: Optional start date for analysis period
    - end_date: Optional end date for analysis period
    - source: Optional specific income source to analyze
    - min_confidence: Minimum confidence score for pattern detection (0.0-1.0)
    
    Returns:
    - Comprehensive income trends analysis including:
      - Detected patterns
      - Seasonality metrics
      - Source-specific statistics
      - Overall predictability score
    """
    try:
        service = IncomeTrendsService(db)
        return await service.analyze_trends(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/trends/source/{source}", response_model=IncomeTrendsAnalysis)
async def analyze_source_trends(
    source: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_confidence: float = 0.5,
    db: AsyncSession = Depends(get_db)
) -> IncomeTrendsAnalysis:
    """
    Analyze trends for a specific income source.
    
    Parameters:
    - source: Income source to analyze
    - start_date: Optional start date for analysis period
    - end_date: Optional end date for analysis period
    - min_confidence: Minimum confidence score for pattern detection (0.0-1.0)
    
    Returns:
    - Income trends analysis focused on the specified source
    """
    request = IncomeTrendsRequest(
        source=source,
        start_date=start_date,
        end_date=end_date,
        min_confidence=min_confidence
    )
    try:
        service = IncomeTrendsService(db)
        return await service.analyze_trends(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/trends/period", response_model=IncomeTrendsAnalysis)
async def analyze_period_trends(
    start_date: date,
    end_date: date,
    min_confidence: float = 0.5,
    db: AsyncSession = Depends(get_db)
) -> IncomeTrendsAnalysis:
    """
    Analyze income trends for a specific time period.
    
    Parameters:
    - start_date: Start date for analysis period
    - end_date: End date for analysis period
    - min_confidence: Minimum confidence score for pattern detection (0.0-1.0)
    
    Returns:
    - Income trends analysis for the specified time period
    """
    request = IncomeTrendsRequest(
        start_date=start_date,
        end_date=end_date,
        min_confidence=min_confidence
    )
    try:
        service = IncomeTrendsService(db)
        return await service.analyze_trends(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
