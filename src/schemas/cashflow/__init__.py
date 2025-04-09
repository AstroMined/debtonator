# Re-export all schemas for backward compatibility
from src.schemas.cashflow.cashflow_account_analysis import (
    AccountCorrelation,
    AccountRiskAssessment,
    AccountUsagePattern,
    BalanceDistribution,
    CrossAccountAnalysis,
    TransferPattern,
)
from src.schemas.cashflow.cashflow_base import (
    CashflowBase,
    CashflowCreate,
    CashflowFilters,
    CashflowInDB,
    CashflowList,
    CashflowResponse,
    CashflowUpdate,
)
from src.schemas.cashflow.cashflow_forecasting import (
    AccountForecastMetrics,
    AccountForecastRequest,
    AccountForecastResponse,
    AccountForecastResult,
    CustomForecastParameters,
    CustomForecastResponse,
    CustomForecastResult,
)
from src.schemas.cashflow.cashflow_historical import (
    HistoricalPeriodAnalysis,
    HistoricalTrendMetrics,
    HistoricalTrendsResponse,
    SeasonalityAnalysis,
)
from src.schemas.cashflow.cashflow_metrics import (
    DeficitCalculation,
    HourlyRates,
    MinimumRequired,
)
