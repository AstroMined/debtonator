"""
Schema factory functions for tests.

This module provides factory functions that generate valid Pydantic schema instances
for use in tests. Using these factories ensures that all repository tests follow
the proper validation flow by passing data through Pydantic schemas first.

This is a façade that re-exports factory functions from domain-specific modules
to maintain backward compatibility while allowing a more organized structure.
"""

# Re-export all factory functions from domain-specific modules to maintain API compatibility
from tests.helpers.schema_factories.accounts import (
    create_account_schema,
)
from tests.helpers.schema_factories.balance_reconciliation import (
    create_balance_reconciliation_schema,
)
from tests.helpers.schema_factories.bill_splits import (
    create_bill_split_schema,
    create_bill_split_update_schema,
)
from tests.helpers.schema_factories.credit_limit_history import (
    create_credit_limit_history_schema,
)
from tests.helpers.schema_factories.liabilities import (
    create_liability_schema,
)
from tests.helpers.schema_factories.payments import (
    create_payment_schema,
)
from tests.helpers.schema_factories.transaction_history import (
    create_transaction_history_schema,
)

# Note: As new domain-specific factory modules are created, they should be imported
# and exported here to maintain backward compatibility.
