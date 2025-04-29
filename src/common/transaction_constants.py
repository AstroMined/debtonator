"""
Constants related to transaction types and field mappings.

This module provides centralized constants for transaction types, field mappings,
and related configuration. These constants serve as the source of truth for
transaction handling across the application.
"""

# Transaction Types
INCOME = "income"
EXPENSE = "expense" 
BILL = "bill"
TRANSFER = "transfer"
RECURRING_BILL = "recurring_bill"
RECURRING_INCOME = "recurring_income"
PAYMENT = "payment"

# Field Mappings
SOURCE_FIELDS = {
    INCOME: "source",
    EXPENSE: "description",
    BILL: "name",
    TRANSFER: "description",
    RECURRING_BILL: "name",
    RECURRING_INCOME: "source",
    PAYMENT: "description"
}

# Category field mappings for different transaction types
CATEGORY_FIELDS = {
    INCOME: "category",
    EXPENSE: "category",
    BILL: "category",
    TRANSFER: None,  # Transfers typically don't have categories
    RECURRING_BILL: "category",
    RECURRING_INCOME: "category",
    PAYMENT: "category"
}

# Amount field mappings for different transaction types
AMOUNT_FIELDS = {
    INCOME: "amount",
    EXPENSE: "amount",
    BILL: "amount",
    TRANSFER: "amount",
    RECURRING_BILL: "amount",
    RECURRING_INCOME: "amount",
    PAYMENT: "amount"
}

# Date field mappings for different transaction types
DATE_FIELDS = {
    INCOME: "date",
    EXPENSE: "date",
    BILL: "due_date",
    TRANSFER: "date",
    RECURRING_BILL: "due_date",
    RECURRING_INCOME: "date",
    PAYMENT: "payment_date"
}

# All transaction types as a list for iteration
ALL_TRANSACTION_TYPES = [
    INCOME, EXPENSE, BILL, TRANSFER,
    RECURRING_BILL, RECURRING_INCOME, PAYMENT
]
