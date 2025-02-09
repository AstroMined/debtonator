import React, { useCallback, useEffect, useState } from 'react';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
} from '@mui/x-data-grid';
import { Box, Chip, IconButton, Tooltip } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { format } from 'date-fns';

import { Income, IncomeTableRow } from '../../types/income';
import { getIncomes, deleteIncome } from '../../services/income';
import { ErrorBoundary } from '../common/ErrorBoundary';

interface IncomeTableProps {
  onEdit: (income: Income) => void;
  onDelete?: (id: number) => void;
}

export const IncomeTable: React.FC<IncomeTableProps> = ({ onEdit, onDelete }) => {
  const [incomes, setIncomes] = useState<IncomeTableRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIncomes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getIncomes();
      const formattedData: IncomeTableRow[] = data.map((income) => ({
        ...income,
        formattedDate: format(new Date(income.date), 'MM/dd/yyyy'),
      }));
      setIncomes(formattedData);
    } catch (error) {
      setError('Failed to fetch incomes');
      console.error('Failed to fetch incomes:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncomes();
  }, [fetchIncomes]);

  const handleDelete = async (id: number) => {
    try {
      await deleteIncome(id);
      if (onDelete) {
        onDelete(id);
      }
      fetchIncomes();
    } catch (error) {
      console.error('Failed to delete income:', error);
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'date',
      headerName: 'Date',
      flex: 1,
      valueFormatter: ({ value }) => {
        return format(new Date(value as string), 'MM/dd/yyyy');
      },
    },
    {
      field: 'source',
      headerName: 'Source',
      flex: 1,
    },
    {
      field: 'amount',
      headerName: 'Amount',
      flex: 1,
      valueFormatter: ({ value }) => {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(value as number);
      },
    },
    {
      field: 'deposited',
      headerName: 'Status',
      flex: 1,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Deposited' : 'Pending'}
          color={params.value ? 'success' : 'warning'}
          size="small"
        />
      ),
    },
    {
      field: 'target_account_name',
      headerName: 'Target Account',
      flex: 1,
    },
    {
      field: 'undeposited_amount',
      headerName: 'Undeposited',
      flex: 1,
      valueFormatter: ({ value }) => {
        const amount = value as number;
        return amount
          ? new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD',
            }).format(amount)
          : '-';
      },
    },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title="Edit">
            <IconButton
              onClick={() => onEdit(params.row)}
              size="small"
              color="primary"
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
          {onDelete && (
            <Tooltip title="Delete">
              <IconButton
                onClick={() => handleDelete(params.row.id)}
                size="small"
                color="error"
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      ),
    },
  ];

  return (
    <ErrorBoundary>
      <Box sx={{ width: '100%', height: 400 }}>
        <DataGrid
          rows={incomes}
          columns={columns}
          loading={loading}
          pageSizeOptions={[5, 10, 25, 50]}
          initialState={{
            pagination: { paginationModel: { pageSize: 10 } },
            sorting: {
              sortModel: [{ field: 'date', sort: 'desc' }],
            },
          }}
          slots={{
            noRowsOverlay: () => (
              <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
                height="100%"
              >
                {error || 'No income entries found'}
              </Box>
            ),
          }}
          disableRowSelectionOnClick
        />
      </Box>
    </ErrorBoundary>
  );
};
