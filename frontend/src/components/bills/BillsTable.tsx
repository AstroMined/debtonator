import React, { useMemo } from 'react';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
} from '@mui/x-data-grid';
import { Box, Chip, IconButton, Tooltip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { Bill, BillStatus, BillTableRow } from '../../types/bills';

interface BillsTableProps {
  bills: Bill[];
  onPaymentToggle: (billId: number, paid: boolean) => void;
  loading?: boolean;
}

export const BillsTable: React.FC<BillsTableProps> = ({
  bills,
  onPaymentToggle,
  loading = false,
}) => {
  const getBillStatus = (bill: Bill): BillStatus => {
    if (bill.paid) return 'paid';
    const dueDate = new Date(bill.dueDate);
    return dueDate < new Date() ? 'overdue' : 'unpaid';
  };

  const rows: BillTableRow[] = useMemo(
    () =>
      bills.map((bill) => ({
        ...bill,
        status: getBillStatus(bill),
      })),
    [bills]
  );

  const getStatusColor = (status: BillStatus) => {
    switch (status) {
      case 'paid':
        return 'success';
      case 'unpaid':
        return 'warning';
      case 'overdue':
        return 'error';
      default:
        return 'default';
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'paid',
      headerName: 'Status',
      width: 100,
      renderCell: (params: GridRenderCellParams<BillTableRow>) => (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <IconButton
            onClick={() => onPaymentToggle(params.row.id, !params.row.paid)}
            size="small"
            color={params.row.paid ? 'success' : 'default'}
          >
            {params.row.paid ? (
              <CheckCircleIcon />
            ) : (
              <RadioButtonUncheckedIcon />
            )}
          </IconButton>
          <Chip
            label={params.row.status}
            size="small"
            color={getStatusColor(params.row.status)}
            variant="outlined"
          />
        </Box>
      ),
      sortable: true,
    },
    {
      field: 'dueDate',
      headerName: 'Due Date',
      width: 120,
      valueGetter: ({ row }: { row: BillTableRow }) => new Date(row.dueDate),
      type: 'date',
    },
    {
      field: 'billName',
      headerName: 'Bill Name',
      width: 200,
      flex: 1,
    },
    {
      field: 'amount',
      headerName: 'Amount',
      width: 120,
      type: 'number',
      valueFormatter: ({ value }) =>
        new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(value as number),
    },
    {
      field: 'account',
      headerName: 'Account',
      width: 120,
    },
    {
      field: 'autoPay',
      headerName: 'Auto Pay',
      width: 100,
      type: 'boolean',
      renderCell: (params: GridRenderCellParams<BillTableRow>) => (
        <Tooltip title={params.row.autoPay ? 'Auto Pay Enabled' : 'Manual Payment'}>
          <Chip
            label={params.row.autoPay ? 'Auto' : 'Manual'}
            size="small"
            color={params.row.autoPay ? 'info' : 'default'}
          />
        </Tooltip>
      ),
    },
  ];

  return (
    <Box sx={{ width: '100%', height: 400 }}>
      <DataGrid
        rows={rows}
        columns={columns}
        loading={loading}
        initialState={{
          sorting: {
            sortModel: [{ field: 'dueDate', sort: 'asc' }],
          },
        }}
        sx={{
          '& .MuiDataGrid-cell:focus': {
            outline: 'none',
          },
        }}
      />
    </Box>
  );
};
