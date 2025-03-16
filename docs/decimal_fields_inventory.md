# Decimal Precision Inventory

## Overview
This document provides a comprehensive inventory of all decimal fields in the Debtonator application, categorized by their precision requirements and usage patterns. This inventory serves as the foundation for implementing ADR-013 (Decimal Precision Handling).

## Methodology
Each decimal field is classified according to:
1. **Current Implementation**: How the field is currently defined in the codebase
2. **Usage Category**:
   - **I/O Boundary**: Fields at user input/output boundaries (API/UI)
   - **Calculation**: Fields used in intermediate calculations
   - **Storage**: Fields for persistence where precision is important
3. **Recommended Precision**: The proposed decimal precision (2 or 4 decimal places)
4. **Rationale**: Justification for the recommendation

## Field Inventory

### Database Models

| File Path | Model Name | Field Name | Current Precision | Usage Category | Recommended Precision | Rationale |
|-----------|------------|------------|-------------------|----------------|----------------------|-----------|
| src/models/accounts.py | Account | available_balance | Numeric(10, 2) | Storage | Numeric(12, 4) | Balance calculations may involve multiple operations |
| src/models/accounts.py | Account | available_credit | Numeric(10, 2) | Storage | Numeric(12, 4) | Credit calculations may involve percentage operations |
| src/models/accounts.py | Account | total_limit | Numeric(10, 2) | Storage | Numeric(12, 4) | Used in credit calculations |
| src/models/accounts.py | Account | last_statement_balance | Numeric(10, 2) | Storage | Numeric(12, 4) | Consistency with other balance fields |
| src/models/liabilities.py | Liability | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Used in bill splits and other calculations |
| src/models/bill_splits.py | BillSplit | amount | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Result of splitting calculations |
| src/models/payments.py | Payment | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | May involve multiple calculations |
| src/models/payments.py | PaymentSource | amount | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Split payment calculations |
| src/models/income.py | Income | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | May be used in calculations |
| src/models/income.py | Income | undeposited_amount | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Calculated field |
| src/models/balance_history.py | BalanceHistory | balance | Numeric(10, 2) | Storage | Numeric(12, 4) | Historical balance tracking, may be used in time-series analysis |
| src/models/balance_history.py | BalanceHistory | available_credit | Numeric(10, 2) | Storage | Numeric(12, 4) | Credit history tracking, may be used in calculations |
| src/models/transaction_history.py | TransactionHistory | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Transaction amounts that affect balance calculations |
| src/models/credit_limit_history.py | CreditLimitHistory | credit_limit | Numeric(10, 2) | Storage | Numeric(12, 4) | Historical credit limit tracking |
| src/models/recurring_bills.py | RecurringBill | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Template amount used to generate liabilities |
| src/models/recurring_income.py | RecurringIncome | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Template amount used to generate income entries |
| src/models/statement_history.py | StatementHistory | statement_balance | Numeric(10, 2) | Storage | Numeric(12, 4) | Historical statement balance tracking |
| src/models/statement_history.py | StatementHistory | minimum_payment | Numeric(10, 2) | Storage | Numeric(12, 4) | Calculated minimum payment amount |
| src/models/balance_reconciliation.py | BalanceReconciliation | previous_balance | Numeric(10, 2) | Storage | Numeric(12, 4) | Historical balance value before reconciliation |
| src/models/balance_reconciliation.py | BalanceReconciliation | new_balance | Numeric(10, 2) | Storage | Numeric(12, 4) | Updated balance value after reconciliation |
| src/models/balance_reconciliation.py | BalanceReconciliation | adjustment_amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Amount of adjustment during reconciliation |
| src/models/deposit_schedules.py | DepositSchedule | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Scheduled deposit amount |
| src/models/payment_schedules.py | PaymentSchedule | amount | Numeric(10, 2) | Storage | Numeric(12, 4) | Scheduled payment amount |
| src/models/cashflow.py | CashflowForecast | total_bills | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Sum of bills in forecast period |
| src/models/cashflow.py | CashflowForecast | total_income | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Sum of income in forecast period |
| src/models/cashflow.py | CashflowForecast | balance | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Current balance calculation |
| src/models/cashflow.py | CashflowForecast | forecast | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Forecasted future balance |
| src/models/cashflow.py | CashflowForecast | min_14_day | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Minimum required funds for 14 days |
| src/models/cashflow.py | CashflowForecast | min_30_day | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Minimum required funds for 30 days |
| src/models/cashflow.py | CashflowForecast | min_60_day | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Minimum required funds for 60 days |
| src/models/cashflow.py | CashflowForecast | min_90_day | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Minimum required funds for 90 days |
| src/models/cashflow.py | CashflowForecast | daily_deficit | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Daily deficit calculation |
| src/models/cashflow.py | CashflowForecast | yearly_deficit | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Yearly deficit projection |
| src/models/cashflow.py | CashflowForecast | required_income | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Income needed to cover expenses |
| src/models/cashflow.py | CashflowForecast | hourly_rate_40 | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Hourly rate needed at 40 hours/week |
| src/models/cashflow.py | CashflowForecast | hourly_rate_30 | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Hourly rate needed at 30 hours/week |
| src/models/cashflow.py | CashflowForecast | hourly_rate_20 | Numeric(10, 2) | Storage/Calculation | Numeric(12, 4) | Hourly rate needed at 20 hours/week |

### Pydantic Schemas

| File Path | Schema Name | Field Name | Current Precision | Usage Category | Recommended Precision | Rationale |
|-----------|-------------|------------|-------------------|----------------|----------------------|-----------|
| src/schemas/accounts.py | AccountBase | available_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/accounts.py | AccountBase | available_credit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/accounts.py | AccountBase | total_limit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/accounts.py | AccountBase | last_statement_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/bill_splits.py | BillSplitBase | amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/liabilities.py | LiabilityBase | amount | validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/liabilities.py | AutoPaySettings | minimum_balance_required | validate_minimum_balance_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payments.py | PaymentSourceBase | amount | validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payments.py | PaymentBase | amount | validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | AccountBalance | current_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | AccountBalance | available_credit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | AccountBalance | total_limit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | RealtimeCashflow | total_available_funds | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | RealtimeCashflow | total_available_credit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | RealtimeCashflow | total_liabilities_due | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | RealtimeCashflow | net_position | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | RealtimeCashflow | minimum_balance_required | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/realtime_cashflow.py | RealtimeCashflow | projected_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/credit_limits.py | CreditLimitHistoryBase | credit_limit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/credit_limits.py | CreditLimitUpdate | credit_limit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/credit_limits.py | AccountCreditLimitHistoryResponse | current_credit_limit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceHistoryBase | balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceHistoryBase | available_credit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | start_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | end_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | net_change | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | average_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | min_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | max_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_history.py | BalanceTrend | volatility | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_reconciliation.py | BalanceReconciliationBase | previous_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_reconciliation.py | BalanceReconciliationBase | new_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/balance_reconciliation.py | BalanceReconciliation | adjustment_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/deposit_schedules.py | DepositScheduleBase | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/deposit_schedules.py | DepositScheduleUpdate | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | AccountImpact | current_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | AccountImpact | projected_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | AccountImpact | current_credit_utilization | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | AccountImpact | projected_credit_utilization | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | CashflowImpact | total_bills | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | CashflowImpact | available_funds | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | CashflowImpact | projected_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/impact_analysis.py | SplitImpactAnalysis | total_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income_trends.py | IncomePattern | average_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income_trends.py | SourceStatistics | total_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income_trends.py | SourceStatistics | average_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income_trends.py | SourceStatistics | min_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income_trends.py | SourceStatistics | max_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income.py | RecurringIncomeBase | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income.py | IncomeBase | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income.py | IncomeUpdate | amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income.py | IncomeFilters | min_amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/income.py | IncomeFilters | max_amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_patterns.py | AmountStatistics | average_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_patterns.py | AmountStatistics | std_dev_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_patterns.py | AmountStatistics | min_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_patterns.py | AmountStatistics | max_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_patterns.py | AmountStatistics | total_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_schedules.py | PaymentScheduleBase | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/payment_schedules.py | PaymentScheduleUpdate | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recommendations.py | ImpactMetrics | balance_impact | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recommendations.py | ImpactMetrics | credit_utilization_impact | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recommendations.py | ImpactMetrics | risk_score | decimal_places=1 | I/O Boundary | 1 decimal place | Direct user interaction - risk score displays |
| src/schemas/recommendations.py | ImpactMetrics | savings_potential | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recommendations.py | BillPaymentTimingRecommendation | historical_pattern_strength | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recommendations.py | RecommendationResponse | total_savings_potential | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recommendations.py | RecommendationResponse | average_confidence | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recurring_bills.py | RecurringBillBase | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/recurring_bills.py | RecurringBillUpdate | amount | decimal_places=2 + validate_amount_precision | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/transactions.py | TransactionBase | amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/transactions.py | TransactionUpdate | amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountCorrelation | correlation_score | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | TransferPattern | average_amount | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountUsagePattern | average_transaction_size | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountUsagePattern | utilization_rate | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | BalanceDistribution | average_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | BalanceDistribution | balance_volatility | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | BalanceDistribution | min_balance_30d | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | BalanceDistribution | max_balance_30d | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | BalanceDistribution | percentage_of_total | decimal_places=4 | I/O Boundary | 4 decimal places | Higher precision needed for percentage calculations |
| src/schemas/cashflow/account_analysis.py | AccountRiskAssessment | overdraft_risk | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountRiskAssessment | credit_utilization_risk | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountRiskAssessment | payment_failure_risk | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountRiskAssessment | volatility_score | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/account_analysis.py | AccountRiskAssessment | overall_risk_score | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | total_bills | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | total_income | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | forecast | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | min_14_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | min_30_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | min_60_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | min_90_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | daily_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | yearly_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | required_income | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | hourly_rate_40 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | hourly_rate_30 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowBase | hourly_rate_20 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | total_bills | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | total_income | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | forecast | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | min_14_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | min_30_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | min_60_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | min_90_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | daily_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | yearly_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | required_income | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | hourly_rate_40 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | hourly_rate_30 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowUpdate | hourly_rate_20 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowFilters | min_balance | Not specified | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/base.py | CashflowFilters | max_balance | Not specified | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | CustomForecastParameters | confidence_threshold | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | CustomForecastResult | projected_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | CustomForecastResult | projected_income | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | CustomForecastResult | projected_expenses | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | CustomForecastResult | confidence_score | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | CustomForecastResponse | overall_confidence | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastRequest | confidence_threshold | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | average_daily_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | minimum_projected_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | maximum_projected_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | average_inflow | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | average_outflow | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | credit_utilization | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | balance_volatility | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastMetrics | forecast_confidence | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastResult | projected_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastResult | projected_inflow | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastResult | projected_outflow | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastResult | confidence_score | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/forecasting.py | AccountForecastResponse | overall_confidence | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalTrendMetrics | average_daily_change | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalTrendMetrics | volatility | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalTrendMetrics | trend_strength | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalTrendMetrics | confidence_score | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalPeriodAnalysis | average_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalPeriodAnalysis | peak_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalPeriodAnalysis | lowest_balance | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalPeriodAnalysis | total_inflow | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalPeriodAnalysis | total_outflow | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | HistoricalPeriodAnalysis | net_change | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/historical.py | SeasonalityAnalysis | seasonal_strength | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | MinimumRequired | min_14_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | MinimumRequired | min_30_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | MinimumRequired | min_60_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | MinimumRequired | min_90_day | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | DeficitCalculation | daily_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | DeficitCalculation | yearly_deficit | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | DeficitCalculation | required_income | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | HourlyRates | hourly_rate_40 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | HourlyRates | hourly_rate_30 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |
| src/schemas/cashflow/metrics.py | HourlyRates | hourly_rate_20 | decimal_places=2 | I/O Boundary | 2 decimal places | Direct user interaction |

## Models Requiring Review
- [x] src/models/balance_history.py
- [x] src/models/balance_reconciliation.py
- [x] src/models/bill_splits.py
- [x] src/models/cashflow.py
- [x] src/models/categories.py
- [x] src/models/credit_limit_history.py
- [x] src/models/deposit_schedules.py
- [x] src/models/income_categories.py
- [x] src/models/income.py
- [x] src/models/liabilities.py
- [x] src/models/payment_schedules.py
- [x] src/models/payments.py
- [x] src/models/recurring_bills.py
- [x] src/models/recurring_income.py
- [x] src/models/statement_history.py
- [x] src/models/transaction_history.py

## Schemas Requiring Review
- [x] src/schemas/accounts.py
- [x] src/schemas/balance_history.py
- [x] src/schemas/balance_reconciliation.py
- [x] src/schemas/bill_splits.py
- [x] src/schemas/categories.py
- [x] src/schemas/credit_limits.py
- [x] src/schemas/deposit_schedules.py
- [x] src/schemas/impact_analysis.py
- [x] src/schemas/income_categories.py
- [x] src/schemas/income_trends.py
- [x] src/schemas/income.py
- [x] src/schemas/liabilities.py
- [x] src/schemas/payment_patterns.py
- [x] src/schemas/payment_schedules.py
- [x] src/schemas/payments.py
- [x] src/schemas/realtime_cashflow.py
- [x] src/schemas/recommendations.py
- [x] src/schemas/recurring_bills.py
- [x] src/schemas/transactions.py
- [x] src/schemas/cashflow/account_analysis.py
- [x] src/schemas/cashflow/base.py
- [x] src/schemas/cashflow/forecasting.py
- [x] src/schemas/cashflow/historical.py
- [x] src/schemas/cashflow/metrics.py

## Special Cases

### Bill Splitting
When splitting a fixed amount (e.g., $100) between multiple accounts (e.g., 3 accounts), traditional rounding can result in discrepancies:
- Equal split would ideally give $33.33 per account
- But $33.33 × 3 = $99.99, leaving $0.01 unaccounted for

**Proposed Solution**: Implement the Largest Remainder Method
- Calculate the base amount per split (integer division of cents)
- Calculate the remainder (modulo operation)
- Distribute the remainder one cent at a time across the splits

### Interest Calculations
Financial calculations involving interest rates:
- Intermediate calculations should use 4 decimal places
- Final amounts should be rounded to 2 decimal places for display

### Running Balances
Account balances that accumulate over many transactions:
- Higher precision during calculation prevents cumulative rounding errors
- Displayed balances still show 2 decimal places

## Calculation Patterns

### Equal Distribution
```python
def distribute_with_largest_remainder(total: Decimal, parts: int) -> List[Decimal]:
    """
    Distribute a total amount into equal parts without losing cents.
    
    Args:
        total: Total amount to distribute
        parts: Number of parts to distribute into
        
    Returns:
        List of distributed amounts that sum exactly to the total
    """
    # Step 1: Calculate base amount (integer division)
    cents = int(total * 100)
    base_cents = cents // parts
    
    # Step 2: Calculate remainder
    remainder_cents = cents - (base_cents * parts)
    
    # Step 3: Distribute base amounts
    result = [Decimal(base_cents) / 100] * parts
    
    # Step 4: Distribute remainder one cent at a time
    for i in range(remainder_cents):
        result[i] += Decimal('0.01')
        
    return result
```

### Percentage-Based Distribution
```python
def distribute_by_percentage(total: Decimal, percentages: List[Decimal]) -> List[Decimal]:
    """
    Distribute a total amount according to percentages, ensuring the sum equals the original total.
    
    Args:
        total: Total amount to distribute
        percentages: List of percentages (should sum to 100%)
        
    Returns:
        List of distributed amounts that sum exactly to the total
    """
    # Step 1: Validate percentages
    percentage_sum = sum(percentages)
    if abs(percentage_sum - Decimal('100')) > Decimal('0.0001'):
        raise ValueError(f"Percentages must sum to 100%, got {percentage_sum}%")
    
    # Step 2: Calculate amounts with 4 decimal precision
    amounts = [total * (p / Decimal('100')) for p in percentages]
    
    # Step 3: Round to 2 decimal places for initial allocation
    rounded = [amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for amount in amounts]
    
    # Step 4: Calculate difference due to rounding
    rounded_sum = sum(rounded)
    remainder = (total - rounded_sum).quantize(Decimal('0.01'))
    
    # Step 5: Distribute remainder using largest fractional part method
    if remainder != Decimal('0'):
        # Find indices of amounts with the largest fractional parts
        fractional_parts = [(i, (amounts[i] - rounded[i]).copy_abs()) 
                          for i in range(len(amounts))]
        fractional_parts.sort(key=lambda x: x[1], reverse=True)
        
        # Add or subtract cents from amounts with the largest fractional parts
        cents_to_distribute = int(remainder * 100)
        for i in range(abs(cents_to_distribute)):
            idx = fractional_parts[i % len(fractional_parts)][0]
            if cents_to_distribute > 0:
                rounded[idx] += Decimal('0.01')
            else:
                rounded[idx] -= Decimal('0.01')
    
    return rounded
