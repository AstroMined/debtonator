import React, { useState } from 'react';
import { Box, Button, Paper, Typography } from '@mui/material';
import { BillEntryForm, BillFormData } from '../../components/forms';

export const BillsPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [lastSubmittedData, setLastSubmittedData] = useState<BillFormData | null>(null);

  const handleSubmit = (values: BillFormData) => {
    setLastSubmittedData(values);
    setShowForm(false);
    // TODO: Integrate with API
    console.log('Submitted values:', values);
  };

  const handleCancel = () => {
    setShowForm(false);
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
        <Paper elevation={2} sx={{ p: 2 }}>
          <BillEntryForm onSubmit={handleSubmit} onCancel={handleCancel} />
        </Paper>
      ) : lastSubmittedData ? (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Last Submitted Bill
          </Typography>
          <Box component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(lastSubmittedData, null, 2)}
          </Box>
        </Paper>
      ) : null}
    </Box>
  );
};
