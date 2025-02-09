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

interface BillsTableProps {
  bills: Bill[];
  onPaymentToggle: (billId: number, paid: boolean) => void;
  onBulkPaymentToggle?: (billIds: number[], paid: boolean) => void;
  loading?: boolean;
}

export const BillsTable: React.FC<BillsTableProps> = ({
  bills,
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
    const dueDate = new Date(bill.dueDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return dueDate < today ? 'overdue' : 'unpaid';
  };

  const getDaysOverdue = (dueDate: string): number => {
    const due = new Date(dueDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffTime = Math.abs(today.getTime() - due.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const rows: BillTableRow[] = useMemo(
    () =>
      bills.map((bill) => ({
        ...bill,
        status: getBillStatus(bill),
        daysOverdue: !bill.paid && new Date(bill.dueDate) < new Date() ? getDaysOverdue(bill.dueDate) : 0,
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
      const selectedBills = rows.filter(row => newSelectionModel.includes(row.id));
      const allPaid = selectedBills.every(bill => bill.paid);
      const allUnpaid = selectedBills.every(bill => !bill.paid);
      
      if (allPaid || allUnpaid) {
        onBulkPaymentToggle(newSelectionModel as number[], !allPaid);
      }
    }
  };

  const getDefaultColumns = (): GridColDef[] => [
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
      valueGetter: ({ row }: { row: BillTableRow }) => new Date(row.dueDate),
      type: 'date',
    },
    {
      field: 'paidDate',
      headerName: 'Paid Date',
      width: 120,
      valueGetter: ({ row }: { row: BillTableRow }) => 
        row.paidDate ? new Date(row.paidDate) : null,
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
      valueFormatter: ({ value }) => formatCurrency(value as number),
    },
    {
      field: 'amexAmount',
      headerName: 'AMEX',
      width: 120,
      type: 'number',
      valueFormatter: ({ value }) => formatCurrency(value as number),
    },
    {
      field: 'unlimitedAmount',
      headerName: 'Unlimited',
      width: 120,
      type: 'number',
      valueFormatter: ({ value }) => formatCurrency(value as number),
    },
    {
      field: 'ufcuAmount',
      headerName: 'UFCU',
      width: 120,
      type: 'number',
      valueFormatter: ({ value }) => formatCurrency(value as number),
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

  const columns = useMemo(() => getDefaultColumns(), [isMobile]);

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
            sortModel: [{ field: 'dueDate', sort: 'asc' }],
          },
          columns: {
            columnVisibilityModel: {
              paidDate: !isMobile,
              amexAmount: !isMobile,
              unlimitedAmount: !isMobile,
              ufcuAmount: !isMobile,
              account: !isMobile,
              autoPay: !isMobile,
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
