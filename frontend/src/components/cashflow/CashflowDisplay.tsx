import React from 'react';
import { Box, Card, CardContent, Grid, Typography, CircularProgress } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { CashflowForecast } from '../../types/cashflow';

interface CashflowDisplayProps {
  isLoading?: boolean;
  error?: Error | null;
  data?: CashflowForecast;
}

const MetricCard: React.FC<{
  title: string;
  value: string;
  subtitle?: string;
}> = ({ title, value, subtitle }) => {
  const theme = useTheme();
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Typography 
          variant="h4" 
          component="div" 
          sx={{ 
            color: theme.palette.primary.main,
            fontWeight: 'bold' 
          }}
        >
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export const CashflowDisplay: React.FC<CashflowDisplayProps> = ({
  isLoading = false,
  error = null,
  data
}) => {
  const theme = useTheme();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box 
        p={3} 
        bgcolor={theme.palette.error.light} 
        color={theme.palette.error.contrastText}
        borderRadius={1}
      >
        <Typography variant="h6">Error loading cashflow data</Typography>
        <Typography variant="body2">{error.message}</Typography>
      </Box>
    );
  }

  if (!data) {
    return (
      <Box p={3} bgcolor={theme.palette.grey[100]} borderRadius={1}>
        <Typography variant="body1">No cashflow data available</Typography>
      </Box>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h5" gutterBottom>
        Cashflow Overview
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Bills"
            value={formatCurrency(data.total_bills)}
            subtitle="Next 90 days"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Income"
            value={formatCurrency(data.total_income)}
            subtitle="Expected"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Current Balance"
            value={formatCurrency(data.balance)}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="90-Day Forecast"
            value={formatCurrency(data.forecast)}
          />
        </Grid>
      </Grid>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Minimum Required Funds
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="14-Day Minimum"
            value={formatCurrency(data.min_14_day)}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="30-Day Minimum"
            value={formatCurrency(data.min_30_day)}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="60-Day Minimum"
            value={formatCurrency(data.min_60_day)}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="90-Day Minimum"
            value={formatCurrency(data.min_90_day)}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default CashflowDisplay;
