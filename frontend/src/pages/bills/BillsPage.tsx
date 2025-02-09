import React, { useState } from 'react';
import { Box, Button, Paper, Typography } from '@mui/material';
import { BillEntryForm, BillFormData } from '../../components/forms';
import { BillsTable } from '../../components/bills';
import { Bill } from '../../types/bills';

export const BillsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [bills, setBills] = useState<Bill[]>([
    {
      id: 1,
      month: 'February',
      dayOfMonth: 15,
      dueDate: '2025-02-15',
      billName: 'Internet',
      amount: 89.99,
      upToDate: true,
      account: 'AMEX',
      autoPay: true,
      paid: false
    },
    {
      id: 2,
      month: 'February',
      dayOfMonth: 1,
      dueDate: '2025-02-01',
      billName: 'Rent',
      amount: 2000,
      upToDate: true,
      account: 'UFCU',
      autoPay: false,
      paid: true,
      paidDate: '2025-02-01'
    }
  ]);

  const handleSubmit = async (values: BillFormData) => {
    try {
      setLoading(true);
      // TODO: Integrate with API
      console.log('Submitted values:', values);
      
      // Mock new bill creation
      if (!values.dueDate) {
        throw new Error('Due date is required');
      }

      const newBill: Bill = {
        id: bills.length + 1,
        month: values.dueDate.toLocaleString('default', { month: 'long' }),
        dayOfMonth: values.dueDate.getDate(),
        dueDate: values.dueDate.toISOString().split('T')[0],
        billName: values.billName,
        amount: values.amount,
        upToDate: true,
        account: values.account,
        autoPay: values.autoPay,
        paid: false
      };
      
      setBills(prev => [...prev, newBill]);
      setShowForm(false);
    } catch (error) {
      console.error('Error creating bill:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
  };

  const handlePaymentToggle = async (billId: number, paid: boolean) => {
    try {
      setLoading(true);
      // TODO: Integrate with API
      console.log('Toggling payment:', { billId, paid });
      
      setBills(prev => prev.map(bill => 
        bill.id === billId 
          ? { 
              ...bill, 
              paid,
              paidDate: paid ? new Date().toISOString().split('T')[0] : undefined 
            }
          : bill
      ));
    } catch (error) {
      console.error('Error updating bill payment:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Bills
        </Typography>
        {!showForm && (
          <Button variant="contained" onClick={() => setShowForm(true)}>
            Add New Bill
          </Button>
        )}
      </Box>

      {showForm ? (
        <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
          <BillEntryForm onSubmit={handleSubmit} onCancel={handleCancel} />
        </Paper>
      ) : null}

      <Paper elevation={2} sx={{ p: 2 }}>
        <BillsTable 
          bills={bills}
          onPaymentToggle={handlePaymentToggle}
          loading={loading}
        />
      </Paper>
    </Box>
  );
};
