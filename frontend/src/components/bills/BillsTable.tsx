import React, { useMemo, useState } from 'react';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridToolbar,
  GridRowSelectionModel,
  GridFilterModel,
} from '@mui/x-data-grid';
import { Box, Chip, IconButton, Tooltip, useTheme, useMediaQuery } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { Bill, BillStatus, BillTableRow } from '../../types/bills';
import { Account } from '../../services/accounts';

interface BillsTableProps {
  bills: Bill[];
  accounts: Account[];
  onPaymentToggle: (billId: number, paid: boolean) => void;
  onBulkPaymentToggle?: (billIds: number[], paid: boolean) => void;
  loading?: boolean;
}

export const BillsTable: React.FC<BillsTableProps> = ({
  bills,
  accounts,
  onPaymentToggle,
  onBulkPaymentToggle,
  loading = false,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [selectionModel, setSelectionModel] = useState<GridRowSelectionModel>([]);
  const [filterModel, setFilterModel] = useState<GridFilterModel>({
    items: [],
  });

  const getBillStatus = (bill: Bill): BillStatus => {
    if (bill.paid) return 'paid';
    if (!bill.due_date) return 'unpaid';
    
    const dueDate = new Date(bill.due_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return dueDate < today ? 'overdue' : 'unpaid';
  };

  const getDaysOverdue = (due_date: string | undefined): number => {
    if (!due_date) return 0;
    
    const due = new Date(due_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffTime = Math.abs(today.getTime() - due.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const rows: BillTableRow[] = useMemo(
    () =>
      bills.map((bill) => {
        // Create a map of account IDs to split amounts
        const splitAmounts = bill.splits?.reduce((acc, split) => {
          acc[split.account_id] = split.amount;
          return acc;
        }, {} as { [accountId: number]: number }) || {};

        return {
          ...bill,
          status: getBillStatus(bill),
          daysOverdue: !bill.paid && bill.due_date && new Date(bill.due_date) < new Date() ? getDaysOverdue(bill.due_date) : 0,
          splitAmounts,
        };
      }),
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

  const formatCurrency = (amount?: number) => {
    if (amount === undefined || amount === 0) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const handleSelectionChange = (newSelectionModel: GridRowSelectionModel) => {
    setSelectionModel(newSelectionModel);
    if (onBulkPaymentToggle && newSelectionModel.length > 0) {
      // Check if all selected bills have the same payment status
      const selectedBills = rows.filter(row => row.id && newSelectionModel.includes(row.id));
      if (selectedBills.length > 0) {
        const allPaid = selectedBills.every(bill => bill.paid);
        const allUnpaid = selectedBills.every(bill => !bill.paid);
        
        if (allPaid || allUnpaid) {
          const validIds = selectedBills.map(bill => bill.id!);
          onBulkPaymentToggle(validIds, !allPaid);
        }
      }
    }
  };

  const getDefaultColumns = (): GridColDef[] => {
    const baseColumns: GridColDef[] = [
    {
      field: 'paid',
      headerName: 'Status',
      width: 130,
      renderCell: (params: GridRenderCellParams<BillTableRow>) => {
        const statusLabel = params.row.status === 'overdue' 
          ? `Overdue (${params.row.daysOverdue} days)`
          : params.row.status;

        return (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <IconButton
              onClick={() => params.row.id && onPaymentToggle(params.row.id, !params.row.paid)}
              size="small"
              color={params.row.paid ? 'success' : 'default'}
            >
              {params.row.paid ? (
                <CheckCircleIcon />
              ) : (
                <RadioButtonUncheckedIcon />
              )}
            </IconButton>
            <Tooltip title={statusLabel}>
              <Chip
                label={params.row.status}
                size="small"
                color={getStatusColor(params.row.status)}
                variant="outlined"
              />
            </Tooltip>
          </Box>
        );
      },
      sortable: true,
    },
    {
      field: 'dueDate',
      headerName: 'Due Date',
      width: 120,
      valueGetter: ({ row }: { row: BillTableRow }) => row.due_date ? new Date(row.due_date) : null,
      type: 'date',
    },
    {
      field: 'paidDate',
      headerName: 'Paid Date',
      width: 120,
      valueGetter: ({ row }: { row: BillTableRow }) => 
        row.paid_date ? new Date(row.paid_date) : null,
      type: 'date',
    },
    {
      field: 'bill_name',
      headerName: 'Bill Name',
      width: 200,
      flex: 1,
    },
    {
      field: 'amount',
      headerName: 'Amount',
      width: 120,
      type: 'number',
      valueFormatter: ({ value }) => formatCurrency(value as number),
    },
    // Account columns for splits
    ...accounts.map((account): GridColDef => ({
      field: `account_${account.id}`,
      headerName: account.name,
      width: 120,
      type: 'number',
      valueGetter: (params: GridRenderCellParams<BillTableRow>) => 
        params.row.splitAmounts?.[account.id] || 
        (params.row.account_id === account.id ? params.row.amount : 0),
      valueFormatter: ({ value }) => formatCurrency(value as number),
    })),

    {
      field: 'account_name',
      headerName: 'Primary Account',
      width: 150,
      valueGetter: (params: GridRenderCellParams<BillTableRow>) => 
        params.row.account_name || accounts.find(a => a.id === params.row.account_id)?.name || '-',
    },

    {
      field: 'auto_pay',
      headerName: 'Auto Pay',
      width: 100,
      type: 'boolean',
      renderCell: (params: GridRenderCellParams<BillTableRow>) => (
        <Tooltip title={params.row.auto_pay ? 'Auto Pay Enabled' : 'Manual Payment'}>
          <Chip
            label={params.row.auto_pay ? 'Auto' : 'Manual'}
            size="small"
            color={params.row.auto_pay ? 'info' : 'default'}
          />
        </Tooltip>
      ),
    },
  ];

  return baseColumns;
};

  const columns = useMemo(() => getDefaultColumns(), [isMobile, accounts, getDefaultColumns]);

  return (
    <Box sx={{ width: '100%', height: 500 }}>
      <DataGrid
        rows={rows}
        columns={columns}
        loading={loading}
        checkboxSelection
        disableRowSelectionOnClick
        rowSelectionModel={selectionModel}
        onRowSelectionModelChange={handleSelectionChange}
        filterModel={filterModel}
        onFilterModelChange={setFilterModel}
        slots={{
          toolbar: GridToolbar,
        }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,
            quickFilterProps: { debounceMs: 500 },
          },
        }}
        initialState={{
          sorting: {
            sortModel: [{ field: 'due_date', sort: 'asc' }],
          },
          columns: {
            columnVisibilityModel: {
              paid_date: !isMobile,
              account_name: !isMobile,
              auto_pay: !isMobile,
            },
          },
          pagination: {
            paginationModel: { pageSize: 10, page: 0 },
          },
        }}
        sx={{
          '& .MuiDataGrid-cell:focus': {
            outline: 'none',
          },
          '& .MuiDataGrid-row': {
            '&:nth-of-type(odd)': {
              backgroundColor: theme.palette.action.hover,
            },
          },
          '& .MuiDataGrid-cell--textLeft': {
            paddingLeft: 2,
          },
        }}
      />
    </Box>
  );
};
