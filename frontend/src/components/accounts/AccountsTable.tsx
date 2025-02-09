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
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { Account } from '../../types/accounts';
import { formatCurrency } from '../../utils/formatters';

interface AccountsTableProps {
  accounts: Account[];
  onEditAccount: (account: Account) => void;
}

export const AccountsTable: React.FC<AccountsTableProps> = ({
  accounts,
  onEditAccount,
}) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
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
            <TableRow key={account.id}>
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
                  color={account.available_balance < 0 ? 'error' : 'inherit'}
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
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
