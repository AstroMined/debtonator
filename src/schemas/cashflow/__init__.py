# Re-export all schemas for backward compatibility
from src.schemas.cashflow.account_analysis import (
    AccountCorrelation,
    AccountRiskAssessment,
    AccountUsagePattern,
    BalanceDistribution,
    CrossAccountAnalysis,
    TransferPattern,
)
from src.schemas.cashflow.base import (
    CashflowBase,
    CashflowCreate,
    CashflowFilters,
    CashflowInDB,
    CashflowList,
    CashflowResponse,
    CashflowUpdate,
)
from src.schemas.cashflow.forecasting import (
    AccountForecastMetrics,
    AccountForecastRequest,
    AccountForecastResponse,
    AccountForecastResult,
    CustomForecastParameters,
    CustomForecastResponse,
    CustomForecastResult,
)
from src.schemas.cashflow.historical import (
    HistoricalPeriodAnalysis,
    HistoricalTrendMetrics,
    HistoricalTrendsResponse,
    SeasonalityAnalysis,
)
from src.schemas.cashflow.metrics import (
    DeficitCalculation,
    HourlyRates,
    MinimumRequired,
)
