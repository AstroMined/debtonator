import React from 'react';
import {
  Box,
  Typography,
  Collapse,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { Decimal } from 'decimal.js';

export const AccountSummary: React.FC = () => {
  const [expanded, setExpanded] = React.useState(true);
  const accounts = useSelector((state: RootState) => state.accounts.accounts);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const totalBalance = accounts.reduce((sum, account) => {
    if (account.type === 'credit') {
      return sum.minus(account.available_balance.abs());
    }
    return sum.plus(account.available_balance);
  }, new Decimal(0));

  const availableCredit = accounts
    .filter(account => account.type === 'credit')
    .reduce((sum, account) => {
      const limit = account.total_limit || new Decimal(0);
      return sum.plus(limit.minus(account.available_balance.abs()));
    }, new Decimal(0));

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="subtitle1" fontWeight="bold">
          Account Summary
        </Typography>
        <IconButton onClick={handleExpandClick} size="small">
          {expanded ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>
      
      <Collapse in={expanded} timeout="auto">
        <List dense>
          <ListItem>
            <ListItemText
              primary="Total Balance"
              secondary={`$${totalBalance.toNumber().toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
              secondaryTypographyProps={{
                color: totalBalance.greaterThanOrEqualTo(0) ? 'success.main' : 'error.main',
                fontWeight: 'bold',
              }}
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Available Credit"
              secondary={`$${availableCredit.toNumber().toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
              secondaryTypographyProps={{
                color: 'info.main',
                fontWeight: 'medium',
              }}
            />
          </ListItem>
          {accounts.map(account => (
            <ListItem key={account.id}>
              <ListItemText
                primary={account.name}
                secondary={`$${account.available_balance.abs().toNumber().toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`}
                secondaryTypographyProps={{
                  color: account.type === 'credit' 
                    ? (account.available_balance.isNegative() ? 'error.main' : 'success.main')
                    : (account.available_balance.greaterThanOrEqualTo(0) ? 'success.main' : 'error.main'),
                }}
              />
            </ListItem>
          ))}
        </List>
      </Collapse>
    </Box>
  );
};
