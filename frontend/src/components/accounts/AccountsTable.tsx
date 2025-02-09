import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Collapse,
  Box,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { Account } from '../../types/accounts';
import { formatCurrency } from '../../utils/formatters';
import { BalanceTrackingDisplay } from './BalanceTrackingDisplay';
import { Decimal } from 'decimal.js';

interface AccountsTableProps {
  accounts: Account[];
  onEditAccount: (account: Account) => void;
}

const Row: React.FC<{ account: Account; onEditAccount: (account: Account) => void }> = ({
  account,
  onEditAccount,
}) => {
  const [open, setOpen] = React.useState(false);

  return (
    <>
      <TableRow>
        <TableCell padding="checkbox">
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>
          <Typography variant="body1">{account.name}</Typography>
        </TableCell>
        <TableCell>
          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
            {account.type}
          </Typography>
        </TableCell>
        <TableCell align="right">
          <Typography
            variant="body2"
            color={new Decimal(account.available_balance).isNegative() ? 'error' : 'inherit'}
          >
            {formatCurrency(account.available_balance)}
          </Typography>
        </TableCell>
        <TableCell align="right">
          {account.type === 'credit' && account.available_credit !== null ? (
            <Typography variant="body2">
              {formatCurrency(account.available_credit)}
            </Typography>
          ) : (
            '-'
          )}
        </TableCell>
        <TableCell align="right">
          {account.type === 'credit' && account.total_limit !== null ? (
            <Typography variant="body2">
              {formatCurrency(account.total_limit)}
            </Typography>
          ) : (
            '-'
          )}
        </TableCell>
        <TableCell align="right">
          {account.last_statement_balance !== null ? (
            <Typography variant="body2">
              {formatCurrency(account.last_statement_balance)}
            </Typography>
          ) : (
            '-'
          )}
        </TableCell>
        <TableCell>
          {account.last_statement_date ? (
            <Typography variant="body2">
              {new Date(account.last_statement_date).toLocaleDateString()}
            </Typography>
          ) : (
            '-'
          )}
        </TableCell>
        <TableCell>
          <Tooltip title="Edit Account">
            <IconButton
              size="small"
              onClick={() => onEditAccount(account)}
              aria-label="edit account"
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <BalanceTrackingDisplay account={account} />
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

export const AccountsTable: React.FC<AccountsTableProps> = ({
  accounts,
  onEditAccount,
}) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox" />
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell align="right">Available Balance</TableCell>
            <TableCell align="right">Available Credit</TableCell>
            <TableCell align="right">Total Limit</TableCell>
            <TableCell align="right">Last Statement Balance</TableCell>
            <TableCell>Last Statement Date</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {accounts.map((account) => (
            <Row key={account.id} account={account} onEditAccount={onEditAccount} />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
