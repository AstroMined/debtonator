import React from 'react';
import { Typography, Paper, Box } from '@mui/material';
import { AppLayout } from './components/layout';

function App() {
  return (
    <AppLayout>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Welcome to Debtonator
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Your personal bill and cashflow management system
          </Typography>
        </Box>
        <Typography paragraph>
          This application helps you track bills, income, and maintain sufficient account balances
          for timely bill payments. Use the navigation menu to access different features.
        </Typography>
      </Paper>
    </AppLayout>
  );
}

export default App;
