import React, { useEffect, useState, useCallback } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import { Income } from '../../types/income';
import { Account, getAccounts } from '../../services/accounts';
import { createIncome, updateIncome } from '../../services/income';
import { ErrorBoundary } from '../common/ErrorBoundary';

interface FormValues {
  source: string;
  amount: number;
  date: Date | null;
  target_account_id: number;
  deposited: boolean;
}

interface IncomeEntryFormProps {
  onSubmit: (values: Income) => void;
  onCancel: () => void;
  initialValues?: Partial<Income>;
}

const validationSchema = Yup.object({
  source: Yup.string().required('Source is required'),
  amount: Yup.number()
    .required('Amount is required')
    .positive('Amount must be positive')
    .test(
      'maxDigitsAfterDecimal',
      'Amount cannot have more than 2 decimal places',
      (number) => number == null || Number.isInteger(number * 100)
    ),
  date: Yup.date()
    .required('Date is required')
    .nullable()
    .transform((value, originalValue) => {
      if (!originalValue) {
        return null;
      }
      const date = new Date(originalValue);
      return isNaN(date.getTime()) ? null : date;
    }),
  target_account_id: Yup.number().required('Target account is required'),
  deposited: Yup.boolean(),
});

const defaultInitialValues: FormValues = {
  source: '',
  amount: 0,
  date: null,
  target_account_id: 0,
  deposited: false,
};

export const IncomeEntryForm: React.FC<IncomeEntryFormProps> = ({
  onSubmit,
  onCancel,
  initialValues,
}) => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAccounts = useCallback(async () => {
    try {
      setError(null);
      const accountsData = await getAccounts();
      setAccounts(accountsData);
    } catch (error) {
      setError('Failed to fetch accounts. Please try again.');
      console.error('Failed to fetch accounts:', error);
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const handleSubmit = async (values: FormValues) => {
    try {
      setLoading(true);
      setError(null);

      const incomeData: Income = {
        source: values.source,
        amount: values.amount,
        date: values.date!.toISOString().split('T')[0],
        target_account_id: values.target_account_id,
        deposited: values.deposited,
      };

      const result = initialValues?.id
        ? await updateIncome(initialValues.id, incomeData)
        : await createIncome(incomeData);

      onSubmit(result);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to save income. Please try again.');
      console.error('Failed to save income:', error);
    } finally {
      setLoading(false);
    }
  };

  const formik = useFormik<FormValues>({
    initialValues: {
      ...defaultInitialValues,
      ...initialValues,
      date: initialValues?.date ? new Date(initialValues.date) : null,
    },
    validationSchema,
    onSubmit: handleSubmit,
  });

  return (
    <ErrorBoundary>
      <Box
        component="form"
        onSubmit={formik.handleSubmit}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          maxWidth: 600,
          margin: '0 auto',
          padding: 2,
        }}
      >
        <Typography variant="h6" component="h2" gutterBottom>
          {initialValues?.source ? 'Edit Income' : 'New Income'}
        </Typography>

        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          id="source"
          name="source"
          label="Source"
          value={formik.values.source}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.source && Boolean(formik.errors.source)}
          helperText={formik.touched.source && formik.errors.source}
          disabled={loading}
        />

        <TextField
          fullWidth
          id="amount"
          name="amount"
          label="Amount"
          type="number"
          inputProps={{
            step: '0.01',
            min: '0',
          }}
          value={formik.values.amount}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.amount && Boolean(formik.errors.amount)}
          helperText={formik.touched.amount && formik.errors.amount}
          disabled={loading}
        />

        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DatePicker
            label="Date"
            value={formik.values.date}
            onChange={(date) => {
              formik.setFieldTouched('date', true, false);
              formik.setFieldValue('date', date, true);
            }}
            slotProps={{
              textField: {
                fullWidth: true,
                error: formik.touched.date && Boolean(formik.errors.date),
                helperText: formik.touched.date && formik.errors.date as string,
                disabled: loading,
              },
            }}
            format="MM/dd/yyyy"
            views={['year', 'month', 'day']}
          />
        </LocalizationProvider>

        <FormControl fullWidth>
          <InputLabel id="target_account_id-label">Target Account</InputLabel>
          <Select
            labelId="target_account_id-label"
            id="target_account_id"
            name="target_account_id"
            value={formik.values.target_account_id}
            label="Target Account"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.target_account_id && Boolean(formik.errors.target_account_id)}
            disabled={loading}
          >
            {accounts.map((account) => (
              <MenuItem key={account.id} value={account.id}>
                {account.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControlLabel
          control={
            <Switch
              id="deposited"
              name="deposited"
              checked={formik.values.deposited}
              onChange={formik.handleChange}
              disabled={loading}
            />
          }
          label="Deposited"
        />

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
          <Button variant="outlined" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            type="submit"
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {initialValues?.source ? 'Update' : 'Create'}
          </Button>
        </Box>
      </Box>
    </ErrorBoundary>
  );
};
