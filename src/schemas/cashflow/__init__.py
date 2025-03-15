# Re-export all schemas for backward compatibility
from src.schemas.cashflow.base import (
    CashflowBase,
    CashflowCreate,
    CashflowUpdate,
    CashflowInDB,
    CashflowResponse,
    CashflowList,
    CashflowFilters
)

from src.schemas.cashflow.metrics import (
    MinimumRequired,
    DeficitCalculation,
    HourlyRates
)

from src.schemas.cashflow.account_analysis import (
    AccountCorrelation,
    TransferPattern,
    AccountUsagePattern,
    BalanceDistribution,
    AccountRiskAssessment,
    CrossAccountAnalysis
)

from src.schemas.cashflow.forecasting import (
    CustomForecastParameters,
    CustomForecastResult,
    CustomForecastResponse,
    AccountForecastRequest,
    AccountForecastMetrics,
    AccountForecastResult,
    AccountForecastResponse
)

from src.schemas.cashflow.historical import (
    HistoricalTrendMetrics,
    HistoricalPeriodAnalysis,
    SeasonalityAnalysis,
    HistoricalTrendsResponse
)
