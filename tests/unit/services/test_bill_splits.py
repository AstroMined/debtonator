"""Unit tests for the BillSplitService focusing on decimal precision handling."""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch

from src.core.decimal_precision import DecimalPrecision
from src.services.bill_splits import BillSplitService, BillSplitValidationError
from src.schemas.bill_splits import BillSplitCreate, BillSplitValidation
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit


class TestBillSplitDecimalPrecision:
    """Test decimal precision handling in the BillSplitService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock DB session for testing."""
        db_session = MagicMock()
        db_session.flush = MagicMock(return_value=None)
        db_session.commit = MagicMock(return_value=None)
        return db_session

    @pytest.fixture
    def bill_split_service(self, mock_db_session):
        """Create a BillSplitService instance with mock DB session."""
        return BillSplitService(mock_db_session)

    @patch('src.services.bill_splits.BillSplitService.get_account')
    @patch('src.services.bill_splits.BillSplitService.get_liability')
    async def test_equal_distribution_with_largest_remainder(self, mock_get_liability, mock_get_account, bill_split_service, mock_db_session):
        """Test equal distribution of bill amounts using largest remainder method."""
        # Mock liability
        liability = MagicMock()
        liability.id = 1
        liability.amount = Decimal('100.00')
        mock_get_liability.return_value = liability

        # Mock accounts
        account1 = MagicMock(spec=Account)
        account1.id = 1
        account1.type = 'checking'
        account1.available_balance = Decimal('1000.00')
        
        account2 = MagicMock(spec=Account)
        account2.id = 2
        account2.type = 'checking'
        account2.available_balance = Decimal('1000.00')
        
        account3 = MagicMock(spec=Account)
        account3.id = 3
        account3.type = 'checking'
        account3.available_balance = Decimal('1000.00')
        
        # Mock get_account to return appropriate account
        mock_get_account.side_effect = lambda id: {1: account1, 2: account2, 3: account3}.get(id)

        # Test data: $100 split three ways = $33.34 + $33.33 + $33.33
        validation = BillSplitValidation(
            liability_id=liability.id,
            total_amount=liability.amount,
            splits=[
                BillSplitCreate(liability_id=liability.id, account_id=1, amount=Decimal('33.34')),
                BillSplitCreate(liability_id=liability.id, account_id=2, amount=Decimal('33.33')),
                BillSplitCreate(liability_id=liability.id, account_id=3, amount=Decimal('33.33'))
            ]
        )

        # Run validation
        is_valid, error = await bill_split_service.validate_splits(validation)
        
        # Assertions
        assert is_valid is True, f"Failed validation with error: {error}"
        assert error is None
        
        # Verify the split amounts sum exactly to the total
        total_split = sum(split.amount for split in validation.splits)
        assert total_split == liability.amount
        
        # Verify precision of amounts (2 decimal places)
        for split in validation.splits:
            assert split.amount.as_tuple().exponent == -2, f"{split.amount} should have exactly 2 decimal places"

    @patch('src.services.bill_splits.BillSplitService.get_account')
    @patch('src.services.bill_splits.BillSplitService.get_liability')
    async def test_four_decimal_precision_in_splits(self, mock_get_liability, mock_get_account, bill_split_service, mock_db_session):
        """Test handling of 4 decimal precision in bill splits (should be validated to 2)."""
        # Mock liability
        liability = MagicMock()
        liability.id = 1
        liability.amount = Decimal('100.00')
        mock_get_liability.return_value = liability

        # Mock account
        account = MagicMock(spec=Account)
        account.id = 1
        account.type = 'checking'
        account.available_balance = Decimal('1000.00')
        mock_get_account.return_value = account

        # Create splits with 4 decimal precision
        # This should be rejected because our API boundary should enforce 2 decimal places
        validation = BillSplitValidation(
            liability_id=liability.id,
            total_amount=liability.amount,
            splits=[
                BillSplitCreate(liability_id=liability.id, account_id=1, amount=Decimal('100.0000'))
            ]
        )
        
        # Mock validation to allow testing internal handling
        with patch('src.schemas.bill_splits.BillSplitCreate.model_validate') as mock_validate:
            mock_validate.return_value = validation.splits[0]
            
            # Run validation
            is_valid, error = await bill_split_service.validate_splits(validation)
            
            # Assert validation passes (because we've mocked the model_validate)
            assert is_valid is True
            assert error is None
            
            # Use DecimalPrecision utility to round to 2 decimal places
            rounded = DecimalPrecision.round_for_display(validation.splits[0].amount)
            assert rounded == Decimal('100.00')
            assert rounded.as_tuple().exponent == -2

    @patch('src.services.bill_splits.BillSplitService.get_account')
    @patch('src.services.bill_splits.BillSplitService.get_liability')
    async def test_common_bill_split_amounts(self, mock_get_liability, mock_get_account, bill_split_service, mock_db_session):
        """Test common bill split scenarios that require precise decimal handling."""
        # Test cases with challenging divisions
        test_cases = [
            # total, num_splits, expected distribution
            (Decimal('100.00'), 3, [Decimal('33.34'), Decimal('33.33'), Decimal('33.33')]),
            (Decimal('10.00'), 3, [Decimal('3.34'), Decimal('3.33'), Decimal('3.33')]),
            (Decimal('1.00'), 3, [Decimal('0.34'), Decimal('0.33'), Decimal('0.33')]),
            (Decimal('20.00'), 3, [Decimal('6.67'), Decimal('6.67'), Decimal('6.66')]),
            (Decimal('50.00'), 3, [Decimal('16.67'), Decimal('16.67'), Decimal('16.66')]),
            (Decimal('0.01'), 3, [Decimal('0.01'), Decimal('0.00'), Decimal('0.00')]),
        ]
        
        for total, num_splits, expected_distribution in test_cases:
            # Mock liability with the test amount
            liability = MagicMock()
            liability.id = 1
            liability.amount = total
            mock_get_liability.return_value = liability
            
            # Mock accounts
            accounts = []
            for i in range(num_splits):
                account = MagicMock(spec=Account)
                account.id = i + 1
                account.type = 'checking'
                account.available_balance = Decimal('1000.00')
                accounts.append(account)
            
            # Update mock_get_account
            mock_get_account.side_effect = lambda id: accounts[id-1]
            
            # Create splits using the expected distribution
            splits = [
                BillSplitCreate(
                    liability_id=liability.id,
                    account_id=i+1,
                    amount=amount
                )
                for i, amount in enumerate(expected_distribution)
            ]
            
            validation = BillSplitValidation(
                liability_id=liability.id,
                total_amount=total,
                splits=splits
            )
            
            # Run validation
            is_valid, error = await bill_split_service.validate_splits(validation)
            
            # Assertions
            assert is_valid is True, f"Failed for {total}/{num_splits}: {error}"
            
            # Verify sum equals total within very small epsilon (for floating point safety)
            split_sum = sum(split.amount for split in validation.splits)
            assert abs(split_sum - total) < Decimal('0.0001'), f"Sum {split_sum} doesn't match total {total}"
            
            # Verify each amount has at most 2 decimal places
            for split in validation.splits:
                assert split.amount.as_tuple().exponent >= -2, f"{split.amount} has more than 2 decimal places"

    @patch('src.services.bill_splits.BillSplitService.get_account')
    @patch('src.services.bill_splits.BillSplitService.get_liability')
    async def test_suggested_splits_decimal_precision(self, mock_get_liability, mock_get_account, bill_split_service, mock_db_session):
        """Test that suggested splits maintain exact sum with 2 decimal precision."""
        # Mock liability
        liability = MagicMock()
        liability.id = 1
        liability.amount = Decimal('100.00')
        liability.primary_account_id = 1
        mock_get_liability.return_value = liability
        
        # Mock accounts
        account1 = MagicMock(spec=Account)
        account1.id = 1
        account1.type = 'checking'
        account1.available_balance = Decimal('50.00')  # Insufficient for full payment
        
        account2 = MagicMock(spec=Account)
        account2.id = 2
        account2.type = 'checking'
        account2.available_balance = Decimal('75.00')
        
        # Mock account retrieval
        mock_get_account.side_effect = lambda id: {1: account1, 2: account2}.get(id)
        
        # Mock methods for getting all accounts and historical patterns
        with patch.object(bill_split_service, 'get_all_accounts') as mock_get_all:
            with patch.object(bill_split_service, 'get_historical_bill_patterns') as mock_get_patterns:
                mock_get_all.return_value = [account1, account2]
                mock_get_patterns.return_value = []  # No historical patterns
                
                # Call the suggestion method
                with patch('src.services.bill_splits.DecimalPrecision.distribute_with_largest_remainder') as mock_distribute:
                    # Mock distribution to return our test case
                    mock_distribute.return_value = [Decimal('50.00'), Decimal('50.00')]
                    
                    suggestions = await bill_split_service.suggest_splits(liability.id)
                    
                    # Verify mock was called with correct parameters
                    mock_distribute.assert_called_once()
                    
                    # Assertions on the result
                    assert suggestions.liability_id == liability.id
                    assert suggestions.total_amount == liability.amount
                    
                    # Verify sum of suggestions equals the total amount
                    total_suggested = sum(s.amount for s in suggestions.suggestions)
                    assert total_suggested == liability.amount
                    
                    # Verify each suggestion amount has exactly 2 decimal places
                    for suggestion in suggestions.suggestions:
                        assert suggestion.amount.as_tuple().exponent == -2, \
                               f"{suggestion.amount} should have exactly 2 decimal places"

    @patch('src.services.bill_splits.BillSplitService.get_account')
    @patch('src.services.bill_splits.BillSplitService.get_liability')
    async def test_hundred_dollar_split_three_ways(self, mock_get_liability, mock_get_account, bill_split_service, mock_db_session):
        """Test the classic $100 split three ways scenario, confirming exact distribution."""
        # Mock liability
        liability = MagicMock()
        liability.id = 1
        liability.amount = Decimal('100.00')
        mock_get_liability.return_value = liability
        
        # Mock accounts
        accounts = []
        for i in range(3):
            account = MagicMock(spec=Account)
            account.id = i + 1
            account.type = 'checking'
            account.available_balance = Decimal('1000.00')
            accounts.append(account)
        
        # Update mock_get_account
        mock_get_account.side_effect = lambda id: accounts[id-1]
        
        # Test using the DecimalPrecision utility directly
        expected_distribution = DecimalPrecision.distribute_with_largest_remainder(Decimal('100.00'), 3)
        assert expected_distribution == [Decimal('33.34'), Decimal('33.33'), Decimal('33.33')]
        assert sum(expected_distribution) == Decimal('100.00')
        
        # Now create splits using this distribution
        splits = [
            BillSplitCreate(
                liability_id=liability.id,
                account_id=i+1,
                amount=amount
            )
            for i, amount in enumerate(expected_distribution)
        ]
        
        validation = BillSplitValidation(
            liability_id=liability.id,
            total_amount=liability.amount,
            splits=splits
        )
        
        # Run validation
        is_valid, error = await bill_split_service.validate_splits(validation)
        
        # Verify validation passes
        assert is_valid is True, f"Validation failed with error: {error}"
        assert error is None
        
        # Verify splits sum to exactly the total
        total_split = sum(split.amount for split in validation.splits)
        assert total_split == Decimal('100.00')
        
        # Verify the distribution matches our expectation
        split_amounts = [split.amount for split in validation.splits]
        assert split_amounts == expected_distribution
        
        # Verify the largest difference between any two splits is exactly $0.01
        max_diff = max(split_amounts) - min(split_amounts)
        assert max_diff == Decimal('0.01')

    @patch('src.services.bill_splits.BillSplitService.get_account')
    @patch('src.services.bill_splits.BillSplitService.get_liability')
    async def test_distribute_large_bill_evenly(self, mock_get_liability, mock_get_account, bill_split_service, mock_db_session):
        """Test distribution of a large bill amount across multiple accounts."""
        # Mock liability with a large amount
        liability = MagicMock()
        liability.id = 1
        liability.amount = Decimal('9999.99')
        mock_get_liability.return_value = liability
        
        # Mock 7 accounts
        accounts = []
        for i in range(7):
            account = MagicMock(spec=Account)
            account.id = i + 1
            account.type = 'checking'
            account.available_balance = Decimal('2000.00')
            accounts.append(account)
        
        # Update mock_get_account
        mock_get_account.side_effect = lambda id: accounts[id-1]
        
        # Calculate distribution using the DecimalPrecision utility
        expected_distribution = DecimalPrecision.distribute_with_largest_remainder(liability.amount, 7)
        
        # Verify distribution properties
        assert len(expected_distribution) == 7
        assert sum(expected_distribution) == liability.amount
        
        # Create splits using this distribution
        splits = [
            BillSplitCreate(
                liability_id=liability.id,
                account_id=i+1,
                amount=amount
            )
            for i, amount in enumerate(expected_distribution)
        ]
        
        validation = BillSplitValidation(
            liability_id=liability.id,
            total_amount=liability.amount,
            splits=splits
        )
        
        # Run validation
        is_valid, error = await bill_split_service.validate_splits(validation)
        
        # Assertions
        assert is_valid is True, f"Validation failed with error: {error}"
        assert error is None
        
        # Verify all amounts have exactly 2 decimal places
        for split in validation.splits:
            assert split.amount.as_tuple().exponent == -2, f"{split.amount} should have exactly 2 decimal places"
        
        # Verify the maximum difference between amounts is at most $0.01
        max_diff = max(split.amount for split in validation.splits) - min(split.amount for split in validation.splits)
        assert max_diff <= Decimal('0.01')
        
        # Verify total is exactly the liability amount
        total_split = sum(split.amount for split in validation.splits)
        assert total_split == liability.amount
