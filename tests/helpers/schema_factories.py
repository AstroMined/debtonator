""" 
Schema factory functions for tests.

NOTE: This file is maintained for backward compatibility only.
New code should import factory functions from the schema_factories package.

Example:
    # Old way (still works)
    from tests.helpers.schema_factories import create_bill_split_schema
    
    # New way (preferred)
    from tests.helpers.schema_factories import create_bill_split_schema
    # or
    from tests.helpers.schema_factories.bill_splits import create_bill_split_schema
"""

# Re-export all factory functions from the new modular structure
from tests.helpers.schema_factories import (
    create_account_schema,
    create_balance_reconciliation_schema,
    create_bill_split_schema,
    create_bill_split_update_schema,
    create_credit_limit_history_schema,
    create_liability_schema,
    create_payment_schema,
    create_transaction_history_schema,
)
