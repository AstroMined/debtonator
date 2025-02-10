from datetime import date, datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.schemas.bills import BillResponse, BillCreate, BillUpdate, BillDateRange
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate
from src.schemas.payments import PaymentCreate, PaymentSourceCreate
from src.services.liabilities import LiabilityService
from src.services.payments import PaymentService

router = APIRouter()

def _convert_bill_to_liability(bill: BillCreate) -> LiabilityCreate:
    """Convert a bill creation request to a liability creation request"""
    # Calculate due date
    due_date = datetime.strptime(f"{bill.month}/{bill.day_of_month}/2025", "%m/%d/%Y").date()
    
    return LiabilityCreate(
        name=bill.bill_name,
        amount=bill.amount,
        due_date=due_date,
        category=bill.account_name,  # Using account name as category for now
        recurring=True,  # All bills are recurring by default
        recurrence_pattern={
            "frequency": "monthly",
            "day": bill.day_of_month
        }
    )

def _convert_bill_update_to_liability_update(bill_update: BillUpdate) -> LiabilityUpdate:
    """Convert a bill update request to a liability update request"""
    update_data = {}
    
    if bill_update.bill_name is not None:
        update_data["name"] = bill_update.bill_name
    if bill_update.amount is not None:
        update_data["amount"] = bill_update.amount
    if bill_update.month is not None and bill_update.day_of_month is not None:
        update_data["due_date"] = datetime.strptime(
            f"{bill_update.month}/{bill_update.day_of_month}/2025",
            "%m/%d/%Y"
        ).date()
    if bill_update.account_name is not None:
        update_data["category"] = bill_update.account_name

    return LiabilityUpdate(**update_data)

@router.get("/", response_model=List[BillResponse], deprecated=True)
async def list_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List all bills with pagination support.
    DEPRECATED: Use /api/v1/liabilities/ instead.
    """
    try:
        liability_service = LiabilityService(db)
        payment_service = PaymentService(db)
        
        liabilities = await liability_service.get_liabilities(skip=skip, limit=limit)
        
        # Convert liabilities to bill responses
        bills = []
        for liability in liabilities:
            payments = await payment_service.get_payments_for_liability(liability.id)
            bills.append({
                "id": liability.id,
                "bill_name": liability.name,
                "amount": liability.amount,
                "due_date": liability.due_date,
                "month": liability.due_date.strftime("%m"),
                "day_of_month": liability.due_date.day,
                "account_id": payments[0].sources[0].account_id if payments and payments[0].sources else None,
                "account_name": liability.category,
                "auto_pay": liability.recurring,
                "paid": bool(payments),
                "paid_date": payments[0].payment_date if payments else None,
                "up_to_date": True,  # Always true in new system
                "created_at": liability.created_at.date(),
                "updated_at": liability.updated_at.date()
            })
        return bills
    except Exception as e:
        import traceback
        error_detail = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/", response_model=BillResponse, status_code=201, deprecated=True)
async def create_bill(
    bill: BillCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bill.
    DEPRECATED: Use /api/v1/liabilities/ instead.
    """
    try:
        # Convert bill to liability
        liability_create = _convert_bill_to_liability(bill)
        
        # Create liability
        liability_service = LiabilityService(db)
        liability = await liability_service.create_liability(liability_create)
        
        # If splits are provided, create payment with sources
        if bill.splits:
            payment_create = PaymentCreate(
                bill_id=liability.id,
                amount=bill.amount,
                payment_date=liability.due_date,
                category=liability.category,
                sources=[
                    PaymentSourceCreate(
                        account_id=split.account_id,
                        amount=split.amount
                    )
                    for split in bill.splits
                ]
            )
            payment_service = PaymentService(db)
            await payment_service.create_payment(payment_create)
        
        # Return bill-style response
        return {
            "id": liability.id,
            "bill_name": liability.name,
            "amount": liability.amount,
            "due_date": liability.due_date,
            "month": liability.due_date.strftime("%m"),
            "day_of_month": liability.due_date.day,
            "account_id": bill.account_id,
            "account_name": liability.category,
            "auto_pay": liability.recurring,
            "paid": False,
            "paid_date": None,
            "up_to_date": True,
            "created_at": liability.created_at.date(),
            "updated_at": liability.updated_at.date()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{bill_id}", response_model=BillResponse, deprecated=True)
async def get_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific bill by ID.
    DEPRECATED: Use /api/v1/liabilities/{id} instead.
    """
    liability_service = LiabilityService(db)
    payment_service = PaymentService(db)
    
    liability = await liability_service.get_liability(bill_id)
    if not liability:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    payments = await payment_service.get_payments_for_liability(bill_id)
    
    return {
        "id": liability.id,
        "bill_name": liability.name,
        "amount": liability.amount,
        "due_date": liability.due_date,
        "month": liability.due_date.strftime("%m"),
        "day_of_month": liability.due_date.day,
        "account_id": payments[0].sources[0].account_id if payments and payments[0].sources else None,
        "account_name": liability.category,
        "auto_pay": liability.recurring,
        "paid": bool(payments),
        "paid_date": payments[0].payment_date if payments else None,
        "up_to_date": True,
        "created_at": liability.created_at.date(),
        "updated_at": liability.updated_at.date()
    }

@router.put("/{bill_id}", response_model=BillResponse, deprecated=True)
async def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a bill's details.
    DEPRECATED: Use /api/v1/liabilities/{id} instead.
    """
    try:
        # Convert bill update to liability update
        liability_update = _convert_bill_update_to_liability_update(bill_update)
        
        # Update liability
        liability_service = LiabilityService(db)
        liability = await liability_service.update_liability(bill_id, liability_update)
        if not liability:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        # If paid status is being updated, handle payment
        if bill_update.paid is not None:
            payment_service = PaymentService(db)
            if bill_update.paid:
                # Create payment if being marked as paid
                payment_create = PaymentCreate(
                    bill_id=bill_id,
                    amount=liability.amount,
                    payment_date=bill_update.paid_date or date.today(),
                    category=liability.category,
                    sources=[
                        PaymentSourceCreate(
                            account_id=bill_update.account_id,
                            amount=liability.amount
                        )
                    ]
                )
                await payment_service.create_payment(payment_create)
        
        # Get payments for response
        payment_service = PaymentService(db)
        payments = await payment_service.get_payments_for_liability(bill_id)
        
        return {
            "id": liability.id,
            "bill_name": liability.name,
            "amount": liability.amount,
            "due_date": liability.due_date,
            "month": liability.due_date.strftime("%m"),
            "day_of_month": liability.due_date.day,
            "account_id": payments[0].sources[0].account_id if payments and payments[0].sources else bill_update.account_id,
            "account_name": liability.category,
            "auto_pay": liability.recurring,
            "paid": bool(payments),
            "paid_date": payments[0].payment_date if payments else None,
            "up_to_date": True,
            "created_at": liability.created_at.date(),
            "updated_at": liability.updated_at.date()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.delete("/{bill_id}", deprecated=True)
async def delete_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a bill.
    DEPRECATED: Use /api/v1/liabilities/{id} instead.
    """
    liability_service = LiabilityService(db)
    success = await liability_service.delete_liability(bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}

@router.get("/unpaid/", response_model=List[BillResponse], deprecated=True)
async def list_unpaid_bills(
    db: AsyncSession = Depends(get_db)
):
    """
    List all unpaid bills.
    DEPRECATED: Use /api/v1/liabilities/unpaid/ instead.
    """
    liability_service = LiabilityService(db)
    payment_service = PaymentService(db)
    
    unpaid_liabilities = await liability_service.get_unpaid_liabilities()
    
    # Convert to bill responses
    bills = []
    for liability in unpaid_liabilities:
        bills.append({
            "id": liability.id,
            "bill_name": liability.name,
            "amount": liability.amount,
            "due_date": liability.due_date,
            "month": liability.due_date.strftime("%m"),
            "day_of_month": liability.due_date.day,
            "account_id": None,  # No payment yet
            "account_name": liability.category,
            "auto_pay": liability.recurring,
            "paid": False,
            "paid_date": None,
            "up_to_date": True,
            "created_at": liability.created_at.date(),
            "updated_at": liability.updated_at.date()
        })
    return bills

@router.get("/by-date-range/", response_model=List[BillResponse], deprecated=True)
async def get_bills_by_date_range(
    date_range: BillDateRange,
    db: AsyncSession = Depends(get_db)
):
    """
    Get bills within a specific date range.
    DEPRECATED: Use /api/v1/liabilities/by-date-range/ instead.
    """
    liability_service = LiabilityService(db)
    payment_service = PaymentService(db)
    
    liabilities = await liability_service.get_liabilities_by_date_range(
        start_date=date_range.start_date,
        end_date=date_range.end_date
    )
    
    # Convert to bill responses
    bills = []
    for liability in liabilities:
        payments = await payment_service.get_payments_for_liability(liability.id)
        bills.append({
            "id": liability.id,
            "bill_name": liability.name,
            "amount": liability.amount,
            "due_date": liability.due_date,
            "month": liability.due_date.strftime("%m"),
            "day_of_month": liability.due_date.day,
            "account_id": payments[0].sources[0].account_id if payments and payments[0].sources else None,
            "account_name": liability.category,
            "auto_pay": liability.recurring,
            "paid": bool(payments),
            "paid_date": payments[0].payment_date if payments else None,
            "up_to_date": True,
            "created_at": liability.created_at.date(),
            "updated_at": liability.updated_at.date()
        })
    return bills

@router.patch("/{bill_id}/mark-paid", response_model=BillResponse, deprecated=True)
async def mark_bill_paid(
    bill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a bill as paid.
    DEPRECATED: Use POST /api/v1/liabilities/{id}/payments/ instead.
    """
    # Get liability
    liability_service = LiabilityService(db)
    liability = await liability_service.get_liability(bill_id)
    if not liability:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Create payment
    payment_service = PaymentService(db)
    payment_create = PaymentCreate(
        bill_id=bill_id,
        amount=liability.amount,
        payment_date=date.today(),
        category=liability.category,
        sources=[
            PaymentSourceCreate(
                account_id=1,  # Default to first account for now
                amount=liability.amount
            )
        ]
    )
    await payment_service.create_payment(payment_create)
    
    # Get updated liability with payment
    liability = await liability_service.get_liability(bill_id)
    payments = await payment_service.get_payments_for_liability(bill_id)
    
    return {
        "id": liability.id,
        "bill_name": liability.name,
        "amount": liability.amount,
        "due_date": liability.due_date,
        "month": liability.due_date.strftime("%m"),
        "day_of_month": liability.due_date.day,
        "account_id": payments[0].sources[0].account_id if payments and payments[0].sources else None,
        "account_name": liability.category,
        "auto_pay": liability.recurring,
        "paid": bool(payments),
        "paid_date": payments[0].payment_date if payments else None,
        "up_to_date": True,
        "created_at": liability.created_at.date(),
        "updated_at": liability.updated_at.date()
    }
