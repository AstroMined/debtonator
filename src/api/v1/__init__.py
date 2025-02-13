from fastapi import APIRouter
from .categories import router as categories_router
from .liabilities import router as liabilities_router
from .bill_splits import router as bill_splits_router
from .accounts import router as accounts_router
from .income import router as income_router
from .cashflow import router as cashflow_router
from .bulk_import import router as bulk_import_router
from .payments import router as payments_router
from .transactions import router as transactions_router
from .recurring_bills import router as recurring_bills_router

api_v1_router = APIRouter()

# Include categories and liabilities routers
api_v1_router.include_router(categories_router, tags=["categories"])
api_v1_router.include_router(liabilities_router, prefix="/liabilities", tags=["liabilities"])

# Payment and bill split routers
api_v1_router.include_router(payments_router, tags=["payments"])

# Other routers
api_v1_router.include_router(bill_splits_router, prefix="/bill-splits", tags=["bill-splits"])
api_v1_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_v1_router.include_router(income_router, prefix="/income", tags=["income"])
api_v1_router.include_router(cashflow_router, prefix="/cashflow", tags=["cashflow"])
api_v1_router.include_router(bulk_import_router, tags=["bulk-import"])
api_v1_router.include_router(transactions_router, tags=["transactions"])
api_v1_router.include_router(recurring_bills_router, prefix="/recurring-bills", tags=["recurring-bills"])
