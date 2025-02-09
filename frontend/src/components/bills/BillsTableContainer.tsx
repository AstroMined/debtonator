import React, { useEffect, useState, useCallback } from 'react';
import { Alert, Box, CircularProgress } from '@mui/material';
import { useAppDispatch, useAppSelector } from '../../store';
import { BillsTable } from './BillsTable';
import { getAccounts } from '../../services/accounts';
import { Account } from '../../types/accounts';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { 
  selectBillsList,
  selectLoading,
  selectError,
  fetchBills,
  updateBillPaymentAsync,
  updateBillsPaymentAsync
} from '../../store/slices/billsSlice';

export const BillsTableContainer: React.FC = () => {
  const dispatch = useAppDispatch();
  const bills = useAppSelector(selectBillsList);
  const loading = useAppSelector(selectLoading);
  const error = useAppSelector(selectError);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [localError, setLocalError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLocalError(null);
      const accountsData = await getAccounts();
      setAccounts(accountsData);
      await dispatch(fetchBills()).unwrap();
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : 'Failed to fetch data');
      console.error('Failed to fetch data:', error);
    }
  }, [dispatch]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePaymentToggle = useCallback(async (billId: number, paid: boolean) => {
    try {
      setLocalError(null);
      await dispatch(updateBillPaymentAsync({ billId, paid })).unwrap();
    } catch (error) {
      setLocalError(
        error instanceof Error
          ? error.message
          : 'Failed to update payment status'
      );
      console.error('Failed to update payment status:', error);
    }
  }, [dispatch]);

  const handleBulkPaymentToggle = useCallback(async (billIds: number[], paid: boolean) => {
    try {
      setLocalError(null);
      await dispatch(updateBillsPaymentAsync({ billIds, paid })).unwrap();
    } catch (error) {
      setLocalError(
        error instanceof Error
          ? error.message
          : 'Failed to update bulk payment status'
      );
      console.error('Failed to update bulk payment status:', error);
    }
  }, [dispatch]);

  const handleImportComplete = useCallback(() => {
    fetchData();
  }, [fetchData]);

  if (loading && !bills.length) {
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
        {(error || localError) && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setLocalError(null)}>
            {error || localError}
          </Alert>
        )}
        <BillsTable
          bills={bills}
          accounts={accounts}
          onPaymentToggle={handlePaymentToggle}
          onBulkPaymentToggle={handleBulkPaymentToggle}
          loading={loading}
          onImportComplete={handleImportComplete}
        />
      </Box>
    </ErrorBoundary>
  );
};
