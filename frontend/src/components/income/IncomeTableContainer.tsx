import React, { useEffect, useState, useCallback } from 'react';
import { Alert, Box, CircularProgress } from '@mui/material';
import { IncomeTable } from './IncomeTable';
import { Income } from '../../types/income';
import { Account } from '../../types/accounts';
import { getAccounts } from '../../services/accounts';
import { getIncomes, updateIncome } from '../../services/income';
import { ErrorBoundary } from '../common/ErrorBoundary';

export const IncomeTableContainer: React.FC = () => {
  const [incomes, setIncomes] = useState<Income[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [incomesData, accountsData] = await Promise.all([
        getIncomes(),
        getAccounts(),
      ]);
      setIncomes(incomesData);
      setAccounts(accountsData);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch data');
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDepositToggle = async (incomeId: number, deposited: boolean) => {
    try {
      setError(null);
      const updatedIncome = await updateIncome(incomeId, { deposited });
      setIncomes((prevIncomes) =>
        prevIncomes.map((income) =>
          income.id === incomeId ? { ...income, ...updatedIncome } : income
        )
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Failed to update deposit status'
      );
      console.error('Failed to update deposit status:', error);
    }
  };

  const handleImportComplete = useCallback(() => {
    fetchData();
  }, [fetchData]);

  if (loading && !incomes.length) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ErrorBoundary>
      <Box sx={{ width: '100%' }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        <IncomeTable
          incomes={incomes}
          accounts={accounts}
          onDepositToggle={handleDepositToggle}
          loading={loading}
          onImportComplete={handleImportComplete}
        />
      </Box>
    </ErrorBoundary>
  );
};
