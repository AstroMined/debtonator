import React, { useState, useCallback } from 'react';
import { Box, Button, Paper, Typography, Alert } from '@mui/material';
import { BillEntryForm } from '../../components/forms';
import { BillsTableContainer } from '../../components/bills';
import { Bill } from '../../types/bills';
import { createBill } from '../../services/bills';
import { ErrorBoundary } from '../../components/common/ErrorBoundary';

export const BillsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (billData: Bill) => {
    try {
      setError(null);
      await createBill(billData);
      setShowForm(false);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Failed to create bill. Please try again.'
      );
      console.error('Error creating bill:', error);
    }
  };

  const handleCancel = useCallback(() => {
    setShowForm(false);
    setError(null);
  }, []);

  return (
    <ErrorBoundary>
      <Box sx={{ p: 3 }}>
        <Box
          sx={{
            mb: 4,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="h4" component="h1">
            Bills
          </Typography>
          {!showForm && (
            <Button variant="contained" onClick={() => setShowForm(true)}>
              Add New Bill
            </Button>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {showForm && (
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <BillEntryForm onSubmit={handleSubmit} onCancel={handleCancel} />
          </Paper>
        )}

        <Paper elevation={2} sx={{ p: 2 }}>
          <BillsTableContainer />
        </Paper>
      </Box>
    </ErrorBoundary>
  );
};
