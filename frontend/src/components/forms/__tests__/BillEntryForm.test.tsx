import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BillEntryForm } from '../BillEntryForm';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const mockOnSubmit = jest.fn();
const mockOnCancel = jest.fn();

const renderForm = () => {
  return render(
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <BillEntryForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />
    </LocalizationProvider>
  );
};

describe('BillEntryForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all form fields', () => {
    renderForm();

    expect(screen.getByLabelText(/bill name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/auto pay/i)).toBeInTheDocument();
  });

  it('shows validation errors for required fields', async () => {
    renderForm();
    
    const submitButton = screen.getByRole('button', { name: /create/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/bill name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/amount is required/i)).toBeInTheDocument();
      expect(screen.getByText(/due date is required/i)).toBeInTheDocument();
    });
  });

  it('calls onSubmit with form data when valid', async () => {
    renderForm();

    // Fill out the form
    await userEvent.type(screen.getByLabelText(/bill name/i), 'Internet Bill');
    await userEvent.type(screen.getByLabelText(/amount/i), '50.00');
    
    // Select date
    const dateInput = screen.getByLabelText(/due date/i);
    await userEvent.click(dateInput);
    const today = screen.getByRole('button', { name: /choose today/i });
    await userEvent.click(today);

    // Select account
    const accountSelect = screen.getByLabelText(/account/i);
    await userEvent.click(accountSelect);
    const amexOption = screen.getByRole('option', { name: /amex/i });
    await userEvent.click(amexOption);

    // Toggle auto pay
    const autoPaySwitch = screen.getByLabelText(/auto pay/i);
    await userEvent.click(autoPaySwitch);

    // Submit form
    const submitButton = screen.getByRole('button', { name: /create/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
      const submittedData = mockOnSubmit.mock.calls[0][0];
      expect(submittedData.billName).toBe('Internet Bill');
      expect(submittedData.amount).toBe(50);
      expect(submittedData.account).toBe('AMEX');
      expect(submittedData.autoPay).toBe(true);
      expect(submittedData.dueDate).toBeInstanceOf(Date);
    });
  });

  it('calls onCancel when cancel button is clicked', () => {
    renderForm();
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it('initializes with provided values', () => {
    const initialValues = {
      billName: 'Phone Bill',
      amount: 75,
      account: 'UNLIMITED' as const,
      autoPay: true,
      dueDate: new Date('2025-02-15'),
    };

    render(
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <BillEntryForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          initialValues={initialValues}
        />
      </LocalizationProvider>
    );

    expect(screen.getByLabelText(/bill name/i)).toHaveValue('Phone Bill');
    expect(screen.getByLabelText(/amount/i)).toHaveValue(75);
    expect(screen.getByLabelText(/account/i)).toHaveValue('UNLIMITED');
    expect(screen.getByLabelText(/auto pay/i)).toBeChecked();
  });
});
