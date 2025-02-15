from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class IncomePattern(BaseModel):
    """Pattern identified in income data"""
    source: str
    frequency: str  # 'weekly', 'biweekly', 'monthly', 'irregular'
    average_amount: Decimal
    confidence_score: float = Field(ge=0.0, le=1.0)
    last_occurrence: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    next_predicted: Optional[datetime]

class SeasonalityMetrics(BaseModel):
    """Seasonal patterns in income"""
    period: str  # 'monthly', 'quarterly', 'annual'
    peak_months: List[int]  # 1-12 representing months
    trough_months: List[int]  # 1-12 representing months
    variance_coefficient: float
    confidence_score: float = Field(ge=0.0, le=1.0)

class SourceStatistics(BaseModel):
    """Statistical analysis for an income source"""
    source: str
    total_occurrences: int
    total_amount: Decimal
    average_amount: Decimal
    min_amount: Decimal
    max_amount: Decimal
    standard_deviation: float
    reliability_score: float = Field(ge=0.0, le=1.0)

class IncomeTrendsAnalysis(BaseModel):
    """Complete income trends analysis"""
    patterns: List[IncomePattern]
    seasonality: Optional[SeasonalityMetrics]
    source_statistics: List[SourceStatistics]
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    data_start_date: datetime
    data_end_date: datetime
    overall_predictability_score: float = Field(ge=0.0, le=1.0)

class IncomeTrendsRequest(BaseModel):
    """Request parameters for trends analysis"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = None
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
