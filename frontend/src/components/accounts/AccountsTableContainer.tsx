import React, { useEffect, useState, useCallback } from 'react';
import { Box, Button, CircularProgress, Alert } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { Account } from '../../types/accounts';
import { getAccounts } from '../../services/accounts';
import { AccountsTable } from './AccountsTable';

export const AccountsTableContainer: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAccounts();
      setAccounts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch accounts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const handleEditAccount = useCallback((account: Account) => {
    // TODO: Implement edit account functionality
    console.log('Edit account:', account);
  }, []);

  const handleAddAccount = useCallback(() => {
    // TODO: Implement add account functionality
    console.log('Add account');
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box mb={2}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddAccount}
        >
          Add Account
        </Button>
      </Box>
      <AccountsTable accounts={accounts} onEditAccount={handleEditAccount} />
    </Box>
  );
};
