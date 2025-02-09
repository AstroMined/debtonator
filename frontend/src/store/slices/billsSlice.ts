import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Bill, BillSplit, BillStatus, BillTableRow } from '../../types/bills';

interface BillsState {
  bills: BillTableRow[];
  selectedBill: Bill | null;
  loading: boolean;
  error: string | null;
  filters: {
    status?: BillStatus;
    month?: string;
    accountId?: number;
  };
}

const initialState: BillsState = {
  bills: [],
  selectedBill: null,
  loading: false,
  error: null,
  filters: {},
};

const billsSlice = createSlice({
  name: 'bills',
  initialState,
  reducers: {
    setBills: (state, action: PayloadAction<BillTableRow[]>) => {
      state.bills = action.payload;
      state.loading = false;
      state.error = null;
    },
    addBill: (state, action: PayloadAction<BillTableRow>) => {
      state.bills.push(action.payload);
    },
    updateBill: (state, action: PayloadAction<{ id: number; updates: Partial<Bill> }>) => {
      const { id, updates } = action.payload;
      const bill = state.bills.find(b => b.id === id);
      if (bill) {
        Object.assign(bill, updates);
      }
    },
    setSelectedBill: (state, action: PayloadAction<Bill | null>) => {
      state.selectedBill = action.payload;
    },
    updateBillSplits: (state, action: PayloadAction<{ billId: number; splits: BillSplit[] }>) => {
      const { billId, splits } = action.payload;
      const bill = state.bills.find(b => b.id === billId);
      if (bill) {
        bill.splits = splits;
        // Update split amounts in table row
        bill.splitAmounts = splits.reduce((acc, split) => {
          acc[split.account_id] = split.amount;
          return acc;
        }, {} as { [accountId: number]: number });
      }
    },
    updatePaymentStatus: (state, action: PayloadAction<{ billId: number; paid: boolean; paidDate?: string }>) => {
      const { billId, paid, paidDate } = action.payload;
      const bill = state.bills.find(b => b.id === billId);
      if (bill) {
        bill.paid = paid;
        if (paid && paidDate) {
          bill.paid_date = paidDate;
        } else {
          bill.paid_date = undefined;
        }
        // Update status
        bill.status = paid ? 'paid' : bill.daysOverdue > 0 ? 'overdue' : 'unpaid';
      }
    },
    setFilters: (state, action: PayloadAction<BillsState['filters']>) => {
      state.filters = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
      if (action.payload) {
        state.error = null;
      }
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  setBills,
  addBill,
  updateBill,
  setSelectedBill,
  updateBillSplits,
  updatePaymentStatus,
  setFilters,
  setLoading,
  setError,
} = billsSlice.actions;

export default billsSlice.reducer;

// Selectors
export const selectBills = (state: { bills: BillsState }) => state.bills.bills;
export const selectSelectedBill = (state: { bills: BillsState }) => state.bills.selectedBill;
export const selectBillById = (state: { bills: BillsState }, id: number) =>
  state.bills.bills.find(bill => bill.id === id);
export const selectLoading = (state: { bills: BillsState }) => state.bills.loading;
export const selectError = (state: { bills: BillsState }) => state.bills.error;
export const selectFilters = (state: { bills: BillsState }) => state.bills.filters;

export const selectFilteredBills = (state: { bills: BillsState }) => {
  const { bills, filters } = state.bills;
  return bills.filter(bill => {
    if (filters.status && bill.status !== filters.status) return false;
    if (filters.month && bill.month !== filters.month) return false;
    if (filters.accountId !== undefined) {
      const isMainAccount = bill.account_id === filters.accountId;
      const hasSplitForAccount = bill.splits?.some(split => split.account_id === filters.accountId);
      if (!isMainAccount && !hasSplitForAccount) return false;
    }
    return true;
  });
};
