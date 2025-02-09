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
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
  Stack,
  Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

import { Bill } from '../../types/bills';
import { Account, getAccounts } from '../../services/accounts';
import { createBill, updateBill } from '../../services/bills';
import { ErrorBoundary } from '../common/ErrorBoundary';

interface FormSplit {
  account_id: number;
  amount: number;
}

interface FormValues {
  bill_name: string;
  amount: number;
  due_date: Date | null;
  account_id: number;
  auto_pay: boolean;
  splits: FormSplit[];
}

interface BillEntryFormProps {
  onSubmit: (values: Bill) => void;
  onCancel: () => void;
  initialValues?: Partial<Bill>;
}

const validationSchema = Yup.object({
  bill_name: Yup.string().required('Bill name is required'),
  amount: Yup.number()
    .required('Amount is required')
    .positive('Amount must be positive')
    .test(
      'maxDigitsAfterDecimal',
      'Amount cannot have more than 2 decimal places',
      (number) => number == null || Number.isInteger(number * 100)
    ),
  due_date: Yup.date()
    .required('Due date is required')
    .nullable()
    .transform((value, originalValue) => {
      if (!originalValue) {
        return null;
      }
      const date = new Date(originalValue);
      return isNaN(date.getTime()) ? null : date;
    }),
  account_id: Yup.number().required('Account is required'),
  auto_pay: Yup.boolean(),
  splits: Yup.array().of(
    Yup.object().shape({
      account_id: Yup.number().required('Account is required'),
      amount: Yup.number()
        .required('Amount is required')
        .positive('Amount must be positive')
        .test(
          'maxDigitsAfterDecimal',
          'Amount cannot have more than 2 decimal places',
          (number) => number == null || Number.isInteger(number * 100)
        ),
    })
  ),
});

const defaultInitialValues: FormValues = {
  bill_name: '',
  amount: 0,
  due_date: null,
  account_id: 0,
  auto_pay: false,
  splits: [],
};

export const BillEntryForm: React.FC<BillEntryFormProps> = ({
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

      const billData: Bill = {
        bill_name: values.bill_name,
        amount: values.amount,
        month: new Date(values.due_date!).toLocaleString('default', { month: 'long' }),
        day_of_month: new Date(values.due_date!).getDate(),
        account_id: values.account_id,
        auto_pay: values.auto_pay,
        splits: values.splits,
      };

      const result = initialValues?.id
        ? await updateBill(initialValues.id, billData)
        : await createBill(billData);

      onSubmit(result);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to save bill. Please try again.');
      console.error('Failed to save bill:', error);
    } finally {
      setLoading(false);
    }
  };

  const formik = useFormik<FormValues>({
    initialValues: {
      ...defaultInitialValues,
      ...initialValues,
      due_date: initialValues?.due_date ? new Date(initialValues.due_date) : null,
    },
    validationSchema,
    onSubmit: handleSubmit,
  });

  const addSplit = () => {
    const splits = formik.values.splits || [];
    formik.setFieldValue('splits', [
      ...splits,
      { account_id: 0, amount: 0 },
    ]);
  };

  const removeSplit = (index: number) => {
    const splits = formik.values.splits || [];
    formik.setFieldValue(
      'splits',
      splits.filter((_, i) => i !== index)
    );
  };

  const totalSplitAmount = (formik.values.splits || [])
    .reduce((sum, split) => sum + (split.amount || 0), 0);

  const remainingAmount = formik.values.amount - totalSplitAmount;

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
          {initialValues?.bill_name ? 'Edit Bill' : 'New Bill'}
        </Typography>

        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          id="bill_name"
          name="bill_name"
          label="Bill Name"
          value={formik.values.bill_name}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.bill_name && Boolean(formik.errors.bill_name)}
          helperText={formik.touched.bill_name && formik.errors.bill_name}
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
            label="Due Date"
            value={formik.values.due_date}
            onChange={(date) => {
              formik.setFieldTouched('due_date', true, false);
              formik.setFieldValue('due_date', date, true);
            }}
            slotProps={{
              textField: {
                fullWidth: true,
                error: formik.touched.due_date && Boolean(formik.errors.due_date),
                helperText: formik.touched.due_date && formik.errors.due_date as string,
                disabled: loading,
              },
            }}
            format="MM/dd/yyyy"
            views={['year', 'month', 'day']}
          />
        </LocalizationProvider>

        <FormControl fullWidth>
          <InputLabel id="account_id-label">Primary Account</InputLabel>
          <Select
            labelId="account_id-label"
            id="account_id"
            name="account_id"
            value={formik.values.account_id}
            label="Primary Account"
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.account_id && Boolean(formik.errors.account_id)}
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
              id="auto_pay"
              name="auto_pay"
              checked={formik.values.auto_pay}
              onChange={formik.handleChange}
              disabled={loading}
            />
          }
          label="Auto Pay"
        />

        <Divider sx={{ my: 2 }} />

        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="subtitle1">Split Payments</Typography>
            <Button
              startIcon={<AddIcon />}
              onClick={addSplit}
              variant="outlined"
              size="small"
              disabled={loading}
            >
              Add Split
            </Button>
          </Stack>

          {(formik.values.splits || []).map((split, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Stack direction="row" spacing={2} alignItems="flex-start">
                <FormControl fullWidth>
                  <InputLabel>Account</InputLabel>
                  <Select
                    value={split.account_id}
                    label="Account"
                    onChange={(e) =>
                      formik.setFieldValue(`splits.${index}.account_id`, e.target.value)
                    }
                    disabled={loading}
                  >
                    {accounts.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  inputProps={{ step: '0.01', min: '0' }}
                  value={split.amount}
                  onChange={(e) =>
                    formik.setFieldValue(`splits.${index}.amount`, parseFloat(e.target.value))
                  }
                  disabled={loading}
                />

                <IconButton
                  onClick={() => removeSplit(index)}
                  color="error"
                  sx={{ mt: 1 }}
                  disabled={loading}
                >
                  <DeleteIcon />
                </IconButton>
              </Stack>
            </Box>
          ))}

          {formik.values.splits && formik.values.splits.length > 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Remaining Amount: ${remainingAmount.toFixed(2)}
            </Typography>
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
          <Button variant="outlined" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            type="submit"
            disabled={loading || remainingAmount < 0}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {initialValues?.bill_name ? 'Update' : 'Create'}
          </Button>
        </Box>
      </Box>
    </ErrorBoundary>
  );
};
