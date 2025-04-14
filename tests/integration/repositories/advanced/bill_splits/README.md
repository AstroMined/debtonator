# Bill Splits Advanced Tests

## Purpose

This directory contains advanced tests for Debtonator's bill split repository functionality, with a focus on the complex interactions between bill splits and polymorphic account types.

## Related Documentation

- [Parent: Advanced Repository Tests](/code/debtonator/tests/integration/repositories/advanced/README.md)
- [System Patterns: Dynamic Accounts and Bill Split Management](/code/debtonator/docs/system_patterns.md#dynamic-accounts-and-bill-split-management)
- [Banking Account Types Tests](/code/debtonator/tests/integration/repositories/advanced/account_types/banking/README.md)

## Architecture

Bill splits represent the distribution of bill amounts across multiple accounts. The system follows these key architectural principles:

1. Each bill has a primary account (required)
2. Bills can be split across multiple accounts through the bill_splits table
3. Primary account split is created automatically to hold the remainder
4. The sum of all splits must equal the total bill amount

The advanced tests in this directory verify the complex interactions between bill splits and various account types, transaction integrity, and validation rules.

## Implementation Patterns

### Bill Split Validation Pattern

Tests should verify that proper validation is applied to bill splits:

```python
@pytest.mark.asyncio
async def test_bill_split_validation(bill_split_repository, db_session, test_bill, test_checking_account):
    """Test validation for bill splits that exceed the total bill amount."""
    # Create bill split schema with amount exceeding bill amount
    split_schema = create_bill_split_schema(
        liability_id=test_bill.id,
        account_id=test_checking_account.id,
        amount=test_bill.amount + Decimal("10.00")
    )
    
    # Verify that creating with invalid data raises exception
    with pytest.raises(ValueError):
        await bill_split_repository.create_bill_splits(
            liability_id=test_bill.id,
            splits=[split_schema.model_dump()]
        )
```

### Transaction Boundary Testing Pattern

Tests should verify proper transaction handling for bill splits:

```python
@pytest.mark.asyncio
async def test_bill_split_transaction_rollback(bill_split_repository, db_session, test_bill, test_checking_account):
    """Test transaction rollback when an error occurs during bill split creation."""
    # Create a valid split and an invalid split (non-existent account)
    splits = [
        create_bill_split_schema(
            liability_id=test_bill.id,
            account_id=test_checking_account.id,
            amount=Decimal("50.00")
        ).model_dump(),
        create_bill_split_schema(
            liability_id=test_bill.id,
            account_id=9999,  # Non-existent account
            amount=Decimal("50.00")
        ).model_dump()
    ]
    
    # Attempt to create splits - should fail and roll back transaction
    with pytest.raises(Exception):
        await bill_split_repository.create_bill_splits(
            liability_id=test_bill.id,
            splits=splits
        )
    
    # Verify no splits were created (transaction rolled back)
    result = await bill_split_repository.get_splits_by_bill(test_bill.id)
    assert len(result) == 0
```

### Primary Account Split Generation Pattern

Tests should verify automatic primary account split generation:

```python
@pytest.mark.asyncio
async def test_primary_account_split_generation(bill_split_repository, db_session, test_bill, test_checking_account, test_savings_account):
    """Test automatic generation of primary account split."""
    # Create bill with primary account and a non-primary split
    # Primary account: test_checking_account
    # Non-primary split: test_savings_account with 25% of bill amount
    
    split_amount = test_bill.amount * Decimal("0.25")
    expected_primary_amount = test_bill.amount - split_amount
    
    split_schema = create_bill_split_schema(
        liability_id=test_bill.id,
        account_id=test_savings_account.id,
        amount=split_amount
    )
    
    # Create bill splits - should auto-generate primary account split
    await bill_split_repository.create_bill_splits(
        liability_id=test_bill.id,
        splits=[split_schema.model_dump()]
    )
    
    # Verify splits were created correctly
    splits = await bill_split_repository.get_splits_by_bill(test_bill.id)
    assert len(splits) == 2
    
    # Verify primary account split was created with correct amount
    primary_split = next((s for s in splits if s.account_id == test_checking_account.id), None)
    assert primary_split is not None
    assert primary_split.amount == expected_primary_amount
    
    # Verify total of all splits equals bill amount
    total = sum(s.amount for s in splits)
    assert total == test_bill.amount
```

## Key Responsibilities

- Test complex bill split scenarios with different account types
- Validate transaction integrity and rollback behavior
- Test automatic primary account split generation
- Verify validation rules for bill splits
- Test update scenarios for existing bill splits
- Validate error handling for invalid account references

## Testing Strategy

- Test with various combinations of account types
- Verify transaction boundaries and error scenarios
- Test partial updates and full updates to bill splits
- Ensure proper terminology (liability_id vs bill_id)
- Test both create_bill_splits and update_bill_splits methods

## Known Considerations

- Primary account split is always generated automatically
- Bill amount must equal the sum of all splits
- All account references must be valid
- No negative split amounts are allowed
- Each bill-account combination must be unique
- The system uses "liability_id" consistently (not "bill_id")
- Transaction rollback should occur for any validation errors
- Bill splits with polymorphic account types require special attention
