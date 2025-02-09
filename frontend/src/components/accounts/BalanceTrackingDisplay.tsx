import React from 'react';
import { Box, Card, CardContent, Typography, useTheme } from '@mui/material';
import { useSelector } from 'react-redux';
import { selectAccountBalanceHistory } from '../../store/slices/accountsSlice';
import { formatCurrency } from '../../utils/formatters';
import { Account } from '../../types/accounts';
import { Decimal } from 'decimal.js';
import { RootState } from '../../store';

interface BalanceTrackingDisplayProps {
  account: Account;
}

export const BalanceTrackingDisplay: React.FC<BalanceTrackingDisplayProps> = ({ account }) => {
  const theme = useTheme();
  const balanceHistory = useSelector((state: RootState) => selectAccountBalanceHistory(state, account.id));
  
  const balanceChange = React.useMemo(() => {
    if (balanceHistory.length < 2) return new Decimal(0);
    return balanceHistory[balanceHistory.length - 1].balance
      .minus(balanceHistory[balanceHistory.length - 2].balance);
  }, [balanceHistory]);

  const getBalanceColor = (change: Decimal) => {
    if (change.isPositive()) return theme.palette.success.main;
    if (change.isNegative()) return theme.palette.error.main;
    return theme.palette.text.primary;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" component="div">
            Current Balance
          </Typography>
          <Typography 
            variant="h5" 
            component="div"
            sx={{ color: getBalanceColor(balanceChange) }}
          >
            {formatCurrency(account.available_balance)}
          </Typography>
        </Box>
        
        {!balanceChange.isZero() && (
          <Box display="flex" justifyContent="flex-end" mt={1}>
            <Typography 
              variant="body2" 
              sx={{ 
                color: getBalanceColor(balanceChange),
                display: 'flex',
                alignItems: 'center'
              }}
            >
              {balanceChange.isPositive() ? '↑' : '↓'} {formatCurrency(balanceChange.abs())}
            </Typography>
          </Box>
        )}

        {account.type === 'credit' && account.total_limit && (
          <Box mt={2}>
            <Typography variant="body2" color="textSecondary">
              Available Credit: {formatCurrency(new Decimal(account.total_limit).minus(new Decimal(account.available_balance).abs()))}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Credit Limit: {formatCurrency(account.total_limit)}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
