import React, { useEffect, useState, useCallback } from 'react';
import { Alert, Box, CircularProgress } from '@mui/material';
import { BillsTable } from './BillsTable';
import { Bill } from '../../types/bills';
import { Account, getAccounts } from '../../services/accounts';
import { getBills, updateBillPaymentStatus } from '../../services/bills';
import { ErrorBoundary } from '../common/ErrorBoundary';

export const BillsTableContainer: React.FC = () => {
  const [bills, setBills] = useState<Bill[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [billsData, accountsData] = await Promise.all([
        getBills(),
        getAccounts(),
      ]);
      setBills(billsData);
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

  const handlePaymentToggle = async (billId: number, paid: boolean) => {
    try {
      setError(null);
      const updatedBill = await updateBillPaymentStatus(billId, paid);
      setBills((prevBills) =>
        prevBills.map((bill) =>
          bill.id === billId ? { ...bill, ...updatedBill } : bill
        )
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Failed to update payment status'
      );
      console.error('Failed to update payment status:', error);
    }
  };

  const handleBulkPaymentToggle = async (billIds: number[], paid: boolean) => {
    try {
      setError(null);
      await Promise.all(
        billIds.map((id) => updateBillPaymentStatus(id, paid))
      );
      setBills((prevBills) =>
        prevBills.map((bill) =>
          billIds.includes(bill.id!) ? { ...bill, paid } : bill
        )
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Failed to update bulk payment status'
      );
      console.error('Failed to update bulk payment status:', error);
    }
  };

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
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        <BillsTable
          bills={bills}
          accounts={accounts}
          onPaymentToggle={handlePaymentToggle}
          onBulkPaymentToggle={handleBulkPaymentToggle}
          loading={loading}
        />
      </Box>
    </ErrorBoundary>
  );
};
