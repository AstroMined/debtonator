import React, { useState } from 'react';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridToolbar,
} from '@mui/x-data-grid';
import {
  Box,
  Button,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { Income } from '../../types/income';
import { Account } from '../../types/accounts';
import FileImportModal from '../common/FileImportModal';
import { previewIncomeImport, importIncome } from '../../services/income';

interface IncomeTableProps {
  incomes: Income[];
  accounts: Account[];
  onDepositToggle: (incomeId: number, deposited: boolean) => void;
  loading?: boolean;
  onImportComplete?: () => void;
}

export const IncomeTable = ({
  incomes,
  accounts,
  onDepositToggle,
  loading = false,
  onImportComplete,
}: IncomeTableProps): React.ReactElement => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [importModalOpen, setImportModalOpen] = useState(false);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const columns: GridColDef[] = [
    {
      field: 'deposited',
      headerName: 'Status',
      width: 130,
      renderCell: (params: GridRenderCellParams<Income>) => (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <IconButton
            onClick={() =>
              params.row.id && onDepositToggle(params.row.id, !params.row.deposited)
            }
            size="small"
            color={params.row.deposited ? 'success' : 'default'}
          >
            {params.row.deposited ? (
              <CheckCircleIcon />
            ) : (
              <RadioButtonUncheckedIcon />
            )}
          </IconButton>
          <Tooltip
            title={params.row.deposited ? 'Deposited' : 'Not Deposited'}
          >
            <Chip
              label={params.row.deposited ? 'Deposited' : 'Pending'}
              size="small"
              color={params.row.deposited ? 'success' : 'warning'}
              variant="outlined"
            />
          </Tooltip>
        </Box>
      ),
      sortable: true,
    },
    {
      field: 'date',
      headerName: 'Date',
      width: 120,
      type: 'date',
      valueGetter: ({ value }) => value && new Date(value),
    },
    {
      field: 'source',
      headerName: 'Source',
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
      field: 'account_id',
      headerName: 'Account',
      width: 150,
      valueGetter: (params: GridRenderCellParams<Income>) =>
        accounts.find((a) => a.id === params.row.account_id)?.name || '-',
    },
  ];

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          startIcon={<UploadFileIcon />}
          onClick={() => setImportModalOpen(true)}
        >
          Import Income
        </Button>
      </Box>

      <Box sx={{ height: 500 }}>
        <DataGrid
          rows={incomes}
          columns={columns}
          loading={loading}
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
              sortModel: [{ field: 'date', sort: 'desc' }],
            },
            columns: {
              columnVisibilityModel: {
                account_id: !isMobile,
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

      <FileImportModal
        open={importModalOpen}
        onClose={() => {
          setImportModalOpen(false);
          if (onImportComplete) {
            onImportComplete();
          }
        }}
        onImport={importIncome}
        onPreview={previewIncomeImport}
        title="Import Income"
        acceptedFormats=".csv,.json"
      />
    </Box>
  );
};
