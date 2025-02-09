import React, { useState } from 'react';
import { Box, Button, Typography } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

import { Income } from '../../types/income';
import { IncomeEntryForm } from '../../components/forms';
import { IncomeTable } from '../../components/income';
import { ErrorBoundary } from '../../components/common/ErrorBoundary';

export const IncomePage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [selectedIncome, setSelectedIncome] = useState<Income | null>(null);

  const handleAdd = () => {
    setSelectedIncome(null);
    setShowForm(true);
  };

  const handleEdit = (income: Income) => {
    setSelectedIncome(income);
    setShowForm(true);
  };

  const handleSubmit = () => {
    setShowForm(false);
    setSelectedIncome(null);
  };

  const handleCancel = () => {
    setShowForm(false);
    setSelectedIncome(null);
  };

  return (
    <ErrorBoundary>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Income
          </Typography>
          {!showForm && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAdd}
            >
              Add Income
            </Button>
          )}
        </Box>

        {showForm ? (
          <IncomeEntryForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            initialValues={selectedIncome || undefined}
          />
        ) : (
          <IncomeTable onEdit={handleEdit} onDelete={undefined} />
        )}
      </Box>
    </ErrorBoundary>
  );
};
