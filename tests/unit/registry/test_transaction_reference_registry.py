"""Unit tests for the TransactionReferenceRegistry."""

from src.registry.transaction_reference import (
    TransactionReferenceRegistry,
    transaction_reference_registry,
)


def test_transaction_reference_registry_singleton():
    """Test that TransactionReferenceRegistry is a singleton."""
    # Get two instances
    registry1 = TransactionReferenceRegistry()
    registry2 = TransactionReferenceRegistry()

    # Check if they are the same instance
    assert registry1 is registry2

    # Check if using the global instance works
    assert registry1 is transaction_reference_registry


def test_transaction_reference_registry_field_constants():
    """Test that field constants are properly initialized."""
    registry = TransactionReferenceRegistry()

    # Check transaction type constants
    assert registry.INCOME == "income"
    assert registry.EXPENSE == "expense"
    assert registry.BILL == "bill"
    assert registry.TRANSFER == "transfer"
    assert registry.RECURRING_BILL == "recurring_bill"
    assert registry.RECURRING_INCOME == "recurring_income"
    assert registry.PAYMENT == "payment"


def test_contribution_key_generation():
    """Test generation of consistent contribution keys."""
    registry = TransactionReferenceRegistry()

    # Check key generation
    assert registry.get_contribution_key("income", "Salary") == "income_Salary"
    assert registry.get_contribution_key("expense", "Groceries") == "expense_Groceries"
    assert registry.get_contribution_key("bill", "Utilities") == "bill_Utilities"


def test_extract_source():
    """Test extracting source from different transaction types."""
    registry = TransactionReferenceRegistry()

    # Check source extraction for income
    income_trans = {"type": "income", "source": "Salary", "amount": 1000}
    assert registry.extract_source(income_trans) == "Salary"

    # Check source extraction for bill
    bill_trans = {"type": "bill", "name": "Rent", "amount": 800}
    assert registry.extract_source(bill_trans) == "Rent"

    # Check source extraction for expense
    expense_trans = {"type": "expense", "description": "Groceries", "amount": 100}
    assert registry.extract_source(expense_trans) == "Groceries"

    # Check source extraction for unknown type
    unknown_trans = {"amount": 200}
    assert registry.extract_source(unknown_trans) == "unknown"


def test_extract_category():
    """Test extracting category from different transaction types."""
    registry = TransactionReferenceRegistry()

    # Check category extraction for income
    income_trans = {"type": "income", "source": "Salary", "category": "Income"}
    assert registry.extract_category(income_trans) == "Income"

    # Check category extraction for bill
    bill_trans = {"type": "bill", "name": "Rent", "category": "Housing"}
    assert registry.extract_category(bill_trans) == "Housing"

    # Check category extraction for expense
    expense_trans = {"type": "expense", "description": "Groceries", "category": "Food"}
    assert registry.extract_category(expense_trans) == "Food"

    # Check category extraction for transfer (should be None)
    transfer_trans = {"type": "transfer", "description": "To Savings", "amount": 500}
    assert registry.extract_category(transfer_trans) is None

    # Check category extraction for unknown type
    unknown_trans = {"amount": 200}
    assert registry.extract_category(unknown_trans) is None


def test_extract_amount():
    """Test extracting amount from different transaction types."""
    registry = TransactionReferenceRegistry()

    # Check amount extraction for income
    income_trans = {"type": "income", "source": "Salary", "amount": 1000}
    assert registry.extract_amount(income_trans) == 1000

    # Check amount extraction for bill
    bill_trans = {"type": "bill", "name": "Rent", "amount": 800}
    assert registry.extract_amount(bill_trans) == 800

    # Check amount extraction for expense
    expense_trans = {"type": "expense", "description": "Groceries", "amount": 100}
    assert registry.extract_amount(expense_trans) == 100

    # Check amount extraction for unknown type
    unknown_trans = {"source": "Unknown"}
    assert registry.extract_amount(unknown_trans) is None


def test_extract_date():
    """Test extracting date from different transaction types."""
    registry = TransactionReferenceRegistry()

    # Sample dates
    income_date = "2025-01-15"
    bill_date = "2025-02-01"
    expense_date = "2025-01-20"

    # Check date extraction for income
    income_trans = {"type": "income", "source": "Salary", "date": income_date}
    assert registry.extract_date(income_trans) == income_date

    # Check date extraction for bill
    bill_trans = {"type": "bill", "name": "Rent", "due_date": bill_date}
    assert registry.extract_date(bill_trans) == bill_date

    # Check date extraction for expense
    expense_trans = {
        "type": "expense",
        "description": "Groceries",
        "date": expense_date,
    }
    assert registry.extract_date(expense_trans) == expense_date

    # Check date extraction for unknown type
    unknown_trans = {"source": "Unknown"}
    assert registry.extract_date(unknown_trans) is None


def test_get_transaction_fields():
    """Test getting all field mappings for transaction types."""
    registry = TransactionReferenceRegistry()

    # Get all field mappings
    field_mappings = registry.get_transaction_fields()

    # Check income field mappings
    assert field_mappings["income"]["source"] == "source"
    assert field_mappings["income"]["category"] == "category"
    assert field_mappings["income"]["amount"] == "amount"
    assert field_mappings["income"]["date"] == "date"

    # Check bill field mappings
    assert field_mappings["bill"]["source"] == "name"
    assert field_mappings["bill"]["category"] == "category"
    assert field_mappings["bill"]["amount"] == "amount"
    assert field_mappings["bill"]["date"] == "due_date"


def test_is_valid_transaction_type():
    """Test checking if a transaction type is valid."""
    registry = TransactionReferenceRegistry()

    # Check valid types
    assert registry.is_valid_transaction_type("income") is True
    assert registry.is_valid_transaction_type("expense") is True
    assert registry.is_valid_transaction_type("bill") is True
    assert registry.is_valid_transaction_type("transfer") is True

    # Check invalid types
    assert registry.is_valid_transaction_type("invalid") is False
    assert registry.is_valid_transaction_type("") is False


def test_get_all_transaction_types():
    """Test getting all registered transaction types."""
    registry = TransactionReferenceRegistry()

    # Get all types
    all_types = registry.get_all_transaction_types()

    # Check expected types are present
    assert "income" in all_types
    assert "expense" in all_types
    assert "bill" in all_types
    assert "transfer" in all_types
    assert "recurring_bill" in all_types
    assert "recurring_income" in all_types
    assert "payment" in all_types

    # Check total count
    assert len(all_types) == 7
