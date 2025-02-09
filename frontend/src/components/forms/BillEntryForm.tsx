import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Button,
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

export interface BillFormData {
  billName: string;
  amount: number;
  dueDate: Date | null;
  account: 'AMEX' | 'UFCU' | 'UNLIMITED';
  autoPay: boolean;
}

interface BillEntryFormProps {
  onSubmit: (values: BillFormData) => void;
  onCancel: () => void;
  initialValues?: Partial<BillFormData>;
}

const validationSchema = Yup.object({
  billName: Yup.string().required('Bill name is required'),
  amount: Yup.number()
    .required('Amount is required')
    .positive('Amount must be positive')
    .test(
      'maxDigitsAfterDecimal',
      'Amount cannot have more than 2 decimal places',
      (number) => number == null || Number.isInteger(number * 100)
    ),
  dueDate: Yup.date()
    .required('Due date is required')
    .nullable()
    .transform((value, originalValue) => {
      if (!originalValue) {
        return null;
      }
      const date = new Date(originalValue);
      return isNaN(date.getTime()) ? null : date;
    }),
  account: Yup.string()
    .oneOf(['AMEX', 'UFCU', 'UNLIMITED'], 'Invalid account selected')
    .required('Account is required'),
  autoPay: Yup.boolean(),
});

const defaultInitialValues: BillFormData = {
  billName: '',
  amount: 0,
  dueDate: null,
  account: 'UFCU',
  autoPay: false,
};

export const BillEntryForm: React.FC<BillEntryFormProps> = ({
  onSubmit,
  onCancel,
  initialValues = defaultInitialValues,
}) => {
  const formik = useFormik({
    initialValues: {
      ...defaultInitialValues,
      ...initialValues,
    },
    validationSchema,
    onSubmit: (values) => {
      onSubmit(values);
    },
  });

  return (
    <Box
      component="form"
      onSubmit={formik.handleSubmit}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        maxWidth: 400,
        margin: '0 auto',
        padding: 2,
      }}
    >
      <Typography variant="h6" component="h2" gutterBottom>
        {initialValues.billName ? 'Edit Bill' : 'New Bill'}
      </Typography>

      <TextField
        fullWidth
        id="billName"
        name="billName"
        label="Bill Name"
        value={formik.values.billName}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        error={formik.touched.billName && Boolean(formik.errors.billName)}
        helperText={formik.touched.billName && formik.errors.billName}
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
      />

      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <DatePicker
          label="Due Date"
          value={formik.values.dueDate}
          onChange={(date) => {
            formik.setFieldTouched('dueDate', true, false);
            formik.setFieldValue('dueDate', date, true);
          }}
          slotProps={{
            textField: {
              fullWidth: true,
              error: formik.touched.dueDate && Boolean(formik.errors.dueDate),
              helperText: formik.touched.dueDate && formik.errors.dueDate as string,
            },
          }}
          format="MM/dd/yyyy"
          views={['year', 'month', 'day']}
        />
      </LocalizationProvider>

      <FormControl fullWidth>
        <InputLabel id="account-label">Account</InputLabel>
        <Select
          labelId="account-label"
          id="account"
          name="account"
          value={formik.values.account}
          label="Account"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.touched.account && Boolean(formik.errors.account)}
        >
          <MenuItem value="AMEX">AMEX</MenuItem>
          <MenuItem value="UFCU">UFCU</MenuItem>
          <MenuItem value="UNLIMITED">UNLIMITED</MenuItem>
        </Select>
      </FormControl>

      <FormControlLabel
        control={
          <Switch
            id="autoPay"
            name="autoPay"
            checked={formik.values.autoPay}
            onChange={formik.handleChange}
          />
        }
        label="Auto Pay"
      />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="contained" type="submit">
          {initialValues.billName ? 'Update' : 'Create'}
        </Button>
      </Box>
    </Box>
  );
};
