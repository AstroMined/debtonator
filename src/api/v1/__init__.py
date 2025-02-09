from fastapi import APIRouter
from .bills import router as bills_router
from .bill_splits import router as bill_splits_router
from .accounts import router as accounts_router
from .income import router as income_router
from .cashflow import router as cashflow_router
from .bulk_import import router as bulk_import_router

api_v1_router = APIRouter()

api_v1_router.include_router(bills_router, prefix="/bills", tags=["bills"])
api_v1_router.include_router(bill_splits_router, prefix="/bill-splits", tags=["bill-splits"])
api_v1_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_v1_router.include_router(income_router, prefix="/income", tags=["income"])
api_v1_router.include_router(cashflow_router, prefix="/cashflow", tags=["cashflow"])
api_v1_router.include_router(bulk_import_router, tags=["bulk-import"])
