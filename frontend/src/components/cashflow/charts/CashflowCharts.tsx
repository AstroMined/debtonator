import React, { useMemo } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { CashflowChart, AccountBalanceChart, RequiredFundsChart } from './';
import type { AccountBalance } from './AccountBalanceChart';
import { CashflowForecast } from '../../../types/cashflow';
import { Account } from '../../../types/accounts';

interface CashflowChartsProps {
  data: CashflowForecast[];
  accounts: Account[];
  onDateRangeChange?: (start: Date, end: Date) => void;
  onAccountToggle?: (accountId: number) => void;
  onPeriodSelect?: (period: string) => void;
}

const CashflowCharts: React.FC<CashflowChartsProps> = ({
  data,
  accounts,
  onDateRangeChange,
  onAccountToggle,
  onPeriodSelect
}) => {
  // Transform data for RequiredFundsChart
  const requiredFundsData = useMemo(() => {
    if (!data.length) return [];
    
    const latest = data[data.length - 1];
    return [
      {
        period: '14d',
        required: latest.min_14_day,
        available: latest.balance
      },
      {
        period: '30d',
        required: latest.min_30_day,
        available: latest.balance
      },
      {
        period: '60d',
        required: latest.min_60_day,
        available: latest.balance
      },
      {
        period: '90d',
        required: latest.min_90_day,
        available: latest.balance
      }
    ];
  }, [data]);

  // Transform data for AccountBalanceChart
  const accountBalanceData: AccountBalance[] = useMemo(() => {
    return data.map(item => {
      const balanceData: AccountBalance = {
        date: item.date.toISOString()
      };
      
      accounts.forEach(account => {
        // This is a placeholder. In a real implementation,
        // we would need account-specific balance data
        balanceData[account.name] = 0;
      });
      
      return balanceData;
    });
  }, [data, accounts]);

  return (
    <Box sx={{ mt: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          90-Day Cashflow Forecast
        </Typography>
        <CashflowChart
          data={data}
          onDateRangeChange={onDateRangeChange}
        />
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Account Balances
        </Typography>
        <AccountBalanceChart
          data={accountBalanceData}
          accounts={accounts}
          onAccountToggle={onAccountToggle}
        />
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Required vs Available Funds
        </Typography>
        <RequiredFundsChart
          data={requiredFundsData}
          onPeriodSelect={onPeriodSelect}
        />
      </Paper>
    </Box>
  );
};

export default CashflowCharts;
