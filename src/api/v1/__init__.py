from fastapi import APIRouter

from src.api.v1.accounts import router as accounts_router
from src.api.v1.banking import router as banking_router
from src.api.v1.bill_splits import router as bill_splits_router
from src.api.v1.bulk_import import router as bulk_import_router
from src.api.v1.cashflow import router as cashflow_router
from src.api.v1.categories import router as categories_router
from src.api.v1.deposit_schedules import router as deposit_schedules_router
from src.api.v1.feature_flags import router as feature_flags_router
from src.api.v1.income import router as income_router
from src.api.v1.income_analysis import router as income_analysis_router
from src.api.v1.income_categories import router as income_categories_router
from src.api.v1.liabilities import router as liabilities_router
from src.api.v1.payment_schedules import router as payment_schedules_router
from src.api.v1.payments import router as payments_router
from src.api.v1.realtime_cashflow import router as realtime_cashflow_router
from src.api.v1.recurring_bills import router as recurring_bills_router
from src.api.v1.recurring_income import router as recurring_income_router
from src.api.v1.transactions import router as transactions_router

api_v1_router = APIRouter()

# Include categories and liabilities routers
api_v1_router.include_router(categories_router, tags=["categories"])
api_v1_router.include_router(
    liabilities_router, prefix="/liabilities", tags=["liabilities"]
)

# Payment and bill split routers
api_v1_router.include_router(payments_router, tags=["payments"])

# Other routers
api_v1_router.include_router(
    bill_splits_router, prefix="/bill-splits", tags=["bill-splits"]
)
api_v1_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_v1_router.include_router(
    income_categories_router, prefix="/income/categories"
)  # Tags already set in router
api_v1_router.include_router(income_router, prefix="/income", tags=["income"])
api_v1_router.include_router(cashflow_router, prefix="/cashflow", tags=["cashflow"])
api_v1_router.include_router(bulk_import_router, tags=["bulk-import"])
api_v1_router.include_router(transactions_router, tags=["transactions"])
api_v1_router.include_router(
    recurring_bills_router, prefix="/recurring-bills", tags=["recurring-bills"]
)
api_v1_router.include_router(payment_schedules_router, tags=["payment-schedules"])
api_v1_router.include_router(deposit_schedules_router, tags=["deposit-schedules"])
api_v1_router.include_router(recurring_income_router, tags=["recurring-income"])
api_v1_router.include_router(income_analysis_router, tags=["income-analysis"])
api_v1_router.include_router(realtime_cashflow_router, tags=["realtime-cashflow"])
api_v1_router.include_router(
    feature_flags_router, prefix="/feature-flags", tags=["feature-flags"]
)
api_v1_router.include_router(banking_router, prefix="/banking", tags=["banking"])
